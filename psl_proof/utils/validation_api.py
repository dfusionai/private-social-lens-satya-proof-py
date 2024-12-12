from typing import Optional, List, Dict, Any

def get_validation_api_url(
    config: Dict[str, Any],
    api_path: str
    ) -> str:
    base_url = config['validator_base_api_url']
    url = f"{base_url}/{api_path}"
    print(f"Connected: {url}")
    return url
