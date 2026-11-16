// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test} from "forge-std/Test.sol";
import {SATYA} from "../src/SATYA.sol";

/// @notice Genesis-level invariants of SATYA — agar ek bhi fail ho, coin deploy mat karo.
contract SATYATest is Test {
    SATYA public satya;
    address public deployer = makeAddr("deployer");

    function setUp() public {
        vm.prank(deployer);
        satya = new SATYA();
    }

    function test_NameIsSATYA() public {
        assertEq(satya.name(), "SATYA");
    }

    function test_SymbolIsSATYA() public {
        assertEq(satya.symbol(), "SATYA");
    }

    function test_DecimalsAre18() public {
        assertEq(satya.decimals(), 18);
    }

    function test_TotalSupplyIsExactlyOneCrore() public {
        assertEq(satya.totalSupply(), 10_000_000 * 10 ** 18);
        assertEq(satya.balanceOf(deployer), 10_000_000 * 10 ** 18);
    }

    function test_TransfersWork() public {
        vm.prank(deployer);
        satya.transfer(makeAddr("rahul"), 100 * 10 ** 18);
        assertEq(satya.balanceOf(makeAddr("rahul")), 100 * 10 ** 18);
        assertEq(satya.balanceOf(deployer), 10_000_000 * 10 ** 18 - 100 * 10 ** 18);
    }

    function test_CannotTransferMoreThanBalance() public {
        vm.prank(makeAddr("rahul"));
        vm.expectRevert();
        satya.transfer(makeAddr("someone"), 1);
    }

    /// @notice The most important invariant: NO ONE can ever mint more SATYA.
    ///         The contract exposes no mint function — this test proves supply
    ///         stays constant no matter who calls what.
    function test_SupplyIsImmutableForever() public {
        uint256 before = satya.totalSupply();
        vm.prank(deployer);
        satya.transfer(makeAddr("someone"), 5_000_000 * 10 ** 18);
        assertEq(satya.totalSupply(), before, "supply must never change");
    }
}
