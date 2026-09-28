"""
============================================================
   GHOST SYNC — Multi-Repo Backup (Code + DB + Sessions)
   Optional module — bot works even if this fails

   Env vars needed:
     GITHUB_TOKEN          — Personal access token
     GITHUB_REPO_DB        — Repo for DB (e.g. user/Data-base-)
     GITHUB_REPO_SESSIONS  — Repo for sessions (e.g. user/Sessions)
     GITHUB_REPO_MAIN      — (optional) Repo for code

   Credit: @Anonymous_User_37
============================================================
"""
import os, sys, time, threading, base64, json
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None

# ══════════════════════ CONFIG ══════════════════════
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# 3 separate repos
GITHUB_REPO_MAIN = os.getenv("GITHUB_REPO_MAIN",
                              "jedop62502-hue/Reaction-Bot")
GITHUB_REPO_DB = os.getenv("GITHUB_REPO_DB",
                           "jedop62502-hue/Data-base-")
GITHUB_REPO_SESSIONS = os.getenv("GITHUB_REPO_SESSIONS",
                                 "jedop62502-hue/Sessions")

GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")

# File paths within each repo
GITHUB_FILE_PATH = os.getenv("GITHUB_FILE_PATH", "ghost_users.db")
GITHUB_SESSIONS_PATH = os.getenv("GITHUB_SESSIONS_PATH", "sessions.json")

SYNC_INTERVAL = int(os.getenv("GITHUB_SYNC_INTERVAL", "180"))
LOCAL_DB_PATH = os.getenv("LOCAL_DB_PATH", "ghost_users.db")
SESSIONS_DIR = os.getenv("SESSIONS_DIR", "sessions")

# ══════════════════════ STATE ══════════════════════
_STATS = {
    "uploads": 0,
    "downloads": 0,
    "merges": 0,
    "errors": 0,
    "last_sync": None,
    "last_error": None,
}
_LOCK = threading.Lock()
_DIRTY = False
_THREAD_STARTED = False


# ══════════════════════ PUBLIC HELPERS ══════════════════════
def is_enabled():
    if requests is None:
        return False
    if not GITHUB_TOKEN:
        return False
    return bool(GITHUB_REPO_DB or GITHUB_REPO_SESSIONS or GITHUB_REPO_MAIN)


def mark_dirty():
    global _DIRTY
    _DIRTY = True


def get_stats():
    with _LOCK:
        return dict(_STATS)


def _record_error(msg):
    with _LOCK:
        _STATS["errors"] += 1
        _STATS["last_error"] = msg[:200]


# ══════════════════════ API HELPERS ══════════════════════
def _api_url_db():
    repo = GITHUB_REPO_DB or GITHUB_REPO_MAIN
    return (f"https://api.github.com/repos/{repo}/contents/"
            f"{GITHUB_FILE_PATH}")


def _api_url_sessions():
    repo = GITHUB_REPO_SESSIONS or GITHUB_REPO_MAIN
    return (f"https://api.github.com/repos/{repo}/contents/"
            f"{GITHUB_SESSIONS_PATH}")


def _headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "GhostBot/2.0",
    }


def _get_remote_sha(url):
    try:
        r = requests.get(
            url,
            headers=_headers(),
            params={"ref": GITHUB_BRANCH},
            timeout=15,
        )
        if r.status_code == 200:
            return r.json().get("sha")
        return None
    except Exception as e:
        _record_error(f"get_sha: {str(e)[:100]}")
        return None


