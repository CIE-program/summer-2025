from flask import Flask, jsonify, request
from web3 import Web3
import json
import os
#from dotenv import load_dotenv

#load_dotenv()
contractAddress = "0x5FbDB2315678afecb367f032d93F642f64180aa3" #The Address of the deployed Solidity Smart Contract
privateKey = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80" #From the 1st locally running Node
accountAddress = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266" #The Account Address from the 1st locally running Node
localRPC = "http://127.0.0.1:8545" #The Address of the Server where the Smart Contract is running.  Retrieved from the 
#The JSON file of the Smart Contract
contractJSON = r"E:\Deshmukh2025\Learning\Blockchain\Polygon\hardhat-tutorial\artifacts\contracts\Token.sol\Token.json"


app = Flask(__name__)

# Connect to local node
w3 = Web3(Web3.HTTPProvider(localRPC))
assert w3.is_connected()

# Load contract ABI
with open(contractJSON) as f:
    abi = json.load(f)['abi']

#Get the Smart Contract handle which will be used in the API Functions below
contract = w3.eth.contract(contractAddress, abi=abi)

#API for Token Transfer - POST method
@app.route("/transfer", methods=["POST"])
def transferTokens():
    print("API Call for transferTokens")
    data = request.get_json()
    to = data["to"]
    amount = int(data["amount"])

    nonce = w3.eth.get_transaction_count(accountAddress)
    
    #Use the Contract handle to call the function
    txn = contract.functions.transfer(to, amount).build_transaction({
        'from': accountAddress,
        'nonce': nonce,
        'gas': 100000,
        'gasPrice': w3.to_wei('1', 'gwei')
    })

    #Sign the Transaction with the Node's Private Key
    signed_txn = w3.eth.account.sign_transaction(txn, privateKey)
    #Send the Transaction to the Blockchain
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

    return jsonify({"tx_hash": tx_hash.hex()})

#API for getting the Balance of the given Node/Wallet Address
@app.route("/balance/<address>", methods=["GET"])
def getBalance(address):
    print("API Call for getBalance")
    balance = contract.functions.balanceOf(address).call()
    return jsonify({"address": address, "balance": balance})

#API for Initializing the Tokens for a given Node/Wallet Address
@app.route("/init", methods=["POST"])
def init_token():
    # Re-initialize token holder to initial balance (only callable by deployer)
    print("API Call for Init")
    w3.eth.default_account = accountAddress
    total = contract.functions.totalSupply().call()
    current_balance = contract.functions.balanceOf(accountAddress).call()
    return jsonify({
        "token": contract.functions.name().call(),
        "symbol": contract.functions.symbol().call(),
        "owner": accountAddress,
        "totalSupply": total,
        "currentBalance": current_balance
    })

if __name__ == "__main__":
    app.run(port=5000)
