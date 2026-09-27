#!/usr/bin/env python3
"""Nex playground server. Serves the site and a small JSON API."""

from __future__ import annotations

import json
import traceback
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import sys

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nex.compare import SHOWCASE, compare_tokenization, morphology_table
from nex.english import TranslateError, from_english
from nex.ids import decode_id_fields, id_layout, token_id
from nex.lexicon import LEXICON, lexicon_public, validate_lexicon
from nex.parser import ParseError, parse
from nex.samples import AMBIGUOUS, EXAMPLES
from nex.serialize import encode, gloss, pretty_tokens, serialize


def _json(handler, code: int, payload: object) -> None:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(data)


def _read_json(handler) -> dict:
    n = int(handler.headers.get("Content-Length", "0") or 0)
    raw = handler.rfile.read(n) if n else b"{}"
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        sys_stdout = __import__("sys").stdout
        sys_stdout.write("server: " + (fmt % args) + "\n")
        sys_stdout.flush()

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/lexicon":
            return _json(self, 200, lexicon_public())
        if path == "/api/examples":
            return _json(self, 200, {"examples": EXAMPLES, "ambiguous": AMBIGUOUS, "showcase": SHOWCASE})
        if path == "/api/morph":
            return _json(self, 200, morphology_table())
        if path == "/api/ids":
            return _json(self, 200, id_layout())
        if path == "/api/health":
            return _json(
                self,
                200,
                {
                    "ok": True,
                    "lexicon": len(lexicon_public()),
                    "problems": validate_lexicon(),
                },
            )
        if path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            body = _read_json(self)
        except json.JSONDecodeError as e:
            return _json(self, 400, {"error": f"invalid json: {e}"})
        try:
            if path == "/api/parse":
                return _json(self, 200, _do_parse(body.get("text", "")))
            if path == "/api/en":
                return _json(self, 200, _do_en(body.get("text", "")))
            if path == "/api/compare":
                return _json(
                    self,
                    200,
                    compare_tokenization(body.get("english", ""), body.get("nex") or None),
                )
            if path == "/api/id":
                form = body.get("form", "")
                return _json(self, 200, {"form": form, **decode_id_fields(token_id(form))})
            return _json(self, 404, {"error": "unknown endpoint"})
        except Exception as e:
            traceback.print_exc()
            return _json(self, 500, {"error": str(e)})


def _do_parse(text: str) -> dict:
    try:
        prog = parse(text)
    except ParseError as e:
        return {"ok": False, "error": str(e), "index": e.index, "token": e.token}
    can = prog.canonical()
    stream = encode(can)
    return {
        "ok": True,
        "nex": serialize(can, pretty=True),
        "nex_compact": serialize(can, pretty=False),
        "gloss": gloss(can),
        "ast": can.to_dict(),
        "tokens": pretty_tokens(stream),
        "token_count": len(stream),
        "ids": [token_id(t) for t in stream],
    }


def _do_en(text: str) -> dict:
    try:
        r = from_english(text)
    except TranslateError as e:
        return {"ok": False, "error": str(e)}
    parsed = _do_parse(r["nex"])
    parsed["notes"] = r["notes"]
    parsed["source"] = "english"
    return parsed


def main() -> None:
    import os

    host = os.environ.get("NEX_HOST", "0.0.0.0")
    port = int(os.environ.get("NEX_PORT", "8000"))
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"Nex playground at http://{host}:{port}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
