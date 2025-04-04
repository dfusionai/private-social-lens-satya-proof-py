from typing import Optional, Dict, Any
import requests
import logging
import traceback
import sys
from dataclasses import dataclass
from psl_proof.models.cargo_data import SourceData
from psl_proof.utils.validation_api import get_validation_api_url
from psl_proof.models.verification_dtos import VerifyTokenResult


def verify_token(config: Dict[str, Any], source_data: SourceData) -> Optional[VerifyTokenResult]:
    try:
        url = get_validation_api_url(config, "api/verifications/verify-token")
        headers = {"Content-Type": "application/json"}
        payload = source_data.to_verification_json()

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            try:
                result_json = response.json()
                #print(f"verify_token result_json: {result_json}")
                result = VerifyTokenResult(
                    is_valid=result_json.get("isValid", False),
                    error_text=result_json.get("errorText", ""),
                    proof_token=result_json.get("proofToken", "")
                )
                return result
            except ValueError as e:
                logging.error(f"Error during parsing verification status: {e}")
                traceback.print_exc()
                sys.exit(1)
        else:
            logging.error(f"Error, unexpected verification response: Status code: {response.status_code}, Response: {response.text}")
            traceback.print_exc()
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        logging.error(f"Error during verification: {e}")
        traceback.print_exc()
        sys.exit(1)
