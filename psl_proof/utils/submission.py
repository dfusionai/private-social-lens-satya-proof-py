from typing import Optional, List, Dict, Any
import requests
import json
import logging

from dataclasses import dataclass, field
from datetime import datetime

from psl_proof.models.cargo_data import SourceData, DataSource
from psl_proof.utils.validation_api import get_validation_api_url
from psl_proof.models.submission_dtos import ChatHistory, SubmissionChat, SubmissionHistory

def get_submisssion_historical_data(
        config: Dict[str, Any],
        source_data: SourceData
    ) -> Optional[SubmissionHistory]:
    try:
        url = get_validation_api_url(
            config,
            "api/submissions/historical-data"
        )
        headers = {"Content-Type": "application/json"}
        payload = source_data.to_submission_json()

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            try:
                result_json = response.json()
                print(f"get submission historical data - result_json: {result_json}")

                # Map JSON response to ChatHistory objects
                chat_histories = []
                chat_histories_json = result_json.get("chatHistories", [])
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
                        source_chat_id = chat_history_data.get("sourceChatId", 0),
                        chat_list=chat_list
                    )
                    chat_histories.append(chat_history)

                return SubmissionHistory(
                    is_valid=result_json.get("isValid", False),
                    error_text=result_json.get("errorText", ""),
                    chat_histories = chat_histories
                )
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
