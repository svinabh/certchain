"""Adversarial integration tests — REAL multi-node HTTP attacks on CertChain.

Spawns real Flask/Werkzeug HTTP servers on random free ports (NodeServer
pattern copied from certchain/network_demo.py) and runs 5 adversarial
scenarios against them:

1. SANITY CONVERGENCE    3 nodes, mine on one, /nodes/resolve on the others
                         → all 3 chains converge (same length, same top hash).
2. DEAD PEER RESILIENCE  a peer entry pointing at a port with no listener →
                         resolve returns 200 fast, chain untouched.
3. POISONED PEER         a peer whose chain contains a FORGED record (signed
                         with the hacker's key but claiming another wallet's
                         address, mined directly via config["STATE"]) →
                         must NOT be adopted despite being the longer chain.
4. SPLIT-BRAIN           two independent chains (2 blocks vs 3 blocks) →
                         longest-valid reconciliation, loser adopts winner.
5. DUPLICATE MEMPOOL     same signed record POSTed twice → 201 then 400
                         "duplicate"; single mine, mempool never doubles.

READ-ONLY wrt certchain/: any failure here documents a product bug — the
tests never patch certchain code.
"""

import socket
import threading
import time
from contextlib import contextmanager

import requests
from werkzeug.serving import make_server

from certchain.core.records import SignedRecord
from certchain.core.wallet import Wallet
from certchain.network.node import create_app, validate_chain_dicts

CLIENT_TIMEOUT = 15        # client-side safety net for normal HTTP calls (s)
MINE_TIMEOUT = 60          # PoW ("0000" prefix) can take a few seconds
RESOLVE_DEADLINE = 10.0    # scenario 2: resolve must finish well under 10s
WAIT_UP_TRIES = 100


# --------------------------------------------------------------------- infra

class NodeServer(threading.Thread):
    """One real HTTP node running in its own daemon thread.

    Same pattern as certchain/network_demo.py, plus:
      * keeps a handle to the Flask app (for config["STATE"] tampering)
      * stop() is idempotent and safe for never-started servers
    """

    def __init__(self, port: int):
        super().__init__(daemon=True)
        self.port = port
        self.app = create_app(port)
        self.server = make_server("127.0.0.1", port, self.app, threaded=True)

    @property
    def state(self):
        """Direct in-memory NodeState access — for adversarial tampering."""
        return self.app.config["STATE"]

    def run(self) -> None:
        self.server.serve_forever()

    def stop(self) -> None:
        # shutdown() blocks forever if serve_forever was never entered,
        # so only call it on a server that actually started.
        if self.is_alive():
            self.server.shutdown()
        self.server.server_close()
        self.join(timeout=5)


def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def spawn_node() -> NodeServer:
    """Bind a server to a fresh free port (retries on rare port races)."""
    for _ in range(50):
        try:
            return NodeServer(free_port())
        except OSError:
            continue  # port snatched between close() and bind — try again
    raise RuntimeError("could not find a free port for node server")


def wait_up(url: str, tries: int = WAIT_UP_TRIES) -> None:
    for _ in range(tries):
        try:
            requests.get(f"{url}/health", timeout=1)
            return
        except requests.RequestException:
            time.sleep(0.1)
    raise RuntimeError(f"node did not come up: {url}")


@contextmanager
def node_cluster(*names):
    """Spawn named real HTTP nodes; guarantee shutdown even on test failure.

    Ports are allocated one-at-a-time right before each server binds, so the
    OS can never hand the same ephemeral port to two servers in one cluster.
    """
    servers = {}
    try:
        for name in names:
            server = spawn_node()
            server.start()
            servers[name] = server
        urls = {name: f"http://127.0.0.1:{servers[name].port}" for name in names}
        for url in urls.values():
            wait_up(url)
        yield servers, urls
    finally:
        for server in servers.values():
            server.stop()


# ------------------------------------------------------------ HTTP helpers

def health(url: str) -> dict:
    return requests.get(f"{url}/health", timeout=CLIENT_TIMEOUT).json()


def chain_body(url: str) -> dict:
    return requests.get(f"{url}/chain", timeout=CLIENT_TIMEOUT).json()


def top_hash(url: str) -> str:
    return chain_body(url)["chain"][-1]["hash"]


