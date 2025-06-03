# 🔗 RD HH Token — Flask API + Streamlit UI Integration

This part of the project builds a simple **RESTful API in Flask** and a **frontend using Streamlit** to interact with your Solidity smart contract deployed on a local Hardhat blockchain.

---

## 🧱 Components

### 1. `flask_api.py` (Flask Backend)
A lightweight Flask server using `web3.py` to:

- Connect to the local Hardhat blockchain
- Interact with the deployed RDT Token smart contract
- Provide RESTful APIs to:
  - Initialize and fetch token metadata
  - Transfer tokens between accounts
  - Get token balance for any address

### 2. `frontend.py` (Streamlit UI)
A clean and interactive dashboard built with Streamlit to:

- Select a sender account
- View balances of sender and recipient
- Transfer tokens
- Fetch token details (name, symbol, supply, owner)

---

## 🌐 Flask API Details

### `/init` (POST)

Initializes and returns the token metadata:

```json
{
  "token": "RD HH Token",
  "symbol": "RDT",
  "owner": "0x...",
  "totalSupply": 100000,
  "currentBalance": 100000
}
```

---

### `/transfer` (POST)

Transfers RDT tokens from a fixed sender to any recipient:

```json
{
  "to": "0xRecipientAddress",
  "amount": 100
}
```

Returns:

```json
{
  "tx_hash": "0xTransactionHash"
}
```

---

### `/balance/<address>` (GET)

Returns the current RDT balance of any given address:

```json
{
  "address": "0x...",
  "balance": 250
}
```

---

## 🖥️ Streamlit UI Features

- 📌 Sidebar: Select sender account and view address + balance
- 🔁 Transfer tokens to another account via dropdown
- 📊 Live view of balances for both sender and recipient
- 🔄 Refresh token metadata (name, symbol, supply)

---

## 🛠 How to Run

### 1. Start Hardhat local blockchain

```bash
npx hardhat node
```

### 2. Deploy the contract

```bash
npx hardhat ignition deploy ./ignition/modules/Token.js --network localhost
```

### 3. Run Flask backend

```bash
python flask_api.py
```

Make sure to update:
- `contractAddress` with the deployed address
- `contractJSON` with correct ABI path
- `accountAddress` and `privateKey` with a local Hardhat account

### 4. Run Streamlit frontend

```bash
streamlit run frontend.py
```

---

## 🔐 Security Notes

- Never use real private keys in development code — this example uses local test keys from Hardhat only.
- For production: use environment variables, wallets like MetaMask, or secure signing solutions.

---

## 📁 Project Structure

```
.
├── contracts/
│   └── Token.sol
├── flask_api.py
├── frontend.py
├── artifacts/
│   └── contracts/
│       └── Token.sol/
│           └── Token.json
├── hardhat.config.js
├── test/
│   └── Token.js
└── ignition/
    └── modules/
        └── Token.js
```

---

## ✅ Summary

This project connects:
- A **Solidity smart contract** (local Hardhat)
- A **Flask API** using Web3.py
- A **Streamlit frontend** for interacting visually

Perfect for local simulation, token testing, and dApp education.

