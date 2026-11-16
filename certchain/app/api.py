"""CertChain APP layer ka HTTP face — user ISI server se baat karta hai.

Ye "invisible" hai: endpoints me wallet, gas, signature, mempool — kuch
nahi. Sirf UPI-style payment aur verify. Blockchain neeche chupchaap kaam
karta hai (node pe), ye layer uska chehra hai.

Endpoints:
  POST /accounts          demo UPI account banao (₹500 demo balance)
  GET  /accounts/<id>     balance dekho
  POST /issue             certificate issue (₹5 UPI fee → relayer → chain)
  GET  /verify/<cert_id>  FREE verification — ✅/❌ + block link
"""

from pathlib import Path
from typing import Dict, Optional

import requests
from flask import Flask, jsonify, render_template, request

from certchain.core.wallet import Wallet
from .relayer import Relayer
from .upi import FakeUPIBank

DEMO_UNIVERSITY = "Demo University"

_REQUIRED_ISSUE_FIELDS = ("account_id", "university", "cert_id", "holder", "course")

# Flask ko string naam dene se root_path ambiguous ho jaata hai — explicit paths rakho
APP_DIR = Path(__file__).parent


def create_app(node_url: str, issuer_wallets: Optional[Dict[str, Wallet]] = None,
               bank: Optional[FakeUPIBank] = None) -> Flask:
    """App server banata hai.

    Demo mode me default university ka wallet khud generate hota hai.
    Real product me issuer wallets HSM/secure vault me hote hain — yahan
    in-memory hai kyunki ye demo hai.
    """
    bank = bank or FakeUPIBank()
    wallets = issuer_wallets or {DEMO_UNIVERSITY: Wallet.generate()}
    relayer = Relayer(node_url=node_url, bank=bank, issuer_wallets=wallets)

    app = Flask(
        "certchain-app",
        template_folder=str(APP_DIR / "templates"),
        static_folder=str(APP_DIR / "static"),
    )

    @app.post("/accounts")
    def create_account():
        payload = request.get_json(silent=True) or {}
        account_id = (payload.get("account_id") or "").strip()
        if not account_id:
            return jsonify({"error": "account_id chahiye (e.g. rahul@upi)"}), 400
        balance = bank.create_account(account_id)
        return jsonify({
            "account_id": account_id,
            "balance_rupees": balance,
            "message": f"demo UPI account ready — ₹{balance} demo balance",
        }), 201

    @app.get("/accounts/<account_id>")
    def account_balance(account_id):
        amount = bank.balance(account_id)
        if amount is None:
            return jsonify({"error": f"account nahi mila: {account_id}"}), 404
        return jsonify({"account_id": account_id, "balance_rupees": amount})

    @app.post("/issue")
    def issue():
        payload = request.get_json(silent=True) or {}
        missing = [f for f in _REQUIRED_ISSUE_FIELDS if not payload.get(f)]
        if missing:
            return jsonify({"error": f"fields missing: {', '.join(missing)}"}), 400
        result = relayer.pay_and_issue(
            user_account=payload["account_id"],
            university=payload["university"],
            cert_id=payload["cert_id"],
            holder=payload["holder"],
            course=payload["course"],
        )
        status = 201 if result["status"] == "issued" else 400
        return jsonify(result), status

    @app.get("/verify/<cert_id>")
    def verify(cert_id):
        return jsonify(relayer.verify(cert_id))

    @app.get("/")
    def home():
        """Web UI — 3 tabs (Issue / Verify / Explorer), 6 languages (langs.json)."""
        langs_path = Path(__file__).parent / "static" / "langs.json"
        langs_json = langs_path.read_text(encoding="utf-8")
        return render_template("index.html", langs_json=langs_json)

    @app.get("/api/blocks")
    def api_blocks():
        """Explorer ka data — node ki chain ko UI ke liye proxy karte hain."""
        try:
            data = requests.get(f"{relayer.node_url}/chain", timeout=5).json()
            return jsonify({"blocks": data.get("chain", []), "length": data.get("length", 0)})
        except (requests.RequestException, ValueError):
            return jsonify({"error": "node se connect nahi ho paya"}), 502

    return app
