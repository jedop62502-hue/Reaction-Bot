"""GitHub Sync Module - v60 MERGED"""
import os
import base64
import json
import sqlite3
import threading
import time
import requests
from datetime import datetime

# ── Token ENV se lo (SECURE), fallback hardcoded ──
GITHUB_TOKEN    = os.getenv("GITHUB_TOKEN", "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")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "jedop62502-hue")
GITHUB_REPO     = os.getenv("GITHUB_REPO", "Reaction-Bot")
GITHUB_BRANCH   = os.getenv("GITHUB_BRANCH", "main")
GITHUB_DB_PATH  = os.getenv("GITHUB_DB_PATH", "data/ghost_users.db")

LOCAL_DB_PATH   = os.getenv(
    "LOCAL_DB_PATH",
    "/app/data/ghost_users.db" if os.path.isdir("/app/data") else "ghost_users.db"
)
SYNC_INTERVAL   = int(os.getenv("SYNC_INTERVAL", "45"))

GH_API = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents"

# ── Per-table JSON paths ──
GH_FILES = {
    "users": "data/users.json", "approvals": "data/approvals.json",
    "bots": "data/bots.json", "watchers": "data/watchers.json",
    "templates": "data/templates.json", "referrals": "data/referrals.json",
    "notifications": "data/notifications.json", "queue": "data/queue.json",
    "payments": "data/payments.json", "force_channels": "data/force_channels.json",
    "team": "data/team.json", "custom_packs": "data/custom_packs.json",
    "reactions": "data/reactions.json", "config": "data/config.json",
    "security_logs": "data/security_logs.json",
}

# ── State ──
_last_sha = None
_last_upload_time = 0
_sync_lock = threading.Lock()
_dirty = False
_stats = {
    "uploads": 0, "downloads": 0, "errors": 0,
    "last_sync": None, "last_msg": "—",
    "enabled": bool(GITHUB_TOKEN and GITHUB_REPO),
}


def _headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GhostReactionBot",
    }


def is_enabled():
    return _stats["enabled"]


