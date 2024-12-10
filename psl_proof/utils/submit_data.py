from typing import List, Dict, Optional
import requests
from psl_proof.models.cargo_data import SourceData

class ValidationResult:
    def __init__(self, uniqueness=0):
        self.uniqueness = uniqueness

    @classmethod
    def from_json(cls, json_data):
        if isinstance(json_data, str):
            data = json.loads(json_data)
        elif isinstance(json_data, dict):
            data = json_data
        else:
            raise ValueError("Invalid JSON data type. Must be a string or dictionary.")

        return cls(uniqueness=data.get('Uniqueness', 0))


# Define the URL of the web service
topics_url = " https://33c2-169-0-170-105.ngrok-free.app"  # Replace with your API endpoint


def validate_proof_data(source_data: SourceData) -> Optional[ValidationResult]:
    try:
        url = f"{topics_url}/api/validations/validate"
        headers = {"Content-Type": "application/json"}
        payload = source_data.get_submission_json()
        response = requests.post(url, data=payload, headers=headers)

        if response.status_code == 200:
            jsondata = response.json()
            result = ValidationResponse.from_json(jsondata)
            print("Validate data successfully:", result)
            return result
        else:
            print(f"Failed to Validate Data. Status code: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return None

def submit_proof_data(source_data: SourceData):
    try:
        url = f"{topics_url}/api/validations/submit"
        headers = {"Content-Type": "application/json"}
        payload = source_data.get_submission_json()
        response = requests.post(url, data=payload, headers=headers)

        if response.status_code == 200:
            jsondata = response.json()
            result = ValidationResponse.from_json(jsondata)
            print("Submission Data successfully:", result)
            return result
        else:
            print(f"Failed to Submission Data. Status code: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return None