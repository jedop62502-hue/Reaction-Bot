"""
============================================================
   GHOST REACTION BOT - v60 FRIENDLY + ANIMATED + GITHUB SYNC
   Full Fixed | Multi-Lang | Admin Check | Auto DB Sync
   Credit: @Anonymous_User_37
============================================================
"""
import os, sys, time, csv, io, random, asyncio, re, hashlib
import sqlite3, requests, traceback, logging
from datetime import datetime, timedelta

from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.messages import (
    ImportChatInviteRequest, AddChatUserRequest)
from telethon.tl.functions.channels import (
    InviteToChannelRequest, GetParticipantRequest,
    EditAdminRequest, GetParticipantsRequest)
from telethon.tl.types import (
    Channel, Chat, ChatAdminRights, ChannelParticipantsAdmins)

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

# ═══ GitHub Sync ═══
import github_sync

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ══════════════════════ CONFIG ══════════════════════
API_ID = 30217812
API_HASH = "d21066a90786cf2dd348b907ece69d24"
ADMIN_SESSION = "1BJWap1wBu2X5POvvWDOSvJZAROd9WIKpJMpSIf-W3skkHehdGLol5KkobjCIfohj9gFhHqh3UKkwjLJAsMqDbuWAflGN8yb1Qu7LxiKBsZCFYHKAHKBfxZgJyv35ivBxl881TvLZ6dbpdfM4_-66CTW7HnBE-j0_yktVaX-q3o1VaL3HYZJkb_wnI5BaJow7s9IHYtqlyWM2RYeQgcQVc23CDjHKLR4qdFpaMM_T2SuQQ478eDnUGQ-R891NssFOq0lOGs765CyI1ngt_C-NU3PYpvHVyJhFHZ3eBqsrgnmP0tpeSC1mJ2egouxeevr7pPUKMdMI_QyoA0aiTviAMEGlERWbrEA="
BACKUP_SESSION_1 = "1AZWarzgBu2tZBeVP2KqGU3PKmu6shSzj5y_cyk-lPl-ymgoGjlVentuWIYdFQ9x_LZxoePMIgwoJM4EVThTNBvdAL0gqTqI5vgQOCzCYghU9p6J9oA-k4eEO8PJESXN-LsN7ch9_MZY-bx8UdBlJvSj1tZkJzbj8ByaSvVwVncgx1r8xtrTqwr8aWUGfxPKI0ESZBK9msBt7Kx2nRht8S1Yb1jcnP5AwNvgV4O73bqnHIZfRKy2cRVSXFiUII-AKsLh_ByQrOOGKIta2JHdzWlUlDBuSvsHLqbDW4NT44bApZskFNr46K-KbeKVE0OObN9-aBGAOpcjubn5V_UsPGV-6kTD2W70="
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

FORCE_CHANNELS_DEFAULT = [
    {"channel": "@MR_GHOST_OFFICIAL",
     "url": "https://t.me/MR_GHOST_OFFICIAL",
     "name": "Main Channel",
     "active": 1},
]

# Boot GitHub sync FIRST
github_sync.start_sync_thread()

DB_FILE = github_sync.LOCAL_DB_PATH if github_sync.is_enabled() else (
    "/app/data/ghost_users.db" if os.path.isdir("/app/data") else "ghost_users.db")

DEFAULT_REACTIONS = ["❤️", "👍", "🔥"]
ALL_REACTIONS = ["❤️", "🔥", "🥰", "😍", "👍", "😇", "👀", "😎", "💯", "🎉",
                 "🤩", "🥳", "😁", "😂", "🤣", "😊", "🙏", "👏", "💪", "⚡",
                 "🌚", "🌭", "🍾", "💋", "🖕", "😈", "🤝", "🎃", "👻", "🤡",
                 "🤔", "🤨", "😐", "😑", "😶", "🙄", "😏", "😣", "😥", "😮",
                 "🤐", "😯", "😪", "😫", "🥱", "😴", "😌", "😛", "😜", "🤪"]

DEFAULT_FREE_COUNT = 5
MAX_REACTIONS = 200
BROADCAST_DELAY = 1.5
FLOOD_SAFETY = 3
PER_BOT_TIMEOUT = 25
PERMANENT_ADMIN_BOTS = {"RN_OTP1_bot", "RN_REACTION_BOT"}
MAX_ADMINS = 50
RESERVED_SLOTS = 5
BATCH_SIZE = MAX_ADMINS - RESERVED_SLOTS
WATCHER_CHECK_INTERVAL = 300
QUEUE_CHECK_INTERVAL = 60
AUTO_WATCH_ENABLED = True
BOT_BUSY_TIMEOUT = 2
POOL_CLEANUP_INTERVAL = 30
USER_COOLDOWN = 15
MAX_CYCLES = 25

PLAN_LIMITS = {"free": 5, "basic": 20, "pro": 50, "premium": 200}
PLAN_NAMES = {"free": "🆓 Free", "basic": "🥉 Basic",
              "pro": "🥈 Pro", "premium": "🥇 Premium"}
DURATIONS = {1: "1 Day", 7: "7 Days", 15: "15 Days", 30: "30 Days"}
PAID_PLANS = {"basic", "pro", "premium"}
DEFAULT_PRICES = {
    "basic":   {1: 70,  7: 250,  15: 500,  30: 900},
    "pro":     {1: 120, 7: 400,  15: 800,  30: 1400},
    "premium": {1: 200, 7: 700,  15: 1400, 30: 2500},
}
LANGUAGES = {
    "en": "🇬🇧 English", "ur": "🇵🇰 اردو", "hi": "🇮🇳 हिन्दी",
    "ar": "🇸🇦 العربية", "ru": "🇷🇺 Русский",
    "es": "🇪🇸 Español", "id": "🇮🇩 Indonesia",
}
PAYMENT_METHODS = {
    "jazzcash": {"name": "JazzCash", "number": "03001234567", "holder": "Rehan"},
    "easypaisa": {"name": "Easypaisa", "number": "03451234567", "holder": "Rehan"},
    "upi": {"name": "UPI (India)", "number": "rehan@upi", "holder": "Rehan"},
    "usdt": {"name": "USDT (TRC20)", "number": "TX1234...", "holder": "Rehan"},
    "binance": {"name": "Binance Pay", "number": "123456789", "holder": "Rehan"},
}
REFERRAL_REWARD = 5
FRIEND_VALID_REWARD = 10
EMOJI_PACKS = {
    "love": ["❤️", "😍", "🥰", "💋", "😘"],
    "fire": ["🔥", "💯", "⚡", "🌟", "✨"],
    "funny": ["😂", "🤣", "😁", "😅", "🤡"],
    "cool": ["😎", "👀", "🙌", "💪", "🤝"],
    "party": ["🎉", "🥳", "🎊", "🎈", "🎁"],
}

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
OWNER_ENTITY_CACHE = {"entity": None, "expires_at": None}
BOT_ENTITY_CACHE = {}
ENTITY_CACHE_TTL = 3600
OWNER_CACHE_TTL = 7200
RESOLVE_FLOOD_UNTIL = None
admin_client = None
backup_client = None
_start_time = time.time()


def _dirty():
    try:
        github_sync.mark_dirty()
    except Exception:
        pass


def global_exception_handler(loop, context):
    exc = context.get("exception")
    if exc:
        print(f"\n{'─' * 60}", flush=True)
        print(f"⚠️  GLOBAL EXCEPTION: {exc}", flush=True)
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        print(f"{'─' * 60}\n", flush=True)


# ══════════════════════ LANGUAGE STRINGS ══════════════════════
LANG_STRINGS = {
    "en": {"welcome": "Welcome Back", "send_reactions": "Send Reactions",
           "auto_watch": "Auto-Watch", "templates": "Templates",
           "referral": "Referral", "upgrade": "Upgrade Plan",
           "notifications": "Notifications", "language": "Language",
           "info": "Info", "support": "Customer Support",
           "owner_panel": "Owner Panel", "home": "Main Menu", "back": "Back",
           "cancel": "Cancel", "channel": "Channel", "group": "Group",
           "default_emoji": "Default", "custom_emoji": "Custom",
           "emoji_packs": "Emoji Packs", "send": "Send",
           "choose_language": "Choose Language",
           "language_changed": "Language Changed",
           "your_limit": "Your limit", "per_post": "per post",
           "plan": "Plan", "free_plan": "Free Plan",
           "my_watches": "My Watches", "add_watch": "Add Watch",
           "contact_owner": "Contact Owner", "retry": "Retry",
           "how_many": "How many reactions?", "emoji_mode": "Emoji mode",
           "post_link": "Send post link", "chat_link": "Send chat link",
           "count_per_post": "Count per post", "chat_type": "Chat type?",
           "my_link": "My Link", "stats": "Stats", "leaderboard": "Leaderboard",
           "analytics": "Analytics", "queue": "Reaction Queue",
           "bulk": "Bulk Reactions", "team": "Team",
           "buy_plan": "Buy Plan", "payment": "Payment"},
    "ur": {"welcome": "خوش آمدید", "send_reactions": "ری ایکشن بھیجیں",
           "auto_watch": "آٹو واچ", "templates": "ٹیمپلیٹس",
           "referral": "ریفرل", "upgrade": "پلان اپ گریڈ",
           "notifications": "اطلاعات", "language": "زبان",
           "info": "معلومات", "support": "کسٹمر سپورٹ",
           "owner_panel": "اونر پینل", "home": "مین مینو", "back": "واپس",
           "cancel": "کینسل", "channel": "چینل", "group": "گروپ",
           "default_emoji": "ڈیفالٹ", "custom_emoji": "کسٹم",
           "emoji_packs": "ایموجی پیکس", "send": "بھیجیں",
           "choose_language": "زبان منتخب کریں",
           "language_changed": "زبان تبدیل ہو گئی",
           "your_limit": "آپ کی حد", "per_post": "فی پوسٹ",
           "plan": "پلان", "free_plan": "مفت پلان",
           "my_watches": "میری واچز", "add_watch": "واچ شامل کریں",
           "contact_owner": "اونر سے رابطہ", "retry": "دوبارہ کوشش",
           "how_many": "کتنے ری ایکشن؟", "emoji_mode": "ایموجی موڈ",
           "post_link": "پوسٹ لنک", "chat_link": "چیٹ لنک",
           "count_per_post": "فی پوسٹ گنتی", "chat_type": "چیٹ کی قسم؟",
           "my_link": "میرا لنک", "stats": "اعداد", "leaderboard": "لیڈر بورڈ",
           "analytics": "تجزیہ", "queue": "ری ایکشن قطار",
           "bulk": "بلک ری ایکشن", "team": "ٹیم",
           "buy_plan": "پلان خریدیں", "payment": "ادائیگی"},
    "hi": {"welcome": "वापसी पर स्वागत", "send_reactions": "रिएक्शन भेजें",
           "auto_watch": "ऑटो-वॉच", "templates": "टेम्पलेट्स",
           "referral": "रेफरल", "upgrade": "प्लान अपग्रेड",
           "notifications": "सूचनाएं", "language": "भाषा",
           "info": "जानकारी", "support": "ग्राहक सहायता",
           "owner_panel": "ओनर पैनल", "home": "मुख्य मेनू", "back": "वापस",
           "cancel": "रद्द", "channel": "चैनल", "group": "ग्रुप",
           "default_emoji": "डिफ़ॉल्ट", "custom_emoji": "कस्टम",
           "emoji_packs": "इमोजी पैक", "send": "भेजें",
           "choose_language": "भाषा चुनें",
           "language_changed": "भाषा बदल गई",
           "your_limit": "आपकी सीमा", "per_post": "प्रति पोस्ट",
           "plan": "प्लान", "free_plan": "फ्री प्लान",
           "my_watches": "मेरी वॉच", "add_watch": "वॉच जोड़ें",
           "contact_owner": "मालिक से संपर्क", "retry": "पुनः प्रयास",
           "how_many": "कितने रिएक्शन?", "emoji_mode": "इमोजी मोड",
           "post_link": "पोस्ट लिंक", "chat_link": "चैट लिंक",
           "count_per_post": "प्रति पोस्ट", "chat_type": "चैट टाइप?",
           "my_link": "मेरा लिंक", "stats": "आंकड़े", "leaderboard": "लीडरबोर्ड",
           "analytics": "विश्लेषण", "queue": "रिएक्शन कतार",
           "bulk": "बल्क रिएक्शन", "team": "टीम",
           "buy_plan": "प्लान खरीदें", "payment": "भुगतान"},
    "ar": {"welcome": "مرحباً بعودتك", "send_reactions": "إرسال التفاعلات",
           "auto_watch": "المراقبة التلقائية", "templates": "القوالب",
           "referral": "الإحالة", "upgrade": "ترقية الخطة",
           "notifications": "الإشعارات", "language": "اللغة",
           "info": "معلومات", "support": "دعم العملاء",
           "owner_panel": "لوحة المالك", "home": "القائمة الرئيسية",
           "back": "رجوع", "cancel": "إلغاء", "channel": "قناة", "group": "مجموعة",
           "default_emoji": "افتراضي", "custom_emoji": "مخصص",
           "emoji_packs": "حزم الرموز", "send": "إرسال",
           "choose_language": "اختر اللغة", "language_changed": "تم تغيير اللغة",
           "your_limit": "حدك", "per_post": "لكل منشور",
           "plan": "خطة", "free_plan": "خطة مجانية",
           "my_watches": "مراقباتي", "add_watch": "إضافة مراقبة",
           "contact_owner": "اتصل بالمالك", "retry": "إعادة المحاولة",
           "how_many": "كم عدد التفاعلات؟", "emoji_mode": "وضع الرموز",
           "post_link": "رابط المنشور", "chat_link": "رابط الدردشة",
           "count_per_post": "العدد لكل منشور", "chat_type": "نوع الدردشة؟",
           "my_link": "رابطي", "stats": "إحصائيات", "leaderboard": "المتصدرون",
           "analytics": "التحليلات", "queue": "قائمة الانتظار",
           "bulk": "تفاعلات جماعية", "team": "الفريق",
           "buy_plan": "شراء الخطة", "payment": "الدفع"},
    "ru": {"welcome": "С возвращением", "send_reactions": "Отправить реакции",
           "auto_watch": "Авто-наблюдение", "templates": "Шаблоны",
           "referral": "Реферал", "upgrade": "Обновить план",
           "notifications": "Уведомления", "language": "Язык",
           "info": "Инфо", "support": "Поддержка",
           "owner_panel": "Панель владельца", "home": "Главное меню",
           "back": "Назад", "cancel": "Отмена", "channel": "Канал", "group": "Группа",
           "default_emoji": "По умолчанию", "custom_emoji": "Свои",
           "emoji_packs": "Наборы эмодзи", "send": "Отправить",
           "choose_language": "Выбрать язык", "language_changed": "Язык изменён",
           "your_limit": "Ваш лимит", "per_post": "на пост",
           "plan": "План", "free_plan": "Бесплатный план",
           "my_watches": "Мои наблюдения", "add_watch": "Добавить",
           "contact_owner": "Связаться", "retry": "Повторить",
           "how_many": "Сколько реакций?", "emoji_mode": "Режим эмодзи",
           "post_link": "Ссылка на пост", "chat_link": "Ссылка на чат",
           "count_per_post": "На пост", "chat_type": "Тип чата?",
           "my_link": "Моя ссылка", "stats": "Статистика", "leaderboard": "Топ",
           "analytics": "Аналитика", "queue": "Очередь",
           "bulk": "Массовые", "team": "Команда",
           "buy_plan": "Купить", "payment": "Оплата"},
    "es": {"welcome": "Bienvenido", "send_reactions": "Enviar Reacciones",
           "auto_watch": "Auto-Vigilancia", "templates": "Plantillas",
           "referral": "Referido", "upgrade": "Actualizar Plan",
           "notifications": "Notificaciones", "language": "Idioma",
           "info": "Info", "support": "Soporte",
           "owner_panel": "Panel de Dueño", "home": "Menú Principal",
           "back": "Atrás", "cancel": "Cancelar", "channel": "Canal", "group": "Grupo",
           "default_emoji": "Predeterminado", "custom_emoji": "Personalizado",
           "emoji_packs": "Paquetes", "send": "Enviar",
           "choose_language": "Elegir idioma", "language_changed": "Idioma cambiado",
           "your_limit": "Tu límite", "per_post": "por post",
           "plan": "Plan", "free_plan": "Plan Gratis",
           "my_watches": "Mis vigilancias", "add_watch": "Agregar",
           "contact_owner": "Contactar", "retry": "Reintentar",
           "how_many": "¿Cuántas reacciones?", "emoji_mode": "Modo emoji",
           "post_link": "Enlace del post", "chat_link": "Enlace del chat",
           "count_per_post": "Por post", "chat_type": "¿Tipo de chat?",
           "my_link": "Mi enlace", "stats": "Estadísticas", "leaderboard": "Ranking",
           "analytics": "Análisis", "queue": "Cola",
           "bulk": "Masivo", "team": "Equipo",
           "buy_plan": "Comprar", "payment": "Pago"},
    "id": {"welcome": "Selamat Datang", "send_reactions": "Kirim Reaksi",
           "auto_watch": "Auto-Pantau", "templates": "Template",
           "referral": "Referral", "upgrade": "Upgrade Plan",
           "notifications": "Notifikasi", "language": "Bahasa",
           "info": "Info", "support": "Dukungan",
           "owner_panel": "Panel Pemilik", "home": "Menu Utama",
           "back": "Kembali", "cancel": "Batal", "channel": "Channel", "group": "Grup",
           "default_emoji": "Default", "custom_emoji": "Kustom",
           "emoji_packs": "Paket Emoji", "send": "Kirim",
           "choose_language": "Pilih Bahasa", "language_changed": "Bahasa diubah",
           "your_limit": "Batas Anda", "per_post": "per posting",
           "plan": "Paket", "free_plan": "Paket Gratis",
           "my_watches": "Pantauan Saya", "add_watch": "Tambah Pantauan",
           "contact_owner": "Hubungi Pemilik", "retry": "Coba Lagi",
           "how_many": "Berapa reaksi?", "emoji_mode": "Mode emoji",
           "post_link": "Kirim link posting", "chat_link": "Kirim link chat",
           "count_per_post": "Per posting", "chat_type": "Tipe chat?",
           "my_link": "Link Saya", "stats": "Statistik", "leaderboard": "Peringkat",
           "analytics": "Analitik", "queue": "Antrian",
           "bulk": "Massal", "team": "Tim",
           "buy_plan": "Beli", "payment": "Pembayaran"},
}

