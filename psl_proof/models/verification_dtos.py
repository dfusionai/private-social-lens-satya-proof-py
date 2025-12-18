from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class VerifyTokenResult:
    is_valid: bool
    error_text: str
    proof_token: str
    cooldown_period_hours: float = 0  # Cooldown period from backend config
