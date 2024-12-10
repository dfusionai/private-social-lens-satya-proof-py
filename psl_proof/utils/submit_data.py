from typing import Optional
import requests
import json

from psl_proof.models.cargo_data import SourceData, DataSource
from datetime import datetime

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
api_url = "https://4bee-169-0-170-105.ngrok-free.app"  # Replace with your API endpoint


def validate_proof_data(source_data: SourceData) -> Optional[ValidationResult]:
    try:
        url = f"{api_url}/api/validations/validate"
        headers = {"Content-Type": "application/json"}
        payload = source_data.to_submission_json()

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            try:
                jsondata = response.json()
                result = ValidationResult.from_json(jsondata)
                print("Validation succeeded:", result)
                return result
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
        url = f"{api_url}/api/validations/submit"
        headers = {"Content-Type": "application/json"}
        payload = source_data.to_submission_json()

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            try:
                jsondata = response.json()
                result = ValidationResult.from_json(jsondata)
                print("Submission succeeded:", result)
                return result
            except ValueError as e:
                print("Error parsing JSON response:", e)
                return None
        else:
            print(f"Submission failed. Status code: {response.status_code}, Response: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return None

if __name__ == "__main__":
    try:
        source_data = SourceData(
            source = DataSource.telegram,
            user = "user01",
            submission_id = "submission_id01",
            submission_by = "submission_by01",
            submission_date = datetime.now()
        )
        validate_proof_data(source_data)
    except Exception as e:
        print(f"Error during proof generation: {e}")