def register_peers(url: str, peers) -> dict:
    resp = requests.post(
        f"{url}/nodes/register", json={"peers": list(peers)}, timeout=CLIENT_TIMEOUT
    )
    assert resp.status_code == 201, f"register failed: {resp.text}"
    return resp.json()


def resolve(url: str) -> dict:
    resp = requests.get(f"{url}/nodes/resolve", timeout=CLIENT_TIMEOUT)
    assert resp.status_code == 200, f"resolve failed: {resp.text}"
    return resp.json()


def new_transaction(url: str, record: dict):
    return requests.post(
        f"{url}/transactions/new", json=record, timeout=CLIENT_TIMEOUT
    )


def mine(url: str) -> dict:
    resp = requests.post(f"{url}/mine", timeout=MINE_TIMEOUT)
    assert resp.status_code == 201, f"mine failed: {resp.text}"
    return resp.json()


def pending(url: str) -> dict:
    return requests.get(f"{url}/pending", timeout=CLIENT_TIMEOUT).json()


def signed_record_dict(wallet: Wallet, cert_id: str, data: str) -> dict:
    """Properly signed record dict — the 'honest client' payload."""
    record = SignedRecord(
        record_type="ISSUE",
        cert_id=cert_id,
        data=data,
        timestamp=time.time(),
        signer=wallet.address,
    )
    record.sign(wallet)
    assert record.verification_failure() is None
    return record.to_dict()


# ------------------------------------------------------------------ tests

def test_1_sanity_convergence_three_nodes_sync():
    university = Wallet.generate()
    with node_cluster("node1", "node2", "node3") as (servers, urls):
        # node2/node3 register node1 as peer
        node1_addr = f"127.0.0.1:{servers['node1'].port}"
        register_peers(urls["node2"], [node1_addr])
        register_peers(urls["node3"], [node1_addr])

        # university signs a record → POST to node1 → mine
        record = signed_record_dict(university, "CERT-ADV-0001", "Asha, B.Tech CSE, 2026")
        resp = new_transaction(urls["node1"], record)
        assert resp.status_code == 201, resp.text
        mined = mine(urls["node1"])
        assert mined["chain_length"] == 2

        # node2/node3 resolve → should adopt node1's 2-block chain
        for name in ("node2", "node3"):
            body = resolve(urls[name])
            assert body["chain_length"] == 2, f"{name} did not sync: {body}"

        # all 3 nodes: same length, same top block hash, /health valid
        lengths, tops = set(), set()
        for name in ("node1", "node2", "node3"):
            h = health(urls[name])
            assert h["valid"] is True, f"{name} reports invalid chain"
            lengths.add(h["chain_length"])
            tops.add(top_hash(urls[name]))
        assert lengths == {2}, f"chain lengths diverged: {lengths}"
        assert len(tops) == 1, f"top block hashes diverged: {tops}"


def test_2_dead_peer_resilience():
    with node_cluster("A") as (servers, urls):
        # a port where NO server is listening (freshly closed socket)
        dead_port = free_port()
        register_peers(urls["A"], [f"127.0.0.1:{dead_port}"])

        start = time.monotonic()
        # client safety net slightly above the deadline; must never trip
        resp = requests.get(f"{urls['A']}/nodes/resolve", timeout=RESOLVE_DEADLINE + 5)
        elapsed = time.monotonic() - start

        assert resp.status_code == 200
        assert elapsed < RESOLVE_DEADLINE, (
            f"resolve against dead peer took {elapsed:.1f}s (>10s)"
        )
        body = resp.json()
        assert "unchanged" in body["message"], body
        assert body["chain_length"] == 1, body

        # node still healthy, own chain untouched
        h = health(urls["A"])
        assert h["chain_length"] == 1
        assert h["valid"] is True


