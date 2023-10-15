pragma solidity ^0.8.0;

contract SpaceExchange {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    mapping(address => mapping(string => uint256)) public balances; // Mapping of user balances for each cryptocurrency

    event Purchased(address indexed buyer, string ticker, uint256 quantity, uint256 total_cost);
    event Sold(address indexed seller, string ticker, uint256 quantity, uint256 total_received);

    // Allows anyone to send Ether directly to the contract's balance
    fallback() external payable { }
    receive() external payable { }

    function buy_crypto(string memory ticker, uint256 quantity, uint256 price_per_unit) public payable {
        require(price_per_unit > 0, "Invalid price.");

        uint256 cost = quantity * price_per_unit;  // Calculate total cost based on quantity
        require(msg.value == cost, "Sent Ether does not match the required amount.");

        balances[msg.sender][ticker] += quantity;

        emit Purchased(msg.sender, ticker, quantity, cost);
    }

    function sell_crypto(string memory ticker, uint256 quantity, uint256 price_per_unit) public {
        require(price_per_unit > 0, "Invalid price.");

        uint256 total_received = quantity * price_per_unit;
        require(address(this).balance >= total_received, "Contract does not have enough funds to buy.");

        balances[msg.sender][ticker] -= quantity;

        payable(msg.sender).transfer(total_received);

        emit Sold(msg.sender, ticker, quantity, total_received);
    }

    function get_crypto_balance(address user, string memory ticker) public view returns (uint256) {
        return balances[user][ticker];
    }
}
