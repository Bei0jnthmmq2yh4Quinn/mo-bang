#!/usr/bin/env python3
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import requests

UPSTREAM = os.environ.get("FREESTYLE_UPSTREAM", "https://api.freestyle.cc.cd").rstrip("/")
API_KEY = os.environ.get("FREESTYLE_API_KEY", "")
FORWARD_UA = os.environ.get("FREESTYLE_UA", "python-requests/2.32.0")
HOST = os.environ.get("FREESTYLE_PROXY_HOST", "127.0.0.1")
PORT = int(os.environ.get("FREESTYLE_PROXY_PORT", "19090"))
TIMEOUT = int(os.environ.get("FREESTYLE_TIMEOUT", "180"))

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
        method = self.command
        path = self.path
        target = f"{UPSTREAM}{path}"

        body = None
        length = self.headers.get("Content-Length")
        if length:
            body = self.rfile.read(int(length))

        # 严格控制上游头，避免 SDK 特征头触发风控
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
                method,
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
            if lk in HOP_BY_HOP:
                continue
            if lk == "content-length":
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

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,PATCH,OPTIONS")
        self.send_header("Content-Length", "0")
        self.end_headers()


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), ProxyHandler)
    print(f"freestyle proxy listening on http://{HOST}:{PORT} -> {UPSTREAM}")
    server.serve_forever()
