# pipeline_trigger.py
import os
import requests

def trigger_pipeline(file_path: str, metadata: dict) -> dict:
    """
    Sends the capture file along with metadata to the local processing pipeline API.
    Returns the JSON result on success.
    """
    url = "http://localhost:8000/process-svo"  # Adjust for your API host/port
    try:
        with open(file_path, "rb") as f:
            files = {"capture_file": (os.path.basename(file_path), f)}
            # Include metadata as form data.
            data = {
                "crop_type": metadata.get("crop_type", ""),
                "variety": metadata.get("variety", ""),
                "location": metadata.get("location", ""),
                "username": metadata.get("username", "")
            }
            response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Pipeline error: {response.status_code} {response.text}")
    except Exception as e:
        raise Exception(f"Failed to trigger pipeline: {e}")
