#Code to create an API in Flask to mint NFT badges using web3.py library
#Exposes APIs to List and Mint Badges that will be consumed by a front end (Streamlit, Gradio, React.js etc)
#Created by: Raghavendra Deshmukh, PESU CIE - Industry Mentor
#Purpose: Summer 2025 Blockchain project internship
#Credits: Hardhat, ChatGPT, Author's own imagination, Tarun Rama

from flask import Flask, jsonify, request
import requests
from web3 import Web3
import json
import os
from dotenv import load_dotenv
from datetime import datetime
from requests_toolbelt import MultipartEncoder
from pathlib import Path
from collections import OrderedDict
import pyshorteners

load_dotenv()

#use os.getenv to read the below Environment variables from the Env file.
contractAddress = os.getenv("SMART_CONTRACT_ADDRESS") #The Address of the deployed Solidity Smart Contract
privateKey = os.getenv("ACCOUNT_PRIVATE_KEY") #From the 1st locally running Node
accountAddress = os.getenv("ACCOUNT_ADDRESS") #The Account Address from the 1st locally running Node
localRPC = "http://127.0.0.1:8545" #The Address of the Server where the Smart Contract is running. 

#The JSON file of the Smart Contract - The ABI aka Application Binary Interface will be used from this file
contractJSON = r"E:\Deshmukh2025\PESU-CIE\Projects\StudentNFT\Solidity\artifacts\contracts\StudentNFT.sol\StudentBadgeNFT.json"
pinataJWT = os.getenv("PINATA_JWT") #JWT Token for Pinata
pinataBaseURL = os.getenv("PINATA_BASE_URL") #Base URL for Pinata
pinataLegacyURL = os.getenv("PINATA_LEGACY_URL")
STUDENT_BADGE_DATA = "./StudentBadges/StudentBadgeData.json"
CERTIFICATE_DIR = "certificates"

#Pinata Headers for API Calls
PINATA_JWT = os.getenv("PINATA_JWT")
HEADERS = {
    "Authorization": f"Bearer {PINATA_JWT}"
}
# Initialize Flask app
app = Flask(__name__)

# Connect to local node
web3 = Web3(Web3.HTTPProvider(localRPC))
assert web3.is_connected()

# Load contract ABI
with open(contractJSON) as f:
    abi = json.load(f)['abi']

#Get the Smart Contract handle which will be used in the API Functions below
contract = web3.eth.contract(contractAddress, abi=abi)

# Utility: get nonce
def get_nonce(address):
    return web3.eth.get_transaction_count(address)

def uploadToPinata(filePath, metadata):
    url = pinataBaseURL

def uploadFileToPinata(filePath, name=None, keyValues=None, groupID=None, network="public"):
    if not os.path.isfile(filePath):
        raise FileNotFoundError(f"File not found: {filePath}")
    
    fileName = os.path.basename(filePath)
    print(f"The fileName is: {fileName}")

    # Build fields for multipart
    fields = {
        "file": (fileName, open(filePath, "rb"), "application/octet-stream"),
        "network": network
    }

    if name:
        fields["name"] = name
    if groupID:
        fields["group_id"] = groupID
    if keyValues:
        fields["keyvalues"] = json.dumps(keyValues)

    # Construct the multipart form data
    m = MultipartEncoder(fields=fields)

    # Update headers with the proper Content-Type
    headers = {
        "Authorization": f"Bearer {PINATA_JWT}",
        "Content-Type": m.content_type
    }

    # POST request 
    # Here we use the v3 version of the Pinata API to upload the Files as you would see in the base URL that we are using
    response = requests.post("https://uploads.pinata.cloud/v3/files",
                             headers=headers,
                             data=m,
                             timeout=30)

    if response.status_code != 200:
        raise requests.HTTPError(f"Upload failed: {response.status_code} - {response.text}")

    responseJSON = response.json()
    if "data" not in responseJSON or "cid" not in responseJSON["data"]:
        raise ValueError("Unexpected response format: 'cid' missing")

    return responseJSON["data"]