# ══════════════════════ DB UPLOAD / DOWNLOAD ══════════════════════
def upload_db(force=False):
    global _DIRTY
    if not is_enabled():
        return False, "Sync disabled"
    if not os.path.exists(LOCAL_DB_PATH):
        return False, "Local DB missing"
    if not force and not _DIRTY:
        return False, "Not dirty"

    try:
        with open(LOCAL_DB_PATH, "rb") as f:
            content = f.read()
        if len(content) == 0:
            return False, "Empty DB"

        encoded = base64.b64encode(content).decode("ascii")
        url = _api_url_db()
        sha = _get_remote_sha(url)

        payload = {
            "message": f"Auto-sync DB: {datetime.utcnow().isoformat()}Z",
            "content": encoded,
            "branch": GITHUB_BRANCH,
        }
        if sha:
            payload["sha"] = sha

        r = requests.put(
            url,
            headers=_headers(),
            json=payload,
            timeout=30,
        )
        if r.status_code in (200, 201):
            with _LOCK:
                _STATS["uploads"] += 1
                _STATS["last_sync"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")
            _DIRTY = False
            return True, f"Uploaded ({len(content)} bytes)"
        else:
            _record_error(f"HTTP {r.status_code}")
            return False, f"HTTP {r.status_code}"
    except Exception as e:
        _record_error(f"upload: {str(e)[:100]}")
        return False, str(e)[:150]


def download_db():
    if not is_enabled():
        return False, "Sync disabled"
    try:
        url = _api_url_db()
        r = requests.get(
            url,
            headers=_headers(),
            params={"ref": GITHUB_BRANCH},
            timeout=30,
        )
        if r.status_code == 404:
            return False, "New DB"
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"

        data = r.json()
        content_b64 = data.get("content", "")
        if not content_b64:
            return False, "No content"

        clean = content_b64.replace("\n", "").replace("\r", "")
        decoded = base64.b64decode(clean)

        # Backup old
        if os.path.exists(LOCAL_DB_PATH):
            try:
                backup = f"{LOCAL_DB_PATH}.backup"
                if os.path.exists(backup):
                    os.remove(backup)
                os.rename(LOCAL_DB_PATH, backup)
            except Exception:
                pass

        with open(LOCAL_DB_PATH, "wb") as f:
            f.write(decoded)

        with _LOCK:
            _STATS["downloads"] += 1
            _STATS["last_sync"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S")
        return True, f"Downloaded ({len(decoded)} bytes)"
    except Exception as e:
        _record_error(f"download: {str(e)[:100]}")
        return False, str(e)[:150]


# ══════════════════════ DB MERGE (no delete) ══════════════════════
def merge_db_download():
    """
    Download remote DB and MERGE with local (no data loss).
    Only adds new rows, never deletes.
    """
    if not is_enabled():
        return False, "Sync disabled"
    try:
        url = _api_url_db()
        r = requests.get(
            url,
            headers=_headers(),
            params={"ref": GITHUB_BRANCH},
            timeout=30,
        )
        if r.status_code == 404:
            return False, "New DB (no merge needed)"
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"

        data = r.json()
        content_b64 = data.get("content", "")
        if not content_b64:
            return False, "No content"

        clean = content_b64.replace("\n", "").replace("\r", "")
        remote_bytes = base64.b64decode(clean)

        # Save remote to temp
        temp_path = f"{LOCAL_DB_PATH}.remote"
        with open(temp_path, "wb") as f:
            f.write(remote_bytes)

        if os.path.exists(LOCAL_DB_PATH):
            merged_count = _merge_sqlite_dbs(LOCAL_DB_PATH, temp_path)
            try:
                os.remove(temp_path)
            except Exception:
                pass
            with _LOCK:
                _STATS["merges"] += 1
                _STATS["last_sync"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")
            return True, f"Merged {merged_count} rows"
        else:
            # No local — just move
            os.rename(temp_path, LOCAL_DB_PATH)
            with _LOCK:
                _STATS["downloads"] += 1
                _STATS["last_sync"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")
            return True, f"Loaded ({len(remote_bytes)} bytes)"
    except Exception as e:
        _record_error(f"merge: {str(e)[:100]}")
        return False, str(e)[:150]


def _merge_sqlite_dbs(local_path, remote_path):
    """
    Merge remote SQLite into local.
    Uses INSERT OR IGNORE — never deletes.
    """
    import sqlite3
    merged = 0
    try:
        conn = sqlite3.connect(local_path)
        try:
            # Attach remote
            conn.execute("ATTACH DATABASE ? AS remote", (remote_path,))

            # Get all tables from remote
            tables = conn.execute("""
                SELECT name FROM remote.sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """).fetchall()

            for (table,) in tables:
                try:
                    # Check if table exists in local
                    exists = conn.execute("""
                        SELECT name FROM sqlite_master
                        WHERE type='table' AND name=?
                    """, (table,)).fetchone()
                    if not exists:
                        # Create table from remote schema
                        schema = conn.execute("""
                            SELECT sql FROM remote.sqlite_master
                            WHERE type='table' AND name=?
                        """, (table,)).fetchone()
                        if schema and schema[0]:
                            conn.execute(schema[0])
                    # Get columns
                    cols = conn.execute(
                        f"PRAGMA remote.table_info({table})"
                    ).fetchall()
                    if not cols:
                        continue
                    col_names = [c[1] for c in cols]
                    cols_str = ", ".join(col_names)

                    # INSERT OR IGNORE from remote
                    cur = conn.execute(
                        f"INSERT OR IGNORE INTO {table} ({cols_str}) "
                        f"SELECT {cols_str} FROM remote.{table}"
                    )
                    merged += cur.rowcount or 0
                except Exception:
                    continue

            conn.commit()
            conn.execute("DETACH DATABASE remote")
        finally:
            conn.close()
    except Exception as e:
        _record_error(f"merge_helper: {str(e)[:100]}")
    return merged


# ══════════════════════ SESSIONS UPLOAD / DOWNLOAD ══════════════════════
def upload_sessions(force=False):
    if not is_enabled():
        return False, "Sync disabled"
    if not os.path.isdir(SESSIONS_DIR):
        return False, "Sessions dir missing"

    try:
        sessions_data = {}
        for fname in os.listdir(SESSIONS_DIR):
            if not fname.endswith(".session"):
                continue
            fpath = os.path.join(SESSIONS_DIR, fname)
            try:
                with open(fpath, "rb") as f:
                    content = f.read()
                sessions_data[fname] = base64.b64encode(
                    content).decode("ascii")
            except Exception:
                continue

        if not sessions_data:
            return False, "No sessions"

        json_str = json.dumps(sessions_data)
        json_bytes = json_str.encode("utf-8")
        encoded = base64.b64encode(json_bytes).decode("ascii")

        url = _api_url_sessions()
        sha = _get_remote_sha(url)

        payload = {
            "message": f"Auto-sync sessions ({len(sessions_data)}): "
                       f"{datetime.utcnow().isoformat()}Z",
            "content": encoded,
            "branch": GITHUB_BRANCH,
        }
        if sha:
            payload["sha"] = sha

        r = requests.put(
            url,
            headers=_headers(),
            json=payload,
            timeout=60,
        )
        if r.status_code in (200, 201):
            with _LOCK:
                _STATS["uploads"] += 1
            return True, f"Uploaded {len(sessions_data)} sessions"
        else:
            _record_error(f"sessions HTTP {r.status_code}")
            return False, f"HTTP {r.status_code}"
    except Exception as e:
        _record_error(f"sessions upload: {str(e)[:100]}")
        return False, str(e)[:150]


def download_sessions():
    if not is_enabled():
        return False, "Sync disabled"
    try:
        url = _api_url_sessions()
        r = requests.get(
            url,
            headers=_headers(),
            params={"ref": GITHUB_BRANCH},
            timeout=60,
        )
        if r.status_code == 404:
            return False, "New sessions"
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"

        data = r.json()
        content_b64 = data.get("content", "")
        if not content_b64:
            return False, "No content"

        clean = content_b64.replace("\n", "").replace("\r", "")
        decoded = base64.b64decode(clean)
        json_str = decoded.decode("utf-8")
        sessions_data = json.loads(json_str)

        if not sessions_data:
            return False, "Empty sessions"

        if not os.path.isdir(SESSIONS_DIR):
            os.makedirs(SESSIONS_DIR, exist_ok=True)

        count = 0
        for fname, b64_content in sessions_data.items():
            try:
                content = base64.b64decode(b64_content)
                fpath = os.path.join(SESSIONS_DIR, fname)
                # Only write if new (don't overwrite existing)
                if not os.path.exists(fpath):
                    with open(fpath, "wb") as f:
                        f.write(content)
                    count += 1
                else:
                    count += 1
            except Exception:
                continue

        with _LOCK:
            _STATS["downloads"] += 1
        return True, f"Downloaded {count} sessions"
    except Exception as e:
        _record_error(f"sessions download: {str(e)[:100]}")
        return False, str(e)[:150]


# ══════════════════════ BOOT FUNCTIONS ══════════════════════
def boot_db():
    """Boot: merge DB from GitHub (no delete)"""
    if not is_enabled():
        return False, "Disabled"
    print("[SYNC] Loading memory...", flush=True)
    ok, msg = merge_db_download()
    if not ok and "New DB" in msg:
        print(f"[SYNC] Memory: {msg}", flush=True)
        return False, msg
    print(f"[SYNC] Memory: {msg}", flush=True)
    return ok, msg


def boot_sessions():
    if not is_enabled():
        return False, "Disabled"
    print("[SYNC] Loading access keys...", flush=True)
    ok, msg = download_sessions()
    print(f"[SYNC] Keys: {msg}", flush=True)
    return ok, msg


# ══════════════════════ SYNC THREAD ══════════════════════
def _sync_loop():
    counter = 0
    while True:
        try:
            time.sleep(SYNC_INTERVAL)
            counter += 1
            if _DIRTY:
                upload_db(force=False)
            # Every 10 cycles, upload sessions
            if counter % 10 == 0:
                upload_sessions(force=True)
        except Exception as e:
            _record_error(str(e)[:100])
            time.sleep(60)


def start_sync_thread():
    global _THREAD_STARTED
    if _THREAD_STARTED:
        return
    if not is_enabled():
        print("[SYNC] ⚠️ Disabled (no token/repo)", flush=True)
        return
    try:
        # Boot: merge DB + load sessions
        boot_db()
        boot_sessions()
        # Start thread
        t = threading.Thread(target=_sync_loop, daemon=True,
                             name="gh_sync")
        t.start()
        _THREAD_STARTED = True
        print(f"[SYNC] ✅ Auto-backup active", flush=True)
    except Exception as e:
        print(f"[SYNC] ⚠️ Failed: {e}", flush=True)


# ══════════════════════ SELF TEST ══════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  GHOST SYNC — MULTI-REPO SELF TEST")
    print("=" * 60)
    print(f"  Token:     {'✅ SET' if GITHUB_TOKEN else '❌ MISSING'}")
    print(f"  Main repo: {GITHUB_REPO_MAIN or '—'}")
    print(f"  DB repo:   {GITHUB_REPO_DB or '—'}")
    print(f"  Sessions:  {GITHUB_REPO_SESSIONS or '—'}")
    print(f"  Branch:    {GITHUB_BRANCH}")
    print(f"  Enabled:   {'✅' if is_enabled() else '❌'}")
    print("=" * 60)
    if not is_enabled():
        print("\n⚠️  Set env vars first:")
        print("   export GITHUB_TOKEN='ghp_xxxxx'")
        print("   export GITHUB_REPO_DB='user/repo-db'")
        print("   export GITHUB_REPO_SESSIONS='user/repo-sessions'")
        sys.exit(1)
    print("\n⬇️  Testing merge download...")
    ok, msg = merge_db_download()
    print(f"   {'✅' if ok else '❌'} {msg}")
    print("\n⬆️  Testing upload...")
    mark_dirty()
    ok, msg = upload_db(force=True)
    print(f"   {'✅' if ok else '❌'} {msg}")
    print("\n📊 Stats:")
    for k, v in get_stats().items():
        print(f"   {k}: {v}")
