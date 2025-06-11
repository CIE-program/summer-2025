# Check existing Fungible and Non Fungible Tokens like BNB, Tether, BoredApeYachtClub

This Python script uses Web3.py to connect to the Ethereum mainnet via a public RPC endpoint. It interacts with ERC-20 token contracts: DAI, WETH, Tether, BNB. Using a simplified ABI, it retrieves each token’s symbol, decimals, total supply and the balance held by a specific Ethereum address (a Uniswap liquidity pool). The values are normalized using the token's decimals() to be human-readable. The results for both tokens are printed to the console.
The program demonstrates how to query token metadata and balances without needing a private API key or full ABI.
Refer to: https://etherscan.io/tokens to get a list of Tokens and check their details

---

## 🔗 References

## https://etherscan.io/tokens

## 📃 License

This project is open source and intended for learning and prototyping purposes.
_Last updated by rdeshmukh73 on 2025-06-11_
