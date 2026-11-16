/**
 * CertChain — Orbit L1 deployment (Phase 8) — CGT flow, FINAL
 * BROADCAST=1: SATYA approve + createRollup Sepolia pe broadcast.
 * Bina BROADCAST ke: sirf estimate/report.
 */

import { createPublicClient, createWalletClient, http } from 'viem';
import { sepolia } from 'viem/chains';
import { privateKeyToAccount } from 'viem/accounts';
import {
  prepareChainConfig,
  createRollupPrepareDeploymentParamsConfig,
  createRollupPrepareTransactionRequest,
  createRollupPrepareCustomFeeTokenApprovalTransactionRequest,
  createRollupEnoughCustomFeeTokenAllowance,
} from '@arbitrum/orbit-sdk';
import * as dotenv from 'dotenv';
import * as fs from 'node:fs';

dotenv.config({ path: '../satya-contracts/.env' });
dotenv.config();

const BROADCAST = process.env.BROADCAST === '1';
const RPC_URL = 'https://ethereum-sepolia-rpc.publicnode.com';
const SATYA_ADDRESS = '0x1b2a8d0d5aa8664f81a47298e4394271317e6551' as `0x${string}`;
const PRICER_ADDRESS = process.env.PRICER_ADDRESS as `0x${string}` | undefined;
const CHAIN_ID_L2 = 987654n; // CertChain L2 chain id (draft — mainnet se pehle final lock)

async function main() {
  const key = process.env.SEPOLIA_PRIVATE_KEY as `0x${string}` | undefined;
  if (!key) throw new Error('SEPOLIA_PRIVATE_KEY missing (.env me daalo)');
  if (!PRICER_ADDRESS) throw new Error('PRICER_ADDRESS missing (.env me daalo)');

  const deployer = privateKeyToAccount(key);
  const wallet = createWalletClient({ account: deployer, chain: sepolia, transport: http(RPC_URL) });
  const publicClient = createPublicClient({ chain: sepolia, transport: http(RPC_URL) });

  console.log('Deployer:', deployer.address);
  const balance = await publicClient.getBalance({ address: deployer.address });
  console.log('SepETH balance:', Number(balance) / 1e18);
  console.log('Fee token pricer:', PRICER_ADDRESS);
  console.log('Broadcast mode:', BROADCAST ? 'ON' : 'OFF (sirf estimate)');

  // 1) SATYA allowance for RollupCreator
  const enough = await createRollupEnoughCustomFeeTokenAllowance({
    nativeToken: SATYA_ADDRESS,
    account: deployer.address,
    publicClient,
  });
  console.log('SATYA allowance enough?', enough);

  if (!enough) {
    const approvalRequest = await createRollupPrepareCustomFeeTokenApprovalTransactionRequest({
      nativeToken: SATYA_ADDRESS,
      account: deployer.address,
      publicClient,
    });
    if (BROADCAST) {
      const approvalHash = await wallet.sendTransaction(approvalRequest as any);
      console.log('Approval tx:', approvalHash);
      await publicClient.waitForTransactionReceipt({ hash: approvalHash });
      console.log('✅ SATYA approved for RollupCreator');
    } else {
      console.log('[estimate-mode] approval tx to:', approvalRequest.to);
    }
  }

  // 2) chain config — CertChain L2
  const chainConfig = prepareChainConfig({
    chainId: Number(CHAIN_ID_L2),
    arbitrum: {
      InitialChainOwner: deployer.address,
      DataAvailabilityCommittee: false,
    },
  });

  // 3) deployment params — CGT: stakeToken = SATYA
  const params = await createRollupPrepareDeploymentParamsConfig(publicClient, {
    chainId: CHAIN_ID_L2,
    owner: deployer.address,
    stakeToken: SATYA_ADDRESS,
    chainConfig,
  });

  // 4) createRollup tx request — CGT ke liye nativeToken + feeTokenPricer zaroori
  const request = await createRollupPrepareTransactionRequest({
    params: {
      config: params,
      batchPosters: [deployer.address],
      validators: [deployer.address],
      nativeToken: SATYA_ADDRESS,
      feeTokenPricer: PRICER_ADDRESS,
    },
    account: deployer.address,
    publicClient,
  } as any);

  const gas = await publicClient.estimateGas({
    to: request.to as `0x${string}`,
    data: request.data,
    ...(request.value ? { value: request.value } : {}),
    account: deployer.address,
  });
  const gasPrice = await publicClient.getGasPrice();
  const estCost = gas * gasPrice;
  console.log('\n=== createRollup GAS ESTIMATE ===');
  console.log('gas:', gas.toString());
  console.log('estimated cost:', Number(estCost) / 1e18, 'SepETH');
  console.log('balance:', Number(balance) / 1e18, 'SepETH');
  console.log('sufficient?', estCost < balance ? 'YES' : 'NO — aur SepETH chahiye');

  fs.writeFileSync('tx-request.json', JSON.stringify({
    to: request.to,
    data: request.data,
    gas: gas.toString(),
  }, null, 2));
  if (!BROADCAST) {
    fs.writeFileSync('chain-config.json', JSON.stringify(chainConfig, null, 2));
    console.log('\n(BROADCAST=1 karke dobara chalao to asli deploy hoga)');
    console.log('tx-request.json saved (to + data + gas) — cast send se broadcast hoga');
    console.log('chain-config.json saved (nitro node isi se chalga)');
    return;
  }
  if (estCost >= balance) throw new Error('Balance insufficient — aur SepETH mine karo');

  // 5) SIGN + SEND — SATYA chain ka janam!
  const hash = await wallet.sendTransaction({
    to: request.to as `0x${string}`,
    data: request.data,
    ...(request.value ? { value: request.value } : {}),
    gas,
  } as any);
  console.log('\n🚀 createRollup tx:', hash);
  const receipt = await publicClient.waitForTransactionReceipt({ hash });
  console.log('✅ status:', receipt.status, '| block:', receipt.blockNumber.toString());
  fs.writeFileSync('chain-config.json', JSON.stringify(chainConfig, null, 2));
  fs.writeFileSync(
    'deploy-receipt.json',
    JSON.stringify(receipt, (_k, v) => (typeof v === 'bigint' ? v.toString() : v), 2),
  );
  console.log('deploy-receipt.json saved — rollup/inbox addresses isme honge');
}

main().catch((e) => {
  console.error('FAILED:', e);
  process.exit(1);
});
