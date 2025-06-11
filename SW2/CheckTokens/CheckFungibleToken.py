#This Python script uses Web3.py to connect to the Ethereum mainnet via a public RPC endpoint. 
# It interacts with two ERC-20 token contracts: DAI and WETH. 
# Using a simplified ABI, it retrieves each token’s symbol, decimals, total supply, and the balance held by a 
# specific Ethereum address (a Uniswap liquidity pool). 
# The values are normalized using the token's decimals() to be human-readable. 
# The results for both tokens are printed to the console. 
# The program demonstrates how to query token metadata and balances without needing a private API key or full ABI.
# Refer to: https://etherscan.io/tokens to get a list of Tokens and check their details

from web3 import Web3

# Using the Etherem Mainnet to Read NFT Token Details.  The URL to be used in Web3 is below
w3 = Web3(Web3.HTTPProvider("https://eth-mainnet.public.blastapi.io"))

dai_token_addr = "0x6B175474E89094C44Da98b954EedeAC495271d0F"     # DAI
weth_token_addr = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"    # Wrapped ether (WETH)

acc_address = "0xA478c2975Ab1Ea89e8196811F51A7B7Ade33eB11"        # Uniswap V2: DAI 2

# This is a simplified Contract Application Binary Interface (ABI) of an ERC-20 Token Contract.
# It will expose only the methods: balanceOf(address), decimals(), symbol() and totalSupply()
simplified_abi = [
    {
        'inputs': [{'internalType': 'address', 'name': 'account', 'type': 'address'}],
        'name': 'balanceOf',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view', 'type': 'function', 'constant': True
    },
    {
        'inputs': [],
        'name': 'decimals',
        'outputs': [{'internalType': 'uint8', 'name': '', 'type': 'uint8'}],
        'stateMutability': 'view', 'type': 'function', 'constant': True
    },
    {
        'inputs': [],
        'name': 'symbol',
        'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
        'stateMutability': 'view', 'type': 'function', 'constant': True
    },
    {
        'inputs': [],
        'name': 'totalSupply',
        'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
        'stateMutability': 'view', 'type': 'function', 'constant': True
    }
]

dai_contract = w3.eth.contract(address=w3.to_checksum_address(dai_token_addr), abi=simplified_abi)
print(dai_contract)

symbol = dai_contract.functions.symbol().call()
decimals = dai_contract.functions.decimals().call()
totalSupply = dai_contract.functions.totalSupply().call() / 10**decimals
addr_balance = dai_contract.functions.balanceOf(acc_address).call() / 10**decimals

#  DAI
print("===== %s =====" % symbol)
print("Total Supply:", totalSupply)
print("Addr Balance:", addr_balance)

weth_contract = w3.eth.contract(address=w3.to_checksum_address(weth_token_addr), abi=simplified_abi)
symbol = weth_contract.functions.symbol().call()
decimals = weth_contract.functions.decimals().call()
totalSupply = weth_contract.functions.totalSupply().call() / 10**decimals
addr_balance = weth_contract.functions.balanceOf(acc_address).call() / 10**decimals

#  WETH
print("===== %s =====" % symbol)
print("Total Supply:", totalSupply)
print("Addr Balance:", addr_balance)

#Tether Token Addr
tether_token_addr = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
teth_contract = w3.eth.contract(address=w3.to_checksum_address(tether_token_addr), abi=simplified_abi)
symbol = teth_contract.functions.symbol().call()
decimals = teth_contract.functions.decimals().call()
totalSupply = teth_contract.functions.totalSupply().call() / 10**decimals
addr_balance = teth_contract.functions.balanceOf(acc_address).call() / 10**decimals

#  Tether
print("===== %s =====" % symbol)
print("Total Supply:", totalSupply)
print("Addr Balance:", addr_balance)

#BNB Token Addr
bnb_token_addr = "0xB8c77482e45F1F44dE1745F52C74426C631bDD52"
bnb_contract = w3.eth.contract(address=w3.to_checksum_address(bnb_token_addr), abi=simplified_abi)
symbol = bnb_contract.functions.symbol().call()
decimals = bnb_contract.functions.decimals().call()
totalSupply = bnb_contract.functions.totalSupply().call() / 10**decimals
addr_balance = bnb_contract.functions.balanceOf(acc_address).call() / 10**decimals

#  BNB
print("===== %s =====" % symbol)
print("Total Supply:", totalSupply)
print("Addr Balance:", addr_balance)