# ══════════════════════════════════════════════════════
#  SINGLE DB FILE SYNC (main.py isko use karta hai)
# ══════════════════════════════════════════════════════
def download_db():
    """GitHub se SQLite DB download karo → local file."""
    global _last_sha
    if not is_enabled():
        return False, "Sync disabled"
    try:
        url = f"{GH_API}/{GITHUB_DB_PATH}"
        r = requests.get(url, headers=_headers(),
                         params={"ref": GITHUB_BRANCH}, timeout=20)
        if r.status_code == 200:
            content = base64.b64decode(r.json()["content"])
            os.makedirs(os.path.dirname(LOCAL_DB_PATH) or ".", exist_ok=True)
            with open(LOCAL_DB_PATH, "wb") as f:
                f.write(content)
            _last_sha = r.json()["sha"]
            _stats["downloads"] += 1
            _stats["last_sync"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _stats["last_msg"] = f"Downloaded {len(content)} bytes"
            return True, _stats["last_msg"]
        elif r.status_code == 404:
            _stats["last_msg"] = "New DB (not on GitHub)"
            return True, _stats["last_msg"]
        _stats["errors"] += 1
        _stats["last_msg"] = f"HTTP {r.status_code}"
        return False, _stats["last_msg"]
    except Exception as e:
        _stats["errors"] += 1
        _stats["last_msg"] = str(e)[:120]
        return False, _stats["last_msg"]


def upload_db(force=False):
    """Local SQLite DB → GitHub."""
    global _last_sha, _last_upload_time, _dirty
    if not is_enabled():
        return False, "Sync disabled"
    if not os.path.exists(LOCAL_DB_PATH):
        return False, "Local DB not found"
    with _sync_lock:
        if not force and (time.time() - _last_upload_time) < 5:
            return False, "Throttled"
        try:
            with open(LOCAL_DB_PATH, "rb") as f:
                content = f.read()
            encoded = base64.b64encode(content).decode()
            payload = {
                "message": f"auto-sync @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "content": encoded, "branch": GITHUB_BRANCH,
            }
            if _last_sha:
                payload["sha"] = _last_sha
            r = requests.put(f"{GH_API}/{GITHUB_DB_PATH}",
                             headers=_headers(), json=payload, timeout=30)
            if r.status_code in (200, 201):
                _last_sha = r.json()["content"]["sha"]
                _last_upload_time = time.time()
                _dirty = False
                _stats["uploads"] += 1
                _stats["last_sync"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                _stats["last_msg"] = f"Uploaded {len(content)} bytes"
                return True, _stats["last_msg"]
            elif r.status_code == 409:
                download_db()
                return upload_db(force=True)
            _stats["errors"] += 1
            _stats["last_msg"] = f"HTTP {r.status_code}"
            return False, _stats["last_msg"]
        except Exception as e:
            _stats["errors"] += 1
            _stats["last_msg"] = str(e)[:120]
            return False, _stats["last_msg"]


def mark_dirty():
    global _dirty
    _dirty = True


def get_stats():
    s = dict(_stats)
    s["dirty"] = _dirty
    s["local_db"] = LOCAL_DB_PATH
    s["repo"] = f"{GITHUB_USERNAME}/{GITHUB_REPO}"
    s["path"] = GITHUB_DB_PATH
    s["branch"] = GITHUB_BRANCH
    return s


def _sync_loop():
    while True:
        try:
            time.sleep(SYNC_INTERVAL)
            if _dirty:
                upload_db()
        except Exception:
            time.sleep(10)


def start_sync_thread():
    """Boot pe download + background sync."""
    ok, msg = download_db()
    print(f"[GITHUB-SYNC] boot download: {msg}", flush=True)
    threading.Thread(target=_sync_loop, daemon=True).start()


# ══════════════════════════════════════════════════════
#  PER-TABLE JSON SYNC (tumhara purana code — optional)
# ══════════════════════════════════════════════════════
def gh_read(path):
    try:
        r = requests.get(f"{GH_API}/{path}", headers=_headers(), timeout=20)
        if r.status_code == 200:
            d = r.json()
            return base64.b64decode(d["content"]).decode("utf-8"), d.get("sha")
        return None, None
    except Exception:
        return None, None


def gh_write(path, content_str, message=None):
    try:
        _, sha = gh_read(path)
        content_b64 = base64.b64encode(content_str.encode()).decode()
        if not message:
            message = f"update {path.split('/')[-1]} @ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        payload = {"message": message, "content": content_b64, "branch": GITHUB_BRANCH}
        if sha:
            payload["sha"] = sha
        r = requests.put(f"{GH_API}/{path}", headers=_headers(), json=payload, timeout=30)
        return r.status_code in (200, 201)
    except Exception:
        return False


def gh_save_table(db_file, table_name):
    path = GH_FILES.get(table_name)
    if not path:
        return False
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(f"SELECT * FROM {table_name}").fetchall()
        conn.close()
        return gh_write(path, json.dumps([dict(r) for r in rows],
                                          indent=2, ensure_ascii=False, default=str))
    except Exception:
        return False


def gh_save_all(db_file, tables=None):
    if tables is None:
        tables = list(GH_FILES.keys())
    return {t: gh_save_table(db_file, t) for t in tables}


def gh_load_table(db_file, table_name, create_sql, columns):
    path = GH_FILES.get(table_name)
    if not path:
        return 0
    try:
        content, _ = gh_read(path)
        if not content:
            return 0
        data = json.loads(content)
        if not isinstance(data, list):
            return 0
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute(create_sql)
        if table_name != "bots":
            c.execute(f"DELETE FROM {table_name}")
        n = 0
        for row in data:
            cols = [col for col in columns if col in row]
            if not cols:
                continue
            ph = ",".join(["?"] * len(cols))
            c.execute(f"INSERT OR REPLACE INTO {table_name} ({','.join(cols)}) VALUES ({ph})",
                      [row[col] for col in cols])
            n += 1
        conn.commit()
        conn.close()
        return n
    except Exception:
        return 0


def gh_load_all(db_file, schemas):
    return {name: gh_load_table(db_file, name, sql, cols)
            for name, (sql, cols) in schemas.items()}