# Upload metadata JSON to Pinata
def uploadMetadataToPinata(metadata):
    #In this case we use the older version - v2 of the Pinata API spec to upload the Metadata
    #Notice that this is the URL: https://api.pinata.cloud/pinning/pinJSONToIPFS and we are pinning the JSON to IPFS
    #This was one way to share the JSON data as a URL in Pinata earlier.  
    #TBD - Figure out how to use the latest Pinata API spec to replace this as well.
    #Also note that we have an option to keep the content that we do not want to publicly expose Private in Pinata.  
    #We can explore these aspects as well if there is a need.
    url = pinataLegacyURL
    headers = {
        "Authorization": f"Bearer {pinataJWT}",
        "Content-Type": "application/json"
    }
    response = requests.request("POST", url, json=metadata, headers=headers)
    if response.status_code != 200:
        raise requests.HTTPError(f"Pinning Metadata to Pinata Failed: {response.status_code} - {response.text}")
    
    responseJSON = response.json()
    if "IpfsHash" not in responseJSON:
        raise ValueError("IPFSHash is not found in the Response")
    return responseJSON["IpfsHash"]

# Endpoint: Check if a badge can be minted
@app.route("/canmint/<badge_type>", methods=["GET"])
def canMint(badge_type):
    try:
        result = contract.functions.canMintBadge(badge_type).call()
        minted = contract.functions.getMintedCount(badge_type).call()
        cap = contract.functions.badgeTypes(badge_type).call()[1]
        return jsonify({
            "can_mint": result,
            "minted": minted,
            "cap": cap
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Endpoint: Mint a new badge
@app.route("/mintBadge", methods=["POST"])
def mintBadge():
    data = request.get_json()
    badge_type = data.get("badge_type")
    token_uri = data.get("token_uri")
    recipient = data.get("recipient")
    print

    try:
        nonce = get_nonce(accountAddress)
        txn = contract.functions.mintBadge(recipient, badge_type, token_uri).build_transaction({
            "from": accountAddress,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": web3.to_wei("2", "gwei")
        })

        signed_txn = web3.eth.account.sign_transaction(txn, private_key=privateKey)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        return jsonify({"tx_hash": web3.to_hex(tx_hash)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Endpoint: Get minted count
@app.route("/getMintedCount/<badge_type>", methods=["GET"])
def mintedCount(badge_type):
    print(f"Calling getMintedCount API - {badge_type}")
    try:
        count = contract.functions.getMintedCount(badge_type).call()
        print(f"Count of Minted NFTS is: {count}")
        return jsonify({"minted_count": count})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

@app.route("/uploadMetadata", methods=["POST"])
def upload_metadata():
    data = request.json
    required_fields = ["student_name", "class_semester", "university", "badge_type"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    student_name = data["student_name"]
    class_semester = data["class_semester"]
    university = data["university"]
    badge_type = data["badge_type"]
    now = datetime.now()
    grant_date = now.strftime("%Y-%m-%d")

    # Upload static image
    baseDir = Path(__file__).parent.resolve()
    imageFileName = f"{badge_type}.PNG"
    image_path =  imageFileName
    #image_path =  os.path.join(r"./certificates", imageFileName).replace("\\", "/")
    print(f"The Image Path is: {image_path}")
    if not os.path.isfile(image_path):
        return jsonify({"error": f"Image for badge type '{badge_type}' not found."}), 400
    # Upload Certificate PNG file to Pinata
    image_cid = uploadFileToPinata(filePath=str(image_path), name=str(image_path), keyValues={"category": "Badge"})

    #We are framing the Image URL that we hae uploaded to Pinata and we shall then create a Short URL to store it as it will save space
    image_url = f"https://gateway.pinata.cloud/ipfs/{image_cid['cid']}"
    s = pyshorteners.Shortener()
    short_url = s.tinyurl.short(image_url)
    #print(short_url)

    #This is a sample of the structure that we are using to store the student details and the Image URL for their earned/granted badge
    #However this can also be a topic to discuss and see what actually should we upload as metadata to Pinata
    pinContent = {
        "image_cid":image_cid['cid'],
        "certificate_url":short_url,
        "attributes" : [
            {"Student":student_name},
            {"Class":class_semester},
            {"University":university},
            {"Date":grant_date},
            {"Badge Type":badge_type}
        ]
    }
    # Construct metadata
    #The pinataMetadata will be the name for the saved File in Pinata which will be studentname-badgetype
    #Again, we can think of a format that is more easy to understand but note that this data is internal and not exposed to students or Admin
    metadata = {
        "pinataMetadata" : {"name": f"{student_name}-{badge_type}"},
        "pinataContent": pinContent
    }

    # Upload metadata JSON to Pinata
    metaDataCid = uploadMetadataToPinata(metadata)
    print(f"https://gateway.pinata.cloud/ipfs/{metaDataCid}")
    metadataURL = f"https://gateway.pinata.cloud/ipfs/{metaDataCid}"
    

    # Save to local JSON log
    #***This code is not of use as of now but leaving it here to use it as a discussion point as it is important to note 
    # the architectural pattern of why we are doing this versus the technical capability
    #We are no longer saving the Badge info locally but it will be retrieved dynamically using the API: list_minted_badges
    #which will call a Solidity function and will retrieve the Indices following which we call another function to get the badge details

    #*** Saving any data that should be retrieved from Blockchain defeats the purpose of the Blockchain itself ***
    record = {
        "student_name": student_name,
        "class_semester": class_semester,
        "university": university,
        "badge_type": badge_type,
        "grant_date": grant_date,
        "metadata_uri": metadataURL
    }

    # Add the Students Badge Data to the local JSON file.  As of now we use this but can also use a database like SQLLite or MongoDB
    local_log_path = STUDENT_BADGE_DATA
    if os.path.exists(local_log_path):
        with open(local_log_path, "r") as f:
            badge_data = json.load(f)
    else:
        badge_data = []

    badge_data.append(record)

    with open(local_log_path, "w") as f:
        json.dump(badge_data, f, indent=2)

    return jsonify({"metadata_uri": metadataURL}), 200

#Use this API to get the list of Minted Badges directly from Blockchain
@app.route("/list_minted_badges", methods=["GET"])
def list_minted_badges():
    #if not os.path.exists(STUDENT_BADGE_DATA):
    #    return jsonify([])
    #with open(STUDENT_BADGE_DATA, "r") as f:
    #    return jsonify(json.load(f))

    #Get the Total Badges Minted as of now from the Blockchain
    metadata_uris = []
    try:
        latest_id = contract.functions.totalSupply().call()  
        if latest_id <= 0:
            return jsonify(0), 200
        for token_id in range(1, latest_id + 1):
            #For each Token ID, get its Metadata URI
            metadata_uri = contract.functions.tokenURI(token_id).call()
            metadata_uris.append(metadata_uri)
    except Exception as e:
        return jsonify({"Unable to get the Minted Badges - Error getting the Token URI": str(e)}), 400

    #If we have the Metadata URIs from the Blockchain, we will retrieve the details of the Minted Badges
    results = []
    for metadata_uri in metadata_uris:
        try:
            print(f"Calling metadata uri with URL {metadata_uri}")
            response = requests.get(metadata_uri)
            if response.status_code != 200:
                continue
            badge_data = response.json()
            print("Got the Response from the Metadata URI")
            #Get the Certificate URL
            certificate_url = badge_data.get('certificate_url', 'N/A')
            attributes = badge_data.get("attributes", [])
            student_collection = {
                list(attr.keys())[0]: list(attr.values())[0] for attr in attributes
            }
            badge_info = OrderedDict([
                ("Student Name", student_collection.get("Student", "N/A")),
                ("Badge Grant Date", student_collection.get("Date", "N/A")),
                ("Badge Type", student_collection.get("Badge Type", "N/A")),
                ("Class or Semester", student_collection.get("Class", "N/A")),
                ("University", student_collection.get("University", "N/A")),
                ("Certificate URL", certificate_url)
            ]       )
            results.append(badge_info)
        except Exception as e:
            return jsonify({"Unable to get the Minted Badges - Error getting Certificate and Student Badge details": str(e)}), 400
        
    return jsonify(results), 200
                    

#This is our Main function where all the magic starts.... Let the games begin
if __name__ == "__main__":
    app.run(debug=True)
