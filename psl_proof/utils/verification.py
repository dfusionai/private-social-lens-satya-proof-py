from typing import Optional, Dict, Any
import requests
from dataclasses import dataclass
from psl_proof.models.cargo_data import SourceData
from psl_proof.utils.validation_api import get_validation_api_url


@dataclass
class VerifyTokenResult:
    is_valid: bool
    error_text: str


def verify_token(config: Dict[str, Any], source_data: SourceData) -> Optional[VerifyTokenResult]:
    try:
        url = get_validation_api_url(config, "api/verifications/verify-token")
        headers = {"Content-Type": "application/json"}
        payload = source_data.to_verification_json()

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            try:
                result_json = response.json()

                result = VerifyTokenResult(
                    is_valid=result_json.get("isValid", False),
                    error_text=result_json.get("errorText", ""),
                )
                return result
            except ValueError as e:
                print("Error parsing JSON response:", e)
                RuntimeError("Error parsing JSON response:", e)  # Replace with logging in production
        else:
            print(f"verify_token failed. Status code: {response.status_code}, Response: {response.text}")  # Replace with logging
            RuntimeError(f"verify_token failed. Status code: {response.status_code}, Response: {response.text}")  # Replace with logging

    except requests.exceptions.RequestException as e:
        print("verify_token:", e)  # Replace with logging
        RuntimeError("verify_token:", e)  # Replace with logging
