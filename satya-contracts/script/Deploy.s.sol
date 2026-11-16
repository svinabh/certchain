// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script} from "forge-std/Script.sol";
import {SATYA} from "../src/SATYA.sol";

/// @notice Deploys SATYA — full 1-crore supply goes to the deployer wallet.
/// Usage (local anvil):
///   forge script script/Deploy.s.sol --rpc-url http://127.0.0.1:8545 --broadcast
/// Usage (Sepolia):
///   forge script script/Deploy.s.sol --rpc-url $SEPOLIA_RPC_URL --broadcast --private-key $PRIVATE_KEY
contract Deploy is Script {
    function run() public returns (SATYA satya) {
        vm.startBroadcast();
        satya = new SATYA();
        vm.stopBroadcast();
    }
}
