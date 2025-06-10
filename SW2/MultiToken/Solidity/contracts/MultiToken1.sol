// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "hardhat/console.sol";

contract MultiToken is ERC1155, Ownable {
    using Strings for uint256;

    // Token ID counters
    uint256 public fungibleTokenId = 0; //FT IDs start from 0
    uint256 public nonFungibleTokenId = 10000; // NFT IDs start from 10000 to separate from fungible

    // Token supply tracking
    mapping(uint256 => uint256) public maxSupply;
    mapping(uint256 => uint256) public currentSupply;
    mapping(uint256 => bool) public isFungible;
    mapping(uint256 => string) public tokenURIs;

    // Base URI
    string private _baseURI;

    constructor(
        string memory baseURI_,
        address initialOwner
    ) ERC1155(baseURI_) Ownable(initialOwner) {
        _baseURI = baseURI_;
    }

    // Create a new fungible token
    function createFungibleToken(
        uint256 initialSupply,
        uint256 _maxSupply,
        string memory tokenURI
    ) external onlyOwner {
        require(
            _maxSupply >= initialSupply,
            "Initial supply exceeds max supply"
        );

        fungibleTokenId++;
        uint256 newTokenId = fungibleTokenId;

        maxSupply[newTokenId] = _maxSupply;
        isFungible[newTokenId] = true;
        tokenURIs[newTokenId] = tokenURI;

        _mint(msg.sender, newTokenId, initialSupply, "");
        currentSupply[newTokenId] = initialSupply;
    }

    // Create a new non-fungible token (NFT)
    function createNonFungibleToken(string memory tokenURI) external onlyOwner {
        nonFungibleTokenId++;
        uint256 newTokenId = nonFungibleTokenId;

        maxSupply[newTokenId] = 1; // NFTs have max supply of 1
        isFungible[newTokenId] = false;
        tokenURIs[newTokenId] = tokenURI;

        _mint(msg.sender, newTokenId, 1, "");
        currentSupply[newTokenId] = 1;
    }

    // Mint additional fungible tokens (if supply allows)
    function mintFungible(uint256 tokenId, uint256 amount) external onlyOwner {
        require(isFungible[tokenId], "Not a fungible token");
        require(
            currentSupply[tokenId] + amount <= maxSupply[tokenId],
            "Exceeds max supply"
        );

        _mint(msg.sender, tokenId, amount, "");
        currentSupply[tokenId] += amount;
    }

    // Override URI function to include our token URIs
    function uri(uint256 tokenId) public view override returns (string memory) {
        return string(abi.encodePacked(_baseURI, tokenURIs[tokenId]));
    }

    // Set base URI
    function setBaseURI(string memory newBaseURI) external onlyOwner {
        _baseURI = newBaseURI;
    }
}
