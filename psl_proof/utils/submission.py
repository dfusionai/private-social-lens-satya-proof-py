from typing import Optional, List, Dict, Any
import requests
import json
from dataclasses import dataclass, field
from datetime import datetime

from psl_proof.models.cargo_data import SourceData, DataSource
from psl_proof.utils.validation_api import get_validation_api_url


@dataclass
class SubmissionChat:
    participant_count: int
    chat_count: int
    chat_length: int
    chat_start_on: datetime
    chat_ended_on: datetime

@dataclass
class ChatHistory:
    source_chat_id : str
    chat_list: List[SubmissionChat] = field(default_factory=list)


def get_historical_chats(
        config: Dict[str, Any],
        source_data: SourceData
    ) -> Optional[List[ChatHistory]]:
    try:
        url = get_validation_api_url(
            config,
            "api/submissions/historical-chats"
        )
        headers = {"Content-Type": "application/json"}
        payload = source_data.to_submission_json()

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            try:
                chat_histories_json = response.json()

                # Map JSON response to ChatHistory objects
                chat_histories = []
                for chat_history_data in chat_histories_json:
                    #print(f"chat_history_data:{chat_history_data}")
                    chat_list = [
                        SubmissionChat(
                            participant_count=chat.get("participantCount", 0),
                            chat_count=chat.get("chatCount", 0),
                            chat_length=chat.get("chatLength", 0),
                            chat_start_on=datetime.fromisoformat(chat["chatStartOn"]),
                            chat_ended_on=datetime.fromisoformat(chat["chatEndedOn"])
                        )
                        for chat in chat_history_data.get("chats", [])
                    ]

                    chat_history = ChatHistory(
                        source_chat_id=chat_history_data.get("sourceChatId", ""),
                        chat_list=chat_list
                    )
                    chat_histories.append(chat_history)

                return chat_histories
            except ValueError as e:
                logging.error(f"Error during parsing Get_historical_chats status: {e}")
                traceback.print_exc()
                sys.exit(1)
        else:
            logging.error(f"Validation failed. Status code: {response.status_code}, Response: {response.text}")
            traceback.print_exc()
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        logging.error("get_historical_chats:", e)
        traceback.print_exc()
        sys.exit(1)



def submit_data(
    config: Dict[str, Any],
    source_data: SourceData
):
    try:
        url = get_validation_api_url(
            config,
            "api/submissions/submit-data"
        )
        headers = {"Content-Type": "application/json"}
        payload = source_data.to_submission_json()

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            logging.error(f"Submission failed. Status code: {response.status_code}, Response: {response.text}")
            traceback.print_exc()
            sys.exit(1)


    except requests.exceptions.RequestException as e:
        logging.error("submit_data:", e)
        traceback.print_exc()
        sys.exit(1)
