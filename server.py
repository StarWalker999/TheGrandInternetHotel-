"""Grand Internet Hotel server. Python standard library and SQLite."""
import hashlib, io, json, os, secrets, sqlite3, time, uuid, zipfile, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import urlparse
from runtime import DEFAULT
from workshop import assess, propose
from certification import verify, BENCHMARK
from world import WORLD

ROOT = Path(__file__).parent
DATA = Path(os.environ.get("HOTEL_DATA", str(ROOT / "data")))
DATA.mkdir(exist_ok=True)
DB = DATA / "hotel.sqlite3"
MUTATION_LOCK = threading.Lock()

class HotelConnection(sqlite3.Connection):
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()

def db():
    c = sqlite3.connect(DB, timeout=15, factory=HotelConnection)
    c.execute("CREATE TABLE IF NOT EXISTS rooms (id TEXT PRIMARY KEY, owner TEXT, data TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS certificates (id TEXT PRIMARY KEY, room TEXT, data TEXT)")
    return c

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()

def event(room, message):
    room["events"].append(dict(at=time.time(), message=message))

def save(room, owner):
    with db() as c:
        c.execute("INSERT OR REPLACE INTO rooms VALUES(?,?,?)", (room["id"], owner, json.dumps(room)))

def public(room):
    return {k: room.get(k) for k in ("id", "name", "portrait", "number", "specialty", "status", "certificate", "version", "public")}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # No cookies, packages, or user input in logs.
        pass

    def owner(self):
        cookie = SimpleCookie()
        try: cookie.load(self.headers.get("Cookie", ""))
        except Exception: pass
        value = cookie.get("hotel_owner")
        if value and len(value.value) == 64 and all(c in "0123456789abcdef" for c in value.value):
            return value.value
        self.new_cookie = secrets.token_hex(32)
        return self.new_cookie

    def send(self, status, body, mime="application/json", filename=None):
        if not isinstance(body, bytes): body = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store" if mime == "application/json" else "no-cache")
        self.send_header("X-Robots-Tag", "noindex, nofollow")
        self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; script-src 'self'; connect-src 'self'; frame-ancestors 'self'; base-uri 'self'")
        if getattr(self, "new_cookie", None):
            self.send_header("Set-Cookie", f"hotel_owner={self.new_cookie}; Path=/agents; Secure; HttpOnly; SameSite=Strict; Max-Age=31536000")
        if filename: self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(body)

    def room(self, ident, owner):
        with db() as c: row = c.execute("SELECT owner,data FROM rooms WHERE id=?", (ident,)).fetchone()
        if not row: raise ValueError("Room not found")
        if row[0] != owner: raise PermissionError("This room belongs to another browser. Public records are available in the guestbook.")
        return json.loads(row[1])

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/")
        owner = self.owner()
        try:
            if path == "/agents/api/world":
                with MUTATION_LOCK: snapshot = WORLD.snapshot(owner)
                return self.send(200, snapshot)
            if path == "/agents/api/state":
                with db() as c: rows = c.execute("SELECT owner,data FROM rooms ORDER BY rowid DESC").fetchall()
                mine, guests = [], []
                for o, raw in rows:
                    room = json.loads(raw)
                    if o == owner: mine.append(room)
                    if room["public"]: guests.append(public(room))
                return self.send(200, dict(rooms=mine, guests=guests, benchmark=BENCHMARK, service="ready"))
            if path.startswith("/agents/api/certificates/"):
                ident = path.split("/")[-1]
                with db() as c:
                    row = c.execute("SELECT room,data FROM certificates WHERE id=?", (ident,)).fetchone()
                    if not row: return self.send(404, {"error": "Certificate not found"})
                    r = c.execute("SELECT owner,data FROM rooms WHERE id=?", (row[0],)).fetchone()
                if not r or (r[0] != owner and not json.loads(r[1])["public"]):
                    return self.send(404, {"error": "This certificate is private"})
                return self.send(200, json.loads(row[1]))
            if path.startswith("/agents/api/export/"):
                room = self.room(path.split("/")[-1], owner)
                if room["status"] != "checked_out": raise ValueError("Accept the verified result at checkout before exporting")
                buf = io.BytesIO()
                with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                    z.writestr("hotel_agent/runtime.py", room.get("export_runtime", (ROOT / "runtime.py").read_text()))
                    z.writestr("hotel_agent/agent.json", json.dumps(dict(format="hotel-agent/1", name=room["name"], config=room["config"]), indent=2))
                    z.writestr("hotel_agent/rollback.json", json.dumps(dict(format="hotel-agent/1", name=room["name"], config=room["baseline_config"]), indent=2))
                    z.writestr("hotel_agent/evidence.json", json.dumps(room["verification"], indent=2))
                    z.writestr("hotel_agent/manifest.json", json.dumps(dict(version=room["version"], config_sha256=digest(room["config"]), runtime_sha256=hashlib.sha256(room.get("export_runtime", (ROOT / "runtime.py").read_text()).encode()).hexdigest(), certificate=room["certificate"], benchmark=BENCHMARK), indent=2))
                    z.writestr("hotel_agent/README.md", '# Your Hotel Agent\n\nRequires Python 3.9+. No dependencies or network access.\n\nRun: `echo \'{"task":"slugify","input":"Crème Brûlée"}\' | python runtime.py`\n\nTasks: slugify (ASCII URL slug), unique (stable scalar deduplication), sort_numbers (numeric ascending order). Input is JSON, output is JSON.\n\nTo roll back, copy rollback.json to agent.json. Keep the original files.\n\nThis package contains deterministic coding tools, not model weights or a general-purpose LLM. Results apply only to the named task suite and configuration.\n')
                return self.send(200, buf.getvalue(), "application/zip", "hotel-agent-upgrade.zip")
            if path == "/agents/api/health": return self.send(200, {"status": "ok"})
            relative = path.removeprefix("/agents/")
            file = ROOT / relative
            allowed = {"characters.js":"text/javascript", "simulation.js":"text/javascript", "app.js": "text/javascript", "style.css": "text/css", "voxel.js": "text/javascript", "voxel.css": "text/css", "voxel-scene.js": "text/javascript", "catalogue.js": "text/javascript", "catalogue.css": "text/css", "lobby.js":"text/javascript", "paper.css":"text/css"}
            if relative in allowed:
                return self.send(200, file.read_bytes(), allowed[relative])
            if relative.startswith("assets/") and file.resolve().is_relative_to((ROOT / "assets").resolve()) and file.is_file():
                mime = {".png":"image/png", ".webp":"image/webp", ".svg":"image/svg+xml", ".jpg":"image/jpeg", ".js":"text/javascript"}.get(file.suffix)
                if mime: return self.send(200, file.read_bytes(), mime)
            if path == "/agents" or (path.startswith("/agents/") and "." not in relative and not relative.startswith("api/")):
                return self.send(200, (ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")
            return self.send(404, {"error": "Not found"})
        except PermissionError as e: self.send(403, {"error": str(e)})
        except ValueError as e: self.send(400, {"error": str(e)})

    def do_POST(self):
        with MUTATION_LOCK:
            self.handle_post()

    def handle_post(self):
        if self.headers.get("Origin") not in (None, "https://thegrandinternethotel.com", "http://127.0.0.1:8049"):
            return self.send(403, {"error": "Origin not allowed"})
        if "application/json" not in self.headers.get("Content-Type", ""):
            return self.send(415, {"error": "JSON required"})
        owner = self.owner()
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size < 2 or size > 32768: raise ValueError("Request must be between 2 and 32768 bytes")
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict): raise ValueError("A JSON object is required")
            path = urlparse(self.path).path
            if path.startswith('/agents/api/world/'):
                return self.send(200, WORLD.command(owner, path.split('/')[-1], data))
            if path == "/agents/api/checkin":
                with db() as c:
                    count = c.execute("SELECT COUNT(*) FROM rooms WHERE owner=?", (owner,)).fetchone()[0]
                    used_numbers = {int(json.loads(row[0])["number"]) for row in c.execute("SELECT data FROM rooms")}
                number = 1
                while number in used_numbers or number in (17,42,108): number += 1
                if count >= 12: raise ValueError("This browser already has 12 rooms")
                name = str(data.get("name", "" )).strip()[:48]
                if not name: raise ValueError("Give your agent a name")
                config = data.get("config", DEFAULT)
                if not isinstance(config, dict) or set(config) != set(DEFAULT) or any(type(v) is not bool for v in config.values()):
                    raise ValueError("Use a hotel-agent/1 package with the four supported boolean configuration flags")
                budget = int(data.get("budget", 8))
                if budget not in (4, 8, 12): raise ValueError("Choose a 4, 8 or 12 evaluation budget")
                room = dict(id=uuid.uuid4().hex, name=name, portrait=data.get("portrait", "sage") if data.get("portrait") in ("sage","rose","blue") else "sage",
                    number=f"{number:03}", specialty="Coding tools", version=1, public=False, config=config,
                    baseline_config=config.copy(), status="arrived", budget=budget, used=0, cost=0,
                    mode="assess" if data.get("mode") == "assess" else "upgrade", events=[], notes="", versions=[], certificate=None, created=time.time())
                event(room, "Checked in. Private room created; package compatibility verified.")
                save(room, owner)
                return self.send(201, room)
            if path != "/agents/api/action": return self.send(404, {"error":"Not found"})
            room = self.room(data.get("id"), owner)
            action = data.get("action")
            if action == "settings":
                if type(data.get("public", False)) is not bool: raise ValueError("Visibility must be true or false")
                room["public"] = bool(data.get("public", False))
                room["notes"] = str(data.get("notes", ""))[:4000]
                event(room, "Room visibility updated to " + ("public. Notes remain private." if room["public"] else "private."))
            elif action == "pause":
                if room["status"] not in ("assessed", "proposed"): raise ValueError("Pause between assessment, workshop and verification")
                room["resume_status"] = room["status"]
                room["status"] = "paused"
                event(room, "Session paused by owner. No evaluations will run.")
            elif action == "resume":
                if room["status"] != "paused": raise ValueError("Session is not paused")
                room["status"] = room.pop("resume_status")
                event(room, "Session resumed.")
            elif action == "assess":
                if room["status"] != "arrived": raise ValueError("Baseline already recorded")
                if room["used"] + 1 > room["budget"]: raise ValueError("Evaluation budget exhausted")
                room["assessment"] = assess(room["config"])
                room["used"] += 1
                room["status"] = "assessed"
                event(room, f'Baseline: {room["assessment"]["passed"]}/6 practice tasks passed.')
            elif action == "improve":
                if room["status"] != "assessed" or room["mode"] == "assess": raise ValueError("An upgrade reservation and baseline are required")
                candidate, experiments = propose(room["config"])
                if room["used"] + len(experiments) > room["budget"]: raise ValueError("Not enough evaluations for this workshop. Increase the budget or check out with the baseline.")
                room["candidate"] = candidate
                room["experiments"] = experiments
                room["used"] += len(experiments)
                room["status"] = "proposed"
                for ex in experiments: event(room, f'{ex["change"]}: {ex["before"]}/6 → {ex["after"]}/6. ' + ("Candidate accepted." if ex["accepted"] else "Candidate rejected."))
                if not experiments: event(room, "No new changes available. Verify the existing configuration.")
            elif action == "budget":
                value = int(data.get("budget", 8))
                if value not in (4, 8, 12) or value < room["used"]: raise ValueError("Invalid budget")
                room["budget"] = value
                event(room, f"Evaluation limit changed to {value}.")
            elif action == "verify":
                if room["status"] not in ("assessed", "proposed"): raise ValueError("Complete assessment first")
                if room["used"] + 1 > room["budget"]: raise ValueError("Evaluation budget exhausted; increase it before verification")
                candidate = room.get("candidate", room["config"])
                room["verification"] = verify(room["baseline_config"], candidate)
                room["used"] += 1
                room["status"] = "verified"
                event(room, f'Independent verification: {room["verification"]["after"]}/12 held-out tasks; {room["verification"]["regressions"]} regressions.')
            elif action == "checkout":
                if room["status"] != "verified": raise ValueError("Verify before checkout")
                result = room["verification"]
                accepted = result["regressions"] == 0 and result["after"] >= result["before"]
                if accepted: room["config"] = room.get("candidate", room["config"])
                room["version"] += int(room["config"] != room["baseline_config"])
                room["status"] = "checked_out"
                room["export_runtime"] = (ROOT / "runtime.py").read_text()
                cert = dict(id="GIH-" + secrets.token_hex(8).upper(), room=room["id"], name=room["name"],
                    version=room["version"], config_sha256=digest(room["config"]), benchmark=BENCHMARK,
                    runtime_sha256=hashlib.sha256(room["export_runtime"].encode()).hexdigest(),
                    result=result, issued=time.time(), classification="Coding tools · verified" if accepted and result["after"] == 12 else "Assessment recorded",
                    accepted=accepted, cost=0, supervision="Owner-approved configuration changes", autonomy="Bounded configuration search; no weight training",
                    limitations="12 fixed held-out examples across three deterministic tool tasks. Does not establish general reasoning or performance on unrelated workloads. Repeated visits reuse suite v1; these tests are not fresh after disclosure.")
                with db() as c: c.execute("INSERT INTO certificates VALUES(?,?,?)", (cert["id"], room["id"], json.dumps(cert)))
                room["certificate"] = cert["id"]
                room["versions"].append(dict(version=room["version"], config=room["config"], certificate=cert["id"], at=time.time()))
                event(room, "Checkout complete. " + ("Verified package ready to download." if accepted else "Original configuration retained; candidate rejected."))
            elif action == "revisit":
                if room["status"] != "checked_out": raise ValueError("Finish the current visit first")
                room["baseline_config"] = room["config"].copy()
                for field in ("candidate", "assessment", "verification", "experiments"): room.pop(field, None)
                room["status"] = "arrived"
                room["used"] = 0
                event(room, "New visit started. Previous certificates remain historical records.")
            elif action == "rollback":
                if room["status"] != "checked_out": raise ValueError("Rollback is available after checkout")
                room["config"] = room["baseline_config"].copy()
                room["version"] += 1
                room["certificate"] = None
                room["status"] = "arrived"
                room["used"] = 0
                for field in ("candidate", "assessment", "verification", "experiments"): room.pop(field, None)
                event(room, "Baseline restored as a new version. Retest required for a current certificate.")
            else: raise ValueError("Unknown action")
            save(room, owner)
            return self.send(200, room)
        except PermissionError as e: self.send(403, {"error": str(e)})
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as e: self.send(400, {"error": str(e)})

if __name__ == "__main__":
    db().close()
    ThreadingHTTPServer(("127.0.0.1", int(os.environ.get("PORT", "8049"))), Handler).serve_forever()
