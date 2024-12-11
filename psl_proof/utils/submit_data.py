from typing import Optional
import requests
import json

from psl_proof.models.cargo_data import SourceData, DataSource
from datetime import datetime

# Define the URL of the web service
#Patrick ToCheck - need get url from server and stored in env.
api_url = "https://4bee-169-0-170-105.ngrok-free.app"  # Replace with your API endpoint


def validate_proof_data(source_data: SourceData) -> Optional[str]:
    try:
        url = f"{api_url}/api/validations/validate"
        headers = {"Content-Type": "application/json"}
        payload = source_data.to_submission_json()

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            try:
                jsondata = response.json()
                #print("Validation succeeded:", jsondata)
                return jsondata
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

        if response.status_code != 200:
            print(f"Submission failed. Status code: {response.status_code}, Response: {response.text}")


    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
