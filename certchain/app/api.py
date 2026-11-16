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

from typing import Dict, Optional

from flask import Flask, jsonify, request

from certchain.core.wallet import Wallet
from .relayer import Relayer
from .upi import FakeUPIBank

DEMO_UNIVERSITY = "Demo University"

_REQUIRED_ISSUE_FIELDS = ("account_id", "university", "cert_id", "holder", "course")


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

    app = Flask("certchain-app")

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

    return app
