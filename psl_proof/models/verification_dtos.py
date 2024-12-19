from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class VerifyTokenResult:
    is_valid: bool
    error_text: str
    proof_token: str
