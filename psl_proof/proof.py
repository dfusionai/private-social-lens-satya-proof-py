import json
import logging
import os
from typing import Dict, Any
import requests

from datetime import datetime, timezone
from psl_proof.models.proof_response import ProofResponse
from psl_proof.utils.hashing_utils import salted_data, serialize_bloom_filter_base64, deserialize_bloom_filter_base64
from psl_proof.models.cargo_data import SourceChatData, CargoData, SourceData, DataSource, MetaData, DataSource
from psl_proof.utils.validate_data import validate_data, get_total_score
from psl_proof.utils.submission import submit_data
from psl_proof.utils.verification import verify_token, VerifyTokenResult
from psl_proof.models.submission_dtos import ChatHistory, SubmissionChat, SubmissionHistory
from psl_proof.utils.submission import get_submission_historical_data


class Proof:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.proof_response = ProofResponse(dlp_id=config['dlp_id'])


    def generate(self) -> ProofResponse:
        """Generate proofs for all input files."""
        logging.info("Starting proof data")

        data_revision = "01.01"
        current_timestamp = datetime.now(timezone.utc)

        source_data = None
        for input_filename in os.listdir(self.config['input_dir']):
            input_file = os.path.join(self.config['input_dir'], input_filename)
            with open(input_file, 'r') as f:
                input_data = json.load(f)
                source_data = get_source_data(
                    input_data,
                    current_timestamp
                )
                break

        salt = self.config['salt']
        source_user_hash_64 = salted_data(
            (source_data.source, source_data.user),
            salt
        )
        proof_failed_reason = ""
        verify_result = verify_token(
            self.config,
            source_data
        )
        is_data_authentic = verify_result
        if is_data_authentic:
            #print(f"verify_result: {verify_result}")
            is_data_authentic = verify_result.is_valid
            proof_failed_reason = verify_result.error_text
            source_data.proof_token = verify_result.proof_token

        cargo_data = CargoData(
            source_data = source_data,
            source_id = source_user_hash_64,
            current_timestamp = current_timestamp
        )

        if is_data_authentic:
            #Validate source data via validator.api & obtain uniqueness
            submission_history_data : SubmissionHistory = get_submission_historical_data(
                self.config,
                source_data
            )
            is_data_authentic = submission_history_data.is_valid
            proof_failed_reason = submission_history_data.error_text
            cargo_data.chat_histories = submission_history_data.chat_histories
            cargo_data.last_submission = submission_history_data.last_submission

        cool_down_period = 4 # hours
        submission_time_elapsed = cargo_data.submission_time_elapsed()
        if is_data_authentic and cargo_data.last_submission and submission_time_elapsed < cool_down_period:
            is_data_authentic = False
            proof_failed_reason = f"Last submission was made within the past {cool_down_period} hours"

        metadata = MetaData(
          source_id = source_user_hash_64,
          dlp_id = self.config['dlp_id']
        )

        self.proof_response.ownership = 1.0 if is_data_authentic else 0.0
        self.proof_response.authenticity = 1.0 if is_data_authentic else 0.0

        if not is_data_authentic: #short circuit so we don't waste analysis
            print(f"Validation proof failed: {proof_failed_reason}")
            self.proof_response.set_proof_is_invalid()
            self.proof_response.attributes = {
                'proof_valid': False,
                'proof_failed_reason': proof_failed_reason,
                'did_score_content': False,
                'source': source_data.source.name,
                'revision': data_revision,
                'submitted_on': current_timestamp.isoformat()
            }
            self.proof_response.metadata = metadata
            logging.info(f"ProofResponseAttributes: {json.dumps(self.proof_response.attributes, indent=2)}")
            return self.proof_response

        #validate/proof data ...
        validate_data(
            self.config,
            cargo_data,
            self.proof_response
        )

        maximum_score = 1
        reward_factor = 100 # Maximium VFSN, Max. reward per chat --> 1 VFSN.
        self.proof_response.quality = cargo_data.total_quality / reward_factor
        if (self.proof_response.quality > maximum_score):
            self.proof_response.quality = maximum_score

        self.proof_response.uniqueness = cargo_data.total_uniqueness / reward_factor
        if (self.proof_response.uniqueness > maximum_score):
            self.proof_response.uniqueness = maximum_score
        #score data
        total_score = get_total_score(
            self.proof_response.quality,
            self.proof_response.uniqueness
        )
        print(f"Scores >> Quality: {self.proof_response.quality} | Uniqueness: {self.proof_response.uniqueness} | Total: {total_score}")

        minimum_score = 0.05 / reward_factor
        self.proof_response.valid = True # might other factor affect it
        self.proof_response.score = total_score
        if total_score < minimum_score:
            self.proof_response.score = minimum_score
        if total_score > maximum_score:
            self.proof_response.score = maximum_score

        print(f"Proof score: {self.proof_response.score }")
        self.proof_response.attributes = {
            'score': self.proof_response.score,
            'did_score_content': True,
            'source': source_data.source.name,
            'revision': data_revision,
            'submitted_on': current_timestamp.isoformat()
            #'chat_data': None #RL: No longer generate useful data...
        }
        self.proof_response.metadata = metadata

        #Submit Source data to server
        submit_data_result = submit_data(
            self.config,
            source_data
        )
        if submit_data_result and not submit_data_result.is_valid :
            logging.info(f"submit data failed: {submit_data_result.error_text}")
            self.proof_response.set_proof_is_invalid()
            self.proof_response.attributes.pop('score', None)
            self.proof_response.attributes.pop('did_score_content', None)
            self.proof_response.attributes.update({
                'proof_valid': False,
                'proof_failed_reason': submit_data_result.error_text
            })

        logging.info(f"ProofResponseAttributes: {json.dumps(self.proof_response.attributes, indent=2)}")
        return self.proof_response

