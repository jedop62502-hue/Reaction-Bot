"""
============================================================
   GHOST REACTION BOT v65 - FINAL
   Real Accounts + Dynamic Payments + Animations + Friendly
   Credit: @Anonymous_User_37
============================================================
"""
import os, sys, time, random, asyncio, re, hashlib
import sqlite3, requests, traceback, logging
from datetime import datetime, timedelta

from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.messages import (
    ImportChatInviteRequest, AddChatUserRequest, SendReactionRequest)
from telethon.tl.functions.channels import (
    InviteToChannelRequest, GetParticipantRequest,
    EditAdminRequest, GetParticipantsRequest)
from telethon.tl.types import (
    Channel, Chat, ChatAdminRights, ChannelParticipantsAdmins, ReactionEmoji)

try:
    from telethon.tl.types import KeyboardButtonStyle
    HAS_BUTTON_STYLE = True
    print("[STARTUP] ✅ ButtonStyle OK")
except ImportError:
    KeyboardButtonStyle = None
    HAS_BUTTON_STYLE = False
    print("[STARTUP] ⚠️ ButtonStyle missing")

from telethon.errors import FloodWaitError
from telethon.errors.rpcerrorlist import (
    MessageIdInvalidError, MessageNotModifiedError,
    UserNotParticipantError, UserAlreadyParticipantError)

from aiohttp import web
import github_sync

