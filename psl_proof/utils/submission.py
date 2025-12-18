from typing import Optional, List, Dict, Any
import requests
import json
import logging
import traceback
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone

from psl_proof.models.cargo_data import SourceData, DataSource
from psl_proof.utils.validation_api import get_validation_api_url
from psl_proof.models.submission_dtos import (
    ChatHistory, 
    SubmissionChat, 
    SubmissionHistory, 
    SubmitDataResponse,
    EvaluateSubmissionResponse,
    EvaluationDetails,
    ChatEvaluationSummary
)


def parse_iso_datetime(date_string: str) -> datetime:
    """Parse ISO datetime string, handling 'Z' suffix and variable fractional seconds."""
    import re
    
    if date_string.endswith('Z'):
        date_string = date_string[:-1] + '+00:00'
    
    # Python's fromisoformat() requires 0, 3, or 6 digits for fractional seconds.
    # Normalize to 6 digits (microseconds) if present.
    # Match pattern: datetime.fraction+timezone or datetime.fraction-timezone
    match = re.match(r'^(.+\.\d+)([+-].+)$', date_string)
    if match:
        dt_part, tz_part = match.groups()
        # Split on '.' to get the fractional part
        base, frac = dt_part.rsplit('.', 1)
        # Pad or truncate to 6 digits
        frac = frac[:6].ljust(6, '0')
        date_string = f"{base}.{frac}{tz_part}"
    
    return datetime.fromisoformat(date_string)

def get_submission_historical_data(
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
                #print(f"get submission historical data - result_json: {result_json}")

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
                            chat_start_on=parse_iso_datetime(chat["chatStartOn"]),
                            chat_ended_on=parse_iso_datetime(chat["chatEndedOn"])
                        )
                        for chat in chat_history_data.get("chats", [])
                    ]

                    chat_history = ChatHistory(
                        source_chat_id = chat_history_data.get("sourceChatId", 0),
                        chat_list=chat_list
                    )
                    chat_histories.append(chat_history)

                #Convert last submission
                last_submission_val = result_json.get("lastSubmission", None)
                #print(f"last_submission_val: {last_submission_val}")
                try:
                    last_submission = (
                        parse_iso_datetime(last_submission_val)
                        if last_submission_val
                        else None
                    )
                except ValueError:
                    print(f"Invalid date format for last_submission_val: {last_submission_val}")
                    last_submission = None

                return SubmissionHistory(
                    is_valid=result_json.get("isValid", False),
                    error_text=result_json.get("errorText", ""),
                    last_submission= last_submission,
                    chat_histories = chat_histories
                )
            except ValueError as e:
                logging.error(f"Error during parsing Get_historical_chats status: {e}")
                traceback.print_exc()
                sys.exit(1)
        else:
            logging.error(f"GetSubmissionHistoricalData failed. Status code: {response.status_code}, Response: {response.text}")
            traceback.print_exc()
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        logging.error("get_historical_chats:", e)
        traceback.print_exc()
        sys.exit(1)



def evaluate_submission(
    config: Dict[str, Any],
    source_data: SourceData,
    raw_input_data: Dict[str, Any]
) -> EvaluateSubmissionResponse:
    """
    Send raw chat data to the backend for quality and uniqueness evaluation.
    The backend will:
    - Parse and normalize the raw data
    - Calculate quality score using LLM
    - Calculate uniqueness score using message hashes
    - Store message hashes to database
    - Store raw data to blob storage
    
    Args:
        config: Configuration dictionary
        source_data: SourceData with proof token and metadata
        raw_input_data: The original raw input JSON data (chats array)
    
    Returns:
        EvaluateSubmissionResponse with quality and uniqueness scores
    """
    try:
        url = get_validation_api_url(
            config,
            "api/submissions/evaluate"
        )
        headers = {"Content-Type": "application/json"}
        
        # Build the evaluation request payload
        # Send raw chat data for backend to parse and evaluate
        raw_chats = raw_input_data.get('chats', [])
        submission_token = raw_input_data.get('submission_token', '')
        payload = {
            "ProofToken": source_data.proof_token,
            "DataSource": source_data.source.value,  # enum value
            "SourceId": str(source_data.user),
            "SubmittedBy": source_data.submission_by(),
            "SubmittedOn": source_data.submission_date.isoformat(),
            "SubmissionToken": submission_token,
            "Chats": [
                {
                    "ChatId": chat.get('chat_id'),
                    "Contents": chat.get('contents', [])
                }
                for chat in raw_chats
            ]
        }
        
        logging.info(f"Calling evaluate endpoint for {len(raw_chats)} chats")
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            result_json = response.json()
            logging.info(f"Evaluate response: quality={result_json.get('quality', 0)}, uniqueness={result_json.get('uniqueness', 0)}")
            
            # Parse details if present
            details = None
            details_json = result_json.get("details")
            if details_json:
                chat_summaries = []
                for summary_json in details_json.get("chatSummaries", []):
                    chat_summaries.append(ChatEvaluationSummary(
                        source_chat_id=summary_json.get("sourceChatId", ""),
                        message_count=summary_json.get("messageCount", 0),
                        chat_quality=summary_json.get("chatQuality", 0.0),
                        chat_uniqueness=summary_json.get("chatUniqueness", 0.0)
                    ))
                
                details = EvaluationDetails(
                    total_messages=details_json.get("totalMessages", 0),
                    unique_messages=details_json.get("uniqueMessages", 0),
                    llm_reasoning=details_json.get("llmReasoning"),
                    chat_summaries=chat_summaries
                )
            
            return EvaluateSubmissionResponse(
                is_valid=result_json.get("isValid", False),
                error_text=result_json.get("errorText", ""),
                quality=result_json.get("quality", 0.0),
                uniqueness=result_json.get("uniqueness", 0.0),
                score=result_json.get("score", 0.0),  # Backend's multiplicative score
                details=details
            )
        else:
            logging.error(f"Evaluate submission failed. Status code: {response.status_code}, Response: {response.text}")
            return EvaluateSubmissionResponse(
                is_valid=False,
                error_text=f"Evaluate request failed with status {response.status_code}",
                quality=0.0,
                uniqueness=0.0,
                score=0.0
            )
            
    except requests.exceptions.RequestException as e:
        logging.error(f"evaluate_submission error: {e}")
        traceback.print_exc()
        return EvaluateSubmissionResponse(
            is_valid=False,
            error_text=str(e),
            quality=0.0,
            uniqueness=0.0,
            score=0.0
        )


def submit_data(
    config: Dict[str, Any],
    source_data: SourceData
) -> SubmitDataResponse :
    try:
        url = get_validation_api_url(
            config,
            "api/submissions/submit-data"
        )
        headers = {"Content-Type": "application/json"}
        payload = source_data.to_submission_json()

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            result_json = response.json()
            #print(f"submit data - result_json: {result_json}")
            return SubmitDataResponse(
                is_valid=result_json.get("isValid", False),
                error_text=result_json.get("errorText", "")
            )
        else :
            logging.error(f"Submit data failed. Status code: {response.status_code}, Response: {response.text}")
            traceback.print_exc()
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        logging.error("submit_data:", e)
        traceback.print_exc()
        sys.exit(1)