# ══════════════════════ WELCOME TEMPLATES ══════════════════════
WELCOME_TEMPLATES = {
    "en": {"title": "GHOST REACTION BOT", "greet": "Welcome",
           "read_first": "IMPORTANT — READ FIRST",
           "warn_line": "Before sending reactions, make the OWNER admin in your channel / group!",
           "owner_lbl": "Owner", "owner_id_lbl": "Owner ID",
           "req_perm": "Required Admin Permissions",
           "perm1": "Add New Admins", "perm2": "Post Messages",
           "perm3": "Delete Messages", "perm4": "Invite Users",
           "howto": "HOW TO ADD ADMIN",
           "step1": "Open your channel/group",
           "step2": "Tap name → Administrators",
           "step3": "Add Admin → search the username",
           "step4": "Enable ALL permissions above",
           "step5": "Save",
           "your_info": "YOUR INFO", "plan": "Plan", "limit": "Limit",
           "per_post": "per post", "balance": "Balance",
           "autowatch": "Auto-Watch", "approved": "Approved",
           "yes": "YES", "no": "NO",
           "ready": "✅ Ready! Tap a button below to start"},
    "ur": {"title": "گھوسٹ ری ایکشن بوٹ", "greet": "خوش آمدید",
           "read_first": "اہم — پہلے یہ پڑھیں",
           "warn_line": "ری ایکشن بھیجنے سے پہلے اپنے چینل/گروپ میں اونر کو ایڈمن بنائیں!",
           "owner_lbl": "اونر", "owner_id_lbl": "اونر آئی ڈی",
           "req_perm": "ضروری ایڈمن اجازتیں",
           "perm1": "نئے ایڈمن شامل کریں", "perm2": "پیغامات بھیجیں",
           "perm3": "پیغامات حذف کریں", "perm4": "صارفین مدعو کریں",
           "howto": "ایڈمن کیسے بنائیں",
           "step1": "اپنا چینل/گروپ کھولیں",
           "step2": "نام پر ٹیپ کریں → ایڈمنسٹریٹرز",
           "step3": "ایڈمن شامل کریں → یوزرنیم تلاش کریں",
           "step4": "اوپر والی تمام اجازتیں آن کریں",
           "step5": "محفوظ کریں",
           "your_info": "آپ کی معلومات", "plan": "پلان", "limit": "حد",
           "per_post": "فی پوسٹ", "balance": "بیلنس",
           "autowatch": "آٹو واچ", "approved": "منظور شدہ",
           "yes": "جی ہاں", "no": "نہیں",
           "ready": "✅ تیار! نیچے کوئی بٹن دبائیں"},
    "hi": {"title": "घोस्ट रिएक्शन बॉट", "greet": "स्वागत है",
           "read_first": "महत्वपूर्ण — पहले पढ़ें",
           "warn_line": "रिएक्शन भेजने से पहले अपने चैनल/ग्रुप में ओनर को एडमिन बनाएं!",
           "owner_lbl": "ओनर", "owner_id_lbl": "ओनर आईडी",
           "req_perm": "आवश्यक एडमिन अनुमतियाँ",
           "perm1": "नए एडमिन जोड़ें", "perm2": "संदेश भेजें",
           "perm3": "संदेश हटाएं", "perm4": "उपयोगकर्ता आमंत्रित करें",
           "howto": "एडमिन कैसे जोड़ें",
           "step1": "अपना चैनल/ग्रुप खोलें",
           "step2": "नाम पर टैप → एडमिनिस्ट्रेटर",
           "step3": "एडमिन जोड़ें → यूज़रनेम खोजें",
           "step4": "ऊपर की सभी अनुमतियाँ चालू करें",
           "step5": "सेव करें",
           "your_info": "आपकी जानकारी", "plan": "प्लान", "limit": "सीमा",
           "per_post": "प्रति पोस्ट", "balance": "बैलेंस",
           "autowatch": "ऑटो-वॉच", "approved": "स्वीकृत",
           "yes": "हाँ", "no": "नहीं",
           "ready": "✅ तैयार! नीचे कोई बटन दबाएं"},
    "ar": {"title": "بوت التفاعلات الشبح", "greet": "أهلاً بك",
           "read_first": "مهم — اقرأ أولاً",
           "warn_line": "قبل إرسال التفاعلات، اجعل المالك مشرفاً في قناتك/مجموعتك!",
           "owner_lbl": "المالك", "owner_id_lbl": "معرف المالك",
           "req_perm": "صلاحيات المشرف المطلوبة",
           "perm1": "إضافة مشرفين جدد", "perm2": "نشر الرسائل",
           "perm3": "حذف الرسائل", "perm4": "دعوة المستخدمين",
           "howto": "كيفية إضافة مشرف",
           "step1": "افتح قناتك/مجموعتك",
           "step2": "اضغط على الاسم → المشرفون",
           "step3": "أضف مشرفاً → ابحث عن المستخدم",
           "step4": "فعّل جميع الصلاحيات", "step5": "احفظ",
           "your_info": "معلوماتك", "plan": "الخطة", "limit": "الحد",
           "per_post": "لكل منشور", "balance": "الرصيد",
           "autowatch": "المراقبة التلقائية", "approved": "موافق",
           "yes": "نعم", "no": "لا",
           "ready": "✅ جاهز! اضغط على زر بالأسفل"},
    "ru": {"title": "ПРИЗРАЧНЫЙ РЕАКЦИОННЫЙ БОТ", "greet": "Добро пожаловать",
           "read_first": "ВАЖНО — ПРОЧТИТЕ",
           "warn_line": "Перед отправкой реакций сделайте владельца админом в канале/группе!",
           "owner_lbl": "Владелец", "owner_id_lbl": "ID владельца",
           "req_perm": "Требуемые права администратора",
           "perm1": "Добавлять новых админов", "perm2": "Публиковать сообщения",
           "perm3": "Удалять сообщения", "perm4": "Приглашать пользователей",
           "howto": "КАК ДОБАВИТЬ АДМИНА",
           "step1": "Откройте канал/группу", "step2": "Имя → Администраторы",
           "step3": "Добавить админа → поиск", "step4": "Включите ВСЕ права",
           "step5": "Сохранить",
           "your_info": "ВАША ИНФОРМАЦИЯ", "plan": "План", "limit": "Лимит",
           "per_post": "на пост", "balance": "Баланс",
           "autowatch": "Авто-наблюдение", "approved": "Одобрен",
           "yes": "ДА", "no": "НЕТ",
           "ready": "✅ Готово! Нажмите кнопку ниже"},
    "es": {"title": "BOT DE REACCIONES FANTASMA", "greet": "Bienvenido",
           "read_first": "IMPORTANTE — LEE PRIMERO",
           "warn_line": "¡Antes de enviar reacciones, haz al DUEÑO admin en tu canal/grupo!",
           "owner_lbl": "Dueño", "owner_id_lbl": "ID del Dueño",
           "req_perm": "Permisos de Admin Requeridos",
           "perm1": "Añadir nuevos admins", "perm2": "Publicar mensajes",
           "perm3": "Eliminar mensajes", "perm4": "Invitar usuarios",
           "howto": "CÓMO AÑADIR ADMIN",
           "step1": "Abre tu canal/grupo", "step2": "Toca el nombre → Administradores",
           "step3": "Añadir Admin → buscar usuario", "step4": "Activa TODOS los permisos",
           "step5": "Guardar",
           "your_info": "TU INFORMACIÓN", "plan": "Plan", "limit": "Límite",
           "per_post": "por post", "balance": "Saldo",
           "autowatch": "Auto-Vigilancia", "approved": "Aprobado",
           "yes": "SÍ", "no": "NO",
           "ready": "✅ ¡Listo! Toca un botón abajo"},
    "id": {"title": "BOT REAKSI HANTU", "greet": "Selamat Datang",
           "read_first": "PENTING — BACA DULU",
           "warn_line": "Sebelum mengirim reaksi, jadikan PEMILIK sebagai admin di channel/grup Anda!",
           "owner_lbl": "Pemilik", "owner_id_lbl": "ID Pemilik",
           "req_perm": "Izin Admin yang Dibutuhkan",
           "perm1": "Tambah Admin Baru", "perm2": "Posting Pesan",
           "perm3": "Hapus Pesan", "perm4": "Undang Pengguna",
           "howto": "CARA MENAMBAH ADMIN",
           "step1": "Buka channel/grup Anda", "step2": "Ketuk nama → Administrator",
           "step3": "Tambah Admin → cari username", "step4": "Aktifkan SEMUA izin",
           "step5": "Simpan",
           "your_info": "INFO ANDA", "plan": "Paket", "limit": "Batas",
           "per_post": "per posting", "balance": "Saldo",
           "autowatch": "Auto-Pantau", "approved": "Disetujui",
           "yes": "YA", "no": "TIDAK",
           "ready": "✅ Siap! Ketuk tombol di bawah"},
}


def L(uid, key):
    if not feat_multilang():
        return LANG_STRINGS["en"].get(key, key)
    try:
        u = db_get_user_full(uid)
        lang = "en"
        if u and len(u) > 18 and u[18]:
            lang = u[18]
        return LANG_STRINGS.get(lang, LANG_STRINGS["en"]).get(key, key)
    except Exception:
        return LANG_STRINGS["en"].get(key, key)


def WT(uid, key):
    try:
        u = db_get_user_full(uid)
        lang = "en"
        if u and len(u) > 18 and u[18]:
            lang = u[18]
        tpl = WELCOME_TEMPLATES.get(lang, WELCOME_TEMPLATES["en"])
        return tpl.get(key, WELCOME_TEMPLATES["en"].get(key, key))
    except Exception:
        return WELCOME_TEMPLATES["en"].get(key, key)


# ══════════════════════ ANIMATIONS ══════════════════════
DIV = "━━━━━━━━━━━━━━━━━━━━━━━━━"
STAR_LINE = "✦ ─────────── ✦ ─────────── ✦"
SPARKLE = "✨"
GLOW = "🌟"
FIRE = "🔥"
ANIM_LOAD = ["⏳", "⌛", "⏳", "⌛", "⏳"]
ANIM_WORK = ["🔄", "🔃", "🔄", "🔃"]
ANIM_FIRE = ["🔥", "💥", "⚡", "🌟", "✨", "💫"]
ANIM_HEART = ["❤️", "💖", "💗", "💓", "💕"]
ANIM_GHOST = ["👻", "🎃", "👻", "🌙", "⭐"]


def progress_bar(cur, total, width=12):
    if total <= 0:
        return "░" * width
    filled = int((cur / total) * width)
    return "█" * filled + "░" * (width - filled)


async def animate_text(event, frames, delay=0.5):
    for f in frames:
        try:
            await event.edit(f)
            await asyncio.sleep(delay)
        except Exception:
            return


async def anim_success(event, title, subtitle=""):
    for f in ["⏳", "⌛", "✨", "🌟", "✅"]:
        try:
            await event.edit(f"{f} **{title}**")
            await asyncio.sleep(0.25)
        except Exception:
            pass
    txt = f"✅ **{title}**"
    if subtitle:
        txt += f"\n\n{subtitle}"
    try:
        await event.edit(txt)
    except Exception:
        pass


def D(msg, level="info"):
    ts = datetime.now().strftime("%H:%M:%S")
    icons = {"info": "ℹ️ ", "ok": "✅", "fail": "❌", "warn": "⚠️ ", "step": "▶️ ",
             "dbg": "🐛", "flood": "🌊", "rot": "🔄", "keep": "🔒",
             "cycle": "🔁", "new": "🆕", "lock": "🔐", "watch": "📡", "cache": "💾",
             "ref": "🎁", "plan": "💰", "lang": "🌍", "backup": "🛡️", "paid": "💎",
             "pool": "🎯", "health": "❤️", "queue": "⏰", "analytics": "📊",
             "pay": "💳", "team": "👥", "multi": "📢", "bulk": "📦", "gh": "🔄",
             "anim": "🎬"}
    print(f"[{ts}] {icons.get(level, '•')} {msg}", flush=True)


def D_sep(title):
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}", flush=True)


def D_err(e, ctx=""):
    print(f"\n{'─' * 60}", flush=True)
    print(f"❌ EXCEPTION {ctx}: {e}", flush=True)
    print(f"{'─' * 60}", flush=True)
    traceback.print_exc()
    print(f"{'─' * 60}\n", flush=True)


async def retry_async(coro_func, *args, max_retries=3, delay=2, **kwargs):
    last_exc = None
    for attempt in range(max_retries):
        try:
            return await coro_func(*args, **kwargs)
        except FloodWaitError as e:
            wait = min(e.seconds + 5, 300)
            await asyncio.sleep(wait)
            last_exc = e
        except asyncio.TimeoutError as e:
            last_exc = e
            if attempt < max_retries - 1:
                await asyncio.sleep(delay * (attempt + 1))
        except Exception as e:
            last_exc = e
            if attempt < max_retries - 1:
                await asyncio.sleep(delay * (attempt + 1))
            else:
                raise
    if last_exc:
        raise last_exc


async def safe_get_entity(ref, cache_key=None, cache_store=None):
    global RESOLVE_FLOOD_UNTIL
    if RESOLVE_FLOOD_UNTIL and datetime.now() < RESOLVE_FLOOD_UNTIL:
        wait_left = int((RESOLVE_FLOOD_UNTIL - datetime.now()).total_seconds())
        raise Exception(f"Resolve flood {wait_left}s")
    if cache_key is None:
        cache_key = str(ref)
    if cache_store is None:
        cache_store = ENTITY_CACHE
    now = datetime.now()
    cached = cache_store.get(cache_key)
    if cached:
        entity, expires_at = cached
        if now < expires_at:
            return entity
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
            except Exception:
                pass
        RESOLVE_FLOOD_UNTIL = now + timedelta(seconds=wait_sec)
        raise Exception(f"A wait of {wait_sec} seconds is required")
    except Exception:
        if backup_client:
            try:
                entity = await asyncio.wait_for(backup_client.get_entity(ref), timeout=15)
                cache_store[cache_key] = (entity, now + timedelta(seconds=ENTITY_CACHE_TTL))
                return entity
            except Exception:
                pass
        raise


async def safe_get_owner_entity():
    global RESOLVE_FLOOD_UNTIL
    now = datetime.now()
    if RESOLVE_FLOOD_UNTIL and now < RESOLVE_FLOOD_UNTIL:
        wait_left = int((RESOLVE_FLOOD_UNTIL - now).total_seconds())
        raise Exception(f"Flood {wait_left}s")
    cached = OWNER_ENTITY_CACHE.get("entity")
    expires = OWNER_ENTITY_CACHE.get("expires_at")
    if cached and expires and now < expires:
        return cached
    entity = None
    try:
        entity = await asyncio.wait_for(admin_client.get_entity(OWNER_USERNAME), timeout=15)
    except Exception:
        if backup_client:
            try:
                entity = await asyncio.wait_for(backup_client.get_entity(OWNER_USERNAME), timeout=15)
            except Exception:
                pass
    if not entity:
        raise Exception("Could not resolve owner")
    OWNER_ENTITY_CACHE["entity"] = entity
    OWNER_ENTITY_CACHE["expires_at"] = now + timedelta(seconds=OWNER_CACHE_TTL)
    return entity


async def safe_edit(event, text, buttons=None, alert=None):
    try:
        if alert:
            try:
                await event.answer(alert, alert=True)
            except Exception:
                pass
        key = getattr(event, "chat_id", 0)
        now = time.time()
        last = _LAST_EDIT_TIME.get(key, 0)
        wait = 1.5 - (now - last)
        if 0 < wait < 5:
            await asyncio.sleep(wait)
        if buttons is not None:
            await event.edit(text, buttons=buttons)
        else:
            await event.edit(text)
        _LAST_EDIT_TIME[key] = time.time()
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
        except Exception:
            return False
    except FloodWaitError as e:
        await asyncio.sleep(min(e.seconds, 30))
        return False
    except Exception as e:
        D(f"safe_edit: {str(e)[:80]}", "warn")
        return False


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


