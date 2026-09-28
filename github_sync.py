"""
GitHub Sync - DB + Sessions pull
"""
import os, base64, threading, time, requests
from datetime import datetime

GITHUB_TOKEN    = os.getenv("GITHUB_TOKEN", "")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "jedop62502-hue")

# DB repo
DB_REPO        = os.getenv("GITHUB_REPO", "Data-base-")
DB_BRANCH      = os.getenv("GITHUB_BRANCH", "main")
GITHUB_DB_PATH = os.getenv("GITHUB_DB_PATH", "data/ghost_users.db")

# Sessions repo
SESSIONS_REPO   = os.getenv("SESSIONS_REPO", "Sessions")
SESSIONS_BRANCH = os.getenv("SESSIONS_BRANCH", "main")
SESSIONS_DIR    = os.getenv("SESSIONS_DIR", "sessions")

LOCAL_DB_PATH = os.getenv("LOCAL_DB_PATH",
    "/app/data/ghost_users.db" if os.path.isdir("/app/data") else "ghost_users.db")
SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "45"))

DB_API = f"https://api.github.com/repos/{GITHUB_USERNAME}/{DB_REPO}/contents/{GITHUB_DB_PATH}"
SESS_API = f"https://api.github.com/repos/{GITHUB_USERNAME}/{SESSIONS_REPO}/contents"

_last_sha = None
_last_upload_time = 0
_lock = threading.Lock()
_dirty = False
_stats = {
    "uploads":0, "downloads":0, "errors":0, "sessions_dl":0,
    "last_sync":None, "last_msg":"—",
    "enabled": bool(GITHUB_TOKEN and GITHUB_USERNAME and DB_REPO),
}


def _headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GhostBot",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def is_enabled(): return _stats["enabled"]


def download_db():
    global _last_sha
    if not is_enabled(): return False, "disabled"
    try:
        r = requests.get(DB_API, headers=_headers(), params={"ref": DB_BRANCH}, timeout=20)
        if r.status_code == 200:
            data = r.json()
            content = base64.b64decode(data["content"])
            os.makedirs(os.path.dirname(LOCAL_DB_PATH) or ".", exist_ok=True)
            with open(LOCAL_DB_PATH, "wb") as f: f.write(content)
            _last_sha = data["sha"]
            _stats["downloads"] += 1
            _stats["last_sync"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _stats["last_msg"] = f"Downloaded {len(content)} bytes"
            return True, _stats["last_msg"]
        elif r.status_code == 404:
            _stats["last_msg"] = "New DB"
            return True, _stats["last_msg"]
        elif r.status_code == 401:
            _stats["errors"] += 1; _stats["last_msg"] = "HTTP 401 (bad token)"
            return False, _stats["last_msg"]
        elif r.status_code == 403:
            _stats["errors"] += 1; _stats["last_msg"] = "HTTP 403"
            return False, _stats["last_msg"]
        else:
            _stats["errors"] += 1; _stats["last_msg"] = f"HTTP {r.status_code}"
            return False, _stats["last_msg"]
    except Exception as e:
        _stats["errors"] += 1; _stats["last_msg"] = str(e)[:120]
        return False, _stats["last_msg"]


def upload_db(force=False):
    global _last_sha, _last_upload_time, _dirty
    if not is_enabled(): return False, "disabled"
    if not os.path.exists(LOCAL_DB_PATH): return False, "local DB missing"
    with _lock:
        if not force and (time.time() - _last_upload_time) < 5: return False, "throttled"
        try:
            with open(LOCAL_DB_PATH, "rb") as f: content = f.read()
            encoded = base64.b64encode(content).decode()
            payload = {"message": f"auto @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                       "content": encoded, "branch": DB_BRANCH}
            if _last_sha: payload["sha"] = _last_sha
            r = requests.put(DB_API, headers=_headers(), json=payload, timeout=30)
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
            else:
                _stats["errors"] += 1
                _stats["last_msg"] = f"HTTP {r.status_code}"
                return False, _stats["last_msg"]
        except Exception as e:
            _stats["errors"] += 1; _stats["last_msg"] = str(e)[:120]
            return False, _stats["last_msg"]


def mark_dirty():
    global _dirty; _dirty = True


def get_stats():
    s = dict(_stats)
    s["dirty"] = _dirty
    s["local_db"] = LOCAL_DB_PATH
    s["repo"] = f"{GITHUB_USERNAME}/{DB_REPO}"
    s["path"] = GITHUB_DB_PATH
    s["branch"] = DB_BRANCH
    s["sessions_repo"] = f"{GITHUB_USERNAME}/{SESSIONS_REPO}"
    s["sessions_dir"] = SESSIONS_DIR
    return s


def _sync_loop():
    while True:
        try:
            time.sleep(SYNC_INTERVAL)
            if _dirty: upload_db()
        except Exception:
            time.sleep(10)


def download_sessions():
    """Download all .session files from Sessions repo."""
    if not is_enabled(): return 0, "disabled"
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    try:
        r = requests.get(SESS_API, headers=_headers(),
                         params={"ref": SESSIONS_BRANCH}, timeout=20)
        if r.status_code != 200:
            return 0, f"HTTP {r.status_code}"
        items = r.json()
        if not isinstance(items, list): return 0, "not a list"
        downloaded = 0
        for item in items:
            name = item.get("name", "")
            if not name.endswith(".session"): continue
            try:
                fr = requests.get(item["download_url"], timeout=30)
                if fr.status_code == 200:
                    with open(os.path.join(SESSIONS_DIR, name), "wb") as f:
                        f.write(fr.content)
                    downloaded += 1
            except Exception as e:
                print(f"[SESS] {name}: {str(e)[:60]}", flush=True)
        _stats["sessions_dl"] = downloaded
        return downloaded, f"Downloaded {downloaded} sessions"
    except Exception as e:
        return 0, str(e)[:120]


def start_sync_thread():
    ok, msg = download_db()
    print(f"[GITHUB-SYNC] boot DB: {msg}", flush=True)
    s_ok, s_msg = download_sessions()
    print(f"[GITHUB-SYNC] boot sessions: {s_msg}", flush=True)
    t = threading.Thread(target=_sync_loop, daemon=True)
    t.start()
    return t
