"""
============================================================
   GHOST REACTION BOT - v49
   Full Feature Control | Per-User Settings | Auto-Watcher
   Credit: @Anonymous_User_37
============================================================
"""

import os
import random
import asyncio
import re
import sqlite3
import requests
import traceback
from datetime import datetime, timedelta

from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.messages import (
    ImportChatInviteRequest,
    AddChatUserRequest,
)
from telethon.tl.functions.channels import (
    InviteToChannelRequest,
    GetParticipantRequest,
    EditAdminRequest,
    GetParticipantsRequest,
)
from telethon.tl.types import (
    Channel,
    Chat,
    ChatAdminRights,
    ChannelParticipantsAdmins,
)

try:
    from telethon.tl.types import KeyboardButtonStyle
    HAS_BUTTON_STYLE = True
    print("[STARTUP] ✅ KeyboardButtonStyle available")
except ImportError:
    KeyboardButtonStyle = None
    HAS_BUTTON_STYLE = False
    print("[STARTUP] ⚠️ KeyboardButtonStyle NOT available")

from telethon.errors import FloodWaitError
from telethon.errors.rpcerrorlist import (
    MessageIdInvalidError,
    MessageNotModifiedError,
    UserNotParticipantError,
    UserAlreadyParticipantError,
)

# ==================== CONFIG ====================
API_ID = 30217812
API_HASH = "d21066a90786cf2dd348b907ece69d24"

ADMIN_SESSION = "1BJWap1wBu2X5POvvWDOSvJZAROd9WIKpJMpSIf-W3skkHehdGLol5KkobjCIfohj9gFhHqh3UKkwjLJAsMqDbuWAflGN8yb1Qu7LxiKBsZCFYHKAHKBfxZgJyv35ivBxl881TvLZ6dbpdfM4_-66CTW7HnBE-j0_yktVaX-q3o1VaL3HYZJkb_wnI5BaJow7s9IHYtqlyWM2RYeQgcQVc23CDjHKLR4qdFpaMM_T2SuQQ478eDnUGQ-R891NssFOq0lOGs765CyI1ngt_C-NU3PYpvHVyJhFHZ3eBqsrgnmP0tpeSC1mJ2egouxeevr7pPUKMdMI_QyoA0aiTviAMEGlERWbrEA="

BOT_TOKEN = "8878162447:AAGMBnukLS2jPxfBthfeY1GAblCCrgtaH2M"

BOT_TOKENS = [
    "8841673258:AAHmkFSMiuS6eja_CnqVH548wcam_XBRAY4",
    "7593703253:AAEgY5r_UoBtXYiCntg6wt_seiBbhxqrMeI",
    "8553819198:AAEtfCIbrvgkvtAhUNMhull2sYZcnBVSj8o",
    "8974028456:AAHmZvMGFbGBy0ie4pQfICxXnqy5GG4Racg",
    "8988266285:AAFrB5RXFcbDyd_-_RZrnMpNVDakIrXT_ePc",
    "8708232817:AAH6jRVisH7W1GvVdZIDbPT-LBELs0NVVzY",
    "8913217410:AAG1sjOnzMGJgGd1wjmbQevpI9QVrKeAdxI",
    "8820548215:AAG9cyP2k9MBkUgJ4q2sQH8W9AaTh1nAcdQ",
    "8968734078:AAGEq778W3nJlADAQdp_zaiatlW-UyDKj1Q",
    "8328358987:AAEcvUOW0AIZBsYrl5C1ediUbR9rCkHVrtg",
    "8728464321:AAGsyJihokd7r5Tlp54W4lPWrFpvRlULRFE",
    "8930721931:AAErSyWq5cRUC7NjfLzLU4F7vuHTF9vfVkM",
    "8783856775:AAE5oRj-CfvKu1QkbabnpYf_NresBkFN_FA",
    "8748532509:AAEQYzaL4BBLddWoF-laUlQ-dR_nC-2v3sQ",
    "8956849671:AAGToCuy-bsGRMxexUAjWIHBiO-XK7mTSTg",
    "8846722436:AAE4blebnl-47O8D7MIYEpaDvlSE1T6PjOs",
    "8944172439:AAF6Bob4CFkN9J1uYfHhzR5F_DboZo5pZ2o",
    "8745749488:AAH9iBk_3OhdRQSxL0_i7ZKY9muQlhruLUw",
    "8841955340:AAG1wx_6Qg-mRdulTXA_10ZyUMt5uS1pM7E",
    "8924067849:AAGTfhAeymFPNkzHZs7qYfoLdHh1Eci9LYM",
    "8771116985:AAEVflfEL_jhDlCjgjuEGEq5ew7XQZtA42w",
    "8603663849:AAFULr5Oa2hxKVvXP9SEUfgTHwOKVsnEVJE",
    "8931110714:AAFc7jMeqLrZNnJT-Gu1PvOCC1KtYiphQcM",
    "8803252857:AAFeiuLDYZq1vXl0HPixIny7sVgwInbeDI4",
    "8979609203:AAH2y70TChxnGN12meD79zfhvgrOUcLxgpQ",
    "8905843316:AAEt7EiKOinstEIFVblgKImWKpDMAx3VOss",
    "8989541204:AAHSlSxo2BTWo4CwHi99wnO2seJ4Q6Ijcl0",
    "8944322541:AAE-L4laExHQoz0RtGGZH4rR0w9HRBsZ5ZQ",
    "8641606957:AAFo2g3KF3_MM2gSqfoLrO-GcdeZDrku_rI",
    "8964416323:AAFCgLhsuDRX6e_qKSdMSeJMvOnftyJIpjw",
    "8857844062:AAHkqUl93T5IIeQzRVI4gTbDtGNXM2l56vY",
    "8819430996:AAG61wjEPXzQt51-XXvxLk44xUUVevEM-Zg",
    "8822557788:AAGo0EpEEj6oPTDS6AZvFQRJLbY0SKILm9E",
    "8698942203:AAHqYg0fbbw91_VXLy-QMaAweNOYpTt0_8U",
    "8685235239:AAFde1c3wMjQUNky9DBFjPZRwiQIzwv2eWM",
    "8768563277:AAEw6E0YI9VvaWKWqGrWV7r__VIECYfd4Tw",
    "8510446309:AAHhEoCC3elgLIsDUNQx8sdT97OOOVKFLGQ",
    "8950435967:AAHz9cX7ni-h9cYfDB-B0Ze7hbTTge9aSS0",
    "8952785819:AAHlGqZdLvIAu_7Gc5cnEWIk_qcX05Uu3L8",
    "8868030693:AAEwQNOs9GLbryk2NyKNCCUioYvEguTcLZA",
    "8757705970:AAEHdekrha8nKfM1dD_K2qQDGEpM62bq7fo",
    "8815901180:AAFvbu5PHknm7Yuiyf4RvK_vMtYW0-KY4oA",
    "8785643638:AAGk7RfKtOkFgGA9VMc-R2KUuot2chkErfY",
    "8871939279:AAFNABGPWmo-jYugam_8yosqvTvlqUs6rOw",
    "8853912055:AAEBXCqq444SNm1PuAWDhAGmqHhsXUhgGhM",
    "8821582256:AAG8RtlrztqJxaX7Tm02A_s9FQhRYoCLOFY",
    "8900198440:AAGxqWK8pv9ymM8Q3h_8LkM3bN6xYzKZfZE",
    "8714611659:AAGYKV151mrnPd8L4un2jqyeGKYJWgWyUNM",
    "8938927350:AAGqDG704mjg-jRhvy5I23pGKsLc5NRXHQY",
    "8256889928:AAHi_MEPlcCX_RAGGijMjjEFu7dPTPL0WZc",
    "8833683561:AAFYJK1JFpZ70AQcV4qGJV6LEZwAqGlqdnM",
    "8100369464:AAEgoYuvVDyiamsJE4Wvn8tNP3AeULjr7qQ",
    "8662013526:AAFpMDtWcV-vPVIIUhwzF890JbzvPONvHeE",
    "8729112057:AAHNJH5Q52rG06cxUhVH5v9abckcorrk-cc",
    "8471788383:AAFh-7qdOm0p_YZfHu-cFlnX0EvbaR_EPNA",
    "8891259440:AAFkd8xRSTXYjLYBoc5BJCUraaECgJyw7MA",
    "8983293074:AAGAEWkH_fRsE1ZHDO6Y8400ItngSMUzWn0",
    "8471875480:AAExUSZAMmB3DJDjBHJJzQFreb4wuUhF-LE",
    "8861709151:AAGkJdg6dfNHgkImCoXLeqpj09BXaFn9K3A",
    "8609489669:AAHFCpioHV24w5UGNsCwEshFmb9SbAsexCQ",
    "8820797593:AAFTZM5d-2lFKU01RtDHwihAHESc6diPfQM",
    "8962290157:AAHXjwHwh_t9msQi0CcudyXM2k220WCDCK0",
    "8008985452:AAG8Bdv1_RxeUMJVls6_Xii1p_inQNlVgxo",
    "8971769677:AAH35Rj_VJbjRlJtFcqQIeuEJ2hWlfjKSU0",
    "8990507622:AAHnMjPXwH2pU9X5wEAmWVWT5M7MwZy5dag",
    "8784663275:AAH8P9qX9v9csE9I-KXnsRcgkjchRsQnDso",
    "8938896874:AAFL2y5KXpzsatkpLIFI057z28GnXU68JRY",
    "8988481023:AAFYAdCPKeFf0ggzW7rVztxQGo7ZxTFEGK8",
    "8994425405:AAGP6ekwed9AHZ3gSf2CsvFSY1EYrZpvNaE",
    "8960571934:AAFlTT44gSwOKsR9-EIRRSV5sLVYOfB69Lg",
    "8779154787:AAFTgYyGhFH9tl886CCAJf693FDcVNhV9U0",
    "8903745472:AAEUCdpnOmFb7FvxAPWYyI9hiHqJJvgxYeQ",
    "8996047725:AAF4hqBOfZX9KkvKrRtzWVKmAMih5rWGd3k",
    "8813887147:AAHPuB5fPRYsZPsdAzywzvEcFBKESdDzmFI",
    "8918383154:AAGD9zce0bs0NOdr2BRiMYQYTgB5yYfHM00",
    "8350933617:AAEf3w6E_m9A_-0Gjo9ipB6-gF1gnYh6u1M",
    "8965953734:AAEMAsvzZE-3Yxf7_ZawAHrG5EN9ewNAfro",
    "8221570065:AAFUFQuB2w2aXjGhh9PtTSbOYi2knb5cEnc",
    "8919303440:AAE2c4d_UwTHCWnm3LGOZ0mKntWrK11g78w",
    "8832547686:AAHl5TnZF5yddtqgnWTHScuIQ3H_D-5FyiE",
    "8949714253:AAEq-kdm7HUj17a2S-2PV7FuuGvUIKusk7Q",
    "8950470890:AAFOc5fE-55FU8fp07HvrrwbKFDtokVz37U",
    "8816997120:AAG3hoky363ACg0sNLTHAz2gdvZ6GBDdUk4",
    "8857013054:AAGKXdUshAe2bZEPHcfxabK7cEpNPfZZbkA",
    "8826047151:AAGIFXxzoVHhNtpca5bavuo6mcKLgUo89Zg",
    "8968831352:AAGFUCm9G_tnVrEskE2S8tmjkucteWCyRSo",
    "8889331184:AAETFEujC9Tkdlrnzr-etu3MUy9Usv_n2tg",
    "8189182599:AAGW4N-_kDhi__wdDxvELX_JqPRyDy4f2CI",
    "8899796556:AAFpkw6ou_KLLNpxc799wff01Df8ARGf6AE",
    "8913059580:AAGYXEjE-AWLsrSt1G8Fhpw0_1o-SiTen_Q",
    "8623196341:AAEWQX-5V9CiearLhCjCIUJ9dkJyltFHaBQ",
    "8893398545:AAG6ytTXtGXsoWG6vFRylbOYXfldHpMzq7s",
    "8552097300:AAFp3DZvoxoZoWTdT-JDGzzYD9MybMus--Y",
    "8981400829:AAHJYVnt0sjQCw47c8Wse9kysLPrT52IBpY",
    "8963410266:AAGR9sXmxA1rrciIz5MZMxByGg1wVOEN9Zg",
    "8716210889:AAESTa6z6lhIL83a4N2ld1iXcA_L-WqRJhg",
    "8912557604:AAHQq888h9ojNuGYssw7n9Ro64rYIz_8SlY",
    "8291028314:AAFrLRo2E_jT3bazVkDKpgd42ppGFJgFV8c",
    "8418409480:AAFYfuWbuuyaD54Ks_ThQAGEHTw3nzbrTyw",
    "8935405135:AAFC3ONCxh-LM2axSRVj0T_GkRFrGf242BY",
    "8862081715:AAGAKOqQZPEm6t1rs1S8W0aQ0ctGv_rPrZ8",
    "8950949832:AAHPAuHamEqE-B9Z3U5dpL4pUyTbcqfETIA",
    "8841428180:AAFPjIUBID7jeC2hj5aM4PuWo2-NJ29sWjM",
    "8941585136:AAFcpOoVjVYuU0UrOvO0w8zd1k0ZxDl2Qlo",
    "8634996391:AAGpg8B4Uh9KIH4bd7jlszmzI03zUqBQnVQ",
    "8813724246:AAHP0rnBLPfBoQmcftjk4i7nfVMZZVp6UrE",
    "8741375662:AAHgRJAK3FLPb9y_Gc-Y8yktiTC4Lr2S-18",
    "8974865654:AAFF4uB0yJLSJSHJTHXigvrPW-rWhB6qFeo",
    "8911644039:AAFYE8CTP7jmwLQljMlAnSzpe02G19VvZwE",
    "8962352673:AAFR6qFzABemeFI_5CX8EXifoxGBI5ZyrPw",
    "8857051106:AAEbY0nWQUsNxQBFJbnCCfv_bZn9vvZjeng",
    "8938143439:AAE7og1KxgCKE_2s_m3nCl4GDuvh_MvPs8w",
    "8824445026:AAEwXki7eTKBmHzC8HVjALgnNB4XhzucfE0",
    "8653676138:AAEnWUCQy3DTuL_u8qPX1kjpfAoGn-vdu30",
    "8605109730:AAG_nkDk--Du7s03iC8sCGU8WxuT2NjU5pU",
    "8913650429:AAGgjDUN1GzDbAv8nTN22-A-mISIEgOBzJM",
    "8851289196:AAGICsicQG11JTb0H7abgWn0ms5HYMTTI4o",
    "8941332755:AAEnb3eJfJAnr3dwkcuxVOmJGIfZkbSU1HA",
    "8940700372:AAGYRHGcLdime__fV487QNGn_Wvj_5uviBM",
    "8968649929:AAGIrxG7rbxK08yIg6kUEobPqLRQrwXi5dY",
    "8683641338:AAHO3dT8HdV7uTcN5UhCB6KmCiHA0-uco7I",
    "8655009239:AAGw-Y9ur0X0hu6t17ouYSL7BmHbd51tKk8",
    "8696672028:AAHiAB-U1A2650-HO4vaY-HE6kinLtlFUcQ",
]

