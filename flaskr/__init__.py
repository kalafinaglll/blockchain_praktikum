import os

from flask import Flask, render_template
from web3 import Web3

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    ganache_url = "http://127.0.0.1:7545"
    web3 = Web3(Web3.HTTPProvider(ganache_url))

    @app.route('/')
    def index():
        # return 'Hello, here is bugs hunter platform'
        return render_template('base.html')

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/tutorial/')
    def tutorial():
        return render_template('tutorial.html', result=web3.isConnected())

    @app.route('/tutorial/transaction_example')
    def transaction():
        account_1 = web3.eth.accounts[0]
        account_2 = web3.eth.accounts[1]

        private_key = 'eff5732bcdff4791f82a095eb6894fc55578d7be7e0485848c2bc62f862f4b96'

        nonce = web3.eth.getTransactionCount(account_1)
        tx = {
            'nonce': nonce,
            'to': account_2,
            'value': web3.toWei(1, 'ether'),
            'gas': 2000000,
            'gasPrice': web3.toWei('50', 'gwei')
        }
        signed_tx = web3.eth.account.signTransaction(tx, private_key)
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return 'successful'

    @app.route('/tutorial/reentrancy')
    def reentrancy():
        web3.eth.defaultAccount = web3.eth.accounts[0]

        bytecode = '608060405234801561001057600080fd5b5061045d806100206000396000f30060806040526004361061006d576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff1680632e1a7d4d1461007257806375807250146100b7578063c71daccb1461010e578063d0e30db014610139578063d5d44d801461015b575b600080fd5b34801561007e57600080fd5b5061009d600480360381019080803590602001909291905050506101b2565b604051808215151515815260200191505060405180910390f35b3480156100c357600080fd5b506100f8600480360381019080803573ffffffffffffffffffffffffffffffffffffffff1690602001909291905050506102f2565b6040518082815260200191505060405180910390f35b34801561011a57600080fd5b5061012361033a565b6040518082815260200191505060405180910390f35b610141610359565b604051808215151515815260200191505060405180910390f35b34801561016757600080fd5b5061019c600480360381019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190505050610419565b6040518082815260200191505060405180910390f35b6000816000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020541015156102e8573373ffffffffffffffffffffffffffffffffffffffff168260405160006040518083038185875af19250505050816000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825403925050819055507f884edad9ce6fa2440d8a54cc123490eb96d2768479d49ff9c7366125a94243643383604051808373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018281526020019250505060405180910390a1600190506102ed565b600090505b919050565b60008060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020549050919050565b60003073ffffffffffffffffffffffffffffffffffffffff1631905090565b6000346000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825401925050819055507fe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c3334604051808373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018281526020019250505060405180910390a16001905090565b600060205280600052604060002060009150905054815600a165627a7a723058203dc8f7bb54f97af8e1b5ef59ae05c1e3528ec5e5707ea8878cced6cd43b3a0030029'
        abi = json.loads('[{"constant":false,"inputs":[{"name":"amount","type":"uint256"}],"name":"withdraw","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"to","type":"address"}],"name":"creditOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"checkBalance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[{"name":"","type":"bool"}],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"credit","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":false,"name":"_who","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"_who","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Withdraw","type":"event"}]')
        ReentrancyGame = web3.eth.contract(abi=abi, bytecode=bytecode)

        tx_hash = ReentrancyGame.constructor().transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

        contract = web3.eth.contract(
            address = tx_receipt.contractAddress,
            abi = abi
        )

        contract.functions.deposit().call()
        return str(contract.functions.checkBalance().call())

    @app.route('/challenge')
    def challenge():
        return render_template('challenge.html')

    return app

