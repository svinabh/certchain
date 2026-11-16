// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script} from "forge-std/Script.sol";
import {ConstantExchangeRatePricer} from "../src/ConstantExchangeRatePricer.sol";

/// @notice Deploys the SATYA↔ETH exchange rate pricer for the CGT Orbit chain.
/// Rate: 1 ETH = 100 SATYA (illustrative — fixed at deploy).
contract DeployPricer is Script {
    function run() public returns (address pricer) {
        vm.startBroadcast();
        pricer = address(new ConstantExchangeRatePricer(100 * 10 ** 18));
        vm.stopBroadcast();
    }
}
