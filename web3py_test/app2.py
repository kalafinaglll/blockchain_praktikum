from web3 import Web3 

ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

print(web3.isConnected())

account_1 = "0xB2C6eD6a8C8941d3C9e957bD0643e19861770f4f"
account_2 = "0x04Af3B69B569a74590FA39E22cF48fdf07CE142f"

private_key = "c08278112bb866252846c04d9fdfb16efdd092cf81ede04fdfa0d481dd32fe16"

#get the nonce
nonce = web3.eth.getTransactionCount(account_1)

#build a transaction
tx = {
    'nonce': nonce,
    'to': account_2,
    'value': web3.toWei(1, 'ether'),
    'gas': 2000000,
    'gasPrice': web3.toWei('50', 'gwei')
}

#sign transaction
signed_tx = web3.eth.account.signTransaction(tx, private_key)

#send transaction
tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

#get transaction hash
print(web3.toHex(tx_hash))