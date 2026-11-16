// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/// @title SATYA — the native coin of CertChain
/// @author svinabh
/// @notice SATYA (सत्य — "truth") is the fixed-supply coin of CertChain, the
///         invisible blockchain for certificate verification.
///         Total supply: 1 crore (10,000,000) SATYA, minted ONCE in the
///         constructor to the deployer. There is NO mint function — the
///         supply is immutable by design, exactly as promised in
///         CHAIN-COIN-SPEC.md and the whitepaper.
/// @dev Deployer receives the full genesis supply. Distribution (community,
///      team vesting, treasury) happens via explicit transfers, all visible
///      on-chain — never via hidden inflation.
contract SATYA is ERC20 {
    /// @notice 1 crore SATYA with 18 decimals (standard, like ETH).
    uint256 public constant TOTAL_SUPPLY = 10_000_000 * 10 ** 18;

    constructor() ERC20("SATYA", "SATYA") {
        _mint(msg.sender, TOTAL_SUPPLY);
    }
}
