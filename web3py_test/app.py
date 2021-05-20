import json
from web3 import Web3 

infura_url = "https://ropsten.infura.io/v3/289f98742e744795a5ee56380c7d3d99"
web3 = Web3(Web3.HTTPProvider(infura_url))

print(web3.isConnected())
print(web3.eth.blockNumber)

balance = web3.eth.getBalance("0x04Af3B69B569a74590FA39E22cF48fdf07CE142f")

print(web3.fromWei(balance, 'ether'))