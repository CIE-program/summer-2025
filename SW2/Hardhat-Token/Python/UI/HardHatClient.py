import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL =  "http://localhost:5000"

# Replace with actual addresses from Hardhat
ACCOUNTS = {
    "Account 1": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
    "Account 2": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
}

st.set_page_config(page_title="Token Transfer", layout="centered")
st.title("💰 RDT Token Dashboard")

# Sidebar to pick active account
sender_label = st.sidebar.selectbox("Active Account (Sender)", list(ACCOUNTS.keys()))
sender_address = ACCOUNTS[sender_label]

# Show Sender Balance
balance_resp = requests.get(f"{API_URL}/balance/{sender_address}")
balance = balance_resp.json()["balance"] if balance_resp.ok else "Error"
st.markdown(f"**{sender_label} Balance:** `{balance}` RDT")

# Show selected account address and balance
st.sidebar.markdown("### 📄 Selected Account Info")
st.sidebar.code(sender_address)
st.sidebar.markdown(f"**Balance:** `{balance}` RDT")

st.markdown("---")

# Show Init Token Info
if st.sidebar.button("🔄 Init / Refresh Token Info"):
    init_resp = requests.post(f"{API_URL}/init")
    if init_resp.ok:
        info = init_resp.json()
        st.success(f"Token Name: {info['token']} ({info['symbol']})")
        st.write(f"Owner: {info['owner']}")
        st.write(f"Total Supply: {info['totalSupply']}")
        st.write(f"Owner Balance: {info['currentBalance']}")
    else:
        st.error("Init failed.")

# Transfer Tokens
st.header("🔁 Transfer Tokens")

recipient_label = st.selectbox("Send To", [a for a in ACCOUNTS.keys() if a != sender_label])
recipient_address = ACCOUNTS[recipient_label]

amount = st.number_input("Amount to Transfer", min_value=1, step=1)

if st.button("🚀 Send"):
    with st.spinner("Transferring..."):
        transfer_resp = requests.post(
            f"{API_URL}/transfer",
            json={"to": recipient_address, "amount": amount}
        )

    if transfer_resp.ok:
        tx_hash = transfer_resp.json()["tx_hash"]
        st.success(f"✅ Transferred {amount} RDT to {recipient_label}")
        st.code(tx_hash, language="json")
    else:
        st.error("❌ Transfer failed")
        st.text(transfer_resp.text)

# Show recipient balance too
recip_balance_resp = requests.get(f"{API_URL}/balance/{recipient_address}")
recip_balance = recip_balance_resp.json()["balance"] if recip_balance_resp.ok else "Error"
st.markdown(f"**{recipient_label} Balance:** `{recip_balance}` RDT")
