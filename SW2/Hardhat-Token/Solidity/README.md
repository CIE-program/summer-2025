# 🪙 RD HH Token — Local Solidity Token Project

This project demonstrates a simple ERC-20–like token called **"RD HH Token" (`RDT`)**, built using Solidity and deployed/tested locally using the Hardhat development environment.

---

## 🛠 Project Structure

| File | Purpose |
|------|---------|
| `contracts/Token.sol` | The Solidity smart contract defining the RDT token |
| `ignition/modules/Token.js` | The deployment module for the Token contract using [Hardhat Ignition](https://hardhat.org/hardhat-runner/plugins/nomicfoundation-hardhat-ignition) |
| `test/Token.js` | Test suite to validate deployment and token transfers |
| `hardhat.config.js` | Hardhat configuration file specifying the Solidity version and plugins |

---

## 📦 Features of the Token Contract

- `name = "RD HH Token"`
- `symbol = "RDT"`
- `totalSupply = 100,000`
- Constructor assigns the **entire supply to the deployer's address**
- `transfer(address to, uint amount)` to send tokens between accounts
- `balanceOf(address)` to check balance
- Emits a `Transfer` event on every token transfer

---

## 🚀 Setup and Deployment

### 1. Install dependencies

```bash
npm install
```

### 2. Start the local Hardhat node

```bash
npx hardhat node
```

This launches a local blockchain with 20 funded accounts.

### 3. Deploy the contract using Hardhat Ignition

```bash
npx hardhat ignition deploy ./ignition/modules/Token.js --network localhost
```

- This deploys the contract using the **first account** from the local Hardhat node.
- That account receives the full 100,000 RDT token supply.

---

## ✅ Run Tests

This project uses [Chai](https://www.chaijs.com/) assertions via Hardhat Toolbox to test:

- Owner receives the full token supply on deployment
- Tokens can be transferred between accounts

```bash
npx hardhat test
```

---

## 🧪 Sample Tests

In `test/Token.js`:

```js
expect(await hardhatToken.totalSupply()).to.equal(ownerBalance);
await hardhatToken.transfer(first.address, 100);
expect(await hardhatToken.balanceOf(first.address)).to.equal(100);
```

---

## 📜 Sample Output (Terminal)

```
Token contract
  ✔ Deployment should assign the total supply of tokens to the owner
  ✔ Should Transfer Tokens from One Account to Another Account
```

---

## 🧠 Notes

- This is **not a complete ERC-20 implementation** — no `approve`, `allowance`, etc.
- It's ideal for learning and simulating dApps before moving to a public testnet (e.g., Polygon Amoy).
- Token balances are governed globally by the contract. Only the deployer receives the initial supply.

---

## 📂 Folder Structure

```
.
├── contracts/
│   └── Token.sol
├── ignition/
│   └── modules/
│       └── Token.js
├── test/
│   └── Token.js
├── hardhat.config.js
└── README.md
```

---

## 🧑‍💻 Author

Built with ❤️ as a local Solidity token project using Hardhat + Ignition.