logging.basicConfig(level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

# ══════════════════════ CONFIG ══════════════════════
API_ID = 30217812
API_HASH = "d21066a90786cf2dd348b907ece69d24"
ADMIN_SESSION = "1BJWap1wBu2X5POvvWDOSvJZAROd9WIKpJMpSIf-W3skkHehdGLol5KkobjCIfohj9gFhHqh3UKkwjLJAsMqDbuWAflGN8yb1Qu7LxiKBsZCFYHKAHKBfxZgJyv35ivBxl881TvLZ6dbpdfM4_-66CTW7HnBE-j0_yktVaX-q3o1VaL3HYZJkb_wnI5BaJow7s9IHYtqlyWM2RYeQgcQVc23CDjHKLR4qdFpaMM_T2SuQQ478eDnUGQ-R891NssFOq0lOGs765CyI1ngt_C-NU3PYpvHVyJhFHZ3eBqsrgnmP0tpeSC1mJ2egouxeevr7pPUKMdMI_QyoA0aiTviAMEGlERWbrEA="
BACKUP_SESSION_1 = "1AZWarzgBu2tZBeVP2KqGU3PKmu6shSzj5y_cyk-lPl-ymgoGjlVentuWIYdFQ9x_LZxoePMIgwoJM4EVThTNBvdAL0gqTqI5vgQOCzCYghU9p6J9oA-k4eEO8PJESXN-LsN7ch9_MZY-bx8UdBlJvSj1tZkJzbj8ByaSvVwVncgx1r8xtrTqwr8aWUGfxPKI0ESZBK9msBt7Kx2nRht8S1Yb1jcnP5AwNvgV4O73bqnHIZfRKy2cRVSXFiUII-AKsLh_ByQrOOGKIta2JHdzWlUlDBuSvsHLqbDW4NT44bApZskFNr46K-KbeKVE0OObN9-aBGAOpcjubn5V_UsPGV-6kTD2W70="
BOT_TOKEN = "8878162447:AAGMBnukLS2jPxfBthfeY1GAblCCrgtaH2M"

BOT_TOKENS = [
    "8841673258:AAHmkFSMiuS6eja_CnqVH548wcam_XBRAY4","7593703253:AAEgY5r_UoBtXYiCntg6wt_seiBbhxqrMeI",
    "8553819198:AAEtfCIbrvgkvtAhUNMhull2sYZcnBVSj8o","8974028456:AAHmZvMGFbGBy0ie4pQfICxXnqy5GG4Racg",
    "8988266285:AAFrB5RXFcbDyd_-_RZrnMpNVDakIrXT_ePc","8708232817:AAH6jRVisH7W1GvVdZIDbPT-LBELs0NVVzY",
    "8913217410:AAG1sjOnzMGJgGd1wjmbQevpI9QVrKeAdxI","8820548215:AAG9cyP2k9MBkUgJ4q2sQH8W9AaTh1nAcdQ",
    "8968734078:AAGEq778W3nJlADAQdp_zaiatlW-UyDKj1Q","8328358987:AAEcvUOW0AIZBsYrl5C1ediUbR9rCkHVrtg",
    "8728464321:AAGsyJihokd7r5Tlp54W4lPWrFpvRlULRFE","8930721931:AAErSyWq5cRUC7NjfLzLU4F7vuHTF9vfVkM",
    "8783856775:AAE5oRj-CfvKu1QkbabnpYf_NresBkFN_FA","8748532509:AAEQYzaL4BBLddWoF-laUlQ-dR_nC-2v3sQ",
    "8956849671:AAGToCuy-bsGRMxexUAjWIHBiO-XK7mTSTg","8846722436:AAE4blebnl-47O8D7MIYEpaDvlSE1T6PjOs",
    "8944172439:AAF6Bob4CFkN9J1uYfHhzR5F_DboZo5pZ2o","8745749488:AAH9iBk_3OhdRQSxL0_i7ZKY9muQlhruLUw",
    "8841955340:AAG1wx_6Qg-mRdulTXA_10ZyUMt5uS1pM7E","8924067849:AAGTfhAeymFPNkzHZs7qYfoLdHh1Eci9LYM",
    "8771116985:AAEVflfEL_jhDlCjgjuEGEq5ew7XQZtA42w","8603663849:AAFULr5Oa2hxKVvXP9SEUfgTHwOKVsnEVJE",
    "8931110714:AAFc7jMeqLrZNnJT-Gu1PvOCC1KtYiphQcM","8803252857:AAFeiuLDYZq1vXl0HPixIny7sVgwInbeDI4",
    "8979609203:AAH2y70TChxnGN12meD79zfhvgrOUcLxgpQ","8905843316:AAEt7EiKOinstEIFVblgKImWKpDMAx3VOss",
    "8989541204:AAHSlSxo2BTWo4CwHi99wnO2seJ4Q6Ijcl0","8944322541:AAE-L4laExHQoz0RtGGZH4rR0w9HRBsZ5ZQ",
    "8641606957:AAFo2g3KF3_MM2gSqfoLrO-GcdeZDrku_rI","8964416323:AAFCgLhsuDRX6e_qKSdMSeJMvOnftyJIpjw",
    "8857844062:AAHkqUl93T5IIeQzRVI4gTbDtGNXM2l56vY","8819430996:AAG61wjEPXzQt51-XXvxLk44xUUVevEM-Zg",
    "8822557788:AAGo0EpEEj6oPTDS6AZvFQRJLbY0SKILm9E","8698942203:AAHqYg0fbbw91_VXLy-QMaAweNOYpTt0_8U",
    "8685235239:AAFde1c3wMjQUNky9DBFjPZRwiQIzwv2eWM","8768563277:AAEw6E0YI9VvaWKWqGrWV7r__VIECYfd4Tw",
    "8510446309:AAHhEoCC3elgLIsDUNQx8sdT97OOOVKFLGQ","8950435967:AAHz9cX7ni-h9cYfDB-B0Ze7hbTTge9aSS0",
    "8952785819:AAHlGqZdLvIAu_7Gc5cnEWIk_qcX05Uu3L8","8868030693:AAEwQNOs9GLbryk2NyKNCCUioYvEguTcLZA",
    "8757705970:AAEHdekrha8nKfM1dD_K2qQDGEpM62bq7fo","8815901180:AAFvbu5PHknm7Yuiyf4RvK_vMtYW0-KY4oA",
    "8785643638:AAGk7RfKtOkFgGA9VMc-R2KUuot2chkErfY","8871939279:AAFNABGPWmo-jYugam_8yosqvTvlqUs6rOw",
    "8853912055:AAEBXCqq444SNm1PuAWDhAGmqHhsXUhgGhM","8821582256:AAG8RtlrztqJxaX7Tm02A_s9FQhRYoCLOFY",
    "8900198440:AAGxqWK8pv9ymM8Q3h_8LkM3bN6xYzKZfZE","8714611659:AAGYKV151mrnPd8L4un2jqyeGKYJWgWyUNM",
    "8938927350:AAGqDG704mjg-jRhvy5I23pGKsLc5NRXHQY","8256889928:AAHi_MEPlcCX_RAGGijMjjEFu7dPTPL0WZc",
    "8833683561:AAFYJK1JFpZ70AQcV4qGJV6LEZwAqGlqdnM","8100369464:AAEgoYuvVDyiamsJE4Wvn8tNP3AeULjr7qQ",
    "8662013526:AAFpMDtWcV-vPVIIUhwzF890JbzvPONvHeE","8729112057:AAHNJH5Q52rG06cxUhVH5v9abckcorrk-cc",
    "8471788383:AAFh-7qdOm0p_YZfHu-cFlnX0EvbaR_EPNA","8891259440:AAFkd8xRSTXYjLYBoc5BJCUraaECgJyw7MA",
    "8983293074:AAGAEWkH_fRsE1ZHDO6Y8400ItngSMUzWn0","8471875480:AAExUSZAMmB3DJDjBHJJzQFreb4wuUhF-LE",
    "8861709151:AAGkJdg6dfNHgkImCoXLeqpj09BXaFn9K3A","8609489669:AAHFCpioHV24w5UGNsCwEshFmb9SbAsexCQ",
    "8820797593:AAFTZM5d-2lFKU01RtDHwihAHESc6diPfQM","8962290157:AAHXjwHwh_t9msQi0CcudyXM2k220WCDCK0",
    "8008985452:AAG8Bdv1_RxeUMJVls6_Xii1p_inQNlVgxo","8971769677:AAH35Rj_VJbjRlJtFcqQIeuEJ2hWlfjKSU0",
    "8990507622:AAHnMjPXwH2pU9X5wEAmWVWT5M7MwZy5dag","8784663275:AAH8P9qX9v9csE9I-KXnsRcgkjchRsQnDso",
    "8938896874:AAFL2y5KXpzsatkpLIFI057z28GnXU68JRY","8988481023:AAFYAdCPKeFf0ggzW7rVztxQGo7ZxTFEGK8",
    "8994425405:AAGP6ekwed9AHZ3gSf2CsvFSY1EYrZpvNaE","8960571934:AAFlTT44gSwOKsR9-EIRRSV5sLVYOfB69Lg",
    "8779154787:AAFTgYyGhFH9tl886CCAJf693FDcVNhV9U0","8903745472:AAEUCdpnOmFb7FvxAPWYyI9hiHqJJvgxYeQ",
    "8996047725:AAF4hqBOfZX9KkvKrRtzWVKmAMih5rWGd3k","8813887147:AAHPuB5fPRYsZPsdAzywzvEcFBKESdDzmFI",
    "8918383154:AAGD9zce0bs0NOdr2BRiMYQYTgB5yYfHM00","8350933617:AAEf3w6E_m9A_-0Gjo9ipB6-gF1gnYh6u1M",
    "8965953734:AAEMAsvzZE-3Yxf7_ZawAHrG5EN9ewNAfro","8221570065:AAFUFQuB2w2aXjGhh9PtTSbOYi2knb5cEnc",
    "8919303440:AAE2c4d_UwTHCWnm3LGOZ0mKntWrK11g78w","8832547686:AAHl5TnZF5yddtqgnWTHScuIQ3H_D-5FyiE",
    "8949714253:AAEq-kdm7HUj17a2S-2PV7FuuGvUIKusk7Q","8950470890:AAFOc5fE-55FU8fp07HvrrwbKFDtokVz37U",
    "8816997120:AAG3hoky363ACg0sNLTHAz2gdvZ6GBDdUk4","8857013054:AAGKXdUshAe2bZEPHcfxabK7cEpNPfZZbkA",
    "8826047151:AAGIFXxzoVHhNtpca5bavuo6mcKLgUo89Zg","8968831352:AAGFUCm9G_tnVrEskE2S8tmjkucteWCyRSo",
    "8889331184:AAETFEujC9Tkdlrnzr-etu3MUy9Usv_n2tg","8189182599:AAGW4N-_kDhi__wdDxvELX_JqPRyDy4f2CI",
    "8899796556:AAFpkw6ou_KLLNpxc799wff01Df8ARGf6AE","8913059580:AAGYXEjE-AWLsrSt1G8Fhpw0_1o-SiTen_Q",
    "8623196341:AAEWQX-5V9CiearLhCjCIUJ9dkJyltFHaBQ","8893398545:AAG6ytTXtGXsoWG6vFRylbOYXfldHpMzq7s",
    "8552097300:AAFp3DZvoxoZoWTdT-JDGzzYD9MybMus--Y","8981400829:AAHJYVnt0sjQCw47c8Wse9kysLPrT52IBpY",
    "8963410266:AAGR9sXmxA1rrciIz5MZMxByGg1wVOEN9Zg","8716210889:AAESTa6z6lhIL83a4N2ld1iXcA_L-WqRJhg",
    "8912557604:AAHQq888h9ojNuGYssw7n9Ro64rYIz_8SlY","8291028314:AAFrLRo2E_jT3bazVkDKpgd42ppGFJgFV8c",
    "8418409480:AAFYfuWbuuyaD54Ks_ThQAGEHTw3nzbrTyw","8935405135:AAFC3ONCxh-LM2axSRVj0T_GkRFrGf242BY",
    "8862081715:AAGAKOqQZPEm6t1rs1S8W0aQ0ctGv_rPrZ8","8950949832:AAHPAuHamEqE-B9Z3U5dpL4pUyTbcqfETIA",
    "8841428180:AAFPjIUBID7jeC2hj5aM4PuWo2-NJ29sWjM","8941585136:AAFcpOoVjVYuU0UrOvO0w8zd1k0ZxDl2Qlo",
    "8634996391:AAGpg8B4Uh9KIH4bd7jlszmzI03zUqBQnVQ","8813724246:AAHP0rnBLPfBoQmcftjk4i7nfVMZZVp6UrE",
    "8741375662:AAHgRJAK3FLPb9y_Gc-Y8yktiTC4Lr2S-18","8974865654:AAFF4uB0yJLSJSHJTHXigvrPW-rWhB6qFeo",
    "8911644039:AAFYE8CTP7jmwLQljMlAnSzpe02G19VvZwE","8962352673:AAFR6qFzABemeFI_5CX8EXifoxGBI5ZyrPw",
    "8857051106:AAEbY0nWQUsNxQBFJbnCCfv_bZn9vvZjeng","8938143439:AAE7og1KxgCKE_2s_m3nCl4GDuvh_MvPs8w",
    "8824445026:AAEwXki7eTKBmHzC8HVjALgnNB4XhzucfE0","8653676138:AAEnWUCQy3DTuL_u8qPX1kjpfAoGn-vdu30",
    "8605109730:AAG_nkDk--Du7s03iC8sCGU8WxuT2NjU5pU","8913650429:AAGgjDUN1GzDbAv8nTN22-A-mISIEgOBzJM",
    "8851289196:AAGICsicQG11JTb0H7abgWn0ms5HYMTTI4o","8941332755:AAEnb3eJfJAnr3dwkcuxVOmJGIfZkbSU1HA",
    "8940700372:AAGYRHGcLdime__fV487QNGn_Wvj_5uviBM","8968649929:AAGIrxG7rbxK08yIg6kUEobPqLRQrwXi5dY",
    "8683641338:AAHO3dT8HdV7uTcN5UhCB6KmCiHA0-uco7I","8655009239:AAGw-Y9ur0X0hu6t17ouYSL7BmHbd51tKk8",
    "8696672028:AAHiAB-U1A2650-HO4vaY-HE6kinLtlFUcQ",
]

OWNER_USERNAME_DEFAULT = "Anonymous_User_37"
OWNER_ID_DEFAULT = 8762845215
FORCE_CHANNELS_DEFAULT = []

SESSIONS_DIR = os.getenv("SESSIONS_DIR", "sessions")
REAL_CLIENTS = {}
REAL_CLIENT_LOCK = asyncio.Lock()
REAL_FLOOD_UNTIL = {}
REAL_COOLDOWN = 1.2

github_sync.start_sync_thread()
DB_FILE = github_sync.LOCAL_DB_PATH if github_sync.is_enabled() else (
    "/app/data/ghost_users.db" if os.path.isdir("/app/data") else "ghost_users.db")

DEFAULT_REACTIONS = ["❤️","👍","🔥"]
ALL_REACTIONS = ["❤️","🔥","🥰","😍","👍","😇","👀","😎","💯","🎉","🤩","🥳","😁","😂","🤣","😊",
                 "🙏","👏","💪","⚡","🌚","🌭","🍾","💋","🖕","😈","🤝","🎃","👻","🤡","🤔","🤨",
                 "😐","😑","😶","🙄","😏","😣","😥","😮","🤐","😯","😪","😫","🥱","😴","😌","😛","😜","🤪"]

DEFAULT_FREE_COUNT = 5
MAX_REACTIONS = 200
BROADCAST_DELAY = 1.5
FLOOD_SAFETY = 3
PER_BOT_TIMEOUT = 25
PERMANENT_ADMIN_BOTS = {"RN_OTP1_bot","RN_REACTION_BOT"}
WATCHER_CHECK_INTERVAL = 300
QUEUE_CHECK_INTERVAL = 60
AUTO_WATCH_ENABLED = True
BOT_BUSY_TIMEOUT = 2
POOL_CLEANUP_INTERVAL = 30
USER_COOLDOWN = 15
MAX_CYCLES = 25

PLAN_LIMITS = {"free":5,"basic":20,"pro":50,"premium":200}
PLAN_NAMES = {"free":"🆓 Free","basic":"🥉 Basic","pro":"🥈 Pro","premium":"🥇 Premium"}
DURATIONS = {1:"1 Day",7:"7 Days",15:"15 Days",30:"30 Days"}
PAID_PLANS = {"basic","pro","premium"}
DEFAULT_PRICES = {"basic":{1:70,7:250,15:500,30:900},"pro":{1:120,7:400,15:800,30:1400},"premium":{1:200,7:700,15:1400,30:2500}}
LANGUAGES = {"en":"🇬🇧 English","ur":"🇵🇰 اردو","hi":"🇮🇳 हिन्दी","ar":"🇸🇦 العربية","ru":"🇷🇺 Русский","es":"🇪🇸 Español","id":"🇮🇩 Indonesia"}
REFERRAL_REWARD = 5
FRIEND_VALID_REWARD = 10
EMOJI_PACKS = {"love":["❤️","😍","🥰","💋","😘"],"fire":["🔥","💯","⚡","🌟","✨"],
               "funny":["😂","🤣","😁","😅","🤡"],"cool":["😎","👀","🙌","💪","🤝"],
               "party":["🎉","🥳","🎊","🎈","🎁"]}

BOT_POOL = {}
BOT_POOL_LOCK = asyncio.Lock()
FLOOD_UNTIL = {}
ADMIN_CACHE = {}
ADMIN_CHECK_ENABLED = True
TASK_RUNNING = False
TASK_OWNER_UID = None
USER_LAST_REQUEST = {}
_LAST_EDIT_TIME = {}
ENTITY_CACHE = {}
OWNER_ENTITY_CACHE = {"entity":None,"expires_at":None}
BOT_ENTITY_CACHE = {}
ENTITY_CACHE_TTL = 3600
OWNER_CACHE_TTL = 7200
RESOLVE_FLOOD_UNTIL = None
admin_client = None
backup_client = None
_start_time = time.time()
bot = TelegramClient("ghost_reaction_bot", API_ID, API_HASH)
USER_STATES = {}


def _dirty():
    try: github_sync.mark_dirty()
    except Exception: pass


def global_exception_handler(loop, context):
    exc = context.get("exception")
    if exc:
        print(f"\n{'─'*60}\n⚠️ GLOBAL: {exc}", flush=True)
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        print(f"{'─'*60}\n", flush=True)


# ══════════════════════ ANIMATIONS ══════════════════════
DIV = "━━━━━━━━━━━━━━━━━━━━━━━━━"
STAR_LINE = "✦ ─────────── ✦ ─────────── ✦"
SPARKLE = "✨"

ANIM_LOAD = ["⏳", "⌛", "⏳", "⌛", "⏳"]
ANIM_WORK = ["🔄", "🔃", "🔄", "🔃"]
ANIM_FIRE = ["🔥", "💥", "⚡", "🌟", "✨", "💫"]
ANIM_HEART = ["❤️", "💖", "💗", "💓", "💕"]
ANIM_GHOST = ["👻", "🎃", "👻", "🌙", "⭐"]
ANIM_SUCCESS = ["⏳", "⌛", "✨", "🌟", "✅"]


def progress_bar(cur, total, width=12):
    if total <= 0: return "░"*width
    f = min(int((cur/total)*width), width)
    return "█"*f + "░"*(width-f)


async def anim_loading(event, msg="Processing"):
    """Play loading animation."""
    for f in ANIM_LOAD[:2]:
        try:
            await event.edit(f"{f} **{msg}...**")
            await asyncio.sleep(0.3)
        except Exception: return


async def anim_success(event, title, subtitle=""):
    """Play success animation."""
    for f in ["⏳", "⌛", "✨", "🌟", "✅"]:
        try:
            await event.edit(f"{f} **{title}**")
            await asyncio.sleep(0.25)
        except Exception: pass
    txt = f"✅ **{title}**"
    if subtitle: txt += f"\n\n{subtitle}"
    try: await event.edit(txt)
    except Exception: pass


async def anim_progress(event, i, total, prefix="⚡", note=""):
    """Animated progress bar."""
    bar = progress_bar(i, total)
    try:
        await event.edit(f"{prefix} `{bar}` **{i}/{total}**\n{note}")
    except Exception: pass


def D(msg, level="info"):
    ts = datetime.now().strftime("%H:%M:%S")
    ic = {"info":"ℹ️ ","ok":"✅","fail":"❌","warn":"⚠️ ","step":"▶️ ","dbg":"🐛",
          "flood":"🌊","rot":"🔄","cycle":"🔁","watch":"📡","ref":"🎁","plan":"💰",
          "lang":"🌍","backup":"🛡️","paid":"💎","pool":"🎯","health":"❤️","queue":"⏰",
          "pay":"💳","team":"👥","bulk":"📦","gh":"🔄","real":"👤","anim":"🎬"}
    print(f"[{ts}] {ic.get(level,'•')} {msg}", flush=True)


def D_sep(t): print(f"\n{'='*60}\n  {t}\n{'='*60}", flush=True)


def D_err(e, ctx=""):
    print(f"\n{'─'*60}\n❌ {ctx}: {e}", flush=True)
    traceback.print_exc()
    print(f"{'─'*60}\n", flush=True)


def get_owner_username(): return cfg_get("owner_username", OWNER_USERNAME_DEFAULT)
def get_owner_id():
    try: return int(cfg_get("owner_id", str(OWNER_ID_DEFAULT)))
    except Exception: return OWNER_ID_DEFAULT
def OWNER_IS(uid): return uid == get_owner_id()


# ══════════════════════ LANGUAGES ══════════════════════
LANG_STRINGS = {
    "en": {"welcome":"Welcome Back","send_reactions":"Send Reactions","auto_watch":"Auto-Watch",
           "templates":"Templates","referral":"Referral","upgrade":"Upgrade","notifications":"Notifications",
           "language":"Language","info":"Info","support":"Support","owner_panel":"Owner Panel",
           "home":"Main Menu","back":"Back","cancel":"Cancel","channel":"Channel","group":"Group",
           "default_emoji":"Default","custom_emoji":"Custom","emoji_packs":"Emoji Packs","send":"Send",
           "choose_language":"Choose Language","language_changed":"Changed","your_limit":"Your limit",
           "per_post":"per post","plan":"Plan","free_plan":"Free Plan","my_watches":"My Watches",
           "add_watch":"Add Watch","contact_owner":"Contact","retry":"Retry","how_many":"How many?",
           "emoji_mode":"Emoji mode","post_link":"Post link","chat_link":"Chat link",
           "count_per_post":"Count per post","chat_type":"Chat type?","my_link":"My Link",
           "stats":"Stats","leaderboard":"Leaderboard","analytics":"Analytics","queue":"Queue",
           "bulk":"Bulk","team":"Team","buy_plan":"Buy Plan","payment":"Payment"},
    "ur": {"welcome":"خوش آمدید","send_reactions":"ری ایکشن بھیجیں","auto_watch":"آٹو واچ","templates":"ٹیمپلیٹس",
           "referral":"ریفرل","upgrade":"اپ گریڈ","notifications":"اطلاعات","language":"زبان","info":"معلومات",
           "support":"سپورٹ","owner_panel":"اونر پینل","home":"مین مینو","back":"واپس","cancel":"کینسل",
           "channel":"چینل","group":"گروپ","default_emoji":"ڈیفالٹ","custom_emoji":"کسٹم","emoji_packs":"پیکس",
           "send":"بھیجیں","choose_language":"زبان منتخب","language_changed":"تبدیل","your_limit":"حد",
           "per_post":"فی پوسٹ","plan":"پلان","free_plan":"مفت","my_watches":"واچز","add_watch":"شامل",
           "contact_owner":"رابطہ","retry":"دوبارہ","how_many":"کتنے؟","emoji_mode":"موڈ",
           "post_link":"پوسٹ لنک","chat_link":"چیٹ لنک","count_per_post":"فی پوسٹ","chat_type":"قسم؟",
           "my_link":"میرا لنک","stats":"اعداد","leaderboard":"لیڈر بورڈ","analytics":"تجزیہ",
           "queue":"قطار","bulk":"بلک","team":"ٹیم","buy_plan":"پلان خریدیں","payment":"ادائیگی"},
    "hi": {"welcome":"स्वागत","send_reactions":"रिएक्शन","auto_watch":"ऑटो","templates":"टेम्पलेट",
           "referral":"रेफरल","upgrade":"अपग्रेड","notifications":"सूचनाएं","language":"भाषा","info":"जानकारी",
           "support":"सहायता","owner_panel":"ओनर","home":"मेनू","back":"वापस","cancel":"रद्द",
           "channel":"चैनल","group":"ग्रुप","default_emoji":"डिफ़ॉल्ट","custom_emoji":"कस्टम","emoji_packs":"पैक",
           "send":"भेजें","choose_language":"भाषा","language_changed":"बदली","your_limit":"सीमा",
           "per_post":"प्रति","plan":"प्लान","free_plan":"फ्री","my_watches":"वॉच","add_watch":"जोड़ें",
           "contact_owner":"संपर्क","retry":"पुनः","how_many":"कितने?","emoji_mode":"मोड",
           "post_link":"लिंक","chat_link":"चैट","count_per_post":"प्रति","chat_type":"टाइप?",
           "my_link":"लिंक","stats":"आंकड़े","leaderboard":"लीडरबोर्ड","analytics":"विश्लेषण",
           "queue":"कतार","bulk":"बल्क","team":"टीम","buy_plan":"खरीदें","payment":"भुगतान"},
    "ar": {"welcome":"مرحباً","send_reactions":"إرسال","auto_watch":"مراقبة","templates":"قوالب",
           "referral":"إحالة","upgrade":"ترقية","notifications":"إشعارات","language":"اللغة","info":"معلومات",
           "support":"دعم","owner_panel":"المالك","home":"الرئيسية","back":"رجوع","cancel":"إلغاء",
           "channel":"قناة","group":"مجموعة","default_emoji":"افتراضي","custom_emoji":"مخصص","emoji_packs":"حزم",
           "send":"إرسال","choose_language":"اختر","language_changed":"تم","your_limit":"حدك",
           "per_post":"لكل","plan":"خطة","free_plan":"مجاني","my_watches":"مراقباتي","add_watch":"إضافة",
           "contact_owner":"اتصل","retry":"إعادة","how_many":"كم؟","emoji_mode":"وضع",
           "post_link":"رابط","chat_link":"رابط","count_per_post":"لكل","chat_type":"نوع؟",
           "my_link":"رابطي","stats":"إحصائيات","leaderboard":"المتصدرون","analytics":"تحليلات",
           "queue":"قائمة","bulk":"جماعي","team":"فريق","buy_plan":"شراء","payment":"دفع"},
    "ru": {"welcome":"Привет","send_reactions":"Реакции","auto_watch":"Авто","templates":"Шаблоны",
           "referral":"Реферал","upgrade":"Обновить","notifications":"Уведомления","language":"Язык","info":"Инфо",
           "support":"Поддержка","owner_panel":"Владелец","home":"Меню","back":"Назад","cancel":"Отмена",
           "channel":"Канал","group":"Группа","default_emoji":"Обычные","custom_emoji":"Свои","emoji_packs":"Наборы",
           "send":"Отправить","choose_language":"Выбрать","language_changed":"Изменён","your_limit":"Лимит",
           "per_post":"на пост","plan":"План","free_plan":"Бесплатно","my_watches":"Наблюдения","add_watch":"Добавить",
           "contact_owner":"Связаться","retry":"Ещё","how_many":"Сколько?","emoji_mode":"Режим",
           "post_link":"Ссылка","chat_link":"Ссылка","count_per_post":"На пост","chat_type":"Тип?",
           "my_link":"Моя ссылка","stats":"Стата","leaderboard":"Топ","analytics":"Аналитика",
           "queue":"Очередь","bulk":"Массово","team":"Команда","buy_plan":"Купить","payment":"Оплата"},
    "es": {"welcome":"Bienvenido","send_reactions":"Enviar","auto_watch":"Auto","templates":"Plantillas",
           "referral":"Referido","upgrade":"Mejorar","notifications":"Notificaciones","language":"Idioma",
           "info":"Info","support":"Soporte","owner_panel":"Dueño","home":"Menú","back":"Atrás","cancel":"Cancelar",
           "channel":"Canal","group":"Grupo","default_emoji":"Predeterminado","custom_emoji":"Personalizado",
           "emoji_packs":"Paquetes","send":"Enviar","choose_language":"Elegir","language_changed":"Cambiado",
           "your_limit":"Límite","per_post":"por post","plan":"Plan","free_plan":"Gratis",
           "my_watches":"Vigilancias","add_watch":"Agregar","contact_owner":"Contactar","retry":"Reintentar",
           "how_many":"¿Cuántas?","emoji_mode":"Modo","post_link":"Enlace","chat_link":"Enlace",
           "count_per_post":"Por post","chat_type":"¿Tipo?","my_link":"Mi enlace","stats":"Stats",
           "leaderboard":"Ranking","analytics":"Análisis","queue":"Cola","bulk":"Masivo","team":"Equipo",
           "buy_plan":"Comprar","payment":"Pago"},
    "id": {"welcome":"Selamat Datang","send_reactions":"Kirim","auto_watch":"Auto","templates":"Template",
           "referral":"Referral","upgrade":"Upgrade","notifications":"Notifikasi","language":"Bahasa",
           "info":"Info","support":"Dukungan","owner_panel":"Pemilik","home":"Menu","back":"Kembali",
           "cancel":"Batal","channel":"Channel","group":"Grup","default_emoji":"Default","custom_emoji":"Kustom",
           "emoji_packs":"Paket","send":"Kirim","choose_language":"Pilih","language_changed":"Diubah",
           "your_limit":"Batas","per_post":"per","plan":"Paket","free_plan":"Gratis",
           "my_watches":"Pantauan","add_watch":"Tambah","contact_owner":"Hubungi","retry":"Coba",
           "how_many":"Berapa?","emoji_mode":"Mode","post_link":"Link","chat_link":"Link",
           "count_per_post":"Per","chat_type":"Tipe?","my_link":"Link","stats":"Statistik",
           "leaderboard":"Ranking","analytics":"Analitik","queue":"Antrian","bulk":"Massal","team":"Tim",
           "buy_plan":"Beli","payment":"Bayar"},
}

WELCOME_TEMPLATES = {
    "en": {"title":"GHOST REACTION BOT","greet":"Welcome","read_first":"IMPORTANT — READ FIRST",
           "warn_line":"Before sending reactions, make the OWNER admin in your channel / group!",
           "owner_lbl":"Owner","owner_id_lbl":"Owner ID","req_perm":"Required Admin Permissions",
           "perm1":"Add New Admins","perm2":"Post Messages","perm3":"Delete Messages","perm4":"Invite Users",
           "howto":"HOW TO ADD ADMIN","step1":"Open your channel/group","step2":"Tap name → Administrators",
           "step3":"Add Admin → search username","step4":"Enable ALL permissions","step5":"Save",
           "your_info":"YOUR INFO","plan":"Plan","limit":"Limit","per_post":"per post","balance":"Balance",
           "autowatch":"Auto-Watch","approved":"Approved","yes":"YES","no":"NO","ready":"✅ Ready! Tap a button"},
    "ur": {"title":"گھوسٹ ری ایکشن بوٹ","greet":"خوش آمدید","read_first":"اہم — پہلے پڑھیں",
           "warn_line":"ری ایکشن بھیجنے سے پہلے اونر کو ایڈمن بنائیں!","owner_lbl":"اونر","owner_id_lbl":"اونر آئی ڈی",
           "req_perm":"ضروری اجازتیں","perm1":"نئے ایڈمن","perm2":"پیغامات","perm3":"حذف","perm4":"مدعو",
           "howto":"ایڈمن کیسے بنائیں","step1":"چینل/گروپ کھولیں","step2":"نام → ایڈمنسٹریٹرز",
           "step3":"ایڈمن → یوزرنیم","step4":"تمام اجازتیں","step5":"محفوظ","your_info":"معلومات",
           "plan":"پلان","limit":"حد","per_post":"فی پوسٹ","balance":"بیلنس","autowatch":"آٹو واچ",
           "approved":"منظور","yes":"جی ہاں","no":"نہیں","ready":"✅ تیار! نیچے بٹن"},
    "hi": {"title":"घोस्ट रिएक्शन बॉट","greet":"स्वागत है","read_first":"महत्वपूर्ण",
           "warn_line":"रिएक्शन से पहले ओनर को एडमिन बनाएं!","owner_lbl":"ओनर","owner_id_lbl":"ओनर ID",
           "req_perm":"अनुमतियाँ","perm1":"एडमिन","perm2":"संदेश","perm3":"हटाएं","perm4":"आमंत्रित",
           "howto":"कैसे","step1":"चैनल खोलें","step2":"नाम → एडमिन","step3":"जोड़ें","step4":"सभी","step5":"सेव",
           "your_info":"जानकारी","plan":"प्लान","limit":"सीमा","per_post":"प्रति","balance":"बैलेंस",
           "autowatch":"ऑटो","approved":"स्वीकृत","yes":"हाँ","no":"नहीं","ready":"✅ तैयार!"},
    "ar": {"title":"بوت التفاعلات","greet":"أهلاً","read_first":"مهم","warn_line":"اجعل المالك مشرفاً!",
           "owner_lbl":"المالك","owner_id_lbl":"معرف","req_perm":"الصلاحيات","perm1":"مشرفين","perm2":"نشر",
           "perm3":"حذف","perm4":"دعوة","howto":"كيفية","step1":"افتح","step2":"اضغط","step3":"أضف",
           "step4":"فعّل","step5":"احفظ","your_info":"معلوماتك","plan":"خطة","limit":"حد","per_post":"لكل",
           "balance":"رصيد","autowatch":"تلقائي","approved":"موافق","yes":"نعم","no":"لا","ready":"✅ جاهز!"},
    "ru": {"title":"ПРИЗРАЧНЫЙ БОТ","greet":"Добро пожаловать","read_first":"ВАЖНО",
           "warn_line":"Сделайте владельца админом!","owner_lbl":"Владелец","owner_id_lbl":"ID",
           "req_perm":"Права","perm1":"Админы","perm2":"Публиковать","perm3":"Удалять","perm4":"Приглашать",
           "howto":"КАК","step1":"Откройте","step2":"Имя","step3":"Добавить","step4":"Все","step5":"Сохранить",
           "your_info":"ИНФО","plan":"План","limit":"Лимит","per_post":"на пост","balance":"Баланс",
           "autowatch":"Авто","approved":"Одобрен","yes":"ДА","no":"НЕТ","ready":"✅ Готово!"},
    "es": {"title":"BOT FANTASMA","greet":"Bienvenido","read_first":"IMPORTANTE",
           "warn_line":"¡Haz al DUEÑO admin!","owner_lbl":"Dueño","owner_id_lbl":"ID","req_perm":"Permisos",
           "perm1":"Admins","perm2":"Publicar","perm3":"Eliminar","perm4":"Invitar","howto":"CÓMO",
           "step1":"Abre","step2":"Nombre","step3":"Añadir","step4":"Todos","step5":"Guardar",
           "your_info":"INFO","plan":"Plan","limit":"Límite","per_post":"por","balance":"Saldo",
           "autowatch":"Auto","approved":"Aprobado","yes":"SÍ","no":"NO","ready":"✅ ¡Listo!"},
    "id": {"title":"BOT HANTU","greet":"Selamat Datang","read_first":"PENTING",
           "warn_line":"Jadikan PEMILIK admin!","owner_lbl":"Pemilik","owner_id_lbl":"ID","req_perm":"Izin",
           "perm1":"Admin","perm2":"Posting","perm3":"Hapus","perm4":"Undang","howto":"CARA",
           "step1":"Buka","step2":"Nama","step3":"Tambah","step4":"Semua","step5":"Simpan",
           "your_info":"INFO","plan":"Paket","limit":"Batas","per_post":"per","balance":"Saldo",
           "autowatch":"Auto","approved":"Disetujui","yes":"YA","no":"TIDAK","ready":"✅ Siap!"},
}


def L(uid, key):
    if not feat_multilang(): return LANG_STRINGS["en"].get(key, key)
    try:
        u = db_get_user_full(uid)
        lang = u[18] if u and len(u) > 18 and u[18] else "en"
        return LANG_STRINGS.get(lang, LANG_STRINGS["en"]).get(key, key)
    except Exception: return LANG_STRINGS["en"].get(key, key)


def WT(uid, key):
    try:
        u = db_get_user_full(uid)
        lang = u[18] if u and len(u) > 18 and u[18] else "en"
        return WELCOME_TEMPLATES.get(lang, WELCOME_TEMPLATES["en"]).get(key, key)
    except Exception: return WELCOME_TEMPLATES["en"].get(key, key)


# ══════════════════════ DATABASE ══════════════════════
def db_init():
    if "/" in DB_FILE: os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, first_name TEXT, username TEXT,
        joined_at TEXT DEFAULT CURRENT_TIMESTAMP, last_active TEXT DEFAULT CURRENT_TIMESTAMP,
        is_banned INTEGER DEFAULT 0, total_reactions INTEGER DEFAULT 0, total_bots INTEGER DEFAULT 0,
        custom_limit INTEGER DEFAULT 0, auto_watch_unlocked INTEGER DEFAULT 0,
        allow_channel INTEGER DEFAULT 1, allow_group INTEGER DEFAULT 1, allow_manual INTEGER DEFAULT 1,
        allow_autowatch INTEGER DEFAULT 0, allow_custom_emoji INTEGER DEFAULT 1,
        plan TEXT DEFAULT 'free', plan_expires TEXT, free_balance INTEGER DEFAULT 0,
        language TEXT DEFAULT 'en', referral_code TEXT, referred_by INTEGER DEFAULT 0,
        referral_count INTEGER DEFAULT 0, referral_earned INTEGER DEFAULT 0,
        team_role TEXT DEFAULT 'user', team_commission INTEGER DEFAULT 0, total_spent INTEGER DEFAULT 0,
        ra_limit_override INTEGER DEFAULT -1)""")
    c.execute("""CREATE TABLE IF NOT EXISTS reactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, chat_title TEXT, chat_id INTEGER,
        post_link TEXT, post_id INTEGER, emoji TEXT, bot_username TEXT, status TEXT,
        method TEXT DEFAULT 'bot', created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS approvals (
        user_id INTEGER PRIMARY KEY, first_name TEXT, username TEXT, status TEXT DEFAULT 'pending',
        requested_at TEXT DEFAULT CURRENT_TIMESTAMP, decided_at TEXT, approved_by INTEGER)""")
    c.execute("""CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS bots (
        token TEXT PRIMARY KEY, username TEXT, bot_id INTEGER, added_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS watchers (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, chat_id INTEGER, chat_title TEXT,
        chat_link TEXT, chat_type TEXT, reaction_count INTEGER DEFAULT 5,
        emoji_mode TEXT DEFAULT 'default', custom_emojis TEXT, last_post_id INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP, last_run TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, emojis TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT, referrer_id INTEGER, new_user_id INTEGER,
        status TEXT DEFAULT 'pending', reward_given INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP, validated_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, message TEXT, is_read INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, chat_link TEXT, post_link TEXT,
        reaction_count INTEGER, emoji_mode TEXT DEFAULT 'default', custom_emojis TEXT,
        scheduled_time TEXT, status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP, executed_at TEXT, error TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS bulk_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, job_type TEXT, total INTEGER DEFAULT 0,
        completed INTEGER DEFAULT 0, failed INTEGER DEFAULT 0, status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP, data TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount INTEGER, plan TEXT, days INTEGER,
        method TEXT, screenshot TEXT, status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP, verified_at TEXT, verified_by INTEGER, notes TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS force_channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT, channel TEXT UNIQUE, url TEXT, name TEXT,
        active INTEGER DEFAULT 1, added_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS team_members (
        user_id INTEGER PRIMARY KEY, role TEXT DEFAULT 'user', permissions TEXT,
        commission_percent INTEGER DEFAULT 0, total_sales INTEGER DEFAULT 0,
        total_commission INTEGER DEFAULT 0, added_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS custom_packs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, emojis TEXT, price INTEGER DEFAULT 0,
        is_paid INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS payment_methods (
        id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT UNIQUE, name TEXT, number TEXT, holder TEXT,
        icon TEXT DEFAULT '💳', instructions TEXT DEFAULT '', active INTEGER DEFAULT 1,
        sort_order INTEGER DEFAULT 0, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    for col, dflt in [("is_banned","INTEGER DEFAULT 0"),("total_reactions","INTEGER DEFAULT 0"),
        ("total_bots","INTEGER DEFAULT 0"),("custom_limit","INTEGER DEFAULT 0"),
        ("auto_watch_unlocked","INTEGER DEFAULT 0"),("allow_channel","INTEGER DEFAULT 1"),
        ("allow_group","INTEGER DEFAULT 1"),("allow_manual","INTEGER DEFAULT 1"),
        ("allow_autowatch","INTEGER DEFAULT 0"),("allow_custom_emoji","INTEGER DEFAULT 1"),
        ("plan","TEXT DEFAULT 'free'"),("plan_expires","TEXT"),("free_balance","INTEGER DEFAULT 0"),
        ("language","TEXT DEFAULT 'en'"),("referral_code","TEXT"),("referred_by","INTEGER DEFAULT 0"),
        ("referral_count","INTEGER DEFAULT 0"),("referral_earned","INTEGER DEFAULT 0"),
        ("team_role","TEXT DEFAULT 'user'"),("team_commission","INTEGER DEFAULT 0"),
        ("total_spent","INTEGER DEFAULT 0"),("ra_limit_override","INTEGER DEFAULT -1")]:
        try: c.execute(f"ALTER TABLE users ADD COLUMN {col} {dflt}")
        except sqlite3.OperationalError: pass

    cfg_defaults = [
        ("owner_username", OWNER_USERNAME_DEFAULT), ("owner_id", str(OWNER_ID_DEFAULT)),
        ("free_count", str(DEFAULT_FREE_COUNT)), ("auto_approve", "0"),
        ("channel_enabled", "1"), ("group_enabled", "1"), ("manual_enabled", "1"),
        ("autowatch_enabled", "1"), ("custom_emoji_enabled", "1"), ("force_join_enabled", "0"),
        ("paid_plans_enabled", "1"), ("referral_enabled", "1"), ("multi_lang_enabled", "1"),
        ("templates_enabled", "1"), ("notifications_enabled", "1"), ("owner_pin_hash", ""),
        ("owner_2fa_enabled", "0"), ("paid_autowatch", "1"), ("paid_custom_emoji", "1"),
        ("paid_templates", "1"), ("paid_multilang", "0"), ("paid_referral", "0"),
        ("paid_balance", "1"), ("paid_channel", "0"), ("paid_group", "0"), ("paid_manual", "0"),
        ("queue_enabled", "1"), ("bulk_enabled", "1"), ("auto_payment_enabled", "1"),
        ("daily_summary_enabled", "1"), ("daily_summary_time", "21:00"), ("team_enabled", "1"),
        ("sales_commission_percent", "10"),
        ("realaccounts_enabled", "1"), ("paid_realaccounts", "1"),
        ("plan_realaccounts_free", "0"), ("plan_realaccounts_basic", "1"),
        ("plan_realaccounts_pro", "1"), ("plan_realaccounts_premium", "1"),
        ("plan_ra_limit_free", "0"), ("plan_ra_limit_basic", "3"),
        ("plan_ra_limit_pro", "8"), ("plan_ra_limit_premium", "20"),
    ]
    for plan, prices in DEFAULT_PRICES.items():
        for days, price in prices.items():
            cfg_defaults.append((f"price_{plan}_{days}", str(price)))
    for k, v in cfg_defaults:
        c.execute("INSERT OR IGNORE INTO config(key, value) VALUES(?, ?)", (k, v))
    conn.commit(); conn.close(); _dirty()
    D(f"DB initialized: {DB_FILE}", "ok")


def cfg_get(k, d=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("SELECT value FROM config WHERE key=?", (k,)).fetchone()
        return r[0] if r else d
    finally: conn.close()


def cfg_set(k, v):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("INSERT OR REPLACE INTO config(key, value) VALUES(?, ?)", (k, str(v)))
        conn.commit()
    finally: conn.close()
    _dirty()


def cfg_bool(k, d=True): return cfg_get(k, "1" if d else "0") == "1"


def cfg_toggle(k):
    n = not cfg_bool(k); cfg_set(k, "1" if n else "0"); return n


def get_plan_price(plan, days):
    try: return int(cfg_get(f"price_{plan}_{days}", "0"))
    except Exception: return 0


def feat_channel(): return cfg_bool("channel_enabled")
def feat_group(): return cfg_bool("group_enabled")
def feat_manual(): return cfg_bool("manual_enabled")
def feat_autowatch(): return cfg_bool("autowatch_enabled")
def feat_custom_emoji(): return cfg_bool("custom_emoji_enabled")
def feat_force_join(): return cfg_bool("force_join_enabled")
def feat_plans(): return cfg_bool("paid_plans_enabled")
def feat_referral(): return cfg_bool("referral_enabled")
def feat_multilang(): return cfg_bool("multi_lang_enabled")
def feat_templates(): return cfg_bool("templates_enabled")
def feat_notifications(): return cfg_bool("notifications_enabled")
def feat_queue(): return cfg_bool("queue_enabled")
def feat_bulk(): return cfg_bool("bulk_enabled")
def feat_payment(): return cfg_bool("auto_payment_enabled")
def feat_daily_summary(): return cfg_bool("daily_summary_enabled")
def feat_team(): return cfg_bool("team_enabled")
def feat_realaccounts(): return cfg_bool("realaccounts_enabled")
def is_paid_feature(f): return cfg_bool(f"paid_{f}", False)
def plan_has_realaccounts(plan): return cfg_bool(f"plan_realaccounts_{plan}", False)


def plan_ra_limit(plan):
    try: return int(cfg_get(f"plan_ra_limit_{plan}", "0"))
    except Exception: return 0


def toggle_plan_realaccounts(plan): return cfg_toggle(f"plan_realaccounts_{plan}")


def get_user_ra_limit(uid):
    if OWNER_IS(uid): return 999, "owner"
    u = db_get_user_full(uid)
    if not u: return 0, "none"
    try: override = u[26] if len(u) > 26 else -1
    except Exception: override = -1
    if override is not None and int(override) >= 0: return int(override), "custom"
    plan = u[15] or "free"
    if plan in PAID_PLANS:
        exp = u[16] if len(u) > 16 else None
        if exp:
            try:
                if datetime.strptime(exp, "%Y-%m-%d %H:%M:%S") < datetime.now(): plan = "free"
            except Exception: pass
    return plan_ra_limit(plan), "plan"


def user_has_realaccounts(uid):
    if OWNER_IS(uid): return True
    if not feat_realaccounts(): return False
    limit, _ = get_user_ra_limit(uid)
    return limit > 0


def set_user_ra_limit(uid, limit):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("UPDATE users SET ra_limit_override=? WHERE user_id=?", (int(limit), uid))
        conn.commit()
    finally: conn.close()
    _dirty()


def user_has_paid_access(uid):
    if OWNER_IS(uid): return True
    u = db_get_user_full(uid)
    if not u or len(u) < 16: return False
    plan = u[15] or "free"
    if plan not in PAID_PLANS: return False
    exp = u[16] if len(u) > 16 else None
    if exp:
        try:
            if datetime.strptime(exp, "%Y-%m-%d %H:%M:%S") < datetime.now(): return False
        except Exception: pass
    return True


def can_use_feature(uid, f):
    if OWNER_IS(uid): return True
    if not is_paid_feature(f): return True
    return user_has_paid_access(uid)


def get_free_count():
    try: return int(cfg_get("free_count", DEFAULT_FREE_COUNT))
    except Exception: return DEFAULT_FREE_COUNT


def is_auto_approve(): return cfg_get("auto_approve", "0") == "1"
def set_auto_approve(v): cfg_set("auto_approve", "1" if v else "0")
def gen_referral_code(uid): return f"REF{uid}{random.randint(1000, 9999)}"


def get_user_limit(uid):
    if OWNER_IS(uid): return MAX_REACTIONS
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("SELECT custom_limit, plan, plan_expires FROM users WHERE user_id=?", (uid,)).fetchone()
    finally: conn.close()
    if not r: return get_free_count()
    cl, plan, pe = r
    if cl and cl > 0: return cl
    if plan and plan in PLAN_LIMITS:
        if pe:
            try:
                if datetime.strptime(pe, "%Y-%m-%d %H:%M:%S") < datetime.now(): return get_free_count()
            except Exception: pass
        return PLAN_LIMITS[plan]
    return get_free_count()


def db_get_user_full(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, first_name, username, joined_at, last_active,
            is_banned, total_reactions, total_bots, custom_limit, auto_watch_unlocked,
            allow_channel, allow_group, allow_manual, allow_autowatch, allow_custom_emoji,
            plan, plan_expires, free_balance, language, referral_code, referred_by,
            referral_count, referral_earned, team_role, team_commission, total_spent,
            ra_limit_override FROM users WHERE user_id=?""", (uid,)).fetchone()
    finally: conn.close()


def db_set_user_perm(uid, feature, value):
    col = {"channel":"allow_channel","group":"allow_group","manual":"allow_manual",
           "autowatch":"allow_autowatch","custom_emoji":"allow_custom_emoji",
           "auto_watch_unlocked":"auto_watch_unlocked"}.get(feature)
    if not col: return False
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute(f"UPDATE users SET {col}=? WHERE user_id=?", (1 if value else 0, uid))
        conn.commit()
    finally: conn.close()
    _dirty(); return True


def db_set_user_lang(uid, lang):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("UPDATE users SET language=? WHERE user_id=?", (lang, uid))
        conn.commit()
    finally: conn.close()
    _dirty()


def db_set_user_plan(uid, plan, days=30):
    exp = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("UPDATE users SET plan=?, plan_expires=? WHERE user_id=?", (plan, exp, uid))
        conn.commit()
    finally: conn.close()
    _dirty()


def db_add_free_balance(uid, amount):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("UPDATE users SET free_balance = free_balance + ? WHERE user_id=?", (amount, uid))
        conn.commit()
    finally: conn.close()
    _dirty()


def db_spend_free_balance(uid, amount):
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("SELECT free_balance FROM users WHERE user_id=?", (uid,)).fetchone()
        if not r or r[0] < amount: return False
        conn.execute("UPDATE users SET free_balance = free_balance - ? WHERE user_id=?", (amount, uid))
        conn.commit(); _dirty(); return True
    finally: conn.close()


def db_add_bot(token, username, bot_id):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("INSERT OR REPLACE INTO bots(token, username, bot_id) VALUES(?, ?, ?)",
                     (token, username, bot_id))
        conn.commit(); _dirty(); return True
    except Exception: return False
    finally: conn.close()


def db_list_bots():
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("SELECT token, username, bot_id, added_at FROM bots ORDER BY added_at ASC").fetchall()
    finally: conn.close()


def db_list_visible_bots():
    return [b for b in db_list_bots() if not is_permanent_admin(b[1])]


def db_count_bots():
    conn = sqlite3.connect(DB_FILE)
    try: return conn.execute("SELECT COUNT(*) FROM bots").fetchone()[0]
    finally: conn.close()


def db_count_visible_bots(): return len(db_list_visible_bots())


def db_save_user(uid, first_name, username=None, referred_by=0):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        ex = c.execute("SELECT referral_code FROM users WHERE user_id=?", (uid,)).fetchone()
        rc = gen_referral_code(uid)
        if ex is None:
            c.execute("""INSERT INTO users (user_id, first_name, username, last_active,
                referral_code, referred_by) VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?)""",
                (uid, first_name, username, rc, referred_by))
        else:
            c.execute("UPDATE users SET first_name=?, username=?, last_active=CURRENT_TIMESTAMP WHERE user_id=?",
                      (first_name, username, uid))
        conn.commit()
    finally: conn.close()
    _dirty()


def db_save_reaction(uid, ct, cid, pl, pid, emoji, bu, status, method="bot"):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            c = conn.cursor()
            c.execute("""INSERT INTO reactions (user_id, chat_title, chat_id, post_link, post_id,
                emoji, bot_username, status, method) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (uid, ct, cid, pl, pid, emoji, bu, status, method))
            if status == "ok":
                c.execute("UPDATE users SET total_reactions = total_reactions + 1 WHERE user_id=?", (uid,))
            conn.commit(); _dirty()
        finally: conn.close()
    except Exception as e: D(f"db_save_reaction: {str(e)[:80]}", "warn")


def db_approval_status(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("SELECT status FROM approvals WHERE user_id=?", (uid,)).fetchone()
        return r[0] if r else None
    finally: conn.close()


def db_has_requested(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("SELECT 1 FROM approvals WHERE user_id=?", (uid,)).fetchone() is not None
    finally: conn.close()


def db_create_approval(uid, fn, un=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("SELECT status FROM approvals WHERE user_id=?", (uid,)).fetchone()
        if r is not None: return False, r[0]
        conn.execute("INSERT INTO approvals (user_id, first_name, username, status) VALUES (?, ?, ?, 'pending')",
                     (uid, fn, un))
        conn.commit(); _dirty(); return True, "created"
    finally: conn.close()


def db_set_approval(uid, status, ab=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        ex = c.execute("SELECT 1 FROM approvals WHERE user_id=?", (uid,)).fetchone()
        if not ex:
            u = c.execute("SELECT first_name, username FROM users WHERE user_id=?", (uid,)).fetchone()
            fn = u[0] if u else "User"
            un = u[1] if u else None
            c.execute("""INSERT INTO approvals (user_id, first_name, username, status, decided_at, approved_by)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)""", (uid, fn, un, status, ab))
        else:
            c.execute("UPDATE approvals SET status=?, decided_at=CURRENT_TIMESTAMP, approved_by=? WHERE user_id=?",
                      (status, ab, uid))
        conn.commit()
    finally: conn.close()
    _dirty()


def db_pending_approvals(l=50):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, first_name, username, requested_at FROM approvals
            WHERE status='pending' ORDER BY requested_at ASC LIMIT ?""", (l,)).fetchall()
    finally: conn.close()


def db_total_users():
    conn = sqlite3.connect(DB_FILE)
    try: return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    finally: conn.close()


def db_total_reactions():
    conn = sqlite3.connect(DB_FILE)
    try: return conn.execute("SELECT COUNT(*) FROM reactions WHERE status='ok'").fetchone()[0]
    finally: conn.close()


def db_reactions_today():
    conn = sqlite3.connect(DB_FILE)
    try:
        t = datetime.now().strftime("%Y-%m-%d")
        return conn.execute("SELECT COUNT(*) FROM reactions WHERE status='ok' AND DATE(created_at)=?", (t,)).fetchone()[0]
    finally: conn.close()


def db_all_users(l=50, o=0):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, first_name, username, joined_at, last_active,
            is_banned, total_reactions, total_bots, custom_limit FROM users
            ORDER BY last_active DESC LIMIT ? OFFSET ?""", (l, o)).fetchall()
    finally: conn.close()


def db_get_user(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, first_name, username, joined_at, last_active,
            is_banned, total_reactions, total_bots, custom_limit FROM users WHERE user_id=?""", (uid,)).fetchone()
    finally: conn.close()


def db_is_banned(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("SELECT is_banned FROM users WHERE user_id=?", (uid,)).fetchone()
        return bool(r and r[0])
    finally: conn.close()


def db_ban_user(uid, ban=True):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("UPDATE users SET is_banned=? WHERE user_id=?", (1 if ban else 0, uid))
        conn.commit(); _dirty(); return True
    finally: conn.close()


def db_set_user_limit(uid, limit):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("UPDATE users SET custom_limit=? WHERE user_id=?", (limit, uid))
        conn.commit(); _dirty(); return True
    finally: conn.close()


def db_recent_reactions(l=20):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT r.user_id, u.first_name, r.chat_title, r.post_id, r.emoji,
            r.bot_username, r.status, r.created_at, r.method FROM reactions r
            LEFT JOIN users u ON u.user_id = r.user_id ORDER BY r.id DESC LIMIT ?""", (l,)).fetchall()
    finally: conn.close()


def db_approved_users(l=100):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, first_name, username, decided_at, approved_by
            FROM approvals WHERE status='approved' ORDER BY decided_at DESC LIMIT ?""", (l,)).fetchall()
    finally: conn.close()


def db_add_watcher(u, ci, ct, cl, cty, rc=5, em="default", ce=None, lp=0):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        es = ",".join(ce) if ce else None
        c.execute("""INSERT INTO watchers (user_id, chat_id, chat_title, chat_link, chat_type,
            reaction_count, emoji_mode, custom_emojis, last_post_id, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""", (u, ci, ct, cl, cty, rc, em, es, lp))
        conn.commit(); _dirty(); return c.lastrowid
    finally: conn.close()


def db_list_watchers(uid=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        sql = """SELECT id, user_id, chat_id, chat_title, chat_link, chat_type, reaction_count,
            emoji_mode, custom_emojis, last_post_id, is_active, created_at, last_run FROM watchers"""
        if uid: return conn.execute(sql + " WHERE user_id=? ORDER BY id DESC", (uid,)).fetchall()
        return conn.execute(sql + " ORDER BY id DESC").fetchall()
    finally: conn.close()


def db_get_watcher(wid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT id, user_id, chat_id, chat_title, chat_link, chat_type,
            reaction_count, emoji_mode, custom_emojis, last_post_id, is_active, created_at,
            last_run FROM watchers WHERE id=?""", (wid,)).fetchone()
    finally: conn.close()


def db_update_watcher(wid, **kw):
    if not kw: return False
    fs, vs = [], []
    for k, v in kw.items(): fs.append(f"{k}=?"); vs.append(v)
    vs.append(wid)
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute(f"UPDATE watchers SET {', '.join(fs)} WHERE id=?", tuple(vs))
        conn.commit(); _dirty(); return True
    finally: conn.close()


def db_delete_watcher(wid):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("DELETE FROM watchers WHERE id=?", (wid,)); conn.commit(); _dirty(); return True
    finally: conn.close()


def db_add_template(uid, name, emojis):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("INSERT INTO templates (user_id, name, emojis) VALUES (?, ?, ?)",
                  (uid, name, ",".join(emojis)))
        conn.commit(); _dirty(); return c.lastrowid
    finally: conn.close()


def db_list_templates(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("SELECT id, name, emojis FROM templates WHERE user_id=? ORDER BY id DESC", (uid,)).fetchall()
    finally: conn.close()


def db_delete_template(tid, uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("DELETE FROM templates WHERE id=? AND user_id=?", (tid, uid)); conn.commit(); _dirty()
    finally: conn.close()


def db_get_referral_code(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("SELECT referral_code FROM users WHERE user_id=?", (uid,)).fetchone()
        return r[0] if r else None
    finally: conn.close()


def db_find_user_by_ref_code(code):
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("SELECT user_id FROM users WHERE referral_code=?", (code,)).fetchone()
        return r[0] if r else None
    finally: conn.close()


def db_add_referral(rid, nid):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        if c.execute("SELECT 1 FROM referrals WHERE new_user_id=?", (nid,)).fetchone(): return False
        c.execute("INSERT INTO referrals (referrer_id, new_user_id, status) VALUES (?, ?, 'pending')", (rid, nid))
        conn.commit(); _dirty(); return True
    finally: conn.close()


def db_validate_referral(nid):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        r = c.execute("SELECT id, referrer_id FROM referrals WHERE new_user_id=? AND status='pending'", (nid,)).fetchone()
        if not r: return None
        rid, ref = r
        c.execute("UPDATE referrals SET status='validated', reward_given=1, validated_at=CURRENT_TIMESTAMP WHERE id=?", (rid,))
        c.execute("""UPDATE users SET referral_count = referral_count + 1,
            referral_earned = referral_earned + ?, free_balance = free_balance + ? WHERE user_id=?""",
            (REFERRAL_REWARD + FRIEND_VALID_REWARD, REFERRAL_REWARD + FRIEND_VALID_REWARD, ref))
        c.execute("UPDATE users SET free_balance = free_balance + ? WHERE user_id=?", (FRIEND_VALID_REWARD, nid))
        conn.commit(); _dirty(); return ref
    finally: conn.close()


def db_get_referral_stats(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("SELECT referral_count, referral_earned FROM users WHERE user_id=?", (uid,)).fetchone()
        return (r[0] or 0, r[1] or 0) if r else (0, 0)
    finally: conn.close()


def db_add_notification(uid, msg):
    if not feat_notifications(): return
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            conn.execute("INSERT INTO notifications (user_id, message) VALUES (?, ?)", (uid, msg))
            conn.commit(); _dirty()
        finally: conn.close()
    except Exception: pass


def db_get_notifications(uid, l=10):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("SELECT id, message, is_read, created_at FROM notifications WHERE user_id=? ORDER BY id DESC LIMIT ?", (uid, l)).fetchall()
    finally: conn.close()


def db_mark_notifications_read(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("UPDATE notifications SET is_read=1 WHERE user_id=?", (uid,)); conn.commit(); _dirty()
    finally: conn.close()


def db_add_queue(uid, cl, pl, rc, em="default", ce=None, st=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        es = ",".join(ce) if ce else None
        c.execute("""INSERT INTO queue (user_id, chat_link, post_link, reaction_count,
            emoji_mode, custom_emojis, scheduled_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')""", (uid, cl, pl, rc, em, es, st))
        conn.commit(); _dirty(); return c.lastrowid
    finally: conn.close()


def db_list_queue(user_id=None, status=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        base = """SELECT id, user_id, chat_link, post_link, reaction_count, emoji_mode,
            custom_emojis, scheduled_time, status, created_at, executed_at, error FROM queue"""
        if user_id and status:
            return conn.execute(base + " WHERE user_id=? AND status=? ORDER BY id DESC", (user_id, status)).fetchall()
        if user_id:
            return conn.execute(base + " WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
        if status:
            return conn.execute(base + " WHERE status=? ORDER BY scheduled_time ASC", (status,)).fetchall()
        return conn.execute(base + " ORDER BY id DESC").fetchall()
    finally: conn.close()


def db_update_queue(qid, **kw):
    if not kw: return False
    fs, vs = [], []
    for k, v in kw.items(): fs.append(f"{k}=?"); vs.append(v)
    vs.append(qid)
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute(f"UPDATE queue SET {', '.join(fs)} WHERE id=?", tuple(vs))
        conn.commit(); _dirty(); return True
    finally: conn.close()


def db_delete_queue(qid, uid=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        if uid: conn.execute("DELETE FROM queue WHERE id=? AND user_id=?", (qid, uid))
        else: conn.execute("DELETE FROM queue WHERE id=?", (qid,))
        conn.commit(); _dirty()
    finally: conn.close()


def db_add_payment(uid, amt, plan, days, method, ss=""):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("""INSERT INTO payments (user_id, amount, plan, days, method, screenshot, status)
            VALUES (?, ?, ?, ?, ?, ?, 'pending')""", (uid, amt, plan, days, method, ss))
        conn.commit(); _dirty(); return c.lastrowid
    finally: conn.close()


def db_list_payments(user_id=None, status=None, l=50):
    conn = sqlite3.connect(DB_FILE)
    try:
        base = """SELECT id, user_id, amount, plan, days, method, screenshot, status,
            created_at, verified_at, verified_by, notes FROM payments"""
        if user_id and status:
            return conn.execute(base + " WHERE user_id=? AND status=? ORDER BY id DESC LIMIT ?", (user_id, status, l)).fetchall()
        if status:
            return conn.execute(base + " WHERE status=? ORDER BY id DESC LIMIT ?", (status, l)).fetchall()
        if user_id:
            return conn.execute(base + " WHERE user_id=? ORDER BY id DESC LIMIT ?", (user_id, l)).fetchall()
        return conn.execute(base + " ORDER BY id DESC LIMIT ?", (l,)).fetchall()
    finally: conn.close()


def db_get_payment(pid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT id, user_id, amount, plan, days, method, screenshot, status,
            created_at, verified_at, verified_by, notes FROM payments WHERE id=?""", (pid,)).fetchone()
    finally: conn.close()


def db_update_payment(pid, **kw):
    if not kw: return False
    fs, vs = [], []
    for k, v in kw.items(): fs.append(f"{k}=?"); vs.append(v)
    vs.append(pid)
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute(f"UPDATE payments SET {', '.join(fs)} WHERE id=?", tuple(vs))
        conn.commit(); _dirty(); return True
    finally: conn.close()


def db_add_bulk_job(uid, jt, total, data=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("INSERT INTO bulk_jobs (user_id, job_type, total, data) VALUES (?, ?, ?, ?)",
                  (uid, jt, total, data))
        conn.commit(); _dirty(); return c.lastrowid
    finally: conn.close()


def db_update_bulk_job(jid, **kw):
    if not kw: return False
    fs, vs = [], []
    for k, v in kw.items(): fs.append(f"{k}=?"); vs.append(v)
    vs.append(jid)
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute(f"UPDATE bulk_jobs SET {', '.join(fs)} WHERE id=?", tuple(vs))
        conn.commit(); _dirty(); return True
    finally: conn.close()


def db_list_force_channels(only_active=True):
    conn = sqlite3.connect(DB_FILE)
    try:
        if only_active:
            return conn.execute("SELECT id, channel, url, name, active FROM force_channels WHERE active=1 ORDER BY id ASC").fetchall()
        return conn.execute("SELECT id, channel, url, name, active FROM force_channels ORDER BY id ASC").fetchall()
    finally: conn.close()


def db_add_force_channel(ch, url, name):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("INSERT OR REPLACE INTO force_channels (channel, url, name, active) VALUES (?, ?, ?, 1)",
                     (ch, url, name))
        conn.commit(); _dirty(); return True
    finally: conn.close()


def db_delete_force_channel(fid):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("DELETE FROM force_channels WHERE id=?", (fid,)); conn.commit(); _dirty()
    finally: conn.close()


def db_toggle_force_channel(fid):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("UPDATE force_channels SET active = 1 - active WHERE id=?", (fid,)); conn.commit(); _dirty()
    finally: conn.close()


def db_list_team():
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, role, permissions, commission_percent,
            total_sales, total_commission, added_at FROM team_members ORDER BY added_at DESC""").fetchall()
    finally: conn.close()


def db_add_team_member(uid, role="reseller", comm=10):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO team_members (user_id, role, commission_percent) VALUES (?, ?, ?)",
                  (uid, role, comm))
        c.execute("UPDATE users SET team_role=?, team_commission=? WHERE user_id=?", (role, comm, uid))
        conn.commit(); _dirty(); return True
    finally: conn.close()


def db_remove_team_member(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("DELETE FROM team_members WHERE user_id=?", (uid,))
        c.execute("UPDATE users SET team_role='user', team_commission=0 WHERE user_id=?", (uid,))
        conn.commit(); _dirty()
    finally: conn.close()


def db_get_team_member(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, role, permissions, commission_percent, total_sales,
            total_commission, added_at FROM team_members WHERE user_id=?""", (uid,)).fetchone()
    finally: conn.close()


def db_list_custom_packs():
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("SELECT id, name, emojis, price, is_paid FROM custom_packs ORDER BY id DESC").fetchall()
    finally: conn.close()


def db_add_custom_pack(name, emojis, price=0, is_paid=0):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("INSERT INTO custom_packs (name, emojis, price, is_paid) VALUES (?, ?, ?, ?)",
                  (name, ",".join(emojis), price, is_paid))
        conn.commit(); _dirty(); return c.lastrowid
    finally: conn.close()


def db_delete_custom_pack(pid):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("DELETE FROM custom_packs WHERE id=?", (pid,)); conn.commit(); _dirty()
    finally: conn.close()


def db_payment_list(active_only=True):
    conn = sqlite3.connect(DB_FILE)
    try:
        sql = """SELECT id, key, name, number, holder, icon, instructions, active, sort_order
            FROM payment_methods"""
        if active_only:
            return conn.execute(sql + " WHERE active=1 ORDER BY sort_order ASC, id ASC").fetchall()
        return conn.execute(sql + " ORDER BY sort_order ASC, id ASC").fetchall()
    finally: conn.close()


def db_payment_get(pid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT id, key, name, number, holder, icon, instructions,
            active, sort_order FROM payment_methods WHERE id=?""", (pid,)).fetchone()
    finally: conn.close()


def db_payment_add(key, name, number, holder, icon="💳", instructions="", active=1):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("""INSERT OR REPLACE INTO payment_methods (key, name, number, holder, icon,
            instructions, active) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (key, name, number, holder, icon, instructions, active))
        conn.commit(); _dirty()
        r = c.execute("SELECT id FROM payment_methods WHERE key=?", (key,)).fetchone()
        return r[0] if r else None
    finally: conn.close()


def db_payment_update(pid, **kw):
    if not kw: return False
    fs, vs = [], []
    for k, v in kw.items(): fs.append(f"{k}=?"); vs.append(v)
    vs.append(pid)
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute(f"UPDATE payment_methods SET {', '.join(fs)} WHERE id=?", tuple(vs))
        conn.commit(); _dirty(); return True
    finally: conn.close()


def db_payment_delete(pid):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("DELETE FROM payment_methods WHERE id=?", (pid,)); conn.commit(); _dirty()
    finally: conn.close()


def db_payment_toggle(pid):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("UPDATE payment_methods SET active = 1 - active WHERE id=?", (pid,)); conn.commit(); _dirty()
    finally: conn.close()


def db_reactions_by_day(days=7):
    conn = sqlite3.connect(DB_FILE)
    try:
        res = []
        for i in range(days-1, -1, -1):
            d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            n = conn.execute("SELECT COUNT(*) FROM reactions WHERE status='ok' AND DATE(created_at)=?", (d,)).fetchone()[0]
            res.append((d, n))
        return res
    finally: conn.close()


def db_top_users_by_reactions(l=10):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("SELECT user_id, first_name, total_reactions FROM users WHERE total_reactions > 0 ORDER BY total_reactions DESC LIMIT ?", (l,)).fetchall()
    finally: conn.close()


def db_top_groups(l=10):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT chat_title, chat_id, COUNT(*) as cnt FROM reactions
            WHERE status='ok' GROUP BY chat_id ORDER BY cnt DESC LIMIT ?""", (l,)).fetchall()
    finally: conn.close()


def db_revenue_stats():
    conn = sqlite3.connect(DB_FILE)
    try:
        t = datetime.now().strftime("%Y-%m-%d")
        m = datetime.now().strftime("%Y-%m")
        tot = conn.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='approved'").fetchone()[0]
        tr = conn.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='approved' AND DATE(created_at)=?", (t,)).fetchone()[0]
        mr = conn.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='approved' AND strftime('%Y-%m', created_at)=?", (m,)).fetchone()[0]
        return tot, tr, mr
    finally: conn.close()


# ══════════════════════ REAL ACCOUNTS ══════════════════════
def discover_session_files():
    if not os.path.isdir(SESSIONS_DIR): return []
    try:
        return sorted([f for f in os.listdir(SESSIONS_DIR) if f.endswith(".session")])
    except Exception: return []


def is_real_flooded(sf):
    u = REAL_FLOOD_UNTIL.get(sf)
    if u is None: return False
    if datetime.now() >= u: REAL_FLOOD_UNTIL.pop(sf, None); return False
    return True


def mark_real_flooded(sf, sec): REAL_FLOOD_UNTIL[sf] = datetime.now() + timedelta(seconds=sec)


def real_count_available():
    return sum(1 for f in discover_session_files() if not is_real_flooded(f))


async def get_real_client(sf):
    async with REAL_CLIENT_LOCK:
        if sf in REAL_CLIENTS:
            c = REAL_CLIENTS[sf]
            try:
                if c.is_connected(): return c
            except Exception: pass
            try: await c.disconnect()
            except Exception: pass
            REAL_CLIENTS.pop(sf, None)
        path = os.path.join(SESSIONS_DIR, sf.replace(".session", ""))
        if not os.path.exists(path + ".session"): return None
        try:
            client = TelegramClient(path, API_ID, API_HASH)
            await asyncio.wait_for(client.connect(), timeout=25)
            if not await client.is_user_authorized():
                await client.disconnect(); return None
            REAL_CLIENTS[sf] = client
            return client
        except Exception as e:
            D(f"Real login fail {sf}: {str(e)[:80]}", "warn")
            return None


async def real_send_reaction(sf, chat_ref, msg_id, emoji):
    if is_real_flooded(sf): return False, "flooded", 0
    client = await get_real_client(sf)
    if not client: return False, "login_failed", 0
    try:
        entity = await asyncio.wait_for(client.get_entity(chat_ref), timeout=20)
        await asyncio.wait_for(client(SendReactionRequest(
            peer=entity, msg_id=msg_id, reaction=[ReactionEmoji(emoticon=emoji)])), timeout=20)
        return True, "", 0
    except FloodWaitError as e: return False, "flood", e.seconds
    except Exception as e: return False, str(e)[:100], 0


async def send_reactions_real(chat_ref, msg_id, count, emoji_pool=None, on_progress=None):
    files = discover_session_files()
    if not files: return {"ok": 0, "fail": 0, "flooded": 0, "total": 0}
    available = [f for f in files if not is_real_flooded(f)]
    if not available: return {"ok": 0, "fail": 0, "flooded": 0, "total": 0}
    random.shuffle(available)
    senders = available[:min(count, len(available))]
    if emoji_pool:
        valid = [e for e in emoji_pool if e in ALL_REACTIONS]
        emojis = valid if valid else DEFAULT_REACTIONS
    else:
        emojis = DEFAULT_REACTIONS + ["🥰","😍","💯","🎉","😎","👏"]
    ok = fail = flooded = 0
    total = len(senders)
    for i, sf in enumerate(senders, 1):
        emoji = random.choice(emojis)
        success, err, wait = await real_send_reaction(sf, chat_ref, msg_id, emoji)
        if success: ok += 1
        elif wait > 0:
            flooded += 1; mark_real_flooded(sf, wait + 10)
        else: fail += 1
        if on_progress:
            try: await on_progress(i, total, ok)
            except Exception: pass
        await asyncio.sleep(REAL_COOLDOWN)
    return {"ok": ok, "fail": fail, "flooded": flooded, "total": total}


async def close_all_real_clients():
    for sf, c in list(REAL_CLIENTS.items()):
        try: await c.disconnect()
        except Exception: pass
    REAL_CLIENTS.clear()


# ══════════════════════ BOT API ══════════════════════
def bot_get_me(token):
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10).json()
        return r.get("result") if r.get("ok") else None
    except Exception: return None


def bot_reaction(token, chat_id, msg_id, emoji):
    url = f"https://api.telegram.org/bot{token}/setMessageReaction"
    payload = {"chat_id": chat_id, "message_id": msg_id,
               "reaction": [{"type": "emoji", "emoji": emoji}]}
    try:
        r = requests.post(url, json=payload, timeout=15).json()
        if r.get("ok"): return True, "", 0
        desc = r.get("description", "")
        retry = 0
        m = re.search(r"retry after (\d+)", desc, re.IGNORECASE)
        if m: retry = int(m.group(1)) + FLOOD_SAFETY
        elif "Too Many Requests" in desc or "FLOOD" in desc.upper(): retry = 30
        return False, desc, retry
    except Exception as e: return False, str(e), 0


def bot_send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
                          timeout=10).json()
        return r.get("ok", False), r.get("description", "")
    except Exception as e: return False, str(e)


def bot_send_photo(token, chat_id, photo_url, caption=""):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "photo": photo_url,
                                      "caption": caption, "parse_mode": "HTML"}, timeout=15).json()
        return r.get("ok", False), r.get("description", "")
    except Exception as e: return False, str(e)


def sync_bots():
    ex = {r[0] for r in db_list_bots()}
    added = 0
    for tok in BOT_TOKENS:
        if tok in ex: continue
        info = bot_get_me(tok)
        if info and db_add_bot(tok, info["username"], info["id"]):
            added += 1; ex.add(tok)
    return db_list_bots(), added


def parse_channel_link(link):
    link = link.strip()
    if "t.me/+" in link: return None, link.split("+")[-1].split("?")[0]
    if "t.me/" in link:
        u = link.split("t.me/")[-1].split("/")[0].split("?")[0]
        if u.startswith("+"): return None, u.lstrip("+")
        return f"@{u}", None
    if link.startswith("@"): return link, None
    if link.lstrip("-").isdigit(): return int(link), None
    return link, None


def parse_post_link(link):
    link = link.strip()
    m = re.match(r"https?://t\.me/c/(\d+)/(\d+)", link)
    if m: return int("-100" + m.group(1)), int(m.group(2))
    m = re.match(r"https?://t\.me/([^/]+)/(\d+)", link)
    if m: return f"@{m.group(1)}", int(m.group(2))
    m = re.match(r"t\.me/([^/]+)/(\d+)", link)
    if m: return f"@{m.group(1)}", int(m.group(2))
    return None, None


def btn(text, data=None, url=None, style=None):
    b = Button.url(text, url) if url else Button.inline(text, data)
    if style and HAS_BUTTON_STYLE and KeyboardButtonStyle is not None:
        try:
            if style == "primary": b.style = KeyboardButtonStyle(bg_primary=True)
            elif style == "success": b.style = KeyboardButtonStyle(bg_success=True)
            elif style == "danger": b.style = KeyboardButtonStyle(bg_danger=True)
        except Exception: pass
    return b


# ══════════════════════ SAFE EDIT / ENTITY ══════════════════════
async def safe_edit(event, text, buttons=None, alert=None):
    try:
        if alert:
            try: await event.answer(alert, alert=True)
            except Exception: pass
        key = getattr(event, "chat_id", 0)
        now = time.time()
        wait = 1.5 - (now - _LAST_EDIT_TIME.get(key, 0))
        if 0 < wait < 5: await asyncio.sleep(wait)
        if buttons is not None: await event.edit(text, buttons=buttons)
        else: await event.edit(text)
        _LAST_EDIT_TIME[key] = time.time()
        return True
    except MessageNotModifiedError: return True
    except MessageIdInvalidError:
        try:
            if buttons is not None:
                await event.client.send_message(event.chat_id, text, buttons=buttons)
            else:
                await event.client.send_message(event.chat_id, text)
            return True
        except Exception: return False
    except FloodWaitError as e:
        await asyncio.sleep(min(e.seconds, 30)); return False
    except Exception as e:
        D(f"safe_edit: {str(e)[:80]}", "warn"); return False


async def safe_get_entity(ref, cache_key=None, cache_store=None):
    global RESOLVE_FLOOD_UNTIL
    if RESOLVE_FLOOD_UNTIL and datetime.now() < RESOLVE_FLOOD_UNTIL:
        raise Exception("Resolve flood")
    if cache_key is None: cache_key = str(ref)
    if cache_store is None: cache_store = ENTITY_CACHE
    now = datetime.now()
    cached = cache_store.get(cache_key)
    if cached:
        entity, expires_at = cached
        if now < expires_at: return entity
        cache_store.pop(cache_key, None)
    try:
        entity = await asyncio.wait_for(admin_client.get_entity(ref), timeout=15)
        cache_store[cache_key] = (entity, now + timedelta(seconds=ENTITY_CACHE_TTL))
        return entity
    except FloodWaitError as e:
        wait_sec = min(e.seconds + 10, 3600)
        if backup_client:
            try:
                entity = await asyncio.wait_for(backup_client.get_entity(ref), timeout=15)
                cache_store[cache_key] = (entity, now + timedelta(seconds=ENTITY_CACHE_TTL))
                return entity
            except Exception: pass
        RESOLVE_FLOOD_UNTIL = now + timedelta(seconds=wait_sec)
        raise Exception(f"Wait {wait_sec}s")
    except Exception:
        if backup_client:
            try:
                entity = await asyncio.wait_for(backup_client.get_entity(ref), timeout=15)
                cache_store[cache_key] = (entity, now + timedelta(seconds=ENTITY_CACHE_TTL))
                return entity
            except Exception: pass
        raise


async def safe_get_owner_entity():
    global RESOLVE_FLOOD_UNTIL
    now = datetime.now()
    if RESOLVE_FLOOD_UNTIL and now < RESOLVE_FLOOD_UNTIL: raise Exception("Flood")
    cached = OWNER_ENTITY_CACHE.get("entity")
    exp = OWNER_ENTITY_CACHE.get("expires_at")
    if cached and exp and now < exp: return cached
    owner_uname = get_owner_username()
    entity = None
    try:
        entity = await asyncio.wait_for(admin_client.get_entity(owner_uname), timeout=15)
    except Exception:
        if backup_client:
            try: entity = await asyncio.wait_for(backup_client.get_entity(owner_uname), timeout=15)
            except Exception: pass
    if not entity: raise Exception("Could not resolve owner")
    OWNER_ENTITY_CACHE["entity"] = entity
    OWNER_ENTITY_CACHE["expires_at"] = now + timedelta(seconds=OWNER_CACHE_TTL)
    return entity


def to_bot_api_chat_id(chat_id):
    s = str(chat_id)
    if s.startswith("-100"): return s
    if s.startswith("-"): return "-100" + s.lstrip("-")
    return "-100" + s


def is_channel(entity): return isinstance(entity, Channel) and getattr(entity, 'broadcast', False)
def is_group(entity):
    if isinstance(entity, Chat): return True
    if isinstance(entity, Channel) and getattr(entity, 'megagroup', False): return True
    return False


def is_permanent_admin(username):
    return bool(username and username in PERMANENT_ADMIN_BOTS)


# ══════════════════════ POOL ══════════════════════
def is_bot_flooded(token):
    u = FLOOD_UNTIL.get(token)
    if u is None: return False
    if datetime.now() >= u: FLOOD_UNTIL.pop(token, None); return False
    return True


def mark_bot_flooded(token, sec): FLOOD_UNTIL[token] = datetime.now() + timedelta(seconds=sec)


def cleanup_bot_pool():
    now = datetime.now(); stale = []
    ft = now - timedelta(minutes=BOT_BUSY_TIMEOUT + 1)
    for tok, info in list(BOT_POOL.items()):
        if not isinstance(info, dict): stale.append(tok); continue
        bu = info.get("busy_until"); lu = info.get("last_used")
        if bu and bu < now: stale.append(tok); continue
        if lu and lu < ft: stale.append(tok); continue
    for tok in stale: BOT_POOL.pop(tok, None)
    for tok in list(FLOOD_UNTIL.keys()):
        if FLOOD_UNTIL[tok] < now: FLOOD_UNTIL.pop(tok, None)
    return len(stale)


async def acquire_bots(count, uid):
    async with BOT_POOL_LOCK:
        cleanup_bot_pool()
        bots = db_list_bots(); now = datetime.now(); free = []
        for tok, uname, bid, added in bots:
            if is_permanent_admin(uname): continue
            if is_bot_flooded(tok): continue
            info = BOT_POOL.get(tok)
            bu = info.get("busy_until") if isinstance(info, dict) else None
            if bu is None or now >= bu: free.append((tok, uname))
            if len(free) >= count: break
        if free:
            for tok, uname in free:
                BOT_POOL[tok] = {"username": uname,
                                 "busy_until": now + timedelta(minutes=BOT_BUSY_TIMEOUT),
                                 "last_used": now}
            return free, 0
        return None, 30


async def release_bots(bl):
    async with BOT_POOL_LOCK:
        now = datetime.now()
        for tok, uname in bl:
            info = BOT_POOL.get(tok)
            if info:
                info["busy_until"] = now; info["last_used"] = now


# ══════════════════════ CHECKS ══════════════════════
async def is_joined(uid):
    if not feat_force_join() or OWNER_IS(uid): return True
    channels = db_list_force_channels(only_active=True)
    if not channels: return True
    for fc in channels:
        try:
            await asyncio.wait_for(bot.get_permissions(fc[1], uid), timeout=8); continue
        except Exception: pass
        try:
            await asyncio.wait_for(admin_client(GetParticipantRequest(
                channel=fc[1], participant=uid)), timeout=8); continue
        except Exception: return False
    return True


def is_approved(uid):
    if OWNER_IS(uid): return True
    if db_is_banned(uid): return False
    return db_approval_status(uid) == "approved"


async def is_admin_in(entity, user_id):
    try:
        perms = await asyncio.wait_for(admin_client.get_permissions(entity, user_id), timeout=10)
        if perms is None: return False
        return getattr(perms, 'is_admin', False)
    except Exception: return False


async def check_owner_admin(entity):
    try:
        oe = await safe_get_owner_entity()
        return await is_admin_in(entity, oe.id)
    except Exception: return False


async def get_current_admin_bots(entity):
    admins = []
    try:
        result = await asyncio.wait_for(admin_client(GetParticipantsRequest(
            channel=entity, filter=ChannelParticipantsAdmins(),
            offset=0, limit=200, hash=0)), timeout=20)
        for u in result.users:
            if getattr(u, 'bot', False) and u.username:
                admins.append((u.username, u.id))
    except Exception: pass
    return admins


async def remove_admin_rights(entity, user_id, username):
    if is_permanent_admin(username): return True
    empty = ChatAdminRights(change_info=False, post_messages=False, edit_messages=False,
                            delete_messages=False, ban_users=False, invite_users=False,
                            pin_messages=False, add_admins=False, anonymous=False,
                            manage_call=False, other=False)
    try:
        await asyncio.wait_for(admin_client(EditAdminRequest(
            channel=entity, user_id=user_id, admin_rights=empty, rank="")), timeout=15)
        return True
    except Exception: return False


async def make_bot_admin(entity, bot_entity, atype):
    if atype == "channel":
        rights = ChatAdminRights(change_info=False, post_messages=True, edit_messages=False,
                                 delete_messages=True, ban_users=False, invite_users=False,
                                 pin_messages=False, add_admins=False, anonymous=False,
                                 manage_call=False, other=False)
    else:
        rights = ChatAdminRights(change_info=True, post_messages=True, edit_messages=False,
                                 delete_messages=True, ban_users=True, invite_users=True,
                                 pin_messages=True, add_admins=False, anonymous=False,
                                 manage_call=True, other=False)
    try:
        await asyncio.wait_for(admin_client(EditAdminRequest(
            channel=entity, user_id=bot_entity, admin_rights=rights, rank="")), timeout=15)
        return True, "promoted"
    except Exception as e:
        m = str(e).lower()
        if "already" in m: return True, "already_admin"
        if "too many admins" in m: return False, "too_many_admins"
        return False, f"admin: {str(e)[:60]}"


async def add_one_bot(entity, bot_token, atype, ck):
    info = bot_get_me(bot_token)
    if not info: return False, "invalid"
    username = info["username"]
    try:
        be = await safe_get_entity(username, cache_key=f"bot:{username}", cache_store=BOT_ENTITY_CACHE)
    except Exception as e: return False, f"resolve: {str(e)[:40]}"
    if atype == "channel":
        if await is_admin_in(entity, be.id): return True, "already_admin"
        return await make_bot_admin(entity, be, "channel")
    else:
        try:
            await asyncio.wait_for(admin_client(GetParticipantRequest(
                channel=entity, participant=be.id)), timeout=10)
        except UserNotParticipantError:
            try:
                await asyncio.wait_for(admin_client(InviteToChannelRequest(
                    channel=entity, users=[be])), timeout=15)
                await asyncio.sleep(2)
            except Exception:
                try:
                    await asyncio.wait_for(admin_client(AddChatUserRequest(
                        chat_id=entity.id, user_id=be, fwd_limit=10)), timeout=15)
                    await asyncio.sleep(2)
                except Exception as e: return False, f"invite: {str(e)[:40]}"
        except Exception: pass
        if await is_admin_in(entity, be.id): return True, "already_admin"
        return await make_bot_admin(entity, be, "group")


async def ensure_owner_admin(entity, ck):
    if ck and ADMIN_CACHE.get(ck, {}).get("owner_done"): return True, "cached"
    try:
        oe = await safe_get_owner_entity(); oid = oe.id
    except Exception as e: return False, f"owner: {str(e)[:40]}"
    if await is_admin_in(entity, oid):
        if ck: ADMIN_CACHE.setdefault(ck, {})["owner_done"] = True
        return True, "already"
    rights = ChatAdminRights(change_info=True, post_messages=True, edit_messages=True,
                             delete_messages=True, ban_users=True, invite_users=True,
                             pin_messages=True, add_admins=True, anonymous=False,
                             manage_call=True, other=True)
    try:
        fresh = await safe_get_owner_entity()
        await asyncio.wait_for(admin_client(EditAdminRequest(
            channel=entity, user_id=fresh, admin_rights=rights, rank="")), timeout=15)
        if ck: ADMIN_CACHE.setdefault(ck, {})["owner_done"] = True
        return True, "promoted"
    except Exception as e:
        m = str(e).lower()
        if "already" in m: return True, "already"
        return False, f"owner: {str(e)[:50]}"


async def send_reactions(chat_id, msg_id, bl, ct, pl, uid, count, em="default", ce=None):
    if count > len(bl): count = len(bl)
    senders = bl[:count]; random.shuffle(senders)
    pool = list(ce) if (em == "custom" and ce) else ALL_REACTIONS.copy()
    random.shuffle(pool)
    ok = skip = 0; api = to_bot_api_chat_id(chat_id)
    for token, uname in senders:
        if is_bot_flooded(token): skip += 1; continue
        emoji = pool.pop(0) if pool else random.choice(DEFAULT_REACTIONS)
        ok_f, desc, retry = bot_reaction(token, api, msg_id, emoji)
        status = "ok" if ok_f else "fail"; final = emoji
        if ok_f: ok += 1
        elif retry > 0:
            mark_bot_flooded(token, retry); skip += 1; status = "skip"
        else: skip += 1
        db_save_reaction(uid, ct, chat_id, pl, msg_id, final, uname, status, method="bot")
        await asyncio.sleep(1.2)
    return ok, skip


async def process_reactions_rotating(event, uid, chat_link, post_link, count,
                                     emoji_mode="default", custom_emojis=None,
                                     is_auto_watch=False):
    chat_ref, invite_hash = parse_channel_link(chat_link)
    post_ref, msg_id = parse_post_link(post_link)
    if not msg_id:
        if event: await safe_edit(event, "❌ Invalid post link")
        return
    user_state = USER_STATES.get(uid, {})
    chat_type = user_state.get("chat_type", "channel")
    total_bots = db_count_bots()
    want = min(count, total_bots)
    if event:
        await anim_loading(event, f"Processing {want} reactions")
    try:
        if invite_hash and not post_ref:
            try: await admin_client(ImportChatInviteRequest(invite_hash))
            except Exception: pass
            entity = await safe_get_entity(f"https://t.me/+{invite_hash}",
                                            cache_key=f"chat:{invite_hash}")
        else:
            target_ref = post_ref or chat_ref
            entity = await safe_get_entity(target_ref, cache_key=f"chat:{target_ref}")
    except Exception as e:
        if event: await safe_edit(event, f"❌ Resolve failed:\n{str(e)[:100]}")
        return
    chat_title = getattr(entity, "title", "Unknown")
    real_id = entity.id
    actual_type = "channel" if is_channel(entity) else ("group" if is_group(entity) else chat_type)
    try:
        post_msg = await asyncio.wait_for(admin_client.get_messages(entity, ids=msg_id), timeout=15)
        if post_msg is None:
            if event: await safe_edit(event, f"❌ Post #{msg_id} not found")
            return
    except Exception: pass
    if not is_auto_watch and ADMIN_CHECK_ENABLED and not OWNER_IS(uid):
        if event:
            try: await event.edit(f"{random.choice(ANIM_GHOST)} **Checking access...**")
            except Exception: pass
        owner_is_admin = await check_owner_admin(entity)
        if not owner_is_admin:
            if event:
                await safe_edit(event, get_admin_needed_message(chat_title, uid),
                                buttons=kb_owner_needed(uid))
            if uid in USER_STATES: USER_STATES[uid] = {}
            return
    cache_key = str(real_id)
    ok_owner, reason_owner = await ensure_owner_admin(entity, cache_key)
    if not ok_owner:
        if event: await safe_edit(event, f"❌ Setup failed: {reason_owner}")
        return
    reactions_done = 0; cycle = 0; failed_batches = 0; cycle_log = []
    while reactions_done < want and cycle < MAX_CYCLES:
        cycle += 1; remaining = want - reactions_done
        if event:
            bar = progress_bar(reactions_done, want)
            await safe_edit(event,
                f"🎬 **Cycle {cycle}** 🎬\n{DIV}\n\n📊 `{bar}` {reactions_done}/{want}\n"
                f"⏳ Remaining: **{remaining}**\n\n🔍 Finding...")
        existing_admins = await get_current_admin_bots(entity)
        db_bots = db_list_bots()
        uname_to_token = {u: t for t, u, b, a in db_bots}
        cycle_admins = []
        for uname, bid in existing_admins:
            if is_permanent_admin(uname): continue
            tok = uname_to_token.get(uname)
            if not tok: continue
            cycle_admins.append((tok, uname))
        cycle_admins = cycle_admins[:remaining]
        if cycle_admins:
            if event:
                await safe_edit(event,
                    f"💫 **Cycle {cycle}** — Phase 1 💫\n{DIV}\n\n"
                    f"♻️ Using **{len(cycle_admins)}** existing...")
            for tok, uname in cycle_admins:
                BOT_POOL.setdefault(tok, {})
                BOT_POOL[tok]["busy_until"] = datetime.now() + timedelta(minutes=BOT_BUSY_TIMEOUT)
                BOT_POOL[tok]["username"] = uname
            ok1, s1 = await send_reactions(real_id, msg_id, cycle_admins, chat_title,
                                            post_link, uid, len(cycle_admins),
                                            emoji_mode=emoji_mode, custom_emojis=custom_emojis)
            reactions_done += ok1
            for uname, bid in existing_admins:
                if is_permanent_admin(uname): continue
                try:
                    await asyncio.wait_for(remove_admin_rights(entity, bid, uname),
                                            timeout=PER_BOT_TIMEOUT)
                    await asyncio.sleep(0.4)
                except Exception: pass
            await release_bots(cycle_admins)
        if reactions_done >= want: break
        remaining = want - reactions_done
        need = remaining + 5
        if event:
            bar = progress_bar(reactions_done, want)
            await safe_edit(event,
                f"🤖 **Cycle {cycle}** — Phase 2 🤖\n{DIV}\n\n📊 `{bar}` {reactions_done}/{want}\n\n"
                f"➕ Adding **{remaining}**...")
        acquired, wait_sec = await acquire_bots(need, uid)
        if acquired is None:
            await asyncio.sleep(wait_sec)
            acquired, wait_sec = await acquire_bots(need, uid)
        if acquired is None:
            failed_batches += 1
            if failed_batches >= 3: break
            continue
        to_add = acquired[:remaining]; promoted = []
        for tok, uname in to_add:
            try:
                ok, rmsg = await asyncio.wait_for(
                    add_one_bot(entity, tok, actual_type, cache_key), timeout=PER_BOT_TIMEOUT)
                if ok: promoted.append((tok, uname))
                elif rmsg == "too_many_admins": break
            except Exception: pass
            await asyncio.sleep(0.6)
        non_promoted = [(t, u) for t, u in acquired if (t, u) not in promoted]
        if non_promoted: await release_bots(non_promoted)
        if not promoted:
            failed_batches += 1
            if failed_batches >= 3: break
            continue
        if event:
            await safe_edit(event,
                f"💫 **Cycle {cycle}** — Reacting 💫\n{DIV}\n\n"
                f"🎯 Using **{len(promoted)}** new...")
        ok2, s2 = await send_reactions(real_id, msg_id, promoted, chat_title, post_link, uid,
                                        len(promoted), emoji_mode=emoji_mode, custom_emojis=custom_emojis)
        reactions_done += ok2
        for tok, uname in promoted:
            if is_permanent_admin(uname): continue
            try:
                ue = await safe_get_entity(uname, cache_key=f"bot:{uname}", cache_store=BOT_ENTITY_CACHE)
                await asyncio.wait_for(remove_admin_rights(entity, ue.id, uname),
                                        timeout=PER_BOT_TIMEOUT)
                await asyncio.sleep(0.3)
            except Exception: pass
        await release_bots(promoted)
        failed_batches = 0
        cycle_log.append((cycle, ok2))
    if event:
        bar = progress_bar(reactions_done, max(want, reactions_done, 1))
        cycles_txt = "".join(f"   🎬 Cycle {cn}: **+{okc}**\n" for cn, okc in cycle_log)
        txt = (f"🎉 **COMPLETE!** 🎉\n{STAR_LINE}\n\n📢 **{chat_title}**\n📩 Post: **#{msg_id}**\n\n"
               f"{DIV}\n🎯 Requested: **{count}**\n✅ Success: **{reactions_done}**\n"
               f"🔁 Cycles: **{cycle}**\n{DIV}\n\n🚀 **{bar}** {reactions_done}/{count}")
        if cycles_txt: txt += f"\n\n**Details:**\n{cycles_txt}"
        txt += f"\n\n{SPARKLE} Thanks for using Ghost Bot! {SPARKLE}"
        await safe_edit(event, txt, buttons=kb_back(uid))
    if uid in USER_STATES and event: USER_STATES[uid] = {}
    return reactions_done


# ══════════════════════ LOOPS ══════════════════════
async def queue_loop():
    global TASK_RUNNING, TASK_OWNER_UID
    while True:
        try:
            await asyncio.sleep(QUEUE_CHECK_INTERVAL)
            if not feat_queue() or TASK_RUNNING: continue
            pending = db_list_queue(status="pending")
            if not pending: continue
            now = datetime.now()
            for job in pending:
                (qid, user_id, cl, pl, rc, em, ce, st, status, cr, ex, err) = job
                if st:
                    try:
                        if datetime.strptime(st, "%Y-%m-%d %H:%M:%S") > now: continue
                    except Exception: pass
                TASK_RUNNING = True; TASK_OWNER_UID = user_id
                try:
                    ce_list = (ce.split(",") if ce else None)
                    result = await process_reactions_rotating(None, user_id, cl, pl, rc,
                                                                emoji_mode=em, custom_emojis=ce_list,
                                                                is_auto_watch=True)
                    db_update_queue(qid, status="done",
                                    executed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                except Exception as e:
                    db_update_queue(qid, status="failed",
                                    executed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    error=str(e)[:200])
                finally:
                    TASK_RUNNING = False; TASK_OWNER_UID = None
        except asyncio.CancelledError: return
        except Exception as e:
            D_err(e, "queue_loop"); await asyncio.sleep(30)


async def watcher_loop():
    global TASK_RUNNING, TASK_OWNER_UID
    while True:
        try:
            await asyncio.sleep(WATCHER_CHECK_INTERVAL)
            if not AUTO_WATCH_ENABLED or not feat_autowatch() or TASK_RUNNING: continue
            watchers = db_list_watchers()
            if not watchers: continue
            for w in watchers:
                (wid, user_id, chat_id, ct, cl, cty, rc, em, ces, lpid, act, cr, lr) = w
                if not act or not can_use_feature(user_id, "autowatch"): continue
                try:
                    entity = await safe_get_entity(chat_id, cache_key=f"watch:{chat_id}")
                    msgs = await asyncio.wait_for(admin_client.get_messages(entity, limit=5), timeout=15)
                    if not msgs: continue
                    newest = max(m.id for m in msgs if m.id > 0)
                    if newest <= lpid: continue
                    TASK_RUNNING = True; TASK_OWNER_UID = user_id
                    try:
                        ce_list = (ces.split(",") if ces else None)
                        pl = f"https://t.me/c/{str(chat_id).replace('-100','')}/{newest}"
                        await process_reactions_rotating(None, user_id, cl, pl, rc,
                                                            emoji_mode=em, custom_emojis=ce_list,
                                                            is_auto_watch=True)
                        db_update_watcher(wid, last_post_id=newest,
                                          last_run=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    finally:
                        TASK_RUNNING = False; TASK_OWNER_UID = None
                except Exception as e: D(f"[WATCHER] {str(e)[:80]}", "fail")
        except asyncio.CancelledError: return
        except Exception as e:
            D_err(e, "watcher_loop"); await asyncio.sleep(30)


async def pool_cleaner_loop():
    while True:
        try:
            await asyncio.sleep(POOL_CLEANUP_INTERVAL); cleanup_bot_pool()
        except asyncio.CancelledError: return
        except Exception as e: D_err(e, "pool_cleaner")


async def health_check_loop():
    while True:
        try:
            await asyncio.sleep(120)
            uptime = int(time.time() - _start_time)
            gh = github_sync.get_stats()
            D(f"HEALTH up={uptime}s task={TASK_RUNNING} pool={len(BOT_POOL)} "
              f"users={db_total_users()} gh={gh['uploads']} sessions={real_count_available()}", "health")
        except asyncio.CancelledError: return
        except Exception as e: D_err(e, "health_check")


async def daily_summary_loop():
    last = None
    while True:
        try:
            await asyncio.sleep(60)
            if not feat_daily_summary(): continue
            tt = cfg_get("daily_summary_time", "21:00")
            now = datetime.now(); today = now.strftime("%Y-%m-%d"); cur = now.strftime("%H:%M")
            if cur == tt and last != today:
                last = today
                tot, tr, mr = db_revenue_stats()
                txt = (f"📊 **DAILY SUMMARY** — {today}\n{STAR_LINE}\n\n"
                       f"👥 Users: **{db_total_users()}**\n💫 Today: **{db_reactions_today()}**\n"
                       f"💫 Total: **{db_total_reactions()}**\n🤖 Bots: **{db_count_visible_bots()}**\n"
                       f"📡 Watchers: **{len(db_list_watchers())}**\n\n"
                       f"💰 Revenue:\n   Today: **{tr}rs**\n   Month: **{mr}rs**\n   Total: **{tot}rs**")
                try: await bot.send_message(get_owner_id(), txt)
                except Exception: pass
        except asyncio.CancelledError: return
        except Exception as e:
            D_err(e, "daily_summary"); await asyncio.sleep(60)


async def get_admin_chats():
    chats = []
    try:
        me = await admin_client.get_me()
        async for d in admin_client.iter_dialogs():
            e = d.entity
            if not isinstance(e, (Channel, Chat)): continue
            try:
                perms = await admin_client.get_permissions(e, me.id)
                if perms and getattr(perms, 'is_admin', False):
                    chats.append({"entity": e, "id": e.id, "title": getattr(e, "title", "Unknown")})
            except Exception: continue
    except Exception: pass
    return chats


async def broadcast_message(text=None, photo_url=None):
    chats = await get_admin_chats(); total = len(chats)
    if total == 0: return 0, 0, 0
    ok_n = fail_n = 0
    for chat in chats:
        api = to_bot_api_chat_id(chat["id"])
        if photo_url and text: ok, _ = bot_send_photo(BOT_TOKEN, api, photo_url, text)
        elif photo_url: ok, _ = bot_send_photo(BOT_TOKEN, api, photo_url)
        elif text: ok, _ = bot_send_message(BOT_TOKEN, api, text)
        else: ok = False
        if ok: ok_n += 1
        else: fail_n += 1
        await asyncio.sleep(BROADCAST_DELAY)
    return ok_n, fail_n, total


# ══════════════════════ KEYBOARDS ══════════════════════
def kb_join():
    rows = [[btn(f"📢 {fc[3]}", url=fc[2], style="primary")] for fc in db_list_force_channels(only_active=True)]
    rows.append([btn("✅ I Have Joined", data=b"check_join", style="success")])
    return rows


def kb_request_access():
    return [[btn("🔔 Request Access", data=b"request_access", style="success")]]


def kb_welcome(uid=None):
    rows = [
        [btn(f"💫 {L(uid, 'send_reactions')}", data=b"react_flow", style="success")],
        [btn(f"⏰ {L(uid, 'queue')} 💎", data=b"queue_menu", style="primary"),
         btn(f"📦 {L(uid, 'bulk')} 💎", data=b"bulk_menu", style="primary")],
        [btn(f"📡 {L(uid, 'auto_watch')} 💎", data=b"watch_flow", style="primary"),
         btn(f"📝 {L(uid, 'templates')} 💎", data=b"templates_menu", style="primary")],
        [btn(f"🎁 {L(uid, 'referral')}", data=b"referral_menu", style="success"),
         btn(f"💰 {L(uid, 'buy_plan')}", data=b"plans_menu", style="success")],
        [btn(f"🔔 {L(uid, 'notifications')}", data=b"notif_menu", style="primary"),
         btn(f"🌍 {L(uid, 'language')}", data=b"lang_menu", style="primary")],
        [btn(f"ℹ️ {L(uid, 'info')}", data=b"info", style="primary"),
         btn(f"💬 {L(uid, 'support')}", data=b"support", style="primary")],
    ]
    if OWNER_IS(uid):
        rows.append([btn(f"👑 {L(uid, 'owner_panel')}", data=b"owner_panel", style="danger")])
    return rows


def kb_owner_needed(uid=None):
    return [
        [btn(f"👑 {L(uid, 'contact_owner')}", url=f"https://t.me/{get_owner_username()}", style="primary")],
        [btn(f"🔄 {L(uid, 'retry')}", data=b"react_flow", style="success")],
        [btn(f"🏠 {L(uid, 'home')}", data=b"home", style="primary")],
    ]


def kb_support():
    return [[btn("💬 DM Owner", url=f"https://t.me/{get_owner_username()}", style="primary")],
            [btn("🔙 Back", data=b"home", style="primary")]]


def kb_chat_type(uid=None):
    return [
        [btn(f"📢 {L(uid, 'channel')}", data=b"chattype:channel", style="primary")],
        [btn(f"👥 {L(uid, 'group')}", data=b"chattype:group", style="success")],
        [btn(f"🔙 {L(uid, 'cancel')}", data=b"home", style="danger")],
    ]


def kb_reaction_count(uid=None):
    limit = get_user_limit(uid) if uid else DEFAULT_FREE_COUNT
    tv = db_count_visible_bots(); ta = db_count_bots()
    if OWNER_IS(uid):
        return [
            [btn(f"🌟 All ({ta})", data=b"rc:all", style="success")],
            [btn("10", data=b"rc:10", style="primary"), btn("20", data=b"rc:20", style="primary"),
             btn("50", data=b"rc:50", style="primary")],
            [btn("100", data=b"rc:100", style="primary"), btn("150", data=b"rc:150", style="primary")],
            [btn("🔙 Back", data=b"home", style="primary")],
        ]
    el = min(limit, tv); rows, row = [], []
    for i in range(1, el + 1):
        row.append(btn(f"{i}", data=f"rc:{i}".encode(), style="primary"))
        if len(row) == 4: rows.append(row); row = []
    if row: rows.append(row)
    rows.append([btn(f"🎁 {el} MAX", data=f"rc:{el}".encode(), style="success")])
    rows.append([btn("🔥 More", data=b"rc_more", style="danger")])
    rows.append([btn("🔙 Back", data=b"home", style="primary")])
    return rows


def kb_emoji_choice(uid=None):
    return [
        [btn(f"🎯 {L(uid, 'default_emoji')}", data=b"emoji:default", style="success")],
        [btn(f"✏️ {L(uid, 'custom_emoji')} 💎", data=b"emoji:custom", style="primary")],
        [btn(f"🎨 {L(uid, 'emoji_packs')} 💎", data=b"emoji:packs", style="primary")],
        [btn(f"📝 {L(uid, 'templates')} 💎", data=b"emoji:templates", style="primary")],
        [btn(f"🔙 {L(uid, 'back')}", data=b"home", style="danger")],
    ]


def kb_watch_menu(uid=None):
    return [
        [btn(f"➕ {L(uid, 'add_watch')}", data=b"watch:add", style="success")],
        [btn(f"📋 {L(uid, 'my_watches')}", data=b"watch:list", style="primary")],
        [btn(f"🔙 {L(uid, 'back')}", data=b"home", style="primary")],
    ]


def kb_queue_menu(uid=None):
    return [
        [btn("➕ New Job", data=b"queue:add", style="success")],
        [btn("📋 My Jobs", data=b"queue:list", style="primary")],
        [btn(f"🔙 {L(uid, 'back')}", data=b"home", style="primary")],
    ]


def kb_bulk_menu(uid=None):
    return [
        [btn("📦 Multi Posts", data=b"bulk:multi_post", style="success")],
        [btn("📋 My Jobs", data=b"bulk:list", style="primary")],
        [btn(f"🔙 {L(uid, 'back')}", data=b"home", style="primary")],
    ]


def kb_templates_menu(uid):
    ts = db_list_templates(uid)
    rows = [[btn("➕ New", data=b"tpl:new", style="success")]]
    for t in ts[:5]:
        rows.append([btn(f"📝 {t[1]}", data=f"tpl:use:{t[0]}".encode(), style="primary"),
                     btn("🗑️", data=f"tpl:del:{t[0]}".encode(), style="danger")])
    rows.append([btn(f"🔙 {L(uid, 'back')}", data=b"home", style="primary")])
    return rows


def kb_referral_menu(uid):
    return [
        [btn(f"🔗 {L(uid, 'my_link')}", data=b"ref:link", style="success")],
        [btn(f"📊 {L(uid, 'stats')}", data=b"ref:stats", style="primary")],
        [btn(f"🏆 {L(uid, 'leaderboard')}", data=b"ref:leaderboard", style="primary")],
        [btn(f"🔙 {L(uid, 'back')}", data=b"home", style="primary")],
    ]


def kb_plans_menu(uid=None):
    rows = [[btn(f"{PLAN_NAMES[k]} — {PLAN_LIMITS[k]}/post",
                 data=f"plan:{k}".encode(), style="primary")]
            for k in ["basic", "pro", "premium"]]
    rows.append([btn(f"🆓 {L(uid, 'free_plan')}", data=b"plan:free", style="success")])
    rows.append([btn(f"🔙 {L(uid, 'back')}", data=b"home", style="primary")])
    return rows


def kb_plan_durations(plan, uid=None):
    rows = [[btn(f"📅 {label} — {get_plan_price(plan, days)}rs",
                 data=f"pland:{plan}:{days}".encode(),
                 style="success" if days == 30 else "primary")]
            for days, label in DURATIONS.items()]
    rows.append([btn(f"🔙 {L(uid, 'back')}", data=f"plan:{plan}".encode(), style="primary")])
    return rows


def kb_payment_methods(plan, days, uid=None):
    methods = db_payment_list(active_only=True)
    rows = []
    for m in methods:
        mid, key, name, number, holder, icon, instr, act, so = m
        rows.append([btn(f"{icon} {name}", data=f"pay:{plan}:{days}:{mid}".encode(), style="primary")])
    if not rows:
        rows.append([btn("❌ No methods", data=b"home", style="danger")])
    rows.append([btn(f"🔙 {L(uid, 'back')}", data=f"pland:{plan}:{days}".encode(), style="primary")])
    return rows


def kb_lang_menu(uid):
    u = db_get_user_full(uid); cur = u[18] if u and len(u) > 18 else "en"
    rows = [[btn(f"{'✅ ' if c == cur else ''}{n}", data=f"lang:{c}".encode(),
                 style="success" if c == cur else "primary")]
            for c, n in LANGUAGES.items()]
    rows.append([btn(f"🔙 {L(uid, 'back')}", data=b"home", style="primary")])
    return rows


def kb_notif_menu(uid=None):
    return [
        [btn("📬 Notifications", data=b"notif:list", style="primary")],
        [btn("✅ Mark Read", data=b"notif:read", style="success")],
        [btn(f"🔙 {L(uid, 'back')}", data=b"home", style="primary")],
    ]


def kb_emoji_packs(uid=None):
    rows = [[btn(f"🎨 {k.title()} — {' '.join(e[:3])}", data=f"pack:{k}".encode(), style="primary")]
            for k, e in EMOJI_PACKS.items()]
    for cp in db_list_custom_packs():
        cpid, name, emojis, price, is_paid = cp
        pre = "💎" if is_paid else "🎨"
        rows.append([btn(f"{pre} {name}", data=f"cpack:{cpid}".encode(), style="primary")])
    rows.append([btn(f"🔙 {L(uid, 'back')}", data=b"emoji:custom", style="danger")])
    return rows


def kb_back(uid=None):
    return [[btn(f"🔙 {L(uid, 'back')}", data=b"home", style="primary")]]


def kb_owner():
    auto = "✅" if is_auto_approve() else "❌"
    vis = db_count_visible_bots(); sess = real_count_available()
    return [
        [btn("📊 Analytics", data=b"op:analytics", style="success"),
         btn("👥 Users", data=b"op:users", style="primary")],
        [btn("💰 Revenue", data=b"op:revenue", style="primary"),
         btn("💳 Payments", data=b"op:payments", style="danger")],
        [btn(f"🤖 Bots ({vis})", data=b"op:bots", style="primary"),
         btn("📢 Broadcast", data=b"op:broadcast", style="danger")],
        [btn(f"👤 Sessions ({sess})", data=b"op:ra", style="success"),
         btn("⚙️ RA Plans", data=b"op:ra_plans", style="primary")],
        [btn("💳 Payment Methods", data=b"op:pm", style="primary"),
         btn("👤 Owner Info", data=b"op:owner_info", style="success")],
        [btn(f"🔓 Auto:{auto}", data=b"op:toggle_auto", style="success"),
         btn(f"⚙️ Free:{get_free_count()}", data=b"op:setfree", style="primary")],
        [btn("🎛️ Features", data=b"op:features", style="primary"),
         btn("💰 Prices", data=b"op:plan_prices", style="success")],
        [btn("💎 PAID FEATURES", data=b"op:paid_features", style="danger")],
        [btn("📢 Force Ch", data=b"op:force_channels", style="primary"),
         btn("👥 Team", data=b"op:team", style="success")],
        [btn("🎨 Emoji Packs", data=b"op:emoji_packs", style="primary"),
         btn("📡 Watchers", data=b"op:watchers", style="primary")],
        [btn("🎁 Referrals", data=b"op:referrals", style="success"),
         btn("⏰ Queue", data=b"op:queue", style="primary")],
        [btn("📊 Pool", data=b"op:pool_status", style="primary"),
         btn("🧹 RESET POOL", data=b"op:reset_pool", style="danger")],
        [btn("🔄 GitHub Sync", data=b"op:ghsync", style="success"),
         btn("🔄 Re-DL Sessions", data=b"op:ra_redl", style="primary")],
        [btn("➕ Add User", data=b"op:adduser", style="success"),
         btn("⏳ Pending", data=b"op:pending", style="danger")],
        [btn("✅ Approved", data=b"op:approved", style="success"),
         btn("📜 Recent", data=b"op:recent", style="primary")],
        [btn("🔙 Main", data=b"home", style="primary")],
    ]


def kb_features():
    def t(k, l): return f"{'✅' if cfg_bool(k) else '❌'} {l}"
    return [
        [btn(t("channel_enabled", "Channel"), data=b"ft:toggle:channel_enabled", style="primary")],
        [btn(t("group_enabled", "Group"), data=b"ft:toggle:group_enabled", style="success")],
        [btn(t("manual_enabled", "Manual"), data=b"ft:toggle:manual_enabled", style="primary")],
        [btn(t("autowatch_enabled", "Auto-Watch"), data=b"ft:toggle:autowatch_enabled", style="success")],
        [btn(t("custom_emoji_enabled", "Custom Emoji"), data=b"ft:toggle:custom_emoji_enabled", style="primary")],
        [btn(t("force_join_enabled", "Force Join"), data=b"ft:toggle:force_join_enabled", style="success")],
        [btn(t("paid_plans_enabled", "Paid Plans"), data=b"ft:toggle:paid_plans_enabled", style="primary")],
        [btn(t("referral_enabled", "Referral"), data=b"ft:toggle:referral_enabled", style="success")],
        [btn(t("multi_lang_enabled", "Multi-Lang"), data=b"ft:toggle:multi_lang_enabled", style="primary")],
        [btn(t("templates_enabled", "Templates"), data=b"ft:toggle:templates_enabled", style="success")],
        [btn(t("notifications_enabled", "Notifications"), data=b"ft:toggle:notifications_enabled", style="primary")],
        [btn(t("queue_enabled", "Queue"), data=b"ft:toggle:queue_enabled", style="success")],
        [btn(t("bulk_enabled", "Bulk"), data=b"ft:toggle:bulk_enabled", style="primary")],
        [btn(t("auto_payment_enabled", "Payment"), data=b"ft:toggle:auto_payment_enabled", style="success")],
        [btn(t("daily_summary_enabled", "Summary"), data=b"ft:toggle:daily_summary_enabled", style="primary")],
        [btn(t("team_enabled", "Team"), data=b"ft:toggle:team_enabled", style="success")],
        [btn(t("realaccounts_enabled", "Real Accounts"), data=b"ft:toggle:realaccounts_enabled", style="primary")],
        [btn("🔙 Back", data=b"owner_panel", style="danger")],
    ]


def kb_plan_prices():
    rows = [[btn(f"💰 {PLAN_NAMES[p]}", data=f"pp:plan:{p}".encode(), style="primary")]
            for p in ["basic", "pro", "premium"]]
    rows.append([btn("🔙 Back", data=b"owner_panel", style="primary")])
    return rows


def kb_plan_prices_durations(plan):
    rows = [[btn(f"📅 {label}: {get_plan_price(plan, days)}rs",
                 data=f"pp:edit:{plan}:{days}".encode(), style="primary")]
            for days, label in DURATIONS.items()]
    rows.append([btn("🔙 Back", data=b"op:plan_prices", style="primary")])
    return rows


def kb_paid_features():
    def t(k, l):
        paid = cfg_bool(f"paid_{k}", False)
        st = "💎 PAID" if paid else "🆓 FREE"
        return btn(f"{st} — {l}", data=f"pf:toggle:{k}".encode(),
                   style="danger" if paid else "success")
    return [
        [t("autowatch", "Auto-Watch")], [t("custom_emoji", "Custom Emoji")],
        [t("templates", "Templates")], [t("multilang", "Multi-Language")],
        [t("referral", "Referral")], [t("balance", "Free Balance")],
        [t("channel", "Channel")], [t("group", "Group")], [t("manual", "Manual")],
        [t("realaccounts", "Real Accounts")],
        [btn("🔙 Back", data=b"owner_panel", style="primary")],
    ]


def kb_force_channels():
    rows = []
    for fc in db_list_force_channels(only_active=False):
        fid, ch, url, name, act = fc
        st = "🟢" if act else "🔴"
        rows.append([btn(f"{st} {name} ({ch})", data=f"fc:toggle:{fid}".encode(), style="primary"),
                     btn("🗑️", data=f"fc:del:{fid}".encode(), style="danger")])
    rows.append([btn("➕ Add", data=b"fc:add", style="success")])
    rows.append([btn("🔙 Back", data=b"owner_panel", style="primary")])
    return rows


def kb_team():
    rows = [[btn(f"👤 {m[0]} — {m[1]} ({m[3]}%)", data=f"team:view:{m[0]}".encode(), style="primary")]
            for m in db_list_team()[:10]]
    rows.append([btn("➕ Add", data=b"team:add", style="success")])
    rows.append([btn("🔙 Back", data=b"owner_panel", style="primary")])
    return rows


def kb_emoji_packs_manage():
    rows = []
    for cp in db_list_custom_packs():
        cpid, name, emojis, price, is_paid = cp
        pre = "💎" if is_paid else "🎨"
        rows.append([btn(f"{pre} {name} — {price}rs",
                         data=f"cp:view:{cpid}".encode(), style="primary"),
                     btn("🗑️", data=f"cp:del:{cpid}".encode(), style="danger")])
    rows.append([btn("➕ New Pack", data=b"cp:new", style="success")])
    rows.append([btn("🔙 Back", data=b"owner_panel", style="primary")])
    return rows


def kb_payment_methods_manage():
    rows = []
    for m in db_payment_list(active_only=False):
        mid, key, name, number, holder, icon, instr, act, so = m
        st = "🟢" if act else "🔴"
        rows.append([btn(f"{st} {icon} {name}", data=f"pm:view:{mid}".encode(), style="primary")])
    rows.append([btn("➕ Add Method", data=b"pm:add", style="success")])
    rows.append([btn("🔙 Back", data=b"owner_panel", style="primary")])
    return rows


def kb_payment_method_edit(mid):
    m = db_payment_get(mid)
    if not m: return [[btn("❌ Not found", data=b"op:pm", style="danger")]]
    mid, key, name, number, holder, icon, instr, act, so = m
    return [
        [btn(f"✏️ Name: {name}", data=f"pm:edit_name:{mid}".encode(), style="primary")],
        [btn(f"✏️ Number: {number}", data=f"pm:edit_number:{mid}".encode(), style="primary")],
        [btn(f"✏️ Holder: {holder}", data=f"pm:edit_holder:{mid}".encode(), style="primary")],
        [btn(f"✏️ Icon: {icon}", data=f"pm:edit_icon:{mid}".encode(), style="primary")],
        [btn(f"{'🟢 ON' if act else '🔴 OFF'}", data=f"pm:toggle:{mid}".encode(),
              style="success" if act else "danger")],
        [btn("🗑️ Delete", data=f"pm:del:{mid}".encode(), style="danger")],
        [btn("🔙 Back", data=b"op:pm", style="primary")],
    ]


def kb_user_manage(uid):
    u = db_get_user_full(uid)
    if not u: return [[btn("❌ Not found", data=b"op:users", style="danger")]]
    def yn(v): return "✅" if v else "❌"
    plan = u[15] or "free"; fb = u[17] or 0
    try: ra_ov = u[26] if len(u) > 26 else -1
    except Exception: ra_ov = -1
    ra_lbl = ra_ov if ra_ov >= 0 else "Plan"
    return [
        [btn(f"{yn(not u[5])} {'BANNED' if u[5] else 'Active'}",
              data=f"um:ban:{uid}".encode(),
              style="danger" if u[5] else "success")],
        [btn(f"🎁 Limit: {u[8] if u[8] > 0 else get_free_count()}",
              data=f"um:limit:{uid}".encode(), style="primary")],
        [btn(f"💰 Plan: {plan}", data=f"um:plan:{uid}".encode(), style="success")],
        [btn(f"🎁 Balance: {fb}", data=f"um:balance:{uid}".encode(), style="primary")],
        [btn(f"👤 RA Limit: {ra_lbl}", data=f"um:ra:{uid}".encode(), style="success")],
        [btn(f"👥 Team: {u[23] or 'user'}", data=f"um:team:{uid}".encode(), style="primary")],
        [btn(f"{yn(u[10])} Channel", data=f"um:channel:{uid}".encode(), style="primary")],
        [btn(f"{yn(u[11])} Group", data=f"um:group:{uid}".encode(), style="success")],
        [btn(f"{yn(u[12])} Manual", data=f"um:manual:{uid}".encode(), style="primary")],
        [btn(f"{yn(u[13])} Auto-Watch", data=f"um:autowatch:{uid}".encode(), style="success")],
        [btn(f"{yn(u[14])} Custom Emoji", data=f"um:custom:{uid}".encode(), style="primary")],
        [btn(f"{yn(u[9])} AW Unlock", data=f"um:unlock:{uid}".encode(), style="success")],
        [btn("🔙 Back", data=b"op:users", style="danger")],
    ]


def kb_user_plan_durations(tuid):
    rows = [[btn(f"{PLAN_NAMES[p]} {DURATIONS[d]}",
                 data=f"um:activate:{p}:{d}:{tuid}".encode(), style="primary")]
            for p in ["basic", "pro", "premium"] for d in [1, 7, 15, 30]]
    rows.append([btn("🆓 Free", data=f"um:activate:free:9999:{tuid}".encode(), style="success")])
    rows.append([btn("🔙 Back", data=f"um:panel:{tuid}".encode(), style="danger")])
    return rows


def kb_approval_actions(tuid):
    return [[btn("✅ Approve", data=f"approve:{tuid}".encode(), style="success"),
             btn("❌ Reject", data=f"reject:{tuid}".encode(), style="danger")]]


def kb_payment_actions(pid):
    return [[btn("✅ Verify", data=f"payv:approve:{pid}".encode(), style="success"),
             btn("❌ Reject", data=f"payv:reject:{pid}".encode(), style="danger")]]


def get_admin_needed_message(chat_title, uid=None):
    return (
        f"{STAR_LINE}\n⚠️ **{WT(uid, 'read_first')}** ⚠️\n{STAR_LINE}\n\n"
        f"📢 **{chat_title}**\n\n❌ {WT(uid, 'warn_line')}\n\n"
        f"{DIV}\n👑 **{WT(uid, 'owner_lbl')}:** @{get_owner_username()}\n"
        f"🆔 **{WT(uid, 'owner_id_lbl')}:** `{get_owner_id()}`\n{DIV}\n\n"
        f"📋 **{WT(uid, 'req_perm')}:**\n"
        f"   ⭐ {WT(uid, 'perm1')}\n   ⭐ {WT(uid, 'perm2')}\n"
        f"   ⭐ {WT(uid, 'perm3')}\n   ⭐ {WT(uid, 'perm4')}\n\n"
        f"{DIV}\n🔧 **{WT(uid, 'howto')}**\n{DIV}\n"
        f"1️⃣ {WT(uid, 'step1')}\n2️⃣ {WT(uid, 'step2')}\n"
        f"3️⃣ {WT(uid, 'step3')}\n4️⃣ {WT(uid, 'step4')}\n5️⃣ {WT(uid, 'step5')}\n"
        f"{DIV}\n\n💬 @{get_owner_username()}  |  🆔 `{get_owner_id()}`"
    )


def get_welcome_message(first_name, uid, auto_approved=True):
    limit = get_user_limit(uid)
    u = db_get_user_full(uid)
    aw = u[9] if u else 0
    plan = u[15] if u else "free"
    fb = u[17] if u else 0
    plan_name = PLAN_NAMES.get(plan, PLAN_NAMES['free'])
    yes_no = f"✅ {WT(uid, 'yes')}" if auto_approved else f"⏳ {WT(uid, 'no')}"
    aw_state = "✅" if aw else "🔒"
    return (
        f"{STAR_LINE}\n👻 **{WT(uid, 'title')}** 👻\n{STAR_LINE}\n\n"
        f"👋 {WT(uid, 'greet')}, **{first_name}**!\n\n"
        f"{DIV}\n⚠️ **{WT(uid, 'read_first')}**\n{DIV}\n\n"
        f"❌ {WT(uid, 'warn_line')}\n\n"
        f"👑 **{WT(uid, 'owner_lbl')}:** @{get_owner_username()}\n"
        f"🆔 **{WT(uid, 'owner_id_lbl')}:** `{get_owner_id()}`\n\n"
        f"📋 **{WT(uid, 'req_perm')}:**\n"
        f"   ⭐ {WT(uid, 'perm1')}\n   ⭐ {WT(uid, 'perm2')}\n"
        f"   ⭐ {WT(uid, 'perm3')}\n   ⭐ {WT(uid, 'perm4')}\n\n"
        f"{DIV}\n🔧 **{WT(uid, 'howto')}**\n{DIV}\n"
        f"1️⃣ {WT(uid, 'step1')}\n2️⃣ {WT(uid, 'step2')}\n"
        f"3️⃣ {WT(uid, 'step3')}\n4️⃣ {WT(uid, 'step4')}\n5️⃣ {WT(uid, 'step5')}\n\n"
        f"{DIV}\n📊 **{WT(uid, 'your_info')}**\n{DIV}\n"
        f"💰 {WT(uid, 'plan')}: **{plan_name}**\n"
        f"🎁 {WT(uid, 'limit')}: **{limit}** {WT(uid, 'per_post')}\n"
        f"💎 {WT(uid, 'balance')}: **{fb}**\n"
        f"📡 {WT(uid, 'autowatch')}: **{aw_state}**\n"
        f"🔓 {WT(uid, 'approved')}: **{yes_no}**\n"
        f"{DIV}\n\n{WT(uid, 'ready')}"
    )


def get_approved_notify_message(first_name, uid=None):
    return (
        f"{STAR_LINE}\n{SPARKLE} 🎉 **APPROVED** 🎉 {SPARKLE}\n{STAR_LINE}\n\n"
        f"👋 {WT(uid, 'greet')}, **{first_name}**!\n✅ Access granted!\n\n"
        f"{DIV}\n👑 **{WT(uid, 'owner_lbl')}:** @{get_owner_username()}\n"
        f"🆔 **{WT(uid, 'owner_id_lbl')}:** `{get_owner_id()}`\n{DIV}\n\n"
        f"⚠️ {WT(uid, 'warn_line')}\n\n"
        f"🎁 {DEFAULT_FREE_COUNT} reactions per post\n🚀 Send /start to begin!"
    )


# ══════════════════════ /start ══════════════════════
@bot.on(events.NewMessage(pattern="/start"))
async def on_start(event):
    try:
        if event.is_channel: return
        uid = event.sender_id
        if uid is None: return
        text = event.text or ""
        ref_code = None
        if " " in text:
            parts = text.split()
            if len(parts) > 1 and parts[1].startswith("ref_"):
                ref_code = parts[1][4:]
        try:
            sender = await event.get_sender()
            if sender is None or isinstance(sender, (Channel, Chat)):
                fn, un = "User", None
            else:
                fn = getattr(sender, "first_name", None) or "User"
                un = getattr(sender, "username", None)
        except Exception: fn, un = "User", None
        existing = db_get_user(uid); is_new = existing is None
        db_save_user(uid, fn, un)
        if is_new and ref_code and feat_referral() and not OWNER_IS(uid):
            rid = db_find_user_by_ref_code(ref_code)
            if rid and rid != uid: db_add_referral(rid, uid)
        if db_is_banned(uid):
            await event.reply("🚫 **BANNED.**"); return
        auto = is_auto_approve()
        if not OWNER_IS(uid) and auto:
            if db_approval_status(uid) in (None, "pending"):
                db_set_approval(uid, "approved", approved_by=get_owner_id())
        if not await is_joined(uid):
            await event.reply(
                f"{STAR_LINE}\n👻 **GHOST REACTION BOT**\n{STAR_LINE}\n\n"
                f"🔐 **ACCESS LOCKED**\n\nJoin all channels to continue!",
                buttons=kb_join())
            return
        if feat_referral():
            referrer = db_validate_referral(uid)
            if referrer:
                try: await bot.send_message(referrer, "🎁 **REFERRAL VALIDATED!**")
                except Exception: pass
        if OWNER_IS(uid):
            await event.reply(
                f"{STAR_LINE}\n👑 **OWNER DASHBOARD**\n{STAR_LINE}\n\n"
                f"🤖 Bots: **{db_count_visible_bots()}**\n"
                f"👥 Users: **{db_total_users()}**\n"
                f"📡 Watchers: **{len(db_list_watchers())}**\n"
                f"⏰ Queue: **{len(db_list_queue(status='pending'))}**\n\n"
                f"✨ Welcome back, boss! 👑",
                buttons=kb_welcome(uid))
            return
        status = db_approval_status(uid)
        if status == "approved" or auto:
            await event.reply(get_welcome_message(fn, uid, auto_approved=True), buttons=kb_welcome(uid))
            return
        if status == "pending":
            await event.reply("⏳ **PENDING**", buttons=kb_request_access()); return
        if status == "rejected":
            await event.reply("❌ **DENIED**"); return
        await event.reply("🔐 **WELCOME**", buttons=kb_request_access())
    except Exception as e: D_err(e, "on_start")


# ══════════════════════ CALLBACK ══════════════════════
@bot.on(events.CallbackQuery)
async def on_cb(event):
    global TASK_RUNNING, TASK_OWNER_UID
    try:
        data = event.data.decode()
        uid = event.sender_id

        if data == "support":
            await event.answer("💬", alert=True)
            await safe_edit(event,
                f"{STAR_LINE}\n💬 **SUPPORT**\n{STAR_LINE}\n\n"
                f"👑 @{get_owner_username()}\n🆔 `{get_owner_id()}`",
                buttons=kb_support()); return

        if data == "request_access":
            if is_auto_approve():
                db_set_approval(uid, "approved", approved_by=get_owner_id())
                await event.answer("✅ Auto-approved!", alert=True)
                await safe_edit(event, "✅ Approved!", buttons=kb_welcome(uid)); return
            if db_has_requested(uid):
                await event.answer("⏳ Already requested", alert=True); return
            try:
                sender = await event.get_sender()
                fn = getattr(sender, "first_name", None) or "User"
                un = getattr(sender, "username", None)
            except Exception: fn, un = "User", None
            ok, reason = db_create_approval(uid, fn, un)
            if not ok:
                await event.answer(f"⏳ {reason}", alert=True); return
            try:
                await bot.send_message(get_owner_id(),
                    f"🔔 **REQUEST**\n👤 {fn}\n🆔 `{uid}`",
                    buttons=kb_approval_actions(uid))
            except Exception: pass
            await event.answer("✅ Sent!", alert=True)
            await safe_edit(event, "⏳ **PENDING**", buttons=kb_request_access()); return

        if data.startswith("approve:"):
            if not OWNER_IS(uid): return
            target = int(data.split(":")[1])
            db_set_approval(target, "approved", approved_by=get_owner_id())
            await event.answer("✅", alert=True)
            try:
                tu = db_get_user(target); tn = tu[1] if tu else "User"
                await bot.send_message(target, get_approved_notify_message(tn, target),
                                        buttons=kb_welcome(target))
            except Exception: pass
            return

        if data.startswith("reject:"):
            if not OWNER_IS(uid): return
            target = int(data.split(":")[1])
            db_set_approval(target, "rejected", approved_by=get_owner_id())
            await event.answer("❌", alert=True); return

        if data == "check_join":
            if await is_joined(uid):
                await event.answer("✅ Verified!", alert=True)
                if feat_referral(): db_validate_referral(uid)
                status = db_approval_status(uid); auto = is_auto_approve()
                if OWNER_IS(uid) or status == "approved" or auto:
                    await safe_edit(event, "👑 Welcome", buttons=kb_welcome(uid))
                else:
                    await safe_edit(event, "🔐 Need approval", buttons=kb_request_access())
            else:
                await event.answer("❌ Join all channels first!", alert=True)
            return

        if db_is_banned(uid): await event.answer("🚫 Banned!", alert=True); return
        if not OWNER_IS(uid) and not is_approved(uid):
            await event.answer("❌ Not approved!", alert=True); return

        if data == "home":
            await safe_edit(event, "🏠 **MAIN MENU**", buttons=kb_welcome(uid)); return

        if data == "info":
            user = db_get_user(uid); u = db_get_user_full(uid)
            limit = get_user_limit(uid); plan = u[15] or "free"
            fb = u[17] or 0; aw = u[9] if u else 0
            rc, re = db_get_referral_stats(uid); exp = u[16] or "N/A"
            ra_lim, ra_src = get_user_ra_limit(uid)
            await safe_edit(event,
                f"ℹ️ **YOUR INFO**\n{DIV}\n\n"
                f"🆔 `{uid}`\n📛 {user[1] if user else '—'}\n"
                f"💰 {L(uid, 'plan')}: **{PLAN_NAMES.get(plan, PLAN_NAMES['free'])}**\n"
                f"📅 Expires: **{exp[:10] if exp != 'N/A' else 'N/A'}**\n"
                f"🎁 {L(uid, 'your_limit')}: **{limit}** {L(uid, 'per_post')}\n"
                f"💎 Balance: **{fb}**\n"
                f"📡 Auto-Watch: **{'✅' if aw else '🔒'}**\n"
                f"🎁 Referrals: **{rc}** ({re} earned)",
                buttons=kb_back(uid)); return

        # QUEUE
        if data == "queue_menu":
            if not feat_queue(): await event.answer("💎 PAID!", alert=True); return
            await safe_edit(event, f"⏰ **{L(uid, 'queue').upper()}**\n{DIV}", buttons=kb_queue_menu(uid)); return
        if data == "queue:add":
            USER_STATES[uid] = {"step": "queue_wait_chat", "chat_type": "channel"}
            await safe_edit(event, "⏰ Send chat link:", buttons=kb_back(uid)); return
        if data == "queue:list":
            jobs = db_list_queue(user_id=uid)
            if not jobs:
                await safe_edit(event, "📋 No jobs.", buttons=kb_queue_menu(uid)); return
            txt = f"📋 **MY JOBS ({len(jobs)})**\n{DIV}\n\n"
            for j in jobs[:10]:
                qid, _, _, _, rc, _, _, st, status, _, _, _ = j
                icon = {"pending": "⏳", "done": "✅", "failed": "❌"}.get(status, "•")
                txt += f"{icon} **#{qid}** {rc}x — {status}\n"
            await safe_edit(event, txt[:4000], buttons=kb_queue_menu(uid)); return

        # BULK
        if data == "bulk_menu":
            if not feat_bulk(): await event.answer("💎 PAID!", alert=True); return
            await safe_edit(event, f"📦 **{L(uid, 'bulk').upper()}**\n{DIV}", buttons=kb_bulk_menu(uid)); return
        if data == "bulk:multi_post":
            USER_STATES[uid] = {"step": "bulk_wait_chat"}
            await safe_edit(event, "📦 Send chat link:", buttons=kb_back(uid)); return
        if data == "bulk:list":
            await safe_edit(event, "📋 Coming soon!", buttons=kb_bulk_menu(uid)); return

        # TEMPLATES
        if data == "templates_menu":
            if not feat_templates(): await event.answer("💎 PAID!", alert=True); return
            await safe_edit(event, f"📝 **{L(uid, 'templates').upper()}**\n{DIV}", buttons=kb_templates_menu(uid)); return
        if data == "tpl:new":
            USER_STATES[uid] = {"step": "tpl_wait_name"}
            await safe_edit(event, "📝 Template naam:", buttons=kb_back(uid)); return
        if data.startswith("tpl:use:"):
            tid = int(data.split(":")[2])
            for t in db_list_templates(uid):
                if t[0] == tid:
                    state = USER_STATES.get(uid, {})
                    state["custom_emojis"] = t[2].split(","); state["emoji_mode"] = "custom"
                    USER_STATES[uid] = state
                    await event.answer("✅ Loaded", alert=True)
                    if state.get("reaction_count"): await _run_reactions(event, uid)
                    else: await safe_edit(event, f"✅ **{t[1]}** loaded!", buttons=kb_back(uid))
                    return
            return
        if data.startswith("tpl:del:"):
            tid = int(data.split(":")[2]); db_delete_template(tid, uid)
            await event.answer("🗑️", alert=True)
            await safe_edit(event, "Deleted", buttons=kb_templates_menu(uid)); return

        # REFERRAL
        if data == "referral_menu":
            if not feat_referral(): await event.answer("❌", alert=True); return
            await safe_edit(event, f"🎁 **REFERRAL**\n{DIV}", buttons=kb_referral_menu(uid)); return
        if data == "ref:link":
            code = db_get_referral_code(uid) or gen_referral_code(uid)
            try:
                conn = sqlite3.connect(DB_FILE)
                conn.execute("UPDATE users SET referral_code=? WHERE user_id=?", (code, uid))
                conn.commit(); conn.close(); _dirty()
            except Exception: pass
            me = await bot.get_me()
            link = f"https://t.me/{me.username}?start=ref_{code}"
            await safe_edit(event, f"🔗 **YOUR LINK**\n{DIV}\n\n`{link}`", buttons=kb_referral_menu(uid)); return
        if data == "ref:stats":
            c, e = db_get_referral_stats(uid)
            await safe_edit(event, f"📊 **STATS**\n{DIV}\n\n🎁 {c}\n💰 {e}", buttons=kb_referral_menu(uid)); return
        if data == "ref:leaderboard":
            try:
                conn = sqlite3.connect(DB_FILE)
                rows = conn.execute("SELECT first_name, referral_count FROM users WHERE referral_count > 0 ORDER BY referral_count DESC LIMIT 10").fetchall()
                conn.close()
            except Exception: rows = []
            txt = f"🏆 **LEADERBOARD**\n{DIV}\n\n"
            for i, r in enumerate(rows, 1): txt += f"{i}. **{r[0] or 'User'}** — {r[1]}\n"
            if not rows: txt += "_No referrals_"
            await safe_edit(event, txt, buttons=kb_referral_menu(uid)); return

        # PLANS
        if data == "plans_menu":
            if not feat_plans(): await event.answer("❌", alert=True); return            await safe_edit(event, f"💰 **{L(uid, 'buy_plan').upper()}**\n{DIV}", buttons=kb_plans_menu(uid)); return
        if data.startswith("plan:"):
            plan_key = data.split(":")[1]
            if plan_key == "free":
                db_set_user_plan(uid, "free", 9999)
                await event.answer("✅ Free active", alert=True)
                await safe_edit(event, "✅ **FREE**", buttons=kb_welcome(uid)); return
            if plan_key not in PLAN_LIMITS: return
            await safe_edit(event, f"{PLAN_NAMES[plan_key]}\n{DIV}\n\nChoose duration:",
                            buttons=kb_plan_durations(plan_key, uid)); return
        if data.startswith("pland:"):
            parts = data.split(":"); plan_key = parts[1]; days = int(parts[2])
            if plan_key not in PLAN_LIMITS: return
            price = get_plan_price(plan_key, days)
            await safe_edit(event,
                f"💰 **ORDER**\n{DIV}\n\n📦 {PLAN_NAMES[plan_key]}\n📅 {DURATIONS[days]}\n"
                f"💰 **{price}rs**\n\nChoose payment:",
                buttons=kb_payment_methods(plan_key, days, uid)); return
        if data.startswith("pay:"):
            parts = data.split(":"); plan_key = parts[1]; days = int(parts[2]); method_id = int(parts[3])
            price = get_plan_price(plan_key, days); m = db_payment_get(method_id)
            if not m: await event.answer("❌", alert=True); return
            mid, key, name, number, holder, icon, instr, act, so = m
            await safe_edit(event,
                f"💳 **PAYMENT**\n{DIV}\n\n📦 {PLAN_NAMES[plan_key]} — {DURATIONS[days]}\n"
                f"💰 **{price}rs**\n\n{icon} **{name}**\n🔢 `{number}`\n👤 {holder}\n"
                + (f"\n📝 {instr}\n" if instr else "") +
                f"\n📸 Payment karke screenshot bhejein.",
                buttons=[[btn("📸 Send Screenshot",
                              data=f"payss:{plan_key}:{days}:{method_id}".encode(),
                              style="success")],
                         [btn("🔙 Back", data=f"pland:{plan_key}:{days}".encode(), style="primary")]])
            return
        if data.startswith("payss:"):
            parts = data.split(":")
            USER_STATES[uid] = {"step": "wait_payment_screenshot", "plan": parts[1],
                                "days": int(parts[2]), "method_id": int(parts[3])}
            await safe_edit(event, "📸 Send screenshot (ya 'skip'):", buttons=kb_back(uid)); return

        # LANGUAGE
        if data == "lang_menu":
            if not feat_multilang(): await event.answer("❌", alert=True); return
            await safe_edit(event, f"🌍 **{L(uid, 'choose_language').upper()}**\n{DIV}", buttons=kb_lang_menu(uid)); return
        if data.startswith("lang:"):
            code = data.split(":")[1]
            if code not in LANGUAGES: return
            db_set_user_lang(uid, code)
            await event.answer(f"✅ {LANGUAGES[code]}", alert=True)
            await safe_edit(event, "✅ Language changed!", buttons=kb_welcome(uid)); return

        # NOTIFICATIONS
        if data == "notif_menu":
            if not feat_notifications(): await event.answer("❌", alert=True); return
            await safe_edit(event, f"🔔 **NOTIFICATIONS**\n{DIV}", buttons=kb_notif_menu(uid)); return
        if data == "notif:list":
            notifs = db_get_notifications(uid, 10)
            txt = f"📬 **NOTIFICATIONS**\n{DIV}\n\n"
            if not notifs: txt += "_None_"
            for n in notifs:
                icon = "📭" if n[2] else "📬"
                txt += f"{icon} {n[1]}\n"
            await safe_edit(event, txt[:4000], buttons=kb_notif_menu(uid)); return
        if data == "notif:read":
            db_mark_notifications_read(uid)
            await event.answer("✅ Read", alert=True)
            await safe_edit(event, "✅ All read", buttons=kb_notif_menu(uid)); return

        # MANUAL REACTIONS
        if data == "react_flow":
            if not feat_manual(): await event.answer("💎 PAID!", alert=True); return
            USER_STATES[uid] = {"step": "wait_chat_type"}
            await safe_edit(event, f"💫 **{L(uid, 'send_reactions').upper()}**\n\n{L(uid, 'chat_type')}",
                            buttons=kb_chat_type(uid)); return
        if data == "chattype:channel":
            USER_STATES[uid] = {"step": "wait_channel", "chat_type": "channel"}
            await safe_edit(event, f"📢 {L(uid, 'chat_link')}:", buttons=kb_back(uid)); return
        if data == "chattype:group":
            USER_STATES[uid] = {"step": "wait_channel", "chat_type": "group"}
            await safe_edit(event, f"👥 {L(uid, 'chat_link')}:", buttons=kb_back(uid)); return
        if data == "emoji:default":
            state = USER_STATES.get(uid, {})
            state["emoji_mode"] = "default"; state["custom_emojis"] = None
            USER_STATES[uid] = state
            await event.answer("🎯", alert=True)
            await _run_reactions(event, uid); return
        if data == "emoji:custom":
            if not feat_custom_emoji(): await event.answer("💎 PAID!", alert=True); return
            state = USER_STATES.get(uid, {}); state["step"] = "wait_custom_emoji"
            USER_STATES[uid] = state
            await safe_edit(event, "✏️ Send emojis:", buttons=kb_back(uid)); return
        if data == "emoji:packs":
            await safe_edit(event, f"🎨 **PACKS**\n{DIV}", buttons=kb_emoji_packs(uid)); return
        if data.startswith("pack:"):
            pkey = data.split(":")[1]
            if pkey not in EMOJI_PACKS: return
            state = USER_STATES.get(uid, {})
            state["custom_emojis"] = EMOJI_PACKS[pkey]; state["emoji_mode"] = "custom"
            USER_STATES[uid] = state
            await event.answer(f"✅ {pkey.title()}", alert=True)
            if state.get("reaction_count"): await _run_reactions(event, uid)
            else: await safe_edit(event, f"✅ Loaded!", buttons=kb_back(uid))
            return
        if data.startswith("cpack:"):
            cpid = int(data.split(":")[1])
            for p in db_list_custom_packs():
                if p[0] == cpid:
                    state = USER_STATES.get(uid, {})
                    state["custom_emojis"] = p[2].split(","); state["emoji_mode"] = "custom"
                    USER_STATES[uid] = state
                    await event.answer(f"✅ {p[1]}", alert=True)
                    if state.get("reaction_count"): await _run_reactions(event, uid)
                    else: await safe_edit(event, f"✅ Loaded!", buttons=kb_back(uid))
                    return
            return
        if data == "emoji:templates":
            await safe_edit(event, f"📝 **TEMPLATES**\n{DIV}", buttons=kb_templates_menu(uid)); return
        if data == "rc:all":
            if not OWNER_IS(uid): return
            count = len(db_list_bots())
            state = USER_STATES.get(uid, {}); state["reaction_count"] = count
            USER_STATES[uid] = state
            await event.answer(f"✅ ALL {count}", alert=True)
            await safe_edit(event, f"🎯 Count: **{count}**", buttons=kb_emoji_choice(uid)); return
        if data.startswith("rc:"):
            try: count = int(data.split(":")[1])
            except Exception: return
            visible = db_count_visible_bots()
            if not OWNER_IS(uid):
                limit = get_user_limit(uid)
                if count > limit: await event.answer(f"❌ Max {limit}", alert=True); return
            actual = min(count, visible if not OWNER_IS(uid) else db_count_bots())
            await event.answer(f"✅ {actual}", alert=True)
            state = USER_STATES.get(uid, {}); state["reaction_count"] = actual
            USER_STATES[uid] = state
            await safe_edit(event, f"🎯 Count: **{actual}**", buttons=kb_emoji_choice(uid)); return
        if data == "rc_more":
            limit = get_user_limit(uid)
            await event.answer(f"💎 More than {limit}", alert=True)
            await safe_edit(event, f"💎 Upgrade:", buttons=kb_plans_menu(uid)); return

        # AUTO-WATCH
        if data == "watch_flow":
            if not feat_autowatch(): await event.answer("💎 PAID!", alert=True); return
            await safe_edit(event, f"📡 **AUTO-WATCH**", buttons=kb_watch_menu(uid)); return
        if data == "watch:add":
            USER_STATES[uid] = {"step": "watch_wait_chat_type"}
            await safe_edit(event, f"📡 {L(uid, 'chat_type')}",
                buttons=[[btn(f"📢 {L(uid, 'channel')}", data=b"watch:chattype:channel", style="primary")],
                         [btn(f"👥 {L(uid, 'group')}", data=b"watch:chattype:group", style="success")],
                         [btn(f"🔙 {L(uid, 'cancel')}", data=b"watch_flow", style="danger")]])
            return
        if data == "watch:chattype:channel":
            USER_STATES[uid] = {"step": "watch_wait_link", "chat_type": "channel"}
            await safe_edit(event, f"📢 {L(uid, 'chat_link')}:", buttons=kb_back(uid)); return
        if data == "watch:chattype:group":
            USER_STATES[uid] = {"step": "watch_wait_link", "chat_type": "group"}
            await safe_edit(event, f"👥 {L(uid, 'chat_link')}:", buttons=kb_back(uid)); return
        if data == "watch:list":
            watchers = db_list_watchers(uid if not OWNER_IS(uid) else None)
            if not watchers:
                await safe_edit(event, "📋 No watchers.", buttons=kb_watch_menu(uid)); return
            txt = f"📋 **MY WATCHES ({len(watchers)})**\n{DIV}\n\n"
            rows = []
            for w in watchers[:10]:
                wid, wuid, cid, ct, cl, cty, rc, em, ce, lpid, act, cr, lr = w
                st = "🟢" if act else "🔴"
                txt += f"{st} **#{wid}** {ct} • {rc}x\n"
                if len(rows) < 10:
                    rows.append([btn(f"⚙️ #{wid} {ct[:15]}", data=f"watch:manage:{wid}".encode(), style="primary")])
            rows.append([btn(f"🔙 {L(uid, 'back')}", data=b"watch_flow", style="primary")])
            await safe_edit(event, txt[:4000], buttons=rows); return
        if data.startswith("watch:manage:"):
            wid = int(data.split(":")[2]); w = db_get_watcher(wid)
            if not w or (not OWNER_IS(uid) and w[1] != uid):
                await event.answer("❌", alert=True); return
            wid, wuid, cid, ct, cl, cty, rc, em, ce, lpid, act, cr, lr = w
            st = "🟢 ACTIVE" if act else "🔴 PAUSED"
            await safe_edit(event,
                f"📡 **WATCH #{wid}**\n{DIV}\n\n📢 {ct}\n🎯 {rc}\n✏️ {em}\n📊 Last: **#{lpid}**\n🔄 {st}",
                buttons=[[btn("🔴 OFF" if act else "🟢 ON", data=f"watch:toggle:{wid}".encode(),
                              style="danger" if act else "success")],
                         [btn("✏️ Count", data=f"watch:edit_count:{wid}".encode(), style="primary")],
                         [btn("✏️ Emoji", data=f"watch:edit_emoji:{wid}".encode(), style="primary")],
                         [btn("🗑️ Delete", data=f"watch:delete:{wid}".encode(), style="danger")],
                         [btn(f"🔙 {L(uid, 'back')}", data=b"watch:list", style="primary")]])
            return
        if data.startswith("watch:toggle:"):
            wid = int(data.split(":")[2]); w = db_get_watcher(wid)
            if not w or (not OWNER_IS(uid) and w[1] != uid): return
            db_update_watcher(wid, is_active=0 if w[10] else 1)
            await event.answer("✅", alert=True)
            await safe_edit(event, "Updated", buttons=[[btn("🔙", data=f"watch:manage:{wid}".encode(), style="primary")]])
            return
        if data.startswith("watch:edit_count:"):
            wid = int(data.split(":")[2])
            USER_STATES[uid] = {"step": "watch_edit_count", "wid": wid}
            await safe_edit(event, "✏️ Count (1-200):", buttons=kb_back(uid)); return
        if data.startswith("watch:edit_emoji:"):
            wid = int(data.split(":")[2])
            await safe_edit(event, "✏️ Emoji mode:",
                buttons=[[btn("🎯 Default", data=f"watch:emoji:default:{wid}".encode(), style="success")],
                         [btn("✏️ Custom", data=f"watch:emoji:custom:{wid}".encode(), style="primary")],
                         [btn("🔙 Back", data=f"watch:manage:{wid}".encode(), style="danger")]])
            return
        if data.startswith("watch:emoji:default:"):
            wid = int(data.split(":")[3])
            db_update_watcher(wid, emoji_mode="default", custom_emojis=None)
            await event.answer("✅", alert=True)
            await safe_edit(event, "✅", buttons=[[btn("🔙", data=f"watch:manage:{wid}".encode(), style="primary")]])
            return
        if data.startswith("watch:emoji:custom:"):
            wid = int(data.split(":")[3])
            USER_STATES[uid] = {"step": "watch_edit_emoji", "wid": wid}
            await safe_edit(event, "✏️ Send emojis:", buttons=kb_back(uid)); return
        if data.startswith("watch:delete:"):
            wid = int(data.split(":")[2]); w = db_get_watcher(wid)
            if not w or (not OWNER_IS(uid) and w[1] != uid): return
            db_delete_watcher(wid)
            await event.answer("🗑️", alert=True)
            await safe_edit(event, "✅ Deleted", buttons=kb_watch_menu(uid)); return
        if data == "watch_emoji:default":
            state = USER_STATES.get(uid, {}); state["watch_custom_emojis"] = None
            USER_STATES[uid] = state
            await event.answer("🎯", alert=True)
            await _finalize_watch_add(event, uid); return
        if data == "watch_emoji:custom":
            state = USER_STATES.get(uid, {}); state["step"] = "watch_wait_custom_emoji"
            USER_STATES[uid] = state
            await safe_edit(event, "✏️ Send emojis:", buttons=kb_back(uid)); return

        # ═══ OWNER PANEL ═══
        if data == "owner_panel":
            if not OWNER_IS(uid): return
            await event.answer("👑")
            busy = sum(1 for t, i in BOT_POOL.items() if isinstance(i, dict) and i.get("busy_until") and i["busy_until"] > datetime.now())
            flooded = sum(1 for t in FLOOD_UNTIL if FLOOD_UNTIL[t] > datetime.now())
            await safe_edit(event,
                f"👑 **OWNER PANEL**\n{DIV}\n\n"
                f"👥 Users: **{db_total_users()}**\n💫 Reactions: **{db_total_reactions()}**\n"
                f"📅 Today: **{db_reactions_today()}**\n🤖 Bots: **{db_count_visible_bots()}**\n"
                f"🔴 Busy: **{busy}**  🌊 Flooded: **{flooded}**\n"
                f"📡 Watchers: **{len(db_list_watchers())}**\n"
                f"⏰ Queue: **{len(db_list_queue(status='pending'))}**\n"
                f"🔓 Auto: **{'✅' if is_auto_approve() else '❌'}**\n"
                f"🎁 Free: **{get_free_count()}**",
                buttons=kb_owner()); return

        if data == "op:owner_info":
            if not OWNER_IS(uid): return
            await safe_edit(event,
                f"👤 **OWNER INFO**\n{DIV}\n\n"
                f"👑 Username: @{get_owner_username()}\n"
                f"🆔 Owner ID: `{get_owner_id()}`\n\n"
                f"Ye info welcome aur admin-needed messages mein use hoti hai.",
                buttons=[[btn("✏️ Edit Username", data=b"oi:edit_uname", style="primary")],
                         [btn("✏️ Edit Owner ID", data=b"oi:edit_oid", style="primary")],
                         [btn("🔙 Back", data=b"owner_panel", style="primary")]])
            return
        if data == "oi:edit_uname":
            if not OWNER_IS(uid): return
            USER_STATES[uid] = {"step": "oi_wait_uname"}
            await safe_edit(event, "✏️ Send new owner username (without @):", buttons=kb_owner()); return
        if data == "oi:edit_oid":
            if not OWNER_IS(uid): return
            USER_STATES[uid] = {"step": "oi_wait_oid"}
            await safe_edit(event, "✏️ Send new owner Telegram ID:", buttons=kb_owner()); return

        # Payment Methods
        if data == "op:pm":
            if not OWNER_IS(uid): return
            await safe_edit(event,
                f"💳 **PAYMENT METHODS**\n{DIV}\n\nTotal: **{len(db_payment_list(active_only=False))}**",
                buttons=kb_payment_methods_manage()); return
        if data == "pm:add":
            if not OWNER_IS(uid): return
            USER_STATES[uid] = {"step": "pm_wait_name"}
            await safe_edit(event, "✏️ Payment method **name** (e.g., JazzCash):",
                            buttons=[[btn("🔙 Cancel", data=b"op:pm", style="danger")]])
            return
        if data.startswith("pm:view:"):
            if not OWNER_IS(uid): return
            mid = int(data.split(":")[2]); m = db_payment_get(mid)
            if not m: await event.answer("❌", alert=True); return
            mid, key, name, number, holder, icon, instr, act, so = m
            await safe_edit(event,
                f"💳 **METHOD #{mid}**\n{DIV}\n\n"
                f"{icon} Name: **{name}**\n🔢 Number: `{number}`\n"
                f"👤 Holder: **{holder}**\n"
                f"📝 Instructions: {instr or '_none_'}\n"
                f"🟢 Active: **{'YES' if act else 'NO'}**",
                buttons=kb_payment_method_edit(mid)); return
        if data.startswith("pm:edit_name:"):
            if not OWNER_IS(uid): return
            mid = int(data.split(":")[2])
            USER_STATES[uid] = {"step": "pm_edit_name", "mid": mid}
            await safe_edit(event, "✏️ New name:", buttons=[[btn("🔙", data=f"pm:view:{mid}".encode(), style="primary")]]); return
        if data.startswith("pm:edit_number:"):
            if not OWNER_IS(uid): return
            mid = int(data.split(":")[2])
            USER_STATES[uid] = {"step": "pm_edit_number", "mid": mid}
            await safe_edit(event, "✏️ New number/address:", buttons=[[btn("🔙", data=f"pm:view:{mid}".encode(), style="primary")]]); return
        if data.startswith("pm:edit_holder:"):
            if not OWNER_IS(uid): return
            mid = int(data.split(":")[2])
            USER_STATES[uid] = {"step": "pm_edit_holder", "mid": mid}
            await safe_edit(event, "✏️ New holder name:", buttons=[[btn("🔙", data=f"pm:view:{mid}".encode(), style="primary")]]); return
        if data.startswith("pm:edit_icon:"):
            if not OWNER_IS(uid): return
            mid = int(data.split(":")[2])
            USER_STATES[uid] = {"step": "pm_edit_icon", "mid": mid}
            await safe_edit(event, "✏️ New icon emoji:", buttons=[[btn("🔙", data=f"pm:view:{mid}".encode(), style="primary")]]); return
        if data.startswith("pm:toggle:"):
            if not OWNER_IS(uid): return
            mid = int(data.split(":")[2]); db_payment_toggle(mid)
            await event.answer("✅", alert=True)
            m = db_payment_get(mid)
            mid, key, name, number, holder, icon, instr, act, so = m
            await safe_edit(event,
                f"💳 **METHOD #{mid}**\n{DIV}\n\n{icon} **{name}**\n"
                f"🔢 `{number}`\n👤 {holder}\n🟢 Active: **{'YES' if act else 'NO'}**",
                buttons=kb_payment_method_edit(mid)); return
        if data.startswith("pm:del:"):
            if not OWNER_IS(uid): return
            mid = int(data.split(":")[2]); db_payment_delete(mid)
            await event.answer("🗑️ Deleted", alert=True)
            await safe_edit(event, "Deleted", buttons=kb_payment_methods_manage()); return

        # Real Accounts
        if data == "op:ra":
            if not OWNER_IS(uid): return
            files = discover_session_files(); total = len(files); avail = real_count_available()
            flooded = sum(1 for f in files if is_real_flooded(f))
            await safe_edit(event,
                f"👤 **SESSIONS**\n{DIV}\n\n"
                f"📊 Total: **{total}**\n🟢 Available: **{avail}**\n🌊 Flooded: **{flooded}**\n\n"
                f"⚙️ Feature: **{'✅ ON' if feat_realaccounts() else '❌ OFF'}**",
                buttons=[
                    [btn("🔄 Refresh", data=b"op:ra", style="success"),
                     btn("🧪 Test All", data=b"ra:testall", style="primary")],
                    [btn(f"⚙️ {'OFF' if feat_realaccounts() else 'ON'}",
                          data=b"ra:toggle", style="danger")],
                    [btn("📋 List", data=b"ra:list", style="primary"),
                     btn("🧹 Clear Flood", data=b"ra:clearflood", style="danger")],
                    [btn("🔙 Back", data=b"owner_panel", style="primary")]])
            return
        if data == "op:ra_redl":
            if not OWNER_IS(uid): return
            await event.answer("🔄", alert=True)
            ok, msg = github_sync.download_sessions()
            await safe_edit(event, f"✅ **{msg}**",
                buttons=[[btn("🔙", data=b"op:ra", style="primary")]]); return
        if data == "ra:list":
            if not OWNER_IS(uid): return
            files = discover_session_files()
            if not files:
                await safe_edit(event, "📋 No sessions.",
                    buttons=[[btn("🔙", data=b"op:ra", style="primary")]]); return
            txt = f"📋 **SESSIONS ({len(files)})**\n{DIV}\n\n"
            for f in files[:30]:
                st = "🌊" if is_real_flooded(f) else "🟢"
                txt += f"{st} `{f}`\n"
            if len(files) > 30: txt += f"\n...+{len(files) - 30}"
            await safe_edit(event, txt[:4000], buttons=[[btn("🔙", data=b"op:ra", style="primary")]]); return
        if data == "ra:testall":
            if not OWNER_IS(uid): return
            await event.answer("🧪 Testing...", alert=True)
            files = discover_session_files()
            if not files:
                await safe_edit(event, "❌ No sessions.",
                    buttons=[[btn("🔙", data=b"op:ra", style="primary")]]); return
            txt = f"🧪 **TEST RESULTS**\n{DIV}\n\n"; ok_n = 0
            for f in files[:15]:
                c = await get_real_client(f)
                if c:
                    try:
                        me = await c.get_me()
                        txt += f"✅ `{f}` — {me.first_name} (@{getattr(me, 'username', '—')})\n"
                        ok_n += 1
                    except Exception as e: txt += f"⚠️ `{f}` — {str(e)[:30]}\n"
                else: txt += f"❌ `{f}` — Login failed\n"
            txt += f"\n\n**Working: {ok_n}/{min(len(files), 15)}**"
            await safe_edit(event, txt[:4000], buttons=[[btn("🔙", data=b"op:ra", style="primary")]]); return
        if data == "ra:toggle":
            if not OWNER_IS(uid): return
            nv = cfg_toggle("realaccounts_enabled")
            await event.answer(f"{'✅ ON' if nv else '❌ OFF'}", alert=True)
            await safe_edit(event, "Updated", buttons=[[btn("🔙", data=b"op:ra", style="primary")]]); return
        if data == "ra:clearflood":
            if not OWNER_IS(uid): return
            REAL_FLOOD_UNTIL.clear()
            await event.answer("✅", alert=True)
            await safe_edit(event, "🧹 Cleared", buttons=[[btn("🔙", data=b"op:ra", style="primary")]]); return

        if data == "op:ra_plans":
            if not OWNER_IS(uid): return
            rows = []
            for p in ["free", "basic", "pro", "premium"]:
                has = plan_has_realaccounts(p); lim = plan_ra_limit(p)
                st = "✅" if has else "❌"
                rows.append([btn(f"{st} {PLAN_NAMES[p]} — {lim}",
                                  data=f"ra:p:{p}".encode(),
                                  style="success" if has else "danger")])
            rows.append([btn("🔙 Back", data=b"owner_panel", style="primary")])
            await safe_edit(event,
                f"⚙️ **PLAN ACCESS**\n{DIV}\n\nTap plan → ON/OFF + Limit",
                buttons=rows); return
        if data.startswith("ra:p:"):
            if not OWNER_IS(uid): return
            plan = data.split(":")[2]
            has = plan_has_realaccounts(plan); lim = plan_ra_limit(plan)
            await safe_edit(event,
                f"⚙️ **{PLAN_NAMES[plan]}**\n{DIV}\n\n"
                f"Feature: **{'✅ ON' if has else '❌ OFF'}**\nSession Limit: **{lim}**",
                buttons=[[btn(f"{'❌ OFF' if has else '✅ ON'}", data=f"ra:ptog:{plan}".encode(),
                              style="danger" if has else "success")],
                         [btn("✏️ Set Limit", data=f"ra:plim:{plan}".encode(), style="primary")],
                         [btn("🔙 Back", data=b"op:ra_plans", style="primary")]])
            return
        if data.startswith("ra:ptog:"):
            if not OWNER_IS(uid): return
            plan = data.split(":")[2]; nv = toggle_plan_realaccounts(plan)
            await event.answer(f"{'✅' if nv else '❌'}", alert=True)
            await safe_edit(event, "Updated",
                buttons=[[btn("🔙", data=f"ra:p:{plan}".encode(), style="primary")]]); return
        if data.startswith("ra:plim:"):
            if not OWNER_IS(uid): return
            plan = data.split(":")[2]
            USER_STATES[uid] = {"step": "ra_set_plan_limit", "plan": plan}
            await safe_edit(event, f"✏️ Limit for {PLAN_NAMES[plan]} (0-100):",
                buttons=[[btn("🔙 Cancel", data=f"ra:p:{plan}".encode(), style="danger")]]); return

        # GitHub (generic label — no mention of real repo names to users)
        if data == "op:ghsync":
            if not OWNER_IS(uid): return
            s = github_sync.get_stats()
            await safe_edit(event,
                f"🔄 **AUTO BACKUP**\n{DIV}\n\n"
                f"📊 Uploads: **{s['uploads']}**\n"
                f"📥 Downloads: **{s['downloads']}**\n"
                f"❌ Errors: **{s['errors']}**\n"
                f"🕒 Last: **{s['last_sync'] or '—'}**\n"
                f"📝 `{s['last_msg']}`\n"
                f"🟡 Dirty: **{'YES' if s['dirty'] else 'NO'}**",
                buttons=[[btn("⬆️ Push Now", data=b"gh:push", style="success"),
                          btn("⬇️ Pull Now", data=b"gh:pull", style="primary")],
                         [btn("👤 Re-Download Sessions", data=b"op:ra_redl", style="success")],
                         [btn("🔙 Back", data=b"owner_panel", style="primary")]])
            return
        if data == "gh:push":
            if not OWNER_IS(uid): return
            await event.answer("⬆️", alert=True)
            ok, msg = github_sync.upload_db(force=True)
            await safe_edit(event, f"{'✅' if ok else '❌'} {msg}",
                buttons=[[btn("🔙", data=b"op:ghsync", style="primary")]]); return
        if data == "gh:pull":
            if not OWNER_IS(uid): return
            await event.answer("⬇️", alert=True)
            ok, msg = github_sync.download_db()
            await safe_edit(event, f"{'✅' if ok else '❌'} {msg}",
                buttons=[[btn("🔙", data=b"op:ghsync", style="primary")]]); return

        if data == "op:analytics":
            if not OWNER_IS(uid): return
            dd = db_reactions_by_day(7); tu = db_top_users_by_reactions(5)
            chart = ""; mx = max([n for _, n in dd], default=1)
            for d, n in dd:
                bl = int((n / mx) * 10) if mx > 0 else 0
                chart += f"`{d[5:]}` {'█' * bl + '░' * (10 - bl)} {n}\n"
            txt = f"📊 **ANALYTICS**\n{DIV}\n\n{chart}\n{DIV}\n\n**Top Users:**\n"
            for i, u_d in enumerate(tu, 1): txt += f"{i}. {u_d[1] or '—'} — **{u_d[2]}**\n"
            await safe_edit(event, txt[:4000], buttons=kb_owner()); return
        if data == "op:revenue":
            if not OWNER_IS(uid): return
            t, tr, mr = db_revenue_stats()
            await safe_edit(event, f"💰 **REVENUE**\n{DIV}\n\n📅 Today: **{tr}rs**\n📆 Month: **{mr}rs**\n💎 Total: **{t}rs**",
                            buttons=kb_owner()); return
        if data == "op:payments":
            if not OWNER_IS(uid): return
            pend = db_list_payments(status="pending", l=10)
            if not pend:
                await safe_edit(event, "✅ No pending.", buttons=kb_owner()); return
            for p in pend[:5]:
                try:
                    await bot.send_message(get_owner_id(),
                        f"💳 **PAYMENT #{p[0]}**\n👤 `{p[1]}`\n💰 {p[2]}rs — {p[3]} {p[4]}d",
                        buttons=kb_payment_actions(p[0]))
                    await asyncio.sleep(0.3)
                except Exception: pass
            await safe_edit(event, f"⏳ {len(pend)} sent.", buttons=kb_owner()); return
        if data.startswith("payv:"):
            if not OWNER_IS(uid): return
            parts = data.split(":"); action = parts[1]; pid = int(parts[2])
            payment = db_get_payment(pid)
            if not payment: await event.answer("❌", alert=True); return
            if action == "approve":
                db_update_payment(pid, status="approved",
                                  verified_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                  verified_by=get_owner_id())
                tuid = payment[1]; pk = payment[3]; ds = payment[4]
                db_set_user_plan(tuid, pk, ds)
                await event.answer("✅", alert=True)
                try: await bot.send_message(tuid, f"🎉 **PLAN ACTIVATED!**\n📦 {PLAN_NAMES.get(pk, pk)}\n📅 {DURATIONS.get(ds, ds)}")
                except Exception: pass
            else:
                db_update_payment(pid, status="rejected",
                                  verified_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                  verified_by=get_owner_id())
                await event.answer("❌", alert=True)
            return

        if data == "op:queue":
            if not OWNER_IS(uid): return
            pend = db_list_queue(status="pending")
            txt = f"⏰ **QUEUE ({len(pend)})**\n{DIV}\n\n"
            for j in pend[:10]: txt += f"⏳ **#{j[0]}** `{j[1]}` — {j[4]}x\n"
            await safe_edit(event, txt[:4000], buttons=kb_owner()); return
        if data == "op:force_channels":
            if not OWNER_IS(uid): return
            await safe_edit(event, f"📢 **FORCE CHANNELS**\n{DIV}", buttons=kb_force_channels()); return
        if data.startswith("fc:toggle:"):
            if not OWNER_IS(uid): return
            db_toggle_force_channel(int(data.split(":")[2]))
            await event.answer("✅", alert=True)
            await safe_edit(event, "Updated", buttons=kb_force_channels()); return
        if data.startswith("fc:del:"):
            if not OWNER_IS(uid): return
            db_delete_force_channel(int(data.split(":")[2]))
            await event.answer("🗑️", alert=True)
            await safe_edit(event, "Deleted", buttons=kb_force_channels()); return
        if data == "fc:add":
            if not OWNER_IS(uid): return
            USER_STATES[uid] = {"step": "fc_wait_channel"}
            await safe_edit(event, "📢 Send @channel:", buttons=kb_owner()); return
        if data == "op:team":
            if not OWNER_IS(uid): return
            await safe_edit(event, f"👥 **TEAM**\n{DIV}", buttons=kb_team()); return
        if data == "team:add":
            if not OWNER_IS(uid): return
            USER_STATES[uid] = {"step": "team_wait_id"}
            await safe_edit(event, "👤 Send user ID:", buttons=kb_owner()); return
        if data.startswith("team:view:"):
            if not OWNER_IS(uid): return
            target = int(data.split(":")[2]); m = db_get_team_member(target)
            if not m: await event.answer("❌", alert=True); return
            await safe_edit(event, f"👤 `{m[0]}`\n👑 {m[1]}\n💰 {m[3]}%",
                buttons=[[btn("🗑️ Remove", data=f"team:del:{target}".encode(), style="danger")],
                         [btn("🔙", data=b"op:team", style="primary")]]); return
        if data.startswith("team:del:"):
            if not OWNER_IS(uid): return
            db_remove_team_member(int(data.split(":")[2]))
            await event.answer("✅", alert=True)
            await safe_edit(event, "Removed", buttons=kb_team()); return
        if data == "op:emoji_packs":
            if not OWNER_IS(uid): return
            await safe_edit(event, f"🎨 **CUSTOM PACKS**\n{DIV}", buttons=kb_emoji_packs_manage()); return
        if data == "cp:new":
            if not OWNER_IS(uid): return
            USER_STATES[uid] = {"step": "cp_wait_name"}
            await safe_edit(event, "🎨 Pack name:", buttons=kb_owner()); return
        if data.startswith("cp:del:"):
            if not OWNER_IS(uid): return
            db_delete_custom_pack(int(data.split(":")[2]))
            await event.answer("🗑️", alert=True)
            await safe_edit(event, "Deleted", buttons=kb_emoji_packs_manage()); return
        if data == "op:features":
            if not OWNER_IS(uid): return
            await event.answer("🎛️")
            await safe_edit(event, f"🎛️ **FEATURES**\n{DIV}", buttons=kb_features()); return
        if data.startswith("ft:toggle:"):
            if not OWNER_IS(uid): return
            key = data.split(":", 2)[2]; nv = cfg_toggle(key)
            await event.answer(f"{'✅' if nv else '❌'}", alert=True)
            await safe_edit(event, f"🎛️ **FEATURES**\n{DIV}", buttons=kb_features()); return
        if data == "op:plan_prices":
            if not OWNER_IS(uid): return
            await safe_edit(event, f"💰 **PRICES**\n{DIV}", buttons=kb_plan_prices()); return
        if data.startswith("pp:plan:"):
            if not OWNER_IS(uid): return
            plan = data.split(":")[2]
            await safe_edit(event, f"💰 **{PLAN_NAMES[plan]}**", buttons=kb_plan_prices_durations(plan)); return
        if data.startswith("pp:edit:"):
            if not OWNER_IS(uid): return
            parts = data.split(":"); plan = parts[2]; days = int(parts[3])
            USER_STATES[uid] = {"step": "pp_edit_price", "plan": plan, "days": days}
            await safe_edit(event, f"✏️ Price for {PLAN_NAMES[plan]} {DURATIONS[days]}:", buttons=kb_back(uid)); return
        if data == "op:paid_features":
            if not OWNER_IS(uid): return
            await safe_edit(event, f"💎 **PAID FEATURES**\n{DIV}", buttons=kb_paid_features()); return
        if data.startswith("pf:toggle:"):
            if not OWNER_IS(uid): return
            feature = data.split(":", 2)[2]; nv = cfg_toggle(f"paid_{feature}")
            await event.answer("💎 PAID" if nv else "🆓 FREE", alert=True)
            await safe_edit(event, f"💎 **PAID**\n{DIV}", buttons=kb_paid_features()); return
        if data == "op:referrals":
            if not OWNER_IS(uid): return
            try:
                conn = sqlite3.connect(DB_FILE)
                tr = conn.execute("SELECT COUNT(*) FROM referrals WHERE status='validated'").fetchone()[0]
                pd = conn.execute("SELECT COUNT(*) FROM referrals WHERE status='pending'").fetchone()[0]
                conn.close()
            except Exception: tr = pd = 0
            await safe_edit(event, f"🎁 **REFERRALS**\n{DIV}\n\n✅ {tr}\n⏳ {pd}", buttons=kb_owner()); return
        if data == "op:pool_status":
            if not OWNER_IS(uid): return
            now = datetime.now()
            allb = db_list_bots(); tot = len(allb)
            perm = sum(1 for b in allb if is_permanent_admin(b[1]))
            fl = sum(1 for t in FLOOD_UNTIL if FLOOD_UNTIL[t] > now)
            busy = free = 0
            for tok, uname, bid, added in allb:
                if is_permanent_admin(uname): continue
                if tok in FLOOD_UNTIL and FLOOD_UNTIL[tok] > now: continue
                info = BOT_POOL.get(tok)
                if isinstance(info, dict) and info.get("busy_until") and info["busy_until"] > now: busy += 1
                else: free += 1
            await safe_edit(event,
                f"📊 **POOL**\n{DIV}\n\n🤖 {tot}\n🔒 Perm: {perm}\n🟢 Free: {free}\n"
                f"🔴 Busy: {busy}\n🌊 Flood: {fl}\n\n"
                f"⏱️ Task: **{'🔴 RUNNING' if TASK_RUNNING else '🟢 IDLE'}**",
                buttons=kb_owner()); return
        if data == "op:reset_pool":
            if not OWNER_IS(uid): return
            op = len(BOT_POOL); of = len(FLOOD_UNTIL)
            BOT_POOL.clear(); FLOOD_UNTIL.clear()
            TASK_RUNNING = False; TASK_OWNER_UID = None
            await event.answer("✅", alert=True)
            await safe_edit(event, f"🧹 Pool: {op}, Flood: {of}", buttons=kb_owner()); return
        if data == "op:toggle_auto":
            if not OWNER_IS(uid): return
            nv = not is_auto_approve(); set_auto_approve(nv)
            await event.answer(f"{'✅' if nv else '❌'}", alert=True)
            await safe_edit(event, f"👑 Auto: **{'✅ ON' if nv else '❌ OFF'}**", buttons=kb_owner()); return
        if data == "op:setfree":
            if not OWNER_IS(uid): return
            USER_STATES[uid] = {"step": "wait_setfree"}
            await safe_edit(event, f"⚙️ Current: {get_free_count()}\nSend new:", buttons=kb_owner()); return
        if data == "op:bots":
            if not OWNER_IS(uid): return
            bs = db_list_visible_bots(); txt = f"🤖 **BOTS ({len(bs)})**\n\n"
            now = datetime.now()
            for i, r in enumerate(bs[:30], 1):
                tok = r[0]; info = BOT_POOL.get(tok); st = "🟢"
                if is_bot_flooded(tok): st = "🌊"
                elif isinstance(info, dict) and info.get("busy_until") and info["busy_until"] > now: st = "🔴"
                txt += f"{st} **{i}.** @{r[1]}\n"
            if len(bs) > 30: txt += f"\n...+{len(bs) - 30}"
            await safe_edit(event, txt[:4000], buttons=kb_owner()); return
        if data == "op:users":
            if not OWNER_IS(uid): return
            rows = db_all_users(10, 0)
            txt = f"👥 **USERS**\n\n"; br = []
            for r in rows:
                ic = "🚫" if r[5] else "✅"
                lim = get_user_limit(r[0])
                txt += f"{ic} **{r[1] or '—'}** `{r[0]}` 🎁 {lim}\n"
                br.append([btn(f"⚙️ {r[1] or 'User'}", data=f"um:panel:{r[0]}".encode(), style="primary")])
            br.append([btn("🔙", data=b"owner_panel", style="danger")])
            await safe_edit(event, txt[:4000], buttons=br); return
        if data.startswith("um:panel:"):
            if not OWNER_IS(uid): return
            target = int(data.split(":")[2]); u = db_get_user_full(target)
            if not u: await event.answer("❌", alert=True); return
            await event.answer("⚙️")
            plan = u[15] or "free"; fb = u[17] or 0
            ra_lbl = "Plan"
            try:
                if len(u) > 26 and u[26] >= 0: ra_lbl = u[26]
            except Exception: pass
            await safe_edit(event,
                f"⚙️ **USER**\n{DIV}\n\n👤 **{u[1] or '—'}**\n🆔 `{u[0]}`\n"
                f"Status: {'BANNED' if u[5] else 'Active'}\n💰 {plan}\n💎 {fb}\n👤 RA: {ra_lbl}",
                buttons=kb_user_manage(target)); return
        if data.startswith("um:ban:"):
            if not OWNER_IS(uid): return
            target = int(data.split(":")[2]); u = db_get_user_full(target)
            nb = not u[5]; db_ban_user(target, ban=nb)
            await event.answer(f"{'🚫' if nb else '✅'}", alert=True)
            await safe_edit(event, "Updated", buttons=kb_user_manage(target)); return
        if data.startswith("um:limit:"):
            if not OWNER_IS(uid): return
            target = int(data.split(":")[2])
            USER_STATES[uid] = {"step": "user_set_limit", "target": target}
            await safe_edit(event, "✏️ Limit:", buttons=kb_owner()); return
        if data.startswith("um:plan:"):
            if not OWNER_IS(uid): return
            target = int(data.split(":")[2])
            await safe_edit(event, f"💰 **PLAN** for `{target}`", buttons=kb_user_plan_durations(target)); return
        if data.startswith("um:activate:"):
            if not OWNER_IS(uid): return
            parts = data.split(":"); pk = parts[2]; ds = int(parts[3]); target = int(parts[4])
            if pk == "free": db_set_user_plan(target, "free", 9999)
            else: db_set_user_plan(target, pk, ds)
            await event.answer("✅", alert=True)
            await safe_edit(event, "✅ Activated", buttons=kb_user_manage(target)); return
        if data.startswith("um:balance:"):
            if not OWNER_IS(uid): return
            target = int(data.split(":")[2])
            USER_STATES[uid] = {"step": "user_add_balance", "target": target}
            await safe_edit(event, "💎 Amount:", buttons=kb_owner()); return
        if data.startswith("um:ra:"):
            if not OWNER_IS(uid): return
            target = int(data.split(":")[2]); u = db_get_user_full(target)
            if not u: await event.answer("❌", alert=True); return
            try: override = u[26] if len(u) > 26 else -1
            except Exception: override = -1
            plan = u[15] or "free"; plan_lim = plan_ra_limit(plan)
            ov_txt = override if override >= 0 else "None (plan)"
            eff = override if override >= 0 else plan_lim
            await safe_edit(event,
                f"👤 **RA LIMIT** for `{target}`\n{DIV}\n\n"
                f"Plan: {PLAN_NAMES.get(plan, plan)}\nPlan limit: **{plan_lim}**\n"
                f"Override: **{ov_txt}**\nEffective: **{eff}**",
                buttons=[[btn("✏️ Set Custom", data=f"um:ra_set:{target}".encode(), style="primary")],
                         [btn("🔄 Reset", data=f"um:ra_reset:{target}".encode(), style="danger")],
                         [btn("🔙", data=f"um:panel:{target}".encode(), style="success")]])
            return
        if data.startswith("um:ra_set:"):
            if not OWNER_IS(uid): return
            target = int(data.split(":")[2])
            USER_STATES[uid] = {"step": "ra_set_user_limit", "target": target}
            await safe_edit(event, f"✏️ RA limit for `{target}` (0-100, -1 reset):",
                buttons=[[btn("🔙", data=f"um:ra:{target}".encode(), style="danger")]]); return
        if data.startswith("um:ra_reset:"):
            if not OWNER_IS(uid): return
            target = int(data.split(":")[2]); set_user_ra_limit(target, -1)
            await event.answer("✅", alert=True)
            await safe_edit(event, "✅ Reset",
                buttons=[[btn("🔙", data=f"um:ra:{target}".encode(), style="primary")]]); return
        if data.startswith("um:team:"):
            if not OWNER_IS(uid): return
            target = int(data.split(":")[2])
            await safe_edit(event, f"👥 Team role for `{target}`",
                buttons=[[btn("👤 User", data=f"um:setteam:user:{target}".encode(), style="primary")],
                         [btn("💼 Reseller", data=f"um:setteam:reseller:{target}".encode(), style="success")],
                         [btn("👑 Sub-Admin", data=f"um:setteam:admin:{target}".encode(), style="danger")],
                         [btn("🔙", data=f"um:panel:{target}".encode(), style="primary")]])
            return
        if data.startswith("um:setteam:"):
            if not OWNER_IS(uid): return
            parts = data.split(":"); role = parts[2]; target = int(parts[3])
            if role == "user": db_remove_team_member(target)
            else: db_add_team_member(target, role, 10 if role == "reseller" else 15)
            await event.answer(f"✅ {role}", alert=True)
            await safe_edit(event, "Updated", buttons=kb_user_manage(target)); return
        for fk in ["channel", "group", "manual", "autowatch", "custom"]:
            if data.startswith(f"um:{fk}:"):
                if not OWNER_IS(uid): return
                target = int(data.split(":")[2]); u = db_get_user_full(target)
                idx = {"channel": 10, "group": 11, "manual": 12, "autowatch": 13, "custom": 14}[fk]
                db_set_user_perm(target, fk if fk != "custom" else "custom_emoji", not u[idx])
                await event.answer("✅", alert=True)
                await safe_edit(event, "Updated", buttons=kb_user_manage(target)); return
        if data.startswith("um:unlock:"):
            if not OWNER_IS(uid): return
            target = int(data.split(":")[2]); u = db_get_user_full(target)
            db_set_user_perm(target, "auto_watch_unlocked", not u[9])
            await event.answer("✅", alert=True)
            await safe_edit(event, "Updated", buttons=kb_user_manage(target)); return
        if data == "op:watchers":
            if not OWNER_IS(uid): return
            ws = db_list_watchers(); txt = f"📡 **ALL WATCHERS ({len(ws)})**\n{DIV}\n\n"
            for w in ws[:15]:
                st = "🟢" if w[10] else "🔴"
                txt += f"{st} **#{w[0]}** {w[3][:25]} • {w[6]}x\n"
            await safe_edit(event, txt[:4000], buttons=kb_owner()); return
        if data == "op:broadcast":
            if not OWNER_IS(uid): return
            ch = await get_admin_chats()
            await safe_edit(event, f"📢 **BROADCAST** ({len(ch)} chats)",
                buttons=[[btn("📝 Text", data=b"bc:text", style="primary")],
                         [btn("🖼️ Photo", data=b"bc:photo", style="success")],
                         [btn("🔙", data=b"owner_panel", style="danger")]])
            return
        if data == "bc:text":
            USER_STATES[uid] = {"step": "wait_bc_text"}
            await safe_edit(event, "📝 Text:", buttons=kb_owner()); return
        if data == "bc:photo":
            USER_STATES[uid] = {"step": "wait_bc_photo"}
            await safe_edit(event, "🖼️ Photo URL:", buttons=kb_owner()); return
        if data == "op:adduser":
            USER_STATES[uid] = {"step": "wait_add_user_id"}
            await safe_edit(event, "➕ Send ID:", buttons=kb_owner()); return
        if data == "op:recent":
            rows = db_recent_reactions(15)
            txt = "📜 **RECENT**\n\n"
            for r in rows:
                ic = "✅" if r[6] == "ok" else "❌"
                m = r[8] if len(r) > 8 else "bot"
                txt += f"{ic} {r[4]} @{r[5]} [{m}]\n"
            await safe_edit(event, txt[:4000] or "_None_", buttons=kb_owner()); return
        if data == "op:pending":
            rows = db_pending_approvals(10)
            if not rows:
                await safe_edit(event, "✅ No pending.", buttons=kb_owner()); return
            for r in rows:
                try:
                    await bot.send_message(get_owner_id(), f"🔔 {r[1]}\n🆔 `{r[0]}`",
                                            buttons=kb_approval_actions(r[0]))
                    await asyncio.sleep(0.4)
                except Exception: pass
            await safe_edit(event, f"⏳ {len(rows)} sent", buttons=kb_owner()); return
        if data == "op:approved":
            rows = db_approved_users(20)
            txt = f"✅ **APPROVED ({len(rows)})**\n\n"
            for r in rows: txt += f"👤 {r[1] or '—'} `{r[0]}`\n"
            await safe_edit(event, txt[:4000], buttons=kb_owner()); return

    except Exception as e:
        D_err(e, "on_cb")
        try: await event.answer("❌ Error", alert=True)
        except Exception: pass


# ══════════════════════ MESSAGE HANDLER ══════════════════════
@bot.on(events.NewMessage)
async def on_msg(event):
    try:
        if event.is_channel: return
        uid = event.sender_id
        if uid is None: return
        if event.text and event.text.startswith("/"): return
        try:
            sender = await event.get_sender()
            if sender is None or isinstance(sender, (Channel, Chat)):
                fn, un = "User", None
            else:
                fn = getattr(sender, "first_name", None) or "User"
                un = getattr(sender, "username", None)
        except Exception: fn, un = "User", None
        db_save_user(uid, fn, un)
        if db_is_banned(uid): return

        if OWNER_IS(uid) and uid in USER_STATES:
            state = USER_STATES[uid]
            step = state.get("step")

            if step == "oi_wait_uname":
                text = event.text.strip().lstrip("@")
                if not text: await event.reply("❌ Invalid"); return
                cfg_set("owner_username", text)
                OWNER_ENTITY_CACHE["entity"] = None; OWNER_ENTITY_CACHE["expires_at"] = None
                del USER_STATES[uid]
                await event.reply(f"✅ Username set: @{text}", buttons=kb_owner()); return
            if step == "oi_wait_oid":
                text = event.text.strip()
                if not text.lstrip("-").isdigit():
                    await event.reply("❌ Numeric ID"); return
                cfg_set("owner_id", int(text))
                del USER_STATES[uid]
                await event.reply(f"✅ Owner ID: `{text}`", buttons=kb_owner()); return
            if step == "pm_wait_name":
                state["pm_name"] = event.text.strip()[:40]; state["step"] = "pm_wait_number"
                USER_STATES[uid] = state
                await event.reply("✏️ Send **number / address**:"); return
            if step == "pm_wait_number":
                state["pm_number"] = event.text.strip()[:100]; state["step"] = "pm_wait_holder"
                USER_STATES[uid] = state
                await event.reply("✏️ Send **holder name**:"); return
            if step == "pm_wait_holder":
                state["pm_holder"] = event.text.strip()[:60]; state["step"] = "pm_wait_icon"
                USER_STATES[uid] = state
                await event.reply("✏️ Send **icon emoji** (or 'skip' for 💳):"); return
            if step == "pm_wait_icon":
                text = event.text.strip()
                icon = "💳" if text.lower() == "skip" else text[:4]
                key = re.sub(r"[^a-z0-9]", "", state["pm_name"].lower())[:20] or f"pm{int(time.time())}"
                mid = db_payment_add(key, state["pm_name"], state["pm_number"], state["pm_holder"], icon)
                del USER_STATES[uid]
                await event.reply(f"✅ Method added (#{mid})", buttons=kb_payment_methods_manage()); return
            if step == "pm_edit_name":
                text = event.text.strip(); mid = state["mid"]
                db_payment_update(mid, name=text[:40]); del USER_STATES[uid]
                await event.reply(f"✅ Updated", buttons=kb_payment_method_edit(mid)); return
            if step == "pm_edit_number":
                text = event.text.strip(); mid = state["mid"]
                db_payment_update(mid, number=text[:100]); del USER_STATES[uid]
                await event.reply(f"✅ Updated", buttons=kb_payment_method_edit(mid)); return
            if step == "pm_edit_holder":
                text = event.text.strip(); mid = state["mid"]
                db_payment_update(mid, holder=text[:60]); del USER_STATES[uid]
                await event.reply(f"✅ Updated", buttons=kb_payment_method_edit(mid)); return
            if step == "pm_edit_icon":
                text = event.text.strip(); mid = state["mid"]
                db_payment_update(mid, icon=text[:4]); del USER_STATES[uid]
                await event.reply(f"✅ Updated", buttons=kb_payment_method_edit(mid)); return
            if step == "ra_set_plan_limit":
                text = event.text.strip()
                if not text.isdigit(): await event.reply("❌ Number"); return
                plan = state["plan"]; cfg_set(f"plan_ra_limit_{plan}", int(text))
                del USER_STATES[uid]
                await event.reply(f"✅ Set: {text}", buttons=[[btn("🔙", data=f"ra:p:{plan}".encode(), style="primary")]]); return
            if step == "ra_set_user_limit":
                text = event.text.strip()
                if not text.lstrip("-").isdigit(): await event.reply("❌ Number"); return
                target = state["target"]; set_user_ra_limit(target, int(text))
                del USER_STATES[uid]
                await event.reply(f"✅ Set {text}", buttons=[[btn("🔙", data=f"um:ra:{target}".encode(), style="primary")]]); return
            if step == "pp_edit_price":
                text = event.text.strip()
                if not text.isdigit(): await event.reply("❌ Number"); return
                cfg_set(f"price_{state['plan']}_{state['days']}", text)
                del USER_STATES[uid]
                await event.reply("✅ Updated!", buttons=kb_plan_prices_durations(state['plan'])); return
            if step == "fc_wait_channel":
                ch = event.text.strip()
                if not ch.startswith("@"): await event.reply("❌ @"); return
                db_add_force_channel(ch, f"https://t.me/{ch[1:]}", ch)
                del USER_STATES[uid]
                await event.reply(f"✅ Added", buttons=kb_force_channels()); return
            if step == "team_wait_id":
                text = event.text.strip()
                if not text.lstrip("-").isdigit(): await event.reply("❌ ID"); return
                USER_STATES[uid] = {"step": "team_wait_commission", "target": int(text)}
                await event.reply("Commission %:", buttons=kb_owner()); return
            if step == "team_wait_commission":
                text = event.text.strip()
                if not text.isdigit(): await event.reply("❌ Number"); return
                db_add_team_member(state['target'], "reseller", int(text))
                del USER_STATES[uid]
                await event.reply("✅ Added", buttons=kb_team()); return
            if step == "cp_wait_name":
                state["cp_name"] = event.text.strip()[:20]; state["step"] = "cp_wait_emojis"
                USER_STATES[uid] = state
                await event.reply("✏️ Emojis:"); return
            if step == "cp_wait_emojis":
                emojis = [p.strip() for p in re.split(r"[,\s]+", event.text.strip()) if p.strip() in ALL_REACTIONS]
                if not emojis: await event.reply("❌ No emojis."); return
                state["cp_emojis"] = emojis[:30]; state["step"] = "cp_wait_price"
                USER_STATES[uid] = state
                await event.reply("💰 Price (0 free):"); return
            if step == "cp_wait_price":
                text = event.text.strip()
                if not text.isdigit(): await event.reply("❌ Number"); return
                price = int(text)
                db_add_custom_pack(state.get("cp_name", "Custom"), state.get("cp_emojis", []),
                                    price, 1 if price > 0 else 0)
                del USER_STATES[uid]
                await event.reply("✅ Created!", buttons=kb_emoji_packs_manage()); return
            if step == "wait_bc_text":
                text = event.text.strip(); del USER_STATES[uid]
                msg = await event.reply("📢 Broadcasting...")
                ok, fail, total = await broadcast_message(text=text)
                await msg.edit(f"✅ {total} | ✅{ok} | ❌{fail}"); return
            if step == "wait_bc_photo":
                url = event.text.strip(); del USER_STATES[uid]
                msg = await event.reply("📢 Broadcasting...")
                ok, fail, total = await broadcast_message(photo_url=url)
                await msg.edit(f"✅ {total} | ✅{ok} | ❌{fail}"); return
            if step == "wait_setfree":
                text = event.text.strip()
                if not text.isdigit(): await event.reply("❌ Number"); return
                cfg_set("free_count", int(text)); del USER_STATES[uid]
                await event.reply(f"✅ Free: {text}", buttons=kb_owner()); return
            if step == "wait_add_user_id":
                text = event.text.strip()
                if not text.lstrip("-").isdigit(): await event.reply("❌ ID"); return
                db_set_approval(int(text), "approved", approved_by=get_owner_id())
                del USER_STATES[uid]
                await event.reply(f"✅ Granted", buttons=kb_owner()); return
            if step == "user_set_limit":
                text = event.text.strip()
                if not text.isdigit(): await event.reply("❌ Number"); return
                db_set_user_limit(state['target'], int(text))
                del USER_STATES[uid]
                await event.reply("✅ Set", buttons=kb_user_manage(state['target'])); return
            if step == "user_add_balance":
                text = event.text.strip()
                if not text.lstrip("-").isdigit(): await event.reply("❌ Number"); return
                db_add_free_balance(state['target'], int(text))
                del USER_STATES[uid]
                await event.reply("✅ Added", buttons=kb_user_manage(state['target'])); return

        if not await is_joined(uid):
            await event.reply("Join all channels:", buttons=kb_join()); return
        if not OWNER_IS(uid) and not is_approved(uid):
            await event.reply("Need approval.", buttons=kb_request_access()); return
        if uid not in USER_STATES:
            await event.reply("Send /start.", buttons=kb_welcome(uid)); return

        state = USER_STATES[uid]; step = state.get("step")

        if step == "queue_wait_chat":
            state["q_chat"] = event.text.strip(); state["step"] = "queue_wait_post"
            USER_STATES[uid] = state
            await event.reply("✅ Chat saved. Post link:", buttons=kb_back(uid)); return
        if step == "queue_wait_post":
            state["q_post"] = event.text.strip(); state["step"] = "queue_wait_count"
            USER_STATES[uid] = state
            limit = get_user_limit(uid)
            await event.reply(f"✅ How many? (max {limit}):", buttons=kb_reaction_count(uid)); return
        if step == "queue_wait_time":
            text = event.text.strip()
            try:
                if ":" in text and len(text.split(":")) == 2:
                    h, m = text.split(":")
                    target = datetime.now().replace(hour=int(h), minute=int(m), second=0, microsecond=0)
                    if target < datetime.now(): target += timedelta(days=1)
                else:
                    target = datetime.now() + timedelta(minutes=int(text))
                qid = db_add_queue(uid, state.get("q_chat"), state.get("q_post"),
                                    state.get("reaction_count", 5), "default", None,
                                    target.strftime("%Y-%m-%d %H:%M:%S"))
                del USER_STATES[uid]
                await event.reply(f"✅ Job #{qid} for {target.strftime('%d %b %H:%M')}",
                                    buttons=kb_queue_menu(uid))
            except Exception as e: await event.reply(f"❌ {str(e)[:60]}")
            return
        if step == "bulk_wait_chat":
            state["b_chat"] = event.text.strip(); state["step"] = "bulk_wait_posts"
            USER_STATES[uid] = state
            await event.reply("✅ Post links (one per line):", buttons=kb_back(uid)); return
        if step == "bulk_wait_posts":
            posts = [p.strip() for p in re.split(r"[,\n]+", event.text.strip()) if p.strip()]
            if not posts: await event.reply("❌ No posts"); return
            state["b_posts"] = posts; state["step"] = "bulk_wait_count"
            USER_STATES[uid] = state
            await event.reply(f"✅ {len(posts)} posts. Reactions per post?:", buttons=kb_reaction_count(uid)); return
        if step == "wait_payment_screenshot":
            plan = state.get("plan"); days = state.get("days"); mid = state.get("method_id")
            price = get_plan_price(plan, days); m = db_payment_get(mid)
            method_name = m[2] if m else f"#{mid}"
            text = event.text.strip()
            ss = "photo" if (event.photo or event.document) else text
            pid = db_add_payment(uid, price, plan, days, method_name, ss)
            del USER_STATES[uid]
            await event.reply(f"✅ **PAYMENT SENT**\n📦 {PLAN_NAMES[plan]}\n💰 {price}rs\nID: `{pid}`\n\nOwner verify karega!",
                                buttons=kb_welcome(uid))
            try:
                await bot.send_message(get_owner_id(),
                    f"💳 **NEW PAYMENT**\n👤 `{uid}`\n💰 {price}rs\n📦 {PLAN_NAMES[plan]}\n📱 {method_name}",
                    buttons=kb_payment_actions(pid))
            except Exception: pass
            return
        if step == "tpl_wait_name":
            state["tpl_name"] = event.text.strip()[:20]; state["step"] = "tpl_wait_emojis"
            USER_STATES[uid] = state
            await event.reply("✏️ Emojis:"); return
        if step == "tpl_wait_emojis":
            emojis = [p.strip() for p in re.split(r"[,\s]+", event.text.strip()) if p.strip() in ALL_REACTIONS]
            if not emojis: await event.reply("❌ No emojis."); return
            db_add_template(uid, state.get("tpl_name", "Template"), emojis[:20])
            del USER_STATES[uid]
            await event.reply("✅ Saved!", buttons=kb_templates_menu(uid)); return
        if step == "wait_channel":
            state["channel_link"] = event.text.strip(); state["step"] = "wait_post"
            USER_STATES[uid] = state
            await event.reply("✅ Post link:", buttons=kb_back(uid)); return
        if step == "wait_post":
            state["post_link"] = event.text.strip(); state["step"] = "wait_count"
            USER_STATES[uid] = state
            limit = get_user_limit(uid)
            await event.reply(f"✅ How many? (max {limit}):", buttons=kb_reaction_count(uid)); return
        if step == "wait_custom_emoji":
            emojis = []
            for p in re.split(r"[,\s]+", event.text.strip()):
                p = p.strip()
                if p and p in ALL_REACTIONS and p not in emojis: emojis.append(p)
            if not emojis: await event.reply("❌ No emojis.", buttons=kb_back(uid)); return
            state["custom_emojis"] = emojis[:30]; state["emoji_mode"] = "custom"
            USER_STATES[uid] = state
            await event.reply("✨ Starting...")
            await _run_reactions(event, uid); return
        if step == "watch_wait_link":
            state["watch_link"] = event.text.strip()
            state["watch_chat_type"] = state.get("chat_type", "channel")
            state["step"] = "watch_wait_count"; USER_STATES[uid] = state
            await event.reply("✅ Count (1-50):", buttons=kb_back(uid)); return
        if step == "watch_wait_count":
            text = event.text.strip()
            if not text.isdigit(): await event.reply("❌ Number"); return
            state["watch_count"] = min(int(text), 50); state["step"] = "watch_wait_emoji"
            USER_STATES[uid] = state
            await event.reply(f"✅ Count: {state['watch_count']}",
                buttons=[[btn("🎯 Default", data=b"watch_emoji:default", style="success")],
                         [btn("✏️ Custom", data=b"watch_emoji:custom", style="primary")],
                         [btn("🔙 Cancel", data=b"watch_flow", style="danger")]])
            return
        if step == "watch_wait_custom_emoji":
            emojis = [p.strip() for p in re.split(r"[,\s]+", event.text.strip()) if p.strip() in ALL_REACTIONS]
            if not emojis: await event.reply("❌ No emojis."); return
            state["watch_custom_emojis"] = emojis[:30]; USER_STATES[uid] = state
            await _finalize_watch_add(event, uid); return
        if step == "watch_edit_count":
            text = event.text.strip()
            if not text.isdigit(): await event.reply("❌ Number"); return
            wid = state["wid"]; db_update_watcher(wid, reaction_count=min(int(text), 200))
            del USER_STATES[uid]
            await event.reply("✅ Updated!", buttons=[[btn("🔙", data=f"watch:manage:{wid}".encode(), style="primary")]]); return
        if step == "watch_edit_emoji":
            emojis = [p.strip() for p in re.split(r"[,\s]+", event.text.strip()) if p.strip() in ALL_REACTIONS]
            if not emojis: await event.reply("❌ No emojis."); return
            wid = state["wid"]; db_update_watcher(wid, emoji_mode="custom", custom_emojis=",".join(emojis[:30]))
            del USER_STATES[uid]
            await event.reply("✅ Updated!", buttons=[[btn("🔙", data=f"watch:manage:{wid}".encode(), style="primary")]]); return

    except Exception as e: D_err(e, "on_msg")


async def _finalize_watch_add(event, uid):
    try:
        state = USER_STATES.get(uid, {})
        link = state.get("watch_link"); cty = state.get("watch_chat_type", "channel")
        count = state.get("watch_count", 5); custom = state.get("watch_custom_emojis")
        mode = "custom" if custom else "default"
        try:
            chat_ref, invite = parse_channel_link(link)
            if invite:
                try: await admin_client(ImportChatInviteRequest(invite))
                except Exception: pass
                entity = await safe_get_entity(f"https://t.me/+{invite}", cache_key=f"chat:{invite}")
            else:
                entity = await safe_get_entity(chat_ref, cache_key=f"chat:{chat_ref}")
        except Exception as e:
            await event.reply(f"❌ {str(e)[:80]}")
            if uid in USER_STATES: USER_STATES[uid] = {}
            return
        chat_id = entity.id; chat_title = getattr(entity, "title", "Unknown")
        for w in db_list_watchers(uid):
            if w[2] == chat_id:
                await event.reply(f"⚠️ Already watching")
                if uid in USER_STATES: USER_STATES[uid] = {}
                return
        try:
            msgs = await asyncio.wait_for(admin_client.get_messages(entity, limit=1), timeout=15)
            last = msgs[0].id if msgs else 0
        except Exception: last = 0
        db_add_watcher(uid, chat_id, chat_title, link, cty, count, mode, custom, last)
        await event.reply(
            f"🎉 **WATCH ADDED**\n📢 {chat_title}\n🎯 {count}/post\n🟢 ACTIVE!",
            buttons=[[btn("📋 My Watches", data=b"watch:list", style="primary")],
                     [btn("🏠 Home", data=b"home", style="success")]])
        if uid in USER_STATES: USER_STATES[uid] = {}
    except Exception as e: D_err(e, "_finalize_watch_add")


async def _run_reactions(event, uid):
    global TASK_RUNNING, TASK_OWNER_UID
    now = time.time(); last = USER_LAST_REQUEST.get(uid, 0)
    if now - last < USER_COOLDOWN:
        await event.answer(f"⏳ Wait {int(USER_COOLDOWN - (now - last))}s", alert=True); return
    if TASK_RUNNING:
        await safe_edit(event, "⏳ Another task running...", buttons=kb_back(uid))
        if uid in USER_STATES: USER_STATES[uid] = {}
        return
    state = USER_STATES.get(uid, {})
    cl = state.get("channel_link"); pl = state.get("post_link")
    count = state.get("reaction_count", 0); em = state.get("emoji_mode", "default")
    ce = state.get("custom_emojis")
    if not cl or not pl or count <= 0:
        await event.answer("❌ Missing data", alert=True); return
    USER_LAST_REQUEST[uid] = now

    user_ra_limit, ra_src = get_user_ra_limit(uid)
    use_real = user_has_realaccounts(uid) and real_count_available() > 0 and user_ra_limit > 0

    TASK_RUNNING = True; TASK_OWNER_UID = uid
    try:
        if use_real:
            post_ref, msg_id = parse_post_link(pl)
            if not msg_id:
                await safe_edit(event, "❌ Invalid post link", buttons=kb_back(uid)); return
            chat_ref, invite = parse_channel_link(cl)
            target = post_ref or chat_ref
            if invite and not post_ref:
                try: await admin_client(ImportChatInviteRequest(invite))
                except Exception: pass
                target = f"https://t.me/+{invite}"
            emoji_pool = ce if (em == "custom" and ce) else None
            real_count = min(count, user_ra_limit, real_count_available())
            await safe_edit(event,
                f"👤 **REAL ACCOUNTS MODE**\n{DIV}\n\n"
                f"🎯 Sending **{real_count}** reactions\n"
                f"🔓 No admin needed ✅\n\n⚡ Processing...")
            async def on_prog(i, total, ok):
                if i % 5 == 0 or i == total:
                    await anim_progress(event, i, total, "✨", f"✅ Success: {ok}")
            res = await send_reactions_real(target, msg_id, real_count,
                                            emoji_pool=emoji_pool, on_progress=on_prog)
            bar = progress_bar(res["ok"], max(real_count, 1))
            await safe_edit(event,
                f"🎉 **COMPLETE!** 🎉\n{STAR_LINE}\n\n👤 Mode: **Real Accounts**\n"
                f"📩 Post: **#{msg_id}**\n\n{DIV}\n🎯 Requested: **{real_count}**\n"
                f"✅ Success: **{res['ok']}**\n❌ Failed: **{res['fail']}**\n"
                f"🌊 Flooded: **{res['flooded']}**\n{DIV}\n\n"
                f"🚀 **{bar}** {res['ok']}/{real_count}",
                buttons=kb_back(uid))
        else:
            await process_reactions_rotating(event, uid, cl, pl, count,
                                             emoji_mode=em, custom_emojis=ce)
    except Exception as e:
        D_err(e, "_run_reactions")
        try: await safe_edit(event, f"❌ {str(e)[:100]}", buttons=kb_back(uid))
        except Exception: pass
    finally:
        TASK_RUNNING = False; TASK_OWNER_UID = None


# ══════════════════════ HEALTH SERVER ══════════════════════
async def start_health_server():
    async def health_handler(request):
        return web.Response(text="OK", status=200)
    async def status_handler(request):
        return web.json_response({
            "status": "online",
            "uptime": int(time.time() - _start_time),
            "task_running": TASK_RUNNING,
            "users": db_total_users(),
        })
    app = web.Application()
    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)
    app.router.add_get("/status", status_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", "8080"))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    D(f"HTTP health server started on port {port}", "ok")


# ══════════════════════ MAIN ══════════════════════
async def main():
    global admin_client, backup_client, TASK_RUNNING, TASK_OWNER_UID
    try:
        loop = asyncio.get_running_loop()
        loop.set_exception_handler(global_exception_handler)
    except Exception: pass
    db_init()
    BOT_POOL.clear(); FLOOD_UNTIL.clear()
    TASK_RUNNING = False; TASK_OWNER_UID = None
    D("Cleared stale state", "pool")
    admin_client = TelegramClient(StringSession(ADMIN_SESSION), API_ID, API_HASH)
    await admin_client.start()
    if not await admin_client.is_user_authorized():
        print("❌ Primary session invalid."); return
    if BACKUP_SESSION_1 and len(BACKUP_SESSION_1) > 250:
        try:
            backup_client = TelegramClient(StringSession(BACKUP_SESSION_1), API_ID, API_HASH)
            await backup_client.start()
            if await backup_client.is_user_authorized(): D("✅ Backup ready", "backup")
            else:
                await backup_client.disconnect(); backup_client = None
        except Exception as e:
            backup_client = None; D(f"⚠️ Backup failed: {str(e)[:80]}", "warn")
    me = await admin_client.get_me()
    bots, added = sync_bots()
    gh = github_sync.get_stats()
    D_sep("GHOST REACTION BOT — v65 FINAL")
    D(f"Owner: {me.first_name} (@{me.username})", "ok")
    D(f"Owner from cfg: @{get_owner_username()} (ID {get_owner_id()})", "ok")
    D(f"Bots: {db_count_visible_bots()} / {db_count_bots()}", "ok")
    D(f"Sessions: {real_count_available()}/{len(discover_session_files())}", "real")
    D(f"Payment Methods: {len(db_payment_list(active_only=False))}", "pay")
    D(f"GitHub DB: {'✅' if gh['enabled'] else '❌'}", "gh")
    D(f"Languages: {len(LANGUAGES)}", "lang")
    D("Bot online ✨", "ok")

    asyncio.create_task(start_health_server())
    asyncio.create_task(watcher_loop())
    asyncio.create_task(pool_cleaner_loop())
    asyncio.create_task(health_check_loop())
    asyncio.create_task(queue_loop())
    asyncio.create_task(daily_summary_loop())

    while True:
        try:
            await bot.start(bot_token=BOT_TOKEN)
            break
        except FloodWaitError as e:
            wait_sec = e.seconds + 30
            D(f"⚠️ Bot FloodWait — {wait_sec}s", "flood")
            await asyncio.sleep(wait_sec)
        except Exception as e:
            D(f"⚠️ Bot start error: {str(e)[:100]}", "fail")
            await asyncio.sleep(30)
    try:
        await bot.run_until_disconnected()
    finally:
        try:
            github_sync.upload_db(force=True)
            await close_all_real_clients()
            D("Cleanup done", "gh")
        except Exception: pass


if __name__ == "__main__":
    asyncio.run(main())
