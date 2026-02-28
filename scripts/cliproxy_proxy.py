#!/usr/bin/env python3
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import requests

UPSTREAM = os.environ.get("CLIPROXY_UPSTREAM", "https://fzl.201452.xyz").rstrip("/")
API_KEY = os.environ.get("CLIPROXY_API_KEY", "")
FORWARD_UA = os.environ.get("CLIPROXY_UA", "python-requests/2.32.0")
HOST = os.environ.get("CLIPROXY_PROXY_HOST", "127.0.0.1")
PORT = int(os.environ.get("CLIPROXY_PROXY_PORT", "19091"))
TIMEOUT = int(os.environ.get("CLIPROXY_TIMEOUT", "180"))

HOP_BY_HOP = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}


class ProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _proxy(self):
        target = f"{UPSTREAM}{self.path}"

        body = None
        length = self.headers.get("Content-Length")
        if length:
            body = self.rfile.read(int(length))

        out_headers = {
            "User-Agent": FORWARD_UA,
            "Accept": self.headers.get("Accept", "application/json"),
        }
        ctype = self.headers.get("Content-Type")
        if ctype:
            out_headers["Content-Type"] = ctype

        if API_KEY:
            out_headers["Authorization"] = f"Bearer {API_KEY}"
        elif self.headers.get("Authorization"):
            out_headers["Authorization"] = self.headers.get("Authorization")

        try:
            resp = requests.request(
                self.command,
                target,
                headers=out_headers,
                data=body,
                timeout=TIMEOUT,
                stream=True,
                allow_redirects=False,
            )
        except requests.RequestException as e:
            msg = f"proxy upstream error: {e}".encode("utf-8", "ignore")
            self.send_response(502)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)
            return

        self.send_response(resp.status_code)
        for k, v in resp.headers.items():
            lk = k.lower()
            if lk in HOP_BY_HOP or lk == "content-length":
                continue
            self.send_header(k, v)

        content = resp.content
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        if content:
            self.wfile.write(content)

    def do_GET(self):
        self._proxy()

    def do_POST(self):
        self._proxy()

    def do_PUT(self):
        self._proxy()

    def do_DELETE(self):
        self._proxy()

    def do_PATCH(self):
        self._proxy()


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), ProxyHandler)
    print(f"cliproxy proxy listening on http://{HOST}:{PORT} -> {UPSTREAM}")
    server.serve_forever()
