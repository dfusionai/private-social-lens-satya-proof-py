from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


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

@dataclass
class SubmitDataResult:
    is_valid: bool
    error_text: str

@dataclass
class SubmissionHistory:
    is_valid: bool
    error_text: str
    last_submission: datetime 
    chat_histories: List[ChatHistory] = field(default_factory=list)

@dataclass
class SubmitDataResponse:
    is_valid: bool
    error_text: str