pragma solidity ^0.8.0;

contract King {
    address levelInstance;

    function King(address _levelInstance) {
        levelInstance = _levelInstance;
    }

    function give() public payable {
        levelInstance.call.value(msg.value)("");
    }
}
