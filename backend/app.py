"""Campus Polling System - Backend REST API (Python standard library only)."""
import json
import os
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

DATA_DIR = os.environ.get("DATA_DIR", "/var/lib/backend_data")
DATA_FILE = os.path.join(DATA_DIR, "votes.json")
OPTIONS = ["A", "B"]
lock = threading.Lock()


def load_votes():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_votes(votes):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(votes, f, indent=2)
    os.replace(tmp, DATA_FILE)


def summary(votes):
    results = {opt: 0 for opt in OPTIONS}
    for v in votes:
        if v.get("option") in results:
            results[v["option"]] += 1
    return {
        "total": len(votes),
        "results": results,
        "votes": [dict(v, index=i) for i, v in enumerate(votes)],
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(200, {})

    def do_GET(self):
       path = urlparse(self.path).path
       if path in ("/", "/index.html"):
           with open(os.path.join(os.path.dirname(__file__), "index.html"), "rb") as f:
               body = f.read()
           self.send_response(200)
           self.send_header("Content-Type", "text/html; charset=utf-8")
           self.send_header("Content-Length", str(len(body)))
           self.end_headers()
           self.wfile.write(body)
           return
       if path != "/votes":
           return self._send(404, {"error": "Endpoint tidak ditemukan"})
       with lock:
           self._send(200, summary(load_votes()))

    def do_POST(self):
        if urlparse(self.path).path != "/votes":
            return self._send(404, {"error": "Endpoint tidak ditemukan"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            return self._send(400, {"error": "Body harus berupa JSON valid"})
        option = str(data.get("option", "")).strip().upper() if isinstance(data, dict) else ""
        if option not in OPTIONS:
            return self._send(400, {"error": "Field 'option' harus salah satu dari %s" % OPTIONS})
        with lock:
            votes = load_votes()
            votes.append({"option": option, "time": datetime.now().isoformat(timespec="seconds")})
            save_votes(votes)
            self._send(201, summary(votes))

    def do_DELETE(self):
        parsed = urlparse(self.path)
        if parsed.path != "/votes":
            return self._send(404, {"error": "Endpoint tidak ditemukan"})
        raw = parse_qs(parsed.query).get("index", [None])[0]
        if raw is None:
            return self._send(400, {"error": "Parameter 'index' wajib diisi"})
        try:
            index = int(raw)
        except ValueError:
            return self._send(400, {"error": "Parameter 'index' harus berupa angka"})
        with lock:
            votes = load_votes()
            if index < 0 or index >= len(votes):
                return self._send(404, {"error": "Data dengan index tersebut tidak ada"})
            removed = votes.pop(index)
            save_votes(votes)
            self._send(200, {"deleted": removed, **summary(votes)})

    def log_message(self, fmt, *args):
        print("[API] %s - %s" % (self.address_string(), fmt % args), flush=True)


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    print("Polling API berjalan di port 5000, data: %s" % DATA_FILE, flush=True)
    ThreadingHTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
