"""GitHub Sync Module - v60"""
import base64
import json
import sqlite3
import requests
from datetime import datetime

GITHUB_TOKEN = "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"
GITHUB_USERNAME = "jedop62502-hue"
GITHUB_REPO = "Reaction-Bot"
GITHUB_BRANCH = "main"

GH_API = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents"

GH_FILES = {
    "users": "data/users.json",
    "approvals": "data/approvals.json",
    "bots": "data/bots.json",
    "watchers": "data/watchers.json",
    "templates": "data/templates.json",
    "referrals": "data/referrals.json",
    "notifications": "data/notifications.json",
    "queue": "data/queue.json",
    "payments": "data/payments.json",
    "force_channels": "data/force_channels.json",
    "team": "data/team.json",
    "custom_packs": "data/custom_packs.json",
    "reactions": "data/reactions.json",
    "config": "data/config.json",
    "security_logs": "data/security_logs.json",
}


def _headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }


def gh_read(path):
    try:
        r = requests.get(f"{GH_API}/{path}", headers=_headers(), timeout=20)
        if r.status_code == 200:
            data = r.json()
            content = base64.b64decode(data["content"]).decode("utf-8")
            return content, data.get("sha")
        elif r.status_code == 404:
            return None, None
        print(f"[GH] read {path}: {r.status_code}", flush=True)
        return None, None
    except Exception as e:
        print(f"[GH] read {path} err: {e}", flush=True)
        return None, None


def gh_write(path, content_str, message=None):
    try:
        _, sha = gh_read(path)
        content_b64 = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
        if not message:
            message = f"update {path.split('/')[-1]} — {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        payload = {"message": message, "content": content_b64, "branch": GITHUB_BRANCH}
        if sha:
            payload["sha"] = sha
        r = requests.put(f"{GH_API}/{path}", headers=_headers(), json=payload, timeout=30)
        if r.status_code in (200, 201):
            return True
        print(f"[GH] write {path}: {r.status_code} {r.text[:80]}", flush=True)
        return False
    except Exception as e:
        print(f"[GH] write {path} err: {e}", flush=True)
        return False


def gh_save_table(db_file, table_name):
    """Save single table."""
    path = GH_FILES.get(table_name)
    if not path:
        return False
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(f"SELECT * FROM {table_name}").fetchall()
        conn.close()
        data = [dict(r) for r in rows]
        json_str = json.dumps(data, indent=2, ensure_ascii=False, default=str)
        return gh_write(path, json_str)
    except Exception as e:
        print(f"[GH] save {table_name} err: {e}", flush=True)
        return False


def gh_save_all(db_file, tables=None):
    if tables is None:
        tables = list(GH_FILES.keys())
    results = {}
    for t in tables:
        results[t] = gh_save_table(db_file, t)
    return results


def gh_load_table(db_file, table_name, create_sql, columns):
    """Load single table into SQLite."""
    path = GH_FILES.get(table_name)
    if not path:
        return 0
    try:
        content, _ = gh_read(path)
        if content is None:
            return 0
        data = json.loads(content)
        if not isinstance(data, list):
            return 0
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute(create_sql)
        if table_name != "bots":  # bots merge karo, delete na karo
            c.execute(f"DELETE FROM {table_name}")
        inserted = 0
        for row in data:
            try:
                cols, vals = [], []
                for col in columns:
                    if col in row:
                        cols.append(col)
                        vals.append(row[col])
                if not cols:
                    continue
                ph = ",".join(["?"] * len(cols))
                sql = f"INSERT OR REPLACE INTO {table_name} ({','.join(cols)}) VALUES ({ph})"
                c.execute(sql, vals)
                inserted += 1
            except Exception:
                pass
        conn.commit()
        conn.close()
        return inserted
    except Exception as e:
        print(f"[GH] load {table_name} err: {e}", flush=True)
        return 0


def gh_load_all(db_file, schemas):
    results = {}
    for name, (create_sql, columns) in schemas.items():
        results[name] = gh_load_table(db_file, name, create_sql, columns)
    return results
