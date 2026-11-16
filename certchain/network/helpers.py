"""Shared helpers: kisi bhi Flask app ko real HTTP server ki tarah chalana.

Demos aur integration tests dono use karte hain — ek jagah, do baar nahi.
"""

import socket
import threading
import time

import requests
from flask import Flask
from werkzeug.serving import make_server


class NodeServer(threading.Thread):
    """Kisi bhi Flask app ko real HTTP server ki tarah chalane ka helper (apne thread me)."""

    def __init__(self, app: Flask, port: int):
        super().__init__(daemon=True)
        self.app = app
        self.port = port
        self.server = make_server("127.0.0.1", port, app, threaded=True)

    def run(self) -> None:
        self.server.serve_forever()


def free_port() -> int:
    """OS se ek khali port maango (race-safe enough for demos/tests)."""
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def wait_up(url: str, tries: int = 50) -> None:
    """Server live hone tak ruko (warna RuntimeError)."""
    for _ in range(tries):
        try:
            requests.get(f"{url}/health", timeout=1)
            return
        except requests.RequestException:
            time.sleep(0.1)
    raise RuntimeError(f"server up nahi hua: {url}")
