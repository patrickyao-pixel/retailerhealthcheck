"""
Local Jira CORS proxy for the Retailer Data Health Monitor (GitHub Pages build).

- Python 3.8+ standard library only. Listens on 127.0.0.1 only.
- Forwards ONLY to your Jira host, so it can't be used as an open proxy.
- Your Jira host is NOT stored in the repo: pass --host, or it is asked once and
  saved to tools/jira_host.local.txt (git-ignored).

Run:   python jira_proxy.py                       (asks for the Jira host the first time)
       python jira_proxy.py --host jira.mycompany.com --origin https://<user>.github.io
Then in the site -> Connect Jira -> CORS proxy prefix:  http://127.0.0.1:8787/?url=
"""
import argparse, os, ssl, sys, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
HOST_FILE = os.path.join(HERE, "jira_host.local.txt")

ap = argparse.ArgumentParser()
ap.add_argument("--port", type=int, default=8787)
ap.add_argument("--host", default="", help="Jira host name only, e.g. jira.mycompany.com")
ap.add_argument("--origin", default="*", help="allowed browser origin, e.g. https://<user>.github.io")
ap.add_argument("--insecure", action="store_true", help="skip SSL verification (company SSL inspection)")
ARGS = ap.parse_args()

if not ARGS.host:
    if os.path.exists(HOST_FILE):
        ARGS.host = open(HOST_FILE, encoding="utf-8").read().strip()
    else:
        ARGS.host = input("Jira host (e.g. jira.mycompany.com): ").strip()
        ARGS.host = urlparse(ARGS.host).hostname or ARGS.host.split("/")[0]
        open(HOST_FILE, "w", encoding="utf-8").write(ARGS.host)
        print(f"Saved to {HOST_FILE} (git-ignored).")

CTX = ssl._create_unverified_context() if ARGS.insecure else ssl.create_default_context()
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler(), urllib.request.HTTPSHandler(context=CTX))
PASS_HEADERS = ("Authorization", "Accept", "Content-Type")


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        origin = self.headers.get("Origin", "")
        allow = "*" if ARGS.origin == "*" else (origin if origin == ARGS.origin.rstrip("/") else ARGS.origin)
        self.send_header("Access-Control-Allow-Origin", allow)
        self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Accept, Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Access-Control-Expose-Headers", "X-Final-URL")
        self.send_header("Access-Control-Max-Age", "600")

    def _fail(self, code, msg):
        body = msg.encode("utf-8")
        self.send_response(code); self._cors()
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def _forward(self, method):
        target = (parse_qs(urlparse(self.path).query).get("url") or [""])[0]
        if not target:
            return self._fail(200, "Jira proxy is running. Use ?url=<encoded Jira URL>")
        t = urlparse(target)
        if t.scheme not in ("http", "https") or t.hostname != ARGS.host:
            return self._fail(403, f"Blocked: only {ARGS.host} is allowed (got {t.hostname})")
        data = None
        if method in ("POST", "PUT"):
            n = int(self.headers.get("Content-Length") or 0)
            data = self.rfile.read(n) if n else None
        req = urllib.request.Request(target, data=data, method=method)
        for h in PASS_HEADERS:
            if self.headers.get(h):
                req.add_header(h, self.headers[h])
        req.add_header("User-Agent", "rdhm-jira-proxy/1.1")
        try:
            with OPENER.open(req, timeout=60) as r:
                status, ctype, body, final = r.status, r.headers.get("Content-Type", "application/json"), r.read(), r.geturl()
        except urllib.error.HTTPError as e:
            status, ctype, body, final = e.code, e.headers.get("Content-Type", "text/plain"), e.read(), target
        except Exception as e:
            hint = " -> try: --insecure" if "CERTIFICATE" in str(e).upper() else " -> check VPN / that Jira opens in your browser"
            print(f"[ERR] {method} {t.path}: {e}", file=sys.stderr)
            return self._fail(502, f"Proxy could not reach Jira: {e}{hint}")
        login = "json" not in (ctype or "").lower()
        print(f"[{status}] {method} {t.path}" + ("  !! non-JSON reply (login page?)" if login else ""))
        self.send_response(status); self._cors()
        self.send_header("Content-Type", ctype); self.send_header("X-Final-URL", final)
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_GET(self):  self._forward("GET")
    def do_POST(self): self._forward("POST")
    def do_PUT(self):  self._forward("PUT")
    def log_message(self, *a): pass


if __name__ == "__main__":
    print(f"Jira proxy on http://127.0.0.1:{ARGS.port} -> {ARGS.host}  (origin: {ARGS.origin}){'  [SSL verify OFF]' if ARGS.insecure else ''}")
    print(f"Site setting 'CORS proxy prefix':  http://127.0.0.1:{ARGS.port}/?url=")
    print("Keep this window open while using the site. Ctrl+C to stop.")
    ThreadingHTTPServer(("127.0.0.1", ARGS.port), Handler).serve_forever()