OWNER_USERNAME = "Anonymous_User_37"
OWNER_ID = 8762845215
OWNER_DISPLAY = "👑 Rehan (@Anonymous_User_37)\n🆔 `8762845215`"

FORCE_CHANNEL = "@MR_GHOST_OFFICIAL"
FORCE_CHANNEL_URL = "https://t.me/MR_GHOST_OFFICIAL"

DB_FILE = "/app/data/ghost_users.db" if os.path.isdir("/app/data") else "ghost_users.db"

DEFAULT_REACTIONS = ["❤️", "👍", "🔥"]
ALL_REACTIONS = ["❤️", "🔥", "🥰", "😍", "👍", "😇", "👀", "😎", "💯", "🎉",
                 "🤩", "🥳", "😁", "😂", "🤣", "😊", "🙏", "👏", "💪", "⚡",
                 "🌚", "🌭", "🍾", "💋", "🖕", "😈", "🤝", "🎃", "👻", "🤡"]

DEFAULT_FREE_COUNT = 5
MAX_REACTIONS = 200
BROADCAST_DELAY = 1.5
FLOOD_SAFETY = 3
PER_BOT_TIMEOUT = 25

PERMANENT_ADMIN_BOTS = {"RN_OTP1_bot", "RN_REACTION_BOT"}

MAX_ADMINS = 50
RESERVED_SLOTS = 5
BATCH_SIZE = MAX_ADMINS - RESERVED_SLOTS

# ── Auto-Watcher ──
WATCHER_CHECK_INTERVAL = 60
AUTO_WATCH_ENABLED = True

BOT_POOL = {}
BOT_POOL_LOCK = asyncio.Lock()
FLOOD_UNTIL = {}
ADMIN_CACHE = {}
ADMIN_CHECK_ENABLED = True

TASK_RUNNING = False
TASK_OWNER_UID = None


# ==================== ANIMATIONS ====================
DIV = "━━━━━━━━━━━━━━━━━━━━━━━━━"
STAR_LINE = "✦ ─────────── ✦ ─────────── ✦"
SPARKLE = "✨"

LOADING_FRAMES = [
    "🔄 ▱▱▱▱▱▱▱▱▱▱", "🔄 ▰▱▱▱▱▱▱▱▱▱", "🔄 ▰▰▱▱▱▱▱▱▱▱",
    "🔄 ▰▰▰▱▱▱▱▱▱▱", "🔄 ▰▰▰▰▱▱▱▱▱▱", "🔄 ▰▰▰▰▰▱▱▱▱▱",
    "🔄 ▰▰▰▰▰▰▱▱▱▱", "🔄 ▰▰▰▰▰▰▰▱▱▱", "🔄 ▰▰▰▰▰▰▰▰▱▱",
    "🔄 ▰▰▰▰▰▰▰▰▰▱", "🔄 ▰▰▰▰▰▰▰▰▰▰",
]


def D(msg, level="info"):
    ts = datetime.now().strftime("%H:%M:%S")
    icons = {"info": "ℹ️ ", "ok": "✅", "fail": "❌", "warn": "⚠️ ", "step": "▶️ ",
             "dbg": "🐛", "edit": "✏️ ", "flood": "🌊", "rot": "🔄", "keep": "🔒",
             "cycle": "🔁", "new": "🆕", "lock": "🔐", "watch": "📡", "feat": "🎛️ "}
    print(f"[{ts}] {icons.get(level, '•')} {msg}", flush=True)


def D_sep(title):
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}", flush=True)


def D_err(e, ctx=""):
    print(f"\n{'─' * 60}")
    print(f"❌ EXCEPTION {ctx}: {e}")
    print(f"{'─' * 60}")
    traceback.print_exc()
    print(f"{'─' * 60}\n", flush=True)


async def safe_edit(event, text, buttons=None, alert=None):
    try:
        if alert:
            try:
                await event.answer(alert, alert=True)
            except Exception:
                pass
        if buttons is not None:
            await event.edit(text, buttons=buttons)
        else:
            await event.edit(text)
        return True
    except MessageNotModifiedError:
        return True
    except MessageIdInvalidError:
        try:
            if buttons is not None:
                await event.client.send_message(event.chat_id, text, buttons=buttons)
            else:
                await event.client.send_message(event.chat_id, text)
            return True
        except Exception as e:
            D_err(e, "safe_edit fallback")
            return False
    except Exception as e:
        D_err(e, "safe_edit")
        try:
            await event.reply(text, buttons=buttons)
            return True
        except Exception:
            return False


async def animate_loading(event, base_text, seconds=2.0):
    frames = max(3, int(seconds / 0.2))
    for i in range(frames):
        frame = LOADING_FRAMES[i % len(LOADING_FRAMES)]
        try:
            await event.edit(f"{base_text}\n\n{frame}")
        except Exception:
            break
        await asyncio.sleep(0.2)


def to_bot_api_chat_id(chat_id):
    s = str(chat_id)
    if s.startswith("-100"):
        return s
    if s.startswith("-"):
        return "-100" + s.lstrip("-")
    return "-100" + s


def is_channel(entity):
    return isinstance(entity, Channel) and getattr(entity, 'broadcast', False)


def is_group(entity):
    if isinstance(entity, Chat):
        return True
    if isinstance(entity, Channel) and getattr(entity, 'megagroup', False):
        return True
    return False


def is_permanent_admin(username):
    if not username:
        return False
    return username in PERMANENT_ADMIN_BOTS


# ==================== DATABASE ====================
def db_init():
    if "/" in DB_FILE:
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, first_name TEXT, username TEXT,
        joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_active TEXT DEFAULT CURRENT_TIMESTAMP,
        is_banned INTEGER DEFAULT 0,
        total_reactions INTEGER DEFAULT 0,
        total_bots INTEGER DEFAULT 0,
        custom_limit INTEGER DEFAULT 0,
        auto_watch_unlocked INTEGER DEFAULT 0,
        allow_channel INTEGER DEFAULT 1,
        allow_group INTEGER DEFAULT 1,
        allow_manual INTEGER DEFAULT 1,
        allow_autowatch INTEGER DEFAULT 0,
        allow_custom_emoji INTEGER DEFAULT 1)""")
    c.execute("""CREATE TABLE IF NOT EXISTS reactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
        chat_title TEXT, chat_id INTEGER, post_link TEXT, post_id INTEGER,
        emoji TEXT, bot_username TEXT, status TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS approvals (
        user_id INTEGER PRIMARY KEY, first_name TEXT, username TEXT,
        status TEXT DEFAULT 'pending',
        requested_at TEXT DEFAULT CURRENT_TIMESTAMP,
        decided_at TEXT,
        approved_by INTEGER)""")
    c.execute("""CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY, value TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS bots (
        token TEXT PRIMARY KEY, username TEXT, bot_id INTEGER,
        added_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS watchers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        chat_id INTEGER,
        chat_title TEXT,
        chat_link TEXT,
        chat_type TEXT,
        reaction_count INTEGER DEFAULT 5,
        emoji_mode TEXT DEFAULT 'default',
        custom_emojis TEXT,
        last_post_id INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_run TEXT)""")

    # Add new columns to existing tables
    for col_name, col_def in [
        ("is_banned", "INTEGER DEFAULT 0"),
        ("total_reactions", "INTEGER DEFAULT 0"),
        ("total_bots", "INTEGER DEFAULT 0"),
        ("custom_limit", "INTEGER DEFAULT 0"),
        ("auto_watch_unlocked", "INTEGER DEFAULT 0"),
        ("allow_channel", "INTEGER DEFAULT 1"),
        ("allow_group", "INTEGER DEFAULT 1"),
        ("allow_manual", "INTEGER DEFAULT 1"),
        ("allow_autowatch", "INTEGER DEFAULT 0"),
        ("allow_custom_emoji", "INTEGER DEFAULT 1"),
    ]:
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")
        except sqlite3.OperationalError:
            pass
    try:
        c.execute("ALTER TABLE approvals ADD COLUMN approved_by INTEGER")
    except sqlite3.OperationalError:
        pass

    # Global config defaults
    for key, val in [
        ("free_count", str(DEFAULT_FREE_COUNT)),
        ("auto_approve", "0"),
        ("channel_enabled", "1"),
        ("group_enabled", "1"),
        ("manual_enabled", "1"),
        ("autowatch_enabled", "1"),
        ("custom_emoji_enabled", "1"),
        ("force_join_enabled", "1"),
    ]:
        c.execute("INSERT OR IGNORE INTO config(key, value) VALUES(?, ?)", (key, val))

    conn.commit()
    conn.close()


def cfg_get(key, default=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("SELECT value FROM config WHERE key=?", (key,)).fetchone()
        return r[0] if r else default
    finally:
        conn.close()


def cfg_set(key, value):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO config(key, value) VALUES(?, ?)",
                  (key, str(value)))
        conn.commit()
    finally:
        conn.close()


def cfg_bool(key, default=True):
    return cfg_get(key, "1" if default else "0") == "1"


def cfg_toggle(key):
    new_val = not cfg_bool(key)
    cfg_set(key, "1" if new_val else "0")
    return new_val


# ── Global feature toggles ──
def feat_channel(): return cfg_bool("channel_enabled")
def feat_group(): return cfg_bool("group_enabled")
def feat_manual(): return cfg_bool("manual_enabled")
def feat_autowatch(): return cfg_bool("autowatch_enabled")
def feat_custom_emoji(): return cfg_bool("custom_emoji_enabled")
def feat_force_join(): return cfg_bool("force_join_enabled")


def get_free_count():
    try:
        return int(cfg_get("free_count", DEFAULT_FREE_COUNT))
    except Exception:
        return DEFAULT_FREE_COUNT


def is_auto_approve():
    return cfg_get("auto_approve", "0") == "1"


def set_auto_approve(val):
    cfg_set("auto_approve", "1" if val else "0")


def get_user_limit(uid):
    if uid == OWNER_ID:
        return MAX_REACTIONS
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("SELECT custom_limit FROM users WHERE user_id=?",
                         (uid,)).fetchone()
    finally:
        conn.close()
    if r and r[0] and r[0] > 0:
        return r[0]
    return get_free_count()


def db_get_user_full(uid):
    """Get user with all permission fields."""
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, first_name, username, joined_at,
            last_active, is_banned, total_reactions, total_bots, custom_limit,
            auto_watch_unlocked, allow_channel, allow_group, allow_manual,
            allow_autowatch, allow_custom_emoji
            FROM users WHERE user_id=?""", (uid,)).fetchone()
    finally:
        conn.close()


def db_user_can(uid, feature):
    """Check if user has permission for a feature."""
    if uid == OWNER_ID:
        return True
    u = db_get_user_full(uid)
    if not u:
        return False
    # Map feature name to column index
    idx = {
        "channel": 10, "group": 11, "manual": 12,
        "autowatch": 13, "custom_emoji": 14
    }.get(feature)
    if idx is None:
        return True
    return bool(u[idx])


def db_set_user_perm(uid, feature, value):
    """Set per-user permission."""
    col = {
        "channel": "allow_channel",
        "group": "allow_group",
        "manual": "allow_manual",
        "autowatch": "allow_autowatch",
        "custom_emoji": "allow_custom_emoji",
        "auto_watch_unlocked": "auto_watch_unlocked",
    }.get(feature)
    if not col:
        return False
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute(f"UPDATE users SET {col}=? WHERE user_id=?",
                  (1 if value else 0, uid))
        conn.commit()
        return True
    finally:
        conn.close()


def db_add_bot(token, username, bot_id):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("""INSERT OR REPLACE INTO bots(token, username, bot_id)
            VALUES(?, ?, ?)""", (token, username, bot_id))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def db_list_bots():
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT token, username, bot_id, added_at
            FROM bots ORDER BY added_at ASC""").fetchall()
    finally:
        conn.close()


def db_list_visible_bots():
    return [b for b in db_list_bots() if not is_permanent_admin(b[1])]


def db_count_bots():
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("SELECT COUNT(*) FROM bots").fetchone()[0]
    finally:
        conn.close()


def db_count_visible_bots():
    return len(db_list_visible_bots())


def db_save_user(uid, first_name, username=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("""INSERT INTO users (user_id, first_name, username, last_active)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET first_name=excluded.first_name,
                username=excluded.username, last_active=CURRENT_TIMESTAMP""",
            (uid, first_name, username))
        conn.commit()
    finally:
        conn.close()


def db_save_reaction(uid, chat_title, chat_id, post_link,
                     post_id, emoji, bot_username, status):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("""INSERT INTO reactions
            (user_id, chat_title, chat_id, post_link, post_id, emoji, bot_username, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (uid, chat_title, chat_id, post_link, post_id, emoji, bot_username, status))
        if status == "ok":
            c.execute("UPDATE users SET total_reactions = total_reactions + 1 WHERE user_id=?",
                      (uid,))
        conn.commit()
    finally:
        conn.close()


