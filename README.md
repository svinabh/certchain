# CertChain

Certificate verification on blockchain — **invisible blockchain** design
(UPI in front, chain behind; users never touch crypto).

> Phase 1: blockchain core — blocks, SHA-256 hashing, light proof-of-work,
> chain linking and tamper detection. ~150 lines, zero dependencies.

## Quickstart

```bash
python3 -m venv .venv
.venv/bin/pip install pytest

# run the demos
.venv/bin/python -m certchain.tamper_demo       # Phase 1: tampering detected
.venv/bin/python -m certchain.forged_cert_demo  # Phase 2: forged certificate rejected
.venv/bin/python -m certchain.network_demo      # Phase 3: 3-node P2P sync + consensus
.venv/bin/python -m certchain.app_demo          # Phase 4: INVISIBLE blockchain (UPI → chain → verify)

# ya ek node manually chalao (port 8000+ — macOS pe 5000 AirPlay Receiver ka hai):
.venv/bin/python -m certchain.run_node --port 8000

# run the tests
.venv/bin/python -m pytest certchain/tests -v
```

## Structure

```
certchain/
├── core/
│   ├── constants.py    # genesis-level constants (immutable, fixed genesis timestamp)
│   ├── crypto.py       # hashing — single place for cryptography
│   ├── block.py        # Block: content, PoW mining, fingerprint
│   ├── wallet.py       # Wallet: Ed25519 keys, address, sign/verify
│   ├── records.py      # SignedRecord: signed transaction + verification
│   └── blockchain.py   # Blockchain: genesis, add_block, is_valid, from_dicts, validate_chain_dicts
├── network/
│   ├── node.py         # Flask node: /chain /mine /transactions/new /nodes/register /nodes/resolve
│   └── helpers.py      # NodeServer/free_port/wait_up — demos & tests share these
├── app/
│   ├── upi.py          # FakeUPIBank: ₹ simulation, receipts, refunds
│   ├── relayer.py      # Relayer: pay → sign → submit → mine → (refund on reject)
│   └── api.py          # App HTTP face: /accounts /issue /verify/<cert_id> — user ko crypto nahi dikhta
├── tests/
│   ├── test_core.py    # 4 tests: genesis, links, PoW, tamper detection
│   ├── test_wallet.py  # 6 tests: address, signatures, impersonation, forgery
│   ├── test_network.py # 9 tests: APIs, mempool, consensus (longest VALID chain)
│   └── test_app.py     # 6 tests: UPI, relayer fees, refund, verify flow
├── tamper_demo.py      # demo: edit one record → chain rejects it
├── forged_cert_demo.py # demo: fake certificate with wrong key → rejected
├── network_demo.py     # demo: 3 real HTTP nodes sync + resolve
├── app_demo.py         # demo: invisible blockchain end-to-end (UPI → issue → verify)
└── run_node.py         # CLI: ek node chalao (--port, --peers)
adversarial/
└── test_adversarial.py # 5 real-HTTP adversarial scenarios (dead peer, poisoned peer, split-brain...)
```

## Docs

- [PLAN.md](PLAN.md) — 6-phase learning plan
- [MASTERPLAN.md](MASTERPLAN.md) — 5-level ladder to mainnet
- [FEATURES.md](FEATURES.md) — full feature menu
- [ROADMAP.md](ROADMAP.md) — 12 phases, shuru se mainnet
- [CHAIN-COIN-SPEC.md](CHAIN-COIN-SPEC.md) — coin: 1 crore supply
- [DEPLOYMENT.md](DEPLOYMENT.md) — deployment guide
