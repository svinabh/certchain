"""🎬 Phase 3 demo: 3 nodes ek network me — transaction, mining, auto-sync, consensus.

Run:  .venv/bin/python -m certchain.network_demo

Ye script khud 3 real HTTP servers spawn karta hai (apne-apne ports pe),
unhe jodta hai, node1 pe transaction mine karta hai, aur node2/node3 ke
resolve se sabko sync karta hai. Laptop ke 3 terminals ka zaroorat nahi!
"""

import time

import requests

from certchain.core.records import SignedRecord
from certchain.core.wallet import Wallet
from certchain.network.helpers import NodeServer, free_port, wait_up
from certchain.network.node import create_app


def banner(text: str) -> None:
    print("\n" + "=" * 64)
    print(text)
    print("=" * 64)


def main() -> None:
    banner("CertChain Phase 3 — 3-node P2P network (real HTTP servers)")

    ports = {name: free_port() for name in ("node1", "node2", "node3")}
    servers = {name: NodeServer(create_app(port), port) for name, port in ports.items()}
    for server in servers.values():
        server.start()
    urls = {name: f"http://127.0.0.1:{port}" for name, port in ports.items()}
    for url in urls.values():
        wait_up(url)
    print("  🟢 3 nodes live:", ", ".join(f"{n}:{ports[n]}" for n in sorted(urls)))

    banner("1) node2 aur node3 ko node1 ka pata dete hain (/nodes/register)")
    for name in ("node2", "node3"):
        requests.post(
            f"{urls[name]}/nodes/register",
            json={"peers": [f"127.0.0.1:{ports['node1']}"]},
            timeout=3,
        )
    for name, url in sorted(urls.items()):
        health = requests.get(f"{url}/health", timeout=3).json()
        print(f"  {name}: chain={health['chain_length']} peers={health['peers']}")

    banner("2) University node1 pe certificate issue karti hai (sign → mempool → mine)")
    university = Wallet.generate()
    record = SignedRecord(
        record_type="ISSUE", cert_id="CERT-2026-0001", data="Rahul, B.Tech CSE, 2026",
        timestamp=time.time(), signer=university.address,
    )
    record.sign(university)
    resp = requests.post(f"{urls['node1']}/transactions/new", json=record.to_dict(), timeout=3)
    print("  record:", resp.json()["message"])
    resp = requests.post(f"{urls['node1']}/mine", timeout=30)
    print("  mine:", resp.json()["message"], "→ chain_length =", resp.json()["chain_length"])
    print("  (node2 aur node3 abhi sirf genesis pe khade hain...)")

    banner("3) node2 aur node3 RESOLVE karte hain (longest valid chain rule)")
    for name in ("node2", "node3"):
        resp = requests.get(f"{urls[name]}/nodes/resolve", timeout=10)
        print(f"  {name}: {resp.json()['message']}")

    banner("4) Sab nodes ki chain ab SAME honi chahiye")
    top_hashes = set()
    for name, url in sorted(urls.items()):
        body = requests.get(f"{url}/chain", timeout=3).json()
        top_hashes.add(body["chain"][-1]["hash"])
        print(f"  {name}: chain={body['length']} top={body['chain'][-1]['hash'][:16]}...")
    print("  🎉 SAB SYNC ME HAIN ✅" if len(top_hashes) == 1 else "  ❌ SYNC FAIL!")

    banner("5) Round 2: node1 pe ek aur block — phir resolve — phir se sab same")
    record2 = SignedRecord(
        record_type="ISSUE", cert_id="CERT-2026-0002", data="Priya, B.Sc Physics, 2026",
        timestamp=time.time(), signer=university.address,
    )
    record2.sign(university)
    requests.post(f"{urls['node1']}/transactions/new", json=record2.to_dict(), timeout=3)
    requests.post(f"{urls['node1']}/mine", timeout=30)
    for name in ("node2", "node3"):
        requests.get(f"{urls[name]}/nodes/resolve", timeout=10)
    lengths, top_hashes = {}, set()
    for name, url in sorted(urls.items()):
        body = requests.get(f"{url}/chain", timeout=3).json()
        lengths[name] = body["length"]
        top_hashes.add(body["chain"][-1]["hash"])
    print("  chain lengths:", lengths)
    synced = len(top_hashes) == 1 and set(lengths.values()) == {3}
    print("  🎉 ROUND 2 BHI SYNC ✅" if synced else "  ❌ SYNC FAIL!")

    banner("Demo complete — nodes band kar rahe hain")
    for server in servers.values():
        server.server.shutdown()
    print("  Phase 3: chain ab network ban gayi 🚀")


if __name__ == "__main__":
    main()