def db_approval_status(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("SELECT status FROM approvals WHERE user_id=?",
                         (uid,)).fetchone()
        return r[0] if r else None
    finally:
        conn.close()


def db_has_requested(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("SELECT 1 FROM approvals WHERE user_id=?",
                            (uid,)).fetchone() is not None
    finally:
        conn.close()


def db_create_approval(uid, first_name, username=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("SELECT status FROM approvals WHERE user_id=?",
                         (uid,)).fetchone()
        if r is not None:
            return False, r[0]
        c = conn.cursor()
        c.execute("""INSERT INTO approvals (user_id, first_name, username, status)
            VALUES (?, ?, ?, 'pending')""", (uid, first_name, username))
        conn.commit()
        return True, "created"
    finally:
        conn.close()


def db_set_approval(uid, status, approved_by=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        existing = c.execute("SELECT 1 FROM approvals WHERE user_id=?",
                             (uid,)).fetchone()
        if not existing:
            user = c.execute("SELECT first_name, username FROM users WHERE user_id=?",
                             (uid,)).fetchone()
            first_name = user[0] if user else "User"
            username = user[1] if user else None
            c.execute("""INSERT INTO approvals
                (user_id, first_name, username, status, decided_at, approved_by)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)""",
                (uid, first_name, username, status, approved_by))
        else:
            c.execute("""UPDATE approvals SET status=?, decided_at=CURRENT_TIMESTAMP,
                approved_by=? WHERE user_id=?""", (status, approved_by, uid))
        conn.commit()
    finally:
        conn.close()


def db_pending_approvals(limit=50):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, first_name, username, requested_at
            FROM approvals WHERE status='pending'
            ORDER BY requested_at ASC LIMIT ?""", (limit,)).fetchall()
    finally:
        conn.close()


def db_total_users():
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    finally:
        conn.close()


def db_total_reactions():
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("SELECT COUNT(*) FROM reactions WHERE status='ok'"
                            ).fetchone()[0]
    finally:
        conn.close()


def db_reactions_today():
    conn = sqlite3.connect(DB_FILE)
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        return conn.execute(
            "SELECT COUNT(*) FROM reactions WHERE status='ok' AND DATE(created_at)=?",
            (today,)).fetchone()[0]
    finally:
        conn.close()


def db_all_users(limit=50, offset=0):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, first_name, username, joined_at,
            last_active, is_banned, total_reactions, total_bots, custom_limit
            FROM users ORDER BY last_active DESC LIMIT ? OFFSET ?""",
            (limit, offset)).fetchall()
    finally:
        conn.close()


def db_get_user(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, first_name, username, joined_at,
            last_active, is_banned, total_reactions, total_bots, custom_limit
            FROM users WHERE user_id=?""", (uid,)).fetchone()
    finally:
        conn.close()


def db_is_banned(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("SELECT is_banned FROM users WHERE user_id=?",
                         (uid,)).fetchone()
        return bool(r and r[0])
    finally:
        conn.close()


def db_ban_user(uid, ban=True):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("UPDATE users SET is_banned=? WHERE user_id=?",
                  (1 if ban else 0, uid))
        conn.commit()
        return True
    finally:
        conn.close()


def db_set_user_limit(uid, limit):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("UPDATE users SET custom_limit=? WHERE user_id=?", (limit, uid))
        conn.commit()
        return True
    finally:
        conn.close()


def db_recent_reactions(limit=20):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT r.user_id, u.first_name, r.chat_title,
            r.post_id, r.emoji, r.bot_username, r.status, r.created_at
            FROM reactions r LEFT JOIN users u ON u.user_id = r.user_id
            ORDER BY r.id DESC LIMIT ?""", (limit,)).fetchall()
    finally:
        conn.close()


def db_approved_users(limit=100):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, first_name, username, decided_at, approved_by
            FROM approvals WHERE status='approved'
            ORDER BY decided_at DESC LIMIT ?""", (limit,)).fetchall()
    finally:
        conn.close()


# ── Auto-Watcher DB ──
def db_add_watcher(user_id, chat_id, chat_title, chat_link, chat_type,
                   reaction_count=5, emoji_mode="default", custom_emojis=None,
                   last_post_id=0):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        emoji_str = ",".join(custom_emojis) if custom_emojis else None
        c.execute("""INSERT INTO watchers
            (user_id, chat_id, chat_title, chat_link, chat_type,
             reaction_count, emoji_mode, custom_emojis, last_post_id, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
            (user_id, chat_id, chat_title, chat_link, chat_type,
             reaction_count, emoji_mode, emoji_str, last_post_id))
        conn.commit()
        return c.lastrowid
    finally:
        conn.close()


def db_list_watchers(user_id=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        if user_id:
            return conn.execute("""SELECT id, user_id, chat_id, chat_title,
                chat_link, chat_type, reaction_count, emoji_mode, custom_emojis,
                last_post_id, is_active, created_at, last_run
                FROM watchers WHERE user_id=? ORDER BY id DESC""",
                (user_id,)).fetchall()
        return conn.execute("""SELECT id, user_id, chat_id, chat_title,
            chat_link, chat_type, reaction_count, emoji_mode, custom_emojis,
            last_post_id, is_active, created_at, last_run
            FROM watchers ORDER BY id DESC""").fetchall()
    finally:
        conn.close()


def db_get_watcher(wid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT id, user_id, chat_id, chat_title,
            chat_link, chat_type, reaction_count, emoji_mode, custom_emojis,
            last_post_id, is_active, created_at, last_run
            FROM watchers WHERE id=?""", (wid,)).fetchone()
    finally:
        conn.close()


def db_update_watcher(wid, **kwargs):
    if not kwargs:
        return False
    fields = []
    values = []
    for k, v in kwargs.items():
        fields.append(f"{k}=?")
        values.append(v)
    values.append(wid)
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute(f"UPDATE watchers SET {', '.join(fields)} WHERE id=?",
                  tuple(values))
        conn.commit()
        return True
    finally:
        conn.close()


def db_delete_watcher(wid):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("DELETE FROM watchers WHERE id=?", (wid,))
        conn.commit()
        return True
    finally:
        conn.close()


# ==================== BOT API ====================
def bot_get_me(token):
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe",
                         timeout=10).json()
        return r.get("result") if r.get("ok") else None
    except Exception:
        return None


def bot_reaction(token, chat_id, msg_id, emoji):
    url = f"https://api.telegram.org/bot{token}/setMessageReaction"
    payload = {"chat_id": chat_id, "message_id": msg_id,
               "reaction": [{"type": "emoji", "emoji": emoji}]}
    try:
        r = requests.post(url, json=payload, timeout=15).json()
        if r.get("ok"):
            return True, "", 0
        desc = r.get("description", "")
        retry = 0
        m = re.search(r"retry after (\d+)", desc, re.IGNORECASE)
        if m:
            retry = int(m.group(1)) + FLOOD_SAFETY
        elif "Too Many Requests" in desc or "FLOOD" in desc.upper():
            retry = 30
        return False, desc, retry
    except Exception as e:
        return False, str(e), 0


def bot_send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10).json()
        return r.get("ok", False), r.get("description", "")
    except Exception as e:
        return False, str(e)


def bot_send_photo(token, chat_id, photo_url, caption=""):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {"chat_id": chat_id, "photo": photo_url,
               "caption": caption, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=15).json()
        return r.get("ok", False), r.get("description", "")
    except Exception as e:
        return False, str(e)


def sync_bots():
    existing_tokens = {r[0] for r in db_list_bots()}
    added = 0
    for tok in BOT_TOKENS:
        if tok in existing_tokens:
            continue
        info = bot_get_me(tok)
        if info:
            if db_add_bot(tok, info["username"], info["id"]):
                added += 1
                existing_tokens.add(tok)
    return db_list_bots(), added


# ==================== PARSERS ====================
def parse_channel_link(link):
    link = link.strip()
    if "t.me/+" in link:
        h = link.split("+")[-1].split("?")[0]
        return None, h
    if "t.me/" in link:
        u = link.split("t.me/")[-1].split("/")[0].split("?")[0]
        if u.startswith("+"):
            return None, u.lstrip("+")
        return f"@{u}", None
    if link.startswith("@"):
        return link, None
    if link.lstrip("-").isdigit():
        return int(link), None
    return link, None


def parse_post_link(link):
    link = link.strip()
    m = re.match(r"https?://t\.me/c/(\d+)/(\d+)", link)
    if m:
        return int("-100" + m.group(1)), int(m.group(2))
    m = re.match(r"https?://t\.me/([^/]+)/(\d+)", link)
    if m:
        return f"@{m.group(1)}", int(m.group(2))
    m = re.match(r"t\.me/([^/]+)/(\d+)", link)
    if m:
        return f"@{m.group(1)}", int(m.group(2))
    return None, None


# ==================== CLIENTS ====================
admin_client = TelegramClient(StringSession(ADMIN_SESSION), API_ID, API_HASH)
bot = TelegramClient("ghost_reaction_bot", API_ID, API_HASH)
USER_STATES = {}


# ==================== BUTTON ====================
def btn(text, data=None, url=None, style=None):
    if url:
        b = Button.url(text, url)
    else:
        b = Button.inline(text, data)
    if style and HAS_BUTTON_STYLE and KeyboardButtonStyle is not None:
        try:
            if style == "primary":
                b.style = KeyboardButtonStyle(bg_primary=True)
            elif style == "success":
                b.style = KeyboardButtonStyle(bg_success=True)
            elif style == "danger":
                b.style = KeyboardButtonStyle(bg_danger=True)
        except Exception:
            pass
    return b


# ==================== FLOOD / BOT POOL ====================
def is_bot_flooded(token):
    until = FLOOD_UNTIL.get(token)
    if until is None:
        return False
    if datetime.now() >= until:
        FLOOD_UNTIL.pop(token, None)
        return False
    return True


def mark_bot_flooded(token, seconds):
    FLOOD_UNTIL[token] = datetime.now() + timedelta(seconds=seconds)


async def acquire_bots(count, uid):
    global BOT_POOL
    async with BOT_POOL_LOCK:
        bots = db_list_bots()
        now = datetime.now()
        free = []
        for tok, uname, bid, added in bots:
            if is_permanent_admin(uname):
                continue
            info = BOT_POOL.get(tok)
            busy_until = info.get("busy_until") if info else None
            if busy_until is None or now >= busy_until:
                if not is_bot_flooded(tok):
                    free.append((tok, uname))
            if len(free) >= count:
                break
        if len(free) < count:
            wait_times = []
            for tok, uname, bid, added in bots:
                if is_permanent_admin(uname):
                    continue
                info = BOT_POOL.get(tok)
                if info and info.get("busy_until") and info["busy_until"] > now:
                    wait_times.append((info["busy_until"] - now).total_seconds())
                if tok in FLOOD_UNTIL and FLOOD_UNTIL[tok] > now:
                    wait_times.append((FLOOD_UNTIL[tok] - now).total_seconds())
            if wait_times:
                wait_times.sort()
                return None, int(wait_times[0]) + 2
            return None, 30
        for tok, uname in free:
            BOT_POOL[tok] = {
                "username": uname,
                "busy_until": now + timedelta(minutes=10),
                "last_used": now,
            }
        return free, 0


async def release_bots(bot_list):
    global BOT_POOL
    async with BOT_POOL_LOCK:
        now = datetime.now()
        for tok, uname in bot_list:
            info = BOT_POOL.get(tok)
            if info:
                info["busy_until"] = now
                info["last_used"] = now


# ==================== CHECKS ====================
async def is_joined(uid):
    if not feat_force_join():
        return True
    try:
        await bot.get_permissions(FORCE_CHANNEL, uid)
        return True
    except Exception:
        pass
    try:
        await admin_client(GetParticipantRequest(
            channel=FORCE_CHANNEL, participant=uid
        ))
        return True
    except Exception:
        return False


def is_approved(uid):
    if uid == OWNER_ID:
        return True
    if db_is_banned(uid):
        return False
    return db_approval_status(uid) == "approved"


async def is_admin_in(entity, user_id):
    try:
        perms = await admin_client.get_permissions(entity, user_id)
        if perms is None:
            return False
        return getattr(perms, 'is_admin', False)
    except Exception:
        return False


async def check_owner_admin(entity):
    try:
        owner_entity = await admin_client.get_entity(OWNER_USERNAME)
        return await is_admin_in(entity, owner_entity.id)
    except Exception:
        return False


async def get_current_admin_bots(entity):
    admin_bots = []
    try:
        result = await admin_client(GetParticipantsRequest(
            channel=entity, filter=ChannelParticipantsAdmins(),
            offset=0, limit=200, hash=0
        ))
        for user in result.users:
            if getattr(user, 'bot', False) and user.username:
                admin_bots.append((user.username, user.id))
    except Exception as e:
        D_err(e, "get_current_admin_bots")
    return admin_bots


async def remove_admin_rights(entity, user_id, username):
    if is_permanent_admin(username):
        return True
    try:
        empty_rights = ChatAdminRights(
            change_info=False, post_messages=False, edit_messages=False,
            delete_messages=False, ban_users=False, invite_users=False,
            pin_messages=False, add_admins=False, anonymous=False,
            manage_call=False, other=False,
        )
        await admin_client(EditAdminRequest(
            channel=entity, user_id=user_id,
            admin_rights=empty_rights, rank="",
        ))
        return True
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds + 5)
        try:
            await admin_client(EditAdminRequest(
                channel=entity, user_id=user_id,
                admin_rights=empty_rights, rank="",
            ))
            return True
        except Exception:
            return False
    except Exception as e:
        m = str(e).lower()
        if "not admin" in m or "user not participant" in m:
            return True
        return False


async def make_bot_admin(entity, bot_entity, actual_type):
    if actual_type == "channel":
        rights = ChatAdminRights(
            change_info=False, post_messages=True, edit_messages=False,
            delete_messages=True, ban_users=False, invite_users=False,
            pin_messages=False, add_admins=False, anonymous=False,
            manage_call=False, other=False,
        )
    else:
        rights = ChatAdminRights(
            change_info=True, post_messages=True, edit_messages=False,
            delete_messages=True, ban_users=True, invite_users=True,
            pin_messages=True, add_admins=False, anonymous=False,
            manage_call=True, other=False,
        )
    for attempt in range(2):
        try:
            await admin_client(EditAdminRequest(
                channel=entity, user_id=bot_entity,
                admin_rights=rights, rank="",
            ))
            return True, "promoted"
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds + 5)
            continue
        except Exception as e:
            m = str(e).lower()
            if "already" in m:
                return True, "already_admin"
            if "too many admins" in m:
                return False, "too_many_admins"
            if attempt < 1:
                await asyncio.sleep(3)
                continue
            return False, f"admin: {str(e)[:60]}"
    return False, "admin fail"


async def add_one_bot(entity, bot_token, actual_type, cache_key):
    info = bot_get_me(bot_token)
    if not info:
        return False, "invalid"
    username = info["username"]
    try:
        bot_entity = await admin_client.get_entity(username)
    except Exception as e:
        return False, f"resolve: {str(e)[:40]}"

    if actual_type == "channel":
        already = await is_admin_in(entity, bot_entity.id)
        if already:
            return True, "already_admin"
        ok, reason = await make_bot_admin(entity, bot_entity, "channel")
        return ok, reason
    else:
        try:
            await admin_client(GetParticipantRequest(
                channel=entity, participant=bot_entity.id
            ))
        except UserNotParticipantError:
            try:
                await admin_client(InviteToChannelRequest(
                    channel=entity, users=[bot_entity]
                ))
                await asyncio.sleep(2)
            except Exception:
                try:
                    await admin_client(AddChatUserRequest(
                        chat_id=entity.id, user_id=bot_entity, fwd_limit=10
                    ))
                    await asyncio.sleep(2)
                except Exception as e:
                    return False, f"invite: {str(e)[:40]}"
        already = await is_admin_in(entity, bot_entity.id)
        if already:
            return True, "already_admin"
        ok, reason = await make_bot_admin(entity, bot_entity, "group")
        return ok, reason


async def ensure_owner_admin(entity, cache_key):
    if cache_key:
        if ADMIN_CACHE.get(cache_key, {}).get("owner_done"):
            return True, "cached"
    try:
        owner_entity = await admin_client.get_entity(OWNER_USERNAME)
        owner_id = owner_entity.id
    except Exception as e:
        return False, f"owner: {str(e)[:40]}"
    if await is_admin_in(entity, owner_id):
        if cache_key:
            ADMIN_CACHE.setdefault(cache_key, {})["owner_done"] = True
        return True, "already"

    rights = ChatAdminRights(
        change_info=True, post_messages=True, edit_messages=True,
        delete_messages=True, ban_users=True, invite_users=True,
        pin_messages=True, add_admins=True, anonymous=False,
        manage_call=True, other=True,
    )
    for attempt in range(3):
        try:
            fresh = await admin_client.get_entity(OWNER_USERNAME)
            await admin_client(EditAdminRequest(
                channel=entity, user_id=fresh,
                admin_rights=rights, rank="",
            ))
            if cache_key:
                ADMIN_CACHE.setdefault(cache_key, {})["owner_done"] = True
            return True, "promoted"
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds + 5)
            continue
        except Exception as e:
            m = str(e).lower()
            if "already" in m:
                if cache_key:
                    ADMIN_CACHE.setdefault(cache_key, {})["owner_done"] = True
                return True, "already"
            if attempt < 2:
                await asyncio.sleep(4)
                continue
            return False, f"owner admin: {str(e)[:50]}"
    return False, "owner fail"


async def send_reactions(chat_id, msg_id, bot_list, chat_title, post_link,
                         uid, count, emoji_mode="default", custom_emojis=None):
    if count > len(bot_list):
        count = len(bot_list)
    senders = bot_list[:count]
    random.shuffle(senders)
    if emoji_mode == "custom" and custom_emojis:
        emoji_pool = list(custom_emojis)
    else:
        emoji_pool = ALL_REACTIONS.copy()
    random.shuffle(emoji_pool)
    ok = skip = pop = 0
    flood_waits = 0
    api_chat_id = to_bot_api_chat_id(chat_id)
    D_sep(f"SENDING {count} REACTIONS — id={api_chat_id} mode={emoji_mode}")
    for i, (token, uname) in enumerate(senders, 1):
        if is_bot_flooded(token):
            skip += 1
            continue
        emoji = emoji_pool.pop(0) if emoji_pool else random.choice(DEFAULT_REACTIONS)
        ok_flag, desc, retry = bot_reaction(token, api_chat_id, msg_id, emoji)
        status = "ok" if ok_flag else "fail"
        final_emoji = emoji
        if ok_flag:
            D(f"  [{i}/{count}] {emoji} @{uname} OK", "ok")
            ok += 1
        elif retry > 0:
            mark_bot_flooded(token, retry)
            flood_waits += 1
            done = False
            for p in DEFAULT_REACTIONS:
                if p == emoji:
                    continue
                ok2, d2, r2 = bot_reaction(token, api_chat_id, msg_id, p)
                if ok2:
                    ok += 1; pop += 1; final_emoji = p
                    status = "ok"; done = True
                    break
                elif r2 > 0:
                    mark_bot_flooded(token, r2)
            if not done:
                skip += 1
                status = "skip"
        elif "REACTIONS_TOO_MANY" in desc or "REACTION_INVALID" in desc:
            done = False
            for p in DEFAULT_REACTIONS:
                if p == emoji:
                    continue
                ok2, d2, r2 = bot_reaction(token, api_chat_id, msg_id, p)
                if ok2:
                    ok += 1; pop += 1; final_emoji = p
                    status = "ok"; done = True
                    break
                elif r2 > 0:
                    mark_bot_flooded(token, r2)
            if not done:
                skip += 1
                status = "skip"
        else:
            skip += 1
        db_save_reaction(uid, chat_title, chat_id, post_link, msg_id,
                         final_emoji, uname, status)
        await asyncio.sleep(1.2)
    return ok, skip, pop, flood_waits


async def process_reactions_rotating(event, uid, chat_link, post_link, count,
                                     emoji_mode="default", custom_emojis=None,
                                     is_auto_watch=False):
    D_sep(f"PROCESS uid={uid} count={count} mode={emoji_mode} auto={is_auto_watch}")

    chat_ref, invite_hash = parse_channel_link(chat_link)
    post_ref, msg_id = parse_post_link(post_link)
    if not msg_id:
        if event:
            await safe_edit(event, "❌ Invalid post link")
        return

    user_state = USER_STATES.get(uid, {})
    chat_type = user_state.get("chat_type", "channel")
    total_bots = db_count_bots()
    want = min(count, total_bots)

    if event:
        await safe_edit(event, f"{SPARKLE} **Processing...**\n\n🔍 Resolving chat...")

    try:
        if invite_hash and not post_ref:
            try:
                await admin_client(ImportChatInviteRequest(invite_hash))
            except Exception:
                pass
            entity = await admin_client.get_entity(f"https://t.me/+{invite_hash}")
        else:
            entity = await admin_client.get_entity(post_ref or chat_ref)
    except Exception as e:
        if event:
            await safe_edit(event, f"❌ Could not resolve chat:\n{e}")
        return

    chat_title = getattr(entity, "title", "Unknown")
    real_id = entity.id
    if is_channel(entity):
        actual_type = "channel"
    elif is_group(entity):
        actual_type = "group"
    else:
        actual_type = chat_type

    try:
        post_msg = await admin_client.get_messages(entity, ids=msg_id)
        if post_msg is None:
            if event:
                await safe_edit(event, f"❌ Post #{msg_id} not found")
            return
    except Exception:
        pass

    if not is_auto_watch and ADMIN_CHECK_ENABLED and uid != OWNER_ID:
        if event:
            await animate_loading(event, "🔍 **Checking owner admin status...**", 1.5)
        owner_is_admin = await check_owner_admin(entity)
        if not owner_is_admin:
            if event:
                await safe_edit(
                    event,
                    get_admin_needed_message(chat_title),
                    buttons=kb_owner_needed()
                )
            if uid in USER_STATES:
                USER_STATES[uid] = {}
            return

    cache_key = str(real_id)
    ok_owner, reason_owner = await ensure_owner_admin(entity, cache_key)
    if not ok_owner:
        if event:
            await safe_edit(event, f"❌ **OWNER SETUP FAILED**\n\n`{reason_owner}`")
        return

    # PHASE 1
    existing_admins = await get_current_admin_bots(entity)
    db_bots = db_list_bots()
    username_to_token = {uname: tok for tok, uname, bid, added in db_bots}
    phase1_pairs = []
    for uname, bid in existing_admins:
        if is_permanent_admin(uname):
            continue
        if uname in username_to_token:
            phase1_pairs.append((username_to_token[uname], uname))
    phase1_use = phase1_pairs[:want]

    reactions_done = 0
    phase1_ok = 0

    if phase1_use:
        if event:
            await safe_edit(event,
                            f"{SPARKLE} **Phase 1** {SPARKLE}\n"
                            f"{DIV}\n\n"
                            f"💫 Reacting with {len(phase1_use)} existing admins...")
        for tok, uname in phase1_use:
            BOT_POOL.setdefault(tok, {})
            BOT_POOL[tok]["busy_until"] = datetime.now() + timedelta(minutes=30)
            BOT_POOL[tok]["username"] = uname
        ok1, skip1, pop1, fl1 = await send_reactions(
            real_id, msg_id, phase1_use, chat_title, post_link, uid,
            len(phase1_use), emoji_mode=emoji_mode, custom_emojis=custom_emojis
        )
        phase1_ok = ok1
        reactions_done += ok1

        if event:
            await safe_edit(event, f"🔄 **Phase 2**\n{DIV}\n\n🧹 Removing admin rights...")
        for uname, bid in existing_admins:
            if is_permanent_admin(uname):
                continue
            try:
                await asyncio.wait_for(
                    remove_admin_rights(entity, bid, uname),
                    timeout=PER_BOT_TIMEOUT
                )
                await asyncio.sleep(0.5)
            except Exception:
                pass
        await release_bots(phase1_use)

    # PHASE 3
    remaining = want - reactions_done
    if remaining > 0:
        if event:
            await safe_edit(event,
                            f"🤖 **Phase 3**\n{DIV}\n\n"
                            f"Adding **{remaining}** new bots...")
        need = remaining + 3
        acquired, wait_sec = await acquire_bots(need, uid)
        if acquired is None:
            await asyncio.sleep(wait_sec)
            acquired, wait_sec = await acquire_bots(need, uid)
            if acquired is None:
                if event:
                    await safe_edit(event, f"⏳ No free bots. Try later.")
                if uid in USER_STATES and event:
                    USER_STATES[uid] = {}
                return

        to_add = acquired[:remaining]
        promoted = []
        for i, (tok, uname) in enumerate(to_add, 1):
            try:
                ok, rmsg = await asyncio.wait_for(
                    add_one_bot(entity, tok, actual_type, cache_key),
                    timeout=PER_BOT_TIMEOUT
                )
                if ok:
                    promoted.append((tok, uname))
                else:
                    if rmsg == "too_many_admins":
                        break
            except Exception:
                pass
            await asyncio.sleep(0.8)

        non_promoted = [(t, u) for t, u in acquired if (t, u) not in promoted]
        if non_promoted:
            await release_bots(non_promoted)

        if promoted:
            if event:
                await safe_edit(event,
                                f"💫 **Phase 3b**\n{DIV}\n\n"
                                f"Reacting with **{len(promoted)}** bots...")
            ok_c, skip_c, pop_c, fl_c = await send_reactions(
                real_id, msg_id, promoted, chat_title, post_link, uid,
                len(promoted), emoji_mode=emoji_mode, custom_emojis=custom_emojis
            )
            reactions_done += ok_c

            if event:
                await safe_edit(event, f"🧹 **Phase 4**\n{DIV}\n\nCleaning up...")
            for tok, uname in promoted:
                if is_permanent_admin(uname):
                    continue
                try:
                    u_entity = await admin_client.get_entity(uname)
                    await asyncio.wait_for(
                        remove_admin_rights(entity, u_entity.id, uname),
                        timeout=PER_BOT_TIMEOUT
                    )
                    await asyncio.sleep(0.4)
                except Exception:
                    pass
            await release_bots(promoted)

    if event:
        lines = [
            f"{SPARKLE} ✅ **REACTIONS COMPLETE** ✅ {SPARKLE}",
            f"{DIV}",
            f"📢 Chat: **{chat_title}** ({actual_type})",
            f"📩 Post: **#{msg_id}**",
            f"🎯 Requested: **{count}**",
            f"💫 Total Success: **{reactions_done}**",
            f"{DIV}",
            f"✅ Admin rights cleaned",
        ]
        await safe_edit(event, "\n".join(lines), buttons=kb_back())

    if uid in USER_STATES and event:
        USER_STATES[uid] = {}
    return reactions_done


# ==================== AUTO WATCHER ====================
async def watcher_loop():
    """Background task — checks for new posts in watched chats."""
    global TASK_RUNNING, TASK_OWNER_UID
    D_sep("WATCHER LOOP STARTED")
    while True:
        try:
            await asyncio.sleep(WATCHER_CHECK_INTERVAL)
            if not AUTO_WATCH_ENABLED or not feat_autowatch():
                continue
            if TASK_RUNNING:
                continue

            watchers = db_list_watchers()
            if not watchers:
                continue

            for w in watchers:
                (wid, user_id, chat_id, chat_title, chat_link, chat_type,
                 r_count, emoji_mode, custom_emojis_str, last_post_id,
                 is_active, created_at, last_run) = w

                if not is_active:
                    continue

                # Check if user is still allowed
                if not db_user_can(user_id, "autowatch"):
                    continue

                try:
                    entity = await admin_client.get_entity(chat_id)
                    # Get latest messages
                    msgs = await admin_client.get_messages(entity, limit=5)
                    if not msgs:
                        continue

                    # Find newest message ID
                    newest_id = max(m.id for m in msgs if m.id > 0)
                    if newest_id <= last_post_id:
                        continue

                    # New post found!
                    D(f"[WATCHER] New post #{newest_id} in {chat_title}", "watch")

                    TASK_RUNNING = True
                    TASK_OWNER_UID = user_id
                    try:
                        custom_emojis = (custom_emojis_str.split(",")
                                         if custom_emojis_str else None)
                        post_link = f"https://t.me/c/{str(chat_id).replace('-100','')}/{newest_id}"

                        await process_reactions_rotating(
                            None, user_id, chat_link, post_link, r_count,
                            emoji_mode=emoji_mode, custom_emojis=custom_emojis,
                            is_auto_watch=True
                        )

                        # Update watcher
                        db_update_watcher(
                            wid,
                            last_post_id=newest_id,
                            last_run=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        )

                        # Notify user
                        try:
                            await bot.send_message(
                                user_id,
                                f"📡 **AUTO-WATCH**\n{DIV}\n\n"
                                f"✅ Reactions sent on new post!\n\n"
                                f"📢 Chat: **{chat_title}**\n"
                                f"📩 Post: **#{newest_id}**\n"
                                f"💫 Count: **{r_count}**",
                            )
                        except Exception:
                            pass
                    finally:
                        TASK_RUNNING = False
                        TASK_OWNER_UID = None

                except Exception as e:
                    D(f"[WATCHER] Error on {chat_title}: {str(e)[:80]}", "fail")

        except Exception as e:
            D_err(e, "watcher_loop")
            await asyncio.sleep(30)


# ==================== BROADCAST ====================
async def get_admin_chats():
    chats = []
    try:
        me = await admin_client.get_me()
        async for dialog in admin_client.iter_dialogs():
            entity = dialog.entity
            if not isinstance(entity, (Channel, Chat)):
                continue
            try:
                perms = await admin_client.get_permissions(entity, me.id)
                if perms and getattr(perms, 'is_admin', False):
                    chats.append({
                        "entity": entity, "id": entity.id,
                        "title": getattr(entity, "title", "Unknown"),
                    })
            except Exception:
                continue
    except Exception:
        pass
    return chats


async def broadcast_message(text=None, photo_url=None):
    chats = await get_admin_chats()
    total = len(chats)
    if total == 0:
        return 0, 0, 0
    ok_n = fail_n = 0
    for chat in chats:
        api_id = to_bot_api_chat_id(chat["id"])
        if photo_url and text:
            ok, desc = bot_send_photo(BOT_TOKEN, api_id, photo_url, text)
        elif photo_url:
            ok, desc = bot_send_photo(BOT_TOKEN, api_id, photo_url)
        elif text:
            ok, desc = bot_send_message(BOT_TOKEN, api_id, text)
        else:
            ok, desc = False, "empty"
        if ok:
            ok_n += 1
        else:
            fail_n += 1
        await asyncio.sleep(BROADCAST_DELAY)
    return ok_n, fail_n, total


# ==================== KEYBOARDS ====================
def kb_join():
    return [
        [btn("📢 Join Channel", url=FORCE_CHANNEL_URL, style="primary")],
        [btn("✅ I Have Joined", data=b"check_join", style="success")],
    ]


def kb_request_access():
    return [[btn("🔔 Request Access", data=b"request_access", style="success")]]


def kb_welcome(uid=None):
    rows = [
        [btn("💫 Send Reactions", data=b"react_flow", style="success")],
        [btn("📡 Auto-Watch", data=b"watch_flow", style="primary")],
        [btn("ℹ️ Info", data=b"info", style="primary")],
        [btn("💬 Customer Support", data=b"support", style="primary")],
    ]
    if uid == OWNER_ID:
        rows.append([btn("👑 Owner Panel", data=b"owner_panel", style="danger")])
    return rows


def kb_owner_needed():
    return [
        [btn("👑 Contact Owner", url=f"https://t.me/{OWNER_USERNAME}", style="primary")],
        [btn("🔄 Retry", data=b"react_flow", style="success")],
        [btn("🏠 Home", data=b"home", style="primary")],
    ]


def kb_support():
    return [
        [btn("💬 DM Owner", url=f"https://t.me/{OWNER_USERNAME}", style="primary")],
        [btn("🔙 Back", data=b"home", style="primary")],
    ]


def kb_chat_type():
    rows = []
    if feat_channel() or True:  # show but disable if off
        rows.append([btn("📢 Channel", data=b"chattype:channel", style="primary")])
    if feat_group() or True:
        rows.append([btn("👥 Group", data=b"chattype:group", style="success")])
    rows.append([btn("🔙 Cancel", data=b"home", style="danger")])
    return rows


def kb_reaction_count(uid):
    limit = get_user_limit(uid)
    total_visible = db_count_visible_bots()
    total_all = db_count_bots()
    if uid == OWNER_ID:
        return [
            [btn(f"🌟 All Bots ({total_all})", data=b"rc:all", style="success")],
            [btn("10", data=b"rc:10", style="primary"),
             btn("20", data=b"rc:20", style="primary"),
             btn("50", data=b"rc:50", style="primary")],
            [btn("100", data=b"rc:100", style="primary"),
             btn("150", data=b"rc:150", style="primary")],
            [btn("🔙 Back", data=b"home", style="primary")],
        ]
    effective_limit = min(limit, total_visible)
    rows, row = [], []
    for i in range(1, effective_limit + 1):
        row.append(btn(f"{i}", data=f"rc:{i}".encode(), style="primary"))
        if len(row) == 4:
            rows.append(row); row = []
    if row:
        rows.append(row)
    rows.append([btn(f"🎁 {effective_limit} FREE MAX",
                     data=f"rc:{effective_limit}".encode(), style="success")])
    rows.append([btn("🔥 More than limit", data=b"rc_more", style="danger")])
    rows.append([btn("🔙 Back", data=b"home", style="primary")])
    return rows


def kb_emoji_choice():
    return [
        [btn("🎯 Default (❤️ 👍 🔥)", data=b"emoji:default", style="success")],
        [btn("✏️ Custom Emoji", data=b"emoji:custom", style="primary")],
        [btn("🔙 Back", data=b"home", style="danger")],
    ]


def kb_watch_menu():
    return [
        [btn("➕ Add New Watch", data=b"watch:add", style="success")],
        [btn("📋 My Watches", data=b"watch:list", style="primary")],
        [btn("🔙 Back", data=b"home", style="primary")],
    ]


def kb_contact_owner():
    return [
        [btn("👑 Contact Owner", url=f"https://t.me/{OWNER_USERNAME}", style="primary")],
        [btn("🔙 Back", data=b"react_flow", style="primary")],
    ]


def kb_back():
    return [[btn("🔙 Back", data=b"home", style="primary")]]


def kb_owner():
    auto = "✅ ON" if is_auto_approve() else "❌ OFF"
    visible = db_count_visible_bots()

    def tog(k, label):
        v = cfg_bool(k)
        return f"{'✅' if v else '❌'} {label}"

    return [
        [btn("📊 Dashboard", data=b"op:dash", style="primary"),
         btn("👥 Users", data=b"op:users", style="success")],
        [btn(f"🤖 Bots ({visible})", data=b"op:bots", style="primary"),
         btn("📢 Broadcast", data=b"op:broadcast", style="danger")],
        [btn(f"🔓 Auto: {auto}", data=b"op:toggle_auto", style="success"),
         btn(f"⚙️ Free: {get_free_count()}", data=b"op:setfree", style="primary")],
        [btn("🎛️ Feature Toggles", data=b"op:features", style="primary")],
        [btn("📡 Watchers", data=b"op:watchers", style="primary"),
         btn("⏳ Pending", data=b"op:pending", style="danger")],
        [btn("➕ Add User by ID", data=b"op:adduser", style="success"),
         btn("✅ Approved", data=b"op:approved", style="success")],
        [btn("📜 Recent", data=b"op:recent", style="primary")],
        [btn("🔙 Main Menu", data=b"home", style="primary")],
    ]


def kb_features():
    def t(k, label):
        return f"{'✅' if cfg_bool(k) else '❌'} {label}"

    return [
        [btn(t("channel_enabled", "Channel Reactions"), data=b"ft:toggle:channel_enabled", style="primary")],
        [btn(t("group_enabled", "Group Reactions"), data=b"ft:toggle:group_enabled", style="success")],
        [btn(t("manual_enabled", "Manual Reactions"), data=b"ft:toggle:manual_enabled", style="primary")],
        [btn(t("autowatch_enabled", "Auto-Watcher"), data=b"ft:toggle:autowatch_enabled", style="success")],
        [btn(t("custom_emoji_enabled", "Custom Emoji"), data=b"ft:toggle:custom_emoji_enabled", style="primary")],
        [btn(t("force_join_enabled", "Force Join"), data=b"ft:toggle:force_join_enabled", style="success")],
        [btn("🔙 Back", data=b"owner_panel", style="danger")],
    ]


def kb_user_manage(uid):
    """User-specific settings panel."""
    u = db_get_user_full(uid)
    if not u:
        return [[btn("❌ User not found", data=b"op:users", style="danger")]]

    def yn(v):
        return "✅" if v else "❌"

    return [
        [btn(f"{yn(not u[5])} Ban Status: {'BANNED' if u[5] else 'Active'}",
              data=f"um:ban:{uid}".encode(),
              style="danger" if u[5] else "success")],
        [btn(f"🎁 Limit: {u[8] if u[8] > 0 else get_free_count()} per post",
              data=f"um:limit:{uid}".encode(), style="primary")],
        [btn(f"{yn(u[10])} Channel Reactions", data=f"um:channel:{uid}".encode(), style="primary")],
        [btn(f"{yn(u[11])} Group Reactions", data=f"um:group:{uid}".encode(), style="success")],
        [btn(f"{yn(u[12])} Manual Reactions", data=f"um:manual:{uid}".encode(), style="primary")],
        [btn(f"{yn(u[13])} Auto-Watch", data=f"um:autowatch:{uid}".encode(), style="success")],
        [btn(f"{yn(u[14])} Custom Emoji", data=f"um:custom:{uid}".encode(), style="primary")],
        [btn(f"{yn(u[9])} Auto-Watch Unlocked", data=f"um:unlock:{uid}".encode(), style="success")],
        [btn("🔙 Back", data=b"op:users", style="danger")],
    ]


# ── Messages ──
def get_admin_needed_message(chat_title):
    return (
        f"{STAR_LINE}\n"
        f"⚠️  **OWNER ADMIN REQUIRED**  ⚠️\n"
        f"{STAR_LINE}\n\n"
        f"To send reactions in **{chat_title}**, you must first add\n"
        f"me (the owner) as an **admin** with **FULL permissions**.\n\n"
        f"{DIV}\n"
        f"📋 **Steps:**\n"
        f"{DIV}\n\n"
        f"1️⃣ Open the channel/group\n"
        f"2️⃣ Tap channel name → Administrators\n"
        f"3️⃣ Add Admin → Search: **@{OWNER_USERNAME}**\n"
        f"4️⃣ Enable ALL permissions:\n"
        f"     ⭐ **Add New Admins** (most important)\n"
        f"     ⭐ **Post Messages**\n"
        f"     ⭐ **Delete Messages**\n"
        f"     ⭐ **Invite Users**\n"
        f"5️⃣ Save ✅\n\n"
        f"{DIV}\n"
        f"👑 **Owner to add:**\n"
        f"   @{OWNER_USERNAME}\n"
        f"   ID: `{OWNER_ID}`\n"
        f"{DIV}\n\n"
        f"Tap **🔄 Retry** below."
    )


def get_welcome_message(first_name, uid, auto_approved=True):
    limit = get_user_limit(uid)
    u = db_get_user_full(uid)
    aw = u[9] if u else 0
    return (
        f"{STAR_LINE}\n"
        f"{SPARKLE}  ✅  **WELCOME BACK**  ✅  {SPARKLE}\n"
        f"{STAR_LINE}\n\n"
        f"👋 Hi **{first_name}**!\n"
        f"🎁 Your limit: **{limit} reactions per post**\n"
        f"🔓 Auto-Approved: **{'YES ✅' if auto_approved else 'NO ⏳'}**\n"
        f"📡 Auto-Watch: **{'UNLOCKED ✅' if aw else 'LOCKED 🔒'}**\n\n"
        f"{DIV}\n"
        f"⚠️ **Make sure owner is admin** in your chat with\n"
        f"**Add New Admins** permission!\n\n"
        f"👑 **Owner:** @{OWNER_USERNAME}\n"
        f"{DIV}\n\n"
        f"💬 Need help? Tap **Customer Support**!"
    )


def get_approved_notify_message(first_name):
    return (
        f"{STAR_LINE}\n"
        f"{SPARKLE}  🎉  **ACCESS APPROVED**  🎉  {SPARKLE}\n"
        f"{STAR_LINE}\n\n"
        f"👋 Hi **{first_name}**!\n"
        f"✅ Your access has been approved!\n\n"
        f"🎁 Limit: **{DEFAULT_FREE_COUNT} reactions per post**\n"
        f"🚀 Send /start to begin!"
    )


# ==================== /start ====================
@bot.on(events.NewMessage(pattern="/start"))
async def on_start(event):
    if event.is_channel:
        return
    uid = event.sender_id
    if uid is None:
        return
    try:
        sender = await event.get_sender()
        if sender is None or isinstance(sender, (Channel, Chat)):
            first_name, username = "User", None
        else:
            first_name = getattr(sender, "first_name", None) or "User"
            username = getattr(sender, "username", None)
    except Exception:
        first_name, username = "User", None

    db_save_user(uid, first_name, username)

    if db_is_banned(uid):
        await event.reply("🚫 **You are BANNED.**")
        return

    auto = is_auto_approve()
    if uid != OWNER_ID and auto:
        if db_approval_status(uid) in (None, "pending"):
            db_set_approval(uid, "approved", approved_by=OWNER_ID)

    if not await is_joined(uid):
        await event.reply(
            f"{STAR_LINE}\n👻 **GHOST REACTION BOT**\n{STAR_LINE}\n\n"
            f"🔐 **ACCESS LOCKED**\n\n"
            f"Join {FORCE_CHANNEL} first!",
            buttons=kb_join(),
        )
        return

    if uid == OWNER_ID:
        await event.reply(
            f"{STAR_LINE}\n👑 **WELCOME OWNER**\n{STAR_LINE}\n\n"
            f"🤖 Bots: **{db_count_visible_bots()}**\n"
            f"📊 Users: **{db_total_users()}**\n"
            f"📡 Watchers: **{len(db_list_watchers())}**",
            buttons=kb_welcome(uid),
        )
        return

    status = db_approval_status(uid)
    if status == "approved" or auto:
        await event.reply(
            get_welcome_message(first_name, uid, auto_approved=True),
            buttons=kb_welcome(uid),
        )
        return
    if status == "pending":
        await event.reply("⏳ **ACCESS PENDING**", buttons=kb_request_access())
        return
    if status == "rejected":
        await event.reply(f"❌ **ACCESS DENIED**\n\n@{OWNER_USERNAME}")
        return

    await event.reply("🔐 **WELCOME**\n\nRequest access:", buttons=kb_request_access())


# ==================== CALLBACK HANDLER ====================
@bot.on(events.CallbackQuery)
async def on_cb(event):
    try:
        data = event.data.decode()
        uid = event.sender_id

        # ═══ SUPPORT ═══
        if data == "support":
            await event.answer("💬 Support", alert=True)
            await safe_edit(event,
                f"{STAR_LINE}\n💬 **CUSTOMER SUPPORT**\n{STAR_LINE}\n\n"
                f"👑 **{OWNER_DISPLAY}**\n\n"
                f"• Make sure owner is admin\n"
                f"• Mention chat name\n"
                f"• Describe issue\n\n"
                f"⏱️ Reply within 24 hours",
                buttons=kb_support())
            return

        # ═══ ACCESS REQUEST ═══
        if data == "request_access":
            if is_auto_approve():
                db_set_approval(uid, "approved", approved_by=OWNER_ID)
                await event.answer("✅ Auto-approved!", alert=True)
                await safe_edit(event, "✅ Approved!", buttons=kb_welcome(uid))
                return
            if db_has_requested(uid):
                status = db_approval_status(uid) or "pending"
                await event.answer(f"⏳ {status}", alert=True)
                return
            try:
                sender = await event.get_sender()
                first_name = getattr(sender, "first_name", None) or "User"
                username = getattr(sender, "username", None)
            except Exception:
                first_name, username = "User", None
            ok, reason = db_create_approval(uid, first_name, username)
            if not ok:
                await event.answer(f"⏳ {reason}", alert=True)
                return
            try:
                await bot.send_message(OWNER_ID,
                    f"🔔 **REQUEST**\n👤 {first_name}\n🆔 `{uid}`",
                    buttons=kb_approval_actions(uid))
            except Exception:
                pass
            await event.answer("✅ Sent!", alert=True)
            await safe_edit(event, "⏳ **PENDING**", buttons=kb_request_access())
            return

        if data.startswith("approve:"):
            if uid != OWNER_ID:
                return
            target = int(data.split(":")[1])
            db_set_approval(target, "approved", approved_by=OWNER_ID)
            await event.answer(f"✅ Approved {target}", alert=True)
            try:
                tu = db_get_user(target)
                tn = tu[1] if tu else "User"
                await bot.send_message(target, get_approved_notify_message(tn),
                                       buttons=kb_welcome(target))
            except Exception:
                pass
            return

        if data.startswith("reject:"):
            if uid != OWNER_ID:
                return
            target = int(data.split(":")[1])
            db_set_approval(target, "rejected", approved_by=OWNER_ID)
            await event.answer(f"❌ Rejected", alert=True)
            return

        if data == "check_join":
            if await is_joined(uid):
                await event.answer("✅ Verified!", alert=True)
                status = db_approval_status(uid)
                auto = is_auto_approve()
                if uid == OWNER_ID or status == "approved" or auto:
                    await safe_edit(event, "👑 Welcome", buttons=kb_welcome(uid))
                else:
                    await safe_edit(event, "🔐 Need approval", buttons=kb_request_access())
            else:
                await event.answer("❌ Join first!", alert=True)
            return

        # ═══ BANNED / APPROVED CHECK ═══
        if db_is_banned(uid):
            await event.answer("🚫 Banned!", alert=True)
            return
        if uid != OWNER_ID and not is_approved(uid):
            await event.answer("❌ Not approved!", alert=True)
            return

        # ═══ HOME / INFO ═══
        if data == "home":
            await safe_edit(event, "🏠 **MAIN MENU**", buttons=kb_welcome(uid))
            return

        if data == "info":
            user = db_get_user(uid)
            limit = get_user_limit(uid)
            u = db_get_user_full(uid)
            aw = u[9] if u else 0
            txt = (
                f"ℹ️ **YOUR INFO**\n{DIV}\n\n"
                f"🆔 `{uid}`\n"
                f"📛 {user[1] if user else '—'}\n"
                f"🎁 Limit: **{limit} per post**\n"
                f"📡 Auto-Watch: **{'✅ UNLOCKED' if aw else '🔒 LOCKED'}**\n"
                f"🤖 Bots: **{db_count_visible_bots()}**\n"
            )
            await safe_edit(event, txt, buttons=kb_back())
            return

        # ═══ MANUAL REACTIONS ═══
        if data == "react_flow":
            if not feat_manual():
                await event.answer("❌ Manual reactions disabled by owner.", alert=True)
                return
            if not db_user_can(uid, "manual"):
                await event.answer("❌ Manual reactions not allowed for you.", alert=True)
                return
            USER_STATES[uid] = {"step": "wait_chat_type"}
            await safe_edit(event, "💫 **SEND REACTIONS**\n\nStep 1: Chat type?",
                            buttons=kb_chat_type())
            return

        if data == "chattype:channel":
            if not feat_channel():
                await event.answer("❌ Channel reactions disabled.", alert=True)
                return
            if not db_user_can(uid, "channel"):
                await event.answer("❌ Channel reactions not allowed.", alert=True)
                return
            USER_STATES[uid] = {"step": "wait_channel", "chat_type": "channel"}
            await safe_edit(event, "📢 **CHANNEL**\n\nSend channel link:", buttons=kb_back())
            return

        if data == "chattype:group":
            if not feat_group():
                await event.answer("❌ Group reactions disabled.", alert=True)
                return
            if not db_user_can(uid, "group"):
                await event.answer("❌ Group reactions not allowed.", alert=True)
                return
            USER_STATES[uid] = {"step": "wait_channel", "chat_type": "group"}
            await safe_edit(event, "👥 **GROUP**\n\nSend group link:", buttons=kb_back())
            return

        if data == "emoji:default":
            state = USER_STATES.get(uid, {})
            state["emoji_mode"] = "default"
            state["custom_emojis"] = None
            USER_STATES[uid] = state
            await event.answer("🎯 Default", alert=True)
            await _run_reactions(event, uid)
            return

        if data == "emoji:custom":
            if not feat_custom_emoji():
                await event.answer("❌ Custom emoji disabled.", alert=True)
                return
            if not db_user_can(uid, "custom_emoji"):
                await event.answer("❌ Not allowed.", alert=True)
                return
            state = USER_STATES.get(uid, {})
            state["step"] = "wait_custom_emoji"
            USER_STATES[uid] = state
            await safe_edit(event, "✏️ **CUSTOM EMOJI**\n\nSend emojis (space/comma):",
                            buttons=kb_back())
            return

        if data == "rc:all":
            if uid != OWNER_ID:
                return
            bots = db_list_bots()
            count = len(bots)
            state = USER_STATES.get(uid, {})
            state["reaction_count"] = count
            USER_STATES[uid] = state
            await event.answer(f"✅ ALL {count}", alert=True)
            await safe_edit(event, f"🎯 Count: **{count}**\n\nEmoji mode?",
                            buttons=kb_emoji_choice())
            return

        if data.startswith("rc:"):
            try:
                count = int(data.split(":")[1])
            except Exception:
                return
            visible_count = db_count_visible_bots()
            if uid != OWNER_ID:
                limit = get_user_limit(uid)
                if count > limit:
                    await event.answer(f"❌ Max {limit}.", alert=True)
                    return
            actual_count = min(count, visible_count if uid != OWNER_ID else db_count_bots())
            await event.answer(f"✅ {actual_count}", alert=True)
            state = USER_STATES.get(uid, {})
            state["reaction_count"] = actual_count
            USER_STATES[uid] = state
            await safe_edit(event, f"🎯 Count: **{actual_count}**\n\nEmoji mode?",
                            buttons=kb_emoji_choice())
            return

        if data == "rc_more":
            limit = get_user_limit(uid)
            await event.answer(f"💎 More than {limit} = PAID", alert=True)
            await safe_edit(event, f"💎 **MORE THAN {limit}**\n\nContact owner:",
                            buttons=kb_contact_owner())
            return

        # ═══ AUTO-WATCH FLOW ═══
        if data == "watch_flow":
            if not feat_autowatch():
                await event.answer("❌ Auto-Watch disabled by owner.", alert=True)
                return
            u = db_get_user_full(uid)
            unlocked = u[9] if u else 0
            if uid != OWNER_ID and not unlocked:
                await event.answer("🔒 Auto-Watch is a PAID feature.", alert=True)
                await safe_edit(event,
                    f"🔒 **AUTO-WATCH (PAID)**\n{DIV}\n\n"
                    f"Auto-Watch automatically sends reactions on every new post!\n\n"
                    f"💰 **Contact owner to unlock**\n\n"
                    f"👑 @{OWNER_USERNAME}\n🆔 `{OWNER_ID}`",
                    buttons=kb_contact_owner())
                return
            await safe_edit(event, "📡 **AUTO-WATCH**\n\nChoose:", buttons=kb_watch_menu())
            return

        if data == "watch:add":
            if not feat_autowatch():
                await event.answer("❌ Disabled", alert=True)
                return
            USER_STATES[uid] = {"step": "watch_wait_chat_type"}
            await safe_edit(event, "📡 **ADD WATCH**\n\nStep 1: Chat type?",
                            buttons=[
                                [btn("📢 Channel", data=b"watch:chattype:channel", style="primary")],
                                [btn("👥 Group", data=b"watch:chattype:group", style="success")],
                                [btn("🔙 Cancel", data=b"watch_flow", style="danger")],
                            ])
            return

        if data == "watch:chattype:channel":
            USER_STATES[uid] = {"step": "watch_wait_link", "chat_type": "channel"}
            await safe_edit(event, "📢 Send channel link:", buttons=kb_back())
            return

        if data == "watch:chattype:group":
            USER_STATES[uid] = {"step": "watch_wait_link", "chat_type": "group"}
            await safe_edit(event, "👥 Send group link:", buttons=kb_back())
            return

        if data == "watch:list":
            watchers = db_list_watchers(uid if uid != OWNER_ID else None)
            if not watchers:
                await safe_edit(event, "📋 **No watchers yet.**", buttons=kb_watch_menu())
                return
            txt = f"📋 **WATCHERS ({len(watchers)})**\n{DIV}\n\n"
            for w in watchers[:10]:
                (wid, wuid, cid, ctitle, clink, ctype, rcount,
                 emode, cemoji, lpid, active, created, last_run) = w
                status = "🟢" if active else "🔴"
                txt += f"{status} **#{wid}** {ctitle}\n"
                txt += f"   📊 {rcount} • {'Channel' if ctype=='channel' else 'Group'}\n"
                txt += f"   👤 `{wuid}`\n\n"
            rows = []
            for w in watchers[:5]:
                wid = w[0]
                rows.append([
                    btn(f"⚙️ #{wid}", data=f"watch:manage:{wid}".encode(), style="primary"),
                ])
            rows.append([btn("🔙 Back", data=b"watch_flow", style="primary")])
            await safe_edit(event, txt[:4000], buttons=rows)
            return

        if data.startswith("watch:manage:"):
            wid = int(data.split(":")[2])
            w = db_get_watcher(wid)
            if not w or (uid != OWNER_ID and w[1] != uid):
                await event.answer("❌ Not found", alert=True)
                return
            (wid, wuid, cid, ctitle, clink, ctype, rcount,
             emode, cemoji, lpid, active, created, last_run) = w
            st = "🟢 ACTIVE" if active else "🔴 PAUSED"
            txt = (
                f"📡 **WATCH #{wid}**\n{DIV}\n\n"
                f"📢 {ctitle}\n"
                f"🎯 Count: **{rcount}**\n"
                f"✏️ Emoji: **{emode}**\n"
                f"📊 Last post: **{lpid}**\n"
                f"🔄 Status: **{st}**\n"
            )
            rows = [
                [btn("🟢 Turn ON" if not active else "🔴 Turn OFF",
                     data=f"watch:toggle:{wid}".encode(),
                     style="success" if not active else "danger")],
                [btn("✏️ Edit Count", data=f"watch:edit_count:{wid}".encode(), style="primary")],
                [btn("✏️ Edit Emoji", data=f"watch:edit_emoji:{wid}".encode(), style="primary")],
                [btn("🗑️ Delete", data=f"watch:delete:{wid}".encode(), style="danger")],
                [btn("🔙 Back", data=b"watch:list", style="primary")],
            ]
            await safe_edit(event, txt, buttons=rows)
            return

        if data.startswith("watch:toggle:"):
            wid = int(data.split(":")[2])
            w = db_get_watcher(wid)
            if not w or (uid != OWNER_ID and w[1] != uid):
                return
            new_active = 0 if w[10] else 1
            db_update_watcher(wid, is_active=new_active)
            await event.answer(f"✅ {'Active' if new_active else 'Paused'}", alert=True)
            # Refresh
            w = db_get_watcher(wid)
            (wid, wuid, cid, ctitle, clink, ctype, rcount,
             emode, cemoji, lpid, active, created, last_run) = w
            st = "🟢 ACTIVE" if active else "🔴 PAUSED"
            txt = (f"📡 **WATCH #{wid}**\n{DIV}\n\n📢 {ctitle}\n"
                   f"🎯 Count: **{rcount}**\n🔄 Status: **{st}**")
            rows = [
                [btn("🟢 Turn ON" if not active else "🔴 Turn OFF",
                     data=f"watch:toggle:{wid}".encode(),
                     style="success" if not active else "danger")],
                [btn("✏️ Edit Count", data=f"watch:edit_count:{wid}".encode(), style="primary")],
                [btn("✏️ Edit Emoji", data=f"watch:edit_emoji:{wid}".encode(), style="primary")],
                [btn("🗑️ Delete", data=f"watch:delete:{wid}".encode(), style="danger")],
                [btn("🔙 Back", data=b"watch:list", style="primary")],
            ]
            await safe_edit(event, txt, buttons=rows)
            return

        if data.startswith("watch:edit_count:"):
            wid = int(data.split(":")[2])
            USER_STATES[uid] = {"step": "watch_edit_count", "wid": wid}
            await safe_edit(event, "✏️ Send new count (1-200):", buttons=kb_back())
            return

        if data.startswith("watch:edit_emoji:"):
            wid = int(data.split(":")[2])
            await safe_edit(event,
                f"✏️ **EDIT EMOJI #{wid}**\n\nChoose mode:",
                buttons=[
                    [btn("🎯 Default", data=f"watch:emoji:default:{wid}".encode(), style="success")],
                    [btn("✏️ Custom", data=f"watch:emoji:custom:{wid}".encode(), style="primary")],
                    [btn("🔙 Back", data=f"watch:manage:{wid}".encode(), style="danger")],
                ])
            return

        if data.startswith("watch:emoji:default:"):
            wid = int(data.split(":")[3])
            db_update_watcher(wid, emoji_mode="default", custom_emojis=None)
            await event.answer("✅ Default emoji", alert=True)
            await safe_edit(event, "✅ Updated!", buttons=[
                [btn("🔙 Back", data=f"watch:manage:{wid}".encode(), style="primary")]
            ])
            return

        if data.startswith("watch:emoji:custom:"):
            wid = int(data.split(":")[3])
            USER_STATES[uid] = {"step": "watch_edit_emoji", "wid": wid}
            await safe_edit(event, "✏️ Send emojis (space/comma):", buttons=kb_back())
            return

        if data.startswith("watch:delete:"):
            wid = int(data.split(":")[2])
            w = db_get_watcher(wid)
            if not w or (uid != OWNER_ID and w[1] != uid):
                return
            db_delete_watcher(wid)
            await event.answer("🗑️ Deleted", alert=True)
            await safe_edit(event, "✅ Deleted", buttons=kb_watch_menu())
            return

        # ═══ OWNER PANEL ═══
        if data == "owner_panel":
            if uid != OWNER_ID:
                return
            await event.answer("👑 Owner Panel")
            await safe_edit(event,
                f"👑 **OWNER PANEL**\n"
                f"👥 Users: **{db_total_users()}**\n"
                f"💫 Reactions: **{db_total_reactions()}**\n"
                f"📅 Today: **{db_reactions_today()}**\n"
                f"🤖 Bots: **{db_count_visible_bots()}**\n"
                f"📡 Watchers: **{len(db_list_watchers())}**\n"
                f"🔓 Auto: **{'✅ ON' if is_auto_approve() else '❌ OFF'}**\n"
                f"🎁 Free: **{get_free_count()}**",
                buttons=kb_owner())
            return

        # ── Feature toggles ──
        if data == "op:features":
            if uid != OWNER_ID:
                return
            await event.answer("🎛️ Feature Toggles")
            await safe_edit(event,
                f"🎛️ **FEATURE TOGGLES**\n{DIV}\n\n"
                f"Tap any button to toggle ON/OFF.\n\n"
                f"These affect **all users** globally.",
                buttons=kb_features())
            return

        if data.startswith("ft:toggle:"):
            if uid != OWNER_ID:
                return
            key = data.split(":", 2)[2]
            new_val = cfg_toggle(key)
            await event.answer(f"{'✅ ON' if new_val else '❌ OFF'}", alert=True)
            await safe_edit(event,
                f"🎛️ **FEATURE TOGGLES**\n{DIV}\n\n"
                f"Tap any button to toggle ON/OFF.",
                buttons=kb_features())
            return

        if data == "op:toggle_auto":
            new_val = not is_auto_approve()
            set_auto_approve(new_val)
            await event.answer(f"Auto: {'ON' if new_val else 'OFF'}", alert=True)
            await safe_edit(event, f"👑 **OWNER PANEL**\n🔓 Auto: **{'✅ ON' if new_val else '❌ OFF'}**",
                            buttons=kb_owner())
            return

        if data == "op:setfree":
            USER_STATES[uid] = {"step": "wait_setfree"}
            await safe_edit(event, f"⚙️ Current: {get_free_count()}\nSend new:",
                            buttons=kb_owner())
            return

        if data == "op:bots":
            bots = db_list_visible_bots()
            txt = f"🤖 **BOTS ({len(bots)})**\n\n"
            now = datetime.now()
            for i, r in enumerate(bots[:30], 1):
                tok = r[0]
                info = BOT_POOL.get(tok)
                status = "🟢"
                if is_bot_flooded(tok):
                    status = "🌊"
                elif info and info.get("busy_until") and info["busy_until"] > now:
                    status = "🔴"
                txt += f"{status} **{i}.** @{r[1]}\n"
            if len(bots) > 30:
                txt += f"\n... +{len(bots)-30} more"
            await safe_edit(event, txt[:4000], buttons=kb_owner())
            return

        if data == "op:dash":
            conn = sqlite3.connect(DB_FILE)
            try:
                approved = conn.execute("SELECT COUNT(*) FROM approvals WHERE status='approved'").fetchone()[0]
                banned = conn.execute("SELECT COUNT(*) FROM users WHERE is_banned=1").fetchone()[0]
            finally:
                conn.close()
            busy = sum(1 for t, i in BOT_POOL.items()
                       if i.get("busy_until") and i["busy_until"] > datetime.now())
            flooded = sum(1 for t in FLOOD_UNTIL if FLOOD_UNTIL[t] > datetime.now())
            await safe_edit(event,
                f"📊 **DASHBOARD**\n👥 Users: **{db_total_users()}**\n"
                f"✅ Approved: **{approved}**\n🚫 Banned: **{banned}**\n"
                f"💫 Reactions: **{db_total_reactions()}**\n"
                f"📅 Today: **{db_reactions_today()}**\n"
                f"🤖 Bots: **{db_count_visible_bots()}**\n"
                f"📡 Watchers: **{len(db_list_watchers())}**\n"
                f"🔴 Busy: **{busy}**  🌊 Flooded: **{flooded}**",
                buttons=kb_owner())
            return

        if data == "op:users":
            rows = db_all_users(10, 0)
            txt = f"👥 **USERS (10/{db_total_users()})**\n\n"
            buttons_rows = []
            for r in rows:
                icon = "🚫" if r[5] else "✅"
                lim = get_user_limit(r[0])
                txt += f"{icon} **{r[1] or '—'}** `{r[0]}` 🎁 {lim}\n"
                buttons_rows.append([
                    btn(f"⚙️ {r[1] or 'User'}", data=f"um:panel:{r[0]}".encode(), style="primary")
                ])
            buttons_rows.append([btn("🔙 Back", data=b"owner_panel", style="danger")])
            await safe_edit(event, txt[:4000], buttons=buttons_rows)
            return

        if data.startswith("um:panel:"):
            if uid != OWNER_ID:
                return
            target = int(data.split(":")[2])
            u = db_get_user_full(target)
            if not u:
                await event.answer("❌ Not found", alert=True)
                return
            await event.answer("⚙️ User Settings")
            txt = (
                f"⚙️ **USER SETTINGS**\n{DIV}\n\n"
                f"👤 **{u[1] or '—'}**\n"
                f"🆔 `{u[0]}`\n"
                f"📛 @{u[2] or 'none'}\n"
                f"✅ Status: {'BANNED' if u[5] else 'Active'}\n"
                f"🎁 Limit: **{u[8] if u[8] > 0 else get_free_count()}** per post\n"
                f"💫 Reactions: **{u[6]}**\n"
            )
            await safe_edit(event, txt, buttons=kb_user_manage(target))
            return

        if data.startswith("um:ban:"):
            if uid != OWNER_ID:
                return
            target = int(data.split(":")[2])
            u = db_get_user_full(target)
            new_ban = not u[5]
            db_ban_user(target, ban=new_ban)
            await event.answer(f"{'🚫 Banned' if new_ban else '✅ Unbanned'}", alert=True)
            u = db_get_user_full(target)
            txt = (f"⚙️ **USER SETTINGS**\n{DIV}\n\n"
                   f"👤 **{u[1] or '—'}**\n🆔 `{u[0]}`\n"
                   f"✅ Status: {'BANNED' if u[5] else 'Active'}\n"
                   f"🎁 Limit: **{u[8] if u[8] > 0 else get_free_count()}**\n")
            await safe_edit(event, txt, buttons=kb_user_manage(target))
            return

        if data.startswith("um:limit:"):
            if uid != OWNER_ID:
                return
            target = int(data.split(":")[2])
            USER_STATES[uid] = {"step": "user_set_limit", "target": target}
            await safe_edit(event, f"✏️ Send new limit for user `{target}`:",
                            buttons=kb_owner())
            return

        if data.startswith("um:channel:"):
            if uid != OWNER_ID:
                return
            target = int(data.split(":")[2])
            u = db_get_user_full(target)
            db_set_user_perm(target, "channel", not u[10])
            await event.answer("✅ Toggled", alert=True)
            await safe_edit(event, "Updated", buttons=kb_user_manage(target))
            return

        if data.startswith("um:group:"):
            if uid != OWNER_ID:
                return
            target = int(data.split(":")[2])
            u = db_get_user_full(target)
            db_set_user_perm(target, "group", not u[11])
            await event.answer("✅ Toggled", alert=True)
            await safe_edit(event, "Updated", buttons=kb_user_manage(target))
            return

        if data.startswith("um:manual:"):
            if uid != OWNER_ID:
                return
            target = int(data.split(":")[2])
            u = db_get_user_full(target)
            db_set_user_perm(target, "manual", not u[12])
            await event.answer("✅ Toggled", alert=True)
            await safe_edit(event, "Updated", buttons=kb_user_manage(target))
            return

        if data.startswith("um:autowatch:"):
            if uid != OWNER_ID:
                return
            target = int(data.split(":")[2])
            u = db_get_user_full(target)
            db_set_user_perm(target, "autowatch", not u[13])
            await event.answer("✅ Toggled", alert=True)
            await safe_edit(event, "Updated", buttons=kb_user_manage(target))
            return

        if data.startswith("um:custom:"):
            if uid != OWNER_ID:
                return
            target = int(data.split(":")[2])
            u = db_get_user_full(target)
            db_set_user_perm(target, "custom_emoji", not u[14])
            await event.answer("✅ Toggled", alert=True)
            await safe_edit(event, "Updated", buttons=kb_user_manage(target))
            return

        if data.startswith("um:unlock:"):
            if uid != OWNER_ID:
                return
            target = int(data.split(":")[2])
            u = db_get_user_full(target)
            db_set_user_perm(target, "auto_watch_unlocked", not u[9])
            await event.answer("✅ Toggled", alert=True)
            await safe_edit(event, "Updated", buttons=kb_user_manage(target))
            return

        if data == "op:watchers":
            if uid != OWNER_ID:
                return
            watchers = db_list_watchers()
            txt = f"📡 **ALL WATCHERS ({len(watchers)})**\n{DIV}\n\n"
            if not watchers:
                txt += "_No watchers yet._"
            for w in watchers[:10]:
                (wid, wuid, cid, ctitle, clink, ctype, rcount,
                 emode, cemoji, lpid, active, created, last_run) = w
                st = "🟢" if active else "🔴"
                txt += f"{st} **#{wid}** {ctitle} • {rcount}x • 👤 `{wuid}`\n"
            await safe_edit(event, txt[:4000], buttons=kb_owner())
            return

        if data == "op:broadcast":
            if uid != OWNER_ID:
                return
            chats = await get_admin_chats()
            await safe_edit(event, f"📢 **BROADCAST**\n\nChats: **{len(chats)}**\n\nChoose:",
                            buttons=[
                                [btn("📝 Text", data=b"bc:text", style="primary")],
                                [btn("🖼️ Photo+Text", data=b"bc:photo_text", style="success")],
                                [btn("🖼️ Photo", data=b"bc:photo", style="primary")],
                                [btn("🔙 Back", data=b"owner_panel", style="danger")],
                            ])
            return

        if data == "bc:text":
            USER_STATES[uid] = {"step": "wait_bc_text"}
            await safe_edit(event, "📝 Send text:", buttons=kb_owner())
            return

        if data == "bc:photo_text":
            USER_STATES[uid] = {"step": "wait_bc_photo"}
            await safe_edit(event, "🖼️ Send photo URL:", buttons=kb_owner())
            return

        if data == "bc:photo":
            USER_STATES[uid] = {"step": "wait_bc_photo_only"}
            await safe_edit(event, "🖼️ Send photo URL:", buttons=kb_owner())
            return

        if data == "op:adduser":
            USER_STATES[uid] = {"step": "wait_add_user_id"}
            await safe_edit(event, "➕ Send user ID:", buttons=kb_owner())
            return

        if data == "op:recent":
            rows = db_recent_reactions(15)
            txt = "📜 **RECENT**\n\n"
            for r in rows:
                icon = "✅" if r[6] == "ok" else "❌"
                txt += f"{icon} {r[4]} @{r[5]}\n   👤 `{r[0]}`\n\n"
            await safe_edit(event, txt[:4000] or "_None._", buttons=kb_owner())
            return

        if data == "op:pending":
            rows = db_pending_approvals(10)
            if not rows:
                await safe_edit(event, "✅ No pending.", buttons=kb_owner())
                return
            for r in rows:
                try:
                    await bot.send_message(OWNER_ID,
                        f"🔔 **PENDING**\n👤 {r[1]}\n🆔 `{r[0]}`",
                        buttons=kb_approval_actions(r[0]))
                    await asyncio.sleep(0.4)
                except Exception:
                    pass
            await safe_edit(event, f"⏳ Sent {len(rows)}.", buttons=kb_owner())
            return

        if data == "op:approved":
            rows = db_approved_users(20)
            txt = f"✅ **APPROVED ({len(rows)})**\n\n"
            for r in rows:
                txt += f"👤 {r[1] or '—'} `{r[0]}`\n"
            await safe_edit(event, txt[:4000] or "_None._", buttons=kb_owner())
            return

    except Exception as e:
        D_err(e, "on_cb")
        try:
            await event.answer("❌ Error", alert=True)
        except Exception:
            pass


# ==================== MESSAGE HANDLER ====================
@bot.on(events.NewMessage)
async def on_msg(event):
    try:
        if event.is_channel:
            return
        uid = event.sender_id
        if uid is None:
            return
        if event.text and event.text.startswith("/"):
            return

        try:
            sender = await event.get_sender()
            if sender is None or isinstance(sender, (Channel, Chat)):
                first_name, username = "User", None
            else:
                first_name = getattr(sender, "first_name", None) or "User"
                username = getattr(sender, "username", None)
        except Exception:
            first_name, username = "User", None

        db_save_user(uid, first_name, username)
        if db_is_banned(uid):
            return

        # ── Owner states ──
        if uid == OWNER_ID and uid in USER_STATES:
            state = USER_STATES[uid]
            step = state.get("step")

            if step == "wait_bc_text":
                text = event.text.strip()
                del USER_STATES[uid]
                msg = await event.reply("📢 Broadcasting...")
                ok, fail, total = await broadcast_message(text=text)
                await msg.edit(f"✅ Done\nTotal: {total}\nSent: {ok}\nFailed: {fail}")
                return

            if step == "wait_bc_photo_only":
                url = event.text.strip()
                del USER_STATES[uid]
                msg = await event.reply("📢 Broadcasting...")
                ok, fail, total = await broadcast_message(photo_url=url)
                await msg.edit(f"✅ Done\nTotal: {total}\nSent: {ok}\nFailed: {fail}")
                return

            if step == "wait_bc_photo":
                url = event.text.strip()
                state["photo_url"] = url
                state["step"] = "wait_bc_photo_caption"
                USER_STATES[uid] = state
                await event.reply("🖼️ Now send caption:")
                return

            if step == "wait_bc_photo_caption":
                text = event.text.strip()
                url = state.get("photo_url")
                del USER_STATES[uid]
                msg = await event.reply("📢 Broadcasting...")
                ok, fail, total = await broadcast_message(photo_url=url, text=text)
                await msg.edit(f"✅ Done\nTotal: {total}\nSent: {ok}\nFailed: {fail}")
                return

            if step == "wait_setfree":
                text = event.text.strip()
                if not text.isdigit():
                    await event.reply("❌ Number")
                    return
                n = int(text)
                cfg_set("free_count", n)
                del USER_STATES[uid]
                await event.reply(f"✅ Free: {n}", buttons=kb_owner())
                return

            if step == "wait_add_user_id":
                text = event.text.strip()
                if not text.lstrip("-").isdigit():
                    await event.reply("❌ Invalid ID")
                    return
                target = int(text)
                db_set_approval(target, "approved", approved_by=OWNER_ID)
                del USER_STATES[uid]
                await event.reply(f"✅ Granted `{target}`", buttons=kb_owner())
                return

            if step == "user_set_limit":
                text = event.text.strip()
                if not text.isdigit():
                    await event.reply("❌ Number")
                    return
                target = state.get("target")
                db_set_user_limit(target, int(text))
                del USER_STATES[uid]
                await event.reply(f"✅ Limit set for `{target}`",
                                  buttons=kb_user_manage(target))
                return

        # ── User states ──
        if not await is_joined(uid):
            await event.reply("Join channel first:", buttons=kb_join())
            return
        if uid != OWNER_ID and not is_approved(uid):
            await event.reply("Need OWNER APPROVAL.", buttons=kb_request_access())
            return
        if uid not in USER_STATES:
            await event.reply("Send /start.", buttons=kb_welcome(uid))
            return

        state = USER_STATES[uid]
        step = state.get("step")

        # Manual reactions
        if step == "wait_channel":
            text = event.text.strip()
            state["channel_link"] = text
            state["step"] = "wait_post"
            USER_STATES[uid] = state
            await event.reply("✅ Chat link saved.\n\nSend post link:", buttons=kb_back())
            return

        if step == "wait_post":
            text = event.text.strip()
            state["post_link"] = text
            state["step"] = "wait_count"
            USER_STATES[uid] = state
            limit = get_user_limit(uid)
            visible = db_count_visible_bots()
            header = (f"👑 OWNER — {visible} bots"
                      if uid == OWNER_ID
                      else f"🎁 Limit: **{limit} per post**")
            await event.reply(f"✅ Post link saved.\n\nHow many reactions?\n\n{header}",
                              buttons=kb_reaction_count(uid))
            return

        if step == "wait_custom_emoji":
            text = event.text.strip()
            parts = re.split(r"[,\s]+", text)
            emojis = []
            for p in parts:
                p = p.strip()
                if p and p in ALL_REACTIONS and p not in emojis:
                    emojis.append(p)
            if not emojis:
                await event.reply("❌ No valid emojis.", buttons=kb_back())
                return
            if len(emojis) > 30:
                emojis = emojis[:30]
            state["custom_emojis"] = emojis
            state["emoji_mode"] = "custom"
            USER_STATES[uid] = state
            await event.reply(f"✅ Starting...")
            await _run_reactions(event, uid)
            return

        # Auto-Watch flow
        if step == "watch_wait_link":
            text = event.text.strip()
            chat_ref, invite_hash = parse_channel_link(text)
            state["watch_link"] = text
            state["watch_chat_type"] = state.get("chat_type", "channel")
            state["step"] = "watch_wait_count"
            USER_STATES[uid] = state
            await event.reply("✅ Link saved.\n\nSend reactions count per post (1-50):",
                              buttons=kb_back())
            return

        if step == "watch_wait_count":
            text = event.text.strip()
            if not text.isdigit():
                await event.reply("❌ Number")
                return
            n = min(int(text), 50)
            state["watch_count"] = n
            state["step"] = "watch_wait_emoji"
            USER_STATES[uid] = state
            await event.reply(f"✅ Count: {n}\n\nChoose emoji mode:",
                              buttons=[
                                  [btn("🎯 Default", data=b"watch_emoji:default", style="success")],
                                  [btn("✏️ Custom", data=b"watch_emoji:custom", style="primary")],
                                  [btn("🔙 Cancel", data=b"watch_flow", style="danger")],
                              ])
            return

        if step == "watch_wait_custom_emoji":
            text = event.text.strip()
            parts = re.split(r"[,\s]+", text)
            emojis = [p.strip() for p in parts if p.strip() in ALL_REACTIONS]
            if not emojis:
                await event.reply("❌ No valid emojis.")
                return
            state["watch_custom_emojis"] = emojis[:30]
            USER_STATES[uid] = state
            await _finalize_watch_add(event, uid)
            return

        if step == "watch_edit_count":
            text = event.text.strip()
            if not text.isdigit():
                await event.reply("❌ Number")
                return
            wid = state.get("wid")
            db_update_watcher(wid, reaction_count=min(int(text), 200))
            del USER_STATES[uid]
            await event.reply(f"✅ Updated!", buttons=[
                [btn("🔙 Back", data=f"watch:manage:{wid}".encode(), style="primary")]
            ])
            return

        if step == "watch_edit_emoji":
            text = event.text.strip()
            parts = re.split(r"[,\s]+", text)
            emojis = [p.strip() for p in parts if p.strip() in ALL_REACTIONS]
            if not emojis:
                await event.reply("❌ No valid emojis.")
                return
            wid = state.get("wid")
            db_update_watcher(wid, emoji_mode="custom",
                              custom_emojis=",".join(emojis[:30]))
            del USER_STATES[uid]
            await event.reply(f"✅ Updated!", buttons=[
                [btn("🔙 Back", data=f"watch:manage:{wid}".encode(), style="primary")]
            ])
            return

    except Exception as e:
        D_err(e, "on_msg")


async def _finalize_watch_add(event, uid):
    """Add watcher to DB and start."""
    state = USER_STATES.get(uid, {})
    link = state.get("watch_link")
    chat_type = state.get("watch_chat_type", "channel")
    count = state.get("watch_count", 5)
    custom = state.get("watch_custom_emojis")
    mode = "custom" if custom else "default"

    try:
        chat_ref, invite_hash = parse_channel_link(link)
        if invite_hash:
            try:
                await admin_client(ImportChatInviteRequest(invite_hash))
            except Exception:
                pass
            entity = await admin_client.get_entity(f"https://t.me/+{invite_hash}")
        else:
            entity = await admin_client.get_entity(chat_ref)
    except Exception as e:
        await event.reply(f"❌ Could not resolve: {e}")
        if uid in USER_STATES:
            USER_STATES[uid] = {}
        return

    chat_id = entity.id
    chat_title = getattr(entity, "title", "Unknown")

    # Check if already watching
    existing = db_list_watchers(uid)
    for w in existing:
        if w[2] == chat_id:
            await event.reply(f"⚠️ You already watch **{chat_title}**")
            if uid in USER_STATES:
                USER_STATES[uid] = {}
            return

    # Get current last post ID
    try:
        msgs = await admin_client.get_messages(entity, limit=1)
        last_id = msgs[0].id if msgs else 0
    except Exception:
        last_id = 0

    wid = db_add_watcher(uid, chat_id, chat_title, link, chat_type,
                         count, mode, custom, last_id)

    await event.reply(
        f"{SPARKLE} ✅ **WATCH ADDED** {SPARKLE}\n{DIV}\n\n"
        f"📢 Chat: **{chat_title}**\n"
        f"🎯 Reactions per post: **{count}**\n"
        f"✏️ Emoji: **{mode}**\n"
        f"📊 Watching from post: **#{last_id}**\n\n"
        f"🟢 **Auto-Watch is now ACTIVE!**\n\n"
        f"I'll send reactions on every new post.",
        buttons=[
            [btn("📋 My Watches", data=b"watch:list", style="primary")],
            [btn("🏠 Home", data=b"home", style="success")],
        ]
    )
    if uid in USER_STATES:
        USER_STATES[uid] = {}


# ═══ Additional callbacks for watch flow ═══
@bot.on(events.CallbackQuery(data=b"watch_emoji:default"))
async def cb_watch_emoji_default(event):
    uid = event.sender_id
    state = USER_STATES.get(uid, {})
    state["watch_custom_emojis"] = None
    USER_STATES[uid] = state
    await event.answer("🎯 Default", alert=True)
    await _finalize_watch_add(event, uid)


@bot.on(events.CallbackQuery(data=b"watch_emoji:custom"))
async def cb_watch_emoji_custom(event):
    uid = event.sender_id
    state = USER_STATES.get(uid, {})
    state["step"] = "watch_wait_custom_emoji"
    USER_STATES[uid] = state
    await safe_edit(event, "✏️ Send emojis (space/comma):", buttons=kb_back())


# ==================== TASK LOCK RUNNER ====================
async def _run_reactions(event, uid):
    global TASK_RUNNING, TASK_OWNER_UID

    if TASK_RUNNING:
        await safe_edit(event,
            f"⏳ **Please Wait**\n{DIV}\n\n"
            f"Another task is running.\nTry again in a moment.",
            buttons=kb_back())
        if uid in USER_STATES:
            USER_STATES[uid] = {}
        return

    state = USER_STATES.get(uid, {})
    chat_link = state.get("channel_link")
    post_link = state.get("post_link")
    count = state.get("reaction_count", 0)
    emoji_mode = state.get("emoji_mode", "default")
    custom_emojis = state.get("custom_emojis")

    if not chat_link or not post_link or count <= 0:
        await event.answer("❌ Missing data", alert=True)
        return

    TASK_RUNNING = True
    TASK_OWNER_UID = uid
    try:
        await process_reactions_rotating(
            event, uid, chat_link, post_link, count,
            emoji_mode=emoji_mode, custom_emojis=custom_emojis
        )
    finally:
        TASK_RUNNING = False
        TASK_OWNER_UID = None


# ==================== MAIN ====================
async def main():
    db_init()
    await admin_client.start()
    if not await admin_client.is_user_authorized():
        print("❌ Session invalid.")
        return

    me = await admin_client.get_me()
    bots, added = sync_bots()

    D_sep("GHOST REACTION BOT — v49")
    D(f"Owner: {me.first_name} (@{me.username})", "ok")
    D(f"Bots: {db_count_visible_bots()} / total {db_count_bots()}", "ok")
    D(f"Button colors: {'✅ YES' if HAS_BUTTON_STYLE else '❌ NO'}", "info")
    D(f"Task lock: ENABLED", "lock")
    D(f"Auto-Watcher: ENABLED", "watch")
    D("Bot online.", "ok")

    # Start watcher loop in background
    asyncio.create_task(watcher_loop())

    await bot.start(bot_token=BOT_TOKEN)
    await bot.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
