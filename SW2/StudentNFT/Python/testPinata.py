import os
import requests
#from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

PINATA_JWT = os.getenv("PINATA_JWT")
if not PINATA_JWT:
    raise EnvironmentError("Missing PINATA_JWT environment variable")

UPLOAD_URL = "https://uploads.pinata.cloud/v3/files"

HEADERS = {
    "Authorization": f"Bearer {PINATA_JWT}"
}

#@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def upload_file(filepath, name=None, keyvalues=None, group_id=None, network="private"):
    print("Uploading file to Pinata...")
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "rb") as file_data:
        files = {
            "file": (os.path.basename(filepath), file_data)
        }
        data = {
            "network": network
        }
        if name:
            data["name"] = name
        if group_id:
            data["group_id"] = group_id
        if keyvalues:
            data["keyvalues"] = json.dumps(keyvalues)  # must be stringified JSON
        print(files)
        print(data)
        response = requests.post(
            UPLOAD_URL,
            headers=HEADERS,
            files=files,
            data=data,
            timeout=30
        )

    if response.status_code != 200:
        raise requests.HTTPError(f"Upload failed: {response.status_code} - {response.text}")

    response_json = response.json()
    if "data" not in response_json or "cid" not in response_json["data"]:
        raise ValueError("Unexpected response format: 'cid' missing")

    return response_json["data"]

# Example Usage
if __name__ == "__main__":
    import json
    print("Main")
    try:
        file_info = upload_file(
            filepath="./certificates/PitchMaster.png",
            name="PitchMaster.png",
            keyvalues={"category": "Badge"}
        )
        print("✅ Upload successful!")
        print(f"📦 CID: {file_info['cid']}")
        print(f"📄 Name: {file_info['name']}")
        print(f"🕓 Created At: {file_info['created_at']}")
    except Exception as e:
        print(f"❌ Error uploading file: {e}")

    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"

    payload = {
        "pinataOptions": {"cidVersion": 1},
        "pinataMetadata": {"name": "RDTest.json"},
        "pinataContent": {"image_cid": file_info['cid']}
}
    headers = {
        "Authorization": f"Bearer {PINATA_JWT}",
         "Content-Type": "application/json"
    }
    print("Using legacy Pinata API to PIN the JSON")
    response = requests.request("POST", url, json=payload, headers=headers)
    print(response.text)
    js = response.json()
    if "IpfsHash" not in js:
        print("Gaya kaam se")
    print(js["IpfsHash"])        

        