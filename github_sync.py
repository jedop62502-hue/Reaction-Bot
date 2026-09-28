"""
============================================================
   GHOST SYNC v76 — Multi-Repo + Direct .session Files
   - DB sync with merge (no delete)
   - Sessions sync (individual .session files)
   - Optional module — bot works without this

   Env vars:
     GITHUB_TOKEN          — Personal access token
     GITHUB_REPO_DB        — Repo for DB (e.g. user/Data-base-)
     GITHUB_REPO_SESSIONS  — Repo for sessions (e.g. user/Sessions)
     GITHUB_REPO_MAIN      — (optional) Repo for code
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

GITHUB_REPO_MAIN = os.getenv("GITHUB_REPO_MAIN",
                              "jedop62502-hue/Reaction-Bot")
GITHUB_REPO_DB = os.getenv("GITHUB_REPO_DB",
                           "jedop62502-hue/Data-base-")
GITHUB_REPO_SESSIONS = os.getenv("GITHUB_REPO_SESSIONS",
                                 "jedop62502-hue/Sessions")

GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")
GITHUB_FILE_PATH = os.getenv("GITHUB_FILE_PATH", "ghost_users.db")

SYNC_INTERVAL = int(os.getenv("GITHUB_SYNC_INTERVAL", "180"))
LOCAL_DB_PATH = os.getenv("LOCAL_DB_PATH", "ghost_users.db")
SESSIONS_DIR = os.getenv("SESSIONS_DIR", "sessions")

# ══════════════════════ STATE ══════════════════════
_STATS = {
    "uploads": 0,
    "downloads": 0,
    "merges": 0,
    "session_uploads": 0,
    "session_downloads": 0,
    "errors": 0,
    "last_sync": None,
    "last_error": None,
}
_LOCK = threading.Lock()
_DIRTY = False
_THREAD_STARTED = False


def _log(msg, level="info"):
    """Debug logger (always prints)"""
    ts = datetime.now().strftime("%H:%M:%S")
    ic = {"info": "🔍", "ok": "✅", "fail": "❌", "warn": "⚠️",
          "sync": "🔄", "db": "💾", "sess": "🔐"}
    print(f"[{ts}] {ic.get(level,'•')} [SYNC] {msg}", flush=True)


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
def _headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "GhostSync/2.0",
    }


def _db_api_url():
    repo = GITHUB_REPO_DB or GITHUB_REPO_MAIN
    return (f"https://api.github.com/repos/{repo}/contents/"
            f"{GITHUB_FILE_PATH}")


def _sessions_list_url():
    repo = GITHUB_REPO_SESSIONS or GITHUB_REPO_MAIN
    return f"https://api.github.com/repos/{repo}/contents/"


def _session_file_url(filename):
    repo = GITHUB_REPO_SESSIONS or GITHUB_REPO_MAIN
    return (f"https://api.github.com/repos/{repo}/contents/"
            f"{filename}")


def _get_remote_sha(url):
    try:
        r = requests.get(
            url,
            headers=_headers(),
            params={"ref": GITHUB_BRANCH},
            timeout=15,
        )
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                return None
            return data.get("sha")
        return None
    except Exception as e:
        _record_error(f"get_sha: {str(e)[:100]}")
        return None


# ══════════════════════ DB UPLOAD ══════════════════════
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
        url = _db_api_url()
        sha = _get_remote_sha(url)

        payload = {
            "message": f"Auto-sync DB: {datetime.utcnow().isoformat()}Z",
            "content": encoded,
            "branch": GITHUB_BRANCH,
        }
        if sha:
            payload["sha"] = sha

        r = requests.put(url, headers=_headers(), json=payload, timeout=30)
        if r.status_code in (200, 201):
            with _LOCK:
                _STATS["uploads"] += 1
                _STATS["last_sync"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")
            _DIRTY = False
            _log(f"DB uploaded ({len(content)} bytes)", "ok")
            return True, f"Uploaded ({len(content)} bytes)"
        else:
            _record_error(f"HTTP {r.status_code}")
            return False, f"HTTP {r.status_code}"
    except Exception as e:
        _record_error(f"upload: {str(e)[:100]}")
        return False, str(e)[:150]


# ══════════════════════ DB DOWNLOAD + MERGE ══════════════════════
def download_db():
    """Download DB with MERGE (no delete)"""
    if not is_enabled():
        return False, "Sync disabled"
    try:
        url = _db_api_url()
        r = requests.get(url, headers=_headers(),
                         params={"ref": GITHUB_BRANCH}, timeout=30)
        if r.status_code == 404:
            _log("DB file not found on GitHub (new)", "info")
            return False, "New DB"
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"

        data = r.json()
        content_b64 = data.get("content", "")
        if not content_b64:
            return False, "No content"

        clean = content_b64.replace("\n", "").replace("\r", "")
        remote_bytes = base64.b64decode(clean)

        _log(f"Remote DB: {len(remote_bytes)} bytes", "sync")

        # Merge mode if local exists
        if os.path.exists(LOCAL_DB_PATH):
            merged = _merge_sqlite(LOCAL_DB_PATH, remote_bytes)
            if merged is not None:
                with _LOCK:
                    _STATS["merges"] += 1
                    _STATS["last_sync"] = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S")
                _log(f"Merged: {merged} rows", "ok")
                return True, f"Merged {merged} rows"
        else:
            # No local — just write
            with open(LOCAL_DB_PATH, "wb") as f:
                f.write(remote_bytes)
            with _LOCK:
                _STATS["downloads"] += 1
                _STATS["last_sync"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")
            _log(f"Downloaded DB: {len(remote_bytes)} bytes", "ok")
            return True, f"Downloaded ({len(remote_bytes)} bytes)"
    except Exception as e:
        _record_error(f"download: {str(e)[:100]}")
        return False, str(e)[:150]


def _merge_sqlite(local_path, remote_bytes):
    """
    Merge remote SQLite bytes into local DB.
    Only ADDS rows (INSERT OR IGNORE), never deletes.
    Returns merged row count or None on error.
    """
    import sqlite3
    import tempfile

    try:
        # Write remote to temp file
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            tf.write(remote_bytes)
            remote_path = tf.name

        merged_rows = 0

        conn = sqlite3.connect(local_path)
        try:
            # Attach remote
            conn.execute("ATTACH DATABASE ? AS remote", (remote_path,))

            # Get tables from remote
            tables = conn.execute("""
                SELECT name FROM remote.sqlite_master
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """).fetchall()

            for (table,) in tables:
                try:
                    # Check if table exists locally
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
                            _log(f"Created table: {table}", "db")

                    # Get columns
                    cols = conn.execute(
                        f"PRAGMA remote.table_info({table})"
                    ).fetchall()
                    if not cols:
                        continue
                    col_names = [c[1] for c in cols]
                    cols_str = ", ".join(col_names)

                    # INSERT OR IGNORE
                    cur = conn.execute(
                        f"INSERT OR IGNORE INTO {table} ({cols_str}) "
                        f"SELECT {cols_str} FROM remote.{table}"
                    )
                    cnt = cur.rowcount or 0
                    merged_rows += cnt
                    if cnt > 0:
                        _log(f"  {table}: +{cnt} rows", "sync")
                except Exception as e:
                    _log(f"  {table}: merge fail — {str(e)[:60]}", "warn")
                    continue

            conn.commit()
            conn.execute("DETACH DATABASE remote")
        finally:
            conn.close()

        # Clean temp
        try:
            os.remove(remote_path)
        except Exception:
            pass

        return merged_rows
    except Exception as e:
        _record_error(f"merge: {str(e)[:100]}")
        return None


# ══════════════════════ SESSIONS — DIRECT .session FILES ══════════════════════
def download_sessions():
    """
    Download all .session files from GitHub repo.
    Files are stored DIRECTLY in repo (no JSON).
    """
    if not is_enabled():
        return False, "Sync disabled"

    try:
        url = _sessions_list_url()
        r = requests.get(
            url,
            headers=_headers(),
            params={"ref": GITHUB_BRANCH},
            timeout=30,
        )
        if r.status_code == 404:
            _log("Sessions repo not found", "warn")
            return False, "Repo not found"
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"

        data = r.json()
        if not isinstance(data, list):
            return False, "Invalid response"

        # Filter .session files
        session_files = [
            item for item in data
            if item.get("type") == "file"
            and item.get("name", "").endswith(".session")
        ]

        if not session_files:
            _log("No .session files found", "info")
            return False, "No .session files"

        _log(f"Found {len(session_files)} .session files", "sess")

        # Ensure local dir
        if not os.path.isdir(SESSIONS_DIR):
            os.makedirs(SESSIONS_DIR, exist_ok=True)

        downloaded = 0
        skipped = 0
        failed = 0

        for i, item in enumerate(session_files, 1):
            fname = item.get("name", "")
            if not fname:
                continue

            local_path = os.path.join(SESSIONS_DIR, fname)

            # Skip if already exists
            if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                skipped += 1
                continue

            try:
                # Get file content
                file_url = item.get("url") or _session_file_url(fname)
                fr = requests.get(
                    file_url,
                    headers=_headers(),
                    params={"ref": GITHUB_BRANCH},
                    timeout=30,
                )
                if fr.status_code != 200:
                    failed += 1
                    continue

                fd = fr.json()
                content_b64 = fd.get("content", "")
                if not content_b64:
                    failed += 1
                    continue

                clean = content_b64.replace("\n", "").replace("\r", "")
                content = base64.b64decode(clean)

                with open(local_path, "wb") as f:
                    f.write(content)
                downloaded += 1

                if i % 5 == 0:
                    _log(f"Downloaded {i}/{len(session_files)}", "sess")
            except Exception as e:
                failed += 1
                _log(f"  {fname}: fail — {str(e)[:60]}", "warn")
                continue

        with _LOCK:
            _STATS["session_downloads"] += downloaded
            _STATS["last_sync"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S")

        _log(f"Sessions: ✅{downloaded} ⏭️{skipped} ❌{failed}", "ok")
        return True, f"Downloaded {downloaded} (skipped {skipped})"
    except Exception as e:
        _record_error(f"sessions download: {str(e)[:100]}")
        _log(f"Sessions download error: {str(e)[:100]}", "fail")
        return False, str(e)[:150]


def upload_sessions(force=False):
    """
    Upload local .session files to GitHub.
    Files stored DIRECTLY (no JSON wrapper).
    """
    if not is_enabled():
        return False, "Sync disabled"
    if not os.path.isdir(SESSIONS_DIR):
        return False, "Sessions dir missing"

    try:
        # List local .session files
        local_files = [
            f for f in os.listdir(SESSIONS_DIR)
            if f.endswith(".session")
        ]
        if not local_files:
            _log("No local .session files", "info")
            return False, "No sessions"

        _log(f"Uploading {len(local_files)} .session files", "sess")

        uploaded = 0
        failed = 0

        for i, fname in enumerate(local_files, 1):
            fpath = os.path.join(SESSIONS_DIR, fname)
            try:
                with open(fpath, "rb") as f:
                    content = f.read()
                if len(content) == 0:
                    failed += 1
                    continue

                encoded = base64.b64encode(content).decode("ascii")
                url = _session_file_url(fname)

                # Get existing SHA
                sha = _get_remote_sha(url)

                payload = {
                    "message": f"Sync session: {fname} "
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
                    timeout=30,
                )
                if r.status_code in (200, 201):
                    uploaded += 1
                    if i % 5 == 0:
                        _log(f"Uploaded {i}/{len(local_files)}", "sess")
                else:
                    failed += 1
                    _log(f"  {fname}: HTTP {r.status_code}", "warn")
            except Exception as e:
                failed += 1
                _log(f"  {fname}: fail — {str(e)[:60]}", "warn")
                continue

        with _LOCK:
            _STATS["session_uploads"] += uploaded

        _log(f"Sessions upload: ✅{uploaded} ❌{failed}", "ok")
        return True, f"Uploaded {uploaded}"
    except Exception as e:
        _record_error(f"sessions upload: {str(e)[:100]}")
        return False, str(e)[:150]


# ══════════════════════ BOOT FUNCTIONS ══════════════════════
def boot_db():
    if not is_enabled():
        return False, "Disabled"
    _log("Loading memory...", "sync")
    ok, msg = download_db()
    _log(f"Memory: {msg}", "ok" if ok else "info")
    return ok, msg


def boot_sessions():
    if not is_enabled():
        return False, "Disabled"
    _log("Loading access keys...", "sync")
    ok, msg = download_sessions()
    _log(f"Keys: {msg}", "ok" if ok else "info")
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
            # Every 10 cycles (~30 min), upload sessions
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
        _log("Disabled (no token/repo)", "warn")
        return
    try:
        # Boot: DB + sessions
        boot_db()
        boot_sessions()
        # Start thread
        t = threading.Thread(target=_sync_loop, daemon=True,
                             name="gh_sync")
        t.start()
        _THREAD_STARTED = True
        _log(f"Auto-backup active (every {SYNC_INTERVAL}s)", "ok")
    except Exception as e:
        _log(f"Failed to start: {e}", "fail")


# ══════════════════════ SELF TEST ══════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  GHOST SYNC — SELF TEST")
    print("=" * 60)
    print(f"  Token:     {'✅ SET' if GITHUB_TOKEN else '❌ MISSING'}")
    print(f"  DB repo:   {GITHUB_REPO_DB or '—'}")
    print(f"  Sess repo: {GITHUB_REPO_SESSIONS or '—'}")
    print(f"  Main repo: {GITHUB_REPO_MAIN or '—'}")
    print(f"  Branch:    {GITHUB_BRANCH}")
    print(f"  Enabled:   {'✅' if is_enabled() else '❌'}")
    print("=" * 60)
    if not is_enabled():
        print("\n⚠️  Set env vars first:")
        print("   export GITHUB_TOKEN='ghp_xxxxx'")
        print("   export GITHUB_REPO_DB='user/repo-db'")
        print("   export GITHUB_REPO_SESSIONS='user/repo-sessions'")
        sys.exit(1)

    print("\n⬇️  Testing DB download + merge...")
    ok, msg = download_db()
    print(f"   {'✅' if ok else '❌'} {msg}")

    print("\n⬇️  Testing sessions download...")
    ok, msg = download_sessions()
    print(f"   {'✅' if ok else '❌'} {msg}")

    print("\n📊 Stats:")
    for k, v in get_stats().items():
        print(f"   {k}: {v}")
