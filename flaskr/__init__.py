import os
import json
import time

from flask import Flask, render_template, request, url_for
from web3 import Web3

from hexbytes import HexBytes
from solcx import compile_files

class HexJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HexBytes):
            return obj.hex()
        return super().default(obj)

def create_app(test_config=None):
    app = Flask(__name__, static_folder='.', static_url_path='', instance_relative_config=True)
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
        return render_template('index.html')

    @app.route('/hall', methods=['GET', 'POST'])
    def hall():
        global user_account
        if request.method == "POST":
            user_account = request.form['account_address']
        else:
            user_account = None
        return render_template('base.html')

    @app.route('/tutorial/')
    def tutorial():
        return render_template('tutorial.html', result=web3.isConnected())


    #--------------------transaction example-------------------------- 

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
            'to': user_account,
            'value': web3.toWei(1, 'ether'),
            'gas': 2000000,
            'gasPrice': web3.toWei('50', 'gwei')
        }
        signed_tx = web3.eth.account.signTransaction(tx, private_key)
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return render_template('tutorial.html', result=web3.isConnected())

    #---------------------transaction end------------------------------------


    # ---------------reentrancy implementation----------------------------------------
    @app.route('/tutorial/reentrancy_intro/')
    def reentrancy_intro():
        page = request.args.get('page', "No page")
        return render_template('reentrancy_intro.html', page=page)

    @app.route('/tutorial/reentrancy')
    def reentrancy():
        text1 = "The 'ReentrancyGame' is the victim contract that we will attack. Click 'ReentrancyGame deployment' to finish the contrat deployment."
        return render_template('reentrancy.html', result1=None, result2=None, text1=text1)

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

        global contract_G, contract_A
        contract_G = contract
        contract_A = None

        text1 = "Now the deployment of 'ReentrancyGame' contract is finished. You can find the information of 'Contract Address', that is where this contract is successfully deployed."
        text2 = "You can do the same operation to the second contract. This one is attacker contract, which intends to exploit the vulnerability in 'ReentrancyGame'. Just deploy it!"

        return render_template('reentrancy.html', result1=contract_G.address, result2=contract_A.address if contract_A else None, text1=text1, text2=text2)

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

        text2 = "You can find the information of ReentrancyAttack's contract address. Next, let's check the balance of these two contract accounts"

        return render_template('reentrancy.html', result1=contract_G.address, result2=contract_A.address, text2=text2)

    @app.route('/tutorial/reentrancy/checkBalance', methods=['GET', 'POST'])
    def checkBalance():
        if request.method == 'POST':
            if request.form['submit_button'] == 'GA':
                Balance_G = contract_G.functions.checkBalance().call()
                Balance_A = contract_A.functions.checkBalance().call()
                if Balance_G == 0:
                    text1 = "Here is the value in this contract account. As you can see, the initial value is 0, because we haven't do any deposit. Then we can try to do it"
                    text2 = "Here is the value in this contract account. 5 means we have set a initial value 5 wei in this contract account."
                elif Balance_A != 5:
                    text1 = "You may noticed that something happened. Part of the value in 'ReentrancyGame' contract account is lost."
                    text2 = "Here we find we get some additional ether through attack action. We did exploit the vulnerability in contract 'ReentrancyGame' to successfully steal ether from it."
                else:
                    text1 = "Good job! We successfully deposit 100 wei into this contract account."
                    text2 = "Nothing happens to contract 'ReentrancyAttack'. The value of this contract account is still 5 wei. Now, everything is ready, we can implement the attack by just clicking 'Start to attack!'"
                return render_template('reentrancy.html', result1=contract_G.address, result2=contract_A.address if contract_A else None, Balance_G=Balance_G, Balance_A=Balance_A if contract_A else None, text1=text1, text2=text2) 
            elif request.form['submit_button'] == 'D':
                tx_hash = contract_G.functions.deposit().transact({
                'to': contract_G.address,
                'from': web3.eth.accounts[0],
                'value': 100
                })
                tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
                text1 = "You just finished the 100 wei deposit to ReentrancyGame contract, let's check the balance of these two contracts to see what happens to them."
                return render_template('reentrancy.html', result1=contract_G.address, result2=contract_A.address, text1=text1)
            else:
                return "nop"


    @app.route('/tutorial/reentrancy/attack')
    def reentrancy_attack():
        tx_hash = contract_A.functions.attack().transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
        text1 = "Nice! The attack works. What happens to the value of these two contracts?"
        text2 = "Let's check the value once more by clicking 'checkBalance'"
        return render_template('reentrancy.html', result1=contract_G.address, result2=contract_A.address, text1=text1, text2=text2) 

    # ---------------------reentrancy end------------------------------------------


    #--------------------------returncheck implementation------------------------------
    @app.route('/tutorial/returncheck_intro/')
    def returncheck_intro():
        page = request.args.get('page', "No page")
        return render_template('returncheck_intro.html', page=page)


    @app.route('/tutorial/returncheck')
    def returncheck():
        text1 = "'UncheckedGame' is the contrat with retrun value check vulnerability. Click 'UncheckedGame deployment' to deploy this contract on network"
        return render_template('returncheck.html', text1=text1)

    @app.route('/tutorial/returncheck/Game_deployment')
    def UncheckedGame_deploy():
        web3.eth.defaultAccount = web3.eth.accounts[0]

        bytecode_Game = '60806040526000805534801561001457600080fd5b506103f3806100246000396000f300608060405260043610610062576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806327e235e3146100675780632e1a7d4d146100be57806352d22518146100eb578063a50ec32614610116575b600080fd5b34801561007357600080fd5b506100a8600480360381019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190505050610134565b6040518082815260200191505060405180910390f35b3480156100ca57600080fd5b506100e96004803603810190808035906020019092919050505061014c565b005b3480156100f757600080fd5b5061010061029a565b6040518082815260200191505060405180910390f35b61011e6102b9565b6040518082815260200191505060405180910390f35b60016020528060005260406000206000915090505481565b80600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020541015151561019a57600080fd5b3373ffffffffffffffffffffffffffffffffffffffff166108fc829081150290604051600060405180830381858888f193505050505080600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825403925050819055508060008082825403925050819055507f884edad9ce6fa2440d8a54cc123490eb96d2768479d49ff9c7366125a94243643382604051808373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018281526020019250505060405180910390a150565b60003073ffffffffffffffffffffffffffffffffffffffff1631905090565b600034600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825401925050819055503460008082825401925050819055507f67d0e209d76ed24370106b1fd0fc1c82de411f7b72ba3d92736b75fe4add443a3334604051808373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018281526020019250505060405180910390a1600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020549050905600a165627a7a72305820a8d46972f26515e0541ebdb0f7caebe9383ffc21186637da01cbe90f49752e6b0029'
        abi = json.loads('[{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balances","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_amount","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"ownedEth","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"deposite","outputs":[{"name":"","type":"uint256"}],"payable":true,"stateMutability":"payable","type":"function"},{"anonymous":false,"inputs":[{"indexed":false,"name":"_who","type":"address"},{"indexed":false,"name":"_amount","type":"uint256"}],"name":"Deposite","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"_who","type":"address"},{"indexed":false,"name":"_amount","type":"uint256"}],"name":"Withdraw","type":"event"}]')
        UncheckedGame = web3.eth.contract(abi=abi, bytecode=bytecode_Game)

        tx_hash = UncheckedGame.constructor().transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

        contract = web3.eth.contract(
            address = tx_receipt.contractAddress,
            abi = abi
        )

        global contract_G1, contract_R1
        contract_G1 = contract
        contract_R1 = None

        text1 = "After the deployment operation, we can find the information of Contract Address, which means the address of this contract on blockchain."
        text2 = "'RevertContract' is a contrat used to exploit the vulnerability in 'UncheckedGame'. Click 'RevertContract deployment' to finish the deployment."

        return render_template('returncheck.html', result1=contract_G1.address, result2=contract_R1.address if contract_R1 else None, text1=text1, text2=text2)

    @app.route('/tutorial/returncheck/Revert_deployment')
    def RevertContract_deploy():
        web3.eth.defaultAccount = web3.eth.accounts[1]

        bytecode_Attack = '608060405234801561001057600080fd5b506102c4806100206000396000f300608060405260043610610057576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff168063069f368c1461005c57806352d2251814610092578063acd7c750146100bd575b600080fd5b610090600480360381019080803573ffffffffffffffffffffffffffffffffffffffff1690602001909291905050506100fd565b005b34801561009e57600080fd5b506100a76101b6565b6040518082815260200191505060405180910390f35b6100fb600480360381019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803590602001909291905050506101d5565b005b600060405180807f6465706f73697465282900000000000000000000000000000000000000000000815250600a019050604051809103902090508173ffffffffffffffffffffffffffffffffffffffff1634827c01000000000000000000000000000000000000000000000000000000009004906040518263ffffffff167c010000000000000000000000000000000000000000000000000000000002815260040160006040518083038185885af19350505050505050565b60003073ffffffffffffffffffffffffffffffffffffffff1631905090565b600060405180807f77697468647261772875696e74323536290000000000000000000000000000008152506011019050604051809103902090508273ffffffffffffffffffffffffffffffffffffffff16817c01000000000000000000000000000000000000000000000000000000009004836040518263ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401808281526020019150506000604051808303816000875af192505050505050505600a165627a7a7230582020d471bbf64b7027dfd18851b4e333860b0475b57ff51f41ef7848ad4d0af06b0029'
        abi = json.loads('[{"constant":false,"inputs":[{"name":"_addr","type":"address"}],"name":"testDeposite","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[],"name":"ownedEth","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_addr","type":"address"},{"name":"_amount","type":"uint256"}],"name":"testWithdraw","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"}]')
        RevertContract = web3.eth.contract(abi=abi, bytecode=bytecode_Attack)

        tx_hash = RevertContract.constructor().transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

        contract = web3.eth.contract(
            address = tx_receipt.contractAddress,
            abi = abi
            )

        global contract_R1
        contract_R1 = contract

        text2 = "Here is the address of contract 'RevertContract'. Then we can just click 'checkBalance' to check the initial value of these two contracts."

        return render_template('returncheck.html', result1=contract_G1.address, result2=contract_R1.address, text2=text2)


    @app.route('/tutorial/returncheck/ownedEth', methods=['GET', 'POST'])
    def ownedEth():
        if request.method == 'POST':
            if request.form['submit_button'] == 'UR':
                Balance_G1 = contract_G1.functions.ownedEth().call()
                Balance_R1 = contract_R1.functions.ownedEth().call()
                Balance_RC=contract_G1.functions.balances(contract_R1.address).call()
                if Balance_G1 == 0:
                    text1 = "The balance of 'UncheckedGame' is 0"
                    text2 = "The balance of RevertContract is 0. Then we can use contract 'RevertContract' to deposit some ether in contract 'UncheckedGame'. Just click 'deposit', 100 wei is ready."
                elif Balance_RC == 80:
                    text1 = "The balance of contract 'UncheckedGame' is still 100 wei."
                    text2 = "The balance of contract 'RevertContract' is still 0. What happens? Does the 'withdraw' operation purely fail? Take your curious to check the balance of account 'RevertContract' in 'UncheckedGame' by clicking 'Balance of Account'."
                else:
                    text1 = "We can find the new balance (100 wei) of contract 'UncheckedGame', which means our deposit operation succeed in depositting ether in 'UncheckedGame'."
                    text2 = "There is no change to the balance of contract 'RevertContract'. Even though we operated on 'RevertContract', the 'deposit' module calls the true deposit function from 'UncheckedGame'. By the way, the deposited ehter is under the address of 'RevertContract'. Then check the balance of account 'RevertContract' in 'UncheckedGame' by click 'Balance of Account'."
                return render_template('returncheck.html', result1=contract_G1.address, result2=contract_R1.address if contract_R1 else None, Balance_G1=Balance_G1, Balance_R1=Balance_R1 if contract_R1 else None, text1=text1, text2=text2) 
            elif request.form['submit_button'] == 'D':
                tx_hash = contract_R1.functions.testDeposite(contract_G1.address).transact({
                'to': contract_R1.address,
                'from': web3.eth.accounts[1],
                'value': 100
                })
                tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
                text1 = "The deposit operation is executed successfully, check the value of both contracts once more to see the difference."
                return render_template('returncheck.html', result1=contract_G1.address, result2=contract_R1.address, text1=text1)
            elif request.form['submit_button'] == 'W':
                tx_hash = contract_R1.functions.testWithdraw(contract_G1.address, 20).transact({
                    'to': contract_R1.address,
                    'from': web3.eth.accounts[1]
                    })
                tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
                text1 = "'withdraw' is finished, let's check the balance to see what changes."
                return render_template('returncheck.html', result1=contract_G1.address, result2=contract_R1.address, text1=text1)
            elif request.form['submit_button'] == 'RC':
                Balance_RC = contract_G1.functions.balances(contract_R1.address).call()
                if Balance_RC == 100:
                    text1 = "This is the balance of account 'RevertContract', which means the amount of ether that contract 'RevertContract' have under its own account in contract 'UncheckedGame'"
                    text2 = "Then we can try to do 'withdraw', which is similar to 'deposit'. We operate on 'RevertContract' to call the function module on 'UncheckedGame'. Just click 'withdraw', we set the amount of withdrawed ether to 20 wei."
                else:
                    text1 = "Here is it! The balance of account 'RevertContract' in 'UncheckedGame' is changed to 80. That means the 'withdraw' operation did happen."
                    text2 = "However, the balance of contract 'RevertContract' is still 0. Nothing is transferred from 'UncheckedGame' to 'RevertContract'. The truth is because of the unchecked retrun value of low level call, even though the transfer operation stopped in the middle, ether was still decreased from the account of 'RevertContract'. This leads to the fact that contract 'RevertContract' loses this 20 wei from its account in 'UncheckedGame'."
                return render_template('returncheck.html', result1=contract_G1.address, result2=contract_R1.address if contract_R1 else None, Balance_RC=Balance_RC, Balance_G1=contract_G1.functions.ownedEth().call(), Balance_R1=contract_R1.functions.ownedEth().call() if contract_R1 else None, text1=text1, text2=text2)
            else:
                return "nop"


    #---------------------------returncheck end----------------------------------------


    #-----------------------challenge module------------------------------------------

    @app.route('/challenge')
    def challenge():
        return render_template('challenge.html')



    @app.route('/challenge/start')
    def challenge_start():
        # start challenge
        # htlc
        web3.eth.defaultAccount = web3.eth.accounts[0]
        #print(user_account)


        bytecode_HTLC = '608060405234801561001057600080fd5b5061136b806100206000396000f3fe6080604052600436106100705760003560e01c80637249fbb61161004e5780637249fbb614610191578063cfb51928146101e4578063e16c7d98146102c0578063f380a9fc146103a057610070565b8063335ef5bd146100755780635c2d49b3146100e15780636361514914610134575b600080fd5b6100cb6004803603606081101561008b57600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff16906020019092919080359060200190929190803590602001909291905050506103ef565b6040518082815260200191505060405180910390f35b3480156100ed57600080fd5b5061011a6004803603602081101561010457600080fd5b810190808035906020019092919050505061087e565b604051808215151515815260200191505060405180910390f35b34801561014057600080fd5b506101776004803603604081101561015757600080fd5b8101908080359060200190929190803590602001909291905050506108ec565b604051808215151515815260200191505060405180910390f35b34801561019d57600080fd5b506101ca600480360360208110156101b457600080fd5b8101908080359060200190929190505050610d79565b604051808215151515815260200191505060405180910390f35b3480156101f057600080fd5b506102aa6004803603602081101561020757600080fd5b810190808035906020019064010000000081111561022457600080fd5b82018360208201111561023657600080fd5b8035906020019184600183028401116401000000008311171561025857600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f82011690508083019250505050505050919291929050505061114f565b6040518082815260200191505060405180910390f35b3480156102cc57600080fd5b506102f9600480360360208110156102e357600080fd5b810190808035906020019092919050505061117a565b604051808973ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018873ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200187815260200186815260200185815260200184151515158152602001831515151581526020018281526020019850505050505050505060405180910390f35b3480156103ac57600080fd5b506103d9600480360360208110156103c357600080fd5b810190808035906020019092919050505061128f565b6040518082815260200191505060405180910390f35b6000803411610466576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260158152602001807f6d73672e76616c7565206d757374206265203e2030000000000000000000000081525060200191505060405180910390fd5b814281116104bf576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260238152602001806112c06023913960400191505060405180910390fd5b60023386348787604051602001808673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1660601b81526014018573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1660601b8152601401848152602001838152602001828152602001955050505050506040516020818303038152906040526040518082805190602001908083835b60208310610592578051825260208201915060208101905060208303925061056f565b6001836020036101000a038019825116818451168082178552505050505050905001915050602060405180830381855afa1580156105d4573d6000803e3d6000fd5b5050506040513d60208110156105e957600080fd5b81019080805190602001909291905050509150600082905061060a8361087e565b1561067d576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260178152602001807f436f6e747261637420616c72656164792065786973747300000000000000000081525060200191505060405180910390fd5b6040518061010001604052803373ffffffffffffffffffffffffffffffffffffffff1681526020018773ffffffffffffffffffffffffffffffffffffffff1681526020013481526020018681526020018581526020016000151581526020016000151581526020016000801b81525060008085815260200190815260200160002060008201518160000160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555060208201518160010160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555060408201518160020155606082015181600301556080820151816004015560a08201518160050160006101000a81548160ff02191690831515021790555060c08201518160050160016101000a81548160ff02191690831515021790555060e082015181600601559050508573ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff16847fc2d52c5a7eb98035421ede814491afb7d24632fdf15f6cfaf45d2ac864a8081a348989876040518085815260200184815260200183815260200182815260200194505050505060405180910390a450509392505050565b60008073ffffffffffffffffffffffffffffffffffffffff1660008084815260200190815260200160002060000160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1614159050919050565b6000826108f88161087e565b61096a576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260198152602001807f636f6e7472616374496420646f6573206e6f742065786973740000000000000081525060200191505060405180910390fd5b8383600281604051602001808281526020019150506040516020818303038152906040526040518082805190602001908083835b602083106109c1578051825260208201915060208101905060208303925061099e565b6001836020036101000a038019825116818451168082178552505050505050905001915050602060405180830381855afa158015610a03573d6000803e3d6000fd5b5050506040513d6020811015610a1857600080fd5b81019080805190602001909291905050506000808481526020019081526020016000206003015414610ab2576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252601c8152602001807f686173686c6f636b206861736820646f6573206e6f74206d617463680000000081525060200191505060405180910390fd5b853373ffffffffffffffffffffffffffffffffffffffff1660008083815260200190815260200160002060010160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1614610b89576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252601a8152602001807f776974686472617761626c653a206e6f7420726563656976657200000000000081525060200191505060405180910390fd5b6000151560008083815260200190815260200160002060050160009054906101000a900460ff16151514610c25576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252601f8152602001807f776974686472617761626c653a20616c72656164792077697468647261776e0081525060200191505060405180910390fd5b426000808381526020019081526020016000206004015411610c92576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260318152602001806113066031913960400191505060405180910390fd5b6000806000898152602001908152602001600020905086816006018190555060018160050160006101000a81548160ff0219169083151502179055508060010160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166108fc82600201549081150290604051600060405180830381858888f19350505050158015610d3c573d6000803e3d6000fd5b50877fd6fd4c8e45bf0c70693141c7ce46451b6a6a28ac8386fca2ba914044e0e2391660405160405180910390a260019550505050505092915050565b600081610d858161087e565b610df7576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260198152602001807f636f6e7472616374496420646f6573206e6f742065786973740000000000000081525060200191505060405180910390fd5b823373ffffffffffffffffffffffffffffffffffffffff1660008083815260200190815260200160002060000160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1614610ece576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260168152602001807f726566756e6461626c653a206e6f742073656e6465720000000000000000000081525060200191505060405180910390fd5b6000151560008083815260200190815260200160002060050160019054906101000a900460ff16151514610f6a576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252601c8152602001807f726566756e6461626c653a20616c726561647920726566756e6465640000000081525060200191505060405180910390fd5b6000151560008083815260200190815260200160002060050160009054906101000a900460ff16151514611006576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252601d8152602001807f726566756e6461626c653a20616c72656164792077697468647261776e00000081525060200191505060405180910390fd5b42600080838152602001908152602001600020600401541115611074576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260238152602001806112e36023913960400191505060405180910390fd5b6000806000868152602001908152602001600020905060018160050160016101000a81548160ff0219169083151502179055508060000160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166108fc82600201549081150290604051600060405180830381858888f19350505050158015611115573d6000803e3d6000fd5b50847f989b3a845197c9aec15f8982bbb30b5da714050e662a7a287bb1a94c81e2e70e60405160405180910390a260019350505050919050565b6000606082905060008151141561116c576000801b915050611175565b60208301519150505b919050565b600080600080600080600080600015156111938a61087e565b151514156111d4576000806000806000806000808797508696508595508460001b94508393508060001b905097509750975097509750975097509750611284565b60008060008b815260200190815260200160002090508060000160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff168160010160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff168260020154836003015484600401548560050160009054906101000a900460ff168660050160019054906101000a900460ff16876006015487975086965098509850985098509850985098509850505b919395975091939597565b6000816040516020018082815260200191505060405160208183030381529060405280519060200120905091905056fe74696d656c6f636b2074696d65206d75737420626520696e2074686520667574757265726566756e6461626c653a2074696d656c6f636b206e6f742079657420706173736564776974686472617761626c653a2074696d656c6f636b2074696d65206d75737420626520696e2074686520667574757265a265627a7a723158207be8b9ef943cfb3abf183497d7ec3e2dea28cd03139e659a32890c69dc9a884164736f6c63430005110032'
        abi = json.loads('[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"contractId","type":"bytes32"},{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":true,"internalType":"address","name":"receiver","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"bytes32","name":"hashlock","type":"bytes32"},{"indexed":false,"internalType":"uint256","name":"timelock","type":"uint256"},{"indexed":false,"internalType":"bytes32","name":"contractId_","type":"bytes32"}],"name":"LogHTLCNew","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"contractId","type":"bytes32"}],"name":"LogHTLCRefund","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"bytes32","name":"contractId","type":"bytes32"}],"name":"LogHTLCWithdraw","type":"event"},{"constant":false,"inputs":[{"internalType":"address payable","name":"_receiver","type":"address"},{"internalType":"bytes32","name":"_hashlock","type":"bytes32"},{"internalType":"uint256","name":"_timelock","type":"uint256"}],"name":"newContract","outputs":[{"internalType":"bytes32","name":"contractId","type":"bytes32"}],"payable":true,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"_contractId","type":"bytes32"}],"name":"refund","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes32","name":"_contractId","type":"bytes32"},{"internalType":"bytes32","name":"_preimage","type":"bytes32"}],"name":"withdraw","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"_contractId","type":"bytes32"}],"name":"getContract","outputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"receiver","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes32","name":"hashlock","type":"bytes32"},{"internalType":"uint256","name":"timelock","type":"uint256"},{"internalType":"bool","name":"withdrawn","type":"bool"},{"internalType":"bool","name":"refunded","type":"bool"},{"internalType":"bytes32","name":"preimage","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"_contractId","type":"bytes32"}],"name":"haveContract","outputs":[{"internalType":"bool","name":"exists","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"string","name":"source","type":"string"}],"name":"stringToBytes32","outputs":[{"internalType":"bytes32","name":"result","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes32","name":"plaintext","type":"bytes32"}],"name":"testSHA256","outputs":[{"internalType":"bytes32","name":"encrypto","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"}]')
        htlc = web3.eth.contract(abi=abi, bytecode=bytecode_HTLC)



        if os.path.exists('flaskr/session'):
            with open("flaskr/session","r") as session:
                    lines = session.readlines()

                    contract = web3.eth.contract(
                        address = lines[0].strip(),
                        abi = abi
                    )
                    addr_new_htlc = lines[1].strip()
                    status = get_contract(contract,addr_new_htlc)

                    return render_template('challenge.html', result1=contract.address, result2= addr_new_htlc, result3 = status)


        tx_hash = htlc.constructor().transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
        contract = web3.eth.contract(
            address = tx_receipt.contractAddress,
            abi = abi
        )

        global contract_HTLC
        contract_HTLC = contract
        #contract_A = None
        #print(contract.abi)
        with open("flaskr/session","w") as session:
            session.write(str(contract.address)+'\n')

        print(os.path.abspath("."))

        addr_new_htlc = initialize_contract(contract)
        addr_new_htlc = "0x"+addr_new_htlc

        with open("flaskr/session","a") as session:
            session.write(str(addr_new_htlc)+'\n')
        status = get_contract(contract,addr_new_htlc)



        with open("flaskr/challenges/ch1","r") as king:
            code_abi = king.readlines()

        ch1 = initialize_contract_ch(code_abi[0].strip(),code_abi[1].strip())
        with open("flaskr/session","a") as session:
            session.write(str(ch1.address)+'\n')
        global address_c1
        address_c1 = ch1.address

        with open("flaskr/session","r") as test:
            aaa = test.readlines()
            for x in aaa:
                print(x)


        with open("flaskr/challenges/ch2","r") as overflow:
            code_abi1 = overflow.readlines()
        ch2 = initialize_contract_ch(code_abi1[0].strip(),code_abi1[1].strip())
        with open("flaskr/session","a") as session:
            session.write(str(ch2.address)+'\n')


        with open("flaskr/challenges/ch3","r") as private_data:
            code_abi2 = private_data.readlines()
        ch3 = initialize_contract_ch(code_abi2[0].strip(),code_abi2[1].strip())
        with open("flaskr/session","a") as session:
            session.write(str(ch3.address)+'\n')


        with open("flaskr/challenges/ch4","r") as conseguess:
            code_abi3 = conseguess.readlines()
        ch4 = initialize_contract_ch(code_abi3[0].strip(),code_abi3[1].strip())
        with open("flaskr/session","a") as session:
            session.write(str(ch4.address)+'\n')


        with open("flaskr/challenges/ch5","r") as reentrancy:
            code_abi4 = reentrancy.readlines()
        ch5 = initialize_contract_ch(code_abi4[0].strip(),code_abi4[1].strip())
        with open("flaskr/session","a") as session:
            session.write(str(ch5.address)+'\n')
        balance_ch5 =ch5.functions.balances(ch5.address).call()
        if balance_ch5 == 0:
                tx_hash = ch5.functions.deposit().transact({
                    'to': ch5.address,
                    'from': web3.eth.accounts[0],
                    'value': 100
                })




        return render_template('challenge.html', result1=contract_HTLC.address, result2= addr_new_htlc, result3 = status)

    def initialize_contract(contract):
        user_account1 = "0xF10CC9735dc4816efA529921781Ea6a3Cd82D434"
        web3.eth.defaultAccount = web3.eth.accounts[0]
        key  = "0x66687aadf862bd776c8fc18b8e9f8e20089714856ee233b3902a591d0d5f2925"#"0x0000000000000000000000000000000000000000000000000000000000000000"
        #"S78DF6G53K4G689S3G":"0x5337384446364735334b34473638395333470000000000000000000000000000":"0xf075faafdc8a1211d3813752a2b8b634151ef44859e7ef5f0358eda775b8553d"

        t = int(int(time.time())+60*60*2.5)
        newContract = contract.functions.newContract(user_account1,key,t).transact({"value":100})
        newContract_receipt = web3.eth.waitForTransactionReceipt(newContract)

        test = web3.eth.getTransactionReceipt(newContract)

        logs = contract.events.LogHTLCNew().processReceipt(test)
        tx_dict = dict(logs[0])
        bytesid = dict(tx_dict)['args']['contractId']
        newcontract_addr = bytesid.hex()
     
        return newcontract_addr

    def get_contract(contract,addr_new_htlc):
        status = contract.functions.getContract(addr_new_htlc).call()
        print(status)
        if status[5] == True:
            return "congratulations!successfully finished challenge!"
        elif time.time() > status[4]:
            contract.functions.refund(addr_new_htlc).call()
            return "you have lost the game, time over!"
        else:
            tl = time.localtime(status[4])
            format_time = time.strftime("%Y-%m-%d %H:%M:%S", tl) 
            resttime = int(status[4] - time.time()) / 60
            return "please try harder! you have time until "+str(format_time)+" , you still have "+str(int(resttime))+" minutes to finish it"

    def initialize_contract_ch(bytecode_chg,abi_chg):
        bytecode_challenge=bytecode_chg
        abi = json.loads(abi_chg)
        challenge1 = web3.eth.contract(abi=abi, bytecode=bytecode_challenge)

        tx_hash = challenge1.constructor().transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
        contract = web3.eth.contract(
            address = tx_receipt.contractAddress,
            abi = abi
        )

        print("this is contrac address"+str(contract.address))
        return contract




    # @app.route('/your_challenges')
    # def show_():
    #     with open("flaskr/session","r") as session:
    #         lines = session.readlines()

    #     with open("flaskr/challenges/ch1") as king:
    #         bycode_abi = king.readlines()

    #     abi = bycode_abi[1]    

    #     contract = web3.eth.contract(
    #         address = lines[2].strip(),
    #         abi = abi
    #     )

    #     status = contract.functions.iskings().call()

    #     with open("flaskr/sol/ch1","r") as ch1:
    #         source = ch1.readlines()




    #     return render_template('challenge1.html', result2= lines[2], result3 = status, source_code=source)

    @app.route('/your_challenges/store', methods=['POST'])
    def storetext():
        web3.eth.defaultAccount = web3.eth.accounts[0]
        if request.method == "POST":
            # print(request.form['text'])
            if request.form['submit'] == 'submit1':
                filename = "flaskr/challenge1.sol"
                contractname = "flaskr/challenge1.sol:King"
            elif request.form['submit'] == 'submit5':
                filename = "flaskr/challenge5.sol"
                contractname = "flaskr/challenge5.sol:Reentrancy"

            with open(filename, "w") as sol:
                sol.write(str(request.form['text']) + "\n")

            contracts = compile_files(
                [filename],
                solc_version='0.8.0'
                )
            app_contract = contracts.pop(contractname)

            # abi = json.loads('[{"inputs":[{"internalType":"address","name":"_levelInstance","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"give","outputs":[],"stateMutability":"payable","type":"function"}]')
            # bytecode = "608060405234801561001057600080fd5b5060405161023d38038061023d8339818101604052810190610032919061008d565b806000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555050610108565b600081519050610087816100f1565b92915050565b6000602082840312156100a3576100a26100ec565b5b60006100b184828501610078565b91505092915050565b60006100c5826100cc565b9050919050565b600073ffffffffffffffffffffffffffffffffffffffff82169050919050565b600080fd5b6100fa816100ba565b811461010557600080fd5b50565b610126806101176000396000f3fe608060405260043610601c5760003560e01c80639e96a23a146021575b600080fd5b60276029565b005b60008054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1634604051606b9060cf565b60006040518083038185875af1925050503d806000811460a6576040519150601f19603f3d011682016040523d82523d6000602084013e60ab565b606091505b505050565b600060bb60008360e2565b915060c48260ed565b600082019050919050565b600060d88260b0565b9150819050919050565b600081905092915050565b5056fea2646970667358221220b58c9d2b602f5b9acc93616feb5a256584af5f366301e6026be495a72e994fd564736f6c63430008060033"

            King = web3.eth.contract(abi=app_contract['abi'], bytecode=app_contract['bin'])
            # King = web3.eth.contract(abi=abi, bytecode=bytecode)
            tx_hash = King.constructor(address_c1).transact({
                'value': 5
                })
            tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
            contract = web3.eth.contract(
                address=tx_receipt.contractAddress,
                abi=abi
                )
            contract.functions.give().call()
            return render_template('base.html')
        return "fail"

    @app.route('/your_challenges/1', methods=['GET', 'POST'])
    def ch1():
        with open("flaskr/session","r") as session:
            lines = session.readlines()

        with open("flaskr/challenges/ch1") as king:
            bycode_abi = king.readlines()

        abi = bycode_abi[1]    

        contract = web3.eth.contract(
            address = lines[2].strip(),
            abi = abi
        )

        status = contract.functions.iskings().call()
        if status == False:
            status = "not solved"
            token_ = "Try harder"
        else:
            status = "solved"
            token_ = "0x00001"
        with open("flaskr/sol/ch1","r") as ch1:
            source = ch1.readlines()

        if request.method == "POST":
            print(request.form['form1'])


        return render_template('challenge1.html', result2= contract.address, result3 = status, source_code=source,token=token_, page=1)


    @app.route('/your_challenges/2')
    def ch2():
        with open("flaskr/session","r") as session:
            lines = session.readlines()

        with open("flaskr/challenges/ch2") as king:
            bycode_abi = king.readlines()

        abi = bycode_abi[1]    

        contract = web3.eth.contract(
            address = lines[3].strip(),
            abi = abi
        )

        status = contract.functions.isof().call()
        if status == False:
            status = "not solved"
            token_ = "Try harder"
        else:
            status = "solved"
            token_ = "0x00001"

        with open("flaskr/sol/ch2","r") as ch2:
            source = ch2.readlines()




        return render_template('challenge1.html', result2= contract.address, result3 = status, source_code=source,token=token_, page=2)


    @app.route('/your_challenges/3')
    def ch3():
        with open("flaskr/session","r") as session:
            lines = session.readlines()

        with open("flaskr/challenges/ch3") as king:
            bycode_abi = king.readlines()

        abi = bycode_abi[1]    

        contract = web3.eth.contract(
            address = lines[4].strip(),
            abi = abi
        )

        status = contract.functions.locked().call()
        if status == True:
            status = "not solved"
            token_ = "Try harder"
        else:
            status = "solved"
            token_ = "0x00001"

        with open("flaskr/sol/ch3","r") as ch3:
            source = ch3.readlines()




        return render_template('challenge1.html', result2= contract.address, result3 = status, source_code=source,token=token_, page=3)


    @app.route('/your_challenges/4')
    def ch4():
        with open("flaskr/session","r") as session:
            lines = session.readlines()

        with open("flaskr/challenges/ch4") as king:
            bycode_abi = king.readlines()

        abi = bycode_abi[1]    

        contract = web3.eth.contract(
            address = lines[5].strip(),
            abi = abi
        )

        status = contract.functions.consecutiveWins().call()
        if status > 5 :
            status = "solved"
            token_ = "0x00001"
        else:
            status = "not solved"
            token_ = "Try harder"

        with open("flaskr/sol/ch4","r") as ch1:
            source = ch1.readlines()




        return render_template('challenge1.html', result2= contract.address, result3 = status, source_code=source,token=token_, page=4)

    @app.route('/your_challenges/5')
    def ch5():
        with open("flaskr/session","r") as session:
            lines = session.readlines()

        with open("flaskr/challenges/ch5") as king:
            bycode_abi = king.readlines()

        abi = bycode_abi[1]    

        contract = web3.eth.contract(
            address = lines[6].strip(),
            abi = abi
        )

        status = contract.functions.balanceOf(contract.address).call()
        if status < 100:
            status = "solved"
            token_ = "0x00001"
        else:
            status = "not solved"
            token_ = "Try harder"

        with open("flaskr/sol/ch5","r") as ch1:
            source = ch1.readlines()




        return render_template('challenge1.html', result2= contract.address, result3 = status, source_code=source,token=token_, page=5)

    return app

