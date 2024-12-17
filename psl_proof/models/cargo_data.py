from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import math
from typing import Union

from dataclasses import dataclass, field
from datetime import datetime

# Enum for DataSource
class DataSource(Enum):
    telegram = 0

# Source Chat Data
@dataclass
class SourceChatData:
    chat_id: int
    participants: list[str] = field(default_factory=list)
    contents: list[str] = field(default_factory=list)
    total_content_length: int = 0
    total_content_value: int = 0
    chat_count : int = 0
    chat_start_on: datetime = None
    chat_ended_on: datetime = None

    def chat_id_as_key(self) -> str :
        return str(self.chat_id)

    def timeliness_value(self) -> float:
        if self.total_content_length == 0:
            return 0
        # tav = (𝛴 litsi) / (𝛴 li)
        time_avg = float(self.total_content_value) / float(self.total_content_length)
        # a = ln(2) / thl
        half_life = 600.0  # 600 minutes
        time_decay = math.log(2) / half_life
        # t = exp(-atav)
        return math.exp(- time_decay * time_avg)  # range 0 to 1

    def thoughtfulness_of_conversation(self) -> float:
        n = len(self.participants)  # n: number of participants
        if n == 1:
            return 0.0
        u = 3.0  # 𝜇: optimal number of participants
        d = 5.0  # 𝜎: standard deviation of the curve

        # Formula: p = exp(-(n-𝜇) / (2𝜎^2))
        return math.exp(-(n - u) / (2 * d ** 2))  # range 0 to 1

    def contextualness_of_conversation(self)  -> float:
        c = self.total_content_length #total token length, c, of the text data
        m = 2.0 #midpoint
        k = 1.0 #key parameters.
        # l=1/(1+exp(-k(c-c0)))
        return 1.0/(1.0 + math.exp(-k*(c-m)))

    def quality_score(self) -> float :
        a = 1 # factor
        b = 1 # factor
        c = 1 # factor
        t = self.timeliness_value()
        p = self.thoughtfulness_of_conversation()
        l = self.contextualness_of_conversation()
        return round((a*t + b*t + c*l)/(a+b+c),2)


    def content_as_text(self) -> str:
        """Converts contents to a single string with each entry on a new line."""
        return "\r".join(self.contents)

    def add_content(
        self,
        content: str,
        chat_timestamp: datetime,
        submission_timestamp: datetime
    ) -> None:
        """Adds a new content string to the contents list if it's not empty."""
        if content:
            self.chat_count += 1
            content_len = len(content)

            # Calculate the difference in minutes
            # Convert current_timestamp to datetime if it's a Unix timestamp
            if isinstance(submission_timestamp, int):
                submission_timestamp = datetime.utcfromtimestamp(submission_timestamp)
            time_in_seconds = (submission_timestamp - chat_timestamp).total_seconds()
            time_in_minutes = int(time_in_seconds // 60)

            if (self.chat_start_on):
               if (self.chat_start_on > chat_timestamp):
                  self.chat_start_on = chat_timestamp
            else :
               self.chat_start_on = chat_timestamp

            if (self.chat_ended_on):
               if (self.chat_ended_on < chat_timestamp):
                  self.chat_ended_on = chat_timestamp
            else :
               self.chat_ended_on = chat_timestamp

            self.total_content_length += content_len
            content_value = time_in_minutes * content_len
            self.total_content_value += content_value

            self.contents.append(content)

    def add_participant(self, participant: str) -> None:
        """Adds a new participant to the participants list if it's not already present."""
        if participant and participant not in self.participants:
            self.participants.append(participant)

    def to_dict(self) -> dict:
        """Converts the object to a dictionary representation."""
        return {
            "chat_id": self.chat_id,
            "contents": self.content_as_text()
        }

    def to_submission_json(self) -> dict:
        chat_start_on = self.chat_start_on if self.chat_start_on is not None else datetime.now()
        chat_ended_on = self.chat_ended_on if self.chat_ended_on is not None else datetime.now()
        return {
            "SourceChatId": self.chat_id_as_key(),
            "ParticipantCount": len(self.participants),
            "ChatCount": self.chat_count,
            "ChatLength": self.total_content_length,
            "ChatStartOn": chat_start_on.isoformat(),
            "ChatEndedOn": chat_ended_on.isoformat()
        }




# SourceData with enum and chat data
@dataclass
class SourceData:
    source: DataSource         # "telegram"
    user: str
    submission_token: str
    submission_id: str
    submission_by: str
    submission_date: datetime
    source_chats: List[SourceChatData]  # List of SourceChatData instances

    def __init__(self, source, submission_token, submission_id, submission_by, submission_date, user, source_chats=None):
        self.source = source
        self.user = user
        self.submission_token = submission_token
        self.submission_id = submission_id
        self.submission_by = submission_by
        self.submission_date = submission_date
        self.source_chats = source_chats or []

    def to_dict(self):
        return {
            "source": self.source.name,  # Use .name to convert enum to string
            "user": self.user,
            "submission_id": self.submission_id,
            "submission_by": self.submission_by,
            "submission_date": self.submission_date.isoformat() if isinstance(self.submission_date, datetime) else str(self.submission_date),
            "chats": [source_chat.to_dict() for source_chat in self.source_chats]
        }

    def to_submission_json(self) :
        json = {
            "DataSource": self.source.value,  # Use .name to convert enum to string
            "SourceId": self.submission_id,
            "SubmissionToken": self.submission_token,
            "SubmittedBy": self.submission_by,
            "SubmittedOn": self.submission_date.isoformat(),
            "Chats": [source_chat.to_submission_json() for source_chat in self.source_chats]
        }
        #print(f"Submission json:{json}")
        return json

    def to_verification_json(self) -> dict:
        return {
            "VerificationType": 0, # VerificationToken.
            "Token": self.submission_token,
            "Reference": self.submission_id,
            "SubmittedBy": self.submission_by,
            "SubmittedOn": self.submission_date.isoformat(),
        }

# ChatData for Source (final destination data structure)
@dataclass
class ChatData:
    chat_length: int
    chat_start_on: datetime = None
    chat_ended_on: datetime = None
    sentiment: Dict[str, Any] = field(default_factory=dict)
    keywords: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "chat_length": self.chat_length,
            "chat_start_on": self.chat_start_on.isoformat(),
            "chat_ended_on": self.chat_ended_on.isoformat(),
            "sentiment": self.sentiment,   # No need to call .to_dict() for dicts
            "keywords": self.keywords,     # Same for other dict fields
        }

# CargoData for Source
@dataclass
class CargoData:
    source_data: SourceData
    source_id: str
    # chat_list: List[ChatData] = field(default_factory=list)

    def to_dict(self):
        # Return a dictionary representation of the CargoData object
        return {
            "source_data": self.source_data,  # Assuming source_data can be serialized directly
            "source_id": self.source_id #,
            #"chat_list": [chat.to_dict() for chat in self.chat_list]  # Convert each ChatData in the list to a dict
        }

    @staticmethod
    def convert_to_serializable(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: CargoData.convert_to_serializable(v) for k, v in obj.items()}  # Recursively handle dictionary values
        elif isinstance(obj, list):
            return [CargoData.convert_to_serializable(item) for item in obj]  # Recursively handle list items
        return obj  # Return the object if it's already serializable

    def get_chat_list_data(self) -> Any:
        # Convert each ChatData to dict and make sure all nested objects are serializable
        chat_list_data = [self.convert_to_serializable(chat_data.to_dict()) for chat_data in self.chat_list]
        return chat_list_data


# MetaData for Source
@dataclass
class MetaData:
    source_id: str
    dlp_id: str

    def to_dict(self):
        return {
            "source_id": self.source_id,
            "dlp_id": self.dlp_id
        }