def get_telegram_data(
    submission_timestamp : datetime,
    input_content: dict,
    source_chat_data: 'SourceChatData'
):
    chat_type = input_content.get('@type')
    if chat_type == "message":
        # Extract user ID
        chat_user_id = input_content.get("sender_id", {}).get("user_id", "")
        #print(f"chat_user_id: {chat_user_id}")
        source_chat_data.add_participant(chat_user_id)

        message_date = submission_timestamp
        # Extract and convert the Unix timestamp to a datetime object
        date_value = input_content.get("date", None)
        if date_value:
            message_date = datetime.utcfromtimestamp(date_value)  # Convert Unix timestamp to datetime
            message_date = message_date.astimezone(timezone.utc)

        #print(f"message_date: {message_date}")

        # Extract the message content
        message = input_content.get('content', {})
        if isinstance(message, dict) and message.get("@type") == "messageText":
            content = message.get("text", {}).get("text", "")
            #print(f"Extracted content: {content}")
            source_chat_data.add_content(
                content,
                message_date,
                submission_timestamp
            )


def get_source_data(
    input_data: Dict[str, Any],
    submission_timestamp: datetime,
 ) -> SourceData:

    revision = input_data.get('revision', '')
    if (revision and revision != "01.01"):
       raise RuntimeError(f"Invalid Revision: {revision}")

    input_source_value = input_data.get('source', '').upper()
    input_source = None

    if input_source_value == 'TELEGRAM':
        input_source = DataSource.telegram
    else:
        raise RuntimeError(f"Unmapped data source: {input_source_value}")

    submission_token = input_data.get('submission_token', '')
    #print("submission_token: {submission_token}")

    input_user = input_data.get('user')
    #print(f"input_user: {input_user}")

    source_data = SourceData(
        source=input_source,
        user=input_user,
        submission_token = submission_token,
        submission_date = submission_timestamp
    )

    input_chats = input_data.get('chats', [])
    source_chats = source_data.source_chats

    for input_chat in input_chats:
        chat_id = input_chat.get('chat_id')
        input_contents = input_chat.get('contents', [])
        if chat_id and input_contents:
            source_chat = SourceChatData(
                chat_id=chat_id
            )
            for input_content in input_contents:
                if input_source == DataSource.telegram:
                    get_telegram_data(
                        submission_timestamp,
                        input_content,
                        source_chat
                    )
                else:
                    raise RuntimeError(f"Unhandled data source: {input_source}")
            source_chats.append(
                source_chat
            )
    return source_data