def test_3_poisoned_peer_chain_rejected():
    with node_cluster("A", "B") as (servers, urls):
        hacker = Wallet.generate()
        victim = Wallet.generate()

        # FORGERY: signed with the hacker's private key, but the record
        # claims victim's address as the signer (impersonation attempt).
        forged = SignedRecord(
            record_type="ISSUE",
            cert_id="CERT-EVIL-0001",
            data="Ghost University, PhD in Nothing, 2026",
            timestamp=time.time(),
            signer=victim.address,          # claimed identity != real key holder
        )
        forged.sign(hacker)                 # signs with hacker's key anyway
        assert forged.verification_failure() is not None

        # Poison node B directly through its Flask app's config["STATE"]:
        # mine the forged record straight into B's in-memory chain.
        b_state = servers["B"].state
        b_state.chain.add_block([forged.to_dict()])
        assert len(b_state.chain.blocks) == 2

        # B now serves a 2-block chain whose block 1 carries a forged record
        b_chain_dicts = chain_body(urls["B"])["chain"]
        reason = validate_chain_dicts(b_chain_dicts)
        assert reason is not None, "validate_chain_dicts accepted a poisoned chain"
        assert "impersonation" in reason or "rejected" in reason, reason

        # A (genesis only) sees a LONGER peer — only validation can save it
        register_peers(urls["A"], [f"127.0.0.1:{servers['B'].port}"])
        body = resolve(urls["A"])
        assert "unchanged" in body["message"], body
        assert body["chain_length"] == 1, body

        h = health(urls["A"])
        assert h["chain_length"] == 1
        assert h["valid"] is True, "A adopted or corrupted state after poisoned peer"


def test_4_split_brain_reconciliation():
    university = Wallet.generate()
    with node_cluster("A", "B") as (servers, urls):
        # A: mine record1 → 2 blocks
        r1 = signed_record_dict(university, "CERT-SPLIT-0001", "Ravi, B.Com, 2026")
        assert new_transaction(urls["A"], r1).status_code == 201
        assert mine(urls["A"])["chain_length"] == 2

        # B (independent, NOT connected yet): mine record2 and record3 in
        # SEPARATE blocks → 3 blocks total (longer than A's 2)
        r2 = signed_record_dict(university, "CERT-SPLIT-0002", "Sana, B.Sc Math, 2026")
        r3 = signed_record_dict(university, "CERT-SPLIT-0003", "Vikram, B.A. Hist, 2026")
        assert new_transaction(urls["B"], r2).status_code == 201
        assert mine(urls["B"])["chain_length"] == 2  # 2 blocks so far
        assert new_transaction(urls["B"], r3).status_code == 201
        assert mine(urls["B"])["chain_length"] == 3

        # split-brain confirmed: divergent lengths AND divergent top hashes
        assert chain_body(urls["A"])["length"] == 2
        assert chain_body(urls["B"])["length"] == 3
        assert top_hash(urls["A"]) != top_hash(urls["B"])

        # reconcile: A learns about B and resolves → adopts B's 3-block chain
        register_peers(urls["A"], [f"127.0.0.1:{servers['B'].port}"])
        body = resolve(urls["A"])
        assert "replaced" in body["message"], body
        assert body["chain_length"] == 3, body

        # B resolves too (no peers) → unchanged
        body_b = resolve(urls["B"])
        assert "unchanged" in body_b["message"], body_b
        assert body_b["chain_length"] == 3, body_b

        # final state: both 3 blocks, identical top hash, both valid
        assert chain_body(urls["A"])["length"] == 3
        assert chain_body(urls["B"])["length"] == 3
        assert top_hash(urls["A"]) == top_hash(urls["B"])
        assert health(urls["A"])["valid"] is True
        assert health(urls["B"])["valid"] is True


def test_5_duplicate_mempool_guard():
    university = Wallet.generate()
    with node_cluster("node1") as (servers, urls):
        record = signed_record_dict(university, "CERT-DUP-0001", "Neha, B.A. Econ, 2026")

        first = new_transaction(urls["node1"], record)
        assert first.status_code == 201, first.text

        second = new_transaction(urls["node1"], record)  # exact same dict again
        assert second.status_code == 400, second.text
        assert "duplicate" in second.json()["error"], second.json()

        # mempool did not double before mining
        assert pending(urls["node1"])["count"] == 1

        mined = mine(urls["node1"])
        assert mined["records_in_block"] == 1, mined  # mined exactly once

        # mempool drained, nothing duplicated into the block either
        assert pending(urls["node1"])["count"] == 0
        block_records = chain_body(urls["node1"])["chain"][-1]["records"]
        assert len(block_records) == 1
