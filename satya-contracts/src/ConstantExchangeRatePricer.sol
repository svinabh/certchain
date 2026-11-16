// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @notice Interface used by nitro to price custom gas tokens (from nitro-contracts src/bridge/ISequencerInbox.sol)
interface IFeeTokenPricer {
    function getExchangeRate() external view returns (uint256);
}

/// @title ConstantExchangeRatePricer — SATYA ↔ ETH fixed rate pricer
/// @notice Reference implementation from OffchainLabs/nitro-contracts
///         (test/foundry/fee-token-pricers — unaudited example, simplified).
///         Fixed rate: 1 ETH = 100 SATYA (illustrative demo pricing).
contract ConstantExchangeRatePricer is IFeeTokenPricer {
    uint256 immutable exchangeRate;

    constructor(uint256 _exchangeRate) {
        exchangeRate = _exchangeRate;
    }

    function getExchangeRate() external view returns (uint256) {
        return exchangeRate;
    }
}
