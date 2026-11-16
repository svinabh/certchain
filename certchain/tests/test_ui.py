"""Phase 5 tests — web UI page aur explorer proxy endpoint."""

import pytest

from certchain.app.api import create_app
from certchain.core.wallet import Wallet
from certchain.network.helpers import NodeServer, free_port, wait_up
from certchain.network.node import create_app as create_node_app


@pytest.fixture()
def node_url(university=None):
    port = free_port()
    server = NodeServer(create_node_app(port), port)
    server.start()
    url = f"http://127.0.0.1:{port}"
    wait_up(url)
    yield url
    server.server.shutdown()
    server.server.server_close()


@pytest.fixture()
def client(node_url):
    app = create_app(node_url)
    return app.test_client()


def test_home_page_renders_with_i18n_hooks(client):
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "CertChain" in html
    assert "data-i18n" in html                      # i18n system wired
    assert "हिन्दी" in html and "العربية" in html     # language switcher options
    assert 'id="verify-form"' in html               # verify tab
    assert 'id="issue-form"' in html                # issue tab


def test_api_blocks_proxies_node_chain(client):
    body = client.get("/api/blocks").get_json()
    assert body["length"] == 1                      # genesis
    assert body["blocks"][0]["index"] == 0
    assert body["blocks"][0]["previous_hash"] == "0" * 64


def test_all_ui_languages_have_same_keys():
    """Har language dictionary me SAME keys hone chahiye — koi key miss nahi honi chahiye."""
    import json
    from pathlib import Path

    langs_path = Path(__file__).parent.parent / "app" / "static" / "langs.json"
    langs = json.loads(langs_path.read_text(encoding="utf-8"))

    reference = set(langs["en"].keys())
    assert len(langs) == 6, "6 languages: en, hi, es, fr, ar, ja"
    for lang, keys in langs.items():
        assert set(keys) == reference, f"language '{lang}' me keys mismatch!"