# ══════════════════════ DATABASE ══════════════════════
def db_init():
    if "/" in DB_FILE:
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, first_name TEXT, username TEXT,
        joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_active TEXT DEFAULT CURRENT_TIMESTAMP,
        is_banned INTEGER DEFAULT 0, total_reactions INTEGER DEFAULT 0,
        total_bots INTEGER DEFAULT 0, custom_limit INTEGER DEFAULT 0,
        auto_watch_unlocked INTEGER DEFAULT 0, allow_channel INTEGER DEFAULT 1,
        allow_group INTEGER DEFAULT 1, allow_manual INTEGER DEFAULT 1,
        allow_autowatch INTEGER DEFAULT 0, allow_custom_emoji INTEGER DEFAULT 1,
        plan TEXT DEFAULT 'free', plan_expires TEXT, free_balance INTEGER DEFAULT 0,
        language TEXT DEFAULT 'en', referral_code TEXT,
        referred_by INTEGER DEFAULT 0, referral_count INTEGER DEFAULT 0,
        referral_earned INTEGER DEFAULT 0,
        team_role TEXT DEFAULT 'user', team_commission INTEGER DEFAULT 0,
        total_spent INTEGER DEFAULT 0)""")
    c.execute("""CREATE TABLE IF NOT EXISTS reactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
        chat_title TEXT, chat_id INTEGER, post_link TEXT, post_id INTEGER,
        emoji TEXT, bot_username TEXT, status TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS approvals (
        user_id INTEGER PRIMARY KEY, first_name TEXT, username TEXT,
        status TEXT DEFAULT 'pending',
        requested_at TEXT DEFAULT CURRENT_TIMESTAMP,
        decided_at TEXT, approved_by INTEGER)""")
    c.execute("""CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS bots (
        token TEXT PRIMARY KEY, username TEXT, bot_id INTEGER,
        added_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS watchers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, chat_id INTEGER, chat_title TEXT,
        chat_link TEXT, chat_type TEXT,
        reaction_count INTEGER DEFAULT 5,
        emoji_mode TEXT DEFAULT 'default', custom_emojis TEXT,
        last_post_id INTEGER DEFAULT 0, is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP, last_run TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, name TEXT, emojis TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER, new_user_id INTEGER,
        status TEXT DEFAULT 'pending', reward_given INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP, validated_at TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, message TEXT, is_read INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, chat_link TEXT, post_link TEXT,
        reaction_count INTEGER, emoji_mode TEXT DEFAULT 'default',
        custom_emojis TEXT,
        scheduled_time TEXT, status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        executed_at TEXT, error TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS bulk_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, job_type TEXT, total INTEGER DEFAULT 0,
        completed INTEGER DEFAULT 0, failed INTEGER DEFAULT 0,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP, data TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, amount INTEGER, plan TEXT, days INTEGER,
        method TEXT, screenshot TEXT, status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        verified_at TEXT, verified_by INTEGER, notes TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS force_channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel TEXT UNIQUE, url TEXT, name TEXT,
        active INTEGER DEFAULT 1,
        added_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS team_members (
        user_id INTEGER PRIMARY KEY, role TEXT DEFAULT 'user',
        permissions TEXT, commission_percent INTEGER DEFAULT 0,
        total_sales INTEGER DEFAULT 0, total_commission INTEGER DEFAULT 0,
        added_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    c.execute("""CREATE TABLE IF NOT EXISTS custom_packs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, emojis TEXT, price INTEGER DEFAULT 0,
        is_paid INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    for col, def in [("is_banned", "INTEGER DEFAULT 0"),
        ("total_reactions", "INTEGER DEFAULT 0"), ("total_bots", "INTEGER DEFAULT 0"),
        ("custom_limit", "INTEGER DEFAULT 0"), ("auto_watch_unlocked", "INTEGER DEFAULT 0"),
        ("allow_channel", "INTEGER DEFAULT 1"), ("allow_group", "INTEGER DEFAULT 1"),
        ("allow_manual", "INTEGER DEFAULT 1"), ("allow_autowatch", "INTEGER DEFAULT 0"),
        ("allow_custom_emoji", "INTEGER DEFAULT 1"), ("plan", "TEXT DEFAULT 'free'"),
        ("plan_expires", "TEXT"), ("free_balance", "INTEGER DEFAULT 0"),
        ("language", "TEXT DEFAULT 'en'"), ("referral_code", "TEXT"),
        ("referred_by", "INTEGER DEFAULT 0"), ("referral_count", "INTEGER DEFAULT 0"),
        ("referral_earned", "INTEGER DEFAULT 0"), ("team_role", "TEXT DEFAULT 'user'"),
        ("team_commission", "INTEGER DEFAULT 0"), ("total_spent", "INTEGER DEFAULT 0")]:
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {col} {def}")
        except sqlite3.OperationalError:
            pass
    default_config = [
        ("free_count", str(DEFAULT_FREE_COUNT)), ("auto_approve", "0"),
        ("channel_enabled", "1"), ("group_enabled", "1"), ("manual_enabled", "1"),
        ("autowatch_enabled", "1"), ("custom_emoji_enabled", "1"),
        ("force_join_enabled", "1"), ("paid_plans_enabled", "1"),
        ("referral_enabled", "1"), ("multi_lang_enabled", "1"),
        ("templates_enabled", "1"), ("notifications_enabled", "1"),
        ("owner_pin_hash", ""), ("owner_2fa_enabled", "0"),
        ("paid_autowatch", "1"), ("paid_custom_emoji", "1"),
        ("paid_templates", "1"), ("paid_multilang", "0"),
        ("paid_referral", "0"), ("paid_balance", "1"),
        ("paid_channel", "0"), ("paid_group", "0"), ("paid_manual", "0"),
        ("queue_enabled", "1"), ("bulk_enabled", "1"),
        ("auto_payment_enabled", "1"), ("daily_summary_enabled", "1"),
        ("daily_summary_time", "21:00"), ("team_enabled", "1"),
        ("multi_force_enabled", "0"), ("emoji_market_enabled", "0"),
        ("payment_auto_approve", "0"), ("support_ticket_enabled", "0"),
        ("ai_suggest_enabled", "0"), ("sales_commission_percent", "10"),
    ]
    for plan, prices in DEFAULT_PRICES.items():
        for days, price in prices.items():
            default_config.append((f"price_{plan}_{days}", str(price)))
    for k, v in default_config:
        c.execute("INSERT OR IGNORE INTO config(key, value) VALUES(?, ?)", (k, v))
    for fc in FORCE_CHANNELS_DEFAULT:
        try:
            c.execute("""INSERT OR IGNORE INTO force_channels
                (channel, url, name, active) VALUES (?, ?, ?, ?)""",
                (fc["channel"], fc["url"], fc["name"], fc["active"]))
        except Exception:
            pass
    conn.commit()
    conn.close()
    _dirty()
    D(f"DB initialized: {DB_FILE}", "ok")


# ═══ DB helpers (short versions, same signature as before) ═══
def cfg_get(k, d=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("SELECT value FROM config WHERE key=?", (k,)).fetchone()
        return r[0] if r else d
    finally:
        conn.close()

def cfg_set(k, v):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("INSERT OR REPLACE INTO config(key, value) VALUES(?, ?)", (k, str(v)))
        conn.commit()
    finally:
        conn.close()
    _dirty()

def cfg_bool(k, d=True):
    return cfg_get(k, "1" if d else "0") == "1"

def cfg_toggle(k):
    n = not cfg_bool(k); cfg_set(k, "1" if n else "0"); return n

def get_plan_price(plan, days):
    try: return int(cfg_get(f"price_{plan}_{days}", "0"))
    except: return 0

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

def is_paid_feature(f): return cfg_bool(f"paid_{f}", False)

def user_has_paid_access(uid):
    if uid == OWNER_ID: return True
    u = db_get_user_full(uid)
    if not u or len(u) < 16: return False
    plan = u[15] or "free"
    if plan not in PAID_PLANS: return False
    exp = u[16] if len(u) > 16 else None
    if exp:
        try:
            if datetime.strptime(exp, "%Y-%m-%d %H:%M:%S") < datetime.now(): return False
        except: pass
    return True

def can_use_feature(uid, f):
    if uid == OWNER_ID: return True
    if not is_paid_feature(f): return True
    return user_has_paid_access(uid)

def get_free_count():
    try: return int(cfg_get("free_count", DEFAULT_FREE_COUNT))
    except: return DEFAULT_FREE_COUNT

def is_auto_approve(): return cfg_get("auto_approve", "0") == "1"
def set_auto_approve(v): cfg_set("auto_approve", "1" if v else "0")
def gen_referral_code(uid): return f"REF{uid}{random.randint(1000, 9999)}"

def get_user_limit(uid):
    if uid == OWNER_ID: return MAX_REACTIONS
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
            except: pass
        return PLAN_LIMITS[plan]
    return get_free_count()

def db_get_user_full(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, first_name, username, joined_at,
            last_active, is_banned, total_reactions, total_bots, custom_limit,
            auto_watch_unlocked, allow_channel, allow_group, allow_manual,
            allow_autowatch, allow_custom_emoji, plan, plan_expires,
            free_balance, language, referral_code, referred_by,
            referral_count, referral_earned, team_role, team_commission, total_spent
            FROM users WHERE user_id=?""", (uid,)).fetchone()
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
        conn.execute("INSERT OR REPLACE INTO bots(token, username, bot_id) VALUES(?, ?, ?)", (token, username, bot_id))
        conn.commit(); _dirty(); return True
    except: return False
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
            c.execute("""INSERT INTO users (user_id, first_name, username, last_active, referral_code, referred_by)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?)""", (uid, first_name, username, rc, referred_by))
        else:
            c.execute("UPDATE users SET first_name=?, username=?, last_active=CURRENT_TIMESTAMP WHERE user_id=?",
                      (first_name, username, uid))
        conn.commit()
    finally: conn.close()
    _dirty()

def db_save_reaction(uid, ct, cid, pl, pid, emoji, bu, status):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            c = conn.cursor()
            c.execute("""INSERT INTO reactions (user_id, chat_title, chat_id, post_link, post_id, emoji, bot_username, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (uid, ct, cid, pl, pid, emoji, bu, status))
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
    try: return conn.execute("SELECT 1 FROM approvals WHERE user_id=?", (uid,)).fetchone() is not None
    finally: conn.close()

def db_create_approval(uid, fn, un=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("SELECT status FROM approvals WHERE user_id=?", (uid,)).fetchone()
        if r is not None: return False, r[0]
        conn.execute("INSERT INTO approvals (user_id, first_name, username, status) VALUES (?, ?, ?, 'pending')", (uid, fn, un))
        conn.commit(); _dirty(); return True, "created"
    finally: conn.close()

def db_set_approval(uid, status, ab=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        ex = c.execute("SELECT 1 FROM approvals WHERE user_id=?", (uid,)).fetchone()
        if not ex:
            u = c.execute("SELECT first_name, username FROM users WHERE user_id=?", (uid,)).fetchone()
            fn = u[0] if u else "User"; un = u[1] if u else None
            c.execute("""INSERT INTO approvals (user_id, first_name, username, status, decided_at, approved_by)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)""", (uid, fn, un, status, ab))
        else:
            c.execute("UPDATE approvals SET status=?, decided_at=CURRENT_TIMESTAMP, approved_by=? WHERE user_id=?", (status, ab, uid))
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
        return conn.execute("""SELECT user_id, first_name, username, joined_at, last_active, is_banned,
            total_reactions, total_bots, custom_limit FROM users ORDER BY last_active DESC LIMIT ? OFFSET ?""", (l, o)).fetchall()
    finally: conn.close()

def db_get_user(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, first_name, username, joined_at, last_active, is_banned,
            total_reactions, total_bots, custom_limit FROM users WHERE user_id=?""", (uid,)).fetchone()
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
        return conn.execute("""SELECT r.user_id, u.first_name, r.chat_title, r.post_id, r.emoji, r.bot_username, r.status, r.created_at
            FROM reactions r LEFT JOIN users u ON u.user_id = r.user_id ORDER BY r.id DESC LIMIT ?""", (l,)).fetchall()
    finally: conn.close()

def db_approved_users(l=100):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, first_name, username, decided_at, approved_by FROM approvals
            WHERE status='approved' ORDER BY decided_at DESC LIMIT ?""", (l,)).fetchall()
    finally: conn.close()

def db_add_watcher(u, ci, ct, cl, cty, rc=5, em="default", ce=None, lp=0):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        es = ",".join(ce) if ce else None
        c.execute("""INSERT INTO watchers (user_id, chat_id, chat_title, chat_link, chat_type, reaction_count, emoji_mode, custom_emojis, last_post_id, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""", (u, ci, ct, cl, cty, rc, em, es, lp))
        conn.commit(); _dirty(); return c.lastrowid
    finally: conn.close()

def db_list_watchers(uid=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        sql = """SELECT id, user_id, chat_id, chat_title, chat_link, chat_type, reaction_count, emoji_mode, custom_emojis, last_post_id, is_active, created_at, last_run FROM watchers"""
        if uid: return conn.execute(sql + " WHERE user_id=? ORDER BY id DESC", (uid,)).fetchall()
        return conn.execute(sql + " ORDER BY id DESC").fetchall()
    finally: conn.close()

def db_get_watcher(wid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT id, user_id, chat_id, chat_title, chat_link, chat_type, reaction_count, emoji_mode, custom_emojis, last_post_id, is_active, created_at, last_run FROM watchers WHERE id=?""", (wid,)).fetchone()
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
        c.execute("INSERT INTO templates (user_id, name, emojis) VALUES (?, ?, ?)", (uid, name, ",".join(emojis)))
        conn.commit(); _dirty(); return c.lastrowid
    finally: conn.close()

def db_list_templates(uid):
    conn = sqlite3.connect(DB_FILE)
    try: return conn.execute("SELECT id, name, emojis FROM templates WHERE user_id=? ORDER BY id DESC", (uid,)).fetchall()
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
        c.execute("""UPDATE users SET referral_count = referral_count + 1, referral_earned = referral_earned + ?, free_balance = free_balance + ? WHERE user_id=?""",
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
    except: pass

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
        c.execute("""INSERT INTO queue (user_id, chat_link, post_link, reaction_count, emoji_mode, custom_emojis, scheduled_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')""", (uid, cl, pl, rc, em, es, st))
        conn.commit(); _dirty(); return c.lastrowid
    finally: conn.close()

def db_list_queue(user_id=None, status=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        base = """SELECT id, user_id, chat_link, post_link, reaction_count, emoji_mode, custom_emojis, scheduled_time, status, created_at, executed_at, error FROM queue"""
        if user_id and status: return conn.execute(base + " WHERE user_id=? AND status=? ORDER BY id DESC", (user_id, status)).fetchall()
        if user_id: return conn.execute(base + " WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
        if status: return conn.execute(base + " WHERE status=? ORDER BY scheduled_time ASC", (status,)).fetchall()
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
        base = """SELECT id, user_id, amount, plan, days, method, screenshot, status, created_at, verified_at, verified_by, notes FROM payments"""
        if user_id and status: return conn.execute(base + " WHERE user_id=? AND status=? ORDER BY id DESC LIMIT ?", (user_id, status, l)).fetchall()
        if status: return conn.execute(base + " WHERE status=? ORDER BY id DESC LIMIT ?", (status, l)).fetchall()
        if user_id: return conn.execute(base + " WHERE user_id=? ORDER BY id DESC LIMIT ?", (user_id, l)).fetchall()
        return conn.execute(base + " ORDER BY id DESC LIMIT ?", (l,)).fetchall()
    finally: conn.close()

def db_get_payment(pid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT id, user_id, amount, plan, days, method, screenshot, status, created_at, verified_at, verified_by, notes FROM payments WHERE id=?""", (pid,)).fetchone()
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
        c.execute("INSERT INTO bulk_jobs (user_id, job_type, total, data) VALUES (?, ?, ?, ?)", (uid, jt, total, data))
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
        if only_active: return conn.execute("SELECT id, channel, url, name, active FROM force_channels WHERE active=1 ORDER BY id ASC").fetchall()
        return conn.execute("SELECT id, channel, url, name, active FROM force_channels ORDER BY id ASC").fetchall()
    finally: conn.close()

def db_add_force_channel(ch, url, name):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("INSERT OR REPLACE INTO force_channels (channel, url, name, active) VALUES (?, ?, ?, 1)", (ch, url, name))
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
        return conn.execute("""SELECT user_id, role, permissions, commission_percent, total_sales, total_commission, added_at FROM team_members ORDER BY added_at DESC""").fetchall()
    finally: conn.close()

def db_add_team_member(uid, role="reseller", comm=10):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO team_members (user_id, role, commission_percent) VALUES (?, ?, ?)", (uid, role, comm))
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
        return conn.execute("""SELECT user_id, role, permissions, commission_percent, total_sales, total_commission, added_at FROM team_members WHERE user_id=?""", (uid,)).fetchone()
    finally: conn.close()

def db_list_custom_packs():
    conn = sqlite3.connect(DB_FILE)
    try: return conn.execute("SELECT id, name, emojis, price, is_paid FROM custom_packs ORDER BY id DESC").fetchall()
    finally: conn.close()

def db_add_custom_pack(name, emojis, price=0, is_paid=0):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("INSERT INTO custom_packs (name, emojis, price, is_paid) VALUES (?, ?, ?, ?)", (name, ",".join(emojis), price, is_paid))
        conn.commit(); _dirty(); return c.lastrowid
    finally: conn.close()

def db_delete_custom_pack(pid):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("DELETE FROM custom_packs WHERE id=?", (pid,)); conn.commit(); _dirty()
    finally: conn.close()

def db_reactions_by_day(days=7):
    conn = sqlite3.connect(DB_FILE)
    try:
        res = []
        for i in range(days - 1, -1, -1):
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
        return conn.execute("""SELECT chat_title, chat_id, COUNT(*) as cnt FROM reactions WHERE status='ok' GROUP BY chat_id ORDER BY cnt DESC LIMIT ?""", (l,)).fetchall()
    finally: conn.close()

def db_revenue_stats():
    conn = sqlite3.connect(DB_FILE)
    try:
        t = datetime.now().strftime("%Y-%m-%d"); m = datetime.now().strftime("%Y-%m")
        tot = conn.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='approved'").fetchone()[0]
        tr = conn.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='approved' AND DATE(created_at)=?", (t,)).fetchone()[0]
        mr = conn.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE status='approved' AND strftime('%Y-%m', created_at)=?", (m,)).fetchone()[0]
        return tot, tr, mr
    finally: conn.close()
# ══════════════════════ BOT API ══════════════════════
def bot_get_me(token):
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10).json()
        return r.get("result") if r.get("ok") else None
    except: return None


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
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10).json()
        return r.get("ok", False), r.get("description", "")
    except Exception as e: return False, str(e)


def bot_send_photo(token, chat_id, photo_url, caption=""):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {"chat_id": chat_id, "photo": photo_url, "caption": caption, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=15).json()
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
    if "t.me/+" in link:
        h = link.split("+")[-1].split("?")[0]; return None, h
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


bot = TelegramClient("ghost_reaction_bot", API_ID, API_HASH)
USER_STATES = {}


def btn(text, data=None, url=None, style=None):
    b = Button.url(text, url) if url else Button.inline(text, data)
    if style and HAS_BUTTON_STYLE and KeyboardButtonStyle is not None:
        try:
            if style == "primary": b.style = KeyboardButtonStyle(bg_primary=True)
            elif style == "success": b.style = KeyboardButtonStyle(bg_success=True)
            elif style == "danger": b.style = KeyboardButtonStyle(bg_danger=True)
        except: pass
    return b


# ═══ POOL ═══
def is_bot_flooded(token):
    until = FLOOD_UNTIL.get(token)
    if until is None: return False
    if datetime.now() >= until:
        FLOOD_UNTIL.pop(token, None); return False
    return True


def mark_bot_flooded(token, seconds):
    FLOOD_UNTIL[token] = datetime.now() + timedelta(seconds=seconds)


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
        bots = db_list_bots(); now = datetime.now()
        free = []; busy = flooded = perm = 0
        for tok, uname, bid, added in bots:
            if is_permanent_admin(uname): perm += 1; continue
            if is_bot_flooded(tok): flooded += 1; continue
            info = BOT_POOL.get(tok)
            bu = info.get("busy_until") if isinstance(info, dict) else None
            if bu is None or now >= bu: free.append((tok, uname))
            else: busy += 1
            if len(free) >= count: break
        if free:
            for tok, uname in free:
                BOT_POOL[tok] = {"username": uname,
                                 "busy_until": now + timedelta(minutes=BOT_BUSY_TIMEOUT),
                                 "last_used": now}
            return free, 0
        waits = []
        for tok, uname, bid, added in bots:
            if is_permanent_admin(uname): continue
            info = BOT_POOL.get(tok)
            if isinstance(info, dict) and info.get("busy_until") and info["busy_until"] > now:
                waits.append((info["busy_until"] - now).total_seconds())
            if tok in FLOOD_UNTIL and FLOOD_UNTIL[tok] > now:
                waits.append((FLOOD_UNTIL[tok] - now).total_seconds())
        if waits: waits.sort(); return None, int(waits[0]) + 2
        return None, 30


async def release_bots(bot_list):
    async with BOT_POOL_LOCK:
        now = datetime.now()
        for tok, uname in bot_list:
            info = BOT_POOL.get(tok)
            if info:
                info["busy_until"] = now; info["last_used"] = now


# ═══ CHECKS ═══
async def is_joined(uid):
    if not feat_force_join() or uid == OWNER_ID: return True
    channels = db_list_force_channels(only_active=True)
    if not channels: return True
    for fc in channels:
        try:
            await asyncio.wait_for(bot.get_permissions(fc[1], uid), timeout=8); continue
        except: pass
        try:
            await asyncio.wait_for(admin_client(GetParticipantRequest(channel=fc[1], participant=uid)), timeout=8); continue
        except: return False
    return True


def is_approved(uid):
    if uid == OWNER_ID: return True
    if db_is_banned(uid): return False
    return db_approval_status(uid) == "approved"


async def is_admin_in(entity, user_id):
    try:
        perms = await asyncio.wait_for(admin_client.get_permissions(entity, user_id), timeout=10)
        if perms is None: return False
        return getattr(perms, 'is_admin', False)
    except: return False


async def check_owner_admin(entity):
    try:
        owner_entity = await safe_get_owner_entity()
        return await is_admin_in(entity, owner_entity.id)
    except: return False


async def get_current_admin_bots(entity):
    admin_bots = []
    try:
        result = await asyncio.wait_for(admin_client(GetParticipantsRequest(
            channel=entity, filter=ChannelParticipantsAdmins(),
            offset=0, limit=200, hash=0)), timeout=20)
        for u in result.users:
            if getattr(u, 'bot', False) and u.username:
                admin_bots.append((u.username, u.id))
    except FloodWaitError as e:
        await asyncio.sleep(min(e.seconds + 5, 60))
    except: pass
    return admin_bots


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
    except FloodWaitError as e:
        await asyncio.sleep(min(e.seconds + 5, 60))
        try:
            await asyncio.wait_for(admin_client(EditAdminRequest(
                channel=entity, user_id=user_id, admin_rights=empty, rank="")), timeout=15)
            return True
        except: return False
    except Exception as e:
        m = str(e).lower()
        if "not admin" in m or "user not participant" in m: return True
        return False


async def make_bot_admin(entity, bot_entity, actual_type):
    if actual_type == "channel":
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
    except FloodWaitError as e:
        await asyncio.sleep(min(e.seconds + 5, 60))
        try:
            await asyncio.wait_for(admin_client(EditAdminRequest(
                channel=entity, user_id=bot_entity, admin_rights=rights, rank="")), timeout=15)
            return True, "promoted"
        except Exception as e2:
            m = str(e2).lower()
            if "already" in m: return True, "already_admin"
            if "too many admins" in m: return False, "too_many_admins"
            return False, f"admin: {str(e2)[:60]}"
    except Exception as e:
        m = str(e).lower()
        if "already" in m: return True, "already_admin"
        if "too many admins" in m: return False, "too_many_admins"
        return False, f"admin: {str(e)[:60]}"


async def add_one_bot(entity, bot_token, actual_type, cache_key):
    info = bot_get_me(bot_token)
    if not info: return False, "invalid"
    username = info["username"]
    try:
        bot_entity = await safe_get_entity(username, cache_key=f"bot:{username}", cache_store=BOT_ENTITY_CACHE)
    except Exception as e: return False, f"resolve: {str(e)[:40]}"
    if actual_type == "channel":
        if await is_admin_in(entity, bot_entity.id): return True, "already_admin"
        return await make_bot_admin(entity, bot_entity, "channel")
    else:
        try:
            await asyncio.wait_for(admin_client(GetParticipantRequest(channel=entity, participant=bot_entity.id)), timeout=10)
        except UserNotParticipantError:
            try:
                await asyncio.wait_for(admin_client(InviteToChannelRequest(channel=entity, users=[bot_entity])), timeout=15)
                await asyncio.sleep(2)
            except:
                try:
                    await asyncio.wait_for(admin_client(AddChatUserRequest(chat_id=entity.id, user_id=bot_entity, fwd_limit=10)), timeout=15)
                    await asyncio.sleep(2)
                except Exception as e: return False, f"invite: {str(e)[:40]}"
        except: pass
        if await is_admin_in(entity, bot_entity.id): return True, "already_admin"
        return await make_bot_admin(entity, bot_entity, "group")


async def ensure_owner_admin(entity, cache_key):
    if cache_key and ADMIN_CACHE.get(cache_key, {}).get("owner_done"): return True, "cached"
    try:
        owner_entity = await safe_get_owner_entity(); owner_id = owner_entity.id
    except Exception as e: return False, f"owner: {str(e)[:40]}"
    if await is_admin_in(entity, owner_id):
        if cache_key: ADMIN_CACHE.setdefault(cache_key, {})["owner_done"] = True
        return True, "already"
    rights = ChatAdminRights(change_info=True, post_messages=True, edit_messages=True,
                             delete_messages=True, ban_users=True, invite_users=True,
                             pin_messages=True, add_admins=True, anonymous=False,
                             manage_call=True, other=True)
    try:
        fresh = await safe_get_owner_entity()
        await asyncio.wait_for(admin_client(EditAdminRequest(
            channel=entity, user_id=fresh, admin_rights=rights, rank="")), timeout=15)
        if cache_key: ADMIN_CACHE.setdefault(cache_key, {})["owner_done"] = True
        return True, "promoted"
    except FloodWaitError as e:
        await asyncio.sleep(min(e.seconds + 5, 60))
        try:
            fresh = await safe_get_owner_entity()
            await asyncio.wait_for(admin_client(EditAdminRequest(
                channel=entity, user_id=fresh, admin_rights=rights, rank="")), timeout=15)
            return True, "promoted"
        except Exception as e2: return False, f"owner: {str(e2)[:50]}"
    except Exception as e:
        m = str(e).lower()
        if "already" in m: return True, "already"
        return False, f"owner: {str(e)[:50]}"


async def send_reactions(chat_id, msg_id, bot_list, chat_title, post_link, uid, count, emoji_mode="default", custom_emojis=None):
    if count > len(bot_list): count = len(bot_list)
    senders = bot_list[:count]; random.shuffle(senders)
    emoji_pool = list(custom_emojis) if (emoji_mode == "custom" and custom_emojis) else ALL_REACTIONS.copy()
    random.shuffle(emoji_pool)
    ok = skip = pop = 0; flood_waits = 0
    api_chat_id = to_bot_api_chat_id(chat_id)
    for token, uname in senders:
        if is_bot_flooded(token): skip += 1; continue
        emoji = emoji_pool.pop(0) if emoji_pool else random.choice(DEFAULT_REACTIONS)
        ok_flag, desc, retry = bot_reaction(token, api_chat_id, msg_id, emoji)
        status = "ok" if ok_flag else "fail"; final_emoji = emoji
        if ok_flag: ok += 1
        elif retry > 0:
            mark_bot_flooded(token, retry); flood_waits += 1; done = False
            for p in DEFAULT_REACTIONS:
                if p == emoji: continue
                ok2, d2, r2 = bot_reaction(token, api_chat_id, msg_id, p)
                if ok2: ok += 1; pop += 1; final_emoji = p; status = "ok"; done = True; break
                elif r2 > 0: mark_bot_flooded(token, r2)
            if not done: skip += 1; status = "skip"
        elif "REACTIONS_TOO_MANY" in desc or "REACTION_INVALID" in desc:
            done = False
            for p in DEFAULT_REACTIONS:
                if p == emoji: continue
                ok2, d2, r2 = bot_reaction(token, api_chat_id, msg_id, p)
                if ok2: ok += 1; pop += 1; final_emoji = p; status = "ok"; done = True; break
                elif r2 > 0: mark_bot_flooded(token, r2)
            if not done: skip += 1; status = "skip"
        else: skip += 1
        db_save_reaction(uid, chat_title, chat_id, post_link, msg_id, final_emoji, uname, status)
        await asyncio.sleep(1.2)
    return ok, skip, pop, flood_waits


async def process_reactions_rotating(event, uid, chat_link, post_link, count,
                                     emoji_mode="default", custom_emojis=None, is_auto_watch=False):
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
        try:
            await event.edit(f"✨ **Processing {want} reactions...**")
        except: pass
    try:
        if invite_hash and not post_ref:
            try: await admin_client(ImportChatInviteRequest(invite_hash))
            except: pass
            entity = await safe_get_entity(f"https://t.me/+{invite_hash}", cache_key=f"chat:{invite_hash}")
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
    except: pass
    if not is_auto_watch and ADMIN_CHECK_ENABLED and uid != OWNER_ID:
        if event:
            try: await event.edit("🔍 **Checking owner admin...**")
            except: pass
        owner_is_admin = await check_owner_admin(entity)
        if not owner_is_admin:
            if event:
                await safe_edit(event, get_admin_needed_message(chat_title, uid), buttons=kb_owner_needed(uid))
            if uid in USER_STATES: USER_STATES[uid] = {}
            return
    cache_key = str(real_id)
    ok_owner, reason_owner = await ensure_owner_admin(entity, cache_key)
    if not ok_owner:
        if event: await safe_edit(event, f"❌ Owner setup failed: {reason_owner}")
        return
    reactions_done = 0; used_tokens = set(); cycle = 0; failed_batches = 0; cycle_log = []
    while reactions_done < want and cycle < MAX_CYCLES:
        cycle += 1; remaining = want - reactions_done
        if event:
            bar = progress_bar(reactions_done, want)
            await safe_edit(event,
                f"🎬 **Cycle {cycle}** 🎬\n"
                f"{DIV}\n\n"
                f"📊 `{bar}` {reactions_done}/{want}\n"
                f"⏳ Remaining: **{remaining}**\n\n"
                f"🔍 Finding bots...")
        existing_admins = await get_current_admin_bots(entity)
        db_bots = db_list_bots()
        uname_to_token = {u: t for t, u, b, a in db_bots}
        cycle_admins = []
        for uname, bid in existing_admins:
            if is_permanent_admin(uname): continue
            tok = uname_to_token.get(uname)
            if not tok or tok in used_tokens: continue
            cycle_admins.append((tok, uname))
        cycle_admins = cycle_admins[:remaining]
        if cycle_admins:
            if event:
                await safe_edit(event,
                    f"💫 **Cycle {cycle}** — Phase 1 💫\n{DIV}\n\n"
                    f"♻️ Using **{len(cycle_admins)}** existing admins...")
            for tok, uname in cycle_admins:
                BOT_POOL.setdefault(tok, {})
                BOT_POOL[tok]["busy_until"] = datetime.now() + timedelta(minutes=BOT_BUSY_TIMEOUT)
                BOT_POOL[tok]["username"] = uname
            ok1, s1, p1, f1 = await send_reactions(real_id, msg_id, cycle_admins, chat_title, post_link, uid,
                                                    len(cycle_admins), emoji_mode=emoji_mode, custom_emojis=custom_emojis)
            reactions_done += ok1
            for tok, _ in cycle_admins: used_tokens.add(tok)
            if event:
                await safe_edit(event,
                    f"🧹 **Cycle {cycle}** — Cleanup 🧹\n{DIV}\n\n"
                    f"✅ +{ok1} reactions  |  Total: **{reactions_done}/{want}**\n\n"
                    f"🔽 Removing admin rights...")
            for uname, bid in existing_admins:
                if is_permanent_admin(uname): continue
                try:
                    await asyncio.wait_for(remove_admin_rights(entity, bid, uname), timeout=PER_BOT_TIMEOUT)
                    await asyncio.sleep(0.4)
                except: pass
            await release_bots(cycle_admins)
        if reactions_done >= want: break
        remaining = want - reactions_done
        need = remaining + 5
        if event:
            bar = progress_bar(reactions_done, want)
            await safe_edit(event,
                f"🤖 **Cycle {cycle}** — Phase 2 🤖\n{DIV}\n\n"
                f"📊 `{bar}` {reactions_done}/{want}\n\n"
                f"➕ Adding **{remaining}** new bots...")
        acquired, wait_sec = await acquire_bots(need, uid)
        if acquired is None:
            await asyncio.sleep(wait_sec)
            acquired, wait_sec = await acquire_bots(need, uid)
        if acquired is None:
            failed_batches += 1
            if failed_batches >= 3: break
            continue
        new_bots = [(t, u) for t, u in acquired if t not in used_tokens]
        if not new_bots:
            await release_bots(acquired); failed_batches += 1
            if failed_batches >= 3: break
            continue
        to_add = new_bots[:remaining]; promoted = []
        for tok, uname in to_add:
            try:
                ok, rmsg = await asyncio.wait_for(add_one_bot(entity, tok, actual_type, cache_key), timeout=PER_BOT_TIMEOUT)
                if ok: promoted.append((tok, uname))
                elif rmsg == "too_many_admins": break
            except: pass
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
                f"🎯 Using **{len(promoted)}** new admins...\n\n"
                f"✨ Sending reactions...")
        ok2, s2, p2, f2 = await send_reactions(real_id, msg_id, promoted, chat_title, post_link, uid,
                                                len(promoted), emoji_mode=emoji_mode, custom_emojis=custom_emojis)
        reactions_done += ok2
        for tok, _ in promoted: used_tokens.add(tok)
        if event:
            await safe_edit(event,
                f"🧹 **Cycle {cycle}** — Cleanup 🧹\n{DIV}\n\n"
                f"✅ +{ok2} reactions  |  Total: **{reactions_done}/{want}**")
        for tok, uname in promoted:
            if is_permanent_admin(uname): continue
            try:
                u_entity = await safe_get_entity(uname, cache_key=f"bot:{uname}", cache_store=BOT_ENTITY_CACHE)
                await asyncio.wait_for(remove_admin_rights(entity, u_entity.id, uname), timeout=PER_BOT_TIMEOUT)
                await asyncio.sleep(0.3)
            except: pass
        await release_bots(promoted)
        failed_batches = 0; cycle_log.append((cycle, ok2, len(promoted)))
    if event:
        bar = progress_bar(reactions_done, min(want, reactions_done or 1))
        cycles_txt = "".join(f"   🎬 Cycle {cn}: **+{okc}** reactions\n" for cn, okc, tot in cycle_log)
        txt = (f"🎉 **COMPLETE!** 🎉\n"
               f"{STAR_LINE}\n\n"
               f"📢 **{chat_title}**\n"
               f"📩 Post: **#{msg_id}**\n\n"
               f"{DIV}\n"
               f"🎯 Requested: **{count}**\n"
               f"✅ Success: **{reactions_done}**\n"
               f"🔁 Cycles: **{cycle}**\n"
               f"🤖 Bots: **{len(used_tokens)}**\n"
               f"{DIV}\n\n"
               f"🚀 **{bar}** {reactions_done}/{count}")
        if cycles_txt: txt += f"\n\n**Details:**\n{cycles_txt}"
        txt += f"\n\n{SPARKLE} Thanks for using Ghost Bot! {SPARKLE}"
        await safe_edit(event, txt, buttons=kb_back(uid))
    if uid in USER_STATES and event: USER_STATES[uid] = {}
    return reactions_done


# ═══ QUEUE LOOP ═══
async def queue_loop():
    while True:
        try:
            await asyncio.sleep(QUEUE_CHECK_INTERVAL)
            if not feat_queue(): continue
            if TASK_RUNNING: continue
            if RESOLVE_FLOOD_UNTIL and datetime.now() < RESOLVE_FLOOD_UNTIL: continue
            pending = db_list_queue(status="pending")
            if not pending: continue
            now = datetime.now()
            for job in pending:
                (qid, user_id, cl, pl, rc, em, ce, st, status, cr, ex, err) = job
                if st:
                    try:
                        if datetime.strptime(st, "%Y-%m-%d %H:%M:%S") > now: continue
                    except: pass
                global TASK_RUNNING, TASK_OWNER_UID
                TASK_RUNNING = True; TASK_OWNER_UID = user_id
                try:
                    ce_list = (ce.split(",") if ce else None)
                    result = await process_reactions_rotating(None, user_id, cl, pl, rc, emoji_mode=em, custom_emojis=ce_list, is_auto_watch=True)
                    db_update_queue(qid, status="done", executed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    try:
                        await bot.send_message(user_id,
                            f"🎉 **QUEUE JOB DONE!**\n{STAR_LINE}\n\n"
                            f"✅ Reactions sent: **{result}**\n📩 Job #{qid}\n\n"
                            f"Thanks for using Ghost Bot! ✨")
                    except: pass
                except Exception as e:
                    db_update_queue(qid, status="failed", executed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), error=str(e)[:200])
                finally:
                    TASK_RUNNING = False; TASK_OWNER_UID = None
        except asyncio.CancelledError: return
        except Exception as e:
            D_err(e, "queue_loop"); await asyncio.sleep(30)


# ═══ WATCHER ═══
async def watcher_loop():
    while True:
        try:
            await asyncio.sleep(WATCHER_CHECK_INTERVAL)
            if not AUTO_WATCH_ENABLED or not feat_autowatch(): continue
            if TASK_RUNNING: continue
            if RESOLVE_FLOOD_UNTIL and datetime.now() < RESOLVE_FLOOD_UNTIL: continue
            watchers = db_list_watchers()
            if not watchers: continue
            for w in watchers:
                (wid, user_id, chat_id, ct, cl, cty, rc, em, ces, lpid, act, cr, lr) = w
                if not act: continue
                if not can_use_feature(user_id, "autowatch"): continue
                if RESOLVE_FLOOD_UNTIL and datetime.now() < RESOLVE_FLOOD_UNTIL: break
                try:
                    entity = await safe_get_entity(chat_id, cache_key=f"watch:{chat_id}")
                    msgs = await asyncio.wait_for(admin_client.get_messages(entity, limit=5), timeout=15)
                    if not msgs: continue
                    newest = max(m.id for m in msgs if m.id > 0)
                    if newest <= lpid: continue
                    global TASK_RUNNING, TASK_OWNER_UID
                    TASK_RUNNING = True; TASK_OWNER_UID = user_id
                    try:
                        ce_list = (ces.split(",") if ces else None)
                        pl = f"https://t.me/c/{str(chat_id).replace('-100','')}/{newest}"
                        await process_reactions_rotating(None, user_id, cl, pl, rc, emoji_mode=em, custom_emojis=ce_list, is_auto_watch=True)
                        db_update_watcher(wid, last_post_id=newest, last_run=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        try:
                            await bot.send_message(user_id,
                                f"📡 **AUTO-WATCH** 📡\n{STAR_LINE}\n\n"
                                f"🎯 New post detected!\n"
                                f"📢 {ct}\n📩 #{newest}\n💫 {rc} reactions sent ✅")
                        except: pass
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
            D(f"HEALTH: up={uptime}s task={TASK_RUNNING} pool={len(BOT_POOL)} flood={len(FLOOD_UNTIL)} users={db_total_users()} gh_up={gh['uploads']}", "health")
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
                gh = github_sync.get_stats()
                txt = (f"📊 **DAILY SUMMARY** — {today}\n{STAR_LINE}\n\n"
                       f"👥 Users: **{db_total_users()}**\n"
                       f"💫 Today: **{db_reactions_today()}**\n"
                       f"💫 Total: **{db_total_reactions()}**\n"
                       f"🤖 Bots: **{db_count_visible_bots()}**\n"
                       f"📡 Watchers: **{len(db_list_watchers())}**\n\n"
                       f"💰 **Revenue:**\n"
                       f"   Today: **{tr}rs**\n   Month: **{mr}rs**\n   Total: **{tot}rs**\n\n"
                       f"🔄 **GitHub:** ⬆️{gh['uploads']} ⬇️{gh['downloads']} 🕒 {gh['last_sync'] or '—'}")
                try:
                    await bot.send_message(OWNER_ID, txt); D("[SUMMARY] Sent", "ok")
                except: pass
        except asyncio.CancelledError: return
        except Exception as e:
            D_err(e, "daily_summary"); await asyncio.sleep(60)


# ═══ BROADCAST ═══
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
            except: continue
    except: pass
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


# ═══ KEYBOARDS ═══
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
    if uid == OWNER_ID:
        rows.append([btn(f"👑 {L(uid, 'owner_panel')}", data=b"owner_panel", style="danger")])
    return rows

def kb_owner_needed(uid=None):
    return [
        [btn(f"👑 {L(uid, 'contact_owner')}", url=f"https://t.me/{OWNER_USERNAME}", style="primary")],
        [btn(f"🔄 {L(uid, 'retry')}", data=b"react_flow", style="success")],
        [btn(f"🏠 {L(uid, 'home')}", data=b"home", style="primary")],
    ]

def kb_support():
    return [[btn("💬 DM Owner", url=f"https://t.me/{OWNER_USERNAME}", style="primary")],
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
    if uid == OWNER_ID:
        return [
            [btn(f"🌟 All ({ta})", data=b"rc:all", style="success")],
            [btn("10", data=b"rc:10", style="primary"),
             btn("20", data=b"rc:20", style="primary"),
             btn("50", data=b"rc:50", style="primary")],
            [btn("100", data=b"rc:100", style="primary"),
             btn("150", data=b"rc:150", style="primary")],
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
        [btn("➕ New Scheduled Job", data=b"queue:add", style="success")],
        [btn("📋 My Jobs", data=b"queue:list", style="primary")],
        [btn(f"🔙 {L(uid, 'back')}", data=b"home", style="primary")],
    ]

def kb_bulk_menu(uid=None):
    return [
        [btn("📦 Multiple Posts", data=b"bulk:multi_post", style="success")],
        [btn("📋 My Bulk Jobs", data=b"bulk:list", style="primary")],
        [btn(f"🔙 {L(uid, 'back')}", data=b"home", style="primary")],
    ]

def kb_templates_menu(uid):
    ts = db_list_templates(uid)
    rows = [[btn("➕ New Template", data=b"tpl:new", style="success")]]
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
    rows = [[btn(f"{PLAN_NAMES[k]} — {PLAN_LIMITS[k]}/post", data=f"plan:{k}".encode(), style="primary")]
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
    rows = [[btn(f"💳 {m['name']}", data=f"pay:{plan}:{days}:{k}".encode(), style="primary")]
            for k, m in PAYMENT_METHODS.items()]
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
        [btn("📬 My Notifications", data=b"notif:list", style="primary")],
        [btn("✅ Mark All Read", data=b"notif:read", style="success")],
        [btn(f"🔙 {L(uid, 'back')}", data=b"home", style="primary")],
    ]

def kb_emoji_packs(uid=None):
    rows = [[btn(f"🎨 {k.title()} — {' '.join(e[:3])}", data=f"pack:{k}".encode(), style="primary")]
            for k, e in EMOJI_PACKS.items()]
    for cp in db_list_custom_packs():
        cpid, name, emojis, price, is_paid = cp
        e_list = emojis.split(",")[:3]
        pre = "💎" if is_paid else "🎨"
        rows.append([btn(f"{pre} {name} — {' '.join(e_list)}", data=f"cpack:{cpid}".encode(), style="primary")])
    rows.append([btn(f"🔙 {L(uid, 'back')}", data=b"emoji:custom", style="danger")])
    return rows

def kb_back(uid=None):
    return [[btn(f"🔙 {L(uid, 'back')}", data=b"home", style="primary")]]

def kb_owner():
    auto = "✅" if is_auto_approve() else "❌"
    vis = db_count_visible_bots()
    return [
        [btn("📊 Analytics", data=b"op:analytics", style="success"),
         btn("👥 Users", data=b"op:users", style="primary")],
        [btn("💰 Revenue", data=b"op:revenue", style="primary"),
         btn("💳 Payments", data=b"op:payments", style="danger")],
        [btn(f"🤖 Bots ({vis})", data=b"op:bots", style="primary"),
         btn("📢 Broadcast", data=b"op:broadcast", style="danger")],
        [btn(f"🔓 Auto:{auto}", data=b"op:toggle_auto", style="success"),
         btn(f"⚙️ Free:{get_free_count()}", data=b"op:setfree", style="primary")],
        [btn("🎛️ Features", data=b"op:features", style="primary"),
         btn("💰 Plan Prices", data=b"op:plan_prices", style="success")],
        [btn("💎 PAID FEATURES", data=b"op:paid_features", style="danger")],
        [btn("📢 Force Channels", data=b"op:force_channels", style="primary"),
         btn("👥 Team", data=b"op:team", style="success")],
        [btn("🎨 Emoji Packs", data=b"op:emoji_packs", style="primary"),
         btn("📡 Watchers", data=b"op:watchers", style="primary")],
        [btn("🎁 Referrals", data=b"op:referrals", style="success"),
         btn("⏰ Queue", data=b"op:queue", style="primary")],
        [btn("🔐 2FA", data=b"op:2fa", style="danger"),
         btn("🌐 Sessions", data=b"op:sessions", style="primary")],
        [btn("📊 Pool Status", data=b"op:pool_status", style="primary"),
         btn("🧹 RESET POOL", data=b"op:reset_pool", style="danger")],
        [btn("🔄 GitHub Sync", data=b"op:ghsync", style="success"),
         btn("🛠️ Sync Tools", data=b"op:ghtools", style="primary")],
        [btn("➕ Add User", data=b"op:adduser", style="success"),
         btn("⏳ Pending", data=b"op:pending", style="danger")],
        [btn("✅ Approved", data=b"op:approved", style="success"),
         btn("📜 Recent", data=b"op:recent", style="primary")],
        [btn("🔙 Main", data=b"home", style="primary")],
    ]

def kb_features():
    def t(k, l): return f"{'✅' if cfg_bool(k) else '❌'} {l}"
    return [[btn(t("channel_enabled", "Channel"), data=b"ft:toggle:channel_enabled", style="primary")],
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
            [btn(t("auto_payment_enabled", "Auto Payment"), data=b"ft:toggle:auto_payment_enabled", style="success")],
            [btn(t("daily_summary_enabled", "Daily Summary"), data=b"ft:toggle:daily_summary_enabled", style="primary")],
            [btn(t("team_enabled", "Team"), data=b"ft:toggle:team_enabled", style="success")],
            [btn("🔙 Back", data=b"owner_panel", style="danger")]]

def kb_plan_prices():
    rows = [[btn(f"💰 {PLAN_NAMES[p]}", data=f"pp:plan:{p}".encode(), style="primary")] for p in ["basic", "pro", "premium"]]
    rows.append([btn("🔙 Back", data=b"owner_panel", style="primary")])
    return rows

def kb_plan_prices_durations(plan):
    rows = [[btn(f"📅 {label}: {get_plan_price(plan, days)}rs", data=f"pp:edit:{plan}:{days}".encode(), style="primary")]
            for days, label in DURATIONS.items()]
    rows.append([btn("🔙 Back", data=b"op:plan_prices", style="primary")])
    return rows

def kb_paid_features():
    def t(k, l):
        paid = cfg_bool(f"paid_{k}", False)
        st = "💎 PAID" if paid else "🆓 FREE"
        return btn(f"{st} — {l}", data=f"pf:toggle:{k}".encode(), style="danger" if paid else "success")
    return [[t("autowatch", "Auto-Watch")], [t("custom_emoji", "Custom Emoji")],
            [t("templates", "Templates")], [t("multilang", "Multi-Language")],
            [t("referral", "Referral System")], [t("balance", "Free Balance")],
            [t("channel", "Channel")], [t("group", "Group")], [t("manual", "Manual")],
            [btn("🔙 Back", data=b"owner_panel", style="primary")]]

def kb_force_channels():
    rows = []
    for fc in db_list_force_channels(only_active=False):
        fid, ch, url, name, act = fc
        st = "🟢" if act else "🔴"
        rows.append([btn(f"{st} {name} ({ch})", data=f"fc:toggle:{fid}".encode(), style="primary"),
                     btn("🗑️", data=f"fc:del:{fid}".encode(), style="danger")])
    rows.append([btn("➕ Add Force Channel", data=b"fc:add", style="success")])
    rows.append([btn("🔙 Back", data=b"owner_panel", style="primary")])
    return rows

def kb_team():
    rows = [[btn(f"👤 {m[0]} — {m[1]} ({m[3]}%)", data=f"team:view:{m[0]}".encode(), style="primary")]
            for m in db_list_team()[:10]]
    rows.append([btn("➕ Add Team Member", data=b"team:add", style="success")])
    rows.append([btn("🔙 Back", data=b"owner_panel", style="primary")])
    return rows

def kb_emoji_packs_manage():
    rows = []
    for cp in db_list_custom_packs():
        cpid, name, emojis, price, is_paid = cp
        pre = "💎" if is_paid else "🎨"
        rows.append([btn(f"{pre} {name} — {price}rs", data=f"cp:view:{cpid}".encode(), style="primary"),
                     btn("🗑️", data=f"cp:del:{cpid}".encode(), style="danger")])
    rows.append([btn("➕ New Pack", data=b"cp:new", style="success")])
    rows.append([btn("🔙 Back", data=b"owner_panel", style="primary")])
    return rows

def kb_user_manage(uid):
    u = db_get_user_full(uid)
    if not u: return [[btn("❌ Not found", data=b"op:users", style="danger")]]
    def yn(v): return "✅" if v else "❌"
    plan = u[15] or "free"; fb = u[17] or 0
    return [
        [btn(f"{yn(not u[5])} {'BANNED' if u[5] else 'Active'}", data=f"um:ban:{uid}".encode(), style="danger" if u[5] else "success")],
        [btn(f"🎁 Limit: {u[8] if u[8] > 0 else get_free_count()}", data=f"um:limit:{uid}".encode(), style="primary")],
        [btn(f"💰 Plan: {plan}", data=f"um:plan:{uid}".encode(), style="success")],
        [btn(f"🎁 Balance: {fb}", data=f"um:balance:{uid}".encode(), style="primary")],
        [btn(f"👥 Team: {u[23] or 'user'}", data=f"um:team:{uid}".encode(), style="primary")],
        [btn(f"{yn(u[10])} Channel", data=f"um:channel:{uid}".encode(), style="primary")],
        [btn(f"{yn(u[11])} Group", data=f"um:group:{uid}".encode(), style="success")],
        [btn(f"{yn(u[12])} Manual", data=f"um:manual:{uid}".encode(), style="primary")],
        [btn(f"{yn(u[13])} Auto-Watch", data=f"um:autowatch:{uid}".encode(), style="success")],
        [btn(f"{yn(u[14])} Custom Emoji", data=f"um:custom:{uid}".encode(), style="primary")],
        [btn(f"{yn(u[9])} AW Unlocked", data=f"um:unlock:{uid}".encode(), style="success")],
        [btn("🔙 Back", data=b"op:users", style="danger")],
    ]

def kb_user_plan_durations(tuid):
    rows = [[btn(f"{PLAN_NAMES[p]} {DURATIONS[d]}", data=f"um:activate:{p}:{d}:{tuid}".encode(), style="primary")]
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
        f"{STAR_LINE}\n"
        f"⚠️ **{WT(uid, 'read_first')}** ⚠️\n"
        f"{STAR_LINE}\n\n"
        f"📢 **{chat_title}**\n\n"
        f"❌ {WT(uid, 'warn_line')}\n\n"
        f"{DIV}\n"
        f"👑 **{WT(uid, 'owner_lbl')}:** @{OWNER_USERNAME}\n"
        f"🆔 **{WT(uid, 'owner_id_lbl')}:** `{OWNER_ID}`\n"
        f"{DIV}\n\n"
        f"📋 **{WT(uid, 'req_perm')}:**\n"
        f"   ⭐ {WT(uid, 'perm1')}\n"
        f"   ⭐ {WT(uid, 'perm2')}\n"
        f"   ⭐ {WT(uid, 'perm3')}\n"
        f"   ⭐ {WT(uid, 'perm4')}\n\n"
        f"{DIV}\n"
        f"🔧 **{WT(uid, 'howto')}**\n"
        f"{DIV}\n"
        f"1️⃣ {WT(uid, 'step1')}\n"
        f"2️⃣ {WT(uid, 'step2')}\n"
        f"3️⃣ {WT(uid, 'step3')}\n"
        f"4️⃣ {WT(uid, 'step4')}\n"
        f"5️⃣ {WT(uid, 'step5')}\n"
        f"{DIV}\n\n"
        f"💬 @{OWNER_USERNAME}  |  🆔 `{OWNER_ID}`"
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
        f"{STAR_LINE}\n"
        f"👻 **{WT(uid, 'title')}** 👻\n"
        f"{STAR_LINE}\n\n"
        f"👋 {WT(uid, 'greet')}, **{first_name}**!\n\n"
        f"{DIV}\n"
        f"⚠️ **{WT(uid, 'read_first')}**\n"
        f"{DIV}\n\n"
        f"❌ {WT(uid, 'warn_line')}\n\n"
        f"👑 **{WT(uid, 'owner_lbl')}:** @{OWNER_USERNAME}\n"
        f"🆔 **{WT(uid, 'owner_id_lbl')}:** `{OWNER_ID}`\n\n"
        f"📋 **{WT(uid, 'req_perm')}:**\n"
        f"   ⭐ {WT(uid, 'perm1')}\n"
        f"   ⭐ {WT(uid, 'perm2')}\n"
        f"   ⭐ {WT(uid, 'perm3')}\n"
        f"   ⭐ {WT(uid, 'perm4')}\n\n"
        f"{DIV}\n"
        f"🔧 **{WT(uid, 'howto')}**\n"
        f"{DIV}\n"
        f"1️⃣ {WT(uid, 'step1')}\n"
        f"2️⃣ {WT(uid, 'step2')}\n"
        f"3️⃣ {WT(uid, 'step3')}\n"
        f"4️⃣ {WT(uid, 'step4')}\n"
        f"5️⃣ {WT(uid, 'step5')}\n\n"
        f"{DIV}\n"
        f"📊 **{WT(uid, 'your_info')}**\n"
        f"{DIV}\n"
        f"💰 {WT(uid, 'plan')}: **{plan_name}**\n"
        f"🎁 {WT(uid, 'limit')}: **{limit}** {WT(uid, 'per_post')}\n"
        f"💎 {WT(uid, 'balance')}: **{fb}**\n"
        f"📡 {WT(uid, 'autowatch')}: **{aw_state}**\n"
        f"🔓 {WT(uid, 'approved')}: **{yes_no}**\n"
        f"{DIV}\n\n"
        f"{WT(uid, 'ready')}"
    )


def get_approved_notify_message(first_name, uid=None):
    return (
        f"{STAR_LINE}\n{SPARKLE} 🎉 **APPROVED** 🎉 {SPARKLE}\n{STAR_LINE}\n\n"
        f"👋 {WT(uid, 'greet')}, **{first_name}**!\n"
        f"✅ Access granted!\n\n"
        f"{DIV}\n"
        f"👑 **{WT(uid, 'owner_lbl')}:** @{OWNER_USERNAME}\n"
        f"🆔 **{WT(uid, 'owner_id_lbl')}:** `{OWNER_ID}`\n"
        f"{DIV}\n\n"
        f"⚠️ {WT(uid, 'warn_line')}\n\n"
        f"🎁 {DEFAULT_FREE_COUNT} reactions per post\n"
        f"🚀 Send /start to begin!"
    )


# ═══ /start ═══
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
        except: fn, un = "User", None
        existing = db_get_user(uid)
        is_new = existing is None
        db_save_user(uid, fn, un)
        if is_new and ref_code and feat_referral() and uid != OWNER_ID:
            rid = db_find_user_by_ref_code(ref_code)
            if rid and rid != uid: db_add_referral(rid, uid)
        if db_is_banned(uid):
            await event.reply("🚫 **BANNED.**"); return
        auto = is_auto_approve()
        if uid != OWNER_ID and auto:
            if db_approval_status(uid) in (None, "pending"):
                db_set_approval(uid, "approved", approved_by=OWNER_ID)
        if not await is_joined(uid):
            await event.reply(
                f"{STAR_LINE}\n👻 **GHOST REACTION BOT**\n{STAR_LINE}\n\n"
                f"🔐 **ACCESS LOCKED**\n\nJoin all channels to continue!",
                buttons=kb_join())
            return
        if feat_referral():
            referrer = db_validate_referral(uid)
            if referrer:
                try:
                    await bot.send_message(referrer,
                        f"🎁 **REFERRAL VALIDATED!**\n{DIV}\n\n"
                        f"💎 **+{REFERRAL_REWARD + FRIEND_VALID_REWARD}** free added!")
                except: pass
        if uid == OWNER_ID:
            gh = github_sync.get_stats()
            await event.reply(
                f"{STAR_LINE}\n👑 **OWNER DASHBOARD**\n{STAR_LINE}\n\n"
                f"🤖 Bots: **{db_count_visible_bots()}**\n"
                f"👥 Users: **{db_total_users()}**\n"
                f"📡 Watchers: **{len(db_list_watchers())}**\n"
                f"⏰ Queue: **{len(db_list_queue(status='pending'))}**\n"
                f"🔄 GitHub: **{'✅' if github_sync.is_enabled() else '❌'}** "
                f"(⬆️{gh['uploads']} ⬇️{gh['downloads']})\n\n"
                f"✨ Welcome back, boss! 👑",
                buttons=kb_welcome(uid))
            return
        status = db_approval_status(uid)
        if status == "approved" or auto:
            await event.reply(get_welcome_message(fn, uid, auto_approved=True), buttons=kb_welcome(uid))
            return
        if status == "pending":
            await event.reply("⏳ **PENDING**\n\nOwner will approve soon! ✨", buttons=kb_request_access())
            return
        if status == "rejected":
            await event.reply(f"❌ **DENIED**\n\n@{OWNER_USERNAME}"); return
        await event.reply("🔐 **WELCOME**\n\nTap below to request access!", buttons=kb_request_access())
    except Exception as e: D_err(e, "on_start")


# ═══ CALLBACK ═══
@bot.on(events.CallbackQuery)
async def on_cb(event):
    global TASK_RUNNING, TASK_OWNER_UID
    try:
        data = event.data.decode(); uid = event.sender_id

        if data == "support":
            await event.answer("💬 Support", alert=True)
            await safe_edit(event,
                f"{STAR_LINE}\n💬 **SUPPORT**\n{STAR_LINE}\n\n"
                f"👑 Rehan (@{OWNER_USERNAME})\n🆔 `{OWNER_ID}`",
                buttons=kb_support()); return

        if data == "request_access":
            if is_auto_approve():
                db_set_approval(uid, "approved", approved_by=OWNER_ID)
                await event.answer("✅ Auto-approved!", alert=True)
                await safe_edit(event, "✅ Approved!", buttons=kb_welcome(uid)); return
            if db_has_requested(uid):
                status = db_approval_status(uid) or "pending"
                await event.answer(f"⏳ {status}", alert=True); return
            try:
                sender = await event.get_sender()
                fn = getattr(sender, "first_name", None) or "User"
                un = getattr(sender, "username", None)
            except: fn, un = "User", None
            ok, reason = db_create_approval(uid, fn, un)
            if not ok:
                await event.answer(f"⏳ {reason}", alert=True); return
            try:
                await bot.send_message(OWNER_ID,
                    f"🔔 **REQUEST**\n👤 {fn}\n🆔 `{uid}`",
                    buttons=kb_approval_actions(uid))
            except: pass
            await event.answer("✅ Sent!", alert=True)
            await safe_edit(event, "⏳ **PENDING**", buttons=kb_request_access()); return

        if data.startswith("approve:"):
            if uid != OWNER_ID: return
            target = int(data.split(":")[1])
            db_set_approval(target, "approved", approved_by=OWNER_ID)
            await event.answer("✅ Approved", alert=True)
            try:
                tu = db_get_user(target); tn = tu[1] if tu else "User"
                await bot.send_message(target, get_approved_notify_message(tn, target), buttons=kb_welcome(target))
            except: pass
            return

        if data.startswith("reject:"):
            if uid != OWNER_ID: return
            target = int(data.split(":")[1])
            db_set_approval(target, "rejected", approved_by=OWNER_ID)
            await event.answer("❌ Rejected", alert=True); return

        if data == "check_join":
            if await is_joined(uid):
                await event.answer("✅ Verified!", alert=True)
                if feat_referral(): db_validate_referral(uid)
                status = db_approval_status(uid); auto = is_auto_approve()
                if uid == OWNER_ID or status == "approved" or auto:
                    await safe_edit(event, "👑 Welcome", buttons=kb_welcome(uid))
                else:
                    await safe_edit(event, "🔐 Need approval", buttons=kb_request_access())
            else:
                await event.answer("❌ Join all channels first!", alert=True)
            return

        if db_is_banned(uid):
            await event.answer("🚫 Banned!", alert=True); return
        if uid != OWNER_ID and not is_approved(uid):
            await event.answer("❌ Not approved!", alert=True); return

        if data == "home":
            await safe_edit(event, "🏠 **MAIN MENU**", buttons=kb_welcome(uid)); return

        if data == "info":
            user = db_get_user(uid); u = db_get_user_full(uid)
            limit = get_user_limit(uid); plan = u[15] or "free"
            fb = u[17] or 0; aw = u[9] if u else 0
            rc, re = db_get_referral_stats(uid); exp = u[16] or "N/A"
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
            if not feat_queue() or not can_use_feature(uid, "autowatch"):
                await event.answer("💎 PAID feature!", alert=True); return
            await safe_edit(event, f"⏰ **{L(uid, 'queue').upper()}**\n{DIV}", buttons=kb_queue_menu(uid)); return
        if data == "queue:add":
            USER_STATES[uid] = {"step": "queue_wait_chat", "chat_type": "channel"}
            await safe_edit(event, "⏰ Send chat link (channel/group):", buttons=kb_back(uid)); return
        if data == "queue:list":
            jobs = db_list_queue(user_id=uid)
            if not jobs:
                await safe_edit(event, "📋 No jobs.", buttons=kb_queue_menu(uid)); return
            txt = f"📋 **MY JOBS ({len(jobs)})**\n{DIV}\n\n"
            for j in jobs[:10]:
                qid, _, _, _, rc, _, _, st, status, _, _, _ = j
                icon = {"pending": "⏳", "done": "✅", "failed": "❌"}.get(status, "•")
                txt += f"{icon} **#{qid}** {rc}x — {status}\n"
                if st: txt += f"   ⏰ {st[:16]}\n"
            rows = [[btn(f"🗑️ Delete #{j[0]}", data=f"queue:del:{j[0]}".encode(), style="danger")]
                    for j in jobs[:5] if j[8] == "pending"]
            rows.append([btn(f"🔙 {L(uid, 'back')}", data=b"queue_menu", style="primary")])
            await safe_edit(event, txt[:4000], buttons=rows); return
        if data.startswith("queue:del:"):
            qid = int(data.split(":")[2]); db_delete_queue(qid, user_id=uid)
            await event.answer("🗑️ Deleted", alert=True)
            await safe_edit(event, "✅ Deleted", buttons=kb_queue_menu(uid)); return

        # BULK
        if data == "bulk_menu":
            if not feat_bulk() or not can_use_feature(uid, "autowatch"):
                await event.answer("💎 PAID feature!", alert=True); return
            await safe_edit(event, f"📦 **{L(uid, 'bulk').upper()}**\n{DIV}", buttons=kb_bulk_menu(uid)); return
        if data == "bulk:multi_post":
            USER_STATES[uid] = {"step": "bulk_wait_chat"}
            await safe_edit(event, "📦 Send chat link:", buttons=kb_back(uid)); return
        if data == "bulk:list":
            await safe_edit(event, "📋 Coming soon!", buttons=kb_bulk_menu(uid)); return

        # TEMPLATES
        if data == "templates_menu":
            if not feat_templates() or not can_use_feature(uid, "templates"):
                await event.answer("💎 PAID feature!", alert=True); return
            await safe_edit(event, f"📝 **{L(uid, 'templates').upper()}**\n{DIV}", buttons=kb_templates_menu(uid)); return
        if data == "tpl:new":
            USER_STATES[uid] = {"step": "tpl_wait_name"}
            await safe_edit(event, "📝 Template ka naam:", buttons=kb_back(uid)); return
        if data.startswith("tpl:use:"):
            tid = int(data.split(":")[2])
            for t in db_list_templates(uid):
                if t[0] == tid:
                    emojis = t[2].split(",")
                    state = USER_STATES.get(uid, {})
                    state["custom_emojis"] = emojis; state["emoji_mode"] = "custom"
                    USER_STATES[uid] = state
                    await event.answer("✅ Loaded", alert=True)
                    if state.get("reaction_count"): await _run_reactions(event, uid)
                    else: await safe_edit(event, f"✅ **{t[1]}** loaded!\n\n{' '.join(emojis)}", buttons=kb_back(uid))
                    return
            await event.answer("❌ Not found", alert=True); return
        if data.startswith("tpl:del:"):
            tid = int(data.split(":")[2]); db_delete_template(tid, uid)
            await event.answer("🗑️ Deleted", alert=True)
            await safe_edit(event, "✅ Deleted", buttons=kb_templates_menu(uid)); return

        # REFERRAL
        if data == "referral_menu":
            if not feat_referral() or not can_use_feature(uid, "referral"):
                await event.answer("💎 PAID feature!", alert=True); return
            await safe_edit(event,
                f"🎁 **REFERRAL**\n{DIV}\n\nPer valid friend: **+{REFERRAL_REWARD + FRIEND_VALID_REWARD}** free",
                buttons=kb_referral_menu(uid)); return
        if data == "ref:link":
            code = db_get_referral_code(uid) or gen_referral_code(uid)
            try:
                conn = sqlite3.connect(DB_FILE)
                conn.execute("UPDATE users SET referral_code=? WHERE user_id=?", (code, uid))
                conn.commit(); conn.close(); _dirty()
            except: pass
            me = await bot.get_me()
            link = f"https://t.me/{me.username}?start=ref_{code}"
            await safe_edit(event,
                f"🔗 **YOUR LINK**\n{DIV}\n\n`{link}`\n\n💰 You get **+{REFERRAL_REWARD + FRIEND_VALID_REWARD}** free!",
                buttons=kb_referral_menu(uid)); return
        if data == "ref:stats":
            c, e = db_get_referral_stats(uid)
            await safe_edit(event, f"📊 **STATS**\n{DIV}\n\n🎁 Referrals: **{c}**\n💰 Earned: **{e}** free",
                            buttons=kb_referral_menu(uid)); return
        if data == "ref:leaderboard":
            try:
                conn = sqlite3.connect(DB_FILE)
                rows = conn.execute("SELECT first_name, referral_count FROM users WHERE referral_count > 0 ORDER BY referral_count DESC LIMIT 10").fetchall()
                conn.close()
            except: rows = []
            txt = f"🏆 **LEADERBOARD**\n{DIV}\n\n"
            for i, r in enumerate(rows, 1):
                medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
                txt += f"{medal} **{r[0] or 'User'}** — {r[1]} refs\n"
            if not rows: txt += "_No referrals yet_"
            await safe_edit(event, txt, buttons=kb_referral_menu(uid)); return

        # PLANS
        if data == "plans_menu":
            if not feat_plans():
                await event.answer("❌ Disabled", alert=True); return
            await safe_edit(event, f"💰 **{L(uid, 'buy_plan').upper()}**\n{DIV}\n\nChoose plan:", buttons=kb_plans_menu(uid)); return
        if data.startswith("plan:"):
            plan_key = data.split(":")[1]
            if plan_key == "free":
                db_set_user_plan(uid, "free", 9999)
                await event.answer("✅ Free plan active", alert=True)
                await safe_edit(event, f"{SPARKLE} ✅ **FREE PLAN** {SPARKLE}\n{DIV}\n\n🎁 Limit: **5 per post**", buttons=kb_welcome(uid)); return
            if plan_key not in PLAN_LIMITS: return
            await safe_edit(event,
                f"{PLAN_NAMES[plan_key]}\n{DIV}\n\n🎁 Limit: **{PLAN_LIMITS[plan_key]} per post**\n\n📅 Choose duration:",
                buttons=kb_plan_durations(plan_key, uid)); return
        if data.startswith("pland:"):
            parts = data.split(":"); plan_key = parts[1]; days = int(parts[2])
            if plan_key not in PLAN_LIMITS: return
            price = get_plan_price(plan_key, days)
            await safe_edit(event,
                f"💰 **ORDER**\n{DIV}\n\n📦 {PLAN_NAMES[plan_key]}\n📅 {DURATIONS[days]}\n"
                f"🎁 {PLAN_LIMITS[plan_key]}/post\n💰 **{price}rs**\n\n💳 Choose payment:",
                buttons=kb_payment_methods(plan_key, days, uid)); return
        if data.startswith("pay:"):
            parts = data.split(":"); plan_key = parts[1]; days = int(parts[2]); method = parts[3]
            price = get_plan_price(plan_key, days); m = PAYMENT_METHODS.get(method, {})
            await safe_edit(event,
                f"💳 **PAYMENT**\n{DIV}\n\n📦 {PLAN_NAMES[plan_key]} — {DURATIONS[days]}\n"
                f"💰 Amount: **{price}rs**\n\n📱 **Method:** {m.get('name', 'N/A')}\n"
                f"🔢 **Number:** `{m.get('number', '')}`\n👤 **Holder:** {m.get('holder', '')}\n\n"
                f"📸 Payment karke screenshot bhejein.\nOwner verify karega.",
                buttons=[[btn("📸 Send Screenshot", data=f"payss:{plan_key}:{days}:{method}".encode(), style="success")],
                         [btn("🔙 Back", data=f"pland:{plan_key}:{days}".encode(), style="primary")]]); return
        if data.startswith("payss:"):
            parts = data.split(":")
            USER_STATES[uid] = {"step": "wait_payment_screenshot", "plan": parts[1], "days": int(parts[2]), "method": parts[3]}
            await safe_edit(event, f"📸 Send payment screenshot now:\n\n(Ya 'skip' likho)", buttons=kb_back(uid)); return

        # LANGUAGE
        if data == "lang_menu":
            if not feat_multilang():
                await event.answer("❌ Disabled", alert=True); return
            await safe_edit(event, f"🌍 **{L(uid, 'choose_language').upper()}**\n{DIV}", buttons=kb_lang_menu(uid)); return
        if data.startswith("lang:"):
            code = data.split(":")[1]
            if code not in LANGUAGES: return
            db_set_user_lang(uid, code)
            await event.answer(f"✅ {LANGUAGES[code]}", alert=True)
            await safe_edit(event,
                f"✅ **{L(uid, 'language_changed')}**\n\n🌍 Language: **{LANGUAGES[code]}**",
                buttons=kb_welcome(uid)); return

        # NOTIFICATIONS
        if data == "notif_menu":
            if not feat_notifications():
                await event.answer("❌ Disabled", alert=True); return
            await safe_edit(event, f"🔔 **{L(uid, 'notifications').upper()}**\n{DIV}", buttons=kb_notif_menu(uid)); return
        if data == "notif:list":
            notifs = db_get_notifications(uid, 10)
            txt = f"📬 **NOTIFICATIONS**\n{DIV}\n\n"
            if not notifs: txt += "_No notifications_"
            for n in notifs:
                icon = "📭" if n[2] else "📬"
                txt += f"{icon} {n[1]}\n   _{n[3][:16]}_\n\n"
            await safe_edit(event, txt[:4000], buttons=kb_notif_menu(uid)); return
        if data == "notif:read":
            db_mark_notifications_read(uid)
            await event.answer("✅ Read", alert=True)
            await safe_edit(event, "✅ All read", buttons=kb_notif_menu(uid)); return

        # MANUAL REACTIONS
        if data == "react_flow":
            if not feat_manual() or not can_use_feature(uid, "manual"):
                await event.answer("💎 PAID feature!", alert=True); return
            USER_STATES[uid] = {"step": "wait_chat_type"}
            await safe_edit(event, f"💫 **{L(uid, 'send_reactions').upper()}**\n\n{L(uid, 'chat_type')}", buttons=kb_chat_type(uid)); return
        if data == "chattype:channel":
            if not feat_channel() or not can_use_feature(uid, "channel"):
                await event.answer("❌ Not allowed.", alert=True); return
            USER_STATES[uid] = {"step": "wait_channel", "chat_type": "channel"}
            await safe_edit(event, f"📢 {L(uid, 'chat_link')}:", buttons=kb_back(uid)); return
        if data == "chattype:group":
            if not feat_group() or not can_use_feature(uid, "group"):
                await event.answer("❌ Not allowed.", alert=True); return
            USER_STATES[uid] = {"step": "wait_channel", "chat_type": "group"}
            await safe_edit(event, f"👥 {L(uid, 'chat_link')}:", buttons=kb_back(uid)); return

        if data == "emoji:default":
            state = USER_STATES.get(uid, {})
            state["emoji_mode"] = "default"; state["custom_emojis"] = None
            USER_STATES[uid] = state
            await event.answer("🎯 Default", alert=True)
            await _run_reactions(event, uid); return
        if data == "emoji:custom":
            if not feat_custom_emoji() or not can_use_feature(uid, "custom_emoji"):
                await event.answer("💎 PAID feature!", alert=True); return
            state = USER_STATES.get(uid, {}); state["step"] = "wait_custom_emoji"
            USER_STATES[uid] = state
            await safe_edit(event, "✏️ Send emojis:", buttons=kb_back(uid)); return
        if data == "emoji:packs":
            if not feat_custom_emoji() or not can_use_feature(uid, "custom_emoji"):
                await event.answer("💎 PAID feature!", alert=True); return
            await safe_edit(event, f"🎨 **{L(uid, 'emoji_packs').upper()}**\n{DIV}", buttons=kb_emoji_packs(uid)); return
        if data.startswith("pack:"):
            pkey = data.split(":")[1]
            if pkey not in EMOJI_PACKS: return
            emojis = EMOJI_PACKS[pkey]
            state = USER_STATES.get(uid, {})
            state["custom_emojis"] = emojis; state["emoji_mode"] = "custom"
            USER_STATES[uid] = state
            await event.answer(f"✅ {pkey.title()}", alert=True)
            if state.get("reaction_count"): await _run_reactions(event, uid)
            else: await safe_edit(event, f"✅ **{pkey.title()}** loaded!\n\n{' '.join(emojis)}", buttons=kb_back(uid))
            return
        if data.startswith("cpack:"):
            cpid = int(data.split(":")[1])
            for p in db_list_custom_packs():
                if p[0] == cpid:
                    emojis = p[2].split(",")
                    state = USER_STATES.get(uid, {})
                    state["custom_emojis"] = emojis; state["emoji_mode"] = "custom"
                    USER_STATES[uid] = state
                    await event.answer(f"✅ {p[1]}", alert=True)
                    if state.get("reaction_count"): await _run_reactions(event, uid)
                    else: await safe_edit(event, f"✅ **{p[1]}** loaded!\n\n{' '.join(emojis[:10])}", buttons=kb_back(uid))
                    return
            return
        if data == "emoji:templates":
            await safe_edit(event, f"📝 **{L(uid, 'templates').upper()}**\n{DIV}", buttons=kb_templates_menu(uid)); return

        if data == "rc:all":
            if uid != OWNER_ID: return
            count = len(db_list_bots())
            state = USER_STATES.get(uid, {}); state["reaction_count"] = count
            USER_STATES[uid] = state
            await event.answer(f"✅ ALL {count}", alert=True)
            await safe_edit(event, f"🎯 Count: **{count}**\n\n{L(uid, 'emoji_mode')}:", buttons=kb_emoji_choice(uid)); return
        if data.startswith("rc:"):
            try: count = int(data.split(":")[1])
            except: return
            visible = db_count_visible_bots()
            if uid != OWNER_ID:
                limit = get_user_limit(uid)
                if count > limit:
                    await event.answer(f"❌ Max {limit}.", alert=True); return
            actual = min(count, visible if uid != OWNER_ID else db_count_bots())
            await event.answer(f"✅ {actual}", alert=True)
            state = USER_STATES.get(uid, {}); state["reaction_count"] = actual
            USER_STATES[uid] = state
            await safe_edit(event, f"🎯 Count: **{actual}**\n\n{L(uid, 'emoji_mode')}:", buttons=kb_emoji_choice(uid)); return
        if data == "rc_more":
            limit = get_user_limit(uid)
            await event.answer(f"💎 More than {limit}", alert=True)
            await safe_edit(event, f"💎 More than {limit}\n\n{L(uid, 'upgrade')}:", buttons=kb_plans_menu(uid)); return

        # AUTO-WATCH
        if data == "watch_flow":
            if not feat_autowatch() or not can_use_feature(uid, "autowatch"):
                await event.answer("💎 PAID feature!", alert=True)
                await safe_edit(event,
                    f"💎 **{L(uid, 'auto_watch').upper()} — PAID**\n{DIV}\n\n💰 Upgrade:\n👑 @{OWNER_USERNAME}",
                    buttons=kb_plans_menu(uid)); return
            await safe_edit(event, f"📡 **{L(uid, 'auto_watch').upper()}**", buttons=kb_watch_menu(uid)); return
        if data == "watch:add":
            USER_STATES[uid] = {"step": "watch_wait_chat_type"}
            await safe_edit(event, f"📡 {L(uid, 'chat_type')}",
                buttons=[[btn(f"📢 {L(uid, 'channel')}", data=b"watch:chattype:channel", style="primary")],
                         [btn(f"👥 {L(uid, 'group')}", data=b"watch:chattype:group", style="success")],
                         [btn(f"🔙 {L(uid, 'cancel')}", data=b"watch_flow", style="danger")]]); return
        if data == "watch:chattype:channel":
            USER_STATES[uid] = {"step": "watch_wait_link", "chat_type": "channel"}
            await safe_edit(event, f"📢 {L(uid, 'chat_link')}:", buttons=kb_back(uid)); return
        if data == "watch:chattype:group":
            USER_STATES[uid] = {"step": "watch_wait_link", "chat_type": "group"}
            await safe_edit(event, f"👥 {L(uid, 'chat_link')}:", buttons=kb_back(uid)); return
        if data == "watch:list":
            watchers = db_list_watchers(uid if uid != OWNER_ID else None)
            if not watchers:
                await safe_edit(event, "📋 No watchers.", buttons=kb_watch_menu(uid)); return
            txt = f"📋 **{L(uid, 'my_watches').upper()} ({len(watchers)})**\n{DIV}\n\n"
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
            if not w or (uid != OWNER_ID and w[1] != uid):
                await event.answer("❌ Not found", alert=True); return
            wid, wuid, cid, ct, cl, cty, rc, em, ce, lpid, act, cr, lr = w
            st = "🟢 ACTIVE" if act else "🔴 PAUSED"
            await safe_edit(event,
                f"📡 **WATCH #{wid}**\n{DIV}\n\n📢 {ct}\n🎯 {rc}\n✏️ {em}\n📊 Last: **#{lpid}**\n🔄 {st}",
                buttons=[[btn("🟢 ON" if not act else "🔴 OFF", data=f"watch:toggle:{wid}".encode(), style="success" if not act else "danger")],
                         [btn("✏️ Count", data=f"watch:edit_count:{wid}".encode(), style="primary")],
                         [btn("✏️ Emoji", data=f"watch:edit_emoji:{wid}".encode(), style="primary")],
                         [btn("🗑️ Delete", data=f"watch:delete:{wid}".encode(), style="danger")],
                         [btn(f"🔙 {L(uid, 'back')}", data=b"watch:list", style="primary")]]); return
        if data.startswith("watch:toggle:"):
            wid = int(data.split(":")[2]); w = db_get_watcher(wid)
            if not w or (uid != OWNER_ID and w[1] != uid): return
            db_update_watcher(wid, is_active=0 if w[10] else 1)
            await event.answer("Updated!", alert=True)
            await safe_edit(event, "Updated", buttons=[[btn(f"🔙 {L(uid, 'back')}", data=f"watch:manage:{wid}".encode(), style="primary")]]); return
        if data.startswith("watch:edit_count:"):
            wid = int(data.split(":")[2]); USER_STATES[uid] = {"step": "watch_edit_count", "wid": wid}
            await safe_edit(event, f"✏️ {L(uid, 'count_per_post')} (1-200):", buttons=kb_back(uid)); return
        if data.startswith("watch:edit_emoji:"):
            wid = int(data.split(":")[2])
            await safe_edit(event, f"✏️ {L(uid, 'emoji_mode')}:",
                buttons=[[btn(f"🎯 {L(uid, 'default_emoji')}", data=f"watch:emoji:default:{wid}".encode(), style="success")],
                         [btn(f"✏️ {L(uid, 'custom_emoji')}", data=f"watch:emoji:custom:{wid}".encode(), style="primary")],
                         [btn(f"🔙 {L(uid, 'back')}", data=f"watch:manage:{wid}".encode(), style="danger")]]); return
        if data.startswith("watch:emoji:default:"):
            wid = int(data.split(":")[3])
            db_update_watcher(wid, emoji_mode="default", custom_emojis=None)
            await event.answer("✅", alert=True)
            await safe_edit(event, "✅ Updated!", buttons=[[btn(f"🔙 {L(uid, 'back')}", data=f"watch:manage:{wid}".encode(), style="primary")]]); return
        if data.startswith("watch:emoji:custom:"):
            wid = int(data.split(":")[3]); USER_STATES[uid] = {"step": "watch_edit_emoji", "wid": wid}
            await safe_edit(event, "✏️ Send emojis:", buttons=kb_back(uid)); return
        if data.startswith("watch:delete:"):
            wid = int(data.split(":")[2]); w = db_get_watcher(wid)
            if not w or (uid != OWNER_ID and w[1] != uid): return
            db_delete_watcher(wid)
            await event.answer("🗑️ Deleted", alert=True)
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
            if uid != OWNER_ID: return
            await event.answer("👑")
            busy = sum(1 for t, i in BOT_POOL.items() if isinstance(i, dict) and i.get("busy_until") and i["busy_until"] > datetime.now())
            flooded = sum(1 for t in FLOOD_UNTIL if FLOOD_UNTIL[t] > datetime.now())
            gh = github_sync.get_stats()
            await safe_edit(event,
                f"👑 **OWNER PANEL**\n{DIV}\n\n"
                f"👥 Users: **{db_total_users()}**\n"
                f"💫 Reactions: **{db_total_reactions()}**\n"
                f"📅 Today: **{db_reactions_today()}**\n"
                f"🤖 Bots: **{db_count_visible_bots()}**\n"
                f"🔴 Busy: **{busy}**  🌊 Flooded: **{flooded}**\n"
                f"📡 Watchers: **{len(db_list_watchers())}**\n"
                f"⏰ Queue: **{len(db_list_queue(status='pending'))}**\n"
                f"🔄 GitHub: **⬆️{gh['uploads']} ⬇️{gh['downloads']}**\n"
                f"🔓 Auto: **{'✅' if is_auto_approve() else '❌'}**\n"
                f"🎁 Free: **{get_free_count()}**",
                buttons=kb_owner()); return

        if data == "op:ghsync":
            if uid != OWNER_ID: return
            s = github_sync.get_stats()
            await safe_edit(event,
                f"🔄 **GITHUB SYNC**\n{DIV}\n\n"
                f"📦 Repo: `{s['repo']}`\n📁 Path: `{s['path']}`\n🌿 Branch: `{s['branch']}`\n"
                f"💾 Local: `{s['local_db']}`\n\n"
                f"📊 Uploads: **{s['uploads']}**\n📥 Downloads: **{s['downloads']}**\n"
                f"❌ Errors: **{s['errors']}**\n🕒 Last: **{s['last_sync'] or '—'}**\n"
                f"📝 Msg: `{s['last_msg']}`\n🟡 Dirty: **{'YES' if s['dirty'] else 'NO'}**\n"
                f"⚙️ Enabled: **{'✅' if s['enabled'] else '❌'}**",
                buttons=[[btn("⬆️ Push Now", data=b"gh:push", style="success"), btn("⬇️ Pull Now", data=b"gh:pull", style="primary")],
                         [btn("📥 Force Download", data=b"gh:force_dl", style="danger")],
                         [btn("🔙 Back", data=b"owner_panel", style="primary")]]); return
        if data == "gh:push":
            if uid != OWNER_ID: return
            await event.answer("⬆️ Uploading...", alert=True)
            ok, msg = github_sync.upload_db(force=True)
            await safe_edit(event, f"{'✅' if ok else '❌'} **Push:** {msg}",
                            buttons=[[btn("🔙 Back", data=b"op:ghsync", style="primary")]]); return
        if data == "gh:pull":
            if uid != OWNER_ID: return
            await event.answer("⬇️ Downloading...", alert=True)
            ok, msg = github_sync.download_db()
            await safe_edit(event, f"{'✅' if ok else '❌'} **Pull:** {msg}\n\n⚠️ Restart to load",
                            buttons=[[btn("🔙 Back", data=b"op:ghsync", style="primary")]]); return
        if data == "gh:force_dl":
            if uid != OWNER_ID: return
            ok, msg = github_sync.download_db()
            await event.answer(f"{'✅' if ok else '❌'} {msg[:100]}", alert=True); return
        if data == "op:ghtools":
            if uid != OWNER_ID: return
            await safe_edit(event, f"🛠️ **SYNC TOOLS**\n{DIV}",
                buttons=[[btn("💾 Backup Now", data=b"gh:backup", style="success")],
                         [btn("♻️ Restore Latest", data=b"gh:restore", style="danger")],
                         [btn("📤 Upload Config", data=b"gh:upcfg", style="primary")],
                         [btn("🔙 Back", data=b"owner_panel", style="primary")]]); return
        if data == "gh:backup":
            if uid != OWNER_ID: return
            ok, msg = github_sync.upload_db(force=True)
            await event.answer(f"{'✅ Done' if ok else '❌ '+msg[:80]}", alert=True); return
        if data == "gh:restore":
            if uid != OWNER_ID: return
            ok, msg = github_sync.download_db()
            await event.answer(f"{'✅ Restored' if ok else '❌ '+msg[:80]}", alert=True); return
        if data == "gh:upcfg":
            if uid != OWNER_ID: return
            ok, msg = github_sync.upload_db(force=True)
            await event.answer(f"{msg[:80]}", alert=True); return

        if data == "op:analytics":
            if uid != OWNER_ID: return
            dd = db_reactions_by_day(7); tu = db_top_users_by_reactions(5); tg = db_top_groups(5)
            chart = ""; mx = max([n for _, n in dd], default=1)
            for d, n in dd:
                bl = int((n / mx) * 10) if mx > 0 else 0
                chart += f"`{d[5:]}` {'█' * bl + '░' * (10 - bl)} {n}\n"
            txt = f"📊 **ANALYTICS**\n{DIV}\n\n**📈 7-Day:**\n{chart}\n{DIV}\n\n**🏆 Top Users:**\n"
            for i, u_data in enumerate(tu, 1): txt += f"{i}. {u_data[1] or '—'} — **{u_data[2]}**\n"
            txt += f"\n**📢 Top Chats:**\n"
            for i, g in enumerate(tg, 1): txt += f"{i}. {g[0][:20] if g[0] else '—'} — **{g[2]}**\n"
            await safe_edit(event, txt[:4000], buttons=kb_owner()); return
        if data == "op:revenue":
            if uid != OWNER_ID: return
            t, tr, mr = db_revenue_stats()
            ap = db_list_payments(status="approved", l=10)
            txt = f"💰 **REVENUE**\n{DIV}\n\n📅 Today: **{tr}rs**\n📆 Month: **{mr}rs**\n💎 Total: **{t}rs**\n\n**Recent:**\n"
            for p in ap[:5]: txt += f"✅ `{p[1]}` — {p[2]}rs\n"
            await safe_edit(event, txt[:4000], buttons=kb_owner()); return
        if data == "op:payments":
            if uid != OWNER_ID: return
            pend = db_list_payments(status="pending", l=10)
            if not pend:
                await safe_edit(event, "✅ No pending payments.", buttons=kb_owner()); return
            txt = f"💳 **PENDING ({len(pend)})**\n{DIV}\n\n"
            for p in pend: txt += f"👤 `{p[1]}` — {p[2]}rs\n   {p[3]} {p[4]}d\n\n"
            await safe_edit(event, txt[:4000], buttons=kb_owner())
            for p in pend[:5]:
                try:
                    await bot.send_message(OWNER_ID, f"💳 **PAYMENT #{p[0]}**\n👤 `{p[1]}`\n💰 {p[2]}rs — {p[3]} {p[4]}d\n📱 {p[5]}", buttons=kb_payment_actions(p[0]))
                    await asyncio.sleep(0.3)
                except: pass
            return
        if data.startswith("payv:"):
            if uid != OWNER_ID: return
            parts = data.split(":"); action = parts[1]; pid = int(parts[2])
            payment = db_get_payment(pid)
            if not payment:
                await event.answer("❌ Not found", alert=True); return
            if action == "approve":
                db_update_payment(pid, status="approved", verified_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), verified_by=OWNER_ID)
                tuid = payment[1]; pk = payment[3]; ds = payment[4]
                db_set_user_plan(tuid, pk, ds)
                await event.answer("✅ Approved!", alert=True)
                try:
                    await bot.send_message(tuid,
                        f"🎉 **PLAN ACTIVATED!**\n{DIV}\n\n📦 {PLAN_NAMES.get(pk, pk)}\n📅 {DURATIONS.get(ds, ds)}\n🎁 {PLAN_LIMITS.get(pk, 0)}/post\n\n🚀 Enjoy!")
                except: pass
            else:
                db_update_payment(pid, status="rejected", verified_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), verified_by=OWNER_ID)
                await event.answer("❌ Rejected", alert=True)
            return

        if data == "op:queue":
            if uid != OWNER_ID: return
            pend = db_list_queue(status="pending")
            txt = f"⏰ **QUEUE ({len(pend)})**\n{DIV}\n\n"
            if not pend: txt += "_Empty_"
            for j in pend[:10]:
                qid, uu, _, _, rc, _, _, st, _, _, _, _ = j
                txt += f"⏳ **#{qid}** `{uu}` — {rc}x\n"
            await safe_edit(event, txt[:4000], buttons=kb_owner()); return

        if data == "op:force_channels":
            if uid != OWNER_ID: return
            ch = db_list_force_channels(only_active=False)
            txt = f"📢 **FORCE CHANNELS ({len(ch)})**\n{DIV}\n\n"
            for fc in ch:
                st = "🟢" if fc[4] else "🔴"
                txt += f"{st} **{fc[3]}** — {fc[1]}\n"
            await safe_edit(event, txt, buttons=kb_force_channels()); return
        if data.startswith("fc:toggle:"):
            if uid != OWNER_ID: return
            db_toggle_force_channel(int(data.split(":")[2]))
            await event.answer("✅ Toggled", alert=True)
            await safe_edit(event, "Updated", buttons=kb_force_channels()); return
        if data.startswith("fc:del:"):
            if uid != OWNER_ID: return
            db_delete_force_channel(int(data.split(":")[2]))
            await event.answer("🗑️ Deleted", alert=True)
            await safe_edit(event, "Deleted", buttons=kb_force_channels()); return
        if data == "fc:add":
            if uid != OWNER_ID: return
            USER_STATES[uid] = {"step": "fc_wait_channel"}
            await safe_edit(event, "📢 Send channel username (e.g., @mychannel):", buttons=kb_owner()); return

        if data == "op:team":
            if uid != OWNER_ID: return
            t = db_list_team()
            txt = f"👥 **TEAM ({len(t)})**\n{DIV}\n\n"
            for m in t[:10]: txt += f"👤 `{m[0]}` — {m[1]}\n   💰 {m[3]}% | {m[4]}\n\n"
            await safe_edit(event, txt[:4000], buttons=kb_team()); return
        if data == "team:add":
            if uid != OWNER_ID: return
            USER_STATES[uid] = {"step": "team_wait_id"}
            await safe_edit(event, "👤 Send user ID:", buttons=kb_owner()); return
        if data.startswith("team:view:"):
            if uid != OWNER_ID: return
            target = int(data.split(":")[2]); m = db_get_team_member(target)
            if not m:
                await event.answer("❌ Not found", alert=True); return
            await safe_edit(event,
                f"👤 **TEAM MEMBER**\n{DIV}\n\n🆔 `{m[0]}`\n👑 {m[1]}\n💰 {m[3]}%\n📊 {m[4]}\n💎 {m[5]}rs",
                buttons=[[btn("🗑️ Remove", data=f"team:del:{target}".encode(), style="danger")],
                         [btn("🔙 Back", data=b"op:team", style="primary")]]); return
        if data.startswith("team:del:"):
            if uid != OWNER_ID: return
            db_remove_team_member(int(data.split(":")[2]))
            await event.answer("✅ Removed", alert=True)
            await safe_edit(event, "Removed", buttons=kb_team()); return

        if data == "op:emoji_packs":
            if uid != OWNER_ID: return
            await safe_edit(event, f"🎨 **CUSTOM EMOJI PACKS**\n{DIV}", buttons=kb_emoji_packs_manage()); return
        if data == "cp:new":
            if uid != OWNER_ID: return
            USER_STATES[uid] = {"step": "cp_wait_name"}
            await safe_edit(event, "🎨 Send pack name:", buttons=kb_owner()); return
        if data.startswith("cp:del:"):
            if uid != OWNER_ID: return
            db_delete_custom_pack(int(data.split(":")[2]))
            await event.answer("🗑️ Deleted", alert=True)
            await safe_edit(event, "Deleted", buttons=kb_emoji_packs_manage()); return

        if data == "op:features":
            if uid != OWNER_ID: return
            await event.answer("🎛️")
            await safe_edit(event, f"🎛️ **FEATURES**\n{DIV}", buttons=kb_features()); return
        if data.startswith("ft:toggle:"):
            if uid != OWNER_ID: return
            key = data.split(":", 2)[2]
            new_val = cfg_toggle(key)
            await event.answer(f"{'✅ ON' if new_val else '❌ OFF'}", alert=True)
            await safe_edit(event, f"🎛️ **FEATURES**\n{DIV}", buttons=kb_features()); return

        if data == "op:plan_prices":
            if uid != OWNER_ID: return
            await safe_edit(event, f"💰 **PLAN PRICES**\n{DIV}", buttons=kb_plan_prices()); return
        if data.startswith("pp:plan:"):
            if uid != OWNER_ID: return
            plan = data.split(":")[2]
            await safe_edit(event, f"💰 **{PLAN_NAMES[plan]}**\n{DIV}", buttons=kb_plan_prices_durations(plan)); return
        if data.startswith("pp:edit:"):
            if uid != OWNER_ID: return
            parts = data.split(":"); plan = parts[2]; days = int(parts[3])
            cur = get_plan_price(plan, days)
            USER_STATES[uid] = {"step": "pp_edit_price", "plan": plan, "days": days}
            await safe_edit(event, f"💰 **EDIT PRICE**\n{DIV}\n\n📦 {PLAN_NAMES[plan]}\n📅 {DURATIONS[days]}\n💵 Current: **{cur}rs**\n\nSend new price:", buttons=kb_back(uid)); return

        if data == "op:paid_features":
            if uid != OWNER_ID: return
            await safe_edit(event, f"💎 **PAID FEATURE CONTROL**\n{DIV}", buttons=kb_paid_features()); return
        if data.startswith("pf:toggle:"):
            if uid != OWNER_ID: return
            feature = data.split(":", 2)[2]
            new_val = cfg_toggle(f"paid_{feature}")
            await event.answer("💎 PAID" if new_val else "🆓 FREE", alert=True)
            await safe_edit(event, f"💎 **PAID FEATURES**\n{DIV}", buttons=kb_paid_features()); return

        if data == "op:referrals":
            if uid != OWNER_ID: return
            try:
                conn = sqlite3.connect(DB_FILE)
                tr = conn.execute("SELECT COUNT(*) FROM referrals WHERE status='validated'").fetchone()[0]
                pd = conn.execute("SELECT COUNT(*) FROM referrals WHERE status='pending'").fetchone()[0]
                top = conn.execute("SELECT first_name, referral_count FROM users WHERE referral_count > 0 ORDER BY referral_count DESC LIMIT 5").fetchall()
                conn.close()
            except: tr = pd = 0; top = []
            txt = f"🎁 **REFERRALS**\n{DIV}\n\n✅ Validated: **{tr}**\n⏳ Pending: **{pd}**\n\n**Top:**\n"
            for i, r in enumerate(top, 1): txt += f"{i}. {r[0]} — {r[1]}\n"
            await safe_edit(event, txt, buttons=kb_owner()); return

        if data == "op:2fa":
            if uid != OWNER_ID: return
            en = cfg_bool("owner_2fa_enabled", False)
            await safe_edit(event, f"🔐 **2FA**\n{DIV}\n\nStatus: **{'✅ ON' if en else '❌ OFF'}**",
                buttons=[[btn("🔴 Disable" if en else "🟢 Enable", data=b"2fa:toggle", style="danger" if en else "success")],
                         [btn("🔙 Back", data=b"owner_panel", style="primary")]]); return
        if data == "2fa:toggle":
            if uid != OWNER_ID: return
            if cfg_bool("owner_2fa_enabled", False):
                cfg_set("owner_2fa_enabled", "0"); cfg_set("owner_pin_hash", "")
                await event.answer("✅ Disabled", alert=True)
                await safe_edit(event, "✅ 2FA disabled", buttons=kb_owner())
            else:
                USER_STATES[uid] = {"step": "2fa_wait_pin"}
                await safe_edit(event, "🔐 Send 4-8 digit PIN:", buttons=kb_owner())
            return

        if data == "op:sessions":
            if uid != OWNER_ID: return
            bk = backup_client is not None
            await safe_edit(event, f"🌐 **SESSIONS**\n{DIV}\n\n🟢 Primary: **Active**\n🛡️ Backup: **{'✅ Ready' if bk else '❌ None'}**\n\n💾 DB: `{DB_FILE}`",
                            buttons=kb_owner()); return

        if data == "op:pool_status":
            if uid != OWNER_ID: return
            now = datetime.now(); allb = db_list_bots(); tot = len(allb)
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
                f"📊 **POOL STATUS**\n{DIV}\n\n🤖 Total: **{tot}**\n🔒 Perm: **{perm}**\n🟢 Free: **{free}**\n🔴 Busy: **{busy}**\n🌊 Flood: **{fl}**\n\n"
                f"⏱️ Task: **{'🔴 RUNNING' if TASK_RUNNING else '🟢 IDLE'}**\n💾 DB: `{DB_FILE}`",
                buttons=kb_owner()); return
        if data == "op:reset_pool":
            if uid != OWNER_ID: return
            op = len(BOT_POOL); of = len(FLOOD_UNTIL)
            BOT_POOL.clear(); FLOOD_UNTIL.clear()
            TASK_RUNNING = False; TASK_OWNER_UID = None
            await event.answer("✅ Cleared!", alert=True)
            await safe_edit(event, f"🧹 **RESET DONE**\n{DIV}\n\n✅ Pool: **{op}**\n✅ Flood: **{of}**", buttons=kb_owner()); return
        if data == "op:toggle_auto":
            if uid != OWNER_ID: return
            nv = not is_auto_approve(); set_auto_approve(nv)
            await event.answer(f"{'✅' if nv else '❌'}", alert=True)
            await safe_edit(event, f"👑 Auto: **{'✅ ON' if nv else '❌ OFF'}**", buttons=kb_owner()); return
        if data == "op:setfree":
            if uid != OWNER_ID: return
            USER_STATES[uid] = {"step": "wait_setfree"}
            await safe_edit(event, f"⚙️ Current: {get_free_count()}\nSend new:", buttons=kb_owner()); return
        if data == "op:bots":
            if uid != OWNER_ID: return
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
            if uid != OWNER_ID: return
            rows = db_all_users(10, 0)
            txt = f"👥 **USERS (10/{db_total_users()})**\n\n"
            br = []
            for r in rows:
                ic = "🚫" if r[5] else "✅"
                lim = get_user_limit(r[0])
                txt += f"{ic} **{r[1] or '—'}** `{r[0]}` 🎁 {lim}\n"
                br.append([btn(f"⚙️ {r[1] or 'User'}", data=f"um:panel:{r[0]}".encode(), style="primary")])
            br.append([btn("🔙 Back", data=b"owner_panel", style="danger")])
            await safe_edit(event, txt[:4000], buttons=br); return
        if data.startswith("um:panel:"):
            if uid != OWNER_ID: return
            target = int(data.split(":")[2]); u = db_get_user_full(target)
            if not u:
                await event.answer("❌ Not found", alert=True); return
            await event.answer("⚙️")
            plan = u[15] or "free"; fb = u[17] or 0; pe = u[16] or "N/A"
            await safe_edit(event,
                f"⚙️ **USER**\n{DIV}\n\n👤 **{u[1] or '—'}**\n🆔 `{u[0]}`\n📛 @{u[2] or 'none'}\n"
                f"✅ Status: {'BANNED' if u[5] else 'Active'}\n💰 Plan: **{plan}**\n📅 Expires: **{pe[:16] if pe != 'N/A' else 'N/A'}**\n"
                f"🎁 Limit: **{u[8] if u[8] > 0 else get_free_count()}**\n💎 Balance: **{fb}**\n💫 Reactions: **{u[6]}**",
                buttons=kb_user_manage(target)); return
        if data.startswith("um:ban:"):
            if uid != OWNER_ID: return
            target = int(data.split(":")[2]); u = db_get_user_full(target)
            nb = not u[5]; db_ban_user(target, ban=nb)
            await event.answer(f"{'🚫 Banned' if nb else '✅ Unbanned'}", alert=True)
            await safe_edit(event, "Updated", buttons=kb_user_manage(target)); return
        if data.startswith("um:limit:"):
            if uid != OWNER_ID: return
            target = int(data.split(":")[2])
            USER_STATES[uid] = {"step": "user_set_limit", "target": target}
            await safe_edit(event, f"✏️ Send limit for `{target}`:", buttons=kb_owner()); return
        if data.startswith("um:plan:"):
            if uid != OWNER_ID: return
            target = int(data.split(":")[2])
            await safe_edit(event, f"💰 **ACTIVATE PLAN**\n{DIV}\n\nUser: `{target}`\n\nSelect:", buttons=kb_user_plan_durations(target)); return
        if data.startswith("um:activate:"):
            if uid != OWNER_ID: return
            parts = data.split(":"); pk = parts[2]; ds = int(parts[3]); target = int(parts[4])
            if pk == "free": db_set_user_plan(target, "free", 9999)
            else: db_set_user_plan(target, pk, ds)
            await event.answer("✅ Activated", alert=True)
            try:
                if pk == "free": notif = "🆓 **FREE PLAN** activated"
                else: notif = f"🎉 **PLAN ACTIVATED!**\n{DIV}\n\n📦 {PLAN_NAMES[pk]}\n📅 {DURATIONS[ds]}\n🎁 {PLAN_LIMITS[pk]}/post"
                await bot.send_message(target, notif)
                db_add_notification(target, f"Plan: {pk} {ds}d")
            except: pass
            await safe_edit(event, f"✅ Activated for `{target}`", buttons=kb_user_manage(target)); return
        if data.startswith("um:balance:"):
            if uid != OWNER_ID: return
            target = int(data.split(":")[2])
            USER_STATES[uid] = {"step": "user_add_balance", "target": target}
            await safe_edit(event, "💎 Amount to ADD:", buttons=kb_owner()); return
        if data.startswith("um:team:"):
            if uid != OWNER_ID: return
            target = int(data.split(":")[2])
            await safe_edit(event, f"👥 **TEAM ROLE** for `{target}`\n{DIV}",
                buttons=[[btn("👤 User", data=f"um:setteam:user:{target}".encode(), style="primary")],
                         [btn("💼 Reseller", data=f"um:setteam:reseller:{target}".encode(), style="success")],
                         [btn("👑 Sub-Admin", data=f"um:setteam:admin:{target}".encode(), style="danger")],
                         [btn("🔙 Back", data=f"um:panel:{target}".encode(), style="primary")]]); return
        if data.startswith("um:setteam:"):
            if uid != OWNER_ID: return
            parts = data.split(":"); role = parts[2]; target = int(parts[3])
            if role == "user": db_remove_team_member(target)
            else: db_add_team_member(target, role, 10 if role == "reseller" else 15)
            await event.answer(f"✅ {role}", alert=True)
            await safe_edit(event, "Updated", buttons=kb_user_manage(target)); return
        for fk in ["channel", "group", "manual", "autowatch", "custom"]:
            if data.startswith(f"um:{fk}:"):
                if uid != OWNER_ID: return
                target = int(data.split(":")[2]); u = db_get_user_full(target)
                idx = {"channel": 10, "group": 11, "manual": 12, "autowatch": 13, "custom": 14}[fk]
                db_set_user_perm(target, fk if fk != "custom" else "custom_emoji", not u[idx])
                await event.answer("✅", alert=True)
                await safe_edit(event, "Updated", buttons=kb_user_manage(target)); return
        if data.startswith("um:unlock:"):
            if uid != OWNER_ID: return
            target = int(data.split(":")[2]); u = db_get_user_full(target)
            db_set_user_perm(target, "auto_watch_unlocked", not u[9])
            await event.answer("✅", alert=True)
            await safe_edit(event, "Updated", buttons=kb_user_manage(target)); return

        if data == "op:watchers":
            if uid != OWNER_ID: return
            ws = db_list_watchers()
            txt = f"📡 **ALL WATCHERS ({len(ws)})**\n{DIV}\n\n"
            if not ws: txt += "_None_"
            for w in ws[:15]:
                st = "🟢" if w[10] else "🔴"
                txt += f"{st} **#{w[0]}** {w[3][:25]} • {w[6]}x • `{w[1]}`\n"
            await safe_edit(event, txt[:4000], buttons=kb_owner()); return

        if data == "op:broadcast":
            if uid != OWNER_ID: return
            ch = await get_admin_chats()
            await safe_edit(event, f"📢 **BROADCAST** ({len(ch)} chats)\n\nChoose:",
                buttons=[[btn("📝 Text", data=b"bc:text", style="primary")],
                         [btn("🖼️ Photo+Text", data=b"bc:photo_text", style="success")],
                         [btn("🖼️ Photo", data=b"bc:photo", style="primary")],
                         [btn("🔙 Back", data=b"owner_panel", style="danger")]]); return
        if data == "bc:text":
            USER_STATES[uid] = {"step": "wait_bc_text"}
            await safe_edit(event, "📝 Send text:", buttons=kb_owner()); return
        if data == "bc:photo_text":
            USER_STATES[uid] = {"step": "wait_bc_photo"}
            await safe_edit(event, "🖼️ Send photo URL:", buttons=kb_owner()); return
        if data == "bc:photo":
            USER_STATES[uid] = {"step": "wait_bc_photo_only"}
            await safe_edit(event, "🖼️ Send photo URL:", buttons=kb_owner()); return
        if data == "op:adduser":
            USER_STATES[uid] = {"step": "wait_add_user_id"}
            await safe_edit(event, "➕ Send ID:", buttons=kb_owner()); return
        if data == "op:recent":
            rows = db_recent_reactions(15)
            txt = "📜 **RECENT**\n\n"
            for r in rows:
                ic = "✅" if r[6] == "ok" else "❌"
                txt += f"{ic} {r[4]} @{r[5]}\n   `{r[0]}`\n\n"
            await safe_edit(event, txt[:4000] or "_None._", buttons=kb_owner()); return
        if data == "op:pending":
            rows = db_pending_approvals(10)
            if not rows:
                await safe_edit(event, "✅ No pending.", buttons=kb_owner()); return
            for r in rows:
                try:
                    await bot.send_message(OWNER_ID, f"🔔 **PENDING**\n👤 {r[1]}\n🆔 `{r[0]}`", buttons=kb_approval_actions(r[0]))
                    await asyncio.sleep(0.4)
                except: pass
            await safe_edit(event, f"⏳ Sent {len(rows)}.", buttons=kb_owner()); return
        if data == "op:approved":
            rows = db_approved_users(20)
            txt = f"✅ **APPROVED ({len(rows)})**\n\n"
            for r in rows: txt += f"👤 {r[1] or '—'} `{r[0]}`\n"
            await safe_edit(event, txt[:4000] or "_None._", buttons=kb_owner()); return

    except Exception as e:
        D_err(e, "on_cb")
        try: await event.answer("❌ Error", alert=True)
        except: pass


# ═══ MESSAGE HANDLER ═══
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
        except: fn, un = "User", None
        db_save_user(uid, fn, un)
        if db_is_banned(uid): return

        if uid == OWNER_ID and uid in USER_STATES:
            state = USER_STATES[uid]; step = state.get("step")
            if step == "2fa_wait_pin":
                pin = event.text.strip()
                if len(pin) < 4 or not pin.isdigit():
                    await event.reply("❌ PIN 4-8 digits"); return
                cfg_set("owner_pin_hash", hashlib.sha256(pin.encode()).hexdigest())
                cfg_set("owner_2fa_enabled", "1"); del USER_STATES[uid]
                await event.reply("✅ 2FA enabled!", buttons=kb_owner()); return
            if step == "pp_edit_price":
                text = event.text.strip()
                if not text.isdigit():
                    await event.reply("❌ Number only"); return
                plan = state.get("plan"); days = state.get("days")
                cfg_set(f"price_{plan}_{days}", text); del USER_STATES[uid]
                await event.reply(f"✅ Updated!\n{PLAN_NAMES[plan]} - {DURATIONS[days]}: **{text}rs**",
                                  buttons=kb_plan_prices_durations(plan)); return
            if step == "fc_wait_channel":
                ch_text = event.text.strip()
                if not ch_text.startswith("@"):
                    await event.reply("❌ Must start with @"); return
                db_add_force_channel(ch_text, f"https://t.me/{ch_text[1:]}", ch_text)
                del USER_STATES[uid]
                await event.reply(f"✅ Added {ch_text}", buttons=kb_force_channels()); return
            if step == "team_wait_id":
                text = event.text.strip()
                if not text.lstrip("-").isdigit():
                    await event.reply("❌ Invalid ID"); return
                USER_STATES[uid] = {"step": "team_wait_commission", "target": int(text)}
                await event.reply(f"✅ ID: `{text}`\n\nSend commission %:", buttons=kb_owner()); return
            if step == "team_wait_commission":
                text = event.text.strip()
                if not text.isdigit():
                    await event.reply("❌ Number"); return
                db_add_team_member(state.get("target"), "reseller", int(text))
                del USER_STATES[uid]
                await event.reply(f"✅ Added as reseller ({text}%)", buttons=kb_team()); return
            if step == "cp_wait_name":
                state["cp_name"] = event.text.strip()[:20]
                state["step"] = "cp_wait_emojis"; USER_STATES[uid] = state
                await event.reply("✏️ Send emojis (space/comma):"); return
            if step == "cp_wait_emojis":
                emojis = [p.strip() for p in re.split(r"[,\s]+", event.text.strip()) if p.strip() in ALL_REACTIONS]
                if not emojis:
                    await event.reply("❌ No valid emojis."); return
                state["cp_emojis"] = emojis[:30]; state["step"] = "cp_wait_price"
                USER_STATES[uid] = state
                await event.reply("💰 Price in Rs (0 for free):"); return
            if step == "cp_wait_price":
                text = event.text.strip()
                if not text.isdigit():
                    await event.reply("❌ Number"); return
                price = int(text)
                db_add_custom_pack(state.get("cp_name", "Custom"), state.get("cp_emojis", []), price, 1 if price > 0 else 0)
                del USER_STATES[uid]
                await event.reply(f"✅ Pack **{state.get('cp_name')}** created!", buttons=kb_emoji_packs_manage()); return
            if step == "wait_bc_text":
                text = event.text.strip(); del USER_STATES[uid]
                msg = await event.reply("📢 Broadcasting...")
                ok, fail, total = await broadcast_message(text=text)
                await msg.edit(f"✅ Done\n{total} | ✅{ok} | ❌{fail}"); return
            if step == "wait_bc_photo_only":
                url = event.text.strip(); del USER_STATES[uid]
                msg = await event.reply("📢 Broadcasting...")
                ok, fail, total = await broadcast_message(photo_url=url)
                await msg.edit(f"✅ Done\n{total} | ✅{ok} | ❌{fail}"); return
            if step == "wait_bc_photo":
                state["photo_url"] = event.text.strip()
                state["step"] = "wait_bc_photo_caption"; USER_STATES[uid] = state
                await event.reply("🖼️ Now caption:"); return
            if step == "wait_bc_photo_caption":
                text = event.text.strip(); url = state.get("photo_url"); del USER_STATES[uid]
                msg = await event.reply("📢 Broadcasting...")
                ok, fail, total = await broadcast_message(photo_url=url, text=text)
                await msg.edit(f"✅ Done\n{total} | ✅{ok} | ❌{fail}"); return
            if step == "wait_setfree":
                text = event.text.strip()
                if not text.isdigit():
                    await event.reply("❌ Number"); return
                cfg_set("free_count", int(text)); del USER_STATES[uid]
                await event.reply(f"✅ Free: {text}", buttons=kb_owner()); return
            if step == "wait_add_user_id":
                text = event.text.strip()
                if not text.lstrip("-").isdigit():
                    await event.reply("❌ Invalid ID"); return
                db_set_approval(int(text), "approved", approved_by=OWNER_ID)
                del USER_STATES[uid]
                await event.reply(f"✅ Granted `{text}`", buttons=kb_owner()); return
            if step == "user_set_limit":
                text = event.text.strip()
                if not text.isdigit():
                    await event.reply("❌ Number"); return
                db_set_user_limit(state.get("target"), int(text))
                del USER_STATES[uid]
                await event.reply("✅ Set", buttons=kb_user_manage(state.get("target"))); return
            if step == "user_add_balance":
                text = event.text.strip()
                if not text.lstrip("-").isdigit():
                    await event.reply("❌ Number"); return
                db_add_free_balance(state.get("target"), int(text))
                del USER_STATES[uid]
                await event.reply(f"✅ Added {text}", buttons=kb_user_manage(state.get("target"))); return

        if not await is_joined(uid):
            await event.reply("Join all channels first:", buttons=kb_join()); return
        if uid != OWNER_ID and not is_approved(uid):
            await event.reply("Need approval.", buttons=kb_request_access()); return
        if uid not in USER_STATES:
            await event.reply("Send /start.", buttons=kb_welcome(uid)); return

        state = USER_STATES[uid]; step = state.get("step")

        if step == "queue_wait_chat":
            state["q_chat"] = event.text.strip(); state["step"] = "queue_wait_post"
            USER_STATES[uid] = state
            await event.reply("✅ Chat saved. Send post link:", buttons=kb_back(uid)); return
        if step == "queue_wait_post":
            state["q_post"] = event.text.strip(); state["step"] = "queue_wait_count"
            USER_STATES[uid] = state
            limit = get_user_limit(uid)
            await event.reply(f"✅ Post saved.\n\nHow many? (max {limit}):", buttons=kb_reaction_count(uid)); return
        if step == "queue_wait_time":
            text = event.text.strip()
            try:
                if ":" in text and len(text.split(":")) == 2:
                    h, m = text.split(":")
                    target = datetime.now().replace(hour=int(h), minute=int(m), second=0, microsecond=0)
                    if target < datetime.now(): target += timedelta(days=1)
                else: target = datetime.now() + timedelta(minutes=int(text))
                state["q_time"] = target.strftime("%Y-%m-%d %H:%M:%S")
                qid = db_add_queue(uid, state.get("q_chat"), state.get("q_post"), state.get("reaction_count", 5), "default", None, state["q_time"])
                del USER_STATES[uid]
                await event.reply(f"✅ **JOB SCHEDULED**\n{DIV}\n\n⏰ Job #{qid}\n🕐 {target.strftime('%d %b %H:%M')}", buttons=kb_queue_menu(uid))
            except Exception as e:
                await event.reply(f"❌ Invalid: {str(e)[:60]}")
            return
        if step == "bulk_wait_chat":
            state["b_chat"] = event.text.strip(); state["step"] = "bulk_wait_posts"
            USER_STATES[uid] = state
            await event.reply("✅ Now send post links (one per line):", buttons=kb_back(uid)); return
        if step == "bulk_wait_posts":
            posts = [p.strip() for p in re.split(r"[,\n]+", event.text.strip()) if p.strip()]
            if not posts:
                await event.reply("❌ No valid posts"); return
            state["b_posts"] = posts; state["step"] = "bulk_wait_count"
            USER_STATES[uid] = state
            await event.reply(f"✅ {len(posts)} posts.\n\nReactions per post?:", buttons=kb_reaction_count(uid)); return
        if step == "bulk_wait_emoji_done":
            await _run_bulk(event, uid); return
        if step == "wait_payment_screenshot":
            plan = state.get("plan"); days = state.get("days"); method = state.get("method")
            price = get_plan_price(plan, days); text = event.text.strip()
            ss = "photo_uploaded" if (event.photo or event.document) else ("no_screenshot" if text.lower() == "skip" else text)
            pid = db_add_payment(uid, price, plan, days, method, ss)
            del USER_STATES[uid]
            await event.reply(
                f"✅ **PAYMENT SENT**\n{DIV}\n\n📦 {PLAN_NAMES[plan]}\n📅 {DURATIONS[days]}\n💰 **{price}rs**\n"
                f"🔢 ID: `{pid}`\n\n⏳ Owner will verify!",
                buttons=kb_welcome(uid))
            try:
                await bot.send_message(OWNER_ID, f"💳 **NEW PAYMENT**\n{DIV}\n\n👤 `{uid}`\n💰 {price}rs\n📦 {PLAN_NAMES[plan]}\n📱 {method}", buttons=kb_payment_actions(pid))
            except: pass
            return
        if step == "tpl_wait_name":
            state["tpl_name"] = event.text.strip()[:20]; state["step"] = "tpl_wait_emojis"
            USER_STATES[uid] = state
            await event.reply("✏️ Send emojis:"); return
        if step == "tpl_wait_emojis":
            emojis = [p.strip() for p in re.split(r"[,\s]+", event.text.strip()) if p.strip() in ALL_REACTIONS]
            if not emojis:
                await event.reply("❌ No valid emojis."); return
            db_add_template(uid, state.get("tpl_name", "Template"), emojis[:20])
            del USER_STATES[uid]
            await event.reply(f"✅ Template saved!", buttons=kb_templates_menu(uid)); return
        if step == "wait_channel":
            state["channel_link"] = event.text.strip(); state["step"] = "wait_post"
            USER_STATES[uid] = state
            await event.reply(f"✅ Chat saved.\n\n{L(uid, 'post_link')}:", buttons=kb_back(uid)); return
        if step == "wait_post":
            state["post_link"] = event.text.strip(); state["step"] = "wait_count"
            USER_STATES[uid] = state
            limit = get_user_limit(uid); vis = db_count_visible_bots()
            header = f"👑 OWNER — {vis} bots" if uid == OWNER_ID else f"🎁 {L(uid, 'your_limit')}: **{limit}**"
            await event.reply(f"✅ Post saved.\n\n{L(uid, 'how_many')}\n\n{header}", buttons=kb_reaction_count(uid)); return
        if step == "wait_custom_emoji":
            emojis = []
            for p in re.split(r"[,\s]+", event.text.strip()):
                p = p.strip()
                if p and p in ALL_REACTIONS and p not in emojis: emojis.append(p)
            if not emojis:
                await event.reply("❌ No valid emojis.", buttons=kb_back(uid)); return
            state["custom_emojis"] = emojis[:30]; state["emoji_mode"] = "custom"
            USER_STATES[uid] = state
            await event.reply("✨ Starting...")
            await _run_reactions(event, uid); return
        if step == "watch_wait_link":
            state["watch_link"] = event.text.strip()
            state["watch_chat_type"] = state.get("chat_type", "channel")
            state["step"] = "watch_wait_count"; USER_STATES[uid] = state
            await event.reply(f"✅ Link saved.\n\n{L(uid, 'count_per_post')} (1-50):", buttons=kb_back(uid)); return
        if step == "watch_wait_count":
            text = event.text.strip()
            if not text.isdigit():
                await event.reply("❌ Number"); return
            state["watch_count"] = min(int(text), 50); state["step"] = "watch_wait_emoji"
            USER_STATES[uid] = state
            await event.reply(f"✅ Count: {state['watch_count']}\n\n{L(uid, 'emoji_mode')}:",
                buttons=[[btn(f"🎯 {L(uid, 'default_emoji')}", data=b"watch_emoji:default", style="success")],
                         [btn(f"✏️ {L(uid, 'custom_emoji')}", data=b"watch_emoji:custom", style="primary")],
                         [btn(f"🔙 {L(uid, 'cancel')}", data=b"watch_flow", style="danger")]]); return
        if step == "watch_wait_custom_emoji":
            emojis = [p.strip() for p in re.split(r"[,\s]+", event.text.strip()) if p.strip() in ALL_REACTIONS]
            if not emojis:
                await event.reply("❌ No valid emojis."); return
            state["watch_custom_emojis"] = emojis[:30]; USER_STATES[uid] = state
            await _finalize_watch_add(event, uid); return
        if step == "watch_edit_count":
            text = event.text.strip()
            if not text.isdigit():
                await event.reply("❌ Number"); return
            wid = state.get("wid"); db_update_watcher(wid, reaction_count=min(int(text), 200))
            del USER_STATES[uid]
            await event.reply("✅ Updated!", buttons=[[btn(f"🔙 {L(uid, 'back')}", data=f"watch:manage:{wid}".encode(), style="primary")]]); return
        if step == "watch_edit_emoji":
            emojis = [p.strip() for p in re.split(r"[,\s]+", event.text.strip()) if p.strip() in ALL_REACTIONS]
            if not emojis:
                await event.reply("❌ No valid emojis."); return
            wid = state.get("wid")
            db_update_watcher(wid, emoji_mode="custom", custom_emojis=",".join(emojis[:30]))
            del USER_STATES[uid]
            await event.reply("✅ Updated!", buttons=[[btn(f"🔙 {L(uid, 'back')}", data=f"watch:manage:{wid}".encode(), style="primary")]]); return

    except Exception as e: D_err(e, "on_msg")


async def _run_bulk(event, uid):
    state = USER_STATES.get(uid, {})
    cl = state.get("b_chat"); posts = state.get("b_posts", [])
    count = state.get("reaction_count", 5); em = state.get("emoji_mode", "default")
    ce = state.get("custom_emojis")
    if not cl or not posts:
        await event.answer("❌ Missing data", alert=True); return
    jid = db_add_bulk_job(uid, "multi_post", len(posts), ",".join(posts[:50]))
    del USER_STATES[uid]
    await event.reply(f"📦 **BULK STARTED**\n{DIV}\n\n🆔 Job #{jid}\n📋 {len(posts)} posts\n\n✨ Processing...", buttons=kb_back(uid))
    ok_n = fail_n = 0
    for i, post in enumerate(posts, 1):
        try:
            r = await process_reactions_rotating(event, uid, cl, post, count, emoji_mode=em, custom_emojis=ce, is_auto_watch=True)
            if r and r > 0: ok_n += 1
            else: fail_n += 1
        except: fail_n += 1
        db_update_bulk_job(jid, completed=ok_n, failed=fail_n)
    db_update_bulk_job(jid, status="done")
    try:
        await event.reply(f"🎉 **BULK DONE**\n{DIV}\n\n✅ Success: **{ok_n}**\n❌ Failed: **{fail_n}**", buttons=kb_bulk_menu(uid))
    except: pass


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
                except: pass
                entity = await safe_get_entity(f"https://t.me/+{invite}", cache_key=f"chat:{invite}")
            else: entity = await safe_get_entity(chat_ref, cache_key=f"chat:{chat_ref}")
        except Exception as e:
            await event.reply(f"❌ Resolve failed: {str(e)[:80]}")
            if uid in USER_STATES: USER_STATES[uid] = {}
            return
        chat_id = entity.id; chat_title = getattr(entity, "title", "Unknown")
        for w in db_list_watchers(uid):
            if w[2] == chat_id:
                await event.reply(f"⚠️ Already watching **{chat_title}**")
                if uid in USER_STATES: USER_STATES[uid] = {}
                return
        try:
            msgs = await asyncio.wait_for(admin_client.get_messages(entity, limit=1), timeout=15)
            last = msgs[0].id if msgs else 0
        except: last = 0
        db_add_watcher(uid, chat_id, chat_title, link, cty, count, mode, custom, last)
        await event.reply(
            f"🎉 **WATCH ADDED** 🎉\n{STAR_LINE}\n\n📢 {chat_title}\n🎯 {count}/post\n✏️ {mode}\n📊 From: **#{last}**\n\n🟢 **ACTIVE!**",
            buttons=[[btn(f"📋 {L(uid, 'my_watches')}", data=b"watch:list", style="primary")],
                     [btn(f"🏠 {L(uid, 'home')}", data=b"home", style="success")]])
        if uid in USER_STATES: USER_STATES[uid] = {}
    except Exception as e: D_err(e, "_finalize_watch_add")


async def _run_reactions(event, uid):
    global TASK_RUNNING, TASK_OWNER_UID
    now = time.time(); last = USER_LAST_REQUEST.get(uid, 0)
    if now - last < USER_COOLDOWN:
        await event.answer(f"⏳ Wait {int(USER_COOLDOWN - (now - last))}s", alert=True); return
    if TASK_RUNNING:
        await safe_edit(event, f"⏳ **Please Wait**\n{DIV}\n\nAnother task running.", buttons=kb_back(uid))
        if uid in USER_STATES: USER_STATES[uid] = {}
        return
    state = USER_STATES.get(uid, {})
    cl = state.get("channel_link"); pl = state.get("post_link")
    count = state.get("reaction_count", 0); em = state.get("emoji_mode", "default")
    ce = state.get("custom_emojis")
    if not cl or not pl or count <= 0:
        await event.answer("❌ Missing data", alert=True); return
    USER_LAST_REQUEST[uid] = now
    u = db_get_user_full(uid); fb = u[17] if u and len(u) > 17 else 0
    limit = get_user_limit(uid)
    if fb > 0 and count > limit:
        extra = count - limit
        if db_spend_free_balance(uid, extra): D(f"Used {extra} free balance for {uid}", "ref")
    TASK_RUNNING = True; TASK_OWNER_UID = uid
    try:
        await process_reactions_rotating(event, uid, cl, pl, count, emoji_mode=em, custom_emojis=ce)
    except Exception as e:
        D_err(e, "_run_reactions")
        try: await safe_edit(event, f"❌ Error: {str(e)[:100]}", buttons=kb_back(uid))
        except: pass
    finally:
        TASK_RUNNING = False; TASK_OWNER_UID = None


# ═══ MAIN ═══
async def main():
    global admin_client, backup_client, TASK_RUNNING, TASK_OWNER_UID
    try:
        loop = asyncio.get_running_loop(); loop.set_exception_handler(global_exception_handler)
    except: pass
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
    D_sep("GHOST REACTION BOT — v60 FRIENDLY + ANIMATED")
    D(f"Owner: {me.first_name} (@{me.username})", "ok")
    D(f"Bots: {db_count_visible_bots()} / {db_count_bots()}", "ok")
    D(f"Colors: {'✅' if HAS_BUTTON_STYLE else '❌'}", "info")
    D(f"Backup: {'✅ Ready' if backup_client else '❌ None'}", "backup")
    D(f"DB: {DB_FILE}", "info")
    D(f"GitHub: {'✅ Enabled' if gh['enabled'] else '❌ Disabled'} ({gh['repo']})", "gh")
    D(f"Boot download: {gh['last_msg']}", "gh")
    D(f"Languages: {len(LANGUAGES)} langs", "lang")
    D("Bot online ✨", "ok")

    asyncio.create_task(watcher_loop())
    asyncio.create_task(pool_cleaner_loop())
    asyncio.create_task(health_check_loop())
    asyncio.create_task(queue_loop())
    asyncio.create_task(daily_summary_loop())

    try:
        await bot.start(bot_token=BOT_TOKEN)
        await bot.run_until_disconnected()
    finally:
        try:
            github_sync.upload_db(force=True)
            D("Final GitHub sync done", "gh")
        except: pass


if __name__ == "__main__":
    asyncio.run(main())