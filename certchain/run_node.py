"""Ek CertChain node chalao:

  .venv/bin/python -m certchain.run_node --port 5000
  .venv/bin/python -m certchain.run_node --port 5001 --peers localhost:5000

3-node demo: teen terminals me alag ports pe chalao, peers ek doosre ko do,
phir /transactions/new + /mine ek pe, /nodes/resolve baaki pe.
"""

import argparse

from certchain.network.node import create_app


def main() -> None:
    parser = argparse.ArgumentParser(description="CertChain node server")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--peers", default="", help="comma-separated host:port peers")
    args = parser.parse_args()

    peers = [p.strip() for p in args.peers.split(",") if p.strip()]
    app = create_app(args.port, initial_peers=peers)

    print(f"🟢 CertChain node live: http://{args.host}:{args.port}")
    print(f"   peers: {', '.join(peers) if peers else '(koi nahi — /nodes/register se jodo)'}")
    app.run(host=args.host, port=args.port, threaded=True, use_reloader=False)


if __name__ == "__main__":
    main()
