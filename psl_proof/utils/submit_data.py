from typing import Optional, List
import requests
import json
from psl_proof.models.cargo_data import SourceData, DataSource, ChatHistory, SubmissionChat
from datetime import datetime


# Define the URL of the web service
#Patrick_ToCheck - need chanage the url from validator api server, suggestion: stored in env.
api_url = "https://4bee-169-0-170-105.ngrok-free.app"  # Replace with your API endpoint


def get_historical_chats(source_data: SourceData) -> Optional[List[ChatHistory]]:
    try:
        url = f"{api_url}/api/submissions/historical-chats"
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
                print("Error parsing JSON response:", e)
                return None
        else:
            print(f"Validation failed. Status code: {response.status_code}, Response: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return None


def submit_proof_data(source_data: SourceData):
    try:
        url = f"{api_url}/api/submissions/submit-data"
        headers = {"Content-Type": "application/json"}
        payload = source_data.to_submission_json()

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            print(f"Submission failed. Status code: {response.status_code}, Response: {response.text}")


    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
