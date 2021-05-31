import os
import json

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

    ganache_url = "http://127.0.0.1:8545"
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
        # 发布一个转账transaction，从默认账户1转账到连接的metamask账户
        account_1 = web3.eth.accounts[0]
        account_2 = web3.eth.accounts[1]
        account_3 = '0x04Af3B69B569a74590FA39E22cF48fdf07CE142f'

        private_key = 'cdd65737c197cfc401c7fe82d344c52edacc003503e32e3e60defa6e36c80340'

        nonce = web3.eth.getTransactionCount(account_1)
        tx = {
            'nonce': nonce,
            'to': account_3,
            'value': web3.toWei(1, 'ether'),
            'gas': 2000000,
            'gasPrice': web3.toWei('50', 'gwei')
        }
        signed_tx = web3.eth.account.signTransaction(tx, private_key)
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return 'successful'

    @app.route('/tutorial/reentrancy')
    def reentrancy():
        return render_template('reentrancy.html', result1=None, result2=None)

    @app.route('/tutorial/reentrancy/Game_deployment')
    def Game_deploy():
        # 为演示reentrancy部署两个合约，受害者合约以及攻击者合约
        # 受害者由默认账户部署，攻击者由用户的metamask账户部署
        web3.eth.defaultAccount = web3.eth.accounts[0]

        bytecode_Game = '608060405234801561001057600080fd5b5061045d806100206000396000f30060806040526004361061006d576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff1680632e1a7d4d1461007257806375807250146100b7578063c71daccb1461010e578063d0e30db014610139578063d5d44d801461015b575b600080fd5b34801561007e57600080fd5b5061009d600480360381019080803590602001909291905050506101b2565b604051808215151515815260200191505060405180910390f35b3480156100c357600080fd5b506100f8600480360381019080803573ffffffffffffffffffffffffffffffffffffffff1690602001909291905050506102f2565b6040518082815260200191505060405180910390f35b34801561011a57600080fd5b5061012361033a565b6040518082815260200191505060405180910390f35b610141610359565b604051808215151515815260200191505060405180910390f35b34801561016757600080fd5b5061019c600480360381019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190505050610419565b6040518082815260200191505060405180910390f35b6000816000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020541015156102e8573373ffffffffffffffffffffffffffffffffffffffff168260405160006040518083038185875af19250505050816000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825403925050819055507f884edad9ce6fa2440d8a54cc123490eb96d2768479d49ff9c7366125a94243643383604051808373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018281526020019250505060405180910390a1600190506102ed565b600090505b919050565b60008060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020549050919050565b60003073ffffffffffffffffffffffffffffffffffffffff1631905090565b6000346000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825401925050819055507fe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c3334604051808373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018281526020019250505060405180910390a16001905090565b600060205280600052604060002060009150905054815600a165627a7a723058203dc8f7bb54f97af8e1b5ef59ae05c1e3528ec5e5707ea8878cced6cd43b3a0030029'
        abi = json.loads('[{"constant":false,"inputs":[{"name":"amount","type":"uint256"}],"name":"withdraw","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"to","type":"address"}],"name":"creditOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"checkBalance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[{"name":"","type":"bool"}],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"credit","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":false,"name":"_who","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"_who","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"Withdraw","type":"event"}]')
        ReentrancyGame = web3.eth.contract(abi=abi, bytecode=bytecode_Game)

        tx_hash = ReentrancyGame.constructor().transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

        contract = web3.eth.contract(
            address = tx_receipt.contractAddress,
            abi = abi
        )

        global contract_G
        contract_G = contract

        return render_template('reentrancy.html', result1=contract_G.address)

        # tx_hash = contract.functions.deposit().transact({
        #     'to': contract.address,
        #     'from': web3.eth.defaultAccount,
        #     'value': 100
        #     })
        # tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
        # return str(contract.functions.checkBalance().call())

    @app.route('/tutorial/reentrancy/Attack_deployment')
    def Attack_deploy():
        web3.eth.defaultAccount = web3.eth.accounts[1]

        bytecode_Attack = '60806040526040516020806106608339810180604052810190808051906020019092919050505033600160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217905550806000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217905550506105a9806100b76000396000f30060806040526004361061006d576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff1680634ad69f4e1461013c5780634f4687251461016b5780639e5faafc146101c2578063c71daccb146101f1578063f8a8fd6d1461021c575b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16632e1a7d4d60016040518263ffffffff167c010000000000000000000000000000000000000000000000000000000002815260040180828152602001915050602060405180830381600087803b1580156100fe57600080fd5b505af1158015610112573d6000803e3d6000fd5b505050506040513d602081101561012857600080fd5b810190808051906020019092919050505050005b34801561014857600080fd5b5061015161024b565b604051808215151515815260200191505060405180910390f35b34801561017757600080fd5b506101806102d4565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b3480156101ce57600080fd5b506101d76102f9565b604051808215151515815260200191505060405180910390f35b3480156101fd57600080fd5b50610206610492565b6040518082815260200191505060405180910390f35b34801561022857600080fd5b506102316104b1565b604051808215151515815260200191505060405180910390f35b6000600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166108fc3073ffffffffffffffffffffffffffffffffffffffff16319081150290604051600060405180830381858888f193505050501580156102cc573d6000803e3d6000fd5b506001905090565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b60008060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1663d0e30db060016040518263ffffffff167c01000000000000000000000000000000000000000000000000000000000281526004016020604051808303818588803b15801561038157600080fd5b505af1158015610395573d6000803e3d6000fd5b50505050506040513d60208110156103ac57600080fd5b8101908080519060200190929190505050506000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16632e1a7d4d60016040518263ffffffff167c010000000000000000000000000000000000000000000000000000000002815260040180828152602001915050602060405180830381600087803b15801561044f57600080fd5b505af1158015610463573d6000803e3d6000fd5b505050506040513d602081101561047957600080fd5b8101908080519060200190929190505050506001905090565b60003073ffffffffffffffffffffffffffffffffffffffff1631905090565b60008060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1663d0e30db060026040518263ffffffff167c01000000000000000000000000000000000000000000000000000000000281526004016020604051808303818588803b15801561053957600080fd5b505af115801561054d573d6000803e3d6000fd5b50505050506040513d602081101561056457600080fd5b81019080805190602001909291905050505060019050905600a165627a7a723058201b8c14292f7886424d34f9f61b15b0f92ecaad078ccca9dc750bbd86f2c761560029'
        abi = json.loads('[{"constant":false,"inputs":[],"name":"geteth","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"regame","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"attack","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"checkBalance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"test","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"addr","type":"address"}],"payable":true,"stateMutability":"payable","type":"constructor"},{"payable":true,"stateMutability":"payable","type":"fallback"}]')
        ReentrancyAttack = web3.eth.contract(abi=abi, bytecode=bytecode_Attack)

        tx_hash = ReentrancyAttack.constructor(contract_G.address).transact({
            'value': 5
            })
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

        contract = web3.eth.contract(
            address = tx_receipt.contractAddress,
            abi = abi
            )

        global contract_A
        contract_A = contract

        return render_template('reentrancy.html', result1=contract_G.address, result2=contract_A.address)

    @app.route('/tutorial/reentrancy/attack')
    def reentrancy_attack():
        tx_hash = contract_A.functions.attack().transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
        return str(contract_A.functions.checkBalance().call())

    @app.route('/challenge')
    def challenge():
        return render_template('challenge.html')

    return app

