from typing import List, Dict, Any, Optional
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

@dataclass
class ChatEvaluationSummary:
    """Summary of evaluation for a single chat"""
    source_chat_id: str
    message_count: int
    chat_quality: float
    chat_uniqueness: float

@dataclass
class EvaluationDetails:
    """Details of the evaluation"""
    total_messages: int
    unique_messages: int
    llm_reasoning: Optional[str] = None
    chat_summaries: List[ChatEvaluationSummary] = field(default_factory=list)

@dataclass
class EvaluateSubmissionResponse:
    """Response from the /api/submissions/evaluate endpoint"""
    is_valid: bool
    error_text: str
    quality: float = 0.0
    uniqueness: float = 0.0
    score: float = 0.0  # Final score: Quality × Uniqueness (multiplicative)
    details: Optional[EvaluationDetails] = None