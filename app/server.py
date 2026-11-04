import base64
import http.server
import os
import socketserver
import urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(ROOT, "shots")


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass

    def _read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(length) if length else b""

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/save":
            self.send_error(404)
            return
        name = os.path.basename(
            urllib.parse.parse_qs(parsed.query).get("name", ["shot.png"])[0]
        ) or "shot.png"
        body = self._read_body().strip()
        try:
            raw = base64.b64decode(body)
        except Exception:
            self.send_error(400, "body must be base64")
            return
        os.makedirs(SHOTS, exist_ok=True)
        path = os.path.join(SHOTS, name)
        with open(path, "wb") as f:
            f.write(raw)
        payload = ("saved %s (%d bytes)" % (path, len(raw))).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


os.chdir(ROOT)
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", 8765), Handler) as httpd:
    print("serving %s on http://127.0.0.1:8765" % ROOT)
    httpd.serve_forever()
