"""CertChain app server chalao (web UI + invisible API):

  .venv/bin/python -m certchain.run_app --port 8100 --node http://127.0.0.1:8000
"""

import argparse

from certchain.app.api import create_app


def main() -> None:
    parser = argparse.ArgumentParser(description="CertChain app server (invisible blockchain UI)")
    parser.add_argument("--port", type=int, default=8100)
    parser.add_argument("--node", default="http://127.0.0.1:8000",
                        help="chain node ka URL jisse app baat kare")
    args = parser.parse_args()

    app = create_app(args.node)
    print(f"🟢 CertChain app live: http://127.0.0.1:{args.port}/")
    print(f"   node: {args.node}")
    app.run(host="127.0.0.1", port=args.port, threaded=True, use_reloader=False)


if __name__ == "__main__":
    main()
