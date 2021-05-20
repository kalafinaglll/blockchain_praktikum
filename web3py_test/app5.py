from web3 import Web3 

infura_url = "https://mainnet.infura.io/v3/289f98742e744795a5ee56380c7d3d99"
web3 = Web3(Web3.HTTPProvider(infura_url))

#inspect the latest block
latest = web3.eth.blockNumber
print(latest)
print(web3.eth.getBlock(latest))

#inspect multiple blocks of latest 10
for i in range(0, 10):
    print(web3.eth.getBlock(latest - i))

#web3 allows you to inspect transactions contained within a specific block\
#the hash is an information of this specific block
hash = '0x1198c142663a85d8b9b8b209d7903a6bf51b869abe17736c3e02bfe87c703869'
print(web3.eth.getTransactionByBlock(hash, 2))