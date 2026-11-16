"""Node — blockchain ka HTTP face. Har node = Flask server + chain + peers + mempool.

Endpoints:
  GET  /health            node info (chain length, peers, mempool, valid?)
  GET  /chain             poori chain JSON me
  GET  /pending           mempool (mining ka wait kar rahe records)
  POST /transactions/new  signed record accept (verify → mempool)
  POST /mine              pending records ka block mine karo
  POST /nodes/register    peers add karo
  GET  /nodes/resolve     consensus: peers se chains mangao, longest VALID adopt

Design rule: core/ ko network ka pata nahi — network core ko use karta hai.
"""

import logging
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Set, Tuple

import requests
from flask import Flask, jsonify, request

from certchain.core.blockchain import Blockchain, validate_chain_dicts
from certchain.core.records import SignedRecord

_RECORD_FIELDS = {
    "version", "record_type", "cert_id", "data",
    "timestamp", "signer", "public_key", "signature",
}


@dataclass
class NodeState:
    chain: Blockchain
    peers: Set[str] = field(default_factory=set)       # "host:port" — scheme ke bina
    mempool: List[dict] = field(default_factory=list)  # pending signed records


def normalize_peer(peer: str) -> Optional[str]:
    """'http://host:5001/' ya 'host:5001' → 'host:5001' (warna None)."""
    if not isinstance(peer, str) or not peer.strip():
        return None
    peer = peer.strip().removeprefix("http://").removeprefix("https://").rstrip("/")
    host, _, port = peer.partition(":")
    if not host or not port.isdigit():
        return None
    return f"{host}:{port}"


def _record_from_dict(data) -> Optional[SignedRecord]:
    """JSON dict → SignedRecord (shape galat ho to None)."""
    if not isinstance(data, dict) or not _RECORD_FIELDS.issubset(data):
        return None
    try:
        return SignedRecord(
            version=data["version"],
            record_type=data["record_type"],
            cert_id=data["cert_id"],
            data=data["data"],
            timestamp=data["timestamp"],
            signer=data["signer"],
            signature=data["signature"],
            public_key=data["public_key"],
        )
    except (TypeError, ValueError):
        return None


def http_fetch_chain(peer: str, timeout: float = 3.0) -> Optional[List[dict]]:
    """Peer se /chain fetch (fail ho to None — node offline ho sakta hai)."""
    try:
        resp = requests.get(f"http://{peer}/chain", timeout=timeout)
        return resp.json().get("chain")
    except (requests.RequestException, ValueError):
        return None


def resolve_consensus(
    state: NodeState, fetcher: Callable[[str], Optional[List[dict]]]
) -> Tuple[bool, Optional[str]]:
    """Longest VALID chain rule — hamari consensus strategy:

    1. Har peer se chain mangao (fetcher injectable hai — tests ke liye)
    2. Doosre network ki chain ignore (genesis hash match hona chahiye)
    3. Lambi chains par dhyan do, par sirf VALID wali (validate_chain_dicts)
    4. Sabse lambi valid chain adopt karo
    """
    own = state.chain.blocks
    own_genesis_hash = own[0].hash
    best: Optional[List[dict]] = None
    best_peer: Optional[str] = None
    for peer in sorted(state.peers):
        candidate = fetcher(peer)
        if not candidate:
            continue                                   # peer offline/garbage
        if candidate[0].get("hash") != own_genesis_hash:
            continue                                   # doosri network ki chain
        if len(candidate) <= len(own):
            continue                                   # hamari already badi/equal hai
        if validate_chain_dicts(candidate, state.chain.difficulty_prefix) is not None:
            continue                                   # invalid chain — kabhi adopt nahi
        if best is None or len(candidate) > len(best):
            best, best_peer = candidate, peer
    if best is None:
        return False, None
    state.chain = Blockchain.from_dicts(best, state.chain.difficulty_prefix)
    return True, best_peer


def create_app(port: int = 5000, initial_peers: Optional[List[str]] = None) -> Flask:
    state = NodeState(chain=Blockchain())
    for peer in initial_peers or []:
        normalized = normalize_peer(peer)
        if normalized:
            state.peers.add(normalized)

    app = Flask(f"certchain-node-{port}")
    app.config["STATE"] = state
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    @app.get("/health")
    def health():
        ok, _ = state.chain.is_valid()
        return jsonify({
            "node": f"certchain-node-{port}",
            "chain_length": len(state.chain.blocks),
            "peers": sorted(state.peers),
            "mempool": len(state.mempool),
            "valid": ok,
        })

    @app.get("/chain")
    def chain():
        return jsonify({
            "chain": [b.to_dict() for b in state.chain.blocks],
            "length": len(state.chain.blocks),
        })

    @app.get("/pending")
    def pending():
        return jsonify({"pending": state.mempool, "count": len(state.mempool)})

    @app.post("/transactions/new")
    def new_transaction():
        record = _record_from_dict(request.get_json(silent=True))
        if record is None:
            return jsonify({"error": "record fields missing or malformed"}), 400
        failure = record.verification_failure()
        if failure:
            return jsonify({"error": f"rejected: {failure}"}), 400
        if any(existing.get("signature") == record.signature for existing in state.mempool):
            return jsonify({"error": "duplicate record — already in mempool"}), 400
        state.mempool.append(record.to_dict())
        return jsonify({"message": "record accepted into mempool", "pending": len(state.mempool)}), 201

    @app.post("/mine")
    def mine():
        if not state.mempool:
            return jsonify({"error": "mempool empty — koi record pending nahi"}), 400
        records = state.mempool
        state.mempool = []
        block = state.chain.add_block(records)
        return jsonify({
            "message": "block mined",
            "index": block.index,
            "hash": block.hash,
            "records_in_block": len(block.records),
            "chain_length": len(state.chain.blocks),
        }), 201

    @app.post("/nodes/register")
    def register():
        payload = request.get_json(silent=True) or {}
        incoming = payload.get("peers") or ([payload["peer"]] if "peer" in payload else [])
        added = []
        for peer in incoming:
            normalized = normalize_peer(peer)
            if normalized and normalized not in state.peers:
                state.peers.add(normalized)
                added.append(normalized)
        return jsonify({"added": added, "peers": sorted(state.peers)}), 201

    @app.get("/nodes/resolve")
    def resolve():
        replaced, from_peer = resolve_consensus(state, http_fetch_chain)
        if replaced:
            return jsonify({
                "message": f"chain replaced — adopted from {from_peer}",
                "chain_length": len(state.chain.blocks),
            }), 200
        return jsonify({
            "message": "chain unchanged — hamari chain already sabse lambi valid hai",
            "chain_length": len(state.chain.blocks),
        }), 200

    return app
