pragma solidity ^0.4.24;

contract IntOverflow{

    function addNumber(uint8 a, uint8 b) public constant returns (uint){
        uint8 c;
        c = a+b;
        return c;
    }

}
