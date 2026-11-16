"""🎬 Phase 4 demo: INVISIBLE blockchain — user sirf UPI use karta hai!

Run:  .venv/bin/python -m certchain.app_demo

Ek node + ek app server real HTTP pe chalte hain. Rahul ₹5 UPI se pay karta
hai, certificate chain pe likha jaata hai, employer FREE me verify karta hai
— aur kisi ko crypto ka "B" nahi dikhta. Wahi hamara vision! ✨
"""

import json
import time

import requests

from certchain.app.api import create_app as create_app_server
from certchain.network.helpers import NodeServer, free_port, wait_up
from certchain.network.node import create_app as create_node_app


def banner(text: str) -> None:
    print("\n" + "=" * 64)
    print(text)
    print("=" * 64)


def pretty(result: dict) -> None:
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main() -> None:
    banner("CertChain Phase 4 — INVISIBLE blockchain (UPI aage, chain peeche)")

    # 1) real node + real app server, dono apne-apne ports pe
    node_port, app_port = free_port(), free_port()
    node = NodeServer(create_node_app(node_port), node_port)
    app = NodeServer(create_app_server(f"http://127.0.0.1:{node_port}"), app_port)
    node.start()
    app.start()
    node_url, app_url = f"http://127.0.0.1:{node_port}", f"http://127.0.0.1:{app_port}"
    wait_up(node_url)
    wait_up(app_url)
    print(f"  🟢 node live: {node_url}")
    print(f"  🟢 app  live: {app_url}   ← USER YAHAN AATA HAI (chain se seedha nahi)")

    banner("1) Rahul ka demo UPI account (₹500 demo balance)")
    r = requests.post(f"{app_url}/accounts", json={"account_id": "rahul@upi"}, timeout=5).json()
    pretty(r)

    banner("2) University certificate ISSUE karti hai — Rahul ₹5 UPI se pay karta hai")
    r = requests.post(f"{app_url}/issue", json={
        "account_id": "rahul@upi",
        "university": "Demo University",
        "cert_id": "CERT-2026-0100",
        "holder": "Rahul",
        "course": "B.Tech CSE",
    }, timeout=35).json()
    pretty(r)
    print("  → Relayer ne kiya: payment liya, record sign kiya, node pe submit, mine — sab HIDDEN")

    banner("3) Employer VERIFY karta hai — FREE, bas cert ID daalo")
    r = requests.get(f"{app_url}/verify/CERT-2026-0100", timeout=5).json()
    pretty(r)

    banner("4) ATTACK: fake certificate verify karne ki koshish")
    r = requests.get(f"{app_url}/verify/FAKE-9999", timeout=5).json()
    pretty(r)

    banner("5) ATTACK-2: unauthorized university issue karne ki koshish")
    r = requests.post(f"{app_url}/issue", json={
        "account_id": "rahul@upi",
        "university": "Fake College of Corruption",
        "cert_id": "CERT-FAKE-001",
        "holder": "Chhota Don",
        "course": "PhD in Scam",
    }, timeout=5).json()
    pretty(r)
    print("  → Payment se PEHLE reject — ₹ kata bhi nahi (design decision!)")

    banner("6) Rahul ka balance — ₹495 (sirf ₹5 issue fee). Crypto use kiya hi nahi!")
    r = requests.get(f"{app_url}/accounts/rahul@upi", timeout=5).json()
    pretty(r)

    banner("✨ INVISIBLE BLOCKCHAIN ✨")
    print("  User ne kiya:     sirf UPI payment")
    print("  User ko dikha:    'Payment successful' + 'Verified ✅'")
    print("  Jo HIDDEN tha:    wallet, keys, signatures, gas, mempool, mining")
    print("  Yahi hai hamara differentiator — India ke liye blockchain, bina blockchain ke 🇮🇳")

    banner("Demo complete — servers band kar rahe hain")
    node.server.shutdown()
    app.server.shutdown()
    print("  Phase 4 complete 🚀")


if __name__ == "__main__":
    main()
