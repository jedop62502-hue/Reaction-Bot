"""
============================================================
   GHOST REACTION BOT v73 - DUAL SERVER EDITION
   Free Server + Paid Server (50/50 split)
   Owner Manual Override + Full Auto Dedupe
   Smart Batch + Fallback + Failed Bot Tracking
   Credit: @Anonymous_User_37
============================================================
"""
import os, sys, time, random, asyncio, re, hashlib, json
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

# ✅ GitHub sync OPTIONAL
try:
    import github_sync
    HAS_GH_SYNC = True
except ImportError:
    HAS_GH_SYNC = False
    class _DummyGH:
        LOCAL_DB_PATH = "ghost_users.db"
        def start_sync_thread(self): pass
        def mark_dirty(self): pass
        def is_enabled(self): return False
        def upload_db(self, force=False): return False, "disabled"
        def download_db(self): return False, "disabled"
        def get_stats(self):
            return {"uploads":0, "downloads":0, "errors":0, "last_sync":None}
    github_sync = _DummyGH()

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
BACKUP_SESSION_1 = ""
BOT_TOKEN = "8878162447:AAGMBnukLS2jPxfBthfeY1GAblCCrgtaH2M"

# ══════════════════════ BOT TOKENS (Master — auto-dedupe) ══════════════════════
# Purane + Naye — duplicates automatically skip ho jayenge
_RAW_BOT_TOKENS = [
    # ═══ PURANE TOKENS (script mein pehle se thay) ═══
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
    
    # ═══ NAYE TOKENS ═══
    "8836762962:AAEfykTc8xW-Qtg5Dj2sdyd8Pv32pdkTEG4",
    "8930953450:AAF4bV7rDvwkyttcwopbt6Cnz1hhDaBwiWs",
    "8872256184:AAFemPe7BzFsg639ZhGFsNEUG_z1IEPHrgs",
    "8873825851:AAEYomO1fiAIlZlXZ0yOFVVTeaAliyw-gOs",
    "8804566350:AAEPorEwqaceNY-COcLN_fxli3pzsl24tPg",
    "8616580968:AAG3aN3PZAE_8YHSSrVdmBRPtvRGb7-uEDo",
    "8694904909:AAFinqlEzBggfpt1PPiUXcmtLHdTY2goBI8",
    "8939598884:AAGOriST39ECwAeyGB0yh-iBuxxdXow-TdY",
    "8753880235:AAHrreP8AQ6xR6ahnB0OQsi87cjsNmqMzqU",
    "8933211188:AAHa_QQSU_d96sVZF8UFECChkxeS1d0Xf-Q",
    "8887882151:AAEXpjYyww2qkL_fqRbldKYdAWbPwp3Lc_Y",
    "8077072239:AAE7FkFKf0tuNhJQcy5u-CE9oB1l92-pvyA",
    "8861881121:AAFs3K3vRKV5cf2xFXf5g9Lli6V7fpSiXkQ",
    "8721434180:AAFVkXTPxCPBVqmLCCv6_tU38wUPhaAAB1M",
    "8855476829:AAGWnB-V7nwLh8qfLi2UWOjusw_P2g1sGzM",
    "8530191277:AAGTJ4vx6txnC1LrzvPjSHn0x_5lmJQxP7A",
    "8825634159:AAFvbmakQ033QgQoeLu7q7OHYSanjM5EgjQ",
    "8186488203:AAEqDlI4PFuANgdqVnkz5pdpmX6wr_34pVk",
    "8834429452:AAEZuOJsCxhvpLUWpetWVnRlXn3tKOzLDlA",
    "8735831279:AAH7Bo8waAf7UM5q8c6idSYT4mgnaniBaeo",
    "8691168768:AAG27i0Okpyfc-QldqKIzHhkw2zsdP3uVGM",
    "8808636199:AAFS4GGzGEeclyRijD4GJGSEmAGJhPvL4I8",
    "8629248468:AAEWztVHReYg7Ir5oZJG4bq1GGGhso-5nbs",
    "8399865674:AAFyEPmrC4XcMuQaXDteDirdo-esc3x1gxI",
    "8711973443:AAHs6k30d_WRPROKhvrZ9vhHif8Ag-KgEws",
    "8895517785:AAHqdkGIZvNzsoREfLDn4W0tsTsRKaRQlvM",
    "8904181880:AAGNsSp4Bpnkt68ZYrb01TYCMLVk3PTaB9c",
    "8659189400:AAHmW51YbEo3TFbImVFvbesUtVqVGTnDjEM",
    "8763339065:AAF1LPBYnMqsKa1JI00YusmQsqp4_3MhRbA",
    "8204077410:AAExKUju6XtVDJcGUmRqW42yAkQ93BsMhjY",
    "8846427241:AAFwE79DBGXuL4D2EDvVmZsIceeIIpgaBRM",
    "8811506527:AAGWuXZIa5jMwjxYd5fs_FYO12Y9ZWtqvJY",
    "8887094335:AAHq_wg4B63pNVynivs2W7YasZsOeGJ9dYA",
    "8759529429:AAHgMj0Fb_ErpMByyuv5q7z0ii4b-mt90mM",
    "8734725201:AAGAJSbWw-2bnmTa2dGmbu7HPBq4w2oNrKk",
    "8744370627:AAHQW-lvCCqShU_ZPBkF0uSYhErm9IWsoms",
    "8636321380:AAEfu54-Xyx-bgOE43GfYC9zXXqS0ibRNpo",
    "8842402547:AAHIuEQyNBf-MYfElZjEy9lB3U6Yxv8TOAY",
    "8968416580:AAF9UIacJE6jtM2zJ0CoUPcO2h5rZ0Hgwxk",
    "8983579841:AAEBNIqju4Mc9GYDM1ROmPdkoYNSYQerZY4",
    "8924470155:AAHStrtWxmnkb_jwHr9o_lDxkocGwaDxF9o",
    "8646190794:AAFxOuZoK1v-K6f9zpDzKiwX8ddYHKL3Fko",
    "8609362391:AAEIX8VEvRerRdYTM8VktjFMKB2e-AYQ1gE",
    "8947005664:AAHqaUFrFOmqmQORagE7TFap_fo3k1t_uRY",
    "8920181738:AAFWT6xF4wiPD2dal3vKLaWi4ByaXv-ql7M",
    "8840708072:AAGTVFU3-Xe5GwJIQcK1wjM5u5F_bpLjKvc",
    "8610161657:AAGM5BOGI9wdSRT6FSHB8WxX_cwrinGvsME",
    "8740955689:AAHb1uP5gbV0JIZma6Az0nKDKptTDCgelDo",
    "8748070601:AAExk7kUdceMo-pHKY9IjcDOxgG8C_H1gwA",
    "8861985796:AAFYWV5aohaFLWYuNYNUAgM1gJRM8-YcxQ4",
    "8629755223:AAHFqbp0zK4G69a8RJoGj9VtLqUpvdumeBU",
    "8799402761:AAGIJ5gHzKz3KKlqZTY8Zh_i9w0Lo23JKLE",
    "8713327772:AAGRiAqQgU5wUjsGbgVupI3b5M9R_io7dVw",
    "8989331034:AAHuD7Eznd9igKtu4lulVnha6jRA2CD7vE8",
    "8737257901:AAHcAkSy3OAuiGModYWUCSeGHU9qD5EAtsY",
    "8912082625:AAF4ky4WPlZcd0WKLDSzDvHPCorldWje33Y",
    "8605178514:AAFBKxv3w4tUsItdh8rlkB0zzQPOQicTv4g",
    "8929272267:AAHY-y1GYqWFuW-_TMgIWqpYWtn9jYgb38Q",
    "8952822895:AAH_D4snLgtdPWp9mdnkgdCmooT4ntkcwqA",
    "8614726892:AAE5oqaTuJXHh8SDaKz8CHQY4-2vSFoaEHI",
    "8861639970:AAEhu3fqxaTFy9GHXy6GSBXNKfaKZ2Yw2g4",
    "8815053623:AAEIcfw4h4Tbmvsn7u620xtdeQY0FsxFXVg",
    "8661258005:AAGpa4BxZdyuDaaPExjitcAzRUumsAQ7Oi4",
    "8662715303:AAEui_9v4xmdBCaLyKmJHufRlN0sYwsjwR8",
    "8543087654:AAGz_rQLHToB_cU2Wy1b7rLO1-mGH21qhhY",
    "8905733010:AAFC5W2ldfSrpEo0cgt6AmA8Mw6C_JO9KEk",
    "8542237475:AAFj8HxMhBVoMYL5rtIGtsdVmI2q2Uu8wyo",
    "8838675159:AAE_54l94SSJpgTS0BnvQDd-gS2sOsrFXGY",
    "8590777451:AAHITDVRlEQ0d1NP61Yw9xnznccWRisOdgc",
    "8867904690:AAHHDJcrVAcjYJdMVPuw8dX1oNYwLJPdLu4",
    "8838965715:AAG7Gz3KSoeKh56SRgO8OEt4Vvu5_8gJAoM",
    "8923909842:AAGKDbORwvFO0TWSaT-OynWWSrDLm1wNSIg",
    "8692228378:AAHS9XL-H1eGqlOtE66Hz9JIXV_aPXIodsU",
    "8804516017:AAHzSTmV53-7cQZdtKJhyNTK94-WdDfw0cU",
    "8719289135:AAEYFp_XYoqzlM201qVhmjhqXtNC6g348-w",
    "8926598293:AAHhG4uZcYymWzt_oeA1WHhwzLPsw4bvCCw",
    "8831931709:AAFPpQvO2xVcsNzCzkSQAXbvh4d7v37NgVE",
    "8810734398:AAFMWRfgY5Sv8dRalbEW0N9NkZfr3uWfzQE",
    "8884046718:AAEhmJzpOJXK_yHQONs37Izd74pnjc9E6_M",
    "8711404123:AAE_R6O1mQErDilOZnx0BplnMFMrgeFgTIo",
    "8759954245:AAEk7G1KIgGMyGo-D9ORBj_NHDw4x4INs-A",
    "8911817060:AAEorqqmHFJUPVHn4hW_3IlHYu3CxXsdSSI",
    "8787801515:AAH20DPUXvRoqcAhaX65vfUSNhnqUPV-9u8",
    "8267821853:AAGD0Yo7XW-nb2WsRdvfQade_HIQBi53StI",
    "8957963473:AAE0oAI40eFp_TvN6kzkV5pdK5y9qU9hRAE",
    "8907296618:AAFJtdNhp9cniBZpc7qdkeZDgNvLbiBvTG8",
    "8962194440:AAEj-NZ7DfJN_PPNAna_QeREJHROmEcI0nc",
    "8232718043:AAEv30sleBvpK-JXENfdA-5f1FhHC3Ijn1Y",
    "8833324855:AAF0kH9wYfX2-t0CONGn0kUOXh55t5TsPuE",
    "8641192792:AAEAUuAei4DOSuR6T8COTL511oiIMZtlYd0",
    "8945018413:AAESHzBg4UF_1i0DxMhux7no28aiQt6Ct74",
    "8888773608:AAGKUVaILpMiJT2GXhHkGXHcIGv5XQxHNUs",
    "8793899520:AAEXtPOveGYXWHm36o9M4XIhuDixO9RizvQ",
    "8870796074:AAHtu7jMDqux_4Abost4rfQbdBOegFGmWBU",
    "8341464481:AAErZ2SMQsRKFXlZ-BKNI_Ew3xr_9XkCrjw",
    "8357485885:AAHS_zBEp6318-E3p_h-6HNFQTd430yvSvs",
    "8917102545:AAHugV7a3IrI66sEqHTJIfU9SWs1U8XV_KY",
    "8604688837:AAHWNcf_Xjh8KpqAy9t0BkRX9tZMOB0uCdg",
    "8933271589:AAGBzf0ZzbooelPSsnnlU0D-h55aYNPbPnw",
    "8926464596:AAGeeKqK8ZDcy1lszofa4Y6Ht-qdW6Ay5yc",
    "8823851915:AAFc6cOnkeK-JYWVE4m6S5D-SAboffz76sM",
    "8943709444:AAE1tRJDj9bhEI6pIie3S8CcynvHdMkQAwY",
    "8918710712:AAGgWI4ivpjcZl3VUYgBIjTx3Jp0HIIuE50",
    "8589602805:AAFmPngJim8_esyKcCjjnjvsGTNol1hnVMc",
    "8976792733:AAGZ9s3VH1bTcnL8d6em2qsIdVXva01v0Vg",
    "8963392391:AAEu9EDeDW5Vl2OsQ4h1infcq-Jei5_Q6uI",
    "8842093299:AAGJp5P9CS0zXgyIRZTpY4C5uvG37NFAp4g",
    "8921757993:AAFDxmWZuNJ4_ZjFAQU3d7ye9zK2t4oWE10",
    "8306659351:AAFuqqKp4X72u486ItBS_HlBA8b4XCxjeuo",
    "8609649936:AAFcrdfMBr-sPmMCrUwyFWyU2J-EjbZBpeE",
    "8858513698:AAF4bsiRMEBOTUqfqMv2dHjVIW5sFKdy9w0",
    "8946299677:AAHMXk6WhVGQU7pj-XphIRwHpLdGmn9A4x0",
    "8985111289:AAG_RVtet6v_IWJ5A1eaE1l7UBO1OWoT3eY",
    "8764444463:AAGOWGjckzdoq2RDKyNifOFbU072HFtJVOk",
    "8897706807:AAEeJkWxFmZJtnm1PU22rHxcniOh6c72GM4",
    "8634253247:AAFRLlUXI0aHxxDuDWWGxcBxEB0aw_6AiTo",
    "8807284103:AAHvWfvjmmZk00S0PXREJbKDZN3y6cPKSM0",
    "8796889247:AAELgigk6c49GdPZz0iwXFyXuB78qGWaCug",
    "8940009825:AAFJFJZ6kUweO_srv5u5rhldO6TJybDtozQ",
]

# ✅ AUTO DEDUPE — Python set() order preserve karta hai (dict se)
def dedupe_tokens(token_list):
    seen = set()
    result = []
    for tok in token_list:
        tok = tok.strip()
        if not tok or tok in seen:
            continue
        seen.add(tok)
        result.append(tok)
    return result

BOT_TOKENS = dedupe_tokens(_RAW_BOT_TOKENS)
_DUPLICATES_SKIPPED = len(_RAW_BOT_TOKENS) - len(BOT_TOKENS)

print(f"[STARTUP] ✅ Bot tokens: {len(_RAW_BOT_TOKENS)} raw → "
      f"{len(BOT_TOKENS)} unique ({_DUPLICATES_SKIPPED} duplicates skipped)")

# ══════════════════════ SERVER SPLIT (50/50) ══════════════════════
def split_bots_servers(all_tokens):
    """
    Split bot tokens: half free server, half paid server.
    Returns (free_list, paid_list)
    """
    total = len(all_tokens)
    half = total // 2
    free_list = all_tokens[:half]
    paid_list = all_tokens[half:]
    return free_list, paid_list

FREE_SERVER_TOKENS, PAID_SERVER_TOKENS = split_bots_servers(BOT_TOKENS)

print(f"[STARTUP] 🆓 Free server bots: {len(FREE_SERVER_TOKENS)}")
print(f"[STARTUP] 💎 Paid server bots: {len(PAID_SERVER_TOKENS)}")
print(f"[STARTUP] 📊 Total: {len(BOT_TOKENS)}")

# ══════════════════════ OTHER CONFIG ══════════════════════
OWNER_USERNAME_DEFAULT = "Anonymous_User_37"
OWNER_ID_DEFAULT = 8762845215
FORCE_CHANNELS_DEFAULT = []

SESSIONS_DIR = os.getenv("SESSIONS_DIR", "sessions")
MAX_CLIENTS = int(os.getenv("MAX_CLIENTS", "15"))
CACHE_MAX = int(os.getenv("CACHE_MAX", "500"))
RETRY_FAILED_INTERVAL = 300
REAL_CLIENTS = {}
REAL_CLIENT_LOCK = asyncio.Lock()
REAL_FLOOD_UNTIL = {}
REAL_COOLDOWN = 1.2

if HAS_GH_SYNC:
    try:
        github_sync.start_sync_thread()
    except Exception:
        pass

DB_FILE = (
    github_sync.LOCAL_DB_PATH
    if HAS_GH_SYNC and github_sync.is_enabled()
    else ("/app/data/ghost_users.db"
          if os.path.isdir("/app/data")
          else "ghost_users.db")
)

# ══════════════════════ REACTIONS ══════════════════════
DEFAULT_REACTIONS = ["❤️", "👍", "🔥"]
FALLBACK_REACTIONS = ["❤️", "👍", "🔥", "🥰", "🎉", "💯", "😍", "👏"]

ALL_REACTIONS = [
    "❤️","🔥","🥰","😍","👍","😇","👀","😎","💯","🎉","🤩","🥳","😁","😂",
    "🤣","😊","🙏","👏","💪","⚡","🌚","🌭","🍾","💋","🖕","😈","🤝","🎃",
    "👻","🤡","🤔","🤨","😐","😑","😶","🙄","😏","😣","😥","😮","🤐","😯",
    "😪","😫","🥱","😴","😌","😛","😜","🤪"
]

# ══════════════════════ LIMITS ══════════════════════
DEFAULT_FREE_COUNT = 5
MAX_REACTIONS = 200
BROADCAST_DELAY = 1.5
FLOOD_SAFETY = 3
PER_BOT_TIMEOUT = 25
PERMANENT_ADMIN_BOTS = {"RN_OTP1_bot", "RN_REACTION_BOT"}
WATCHER_CHECK_INTERVAL = 300
QUEUE_CHECK_INTERVAL = 60
AUTO_WATCH_ENABLED = True
BOT_BUSY_TIMEOUT = 2
POOL_CLEANUP_INTERVAL = 30
USER_COOLDOWN = 15

# ── Smart batch config ──
TELEGRAM_ADMIN_LIMIT = 50
BATCH_SIZE = 45
MAX_CYCLES = 50
MAX_FAILED_BATCHES = 5
FALLBACK_ENABLED = True
FAILED_BOT_RETRY = True

# ══════════════════════ PLANS ══════════════════════
PLAN_LIMITS = {"free":5, "basic":20, "pro":50, "premium":200}
PLAN_NAMES = {
    "free":"🆓 Free","basic":"🥉 Basic","pro":"🥈 Pro","premium":"🥇 Premium"
}
DURATIONS = {1:"1 Day", 7:"7 Days", 15:"15 Days", 30:"30 Days"}
PAID_PLANS = {"basic", "pro", "premium"}
DEFAULT_PRICES = {
    "basic":   {1:70,  7:250,  15:500,  30:900},
    "pro":     {1:120, 7:400,  15:800,  30:1400},
    "premium": {1:200, 7:700,  15:1400, 30:2500}
}

# ── Server assignment ──
# Free plan users → free server
# Basic + Pro + Premium + Owner → paid server
SERVER_FREE_PLANS = {"free"}
SERVER_PAID_PLANS = {"basic", "pro", "premium"}

LANGUAGES = {
    "en":"🇬🇧 English", "ur":"🇵🇰 اردو", "hi":"🇮🇳 हिन्दी",
    "ar":"🇸🇦 العربية", "ru":"🇷🇺 Русский", "es":"🇪🇸 Español",
    "id":"🇮🇩 Indonesia"
}
REFERRAL_REWARD = 5
FRIEND_VALID_REWARD = 10
EMOJI_PACKS = {
    "love":  ["❤️","😍","🥰","💋","😘"],
    "fire":  ["🔥","💯","⚡","🌟","✨"],
    "funny": ["😂","🤣","😁","😅","🤡"],
    "cool":  ["😎","👀","🙌","💪","🤝"],
    "party": ["🎉","🥳","🎊","🎈","🎁"]
}

# ══════════════════════ GLOBAL STATE ══════════════════════
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
bot = TelegramClient("ghost_reaction_bot", API_ID, API_HASH)
USER_STATES = {}
FAILED_BOTS_TRACKER = {}

# ── Server pools (separate!) ──
FREE_POOL = {}
PAID_POOL = {}
FREE_FLOOD_UNTIL = {}
PAID_FLOOD_UNTIL = {}


def _dirty():
    try:
        if HAS_GH_SYNC:
            github_sync.mark_dirty()
    except Exception:
        pass


def global_exception_handler(loop, context):
    exc = context.get("exception")
    if not exc:
        return
    err_name = type(exc).__name__
    if err_name in ("QueryIdInvalidError",):
        return
    if "query ID is invalid" in str(exc):
        return
    print(f"\n{'─'*60}\n⚠️ GLOBAL: {exc}", flush=True)
    traceback.print_exception(type(exc), exc, exc.__traceback__)
    print(f"{'─'*60}\n", flush=True)


DIV = "━━━━━━━━━━━━━━━━━━━━━━━━━"
STAR_LINE = "✦ ─────────── ✦ ─────────── ✦"
SPARKLE = "✨"


def progress_bar(cur, total, width=12):
    if total <= 0:
        return "░" * width
    f = min(int((cur / total) * width), width)
    return "█" * f + "░" * (width - f)


def D(msg, level="info"):
    ts = datetime.now().strftime("%H:%M:%S")
    ic = {
        "info":"ℹ️ ","ok":"✅","fail":"❌","warn":"⚠️ ","step":"▶️ ","dbg":"🐛",
        "flood":"🌊","rot":"🔄","cycle":"🔁","watch":"📡","ref":"🎁",
        "plan":"💰","lang":"🌍","backup":"🛡️","paid":"💎","pool":"🎯",
        "health":"❤️","queue":"⏰","pay":"💳","team":"👥","bulk":"📦",
        "gh":"🔄","real":"👤","anim":"🎬","store":"🏪","smart":"🧠",
        "fallback":"🩹","batch":"📦","free":"🆓","server":"🖥️"
    }
    print(f"[{ts}] {ic.get(level,'•')} {msg}", flush=True)


def D_sep(t):
    print(f"\n{'='*60}\n  {t}\n{'='*60}", flush=True)


def D_err(e, ctx=""):
    print(f"\n{'─'*60}\n❌ {ctx}: {e}", flush=True)
    traceback.print_exc()
    print(f"{'─'*60}\n", flush=True)


def get_owner_username():
    return cfg_get("owner_username", OWNER_USERNAME_DEFAULT)


def get_owner_id():
    try:
        return int(cfg_get("owner_id", str(OWNER_ID_DEFAULT)))
    except Exception:
        return OWNER_ID_DEFAULT


def OWNER_IS(uid):
    return uid == get_owner_id()


def get_today_str():
    return datetime.now().strftime("%Y-%m-%d")


def get_week_start_str():
    now = datetime.now()
    monday = now - timedelta(days=now.weekday())
    return monday.strftime("%Y-%m-%d")


# ══════════════════════ END OF PART 1 ══════════════════════
D("✅ Part 1 loaded — Config + Bots + Server Split (50/50)", "ok")
# ══════════════════════ DATABASE — PART 1 ══════════════════════
def db_init():
    """Initialize database with ALL tables (Part 1 + 2 + 3 combined)"""
    if "/" in DB_FILE:
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # ═══════════════════════════════════════════════════════
    # ═════ PART 1 TABLES ═════
    # ═══════════════════════════════════════════════════════

    # ── Users ──
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, first_name TEXT, username TEXT,
        joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_active TEXT DEFAULT CURRENT_TIMESTAMP,
        is_banned INTEGER DEFAULT 0, total_reactions INTEGER DEFAULT 0,
        total_bots INTEGER DEFAULT 0, custom_limit INTEGER DEFAULT 0,
        auto_watch_unlocked INTEGER DEFAULT 0,
        allow_channel INTEGER DEFAULT 1, allow_group INTEGER DEFAULT 1,
        allow_manual INTEGER DEFAULT 1, allow_autowatch INTEGER DEFAULT 0,
        allow_custom_emoji INTEGER DEFAULT 1,
        plan TEXT DEFAULT 'free', plan_expires TEXT,
        free_balance INTEGER DEFAULT 0, language TEXT DEFAULT 'en',
        referral_code TEXT, referred_by INTEGER DEFAULT 0,
        referral_count INTEGER DEFAULT 0, referral_earned INTEGER DEFAULT 0,
        team_role TEXT DEFAULT 'user', team_commission INTEGER DEFAULT 0,
        total_spent INTEGER DEFAULT 0,
        ra_limit_override INTEGER DEFAULT -1,
        server_override TEXT DEFAULT NULL)""")

    # ── Reactions log ──
    c.execute("""CREATE TABLE IF NOT EXISTS reactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
        chat_title TEXT, chat_id INTEGER, post_link TEXT, post_id INTEGER,
        emoji TEXT, bot_username TEXT, status TEXT,
        method TEXT DEFAULT 'bot',
        server TEXT DEFAULT 'free',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    # ── Approvals ──
    c.execute("""CREATE TABLE IF NOT EXISTS approvals (
        user_id INTEGER PRIMARY KEY, first_name TEXT, username TEXT,
        status TEXT DEFAULT 'pending',
        requested_at TEXT DEFAULT CURRENT_TIMESTAMP,
        decided_at TEXT, approved_by INTEGER)""")

    # ── Config ──
    c.execute("""CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY, value TEXT)""")

    # ── Bots (main pool) ──
    c.execute("""CREATE TABLE IF NOT EXISTS bots (
        token TEXT PRIMARY KEY, username TEXT, bot_id INTEGER,
        server TEXT DEFAULT 'free',
        added_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    # ── Bot Servers (management table) ──
    c.execute("""CREATE TABLE IF NOT EXISTS bot_servers (
        token TEXT PRIMARY KEY, username TEXT,
        server TEXT DEFAULT 'free',
        priority INTEGER DEFAULT 100,
        is_active INTEGER DEFAULT 1,
        moved_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    # ═══════════════════════════════════════════════════════
    # ═════ PART 2 TABLES ═════
    # ═══════════════════════════════════════════════════════

    # ── Watchers ──
    c.execute("""CREATE TABLE IF NOT EXISTS watchers (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
        chat_id INTEGER, chat_title TEXT, chat_link TEXT,
        chat_type TEXT, reaction_count INTEGER DEFAULT 5,
        emoji_mode TEXT DEFAULT 'default', custom_emojis TEXT,
        last_post_id INTEGER DEFAULT 0, is_active INTEGER DEFAULT 1,
        server TEXT DEFAULT 'free',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP, last_run TEXT)""")

    # ── Templates ──
    c.execute("""CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
        name TEXT, emojis TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    # ── Referrals ──
    c.execute("""CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER, new_user_id INTEGER,
        status TEXT DEFAULT 'pending', reward_given INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        validated_at TEXT)""")

    # ── Notifications ──
    c.execute("""CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
        message TEXT, is_read INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    # ═══════════════════════════════════════════════════════
    # ═════ PART 3 TABLES ═════
    # ═══════════════════════════════════════════════════════

    # ── Queue ──
    c.execute("""CREATE TABLE IF NOT EXISTS queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
        chat_link TEXT, post_link TEXT, reaction_count INTEGER,
        emoji_mode TEXT DEFAULT 'default', custom_emojis TEXT,
        scheduled_time TEXT, status TEXT DEFAULT 'pending',
        server TEXT DEFAULT 'free',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        executed_at TEXT, error TEXT)""")

    # ── Bulk jobs ──
    c.execute("""CREATE TABLE IF NOT EXISTS bulk_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
        job_type TEXT, total INTEGER DEFAULT 0,
        completed INTEGER DEFAULT 0, failed INTEGER DEFAULT 0,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP, data TEXT)""")

    # ── Payments ──
    c.execute("""CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
        amount INTEGER, plan TEXT, days INTEGER, method TEXT,
        screenshot TEXT, status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        verified_at TEXT, verified_by INTEGER, notes TEXT)""")

    # ── Force channels ──
    c.execute("""CREATE TABLE IF NOT EXISTS force_channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT, channel TEXT UNIQUE,
        url TEXT, name TEXT, active INTEGER DEFAULT 1,
        added_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    # ── Team members ──
    c.execute("""CREATE TABLE IF NOT EXISTS team_members (
        user_id INTEGER PRIMARY KEY, role TEXT DEFAULT 'user',
        permissions TEXT, commission_percent INTEGER DEFAULT 0,
        total_sales INTEGER DEFAULT 0,
        total_commission INTEGER DEFAULT 0,
        added_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    # ── Custom packs ──
    c.execute("""CREATE TABLE IF NOT EXISTS custom_packs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT,
        emojis TEXT, price INTEGER DEFAULT 0,
        is_paid INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    # ── User stats ──
    c.execute("""CREATE TABLE IF NOT EXISTS user_stats (
        user_id INTEGER PRIMARY KEY, total_sent INTEGER DEFAULT 0,
        today_sent INTEGER DEFAULT 0, today_date TEXT,
        week_sent INTEGER DEFAULT 0, week_start TEXT,
        success_count INTEGER DEFAULT 0, fail_count INTEGER DEFAULT 0,
        streak_days INTEGER DEFAULT 0, last_bonus_date TEXT,
        trust_score INTEGER DEFAULT 100,
        last_active TEXT DEFAULT CURRENT_TIMESTAMP)""")

    # ── Daily bonus ──
    c.execute("""CREATE TABLE IF NOT EXISTS daily_bonus (
        user_id INTEGER, bonus_date TEXT, amount INTEGER DEFAULT 0,
        streak_day INTEGER DEFAULT 1,
        PRIMARY KEY(user_id, bonus_date))""")

    # ── Coupons ──
    c.execute("""CREATE TABLE IF NOT EXISTS coupons (
        id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE,
        discount_percent INTEGER DEFAULT 0,
        discount_flat INTEGER DEFAULT 0,
        max_uses INTEGER DEFAULT 0, used_count INTEGER DEFAULT 0,
        expires_at TEXT, active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    # ── Coupon uses ──
    c.execute("""CREATE TABLE IF NOT EXISTS coupon_uses (
        id INTEGER PRIMARY KEY AUTOINCREMENT, coupon_id INTEGER,
        user_id INTEGER,
        used_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    # ── Retry queue ──
    c.execute("""CREATE TABLE IF NOT EXISTS retry_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
        chat_link TEXT, post_link TEXT, count INTEGER,
        emoji_mode TEXT DEFAULT 'default', custom_emojis TEXT,
        attempts INTEGER DEFAULT 0, max_attempts INTEGER DEFAULT 3,
        next_retry TEXT, last_error TEXT,
        status TEXT DEFAULT 'pending',
        server TEXT DEFAULT 'free',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    # ── Emoji store (🔴 YEH PEHLE MISSING THA) ──
    c.execute("""CREATE TABLE IF NOT EXISTS emoji_store (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT,
        emojis TEXT, price INTEGER DEFAULT 0,
        description TEXT, is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    # ── User store buys ──
    c.execute("""CREATE TABLE IF NOT EXISTS user_store_buys (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
        pack_id INTEGER, paid_amount INTEGER,
        bought_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    # ── Post analytics ──
    c.execute("""CREATE TABLE IF NOT EXISTS post_analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
        chat_id INTEGER, post_id INTEGER, chat_title TEXT,
        sent_count INTEGER DEFAULT 0,
        requested_count INTEGER DEFAULT 0,
        server TEXT DEFAULT 'free',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    # ── Teams ──
    c.execute("""CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER,
        name TEXT, commission_percent INTEGER DEFAULT 10,
        active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    # ── Team clients ──
    c.execute("""CREATE TABLE IF NOT EXISTS team_clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT, team_id INTEGER,
        reseller_id INTEGER, client_id INTEGER,
        plan TEXT, expires_at TEXT,
        commission_paid INTEGER DEFAULT 0,
        added_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

    # ══════════════════════ SQLITE OPTIMIZATIONS ══════════════════════
    try:
        c.execute("PRAGMA journal_mode=WAL")
        c.execute("PRAGMA synchronous=NORMAL")
        c.execute("PRAGMA cache_size=2000")
        c.execute("PRAGMA temp_store=MEMORY")
    except Exception:
        pass

    # ── Indices ──
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_reactions_user ON reactions(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_reactions_date ON reactions(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_reactions_status ON reactions(status)",
        "CREATE INDEX IF NOT EXISTS idx_reactions_server ON reactions(server)",
        "CREATE INDEX IF NOT EXISTS idx_users_plan ON users(plan)",
        "CREATE INDEX IF NOT EXISTS idx_approvals_status ON approvals(status)",
        "CREATE INDEX IF NOT EXISTS idx_queue_status ON queue(status, scheduled_time)",
        "CREATE INDEX IF NOT EXISTS idx_watchers_active ON watchers(is_active)",
        "CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, is_read)",
        "CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)",
        "CREATE INDEX IF NOT EXISTS idx_retry_status ON retry_queue(status, next_retry)",
        "CREATE INDEX IF NOT EXISTS idx_store_active ON emoji_store(is_active)",
        "CREATE INDEX IF NOT EXISTS idx_coupons_code ON coupons(code)",
        "CREATE INDEX IF NOT EXISTS idx_stats_today ON user_stats(today_date)",
        "CREATE INDEX IF NOT EXISTS idx_bots_server ON bots(server)",
    ]
    for sql in indices:
        try:
            c.execute(sql)
        except Exception:
            pass

    # ══════════════════════ CONFIG DEFAULTS ══════════════════════
    cfg_defaults = [
        ("owner_username", OWNER_USERNAME_DEFAULT),
        ("owner_id", str(OWNER_ID_DEFAULT)),
        ("free_count", str(DEFAULT_FREE_COUNT)),
        ("auto_approve", "1"),
        ("channel_enabled", "1"), ("group_enabled", "1"),
        ("manual_enabled", "1"), ("autowatch_enabled", "1"),
        ("custom_emoji_enabled", "1"), ("force_join_enabled", "0"),
        ("paid_plans_enabled", "1"), ("referral_enabled", "1"),
        ("multi_lang_enabled", "1"), ("templates_enabled", "1"),
        ("notifications_enabled", "1"),
        ("paid_autowatch", "1"), ("paid_custom_emoji", "1"),
        ("paid_templates", "1"), ("paid_multilang", "0"),
        ("paid_referral", "0"), ("paid_balance", "1"),
        ("paid_channel", "0"), ("paid_group", "0"), ("paid_manual", "0"),
        ("queue_enabled", "1"), ("bulk_enabled", "1"),
        ("auto_payment_enabled", "0"),
        ("daily_summary_enabled", "1"), ("daily_summary_time", "21:00"),
        ("team_enabled", "1"), ("sales_commission_percent", "10"),
        ("realaccounts_enabled", "1"), ("paid_realaccounts", "1"),
        ("plan_realaccounts_free", "0"),
        ("plan_realaccounts_basic", "1"),
        ("plan_realaccounts_pro", "1"),
        ("plan_realaccounts_premium", "1"),
        ("plan_ra_limit_free", "0"), ("plan_ra_limit_basic", "3"),
        ("plan_ra_limit_pro", "8"), ("plan_ra_limit_premium", "20"),
        ("daily_bonus_enabled", "1"), ("daily_bonus_amount", "1"),
        ("streak_bonus_amount", "5"),
        ("auto_retry_enabled", "1"), ("auto_retry_max", "3"),
        ("smart_notif_enabled", "1"), ("coupon_enabled", "1"),
        ("emoji_store_enabled", "1"), ("post_analytics_enabled", "1"),
        ("team_reseller_enabled", "1"), ("upsell_enabled", "1"),
        ("smart_reaction_enabled", "1"), ("fallback_enabled", "1"),
        ("dual_server_enabled", "1"),
    ]
    for plan, prices in DEFAULT_PRICES.items():
        for days, price in prices.items():
            cfg_defaults.append((f"price_{plan}_{days}", str(price)))

    for k, v in cfg_defaults:
        c.execute("INSERT OR IGNORE INTO config(key, value) VALUES(?, ?)",
                  (k, v))

    # ══════════════════════ MIGRATION COLUMNS ══════════════════════
    for col, dflt in [
        ("is_banned","INTEGER DEFAULT 0"),
        ("total_reactions","INTEGER DEFAULT 0"),
        ("total_bots","INTEGER DEFAULT 0"),
        ("custom_limit","INTEGER DEFAULT 0"),
        ("auto_watch_unlocked","INTEGER DEFAULT 0"),
        ("allow_channel","INTEGER DEFAULT 1"),
        ("allow_group","INTEGER DEFAULT 1"),
        ("allow_manual","INTEGER DEFAULT 1"),
        ("allow_autowatch","INTEGER DEFAULT 0"),
        ("allow_custom_emoji","INTEGER DEFAULT 1"),
        ("plan","TEXT DEFAULT 'free'"), ("plan_expires","TEXT"),
        ("free_balance","INTEGER DEFAULT 0"),
        ("language","TEXT DEFAULT 'en'"), ("referral_code","TEXT"),
        ("referred_by","INTEGER DEFAULT 0"),
        ("referral_count","INTEGER DEFAULT 0"),
        ("referral_earned","INTEGER DEFAULT 0"),
        ("team_role","TEXT DEFAULT 'user'"),
        ("team_commission","INTEGER DEFAULT 0"),
        ("total_spent","INTEGER DEFAULT 0"),
        ("ra_limit_override","INTEGER DEFAULT -1"),
        ("server_override","TEXT DEFAULT NULL"),
    ]:
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {col} {dflt}")
        except sqlite3.OperationalError:
            pass

    # Reactions migration
    for col, dflt in [("server","TEXT DEFAULT 'free'"),
                      ("method","TEXT DEFAULT 'bot'")]:
        try:
            c.execute(f"ALTER TABLE reactions ADD COLUMN {col} {dflt}")
        except sqlite3.OperationalError:
            pass

    # Bots migration
    try:
        c.execute("ALTER TABLE bots ADD COLUMN server TEXT DEFAULT 'free'")
    except sqlite3.OperationalError:
        pass

    # Queue migration
    for col, dflt in [("server","TEXT DEFAULT 'free'")]:
        try:
            c.execute(f"ALTER TABLE queue ADD COLUMN {col} {dflt}")
        except sqlite3.OperationalError:
            pass

    # Watchers migration
    try:
        c.execute("ALTER TABLE watchers ADD COLUMN server TEXT DEFAULT 'free'")
    except sqlite3.OperationalError:
        pass

    # Retry migration
    try:
        c.execute("ALTER TABLE retry_queue ADD COLUMN server TEXT DEFAULT 'free'")
    except sqlite3.OperationalError:
        pass

    # Post analytics migration
    try:
        c.execute("ALTER TABLE post_analytics ADD COLUMN server TEXT DEFAULT 'free'")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()
    _dirty()
    D(f"DB initialized: {DB_FILE}", "ok")


# ══════════════════════ CONFIG HELPERS ══════════════════════
def cfg_get(k, d=None):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            r = conn.execute("SELECT value FROM config WHERE key=?",
                             (k,)).fetchone()
            return r[0] if r else d
        finally:
            conn.close()
    except Exception:
        return d


def cfg_set(k, v):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            conn.execute("INSERT OR REPLACE INTO config(key, value) VALUES(?, ?)",
                         (k, str(v)))
            conn.commit()
        finally:
            conn.close()
        _dirty()
    except Exception as e:
        D(f"cfg_set error: {str(e)[:60]}", "warn")


def cfg_bool(k, d=True):
    return cfg_get(k, "1" if d else "0") == "1"


def cfg_toggle(k):
    n = not cfg_bool(k)
    cfg_set(k, "1" if n else "0")
    return n


def get_plan_price(plan, days):
    try:
        return int(cfg_get(f"price_{plan}_{days}", "0"))
    except Exception:
        return 0


# ══════════════════════ FEATURE FLAGS ══════════════════════
def feat_channel():        return cfg_bool("channel_enabled")
def feat_group():          return cfg_bool("group_enabled")
def feat_manual():         return cfg_bool("manual_enabled")
def feat_autowatch():      return cfg_bool("autowatch_enabled")
def feat_custom_emoji():   return cfg_bool("custom_emoji_enabled")
def feat_force_join():     return cfg_bool("force_join_enabled")
def feat_plans():          return cfg_bool("paid_plans_enabled")
def feat_referral():       return cfg_bool("referral_enabled")
def feat_multilang():      return cfg_bool("multi_lang_enabled")
def feat_templates():      return cfg_bool("templates_enabled")
def feat_notifications():  return cfg_bool("notifications_enabled")
def feat_queue():          return cfg_bool("queue_enabled")
def feat_bulk():           return cfg_bool("bulk_enabled")
def feat_payment():        return cfg_bool("auto_payment_enabled")
def feat_daily_summary():  return cfg_bool("daily_summary_enabled")
def feat_team():           return cfg_bool("team_enabled")
def feat_realaccounts():   return cfg_bool("realaccounts_enabled")
def feat_daily_bonus():    return cfg_bool("daily_bonus_enabled")
def feat_auto_retry():     return cfg_bool("auto_retry_enabled")
def feat_smart_notif():    return cfg_bool("smart_notif_enabled")
def feat_coupon():         return cfg_bool("coupon_enabled")
def feat_store():          return cfg_bool("emoji_store_enabled")
def feat_post_analytics(): return cfg_bool("post_analytics_enabled")
def feat_team_reseller():  return cfg_bool("team_reseller_enabled")
def feat_upsell():         return cfg_bool("upsell_enabled")
def feat_smart_reaction(): return cfg_bool("smart_reaction_enabled")
def feat_fallback():       return cfg_bool("fallback_enabled")
def feat_dual_server():    return cfg_bool("dual_server_enabled")


def is_paid_feature(f):
    return cfg_bool(f"paid_{f}", False)


def plan_has_realaccounts(plan):
    return cfg_bool(f"plan_realaccounts_{plan}", False)


def plan_ra_limit(plan):
    try:
        return int(cfg_get(f"plan_ra_limit_{plan}", "0"))
    except Exception:
        return 0


# ══════════════════════ USER LIMITS & SERVER ══════════════════════
def get_user_ra_limit(uid):
    if OWNER_IS(uid):
        return 999, "owner"
    u = db_get_user_full(uid)
    if not u:
        return 0, "none"
    try:
        override = u[26] if len(u) > 26 else -1
    except Exception:
        override = -1
    if override is not None and int(override) >= 0:
        return int(override), "custom"
    plan = u[15] or "free"
    if plan in PAID_PLANS:
        exp = u[16] if len(u) > 16 else None
        if exp:
            try:
                if datetime.strptime(exp, "%Y-%m-%d %H:%M:%S") < datetime.now():
                    plan = "free"
            except Exception:
                pass
    return plan_ra_limit(plan), "plan"


def user_has_realaccounts(uid):
    if OWNER_IS(uid):
        return True
    if not feat_realaccounts():
        return False
    limit, _ = get_user_ra_limit(uid)
    return limit > 0


def set_user_ra_limit(uid, limit):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("UPDATE users SET ra_limit_override=? WHERE user_id=?",
                     (int(limit), uid))
        conn.commit()
    finally:
        conn.close()
    _dirty()


def user_has_paid_access(uid):
    if OWNER_IS(uid):
        return True
    u = db_get_user_full(uid)
    if not u or len(u) < 16:
        return False
    plan = u[15] or "free"
    if plan not in PAID_PLANS:
        return False
    exp = u[16] if len(u) > 16 else None
    if exp:
        try:
            if datetime.strptime(exp, "%Y-%m-%d %H:%M:%S") < datetime.now():
                return False
        except Exception:
            pass
    return True


def can_use_feature(uid, f):
    if OWNER_IS(uid):
        return True
    if not is_paid_feature(f):
        return True
    return user_has_paid_access(uid)


def get_free_count():
    try:
        return int(cfg_get("free_count", DEFAULT_FREE_COUNT))
    except Exception:
        return DEFAULT_FREE_COUNT


def is_auto_approve():
    return cfg_get("auto_approve", "1") == "1"


def set_auto_approve(v):
    cfg_set("auto_approve", "1" if v else "0")


def gen_referral_code(uid):
    return f"REF{uid}{random.randint(1000, 9999)}"


def get_user_limit(uid):
    if OWNER_IS(uid):
        return MAX_REACTIONS
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("""SELECT custom_limit, plan, plan_expires
            FROM users WHERE user_id=?""", (uid,)).fetchone()
    finally:
        conn.close()
    if not r:
        return get_free_count()
    cl, plan, pe = r
    if cl and cl > 0:
        return cl
    if plan and plan in PLAN_LIMITS:
        if pe:
            try:
                if datetime.strptime(pe, "%Y-%m-%d %H:%M:%S") < datetime.now():
                    return get_free_count()
            except Exception:
                pass
        return PLAN_LIMITS[plan]
    return get_free_count()


# ══════════════════════ SERVER ASSIGNMENT ══════════════════════
def get_user_server(uid):
    """
    Determine which server a user should use.
    Returns: 'free' or 'paid'
    """
    if OWNER_IS(uid):
        return "paid"
    u = db_get_user_full(uid)
    if not u:
        return "free"
    # Check manual override first
    try:
        override = u[27] if len(u) > 27 else None
    except Exception:
        override = None
    if override in ("free", "paid"):
        return override
    # Determine from plan
    plan = u[15] or "free"
    if plan in PAID_PLANS:
        exp = u[16] if len(u) > 16 else None
        if exp:
            try:
                if datetime.strptime(exp, "%Y-%m-%d %H:%M:%S") < datetime.now():
                    return "free"
            except Exception:
                pass
        return "paid"
    return "free"


def set_user_server_override(uid, server):
    """Set manual server override. server='free'/'paid'/None"""
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("UPDATE users SET server_override=? WHERE user_id=?",
                     (server, uid))
        conn.commit()
    finally:
        conn.close()
    _dirty()


def get_server_tokens(server):
    """Get list of tokens for a server"""
    if server == "paid":
        return PAID_SERVER_TOKENS
    return FREE_SERVER_TOKENS


def get_server_label(server):
    if server == "paid":
        return "💎 PAID"
    return "🆓 FREE"


# ══════════════════════ DB — USERS ══════════════════════
def db_get_user_full(uid):
    if uid is None:
        return None
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, first_name, username,
            joined_at, last_active, is_banned, total_reactions, total_bots,
            custom_limit, auto_watch_unlocked, allow_channel, allow_group,
            allow_manual, allow_autowatch, allow_custom_emoji, plan,
            plan_expires, free_balance, language, referral_code, referred_by,
            referral_count, referral_earned, team_role, team_commission,
            total_spent, ra_limit_override, server_override
            FROM users WHERE user_id=?""", (uid,)).fetchone()
    finally:
        conn.close()


def db_get_user(uid):
    if uid is None:
        return None
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, first_name, username,
            joined_at, last_active, is_banned, total_reactions,
            total_bots, custom_limit FROM users WHERE user_id=?""",
            (uid,)).fetchone()
    finally:
        conn.close()


def db_save_user(uid, first_name, username=None, referred_by=0):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        ex = c.execute("SELECT referral_code FROM users WHERE user_id=?",
                       (uid,)).fetchone()
        rc = gen_referral_code(uid)
        if ex is None:
            c.execute("""INSERT INTO users (user_id, first_name, username,
                last_active, referral_code, referred_by)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?)""",
                (uid, first_name, username, rc, referred_by))
        else:
            c.execute("""UPDATE users SET first_name=?, username=?,
                last_active=CURRENT_TIMESTAMP WHERE user_id=?""",
                (first_name, username, uid))
        c.execute("INSERT OR IGNORE INTO user_stats(user_id) VALUES(?)",
                  (uid,))
        conn.commit()
    finally:
        conn.close()
    _dirty()


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
        conn.execute("UPDATE users SET is_banned=? WHERE user_id=?",
                     (1 if ban else 0, uid))
        conn.commit()
        _dirty()
        return True
    finally:
        conn.close()


def db_set_user_limit(uid, limit):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("UPDATE users SET custom_limit=? WHERE user_id=?",
                     (limit, uid))
        conn.commit()
        _dirty()
        return True
    finally:
        conn.close()


def db_set_user_perm(uid, feature, value):
    col = {
        "channel": "allow_channel", "group": "allow_group",
        "manual": "allow_manual", "autowatch": "allow_autowatch",
        "custom_emoji": "allow_custom_emoji",
        "auto_watch_unlocked": "auto_watch_unlocked"
    }.get(feature)
    if not col:
        return False
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute(f"UPDATE users SET {col}=? WHERE user_id=?",
                     (1 if value else 0, uid))
        conn.commit()
    finally:
        conn.close()
    _dirty()
    return True


def db_set_user_lang(uid, lang):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("UPDATE users SET language=? WHERE user_id=?",
                     (lang, uid))
        conn.commit()
    finally:
        conn.close()
    _dirty()


def db_set_user_plan(uid, plan, days=30):
    exp = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("UPDATE users SET plan=?, plan_expires=? WHERE user_id=?",
                     (plan, exp, uid))
        conn.commit()
    finally:
        conn.close()
    _dirty()


def db_add_free_balance(uid, amount):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("""UPDATE users SET free_balance = free_balance + ?
            WHERE user_id=?""", (amount, uid))
        conn.commit()
    finally:
        conn.close()
    _dirty()


def db_spend_free_balance(uid, amount):
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("SELECT free_balance FROM users WHERE user_id=?",
                         (uid,)).fetchone()
        if not r or r[0] < amount:
            return False
        conn.execute("""UPDATE users SET free_balance = free_balance - ?
            WHERE user_id=?""", (amount, uid))
        conn.commit()
        _dirty()
        return True
    finally:
        conn.close()


def db_total_users():
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    finally:
        conn.close()


def db_all_users(l=50, o=0):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, first_name, username,
            joined_at, last_active, is_banned, total_reactions,
            total_bots, custom_limit FROM users
            ORDER BY last_active DESC LIMIT ? OFFSET ?""",
            (l, o)).fetchall()
    finally:
        conn.close()


def db_count_banned_users():
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT COUNT(*) FROM users
            WHERE is_banned=1""").fetchone()[0]
    finally:
        conn.close()


# ══════════════════════ DB — REACTIONS ══════════════════════
def db_save_reaction(uid, ct, cid, pl, pid, emoji, bu, status,
                     method="bot", server="free"):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            c = conn.cursor()
            c.execute("""INSERT INTO reactions (user_id, chat_title,
                chat_id, post_link, post_id, emoji, bot_username, status,
                method, server)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (uid, ct, cid, pl, pid, emoji, bu, status, method, server))
            if status == "ok":
                c.execute("""UPDATE users SET total_reactions =
                    total_reactions + 1 WHERE user_id=?""", (uid,))
            conn.commit()
            _dirty()
        finally:
            conn.close()
    except Exception as e:
        D(f"db_save_reaction: {str(e)[:80]}", "warn")


def db_total_reactions():
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT COUNT(*) FROM reactions
                WHERE status='ok'""").fetchone()[0]
        finally:
            conn.close()
    except Exception:
        return 0


def db_reactions_today():
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            t = datetime.now().strftime("%Y-%m-%d")
            return conn.execute("""SELECT COUNT(*) FROM reactions
                WHERE status='ok' AND DATE(created_at)=?""",
                (t,)).fetchone()[0]
        finally:
            conn.close()
    except Exception:
        return 0


def db_recent_reactions(l=20):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT r.user_id, u.first_name,
                r.chat_title, r.post_id, r.emoji, r.bot_username,
                r.status, r.created_at, r.method, r.server
                FROM reactions r LEFT JOIN users u
                ON u.user_id = r.user_id
                ORDER BY r.id DESC LIMIT ?""", (l,)).fetchall()
        finally:
            conn.close()
    except Exception:
        return []


def db_reactions_by_day(days=7):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            res = []
            for i in range(days-1, -1, -1):
                d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                n = conn.execute("""SELECT COUNT(*) FROM reactions
                    WHERE status='ok' AND DATE(created_at)=?""",
                    (d,)).fetchone()[0]
                res.append((d, n))
            return res
        finally:
            conn.close()
    except Exception:
        return []


def db_top_users_by_reactions(l=10):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT user_id, first_name,
                total_reactions FROM users WHERE total_reactions > 0
                ORDER BY total_reactions DESC LIMIT ?""", (l,)).fetchall()
        finally:
            conn.close()
    except Exception:
        return []


def db_top_groups(l=10):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT chat_title, chat_id,
                COUNT(*) as cnt FROM reactions WHERE status='ok'
                GROUP BY chat_id ORDER BY cnt DESC LIMIT ?""",
                (l,)).fetchall()
        finally:
            conn.close()
    except Exception:
        return []


def db_revenue_stats():
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            t = datetime.now().strftime("%Y-%m-%d")
            m = datetime.now().strftime("%Y-%m")
            tot = conn.execute("""SELECT COALESCE(SUM(amount),0)
                FROM payments WHERE status='approved'""").fetchone()[0]
            tr = conn.execute("""SELECT COALESCE(SUM(amount),0)
                FROM payments WHERE status='approved'
                AND DATE(created_at)=?""", (t,)).fetchone()[0]
            mr = conn.execute("""SELECT COALESCE(SUM(amount),0)
                FROM payments WHERE status='approved'
                AND strftime('%Y-%m', created_at)=?""", (m,)).fetchone()[0]
            return tot, tr, mr
        finally:
            conn.close()
    except Exception:
        return 0, 0, 0


# ══════════════════════ DB — BOTS & SERVERS ══════════════════════
def db_add_bot(token, username, bot_id, server="free"):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("""INSERT OR REPLACE INTO bots
            (token, username, bot_id, server) VALUES(?, ?, ?, ?)""",
            (token, username, bot_id, server))
        conn.execute("""INSERT OR REPLACE INTO bot_servers
            (token, username, server) VALUES(?, ?, ?)""",
            (token, username, server))
        conn.commit()
        _dirty()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def db_list_bots(server=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        if server:
            return conn.execute("""SELECT token, username, bot_id, added_at
                FROM bots WHERE server=? ORDER BY added_at ASC""",
                (server,)).fetchall()
        return conn.execute("""SELECT token, username, bot_id, added_at
            FROM bots ORDER BY added_at ASC""").fetchall()
    finally:
        conn.close()


def db_list_visible_bots(server=None):
    """Bots except permanent admins"""
    return [b for b in db_list_bots(server)
            if not is_permanent_admin(b[1])]


def db_count_bots(server=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        if server:
            return conn.execute("""SELECT COUNT(*) FROM bots
                WHERE server=?""", (server,)).fetchone()[0]
        return conn.execute("SELECT COUNT(*) FROM bots").fetchone()[0]
    finally:
        conn.close()


def db_count_visible_bots(server=None):
    return len(db_list_visible_bots(server))


def db_remove_bot(token):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("DELETE FROM bots WHERE token=?", (token,))
        conn.execute("DELETE FROM bot_servers WHERE token=?", (token,))
        conn.commit()
        _dirty()
        return True
    finally:
        conn.close()


def db_get_bot_by_username(username):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT token, username, bot_id, server
            FROM bots WHERE username=?""", (username,)).fetchone()
    finally:
        conn.close()


def db_move_bot_server(token, new_server):
    """Move bot to different server"""
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("UPDATE bots SET server=? WHERE token=?",
                     (new_server, token))
        conn.execute("""UPDATE bot_servers SET server=?,
            moved_at=CURRENT_TIMESTAMP WHERE token=?""",
            (new_server, token))
        conn.commit()
        _dirty()
        return True
    finally:
        conn.close()


def db_bot_stats():
    conn = sqlite3.connect(DB_FILE)
    try:
        total = conn.execute("SELECT COUNT(*) FROM bots").fetchone()[0]
        free = conn.execute("""SELECT COUNT(*) FROM bots
            WHERE server='free'""").fetchone()[0]
        paid = conn.execute("""SELECT COUNT(*) FROM bots
            WHERE server='paid'""").fetchone()[0]
        perm = sum(1 for b in db_list_bots() if is_permanent_admin(b[1]))
        return {"total": total, "free": free, "paid": paid,
                "permanent": perm}
    finally:
        conn.close()


# ══════════════════════ END OF PART 2 ══════════════════════
D("✅ Part 2 loaded — DB Part 1 (Users, Reactions, Bots, Servers)", "ok")
# ══════════════════════ DB — APPROVALS ══════════════════════
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


def db_create_approval(uid, fn, un=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("SELECT status FROM approvals WHERE user_id=?",
                         (uid,)).fetchone()
        if r is not None:
            return False, r[0]
        conn.execute("""INSERT INTO approvals (user_id, first_name,
            username, status) VALUES (?, ?, ?, 'pending')""", (uid, fn, un))
        conn.commit()
        _dirty()
        return True, "created"
    finally:
        conn.close()


def db_set_approval(uid, status, approved_by=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        ex = c.execute("SELECT 1 FROM approvals WHERE user_id=?",
                       (uid,)).fetchone()
        if not ex:
            u = c.execute("""SELECT first_name, username FROM users
                WHERE user_id=?""", (uid,)).fetchone()
            fn = u[0] if u else "User"
            un = u[1] if u else None
            c.execute("""INSERT INTO approvals (user_id, first_name,
                username, status, decided_at, approved_by)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, ?)""",
                (uid, fn, un, status, approved_by))
        else:
            c.execute("""UPDATE approvals SET status=?,
                decided_at=CURRENT_TIMESTAMP, approved_by=?
                WHERE user_id=?""", (status, approved_by, uid))
        conn.commit()
    finally:
        conn.close()
    _dirty()


def db_pending_approvals(l=50):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, first_name, username,
            requested_at FROM approvals WHERE status='pending'
            ORDER BY requested_at ASC LIMIT ?""", (l,)).fetchall()
    finally:
        conn.close()


def db_approved_users(l=100):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, first_name, username,
            decided_at, approved_by FROM approvals
            WHERE status='approved'
            ORDER BY decided_at DESC LIMIT ?""", (l,)).fetchall()
    finally:
        conn.close()


def db_count_pending_approvals():
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT COUNT(*) FROM approvals
                WHERE status='pending'""").fetchone()[0]
        finally:
            conn.close()
    except Exception:
        return 0


def db_count_approved_users():
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT COUNT(*) FROM approvals
                WHERE status='approved'""").fetchone()[0]
        finally:
            conn.close()
    except Exception:
        return 0


def db_count_rejected_users():
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT COUNT(*) FROM approvals
                WHERE status='rejected'""").fetchone()[0]
        finally:
            conn.close()
    except Exception:
        return 0


# ══════════════════════ DB — WATCHERS ══════════════════════
def db_add_watcher(u, ci, ct, cl, cty, rc=5, em="default",
                   ce=None, lp=0, server="free"):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        es = ",".join(ce) if ce else None
        c.execute("""INSERT INTO watchers (user_id, chat_id, chat_title,
            chat_link, chat_type, reaction_count, emoji_mode,
            custom_emojis, last_post_id, is_active, server)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)""",
            (u, ci, ct, cl, cty, rc, em, es, lp, server))
        conn.commit()
        _dirty()
        return c.lastrowid
    finally:
        conn.close()


def db_list_watchers(uid=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        sql = """SELECT id, user_id, chat_id, chat_title, chat_link,
            chat_type, reaction_count, emoji_mode, custom_emojis,
            last_post_id, is_active, created_at, last_run, server
            FROM watchers"""
        if uid:
            return conn.execute(sql + " WHERE user_id=? ORDER BY id DESC",
                                (uid,)).fetchall()
        return conn.execute(sql + " ORDER BY id DESC").fetchall()
    finally:
        conn.close()


def db_get_watcher(wid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT id, user_id, chat_id, chat_title,
            chat_link, chat_type, reaction_count, emoji_mode,
            custom_emojis, last_post_id, is_active, created_at,
            last_run, server FROM watchers WHERE id=?""", (wid,)).fetchone()
    finally:
        conn.close()


def db_update_watcher(wid, **kw):
    if not kw:
        return False
    fs, vs = [], []
    for k, v in kw.items():
        fs.append(f"{k}=?")
        vs.append(v)
    vs.append(wid)
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute(f"UPDATE watchers SET {', '.join(fs)} WHERE id=?",
                     tuple(vs))
        conn.commit()
        _dirty()
        return True
    finally:
        conn.close()


def db_delete_watcher(wid):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("DELETE FROM watchers WHERE id=?", (wid,))
        conn.commit()
        _dirty()
        return True
    finally:
        conn.close()


def db_count_active_watchers():
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT COUNT(*) FROM watchers
                WHERE is_active=1""").fetchone()[0]
        finally:
            conn.close()
    except Exception:
        return 0


# ══════════════════════ DB — TEMPLATES ══════════════════════
def db_add_template(uid, name, emojis):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("""INSERT INTO templates (user_id, name, emojis)
            VALUES (?, ?, ?)""", (uid, name, ",".join(emojis)))
        conn.commit()
        _dirty()
        return c.lastrowid
    finally:
        conn.close()


def db_list_templates(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT id, name, emojis FROM templates
            WHERE user_id=? ORDER BY id DESC""", (uid,)).fetchall()
    finally:
        conn.close()


def db_get_template(tid, uid=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        if uid:
            return conn.execute("""SELECT id, name, emojis FROM templates
                WHERE id=? AND user_id=?""", (tid, uid)).fetchone()
        return conn.execute("""SELECT id, name, emojis FROM templates
            WHERE id=?""", (tid,)).fetchone()
    finally:
        conn.close()


def db_delete_template(tid, uid=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        if uid:
            conn.execute("DELETE FROM templates WHERE id=? AND user_id=?",
                         (tid, uid))
        else:
            conn.execute("DELETE FROM templates WHERE id=?", (tid,))
        conn.commit()
        _dirty()
    finally:
        conn.close()


def db_count_templates(uid=None):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            if uid:
                return conn.execute("""SELECT COUNT(*) FROM templates
                    WHERE user_id=?""", (uid,)).fetchone()[0]
            return conn.execute("SELECT COUNT(*) FROM templates").fetchone()[0]
        finally:
            conn.close()
    except Exception:
        return 0


# ══════════════════════ DB — REFERRALS ══════════════════════
def db_get_referral_code(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("SELECT referral_code FROM users WHERE user_id=?",
                         (uid,)).fetchone()
        return r[0] if r else None
    finally:
        conn.close()


def db_find_user_by_ref_code(code):
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("SELECT user_id FROM users WHERE referral_code=?",
                         (code,)).fetchone()
        return r[0] if r else None
    finally:
        conn.close()


def db_add_referral(rid, nid):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        if c.execute("SELECT 1 FROM referrals WHERE new_user_id=?",
                     (nid,)).fetchone():
            return False
        c.execute("""INSERT INTO referrals (referrer_id, new_user_id, status)
            VALUES (?, ?, 'pending')""", (rid, nid))
        conn.commit()
        _dirty()
        return True
    finally:
        conn.close()


def db_validate_referral(nid):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        r = c.execute("""SELECT id, referrer_id FROM referrals
            WHERE new_user_id=? AND status='pending'""", (nid,)).fetchone()
        if not r:
            return None
        rid, ref = r
        total_reward = REFERRAL_REWARD + FRIEND_VALID_REWARD
        c.execute("""UPDATE referrals SET status='validated',
            reward_given=1, validated_at=CURRENT_TIMESTAMP
            WHERE id=?""", (rid,))
        c.execute("""UPDATE users SET referral_count = referral_count + 1,
            referral_earned = referral_earned + ?,
            free_balance = free_balance + ? WHERE user_id=?""",
            (total_reward, total_reward, ref))
        c.execute("""UPDATE users SET free_balance = free_balance + ?
            WHERE user_id=?""", (FRIEND_VALID_REWARD, nid))
        conn.commit()
        _dirty()
        return ref
    finally:
        conn.close()


def db_get_referral_stats(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("""SELECT referral_count, referral_earned
            FROM users WHERE user_id=?""", (uid,)).fetchone()
        return (r[0] or 0, r[1] or 0) if r else (0, 0)
    finally:
        conn.close()


def db_top_referrers(l=10):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, first_name, referral_count,
            referral_earned FROM users WHERE referral_count > 0
            ORDER BY referral_count DESC LIMIT ?""", (l,)).fetchall()
    finally:
        conn.close()


def db_count_referrals():
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            total = conn.execute("SELECT COUNT(*) FROM referrals"
                                 ).fetchone()[0]
            valid = conn.execute("""SELECT COUNT(*) FROM referrals
                WHERE status='validated'""").fetchone()[0]
            pend = conn.execute("""SELECT COUNT(*) FROM referrals
                WHERE status='pending'""").fetchone()[0]
            return {"total": total, "valid": valid, "pending": pend}
        finally:
            conn.close()
    except Exception:
        return {"total": 0, "valid": 0, "pending": 0}


# ══════════════════════ DB — NOTIFICATIONS ══════════════════════
def db_add_notification(uid, msg):
    if not feat_notifications():
        return
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            conn.execute("""INSERT INTO notifications (user_id, message)
                VALUES (?, ?)""", (uid, msg))
            conn.commit()
            _dirty()
        finally:
            conn.close()
    except Exception:
        pass


def db_get_notifications(uid, l=10):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT id, message, is_read, created_at
            FROM notifications WHERE user_id=?
            ORDER BY id DESC LIMIT ?""", (uid, l)).fetchall()
    finally:
        conn.close()


def db_count_unread_notifications(uid):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT COUNT(*) FROM notifications
                WHERE user_id=? AND is_read=0""", (uid,)).fetchone()[0]
        finally:
            conn.close()
    except Exception:
        return 0


def db_mark_notifications_read(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("UPDATE notifications SET is_read=1 WHERE user_id=?",
                     (uid,))
        conn.commit()
        _dirty()
    finally:
        conn.close()


def db_delete_notification(nid, uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("DELETE FROM notifications WHERE id=? AND user_id=?",
                     (nid, uid))
        conn.commit()
        _dirty()
    finally:
        conn.close()


def db_clear_notifications(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("DELETE FROM notifications WHERE user_id=?", (uid,))
        conn.commit()
        _dirty()
    finally:
        conn.close()


def db_broadcast_notification(message):
    """Send notification to all users"""
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("""INSERT INTO notifications (user_id, message)
            SELECT user_id, ? FROM users WHERE is_banned=0""", (message,))
        n = c.rowcount
        conn.commit()
        _dirty()
        return n
    finally:
        conn.close()


# ══════════════════════ END OF PART 3 ══════════════════════
D("✅ Part 3 loaded — DB Part 2 (Approvals, Watchers, Templates, Referrals, Notifications)", "ok")
# ══════════════════════ DB — QUEUE ══════════════════════
def db_add_queue(uid, cl, pl, rc, em="default", ce=None, st=None,
                 server="free"):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        es = ",".join(ce) if ce else None
        c.execute("""INSERT INTO queue (user_id, chat_link, post_link,
            reaction_count, emoji_mode, custom_emojis, scheduled_time,
            status, server) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)""",
            (uid, cl, pl, rc, em, es, st, server))
        conn.commit()
        _dirty()
        return c.lastrowid
    finally:
        conn.close()


def db_list_queue(user_id=None, status=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        base = """SELECT id, user_id, chat_link, post_link, reaction_count,
            emoji_mode, custom_emojis, scheduled_time, status, created_at,
            executed_at, error, server FROM queue"""
        if user_id and status:
            return conn.execute(base + """ WHERE user_id=? AND status=?
                ORDER BY id DESC""", (user_id, status)).fetchall()
        if user_id:
            return conn.execute(base + " WHERE user_id=? ORDER BY id DESC",
                                (user_id,)).fetchall()
        if status:
            return conn.execute(base + """ WHERE status=?
                ORDER BY scheduled_time ASC""", (status,)).fetchall()
        return conn.execute(base + " ORDER BY id DESC").fetchall()
    finally:
        conn.close()


def db_get_queue(qid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT id, user_id, chat_link, post_link,
            reaction_count, emoji_mode, custom_emojis, scheduled_time,
            status, created_at, executed_at, error, server
            FROM queue WHERE id=?""", (qid,)).fetchone()
    finally:
        conn.close()


def db_update_queue(qid, **kw):
    if not kw:
        return False
    fs, vs = [], []
    for k, v in kw.items():
        fs.append(f"{k}=?")
        vs.append(v)
    vs.append(qid)
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute(f"UPDATE queue SET {', '.join(fs)} WHERE id=?", tuple(vs))
        conn.commit()
        _dirty()
        return True
    finally:
        conn.close()


def db_delete_queue(qid, uid=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        if uid:
            conn.execute("DELETE FROM queue WHERE id=? AND user_id=?",
                         (qid, uid))
        else:
            conn.execute("DELETE FROM queue WHERE id=?", (qid,))
        conn.commit()
        _dirty()
    finally:
        conn.close()


def db_count_queue(status=None):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            if status:
                return conn.execute("""SELECT COUNT(*) FROM queue
                    WHERE status=?""", (status,)).fetchone()[0]
            return conn.execute("SELECT COUNT(*) FROM queue").fetchone()[0]
        finally:
            conn.close()
    except Exception:
        return 0


# ══════════════════════ DB — PAYMENTS ══════════════════════
def db_add_payment(uid, amt, plan, days, method, ss=""):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("""INSERT INTO payments (user_id, amount, plan, days,
            method, screenshot, status) VALUES (?, ?, ?, ?, ?, ?, 'pending')""",
            (uid, amt, plan, days, method, ss))
        conn.commit()
        _dirty()
        return c.lastrowid
    finally:
        conn.close()


def db_list_payments(user_id=None, status=None, l=50):
    conn = sqlite3.connect(DB_FILE)
    try:
        base = """SELECT id, user_id, amount, plan, days, method,
            screenshot, status, created_at, verified_at, verified_by, notes
            FROM payments"""
        if user_id and status:
            return conn.execute(base + """ WHERE user_id=? AND status=?
                ORDER BY id DESC LIMIT ?""",
                (user_id, status, l)).fetchall()
        if status:
            return conn.execute(base + """ WHERE status=?
                ORDER BY id DESC LIMIT ?""", (status, l)).fetchall()
        if user_id:
            return conn.execute(base + """ WHERE user_id=?
                ORDER BY id DESC LIMIT ?""", (user_id, l)).fetchall()
        return conn.execute(base + " ORDER BY id DESC LIMIT ?", (l,)).fetchall()
    finally:
        conn.close()


def db_get_payment(pid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT id, user_id, amount, plan, days,
            method, screenshot, status, created_at, verified_at,
            verified_by, notes FROM payments WHERE id=?""", (pid,)).fetchone()
    finally:
        conn.close()


def db_update_payment(pid, **kw):
    if not kw:
        return False
    fs, vs = [], []
    for k, v in kw.items():
        fs.append(f"{k}=?")
        vs.append(v)
    vs.append(pid)
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute(f"UPDATE payments SET {', '.join(fs)} WHERE id=?",
                     tuple(vs))
        conn.commit()
        _dirty()
        return True
    finally:
        conn.close()


def db_count_payments(status=None):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            if status:
                return conn.execute("""SELECT COUNT(*) FROM payments
                    WHERE status=?""", (status,)).fetchone()[0]
            return conn.execute("SELECT COUNT(*) FROM payments").fetchone()[0]
        finally:
            conn.close()
    except Exception:
        return 0


# ══════════════════════ DB — BULK JOBS ══════════════════════
def db_add_bulk_job(uid, jt, total, data=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("""INSERT INTO bulk_jobs (user_id, job_type, total, data)
            VALUES (?, ?, ?, ?)""", (uid, jt, total, data))
        conn.commit()
        _dirty()
        return c.lastrowid
    finally:
        conn.close()


def db_update_bulk_job(jid, **kw):
    if not kw:
        return False
    fs, vs = [], []
    for k, v in kw.items():
        fs.append(f"{k}=?")
        vs.append(v)
    vs.append(jid)
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute(f"UPDATE bulk_jobs SET {', '.join(fs)} WHERE id=?",
                     tuple(vs))
        conn.commit()
        _dirty()
        return True
    finally:
        conn.close()


def db_get_bulk_job(jid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT id, user_id, job_type, total,
            completed, failed, status, created_at, data
            FROM bulk_jobs WHERE id=?""", (jid,)).fetchone()
    finally:
        conn.close()


def db_list_bulk_jobs(uid=None, l=20):
    conn = sqlite3.connect(DB_FILE)
    try:
        base = """SELECT id, user_id, job_type, total, completed, failed,
            status, created_at, data FROM bulk_jobs"""
        if uid:
            return conn.execute(base + """ WHERE user_id=?
                ORDER BY id DESC LIMIT ?""", (uid, l)).fetchall()
        return conn.execute(base + " ORDER BY id DESC LIMIT ?", (l,)).fetchall()
    finally:
        conn.close()


# ══════════════════════ DB — FORCE CHANNELS ══════════════════════
def db_list_force_channels(only_active=True):
    conn = sqlite3.connect(DB_FILE)
    try:
        if only_active:
            return conn.execute("""SELECT id, channel, url, name, active
                FROM force_channels WHERE active=1 ORDER BY id ASC""").fetchall()
        return conn.execute("""SELECT id, channel, url, name, active
            FROM force_channels ORDER BY id ASC""").fetchall()
    finally:
        conn.close()


def db_add_force_channel(ch, url, name):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("""INSERT OR REPLACE INTO force_channels
            (channel, url, name, active) VALUES (?, ?, ?, 1)""",
            (ch, url, name))
        conn.commit()
        _dirty()
        return True
    finally:
        conn.close()


def db_delete_force_channel(fid):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("DELETE FROM force_channels WHERE id=?", (fid,))
        conn.commit()
        _dirty()
    finally:
        conn.close()


def db_toggle_force_channel(fid):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("""UPDATE force_channels SET active = 1 - active
            WHERE id=?""", (fid,))
        conn.commit()
        _dirty()
    finally:
        conn.close()


def db_count_force_channels(only_active=True):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            if only_active:
                return conn.execute("""SELECT COUNT(*) FROM force_channels
                    WHERE active=1""").fetchone()[0]
            return conn.execute("SELECT COUNT(*) FROM force_channels"
                                ).fetchone()[0]
        finally:
            conn.close()
    except Exception:
        return 0


# ══════════════════════ DB — TEAM MEMBERS ══════════════════════
def db_list_team():
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, role, permissions,
            commission_percent, total_sales, total_commission, added_at
            FROM team_members ORDER BY added_at DESC""").fetchall()
    finally:
        conn.close()


def db_add_team_member(uid, role="reseller", comm=10):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("""INSERT OR REPLACE INTO team_members
            (user_id, role, commission_percent) VALUES (?, ?, ?)""",
            (uid, role, comm))
        c.execute("""UPDATE users SET team_role=?, team_commission=?
            WHERE user_id=?""", (role, comm, uid))
        conn.commit()
        _dirty()
        return True
    finally:
        conn.close()


def db_remove_team_member(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("DELETE FROM team_members WHERE user_id=?", (uid,))
        c.execute("""UPDATE users SET team_role='user', team_commission=0
            WHERE user_id=?""", (uid,))
        conn.commit()
        _dirty()
    finally:
        conn.close()


def db_get_team_member(uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT user_id, role, permissions,
            commission_percent, total_sales, total_commission, added_at
            FROM team_members WHERE user_id=?""", (uid,)).fetchone()
    finally:
        conn.close()


def db_count_team_members():
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("SELECT COUNT(*) FROM team_members"
                                ).fetchone()[0]
        finally:
            conn.close()
    except Exception:
        return 0


# ══════════════════════ DB — CUSTOM PACKS ══════════════════════
def db_list_custom_packs():
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT id, name, emojis, price, is_paid
            FROM custom_packs ORDER BY id DESC""").fetchall()
    finally:
        conn.close()


def db_get_custom_pack(pid):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT id, name, emojis, price, is_paid
            FROM custom_packs WHERE id=?""", (pid,)).fetchone()
    finally:
        conn.close()


def db_add_custom_pack(name, emojis, price=0, is_paid=0):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        emo = ",".join(emojis) if isinstance(emojis, list) else emojis
        c.execute("""INSERT INTO custom_packs (name, emojis, price, is_paid)
            VALUES (?, ?, ?, ?)""", (name, emo, price, is_paid))
        conn.commit()
        _dirty()
        return c.lastrowid
    finally:
        conn.close()


def db_delete_custom_pack(pid):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("DELETE FROM custom_packs WHERE id=?", (pid,))
        conn.commit()
        _dirty()
    finally:
        conn.close()


def db_count_custom_packs():
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("SELECT COUNT(*) FROM custom_packs"
                                ).fetchone()[0]
        finally:
            conn.close()
    except Exception:
        return 0


# ══════════════════════ DB — USER STATS ══════════════════════
def stats_get(uid):
    if uid is None:
        return (None, 0, 0, None, 0, None, 0, 0, 0, None, 100, None)
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            r = conn.execute("""SELECT user_id, total_sent, today_sent,
                today_date, week_sent, week_start, success_count, fail_count,
                streak_days, last_bonus_date, trust_score, last_active
                FROM user_stats WHERE user_id=?""", (uid,)).fetchone()
            if not r:
                try:
                    conn.execute("""INSERT OR IGNORE INTO user_stats(user_id)
                        VALUES(?)""", (uid,))
                    conn.commit()
                except Exception:
                    pass
                return (uid, 0, 0, None, 0, None, 0, 0, 0, None, 100,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            return r
        finally:
            conn.close()
    except Exception:
        return (uid, 0, 0, None, 0, None, 0, 0, 0, None, 100, None)


def stats_bump(uid, ok=True):
    today = get_today_str()
    week_start = get_week_start_str()
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO user_stats(user_id) VALUES(?)",
                      (uid,))
            r = c.execute("""SELECT today_date, week_start FROM user_stats
                WHERE user_id=?""", (uid,)).fetchone()
            if r:
                if r[0] != today:
                    c.execute("""UPDATE user_stats SET today_sent=0,
                        today_date=? WHERE user_id=?""", (today, uid))
                if r[1] != week_start:
                    c.execute("""UPDATE user_stats SET week_sent=0,
                        week_start=? WHERE user_id=?""", (week_start, uid))
            if ok:
                c.execute("""UPDATE user_stats SET total_sent = total_sent + 1,
                    today_sent = today_sent + 1, week_sent = week_sent + 1,
                    success_count = success_count + 1,
                    last_active = CURRENT_TIMESTAMP WHERE user_id=?""", (uid,))
            else:
                c.execute("""UPDATE user_stats SET fail_count = fail_count + 1,
                    last_active = CURRENT_TIMESTAMP WHERE user_id=?""", (uid,))
            conn.commit()
        finally:
            conn.close()
        _dirty()
    except Exception:
        pass


def stats_update_trust(uid, delta):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            conn.execute("""UPDATE user_stats SET
                trust_score = MAX(0, MIN(100, trust_score + ?))
                WHERE user_id=?""", (delta, uid))
            conn.commit()
        finally:
            conn.close()
        _dirty()
    except Exception:
        pass


def stats_leaderboard(limit=10):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT s.user_id, u.first_name,
                s.total_sent, s.success_count, s.trust_score
                FROM user_stats s LEFT JOIN users u ON u.user_id = s.user_id
                ORDER BY s.total_sent DESC LIMIT ?""", (limit,)).fetchall()
        finally:
            conn.close()
    except Exception:
        return []


# ══════════════════════ DB — DAILY BONUS ══════════════════════
def bonus_can_claim(uid):
    try:
        today = get_today_str()
        conn = sqlite3.connect(DB_FILE)
        try:
            r = conn.execute("""SELECT 1 FROM daily_bonus
                WHERE user_id=? AND bonus_date=?""", (uid, today)).fetchone()
            return r is None
        finally:
            conn.close()
    except Exception:
        return True


def bonus_get_streak(uid):
    try:
        today = get_today_str()
        yesterday = (datetime.now() - timedelta(days=1)
                     ).strftime("%Y-%m-%d")
        conn = sqlite3.connect(DB_FILE)
        try:
            r = conn.execute("""SELECT streak_days, last_bonus_date
                FROM user_stats WHERE user_id=?""", (uid,)).fetchone()
            if not r:
                return 0
            streak, last = r
            if last == today:
                return streak or 0
            if last == yesterday:
                return streak or 0
            return 0
        finally:
            conn.close()
    except Exception:
        return 0


def bonus_claim(uid):
    if not bonus_can_claim(uid):
        return False, 0, bonus_get_streak(uid)
    today = get_today_str()
    try:
        base_amt = int(cfg_get("daily_bonus_amount", "1"))
    except Exception:
        base_amt = 1
    try:
        streak_bonus = int(cfg_get("streak_bonus_amount", "5"))
    except Exception:
        streak_bonus = 5
    current_streak = bonus_get_streak(uid)
    new_streak = current_streak + 1
    total = base_amt
    if new_streak % 7 == 0:
        total += streak_bonus
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            c = conn.cursor()
            c.execute("""INSERT OR REPLACE INTO daily_bonus
                (user_id, bonus_date, amount, streak_day)
                VALUES(?, ?, ?, ?)""", (uid, today, total, new_streak))
            c.execute("INSERT OR IGNORE INTO user_stats(user_id) VALUES(?)",
                      (uid,))
            c.execute("""UPDATE user_stats SET streak_days=?,
                last_bonus_date=? WHERE user_id=?""",
                (new_streak, today, uid))
            c.execute("""UPDATE users SET free_balance = free_balance + ?
                WHERE user_id=?""", (total, uid))
            conn.commit()
        finally:
            conn.close()
        _dirty()
    except Exception:
        return False, 0, 0
    return True, total, new_streak


def bonus_history(uid, l=10):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT bonus_date, amount, streak_day
                FROM daily_bonus WHERE user_id=?
                ORDER BY bonus_date DESC LIMIT ?""", (uid, l)).fetchall()
        finally:
            conn.close()
    except Exception:
        return []


# ══════════════════════ DB — AUTO-RETRY ══════════════════════
def retry_add(uid, chat_link, post_link, count, em="default",
              ce=None, err="", server="free"):
    try:
        max_att = int(cfg_get("auto_retry_max", "3"))
    except Exception:
        max_att = 3
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        es = ",".join(ce) if ce else None
        next_retry = (datetime.now() + timedelta(seconds=RETRY_FAILED_INTERVAL)
                      ).strftime("%Y-%m-%d %H:%M:%S")
        c.execute("""INSERT INTO retry_queue (user_id, chat_link,
            post_link, count, emoji_mode, custom_emojis, next_retry,
            last_error, server) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (uid, chat_link, post_link, count, em, es, next_retry,
             err[:200], server))
        conn.commit()
        _dirty()
        return c.lastrowid
    finally:
        conn.close()


def retry_list_due():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT id, user_id, chat_link, post_link,
                count, emoji_mode, custom_emojis, attempts, max_attempts,
                server FROM retry_queue
                WHERE status='pending' AND next_retry <= ?
                ORDER BY next_retry ASC LIMIT 5""", (now,)).fetchall()
        finally:
            conn.close()
    except Exception:
        return []


def retry_list_pending():
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT id, user_id, chat_link, post_link,
                count, emoji_mode, custom_emojis, attempts, max_attempts,
                next_retry, last_error, server FROM retry_queue
                WHERE status='pending' ORDER BY next_retry ASC""").fetchall()
        finally:
            conn.close()
    except Exception:
        return []


def retry_mark(rid, success=False, err=""):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        if success:
            c.execute("UPDATE retry_queue SET status='done' WHERE id=?", (rid,))
        else:
            r = c.execute("""SELECT attempts, max_attempts FROM retry_queue
                WHERE id=?""", (rid,)).fetchone()
            if r:
                att, mx = r
                new_att = att + 1
                if new_att >= mx:
                    c.execute("""UPDATE retry_queue SET attempts=?,
                        status='failed', last_error=? WHERE id=?""",
                        (new_att, err[:200], rid))
                else:
                    next_retry = (datetime.now()
                                  + timedelta(seconds=RETRY_FAILED_INTERVAL)
                                  ).strftime("%Y-%m-%d %H:%M:%S")
                    c.execute("""UPDATE retry_queue SET attempts=?,
                        next_retry=?, last_error=? WHERE id=?""",
                        (new_att, next_retry, err[:200], rid))
        conn.commit()
        _dirty()
    finally:
        conn.close()


def retry_count_pending():
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT COUNT(*) FROM retry_queue
                WHERE status='pending'""").fetchone()[0]
        finally:
            conn.close()
    except Exception:
        return 0


def retry_clear_all():
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("DELETE FROM retry_queue WHERE status='pending'")
        conn.commit()
        _dirty()
    finally:
        conn.close()


# ══════════════════════ DB — COUPONS ══════════════════════
def coupon_create(code, percent=0, flat=0, max_uses=0, expires=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("""INSERT OR REPLACE INTO coupons (code,
            discount_percent, discount_flat, max_uses, expires_at)
            VALUES(?, ?, ?, ?, ?)""",
            (code.upper(), percent, flat, max_uses, expires))
        conn.commit()
        _dirty()
        return True
    finally:
        conn.close()


def coupon_get(code):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute("""SELECT id, code, discount_percent,
            discount_flat, max_uses, used_count, expires_at, active
            FROM coupons WHERE code=?""", (code.upper(),)).fetchone()
    finally:
        conn.close()


def coupon_apply(code, original_price, uid):
    c = coupon_get(code)
    if not c:
        return None, "Coupon not found"
    cid, code_, pct, flat, max_u, used, expires, active = c
    if not active:
        return None, "Coupon disabled"
    if max_u > 0 and used >= max_u:
        return None, "Coupon fully used"
    if expires:
        try:
            if datetime.strptime(expires, "%Y-%m-%d %H:%M:%S") < datetime.now():
                return None, "Coupon expired"
        except Exception:
            pass
    conn = sqlite3.connect(DB_FILE)
    try:
        r = conn.execute("""SELECT 1 FROM coupon_uses
            WHERE coupon_id=? AND user_id=?""", (cid, uid)).fetchone()
        if r:
            return None, "Already used by you"
    finally:
        conn.close()
    discount = 0
    if pct > 0:
        discount += int(original_price * pct / 100)
    if flat > 0:
        discount += flat
    final_price = max(0, original_price - discount)
    return (cid, discount, final_price), None


def coupon_mark_used(cid, uid):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("""INSERT INTO coupon_uses(coupon_id, user_id)
            VALUES(?, ?)""", (cid, uid))
        c.execute("""UPDATE coupons SET used_count = used_count + 1
            WHERE id=?""", (cid,))
        conn.commit()
        _dirty()
    finally:
        conn.close()


def coupon_list():
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT id, code, discount_percent,
                discount_flat, max_uses, used_count, expires_at, active
                FROM coupons ORDER BY id DESC""").fetchall()
        finally:
            conn.close()
    except Exception:
        return []


def coupon_delete(cid):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("DELETE FROM coupons WHERE id=?", (cid,))
        conn.commit()
        _dirty()
    finally:
        conn.close()


def coupon_toggle(cid):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("""UPDATE coupons SET active = 1 - active
            WHERE id=?""", (cid,))
        conn.commit()
        _dirty()
    finally:
        conn.close()


def coupon_count_active():
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT COUNT(*) FROM coupons
                WHERE active=1""").fetchone()[0]
        finally:
            conn.close()
    except Exception:
        return 0


# ══════════════════════ DB — EMOJI STORE ══════════════════════
def store_list(active_only=True):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            if active_only:
                return conn.execute("""SELECT id, name, emojis, price,
                    description FROM emoji_store WHERE is_active=1
                    ORDER BY price ASC""").fetchall()
            return conn.execute("""SELECT id, name, emojis, price,
                description, is_active FROM emoji_store
                ORDER BY id DESC""").fetchall()
        finally:
            conn.close()
    except Exception:
        return []


def store_get(pid):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT id, name, emojis, price,
                description, is_active FROM emoji_store WHERE id=?""",
                (pid,)).fetchone()
        finally:
            conn.close()
    except Exception:
        return None


def store_add(name, emojis, price=0, desc=""):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        emo = ",".join(emojis) if isinstance(emojis, list) else emojis
        c.execute("""INSERT INTO emoji_store (name, emojis, price,
            description) VALUES(?, ?, ?, ?)""", (name, emo, price, desc))
        conn.commit()
        _dirty()
        return c.lastrowid
    finally:
        conn.close()


def store_delete(pid):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("DELETE FROM emoji_store WHERE id=?", (pid,))
        conn.commit()
        _dirty()
    finally:
        conn.close()


def store_toggle(pid):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("""UPDATE emoji_store SET is_active = 1 - is_active
            WHERE id=?""", (pid,))
        conn.commit()
        _dirty()
    finally:
        conn.close()


def store_user_owns(uid, pid):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            r = conn.execute("""SELECT 1 FROM user_store_buys
                WHERE user_id=? AND pack_id=?""", (uid, pid)).fetchone()
            return r is not None
        finally:
            conn.close()
    except Exception:
        return False


def store_buy(uid, pid, amount):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("""INSERT INTO user_store_buys
            (user_id, pack_id, paid_amount) VALUES(?, ?, ?)""",
            (uid, pid, amount))
        conn.commit()
        _dirty()
        return True
    finally:
        conn.close()


def store_user_purchases(uid):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT b.id, p.name, p.emojis,
                b.paid_amount, b.bought_at FROM user_store_buys b
                LEFT JOIN emoji_store p ON p.id = b.pack_id
                WHERE b.user_id=? ORDER BY b.id DESC""", (uid,)).fetchall()
        finally:
            conn.close()
    except Exception:
        return []


def store_count_active():
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT COUNT(*) FROM emoji_store
                WHERE is_active=1""").fetchone()[0]
        finally:
            conn.close()
    except Exception:
        return 0


# ══════════════════════ DB — POST ANALYTICS ══════════════════════
def post_analytics_add(uid, chat_id, post_id, chat_title, sent,
                       requested, server="free"):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            c = conn.cursor()
            c.execute("""INSERT INTO post_analytics (user_id, chat_id,
                post_id, chat_title, sent_count, requested_count, server)
                VALUES(?, ?, ?, ?, ?, ?, ?)""",
                (uid, chat_id, post_id, chat_title, sent, requested, server))
            conn.commit()
            _dirty()
        finally:
            conn.close()
    except Exception:
        pass


def post_analytics_user(uid, limit=10):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT chat_title, post_id, sent_count,
                requested_count, created_at FROM post_analytics
                WHERE user_id=? ORDER BY id DESC LIMIT ?""",
                (uid, limit)).fetchall()
        finally:
            conn.close()
    except Exception:
        return []


def post_analytics_stats(uid):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            r = conn.execute("""SELECT COUNT(*), COALESCE(SUM(sent_count),0),
                COALESCE(SUM(requested_count),0) FROM post_analytics
                WHERE user_id=?""", (uid,)).fetchone()
            total_posts, total_sent, total_req = r if r else (0, 0, 0)
            rate = int(total_sent / max(1, total_req) * 100)
            return {"posts": total_posts, "sent": total_sent,
                    "requested": total_req, "rate": rate}
        finally:
            conn.close()
    except Exception:
        return {"posts": 0, "sent": 0, "requested": 0, "rate": 0}


# ══════════════════════ DB — TEAMS (Reseller) ══════════════════════
def team_create(owner_id, name, comm=10):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("""INSERT INTO teams (owner_id, name, commission_percent)
            VALUES(?, ?, ?)""", (owner_id, name, comm))
        conn.commit()
        _dirty()
        return c.lastrowid
    finally:
        conn.close()


def team_list_reseller(rid):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("""SELECT id, client_id, plan, expires_at,
                commission_paid, added_at FROM team_clients
                WHERE reseller_id=? ORDER BY id DESC""", (rid,)).fetchall()
        finally:
            conn.close()
    except Exception:
        return []


def team_add_client(reseller_id, client_id, plan="free", expires=None):
    conn = sqlite3.connect(DB_FILE)
    try:
        c = conn.cursor()
        c.execute("""INSERT INTO team_clients (team_id, reseller_id,
            client_id, plan, expires_at) VALUES(?, ?, ?, ?, ?)""",
            (0, reseller_id, client_id, plan, expires))
        conn.commit()
        _dirty()
        return c.lastrowid
    finally:
        conn.close()


def team_reseller_stats(rid):
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            r = conn.execute("""SELECT COUNT(*),
                COALESCE(SUM(commission_paid),0)
                FROM team_clients WHERE reseller_id=?""", (rid,)).fetchone()
            return (r[0] or 0, r[1] or 0) if r else (0, 0)
        finally:
            conn.close()
    except Exception:
        return (0, 0)


def team_count_clients():
    try:
        conn = sqlite3.connect(DB_FILE)
        try:
            return conn.execute("SELECT COUNT(*) FROM team_clients"
                                ).fetchone()[0]
        finally:
            conn.close()
    except Exception:
        return 0


# ══════════════════════ SYNC BOTS FROM CONFIG ══════════════════════
def sync_bots_from_config():
    """
    Sync bots from config (BOT_TOKENS) into DB.
    Server split 50/50 based on config lists.
    Auto-dedupe + auto-assign server.
    """
    existing = {r[0] for r in db_list_bots()}
    added_free = 0
    added_paid = 0
    skipped = 0

    # Add free server bots
    for tok in FREE_SERVER_TOKENS:
        if tok in existing:
            skipped += 1
            continue
        info = bot_get_me(tok)
        if info and db_add_bot(tok, info["username"], info["id"],
                               server="free"):
            added_free += 1
            existing.add(tok)

    # Add paid server bots
    for tok in PAID_SERVER_TOKENS:
        if tok in existing:
            skipped += 1
            continue
        info = bot_get_me(tok)
        if info and db_add_bot(tok, info["username"], info["id"],
                               server="paid"):
            added_paid += 1
            existing.add(tok)

    D(f"Bot sync: +{added_free} free, +{added_paid} paid, "
      f"{skipped} skipped", "ok")
    return added_free + added_paid


# ══════════════════════ END OF PART 4 ══════════════════════
D("✅ Part 4 loaded — DB Part 3 (Queue, Payments, Store, Coupons, Stats)", "ok")
# ══════════════════════ LANGUAGES ══════════════════════
LANG_STRINGS = {
    "en": {
        "welcome":"Welcome back", "send_reactions":"Send Reactions",
        "auto_watch":"Auto-Watch", "templates":"Templates",
        "referral":"Referral", "upgrade":"Upgrade",
        "notifications":"Notifications", "language":"Language",
        "info":"Info", "support":"Support", "help":"Help",
        "owner_panel":"Owner Panel", "home":"Main Menu",
        "back":"Back", "cancel":"Cancel", "channel":"Channel",
        "group":"Group", "default_emoji":"Default Emoji",
        "custom_emoji":"Custom Emoji", "emoji_packs":"Emoji Packs",
        "send":"Send", "choose_language":"Choose Language",
        "language_changed":"Language changed!", "your_limit":"Your limit",
        "per_post":"per post", "plan":"Plan", "free_plan":"Free Plan",
        "my_watches":"My Watches", "add_watch":"Add Watch",
        "contact_owner":"Contact Owner", "retry":"Retry",
        "how_many":"How many reactions?", "emoji_mode":"Emoji mode",
        "post_link":"Send post link", "chat_link":"Send chat link",
        "count_per_post":"Count per post", "chat_type":"Chat type?",
        "my_link":"My Link", "stats":"Stats",
        "leaderboard":"Leaderboard", "analytics":"Analytics",
        "queue":"Queue", "bulk":"Bulk", "team":"Team",
        "buy_plan":"Buy Plan", "payment":"Payment",
        "dashboard":"Dashboard", "daily_bonus":"Daily Bonus",
        "claim":"Claim Bonus", "streak":"Streak",
        "trust_score":"Trust Score", "post_history":"Post History",
        "store":"Emoji Store", "reseller":"Reseller Panel",
        "help_title":"How to Make Owner Admin",
        "server":"Server", "free_server":"Free Server",
        "paid_server":"Paid Server", "your_server":"Your Server",
    },
    "ur": {
        "welcome":"خوش آمدید", "send_reactions":"ری ایکشن بھیجیں",
        "auto_watch":"آٹو واچ", "templates":"ٹیمپلیٹس",
        "referral":"ریفرل", "upgrade":"اپ گریڈ",
        "notifications":"اطلاعات", "language":"زبان",
        "info":"معلومات", "support":"سپورٹ", "help":"مدد",
        "owner_panel":"اونر پینل", "home":"مین مینو",
        "back":"واپس", "cancel":"کینسل", "channel":"چینل",
        "group":"گروپ", "default_emoji":"ڈیفالٹ ایموجی",
        "custom_emoji":"کسٹم ایموجی", "emoji_packs":"ایموجی پیکس",
        "send":"بھیجیں", "choose_language":"زبان منتخب کریں",
        "language_changed":"زبان تبدیل ہو گئی!",
        "your_limit":"آپ کی حد", "per_post":"فی پوسٹ",
        "plan":"پلان", "free_plan":"مفت پلان",
        "my_watches":"میری واچز", "add_watch":"واچ شامل کریں",
        "contact_owner":"اونر سے رابطہ", "retry":"دوبارہ",
        "how_many":"کتنے ری ایکشن؟", "emoji_mode":"ایموجی موڈ",
        "post_link":"پوسٹ لنک بھیجیں", "chat_link":"چیٹ لنک بھیجیں",
        "count_per_post":"فی پوسٹ", "chat_type":"چیٹ کی قسم؟",
        "my_link":"میرا لنک", "stats":"اعداد",
        "leaderboard":"لیڈر بورڈ", "analytics":"تجزیہ",
        "queue":"قطار", "bulk":"بلک", "team":"ٹیم",
        "buy_plan":"پلان خریدیں", "payment":"ادائیگی",
        "dashboard":"ڈیش بورڈ", "daily_bonus":"روزانہ بونس",
        "claim":"بونس لیں", "streak":"سٹریک",
        "trust_score":"ٹرسٹ سکور", "post_history":"پوسٹ ہسٹری",
        "store":"ایموجی اسٹور", "reseller":"ری سیلر پینل",
        "help_title":"اونر کو ایڈمن کیسے بنائیں",
        "server":"سرور", "free_server":"مفت سرور",
        "paid_server":"پڈ سرور", "your_server":"آپ کا سرور",
    },
    "hi": {
        "welcome":"वापसी पर स्वागत", "send_reactions":"रिएक्शन भेजें",
        "auto_watch":"ऑटो-वॉच", "templates":"टेम्पलेट",
        "referral":"रेफरल", "upgrade":"अपग्रेड",
        "notifications":"सूचनाएं", "language":"भाषा",
        "info":"जानकारी", "support":"सहायता", "help":"मदद",
        "owner_panel":"ओनर पैनल", "home":"मुख्य मेनू",
        "back":"वापस", "cancel":"रद्द", "channel":"चैनल",
        "group":"ग्रुप", "default_emoji":"डिफ़ॉल्ट इमोजी",
        "custom_emoji":"कस्टम इमोजी", "emoji_packs":"इमोजी पैक",
        "send":"भेजें", "choose_language":"भाषा चुनें",
        "language_changed":"भाषा बदल गई!",
        "your_limit":"आपकी सीमा", "per_post":"प्रति पोस्ट",
        "plan":"प्लान", "free_plan":"फ्री प्लान",
        "my_watches":"मेरी वॉच", "add_watch":"वॉच जोड़ें",
        "contact_owner":"मालिक से संपर्क", "retry":"पुनः",
        "how_many":"कितने रिएक्शन?", "emoji_mode":"इमोजी मोड",
        "post_link":"पोस्ट लिंक भेजें", "chat_link":"चैट लिंक भेजें",
        "count_per_post":"प्रति पोस्ट", "chat_type":"चैट टाइप?",
        "my_link":"मेरा लिंक", "stats":"आंकड़े",
        "leaderboard":"लीडरबोर्ड", "analytics":"विश्लेषण",
        "queue":"कतार", "bulk":"बल्क", "team":"टीम",
        "buy_plan":"प्लान खरीदें", "payment":"भुगतान",
        "dashboard":"डैशबोर्ड", "daily_bonus":"दैनिक बोनस",
        "claim":"बोनस लें", "streak":"स्ट्रीक",
        "trust_score":"ट्रस्ट स्कोर", "post_history":"पोस्ट इतिहास",
        "store":"इमोजी स्टोर", "reseller":"रीसेलर पैनल",
        "help_title":"मालिक को एडमिन कैसे बनाएं",
        "server":"सर्वर", "free_server":"फ्री सर्वर",
        "paid_server":"पेड सर्वर", "your_server":"आपका सर्वर",
    },
    "ar": {
        "welcome":"مرحباً بعودتك", "send_reactions":"إرسال التفاعلات",
        "auto_watch":"المراقبة", "templates":"القوالب",
        "referral":"الإحالة", "upgrade":"ترقية",
        "notifications":"الإشعارات", "language":"اللغة",
        "info":"معلومات", "support":"الدعم", "help":"مساعدة",
        "owner_panel":"لوحة المالك", "home":"القائمة",
        "back":"رجوع", "cancel":"إلغاء", "channel":"قناة",
        "group":"مجموعة", "default_emoji":"افتراضي",
        "custom_emoji":"مخصص", "emoji_packs":"حزم",
        "send":"إرسال", "choose_language":"اختر اللغة",
        "language_changed":"تم التغيير!",
        "your_limit":"حدك", "per_post":"لكل منشور",
        "plan":"خطة", "free_plan":"مجاني",
        "my_watches":"مراقباتي", "add_watch":"إضافة",
        "contact_owner":"اتصل بالمالك", "retry":"إعادة",
        "how_many":"كم؟", "emoji_mode":"وضع الرموز",
        "post_link":"رابط المنشور", "chat_link":"رابط الدردشة",
        "count_per_post":"لكل منشور", "chat_type":"نوع الدردشة؟",
        "my_link":"رابطي", "stats":"إحصائيات",
        "leaderboard":"المتصدرون", "analytics":"تحليلات",
        "queue":"قائمة", "bulk":"جماعي", "team":"فريق",
        "buy_plan":"شراء", "payment":"دفع",
        "dashboard":"لوحة", "daily_bonus":"مكافأة يومية",
        "claim":"مطالبة", "streak":"سلسلة",
        "trust_score":"درجة الثقة", "post_history":"سجل المنشورات",
        "store":"متجر الرموز", "reseller":"لوحة الموزع",
        "help_title":"كيفية جعل المالك مشرفًا",
        "server":"خادم", "free_server":"خادم مجاني",
        "paid_server":"خادم مدفوع", "your_server":"خادمك",
    },
    "ru": {
        "welcome":"С возвращением", "send_reactions":"Реакции",
        "auto_watch":"Авто-наблюдение", "templates":"Шаблоны",
        "referral":"Реферал", "upgrade":"Обновить",
        "notifications":"Уведомления", "language":"Язык",
        "info":"Инфо", "support":"Поддержка", "help":"Помощь",
        "owner_panel":"Панель владельца", "home":"Меню",
        "back":"Назад", "cancel":"Отмена", "channel":"Канал",
        "group":"Группа", "default_emoji":"Обычные",
        "custom_emoji":"Свои", "emoji_packs":"Наборы",
        "send":"Отправить", "choose_language":"Выбрать язык",
        "language_changed":"Язык изменён!",
        "your_limit":"Лимит", "per_post":"на пост",
        "plan":"План", "free_plan":"Бесплатный",
        "my_watches":"Мои наблюдения", "add_watch":"Добавить",
        "contact_owner":"Связаться", "retry":"Повтор",
        "how_many":"Сколько?", "emoji_mode":"Режим",
        "post_link":"Ссылка на пост", "chat_link":"Ссылка чата",
        "count_per_post":"На пост", "chat_type":"Тип чата?",
        "my_link":"Моя ссылка", "stats":"Статистика",
        "leaderboard":"Топ", "analytics":"Аналитика",
        "queue":"Очередь", "bulk":"Массово", "team":"Команда",
        "buy_plan":"Купить", "payment":"Оплата",
        "dashboard":"Панель", "daily_bonus":"Дневной бонус",
        "claim":"Забрать", "streak":"Серия",
        "trust_score":"Рейтинг", "post_history":"История",
        "store":"Магазин", "reseller":"Реселлер",
        "help_title":"Как сделать владельца админом",
        "server":"Сервер", "free_server":"Бесплатный",
        "paid_server":"Платный", "your_server":"Ваш сервер",
    },
    "es": {
        "welcome":"Bienvenido", "send_reactions":"Reacciones",
        "auto_watch":"Auto-Vigilancia", "templates":"Plantillas",
        "referral":"Referido", "upgrade":"Mejorar",
        "notifications":"Notificaciones", "language":"Idioma",
        "info":"Info", "support":"Soporte", "help":"Ayuda",
        "owner_panel":"Panel Dueño", "home":"Menú",
        "back":"Atrás", "cancel":"Cancelar", "channel":"Canal",
        "group":"Grupo", "default_emoji":"Predeterminado",
        "custom_emoji":"Personalizado", "emoji_packs":"Paquetes",
        "send":"Enviar", "choose_language":"Elegir idioma",
        "language_changed":"¡Cambiado!",
        "your_limit":"Límite", "per_post":"por post",
        "plan":"Plan", "free_plan":"Gratis",
        "my_watches":"Vigilancias", "add_watch":"Agregar",
        "contact_owner":"Contactar", "retry":"Reintentar",
        "how_many":"¿Cuántas?", "emoji_mode":"Modo emoji",
        "post_link":"Enlace post", "chat_link":"Enlace chat",
        "count_per_post":"Por post", "chat_type":"¿Tipo?",
        "my_link":"Mi enlace", "stats":"Stats",
        "leaderboard":"Ranking", "analytics":"Análisis",
        "queue":"Cola", "bulk":"Masivo", "team":"Equipo",
        "buy_plan":"Comprar", "payment":"Pago",
        "dashboard":"Panel", "daily_bonus":"Bono diario",
        "claim":"Reclamar", "streak":"Racha",
        "trust_score":"Confianza", "post_history":"Historial",
        "store":"Tienda", "reseller":"Revendedor",
        "help_title":"Cómo hacer admin al dueño",
        "server":"Servidor", "free_server":"Gratis",
        "paid_server":"Pago", "your_server":"Tu servidor",
    },
    "id": {
        "welcome":"Selamat Datang", "send_reactions":"Kirim Reaksi",
        "auto_watch":"Auto-Pantau", "templates":"Template",
        "referral":"Referral", "upgrade":"Upgrade",
        "notifications":"Notifikasi", "language":"Bahasa",
        "info":"Info", "support":"Dukungan", "help":"Bantuan",
        "owner_panel":"Panel Pemilik", "home":"Menu",
        "back":"Kembali", "cancel":"Batal", "channel":"Channel",
        "group":"Grup", "default_emoji":"Default",
        "custom_emoji":"Kustom", "emoji_packs":"Paket",
        "send":"Kirim", "choose_language":"Pilih Bahasa",
        "language_changed":"Bahasa diubah!",
        "your_limit":"Batas", "per_post":"per",
        "plan":"Paket", "free_plan":"Gratis",
        "my_watches":"Pantauan", "add_watch":"Tambah",
        "contact_owner":"Hubungi", "retry":"Coba",
        "how_many":"Berapa?", "emoji_mode":"Mode",
        "post_link":"Link posting", "chat_link":"Link chat",
        "count_per_post":"Per", "chat_type":"Tipe?",
        "my_link":"Link", "stats":"Statistik",
        "leaderboard":"Peringkat", "analytics":"Analitik",
        "queue":"Antrian", "bulk":"Massal", "team":"Tim",
        "buy_plan":"Beli", "payment":"Bayar",
        "dashboard":"Dasbor", "daily_bonus":"Bonus Harian",
        "claim":"Klaim", "streak":"Streak",
        "trust_score":"Trust Score", "post_history":"Riwayat",
        "store":"Toko", "reseller":"Reseller",
        "help_title":"Cara menjadikan pemilik sebagai admin",
        "server":"Server", "free_server":"Gratis",
        "paid_server":"Berbayar", "your_server":"Server Anda",
    },
}


def L(uid, key):
    """Get translated string for user's language"""
    if not feat_multilang():
        return LANG_STRINGS["en"].get(key, key)
    if uid is None:
        return LANG_STRINGS["en"].get(key, key)
    try:
        u = db_get_user_full(uid)
        lang = "en"
        if u and len(u) > 18 and u[18] and u[18] in LANG_STRINGS:
            lang = u[18]
        return LANG_STRINGS.get(lang, LANG_STRINGS["en"]).get(key, key)
    except Exception:
        return LANG_STRINGS["en"].get(key, key)


def L_static(lang, key):
    return LANG_STRINGS.get(lang, LANG_STRINGS["en"]).get(key, key)


# ══════════════════════ HELP TEXT (Multi-Lang) ══════════════════════
def get_help_text(uid=None):
    """Complete help guide for making owner admin"""
    uname = get_owner_username()
    oid = get_owner_id()

    u = db_get_user_full(uid) if uid else None
    lang = "en"
    if u and len(u) > 18 and u[18]:
        lang = u[18]

    if lang == "ur":
        return (
            f"{STAR_LINE}\n📖 **مدد — اونر کو ایڈمن بنائیں** 📖\n{STAR_LINE}\n\n"
            f"❌ **پہلے یہ ضروری ہے!**\n"
            f"ری ایکشن بھیجنے سے پہلے اونر کو ایڈمن بنانا لازمی ہے۔\n\n"
            f"{DIV}\n👑 **اونر کی تفصیل**\n{DIV}\n"
            f"👤 یوزرنیم: @{uname}\n"
            f"🆔 آئی ڈی: `{oid}`\n\n"
            f"{DIV}\n📋 **کیسے ایڈمن بنائیں؟**\n{DIV}\n\n"
            f"**1️⃣ اپنے چینل/گروپ کو کھولیں**\n\n"
            f"**2️⃣ ایڈمنسٹریٹرز میں جائیں**\n"
            f"   چینل/گروپ کا نام دبائیں → Administrators\n\n"
            f"**3️⃣ نیا ایڈمن شامل کریں**\n"
            f"   🔍 سرچ میں لکھیں: `@{uname}`\n"
            f"   یا آئی ڈی: `{oid}`\n\n"
            f"**4️⃣ تمام اجازتیں دیں** ⚠️\n"
            f"   ✅ Change Info\n"
            f"   ✅ Add New Admins\n"
            f"   ✅ Post Messages\n"
            f"   ✅ Edit Messages\n"
            f"   ✅ Delete Messages\n"
            f"   ✅ Invite Users\n"
            f"   ✅ Pin Messages\n"
            f"   ✅ Manage Voice Chats\n"
            f"   ✅ Ban Users\n\n"
            f"**5️⃣ محفوظ کریں** ✅\n\n"
            f"{DIV}\n⚠️ **اہم نوٹ**\n{DIV}\n"
            f"• یہ عمل صرف **ایک بار** کرنا ہے\n"
            f"• اونر کو **ایڈمن رہنے دیں**\n"
            f"• آپ کے اصل ایڈمن **محفوظ** رہیں گے\n\n"
            f"💬 @{uname}"
        )

    if lang == "hi":
        return (
            f"{STAR_LINE}\n📖 **मदद — मालिक को एडमिन बनाएं** 📖\n{STAR_LINE}\n\n"
            f"❌ **पहले यह ज़रूरी है!**\n"
            f"रिएक्शन भेजने से पहले मालिक को एडमिन बनाना ज़रूरी है।\n\n"
            f"{DIV}\n👑 **मालिक की जानकारी**\n{DIV}\n"
            f"👤 यूज़रनेम: @{uname}\n"
            f"🆔 आईडी: `{oid}`\n\n"
            f"{DIV}\n📋 **एडमिन कैसे बनाएं?**\n{DIV}\n\n"
            f"**1️⃣ अपना चैनल/ग्रुप खोलें**\n\n"
            f"**2️⃣ एडमिनिस्ट्रेटर्स में जाएं**\n\n"
            f"**3️⃣ नया एडमिन जोड़ें**\n"
            f"   🔍 सर्च: `@{uname}`\n"
            f"   या आईडी: `{oid}`\n\n"
            f"**4️⃣ सभी परमिशन दें** ⚠️\n"
            f"   ✅ Change Info / Add Admins / Post / Edit / Delete\n"
            f"   ✅ Invite / Pin / Manage Voice / Ban\n\n"
            f"**5️⃣ सेव करें** ✅\n\n"
            f"{DIV}\n⚠️ **ज़रूरी**\n{DIV}\n"
            f"• सिर्फ **एक बार** करना है\n"
            f"• मालिक को **एडमिन रहने दें**\n\n"
            f"💬 @{uname}"
        )

    if lang == "ar":
        return (
            f"{STAR_LINE}\n📖 **مساعدة — جعل المالك مشرفًا** 📖\n{STAR_LINE}\n\n"
            f"❌ **هذا مطلوب أولاً!**\n\n"
            f"{DIV}\n👑 **بيانات المالك**\n{DIV}\n"
            f"👤 @{uname}\n"
            f"🆔 `{oid}`\n\n"
            f"**1️⃣ افتح قناتك/مجموعتك**\n"
            f"**2️⃣ اذهب إلى المشرفين**\n"
            f"**3️⃣ أضف مشرفًا**\n"
            f"   `@{uname}` أو `{oid}`\n"
            f"**4️⃣ امنح جميع الصلاحيات** ✅\n"
            f"**5️⃣ احفظ** ✅\n\n"
            f"💬 @{uname}"
        )

    if lang == "ru":
        return (
            f"{STAR_LINE}\n📖 **Помощь — владелец админом** 📖\n{STAR_LINE}\n\n"
            f"❌ **Это обязательно!**\n\n"
            f"{DIV}\n👑 **Владелец**\n{DIV}\n"
            f"👤 @{uname}\n"
            f"🆔 `{oid}`\n\n"
            f"**1️⃣ Откройте канал/группу**\n"
            f"**2️⃣ Администраторы**\n"
            f"**3️⃣ Добавить админа**\n"
            f"   `@{uname}` или `{oid}`\n"
            f"**4️⃣ Дайте ВСЕ права** ✅\n"
            f"**5️⃣ Сохраните** ✅\n\n"
            f"💬 @{uname}"
        )

    if lang == "es":
        return (
            f"{STAR_LINE}\n📖 **Ayuda — Hacer admin al dueño** 📖\n{STAR_LINE}\n\n"
            f"❌ **¡Obligatorio!**\n\n"
            f"{DIV}\n👑 **Dueño**\n{DIV}\n"
            f"👤 @{uname}\n"
            f"🆔 `{oid}`\n\n"
            f"**1️⃣ Abre tu canal/grupo**\n"
            f"**2️⃣ Administradores**\n"
            f"**3️⃣ Añadir admin**\n"
            f"   `@{uname}` o `{oid}`\n"
            f"**4️⃣ Dar TODOS los permisos** ✅\n"
            f"**5️⃣ Guardar** ✅\n\n"
            f"💬 @{uname}"
        )

    if lang == "id":
        return (
            f"{STAR_LINE}\n📖 **Bantuan — Pemilik jadi admin** 📖\n{STAR_LINE}\n\n"
            f"❌ **Wajib dulu!**\n\n"
            f"{DIV}\n👑 **Pemilik**\n{DIV}\n"
            f"👤 @{uname}\n"
            f"🆔 `{oid}`\n\n"
            f"**1️⃣ Buka channel/grup**\n"
            f"**2️⃣ Administrator**\n"
            f"**3️⃣ Tambah admin**\n"
            f"   `@{uname}` atau `{oid}`\n"
            f"**4️⃣ Beri SEMUA izin** ✅\n"
            f"**5️⃣ Simpan** ✅\n\n"
            f"💬 @{uname}"
        )

    # English default
    return (
        f"{STAR_LINE}\n📖 **HELP — Make Owner Admin** 📖\n{STAR_LINE}\n\n"
        f"❌ **Required first!**\n"
        f"Before sending reactions, you MUST make the owner an admin.\n\n"
        f"{DIV}\n👑 **OWNER INFO**\n{DIV}\n"
        f"👤 Username: @{uname}\n"
        f"🆔 ID: `{oid}`\n\n"
        f"{DIV}\n📋 **HOW TO MAKE ADMIN**\n{DIV}\n\n"
        f"**1️⃣ Open your Channel/Group**\n"
        f"   Go to Telegram and open the chat where you want reactions\n\n"
        f"**2️⃣ Go to Administrators**\n"
        f"   Tap the channel/group name → Administrators\n\n"
        f"**3️⃣ Add New Admin**\n"
        f"   Tap Add Admin\n"
        f"   🔍 Search: `@{uname}`\n"
        f"   or ID: `{oid}`\n\n"
        f"**4️⃣ Give ALL permissions** ⚠️\n"
        f"   ✅ Change Info\n"
        f"   ✅ Add New Admins\n"
        f"   ✅ Post Messages\n"
        f"   ✅ Edit Messages\n"
        f"   ✅ Delete Messages\n"
        f"   ✅ Invite Users\n"
        f"   ✅ Pin Messages\n"
        f"   ✅ Manage Voice Chats\n"
        f"   ✅ Ban Users\n\n"
        f"**5️⃣ Save**\n"
        f"   Tap Save ✅\n\n"
        f"{DIV}\n⚠️ **IMPORTANT NOTES**\n{DIV}\n"
        f"• Do this **ONLY ONCE**\n"
        f"• Keep the owner as **admin** — don't remove\n"
        f"• Reaction bots are added & removed **automatically**\n"
        f"• Your original admins stay **SAFE**\n\n"
        f"{DIV}\n❓ Need help?\n{DIV}\n"
        f"💬 @{uname}"
    )


# ══════════════════════ BOT API HELPERS ══════════════════════
def bot_get_me(token):
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe",
                         timeout=10).json()
        return r.get("result") if r.get("ok") else None
    except Exception:
        return None


def bot_reaction(token, chat_id, msg_id, emoji):
    """Send single reaction. Returns (ok, desc, retry_sec)"""
    url = f"https://api.telegram.org/bot{token}/setMessageReaction"
    payload = {
        "chat_id": chat_id,
        "message_id": msg_id,
        "reaction": [{"type": "emoji", "emoji": emoji}]
    }
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


# ══════════════════════ PARSE HELPERS ══════════════════════
def parse_channel_link(link):
    link = link.strip()
    if "t.me/+" in link:
        h = link.split("+")[-1].split("?")[0]
        return None, h
    if "t.me/joinchat/" in link:
        h = link.split("joinchat/")[-1].split("?")[0]
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
    return bool(username and username in PERMANENT_ADMIN_BOTS)


# ══════════════════════ BUTTON HELPER ══════════════════════
def btn(text, data=None, url=None, style=None):
    if url:
        b = Button.url(text, url)
    else:
        b = Button.inline(text, data if data else b"none")
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


# ══════════════════════ SAFE EDIT / ANSWER ══════════════════════
async def safe_edit(event, text, buttons=None, alert=None):
    try:
        if alert:
            try:
                await event.answer(alert, alert=True)
            except Exception:
                pass
        key = getattr(event, "chat_id", 0)
        now = time.time()
        wait = 1.5 - (now - _LAST_EDIT_TIME.get(key, 0))
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
                await event.client.send_message(event.chat_id, text,
                                                buttons=buttons)
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


async def safe_answer(event, text=None, alert=False):
    try:
        if text:
            await event.answer(text, alert=alert)
        else:
            await event.answer()
    except Exception:
        pass


# ══════════════════════ SAFE ENTITY ══════════════════════
async def safe_get_entity(ref, cache_key=None, cache_store=None):
    global RESOLVE_FLOOD_UNTIL
    if RESOLVE_FLOOD_UNTIL and datetime.now() < RESOLVE_FLOOD_UNTIL:
        raise Exception("Resolve flood")
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
        entity = await asyncio.wait_for(admin_client.get_entity(ref),
                                        timeout=15)
        cache_store[cache_key] = (entity,
                                  now + timedelta(seconds=ENTITY_CACHE_TTL))
        return entity
    except FloodWaitError as e:
        wait_sec = min(e.seconds + 10, 3600)
        if backup_client:
            try:
                entity = await asyncio.wait_for(
                    backup_client.get_entity(ref), timeout=15)
                cache_store[cache_key] = (entity,
                                          now + timedelta(seconds=ENTITY_CACHE_TTL))
                return entity
            except Exception:
                pass
        RESOLVE_FLOOD_UNTIL = now + timedelta(seconds=wait_sec)
        raise Exception(f"Wait {wait_sec}s")
    except Exception:
        if backup_client:
            try:
                entity = await asyncio.wait_for(
                    backup_client.get_entity(ref), timeout=15)
                cache_store[cache_key] = (entity,
                                          now + timedelta(seconds=ENTITY_CACHE_TTL))
                return entity
            except Exception:
                pass
        raise


async def safe_get_owner_entity():
    global RESOLVE_FLOOD_UNTIL
    now = datetime.now()
    if RESOLVE_FLOOD_UNTIL and now < RESOLVE_FLOOD_UNTIL:
        raise Exception("Flood")
    cached = OWNER_ENTITY_CACHE.get("entity")
    exp = OWNER_ENTITY_CACHE.get("expires_at")
    if cached and exp and now < exp:
        return cached
    owner_uname = get_owner_username()
    entity = None
    try:
        entity = await asyncio.wait_for(admin_client.get_entity(owner_uname),
                                        timeout=15)
    except Exception:
        if backup_client:
            try:
                entity = await asyncio.wait_for(
                    backup_client.get_entity(owner_uname), timeout=15)
            except Exception:
                pass
    if not entity:
        raise Exception("Could not resolve owner")
    OWNER_ENTITY_CACHE["entity"] = entity
    OWNER_ENTITY_CACHE["expires_at"] = now + timedelta(seconds=OWNER_CACHE_TTL)
    return entity


def clear_owner_cache():
    OWNER_ENTITY_CACHE["entity"] = None
    OWNER_ENTITY_CACHE["expires_at"] = None


# ══════════════════════ END OF PART 5 ══════════════════════
D("✅ Part 5 loaded — Languages + Help + Bot API + Helpers", "ok")
# ══════════════════════ BOT POOL (DUAL-SERVER AWARE) ══════════════════════
def get_pool(server):
    """Get pool dict for a server"""
    return PAID_POOL if server == "paid" else FREE_POOL


def get_flood_map(server):
    """Get flood dict for a server"""
    return PAID_FLOOD_UNTIL if server == "paid" else FREE_FLOOD_UNTIL


def is_bot_flooded(token, server=None):
    """Check if bot is in flood wait (server-aware)"""
    if server:
        flood_map = get_flood_map(server)
        u = flood_map.get(token)
    else:
        u = FLOOD_UNTIL.get(token)
        if u is None:
            u = FREE_FLOOD_UNTIL.get(token) or PAID_FLOOD_UNTIL.get(token)
    if u is None:
        return False
    if datetime.now() >= u:
        if server:
            get_flood_map(server).pop(token, None)
        else:
            FLOOD_UNTIL.pop(token, None)
            FREE_FLOOD_UNTIL.pop(token, None)
            PAID_FLOOD_UNTIL.pop(token, None)
        return False
    return True


def mark_bot_flooded(token, sec, server=None):
    """Mark bot as flooded"""
    until = datetime.now() + timedelta(seconds=sec)
    FLOOD_UNTIL[token] = until
    if server == "paid":
        PAID_FLOOD_UNTIL[token] = until
    elif server == "free":
        FREE_FLOOD_UNTIL[token] = until


def cleanup_bot_pool():
    """Remove stale bots from both pools"""
    now = datetime.now()
    ft = now - timedelta(minutes=BOT_BUSY_TIMEOUT + 1)
    cleaned = 0

    for pool in (FREE_POOL, PAID_POOL):
        stale = []
        for tok, info in list(pool.items()):
            if not isinstance(info, dict):
                stale.append(tok)
                continue
            bu = info.get("busy_until")
            lu = info.get("last_used")
            if bu and bu < now:
                stale.append(tok)
                continue
            if lu and lu < ft:
                stale.append(tok)
                continue
        for tok in stale:
            pool.pop(tok, None)
            cleaned += 1

    # Cleanup floods
    for fm in (FLOOD_UNTIL, FREE_FLOOD_UNTIL, PAID_FLOOD_UNTIL):
        for tok in list(fm.keys()):
            if fm[tok] < now:
                fm.pop(tok, None)

    return cleaned


async def acquire_bots(count, uid, server):
    """
    Acquire N free bots from specified server pool.
    Returns (list_of_(token, username), wait_sec)
    """
    async with BOT_POOL_LOCK:
        cleanup_bot_pool()
        bots = db_list_bots(server=server)
        pool = get_pool(server)
        flood_map = get_flood_map(server)
        now = datetime.now()
        free = []

        for tok, uname, bid, added in bots:
            if is_permanent_admin(uname):
                continue
            if is_bot_flooded(tok, server):
                continue
            info = pool.get(tok)
            bu = info.get("busy_until") if isinstance(info, dict) else None
            if bu is None or now >= bu:
                free.append((tok, uname))
            if len(free) >= count:
                break

        if free:
            for tok, uname in free:
                pool[tok] = {
                    "username": uname,
                    "busy_until": now + timedelta(minutes=BOT_BUSY_TIMEOUT),
                    "last_used": now,
                }
            return free, 0
        return None, 30


async def release_bots(bot_list, server):
    """Release bots back to pool"""
    async with BOT_POOL_LOCK:
        now = datetime.now()
        pool = get_pool(server)
        for tok, uname in bot_list:
            info = pool.get(tok)
            if info:
                info["busy_until"] = now
                info["last_used"] = now


def get_pool_status(server=None):
    """Get detailed pool status for one or both servers"""
    now = datetime.now()
    result = {}

    servers_to_check = [server] if server else ["free", "paid"]

    for sv in servers_to_check:
        all_bots = db_list_bots(server=sv)
        pool = get_pool(sv)
        flood_map = get_flood_map(sv)
        total = len(all_bots)
        perm = sum(1 for b in all_bots if is_permanent_admin(b[1]))
        flooded = sum(1 for t in flood_map if flood_map[t] > now)
        busy = 0
        free = 0
        for tok, uname, bid, added in all_bots:
            if is_permanent_admin(uname):
                continue
            if tok in flood_map and flood_map[tok] > now:
                continue
            info = pool.get(tok)
            if isinstance(info, dict) and info.get("busy_until") and \
               info["busy_until"] > now:
                busy += 1
            else:
                free += 1
        result[sv] = {
            "total": total, "permanent": perm, "visible": total - perm,
            "free": free, "busy": busy, "flooded": flooded
        }

    if server:
        return result[server]
    return result


def reset_bot_pool(server=None):
    """Reset pool(s) — clear busy + flood"""
    if server == "free":
        op = len(FREE_POOL)
        of = len(FREE_FLOOD_UNTIL)
        FREE_POOL.clear()
        FREE_FLOOD_UNTIL.clear()
        return op, of
    if server == "paid":
        op = len(PAID_POOL)
        of = len(PAID_FLOOD_UNTIL)
        PAID_POOL.clear()
        PAID_FLOOD_UNTIL.clear()
        return op, of
    # Reset both
    op = len(FREE_POOL) + len(PAID_POOL)
    of = len(FREE_FLOOD_UNTIL) + len(PAID_FLOOD_UNTIL)
    FREE_POOL.clear()
    PAID_POOL.clear()
    FREE_FLOOD_UNTIL.clear()
    PAID_FLOOD_UNTIL.clear()
    FLOOD_UNTIL.clear()
    BOT_POOL.clear()
    return op, of


# ══════════════════════ REAL ACCOUNTS ══════════════════════
def discover_session_files():
    if not os.path.isdir(SESSIONS_DIR):
        return []
    try:
        return sorted([
            f for f in os.listdir(SESSIONS_DIR)
            if f.endswith(".session")
        ])
    except Exception:
        return []


def is_real_flooded(sf):
    u = REAL_FLOOD_UNTIL.get(sf)
    if u is None:
        return False
    if datetime.now() >= u:
        REAL_FLOOD_UNTIL.pop(sf, None)
        return False
    return True


def mark_real_flooded(sf, sec):
    REAL_FLOOD_UNTIL[sf] = datetime.now() + timedelta(seconds=sec)


def real_count_available():
    return sum(1 for f in discover_session_files()
               if not is_real_flooded(f))


def real_count_flooded():
    return sum(1 for f in discover_session_files() if is_real_flooded(f))


def real_get_status():
    files = discover_session_files()
    flooded = real_count_flooded()
    busy = len(REAL_CLIENTS)
    return {
        "total": len(files),
        "available": len(files) - flooded,
        "flooded": flooded,
        "loaded": busy,
        "max_clients": MAX_CLIENTS,
        "files": files
    }


async def get_real_client(sf):
    async with REAL_CLIENT_LOCK:
        if len(REAL_CLIENTS) >= MAX_CLIENTS:
            to_remove = list(REAL_CLIENTS.keys())[
                :max(1, len(REAL_CLIENTS) - MAX_CLIENTS + 1)]
            for k in to_remove:
                try:
                    await REAL_CLIENTS[k].disconnect()
                except Exception:
                    pass
                REAL_CLIENTS.pop(k, None)
        if sf in REAL_CLIENTS:
            c = REAL_CLIENTS[sf]
            try:
                if c.is_connected():
                    return c
            except Exception:
                pass
            try:
                await c.disconnect()
            except Exception:
                pass
            REAL_CLIENTS.pop(sf, None)
        path = os.path.join(SESSIONS_DIR, sf.replace(".session", ""))
        if not os.path.exists(path + ".session"):
            return None
        try:
            client = TelegramClient(path, API_ID, API_HASH)
            await asyncio.wait_for(client.connect(), timeout=25)
            if not await client.is_user_authorized():
                await client.disconnect()
                return None
            REAL_CLIENTS[sf] = client
            return client
        except Exception as e:
            D(f"Real login fail {sf}: {str(e)[:80]}", "warn")
            return None


async def real_send_reaction(sf, chat_ref, msg_id, emoji):
    if is_real_flooded(sf):
        return False, "flooded", 0
    client = await get_real_client(sf)
    if not client:
        return False, "login_failed", 0
    try:
        entity = await asyncio.wait_for(client.get_entity(chat_ref), timeout=20)
        await asyncio.wait_for(
            client(SendReactionRequest(
                peer=entity, msg_id=msg_id,
                reaction=[ReactionEmoji(emoticon=emoji)])),
            timeout=20)
        return True, "", 0
    except FloodWaitError as e:
        return False, "flood", e.seconds
    except Exception as e:
        return False, str(e)[:100], 0


async def send_reactions_real(chat_ref, msg_id, count,
                               emoji_pool=None, on_progress=None):
    files = discover_session_files()
    if not files:
        return {"ok": 0, "fail": 0, "flooded": 0, "total": 0}
    available = [f for f in files if not is_real_flooded(f)]
    if not available:
        return {"ok": 0, "fail": 0, "flooded": 0, "total": 0}
    random.shuffle(available)
    senders = available[:min(count, len(available))]
    if emoji_pool:
        valid = [e for e in emoji_pool if e in ALL_REACTIONS]
        emojis = valid if valid else DEFAULT_REACTIONS
    else:
        emojis = DEFAULT_REACTIONS + ["🥰", "😍", "💯", "🎉", "😎", "👏"]
    ok = fail = flooded = 0
    total = len(senders)
    for i, sf in enumerate(senders, 1):
        emoji = random.choice(emojis)
        success, err, wait = await real_send_reaction(sf, chat_ref, msg_id, emoji)
        if success:
            ok += 1
        elif wait > 0:
            flooded += 1
            mark_real_flooded(sf, wait + 10)
        else:
            fail += 1
        if on_progress:
            try:
                await on_progress(i, total, ok)
            except Exception:
                pass
        await asyncio.sleep(REAL_COOLDOWN)
    return {"ok": ok, "fail": fail, "flooded": flooded, "total": total}


async def close_all_real_clients():
    for sf, c in list(REAL_CLIENTS.items()):
        try:
            await c.disconnect()
        except Exception:
            pass
    REAL_CLIENTS.clear()


# ══════════════════════ JOIN / APPROVAL CHECKS ══════════════════════
async def is_joined(uid):
    if not feat_force_join() or OWNER_IS(uid):
        return True
    channels = db_list_force_channels(only_active=True)
    if not channels:
        return True
    for fc in channels:
        try:
            await asyncio.wait_for(
                bot.get_permissions(fc[1], uid), timeout=8)
            continue
        except Exception:
            pass
        try:
            await asyncio.wait_for(
                admin_client(GetParticipantRequest(
                    channel=fc[1], participant=uid)), timeout=8)
            continue
        except Exception:
            return False
    return True


def is_approved(uid):
    if OWNER_IS(uid):
        return True
    if db_is_banned(uid):
        return False
    return db_approval_status(uid) == "approved"


# ══════════════════════ ADMIN CHECKS ══════════════════════
async def is_admin_in(entity, user_id):
    try:
        perms = await asyncio.wait_for(
            admin_client.get_permissions(entity, user_id), timeout=10)
        if perms is None:
            return False
        return getattr(perms, 'is_admin', False)
    except Exception:
        return False


async def check_owner_admin(entity):
    try:
        oe = await safe_get_owner_entity()
        return await is_admin_in(entity, oe.id)
    except Exception:
        return False


async def get_current_admin_bots(entity):
    admins = []
    try:
        result = await asyncio.wait_for(
            admin_client(GetParticipantsRequest(
                channel=entity,
                filter=ChannelParticipantsAdmins(),
                offset=0, limit=200, hash=0)),
            timeout=20)
        for u in result.users:
            if getattr(u, 'bot', False) and u.username:
                admins.append((u.username, u.id))
    except Exception:
        pass
    return admins


async def get_our_admin_bots(entity, server=None):
    """
    Get ONLY our reaction bots that are admin (server-aware).
    Skips permanent + original admins.
    """
    all_admins = await get_current_admin_bots(entity)
    if not all_admins:
        return []
    if server:
        db_bots = db_list_bots(server=server)
    else:
        db_bots = db_list_bots()
    uname_to_token = {u: t for t, u, b, a in db_bots}
    result = []
    for uname, uid in all_admins:
        if is_permanent_admin(uname):
            continue
        tok = uname_to_token.get(uname)
        if not tok:
            continue
        result.append((tok, uname, uid))
    return result


async def get_non_our_admin_bots(entity):
    """Original admins (never touch)"""
    all_admins = await get_current_admin_bots(entity)
    if not all_admins:
        return []
    db_bots = db_list_bots()
    our_usernames = {u for t, u, b, a in db_bots}
    result = []
    for uname, uid in all_admins:
        if is_permanent_admin(uname):
            continue
        if uname not in our_usernames:
            result.append((uname, uid))
    return result


# ══════════════════════ MAKE / REMOVE ADMIN ══════════════════════
async def make_bot_admin(entity, bot_entity, atype):
    if atype == "channel":
        rights = ChatAdminRights(
            change_info=False, post_messages=True, edit_messages=False,
            delete_messages=True, ban_users=False, invite_users=False,
            pin_messages=False, add_admins=False, anonymous=False,
            manage_call=False, other=False)
    else:
        rights = ChatAdminRights(
            change_info=True, post_messages=True, edit_messages=False,
            delete_messages=True, ban_users=True, invite_users=True,
            pin_messages=True, add_admins=False, anonymous=False,
            manage_call=True, other=False)
    try:
        await asyncio.wait_for(
            admin_client(EditAdminRequest(
                channel=entity, user_id=bot_entity,
                admin_rights=rights, rank="")),
            timeout=15)
        return True, "promoted"
    except Exception as e:
        m = str(e).lower()
        if "already" in m:
            return True, "already_admin"
        if "too many admins" in m:
            return False, "too_many_admins"
        return False, f"admin: {str(e)[:60]}"


async def remove_admin_rights(entity, user_id, username):
    if is_permanent_admin(username):
        return True
    empty = ChatAdminRights(
        change_info=False, post_messages=False, edit_messages=False,
        delete_messages=False, ban_users=False, invite_users=False,
        pin_messages=False, add_admins=False, anonymous=False,
        manage_call=False, other=False)
    try:
        await asyncio.wait_for(
            admin_client(EditAdminRequest(
                channel=entity, user_id=user_id,
                admin_rights=empty, rank="")),
            timeout=15)
        return True
    except Exception as e:
        m = str(e).lower()
        if "not admin" in m or "participant" in m:
            return True
        return False


async def remove_admin_by_username(entity, username):
    if is_permanent_admin(username):
        return False
    bot_row = db_get_bot_by_username(username)
    if not bot_row:
        return False
    try:
        be = await safe_get_entity(
            username, cache_key=f"bot:{username}",
            cache_store=BOT_ENTITY_CACHE)
        return await remove_admin_rights(entity, be.id, username)
    except Exception:
        return False


# ══════════════════════ ADD ONE BOT ══════════════════════
async def add_one_bot(entity, bot_token, atype, cache_key):
    info = bot_get_me(bot_token)
    if not info:
        return False, "invalid"
    username = info["username"]
    try:
        be = await safe_get_entity(
            username, cache_key=f"bot:{username}",
            cache_store=BOT_ENTITY_CACHE)
    except Exception as e:
        return False, f"resolve: {str(e)[:40]}"

    if atype == "channel":
        if await is_admin_in(entity, be.id):
            return True, "already_admin"
        return await make_bot_admin(entity, be, "channel")

    try:
        await asyncio.wait_for(
            admin_client(GetParticipantRequest(
                channel=entity, participant=be.id)),
            timeout=10)
    except UserNotParticipantError:
        try:
            await asyncio.wait_for(
                admin_client(InviteToChannelRequest(
                    channel=entity, users=[be])),
                timeout=15)
            await asyncio.sleep(2)
        except Exception:
            try:
                await asyncio.wait_for(
                    admin_client(AddChatUserRequest(
                        chat_id=entity.id, user_id=be, fwd_limit=10)),
                    timeout=15)
                await asyncio.sleep(2)
            except Exception as e:
                return False, f"invite: {str(e)[:40]}"
    except Exception:
        pass

    if await is_admin_in(entity, be.id):
        return True, "already_admin"
    return await make_bot_admin(entity, be, "group")


# ══════════════════════ ENSURE OWNER ADMIN ══════════════════════
async def ensure_owner_admin(entity, cache_key):
    if cache_key and ADMIN_CACHE.get(cache_key, {}).get("owner_done"):
        return True, "cached"
    try:
        oe = await safe_get_owner_entity()
        oid = oe.id
    except Exception as e:
        return False, f"owner: {str(e)[:40]}"
    if await is_admin_in(entity, oid):
        if cache_key:
            ADMIN_CACHE.setdefault(cache_key, {})["owner_done"] = True
        return True, "already"
    rights = ChatAdminRights(
        change_info=True, post_messages=True, edit_messages=True,
        delete_messages=True, ban_users=True, invite_users=True,
        pin_messages=True, add_admins=True, anonymous=False,
        manage_call=True, other=True)
    try:
        fresh = await safe_get_owner_entity()
        await asyncio.wait_for(
            admin_client(EditAdminRequest(
                channel=entity, user_id=fresh,
                admin_rights=rights, rank="")),
            timeout=15)
        if cache_key:
            ADMIN_CACHE.setdefault(cache_key, {})["owner_done"] = True
        return True, "promoted"
    except Exception as e:
        m = str(e).lower()
        if "already" in m:
            return True, "already"
        return False, f"owner: {str(e)[:50]}"


# ══════════════════════ SYNC BOTS (STARTUP) ══════════════════════
def sync_bots():
    """
    Sync bots from config into DB with server assignment.
    Uses PART 1 dedupe lists.
    """
    existing = {r[0] for r in db_list_bots()}
    added_free = 0
    added_paid = 0
    skipped = 0

    # Free server
    for tok in FREE_SERVER_TOKENS:
        if tok in existing:
            skipped += 1
            continue
        info = bot_get_me(tok)
        if info and db_add_bot(tok, info["username"], info["id"],
                               server="free"):
            added_free += 1
            existing.add(tok)

    # Paid server
    for tok in PAID_SERVER_TOKENS:
        if tok in existing:
            skipped += 1
            continue
        info = bot_get_me(tok)
        if info and db_add_bot(tok, info["username"], info["id"],
                               server="paid"):
            added_paid += 1
            existing.add(tok)

    D(f"Bot sync: +{added_free} free, +{added_paid} paid, "
      f"{skipped} skipped (existing)", "ok")
    return added_free + added_paid


# ══════════════════════ END OF PART 6 ══════════════════════
D("✅ Part 6 loaded — Dual-Server Bot Pool + Real Accounts + Admin Checks", "ok")
# ══════════════════════ FAILED BOT TRACKER ══════════════════════
def track_failed_bot(task_key, bot_username, reason=""):
    """Track failed bot per task"""
    if task_key not in FAILED_BOTS_TRACKER:
        FAILED_BOTS_TRACKER[task_key] = {}
    if bot_username not in FAILED_BOTS_TRACKER[task_key]:
        FAILED_BOTS_TRACKER[task_key][bot_username] = {
            "fail_count": 0, "last_reason": "", "added_at": time.time()
        }
    FAILED_BOTS_TRACKER[task_key][bot_username]["fail_count"] += 1
    FAILED_BOTS_TRACKER[task_key][bot_username]["last_reason"] = reason[:80]


def get_failed_bots(task_key):
    return FAILED_BOTS_TRACKER.get(task_key, {})


def is_bot_failed(task_key, bot_username):
    return bot_username in get_failed_bots(task_key)


def clear_failed_bots(task_key):
    FAILED_BOTS_TRACKER.pop(task_key, None)


# ══════════════════════ SINGLE REACTION WITH FALLBACK ══════════════════════
def send_reaction_with_fallback(token, chat_id, msg_id, primary_emoji,
                                 server=None):
    """
    🔥 Send reaction with fallback chain.
    Primary → ❤️ → 👍 → 🔥 → 🥰 → 🎉 → 💯 → 😍 → 👏
    Returns (ok, used_emoji, err)
    """
    # Try primary
    ok, desc, retry = bot_reaction(token, chat_id, msg_id, primary_emoji)
    if ok:
        return True, primary_emoji, ""
    if retry > 0:
        return False, primary_emoji, f"flood:{retry}"
    # Fallback chain
    if feat_fallback():
        for fb_emoji in FALLBACK_REACTIONS:
            if fb_emoji == primary_emoji:
                continue
            ok, desc, retry = bot_reaction(token, chat_id, msg_id, fb_emoji)
            if ok:
                D(f"🩹 Fallback: {fb_emoji} for {primary_emoji}", "fallback")
                return True, fb_emoji, ""
            if retry > 0:
                return False, primary_emoji, f"flood:{retry}"
    return False, primary_emoji, (desc[:80] if desc else "unknown")


# ══════════════════════ SEND BATCH REACTIONS (SERVER-AWARE) ══════════════════════
async def send_batch_reactions(chat_id, msg_id, bot_batch, chat_title,
                                post_link, uid, server,
                                emoji_mode="default",
                                custom_emojis=None, task_key=None,
                                on_progress=None):
    """
    🔥 Send reactions from a batch with fallback + tracking.
    Returns (ok_count, skip_count, failed_bots_list)
    """
    if not bot_batch:
        return 0, 0, []

    api_chat_id = to_bot_api_chat_id(chat_id)

    # Emoji pool
    if emoji_mode == "custom" and custom_emojis:
        pool = [e for e in custom_emojis if e in ALL_REACTIONS]
        if not pool:
            pool = ALL_REACTIONS.copy()
    else:
        pool = ALL_REACTIONS.copy()
    random.shuffle(pool)

    ok = 0
    skip = 0
    failed_bots = []
    total = len(bot_batch)

    for idx, (token, uname) in enumerate(bot_batch, 1):
        # Skip flooded
        if is_bot_flooded(token, server):
            skip += 1
            continue
        # Skip already-failed in this task
        if task_key and is_bot_failed(task_key, uname):
            skip += 1
            continue

        emoji = pool.pop(0) if pool else random.choice(DEFAULT_REACTIONS)

        # 🔥 Send with fallback
        ok_f, used_emoji, err = send_reaction_with_fallback(
            token, api_chat_id, msg_id, emoji, server=server)

        if ok_f:
            ok += 1
            try:
                db_save_reaction(uid, chat_title, chat_id, post_link,
                                 msg_id, used_emoji, uname, "ok",
                                 method="bot", server=server)
                stats_bump(uid, ok=True)
            except Exception:
                pass
        else:
            if "flood:" in err:
                try:
                    wait = int(err.split(":")[1])
                except Exception:
                    wait = 30
                mark_bot_flooded(token, wait, server)
                skip += 1
            else:
                skip += 1
                failed_bots.append((token, uname))
                if task_key:
                    track_failed_bot(task_key, uname, err)
                try:
                    db_save_reaction(uid, chat_title, chat_id, post_link,
                                     msg_id, emoji, uname, "fail",
                                     method="bot", server=server)
                    stats_bump(uid, ok=False)
                except Exception:
                    pass

        if on_progress and (idx % 5 == 0 or idx == total):
            try:
                await on_progress(idx, total, ok)
            except Exception:
                pass

        await asyncio.sleep(0.6)

    return ok, skip, failed_bots


# ══════════════════════ MAIN SMART ENGINE (SERVER-AWARE) ══════════════════════
async def process_reactions_rotating(event, uid, chat_link, post_link,
                                      count, emoji_mode="default",
                                      custom_emojis=None,
                                      is_auto_watch=False):
    """
    🔥 SMART REACTION ENGINE v3 — Dual Server

    Phases:
    1. Existing our-admin-bots (server-specific)
    2. Adaptive batch add
    3. React from batch (with fallback)
    4. Remove our bots (SAFE)
    5. Failed bots retry
    """
    global TASK_RUNNING, TASK_OWNER_UID

    # ═════ Determine server ═════
    server = get_user_server(uid)
    D(f"[ENGINE] User {uid} → server: {server}", "server")

    # ═════ Parse links ═════
    chat_ref, invite_hash = parse_channel_link(chat_link)
    post_ref, msg_id = parse_post_link(post_link)

    if not msg_id:
        if event:
            await safe_edit(event, "❌ Invalid post link",
                            buttons=kb_back(uid))
        return 0

    user_state = USER_STATES.get(uid, {})
    chat_type = user_state.get("chat_type", "channel")

    total_bots = db_count_bots(server=server)
    want = min(count, total_bots)

    if want <= 0:
        if event:
            await safe_edit(event,
                            f"❌ No bots available on {get_server_label(server)} server",
                            buttons=kb_back(uid))
        return 0

    if event:
        try:
            await event.edit(
                f"⏳ **Starting {get_server_label(server)} engine...**\n\n"
                f"🎯 Target: **{want}** reactions\n"
                f"🤖 Available bots: **{total_bots}**")
        except Exception:
            pass

    # ═════ Resolve chat ═════
    try:
        if invite_hash and not post_ref:
            try:
                await admin_client(ImportChatInviteRequest(invite_hash))
            except Exception:
                pass
            entity = await safe_get_entity(
                f"https://t.me/+{invite_hash}",
                cache_key=f"chat:{invite_hash}")
        else:
            target_ref = post_ref or chat_ref
            entity = await safe_get_entity(
                target_ref, cache_key=f"chat:{target_ref}")
    except Exception as e:
        if event:
            await safe_edit(event, f"❌ Resolve failed:\n{str(e)[:100]}",
                            buttons=kb_back(uid))
        return 0

    chat_title = getattr(entity, "title", "Unknown")
    real_id = entity.id
    actual_type = ("channel" if is_channel(entity)
                   else ("group" if is_group(entity) else chat_type))

    # ═════ Verify post ═════
    try:
        post_msg = await asyncio.wait_for(
            admin_client.get_messages(entity, ids=msg_id), timeout=15)
        if post_msg is None:
            if event:
                await safe_edit(event, f"❌ Post #{msg_id} not found",
                                buttons=kb_back(uid))
            return 0
    except Exception:
        pass

    # ═════ Owner admin check ═════
    if not is_auto_watch and ADMIN_CHECK_ENABLED and not OWNER_IS(uid):
        if event:
            try:
                await event.edit("🔍 **Checking owner admin...**")
            except Exception:
                pass
        owner_is_admin = await check_owner_admin(entity)
        if not owner_is_admin:
            if event:
                await safe_edit(event,
                                get_admin_needed_message(chat_title, uid),
                                buttons=kb_owner_needed(uid))
            if uid in USER_STATES:
                USER_STATES[uid] = {}
            return 0

    # ═════ Ensure owner admin ═════
    cache_key = str(real_id)
    ok_owner, reason_owner = await ensure_owner_admin(entity, cache_key)
    if not ok_owner:
        if event:
            await safe_edit(event, f"❌ Owner setup failed: {reason_owner}",
                            buttons=kb_back(uid))
        return 0

    # ═════ Task key ═════
    task_key = f"{uid}:{real_id}:{msg_id}:{server}"
    clear_failed_bots(task_key)

    # ═════ Main loop ═════
    reactions_done = 0
    cycle = 0
    failed_batches = 0
    cycle_log = []
    all_failed_bots = []
    used_bots = set()

    while reactions_done < want and cycle < MAX_CYCLES:
        cycle += 1
        remaining = want - reactions_done

        if event:
            bar = progress_bar(reactions_done, want)
            await safe_edit(
                event,
                f"🎬 **Cycle {cycle}/{MAX_CYCLES}** {get_server_label(server)}\n"
                f"{DIV}\n\n"
                f"📊 `{bar}` {reactions_done}/{want}\n"
                f"⏳ Remaining: **{remaining}**\n"
                f"❌ Failed: **{len(all_failed_bots)}**")

        # ══════════════════════════════════════════
        # PHASE 1: Existing our-admin-bots
        # ══════════════════════════════════════════
        our_admins = await get_our_admin_bots(entity, server=server)
        phase1_bots = []
        for tok, uname, bid in our_admins:
            if is_bot_flooded(tok, server):
                continue
            if uname in used_bots:
                continue
            if is_bot_failed(task_key, uname):
                continue
            phase1_bots.append((tok, uname))
        phase1_bots = phase1_bots[:remaining]

        if phase1_bots and reactions_done < want:
            if event:
                await safe_edit(
                    event,
                    f"💫 **Phase 1** — {len(phase1_bots)} existing admins\n"
                    f"📊 {progress_bar(reactions_done, want)} "
                    f"{reactions_done}/{want}")

            pool = get_pool(server)
            for tok, uname in phase1_bots:
                pool.setdefault(tok, {})
                pool[tok]["busy_until"] = (
                    datetime.now() + timedelta(minutes=BOT_BUSY_TIMEOUT))
                pool[tok]["username"] = uname
                used_bots.add(uname)

            async def on_p1_prog(i, t, ok):
                if event and (i % 10 == 0 or i == t):
                    try:
                        bar = progress_bar(reactions_done + ok, want)
                        await event.edit(
                            f"💫 **Phase 1** — Reacting\n"
                            f"📊 `{bar}` {reactions_done + ok}/{want}")
                    except Exception:
                        pass

            ok1, skip1, fail1 = await send_batch_reactions(
                real_id, msg_id, phase1_bots, chat_title, post_link,
                uid, server,
                emoji_mode=emoji_mode, custom_emojis=custom_emojis,
                task_key=task_key, on_progress=on_p1_prog)

            reactions_done += ok1
            all_failed_bots.extend(fail1)

            # Remove our bots
            for tok, uname in phase1_bots:
                try:
                    await asyncio.wait_for(
                        remove_admin_by_username(entity, uname),
                        timeout=PER_BOT_TIMEOUT)
                    await asyncio.sleep(0.3)
                except Exception:
                    pass
            await release_bots(phase1_bots, server)

            if reactions_done >= want:
                break

        # ══════════════════════════════════════════
        # PHASE 2: Add new batch (adaptive)
        # ══════════════════════════════════════════
        remaining = want - reactions_done

        if cycle <= 2:
            batch_size = min(BATCH_SIZE, remaining + 5)
        elif cycle <= 4:
            batch_size = min(25, remaining + 3)
        else:
            batch_size = min(10, remaining + 2)

        if event:
            await safe_edit(
                event,
                f"🤖 **Phase 2** — Adding batch of {batch_size} "
                f"({get_server_label(server)})\n"
                f"📊 {progress_bar(reactions_done, want)} "
                f"{reactions_done}/{want}")

        acquired, wait_sec = await acquire_bots(batch_size, uid, server)
        if acquired is None:
            await asyncio.sleep(wait_sec)
            acquired, wait_sec = await acquire_bots(batch_size, uid, server)
        if acquired is None:
            failed_batches += 1
            if event:
                await safe_edit(event, "⚠️ No free bots. Retrying...",
                                buttons=kb_back(uid))
            await asyncio.sleep(5)
            if failed_batches >= MAX_FAILED_BATCHES:
                break
            continue

        to_add = []
        for tok, uname in acquired:
            if uname in used_bots:
                continue
            if is_bot_failed(task_key, uname):
                continue
            to_add.append((tok, uname))
        to_add = to_add[:remaining]

        if not to_add:
            await release_bots(acquired, server)
            failed_batches += 1
            if failed_batches >= MAX_FAILED_BATCHES:
                break
            continue

        # Add to admin
        promoted = []
        for tok, uname in to_add:
            try:
                ok, rmsg = await asyncio.wait_for(
                    add_one_bot(entity, tok, actual_type, cache_key),
                    timeout=PER_BOT_TIMEOUT)
                if ok:
                    promoted.append((tok, uname))
                    used_bots.add(uname)
                elif rmsg == "too_many_admins":
                    D(f"[CYCLE] Chat full — {len(promoted)} added", "warn")
                    break
            except Exception:
                pass
            await asyncio.sleep(0.6)

        non_promoted = [(t, u) for t, u in acquired
                        if (t, u) not in promoted]
        if non_promoted:
            await release_bots(non_promoted, server)

        if not promoted:
            failed_batches += 1
            if failed_batches >= MAX_FAILED_BATCHES:
                break
            continue

        # ══════════════════════════════════════════
        # PHASE 3: React from new batch
        # ══════════════════════════════════════════
        if event:
            await safe_edit(
                event,
                f"💫 **Phase 3** — Reacting {len(promoted)} bots\n"
                f"📊 {progress_bar(reactions_done, want)} "
                f"{reactions_done}/{want}")

        async def on_p3_prog(i, t, ok):
            if event and (i % 5 == 0 or i == t):
                try:
                    bar = progress_bar(reactions_done + ok, want)
                    await event.edit(
                        f"💫 **Phase 3** — Cycle {cycle}\n"
                        f"📊 `{bar}` {reactions_done + ok}/{want}")
                except Exception:
                    pass

        ok2, skip2, fail2 = await send_batch_reactions(
            real_id, msg_id, promoted, chat_title, post_link,
            uid, server,
            emoji_mode=emoji_mode, custom_emojis=custom_emojis,
            task_key=task_key, on_progress=on_p3_prog)

        reactions_done += ok2
        all_failed_bots.extend(fail2)

        # ══════════════════════════════════════════
        # PHASE 4: Remove our bots (SAFE)
        # ══════════════════════════════════════════
        for tok, uname in promoted:
            try:
                await asyncio.wait_for(
                    remove_admin_by_username(entity, uname),
                    timeout=PER_BOT_TIMEOUT)
                await asyncio.sleep(0.3)
            except Exception:
                pass

        await release_bots(promoted, server)

        if ok2 > 0:
            failed_batches = 0
        else:
            failed_batches += 1
            if failed_batches >= MAX_FAILED_BATCHES:
                D(f"[CYCLE] Too many failed batches — stopping", "warn")
                break

        cycle_log.append((cycle, ok2))
        D(f"[CYCLE {cycle}] +{ok2} (total {reactions_done}/{want}) "
          f"server={server}", "cycle")

    # ══════════════════════════════════════════
    # PHASE 5: Failed bots retry
    # ══════════════════════════════════════════
    remaining = want - reactions_done
    if remaining > 0 and all_failed_bots and FAILED_BOT_RETRY:
        if event:
            await safe_edit(
                event,
                f"🔄 **Phase 5** — Retrying failed bots\n"
                f"🎯 Need: **{remaining}** more")
        failed_tokens = list(set(all_failed_bots))[:remaining]
        if failed_tokens:
            pool = get_pool(server)
            for tok, uname in failed_tokens:
                pool.setdefault(tok, {})
                pool[tok]["busy_until"] = (
                    datetime.now() + timedelta(minutes=BOT_BUSY_TIMEOUT))
            re_added = []
            for tok, uname in failed_tokens:
                try:
                    ok, rmsg = await asyncio.wait_for(
                        add_one_bot(entity, tok, actual_type, cache_key),
                        timeout=PER_BOT_TIMEOUT)
                    if ok:
                        re_added.append((tok, uname))
                except Exception:
                    pass
                await asyncio.sleep(0.5)
            if re_added:
                ok5, _, _ = await send_batch_reactions(
                    real_id, msg_id, re_added, chat_title, post_link,
                    uid, server,
                    emoji_mode=emoji_mode, custom_emojis=custom_emojis,
                    task_key=task_key)
                reactions_done += ok5
                for tok, uname in re_added:
                    try:
                        await asyncio.wait_for(
                            remove_admin_by_username(entity, uname),
                            timeout=PER_BOT_TIMEOUT)
                    except Exception:
                        pass
                await release_bots(re_added, server)

    # ══════════════════════════════════════════
    # FINAL REPORT
    # ══════════════════════════════════════════
    if event:
        bar = progress_bar(reactions_done, max(want, reactions_done, 1))
        cycles_txt = "".join(
            f"   🎬 Cycle {cn}: **+{okc}**\n"
            for cn, okc in cycle_log[:15])
        if len(cycle_log) > 15:
            cycles_txt += f"   ... +{len(cycle_log) - 15} more\n"

        failed_count = len(set(all_failed_bots))
        success_pct = int(reactions_done / max(1, want) * 100)

        txt = (
            f"🎉 **COMPLETE!** 🎉\n{STAR_LINE}\n\n"
            f"📢 **{chat_title}**\n"
            f"📩 Post: **#{msg_id}**\n"
            f"🖥️ Server: **{get_server_label(server)}**\n\n"
            f"{DIV}\n"
            f"🎯 Requested: **{count}**\n"
            f"✅ Success: **{reactions_done}**\n"
            f"📈 Rate: **{success_pct}%**\n"
            f"🔁 Cycles: **{cycle}**\n"
            f"❌ Failed bots: **{failed_count}**\n"
            f"{DIV}\n\n"
            f"🚀 **{bar}** {reactions_done}/{count}")

        if cycles_txt:
            txt += f"\n\n**Details:**\n{cycles_txt}"

        if reactions_done < count:
            txt += (f"\n\n⚠️ **Note:** Only {reactions_done} "
                    f"reactions sent. Try again later.")
        else:
            txt += f"\n\n{SPARKLE} Full target achieved! {SPARKLE}"

        await safe_edit(event, txt, buttons=kb_back(uid))

    # ═════ Analytics ═════
    try:
        post_analytics_add(uid, real_id, msg_id, chat_title,
                           reactions_done, count, server=server)
    except Exception:
        pass

    # ═════ Cleanup ═════
    clear_failed_bots(task_key)
    if uid in USER_STATES and event:
        USER_STATES[uid] = {}

    return reactions_done


# ══════════════════════ END OF PART 7 ══════════════════════
D("✅ Part 7 loaded — Smart Reaction Engine (Dual Server)", "ok")
# ══════════════════════ GET ADMIN CHATS ══════════════════════
async def get_admin_chats():
    chats = []
    try:
        me = await admin_client.get_me()
        async for d in admin_client.iter_dialogs():
            e = d.entity
            if not isinstance(e, (Channel, Chat)):
                continue
            try:
                perms = await admin_client.get_permissions(e, me.id)
                if perms and getattr(perms, 'is_admin', False):
                    chats.append({
                        "entity": e, "id": e.id,
                        "title": getattr(e, "title", "Unknown")
                    })
            except Exception:
                continue
    except Exception as e:
        D(f"get_admin_chats: {str(e)[:80]}", "warn")
    return chats


# ══════════════════════ BROADCAST ══════════════════════
async def broadcast_message(text=None, photo_url=None, on_progress=None):
    chats = await get_admin_chats()
    total = len(chats)
    if total == 0:
        return 0, 0, 0
    ok_n = fail_n = 0
    for idx, chat in enumerate(chats, 1):
        api = to_bot_api_chat_id(chat["id"])
        try:
            if photo_url and text:
                ok, _ = bot_send_photo(BOT_TOKEN, api, photo_url, text)
            elif photo_url:
                ok, _ = bot_send_photo(BOT_TOKEN, api, photo_url)
            elif text:
                ok, _ = bot_send_message(BOT_TOKEN, api, text)
            else:
                ok = False
            if ok:
                ok_n += 1
            else:
                fail_n += 1
        except Exception:
            fail_n += 1
        if on_progress and idx % 5 == 0:
            try:
                await on_progress(idx, total, ok_n)
            except Exception:
                pass
        await asyncio.sleep(BROADCAST_DELAY)
    return ok_n, fail_n, total


# ══════════════════════ QUEUE LOOP (SERVER-AWARE) ══════════════════════
async def queue_loop():
    global TASK_RUNNING, TASK_OWNER_UID
    while True:
        try:
            await asyncio.sleep(QUEUE_CHECK_INTERVAL)
            if not feat_queue() or TASK_RUNNING:
                continue
            pending = db_list_queue(status="pending")
            if not pending:
                continue
            now = datetime.now()
            for job in pending:
                (qid, user_id, cl, pl, rc, em, ce, st,
                 status, cr, ex, err, sv) = job
                if st:
                    try:
                        if datetime.strptime(st, "%Y-%m-%d %H:%M:%S") > now:
                            continue
                    except Exception:
                        pass
                TASK_RUNNING = True
                TASK_OWNER_UID = user_id
                try:
                    D(f"[QUEUE] Job #{qid} for {user_id} on {sv}", "queue")
                    ce_list = (ce.split(",") if ce else None)
                    result = await process_reactions_rotating(
                        None, user_id, cl, pl, rc,
                        emoji_mode=em, custom_emojis=ce_list,
                        is_auto_watch=True)
                    db_update_queue(
                        qid, status="done",
                        executed_at=datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"))
                    try:
                        await bot.send_message(
                            user_id,
                            f"✅ **QUEUE DONE**\n"
                            f"📩 Job #{qid}\n"
                            f"💫 Sent: **{result}**")
                    except Exception:
                        pass
                except Exception as e:
                    db_update_queue(
                        qid, status="failed",
                        executed_at=datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"),
                        error=str(e)[:200])
                    D(f"[QUEUE] Job #{qid} failed: {str(e)[:80]}", "fail")
                finally:
                    TASK_RUNNING = False
                    TASK_OWNER_UID = None
        except asyncio.CancelledError:
            return
        except Exception as e:
            D_err(e, "queue_loop")
            await asyncio.sleep(30)


# ══════════════════════ AUTO-RETRY LOOP (SERVER-AWARE) ══════════════════════
async def retry_loop():
    global TASK_RUNNING, TASK_OWNER_UID
    while True:
        try:
            await asyncio.sleep(60)
            if not feat_auto_retry() or TASK_RUNNING:
                continue
            jobs = retry_list_due()
            if not jobs:
                continue
            for job in jobs:
                (rid, user_id, cl, pl, count, em, ce, att, mx,
                 sv) = job
                TASK_RUNNING = True
                TASK_OWNER_UID = user_id
                try:
                    D(f"[RETRY] Job #{rid} attempt {att+1}/{mx}", "rot")
                    ce_list = (ce.split(",") if ce else None)
                    result = await process_reactions_rotating(
                        None, user_id, cl, pl, count,
                        emoji_mode=em, custom_emojis=ce_list,
                        is_auto_watch=True)
                    if result and result > 0:
                        retry_mark(rid, success=True)
                        try:
                            await bot.send_message(
                                user_id,
                                f"✅ **RETRY SUCCESS**\n"
                                f"📩 Job #{rid}\n"
                                f"💫 Sent: {result}")
                        except Exception:
                            pass
                    else:
                        retry_mark(rid, success=False, err="zero sent")
                except Exception as e:
                    retry_mark(rid, success=False, err=str(e)[:200])
                finally:
                    TASK_RUNNING = False
                    TASK_OWNER_UID = None
                    await asyncio.sleep(2)
        except asyncio.CancelledError:
            return
        except Exception as e:
            D_err(e, "retry_loop")
            await asyncio.sleep(30)


# ══════════════════════ WATCHER LOOP (SERVER-AWARE) ══════════════════════
async def watcher_loop():
    global TASK_RUNNING, TASK_OWNER_UID
    while True:
        try:
            await asyncio.sleep(WATCHER_CHECK_INTERVAL)
            if (not AUTO_WATCH_ENABLED or not feat_autowatch()
                    or TASK_RUNNING):
                continue
            watchers = db_list_watchers()
            if not watchers:
                continue
            for w in watchers:
                (wid, user_id, chat_id, ct, cl, cty, rc, em, ces,
                 lpid, act, cr, lr, sv) = w
                if not act or not can_use_feature(user_id, "autowatch"):
                    continue
                try:
                    entity = await safe_get_entity(
                        chat_id, cache_key=f"watch:{chat_id}")
                    msgs = await asyncio.wait_for(
                        admin_client.get_messages(entity, limit=5),
                        timeout=15)
                    if not msgs:
                        continue
                    newest = max(m.id for m in msgs if m.id > 0)
                    if newest <= lpid:
                        continue
                    TASK_RUNNING = True
                    TASK_OWNER_UID = user_id
                    try:
                        ce_list = (ces.split(",") if ces else None)
                        chat_str = str(chat_id).replace("-100", "")
                        pl = f"https://t.me/c/{chat_str}/{newest}"
                        await process_reactions_rotating(
                            None, user_id, cl, pl, rc,
                            emoji_mode=em, custom_emojis=ce_list,
                            is_auto_watch=True)
                        db_update_watcher(
                            wid, last_post_id=newest,
                            last_run=datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"))
                        try:
                            await bot.send_message(
                                user_id,
                                f"📡 **AUTO-WATCH** 📡\n{DIV}\n\n"
                                f"✅ New post reacted!\n"
                                f"📢 {ct}\n"
                                f"📩 #{newest}\n"
                                f"💫 {rc} reactions")
                        except Exception:
                            pass
                    finally:
                        TASK_RUNNING = False
                        TASK_OWNER_UID = None
                except Exception as e:
                    D(f"[WATCHER] {str(e)[:80]}", "fail")
        except asyncio.CancelledError:
            return
        except Exception as e:
            D_err(e, "watcher_loop")
            await asyncio.sleep(30)


# ══════════════════════ POOL CLEANER LOOP ══════════════════════
async def pool_cleaner_loop():
    while True:
        try:
            await asyncio.sleep(POOL_CLEANUP_INTERVAL)
            cleaned = cleanup_bot_pool()
            if cleaned > 0:
                D(f"[POOL] Cleaned {cleaned} stale bots (both servers)",
                  "pool")
        except asyncio.CancelledError:
            return
        except Exception as e:
            D_err(e, "pool_cleaner")


# ══════════════════════ HEALTH CHECK LOOP ══════════════════════
async def health_check_loop():
    while True:
        try:
            await asyncio.sleep(120)
            uptime = int(time.time() - _start_time)
            fs = get_pool_status("free")
            ps = get_pool_status("paid")
            D(
                f"HEALTH up={uptime}s "
                f"task={TASK_RUNNING} "
                f"FREE[{fs['free']}f/{fs['busy']}b/{fs['flooded']}fl] "
                f"PAID[{ps['free']}f/{ps['busy']}b/{ps['flooded']}fl] "
                f"clients={len(REAL_CLIENTS)} "
                f"users={db_total_users()} "
                f"sessions={real_count_available()}",
                "health")
        except asyncio.CancelledError:
            return
        except Exception as e:
            D_err(e, "health_check")


# ══════════════════════ DAILY SUMMARY LOOP ══════════════════════
async def daily_summary_loop():
    last_sent = None
    while True:
        try:
            await asyncio.sleep(60)
            if not feat_daily_summary():
                continue
            tt = cfg_get("daily_summary_time", "21:00")
            now = datetime.now()
            today = now.strftime("%Y-%m-%d")
            cur = now.strftime("%H:%M")
            if cur == tt and last_sent != today:
                last_sent = today
                tot, tr, mr = db_revenue_stats()
                ref_stats = db_count_referrals()
                fs = get_pool_status("free")
                ps = get_pool_status("paid")
                real = real_get_status()
                bot_stats = db_bot_stats()

                txt = (
                    f"📊 **DAILY SUMMARY** — {today}\n"
                    f"{STAR_LINE}\n\n"
                    f"👥 Users: **{db_total_users()}**\n"
                    f"✅ Approved: **{db_count_approved_users()}**\n"
                    f"⏳ Pending: **{db_count_pending_approvals()}**\n"
                    f"🚫 Banned: **{db_count_banned_users()}**\n\n"
                    f"💫 Today: **{db_reactions_today()}**\n"
                    f"💫 Total: **{db_total_reactions()}**\n"
                    f"🎁 Referrals: **{ref_stats['valid']}**\n\n"
                    f"🖥️ **FREE SERVER**\n"
                    f"   🤖 {fs['visible']} bots\n"
                    f"   🟢 {fs['free']} / 🔴 {fs['busy']} / 🌊 {fs['flooded']}\n\n"
                    f"💎 **PAID SERVER**\n"
                    f"   🤖 {ps['visible']} bots\n"
                    f"   🟢 {ps['free']} / 🔴 {ps['busy']} / 🌊 {ps['flooded']}\n\n"
                    f"📊 Total bots: **{bot_stats['total']}** "
                    f"(F:{bot_stats['free']} / P:{bot_stats['paid']})\n\n"
                    f"👤 Sessions:\n"
                    f"   Available: **{real['available']}/{real['total']}**\n"
                    f"   Flooded: **{real['flooded']}**\n"
                    f"   Loaded: **{real['loaded']}/{real['max_clients']}**\n\n"
                    f"📡 Watchers: **{len(db_list_watchers())}**\n"
                    f"⏰ Queue: **{len(db_list_queue(status='pending'))}**\n"
                    f"🔄 Retries: **{retry_count_pending()}**\n\n"
                    f"💰 Revenue:\n"
                    f"   Today: **{tr}rs**\n"
                    f"   Month: **{mr}rs**\n"
                    f"   Total: **{tot}rs**")
                try:
                    await bot.send_message(get_owner_id(), txt)
                except Exception:
                    pass
        except asyncio.CancelledError:
            return
        except Exception as e:
            D_err(e, "daily_summary")
            await asyncio.sleep(60)


# ══════════════════════ STARTUP SYNC BOTS LOOP ══════════════════════
async def startup_bot_sync():
    """
    Runs once at startup — ensures bot_servers table is complete.
    Assigns server='free' or 'paid' to any bot missing it.
    """
    try:
        await asyncio.sleep(5)  # wait for startup
        conn = sqlite3.connect(DB_FILE)
        try:
            c = conn.cursor()
            # Bots without server column set
            rows = c.execute("""SELECT token, username FROM bots
                WHERE server IS NULL OR server=''""").fetchall()
            for tok, uname in rows:
                # Assign based on config lists
                if tok in FREE_SERVER_TOKENS:
                    c.execute("""UPDATE bots SET server='free'
                        WHERE token=?""", (tok,))
                elif tok in PAID_SERVER_TOKENS:
                    c.execute("""UPDATE bots SET server='paid'
                        WHERE token=?""", (tok,))
                else:
                    c.execute("""UPDATE bots SET server='free'
                        WHERE token=?""", (tok,))
            # Sync bot_servers table
            c.execute("""INSERT OR IGNORE INTO bot_servers
                (token, username, server)
                SELECT token, username, COALESCE(server, 'free')
                FROM bots""")
            conn.commit()
        finally:
            conn.close()
        _dirty()
        D("Startup bot-server sync complete", "server")
    except Exception as e:
        D_err(e, "startup_bot_sync")


# ══════════════════════ END OF PART 8 ══════════════════════
D("✅ Part 8 loaded — Broadcast + Loops (Dual Server)", "ok")
# ══════════════════════ USER KEYBOARDS ══════════════════════
def kb_join():
    """Force join channels keyboard"""
    rows = [
        [btn(f"📢 {fc[3]}", url=fc[2], style="primary")]
        for fc in db_list_force_channels(only_active=True)
    ]
    rows.append([btn("✅ I Have Joined", data=b"check_join",
                     style="success")])
    return rows


def kb_request_access(uid=None):
    return [[btn("🔔 Request Access", data=b"request_access",
                 style="success")]]


def kb_welcome(uid=None):
    """Main welcome menu"""
    rows = [
        [btn(f"💫 {L(uid, 'send_reactions')}", data=b"react_flow",
             style="success")],
        [btn(f"📊 {L(uid, 'dashboard')}", data=b"dashboard",
             style="primary"),
         btn(f"🎁 {L(uid, 'daily_bonus')}", data=b"daily_bonus",
             style="success")],
        [btn(f"⏰ {L(uid, 'queue')} 💎", data=b"queue_menu",
             style="primary"),
         btn(f"📦 {L(uid, 'bulk')} 💎", data=b"bulk_menu",
             style="primary")],
        [btn(f"📡 {L(uid, 'auto_watch')} 💎", data=b"watch_flow",
             style="primary"),
         btn(f"📝 {L(uid, 'templates')} 💎", data=b"templates_menu",
             style="primary")],
        [btn(f"🏪 {L(uid, 'store')}", data=b"store_menu",
             style="success"),
         btn(f"📜 {L(uid, 'post_history')}", data=b"post_history",
             style="primary")],
        [btn(f"🎁 {L(uid, 'referral')}", data=b"referral_menu",
             style="success"),
         btn(f"💰 {L(uid, 'buy_plan')}", data=b"plans_menu",
             style="success")],
        [btn(f"🔔 {L(uid, 'notifications')}", data=b"notif_menu",
             style="primary"),
         btn(f"🌍 {L(uid, 'language')}", data=b"lang_menu",
             style="primary")],
        [btn(f"❓ {L(uid, 'help')}", data=b"help", style="success"),
         btn(f"ℹ️ {L(uid, 'info')}", data=b"info", style="primary")],
        [btn(f"💬 {L(uid, 'support')}", data=b"support",
             style="primary")],
    ]
    if OWNER_IS(uid):
        rows.append([btn(f"👑 {L(uid, 'owner_panel')}",
                         data=b"owner_panel", style="danger")])
    return rows


def kb_help(uid=None):
    return [
        [btn("📖 Full Guide", data=b"help_full", style="success")],
        [btn("👑 Owner Username", data=b"help_username",
             style="primary"),
         btn("🆔 Owner ID", data=b"help_ownerid", style="primary")],
        [btn("💬 Contact Owner",
             url=f"https://t.me/{get_owner_username()}",
             style="primary")],
        [btn(f"🔙 {L(uid, 'back')}", data=b"home", style="danger")],
    ]


def kb_owner_needed(uid=None):
    return [
        [btn(f"📖 {L(uid, 'help')}", data=b"help_full",
             style="success")],
        [btn(f"👑 {L(uid, 'contact_owner')}",
             url=f"https://t.me/{get_owner_username()}",
             style="primary")],
        [btn(f"🔄 {L(uid, 'retry')}", data=b"react_flow",
             style="success")],
        [btn(f"🏠 {L(uid, 'home')}", data=b"home", style="primary")],
    ]


def kb_support(uid=None):
    return [
        [btn(f"💬 {L(uid, 'contact_owner')}",
             url=f"https://t.me/{get_owner_username()}",
             style="primary")],
        [btn("📖 Help Guide", data=b"help_full", style="success")],
        [btn(f"🔙 {L(uid, 'back')}", data=b"home", style="primary")],
    ]


def kb_chat_type(uid=None):
    return [
        [btn(f"📢 {L(uid, 'channel')}", data=b"chattype:channel",
             style="primary")],
        [btn(f"👥 {L(uid, 'group')}", data=b"chattype:group",
             style="success")],
        [btn(f"🔙 {L(uid, 'cancel')}", data=b"home", style="danger")],
    ]


def kb_reaction_count(uid=None):
    """Reaction count selection (uses correct server)"""
    limit = get_user_limit(uid) if uid else DEFAULT_FREE_COUNT
    server = get_user_server(uid) if uid else "free"
    tv = db_count_visible_bots(server=server)

    if OWNER_IS(uid):
        return [
            [btn(f"🌟 All ({tv})", data=b"rc:all", style="success")],
            [btn("10", data=b"rc:10", style="primary"),
             btn("20", data=b"rc:20", style="primary"),
             btn("50", data=b"rc:50", style="primary")],
            [btn("100", data=b"rc:100", style="primary"),
             btn("150", data=b"rc:150", style="primary"),
             btn("200", data=b"rc:200", style="primary")],
            [btn(f"🔙 {L(uid, 'back')}", data=b"home", style="primary")],
        ]

    effective_limit = min(limit, tv)
    rows = []
    row = []
    for i in range(1, effective_limit + 1):
        row.append(btn(f"{i}", data=f"rc:{i}".encode(),
                       style="primary"))
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    rows.append([btn(f"🎁 {effective_limit} MAX",
                     data=f"rc:{effective_limit}".encode(),
                     style="success")])

    if limit < MAX_REACTIONS:
        rows.append([btn("🔥 More 💎", data=b"rc_more",
                         style="danger")])

    rows.append([btn(f"🔙 {L(uid, 'back')}", data=b"home",
                     style="primary")])
    return rows


def kb_emoji_choice(uid=None):
    return [
        [btn(f"🎯 {L(uid, 'default_emoji')}", data=b"emoji:default",
             style="success")],
        [btn(f"✏️ {L(uid, 'custom_emoji')} 💎", data=b"emoji:custom",
             style="primary")],
        [btn(f"🎨 {L(uid, 'emoji_packs')} 💎", data=b"emoji:packs",
             style="primary")],
        [btn(f"📝 {L(uid, 'templates')} 💎",
             data=b"emoji:templates", style="primary")],
        [btn(f"🔙 {L(uid, 'back')}", data=b"home", style="danger")],
    ]


def kb_emoji_packs(uid=None):
    rows = [
        [btn(f"🎨 {k.title()} — {' '.join(e[:3])}",
             data=f"pack:{k}".encode(), style="primary")]
        for k, e in EMOJI_PACKS.items()
    ]
    for cp in db_list_custom_packs():
        cpid, name, emojis, price, is_paid = cp
        pre = "💎" if is_paid else "🎨"
        rows.append([btn(f"{pre} {name}",
                         data=f"cpack:{cpid}".encode(),
                         style="primary")])
    rows.append([btn(f"🔙 {L(uid, 'back')}", data=b"emoji:custom",
                     style="danger")])
    return rows


def kb_watch_menu(uid=None):
    return [
        [btn(f"➕ {L(uid, 'add_watch')}", data=b"watch:add",
             style="success")],
        [btn(f"📋 {L(uid, 'my_watches')}", data=b"watch:list",
             style="primary")],
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
        [btn("📦 Multi Posts", data=b"bulk:multi_post",
             style="success")],
        [btn("📋 My Jobs", data=b"bulk:list", style="primary")],
        [btn(f"🔙 {L(uid, 'back')}", data=b"home", style="primary")],
    ]


def kb_templates_menu(uid):
    ts = db_list_templates(uid)
    rows = [[btn("➕ New Template", data=b"tpl:new",
                 style="success")]]
    for t in ts[:5]:
        rows.append([
            btn(f"📝 {t[1]}", data=f"tpl:use:{t[0]}".encode(),
                style="primary"),
            btn("🗑️", data=f"tpl:del:{t[0]}".encode(),
                style="danger")
        ])
    rows.append([btn(f"🔙 {L(uid, 'back')}", data=b"home",
                     style="primary")])
    return rows


def kb_referral_menu(uid):
    return [
        [btn(f"🔗 {L(uid, 'my_link')}", data=b"ref:link",
             style="success")],
        [btn(f"📊 {L(uid, 'stats')}", data=b"ref:stats",
             style="primary")],
        [btn(f"🏆 {L(uid, 'leaderboard')}", data=b"ref:leaderboard",
             style="primary")],
        [btn(f"🔙 {L(uid, 'back')}", data=b"home", style="primary")],
    ]


def kb_plans_menu(uid=None):
    rows = [
        [btn(f"{PLAN_NAMES[k]} — {PLAN_LIMITS[k]}/post",
             data=f"plan:{k}".encode(), style="primary")]
        for k in ["basic", "pro", "premium"]
    ]
    rows.append([btn(f"🆓 {L(uid, 'free_plan')}",
                     data=b"plan:free", style="success")])
    rows.append([btn(f"🔙 {L(uid, 'back')}", data=b"home",
                     style="primary")])
    return rows


def kb_plan_durations(plan, uid=None):
    rows = []
    for days, label in DURATIONS.items():
        price = get_plan_price(plan, days)
        rows.append([btn(f"📅 {label} — {price}rs",
                         data=f"pland:{plan}:{days}".encode(),
                         style="success" if days == 30 else "primary")])
    rows.append([btn(f"🔙 {L(uid, 'back')}",
                     data=f"plan:{plan}".encode(),
                     style="primary")])
    return rows


def kb_lang_menu(uid):
    u = db_get_user_full(uid)
    cur = u[18] if u and len(u) > 18 else "en"
    rows = []
    for c, n in LANGUAGES.items():
        pre = "✅ " if c == cur else ""
        rows.append([btn(f"{pre}{n}", data=f"lang:{c}".encode(),
                         style="success" if c == cur else "primary")])
    rows.append([btn(f"🔙 {L(uid, 'back')}", data=b"home",
                     style="primary")])
    return rows


def kb_notif_menu(uid=None):
    return [
        [btn("📬 My Notifications", data=b"notif:list",
             style="primary")],
        [btn("✅ Mark All Read", data=b"notif:read",
             style="success")],
        [btn("🗑️ Clear All", data=b"notif:clear", style="danger")],
        [btn(f"🔙 {L(uid, 'back')}", data=b"home", style="primary")],
    ]


def kb_back(uid=None):
    return [[btn(f"🔙 {L(uid, 'back')}", data=b"home",
                 style="primary")]]


def kb_mode_choice(uid=None):
    """Reaction mode selection"""
    has_real = user_has_realaccounts(uid) if uid else False
    server = get_user_server(uid) if uid else "free"
    server_label = get_server_label(server)
    return [
        [btn(f"👑 With Admin ({server_label})", data=b"mode:with",
             style="primary")],
        [btn(f"🔓 Without Admin {'💎' if not has_real else ''}",
             data=b"mode:without", style="success")],
        [btn(f"🔙 {L(uid, 'cancel')}", data=b"home",
             style="danger")],
    ]


# ── Feature Keyboards ──
def kb_dashboard(uid):
    return [
        [btn("🔄 Refresh", data=b"dashboard", style="success"),
         btn(f"📜 {L(uid, 'post_history')}", data=b"post_history",
             style="primary")],
        [btn(f"🎁 {L(uid, 'daily_bonus')}", data=b"daily_bonus",
             style="success")],
        [btn(f"🏠 {L(uid, 'home')}", data=b"home", style="primary")],
    ]


def kb_daily_bonus(uid):
    can = bonus_can_claim(uid)
    rows = []
    if can:
        rows.append([btn("🎁 Claim Today's Bonus", data=b"bonus_claim",
                         style="success")])
    else:
        rows.append([btn("✅ Already Claimed Today",
                         data=b"dashboard", style="primary")])
    rows.append([btn("📊 View Streak", data=b"dashboard",
                     style="primary")])
    rows.append([btn(f"🔙 {L(uid, 'back')}", data=b"home",
                     style="primary")])
    return rows


def kb_post_history(uid):
    return [
        [btn("🔄 Refresh", data=b"post_history", style="success")],
        [btn("📊 Analytics", data=b"post_analytics",
             style="primary")],
        [btn(f"🔙 {L(uid, 'back')}", data=b"dashboard",
             style="primary")],
    ]


def kb_store(uid):
    packs = store_list(active_only=True)
    rows = []
    for p in packs[:8]:
        pid, name, emojis, price, desc = p
        owns = store_user_owns(uid, pid)
        pre = "✅" if owns else "🏪"
        rows.append([btn(f"{pre} {name} — {price}rs",
                         data=f"store_view:{pid}".encode(),
                         style="success" if owns else "primary")])
    if not packs:
        rows.append([btn("❌ No packs available", data=b"home",
                         style="danger")])
    rows.append([btn("🛍️ My Purchases", data=b"store_mine",
                     style="primary")])
    rows.append([btn(f"🔙 {L(uid, 'back')}", data=b"home",
                     style="primary")])
    return rows


def kb_store_view(pid, uid):
    owns = store_user_owns(uid, pid)
    p = store_get(pid)
    if not p:
        return [[btn("❌ Not found", data=b"store_menu",
                     style="danger")]]
    rows = []
    if owns:
        rows.append([btn("✅ Owned — Load Pack",
                         data=f"store_use:{pid}".encode(),
                         style="success")])
    else:
        _, _, _, price, _, _ = p
        rows.append([btn(f"💳 Buy for {price}rs",
                         data=f"store_buy:{pid}".encode(),
                         style="primary")])
    rows.append([btn(f"🔙 {L(uid, 'back')}", data=b"store_menu",
                     style="primary")])
    return rows


def kb_store_mine(uid):
    return [
        [btn("🔄 Refresh", data=b"store_mine", style="success")],
        [btn(f"🔙 {L(uid, 'back')}", data=b"store_menu",
             style="primary")],
    ]


# ══════════════════════ END OF PART 9 ══════════════════════
D("✅ Part 9 loaded — User Keyboards (Server-Aware)", "ok")
# ══════════════════════ OWNER KEYBOARDS ══════════════════════
def kb_owner():
    """Main owner panel with server management"""
    auto = "✅" if is_auto_approve() else "❌"
    stats = db_bot_stats()
    real_status = real_get_status()
    free_s = get_pool_status("free")
    paid_s = get_pool_status("paid")

    return [
        # Row 1
        [btn("📊 Analytics", data=b"op:analytics", style="success"),
         btn("👥 Users", data=b"op:users", style="primary")],
        # Row 2
        [btn("💰 Revenue", data=b"op:revenue", style="primary"),
         btn("💳 Payments", data=b"op:payments", style="danger")],
        # Row 3: Bot info
        [btn(f"🤖 Bots: {stats['total']}",
              data=b"op:bots", style="primary"),
         btn("📢 Broadcast", data=b"op:broadcast", style="danger")],
        # Row 4: SERVER MANAGEMENT (NEW)
        [btn(f"🖥️ Free Server ({stats['free']})",
              data=b"srv:panel:free", style="success"),
         btn(f"💎 Paid Server ({stats['paid']})",
              data=b"srv:panel:paid", style="primary")],
        # Row 5: Sessions + RA Plans
        [btn(f"👤 Sessions ({real_status['available']}/"
              f"{real_status['total']})",
              data=b"op:ra", style="success"),
         btn("⚙️ RA Plans", data=b"op:ra_plans", style="primary")],
        # Row 6
        [btn("👤 Owner Info", data=b"op:owner_info", style="success"),
         btn("🎟️ Coupons", data=b"op:coupons", style="success")],
        # Row 7
        [btn("🏪 Emoji Store", data=b"op:store", style="primary"),
         btn("🔄 Auto-Retry", data=b"op:retry", style="primary")],
        # Row 8
        [btn("👥 Bulk Users", data=b"op:bulk_users", style="primary"),
         btn("📈 Rate Limits", data=b"op:rate_limits", style="primary")],
        # Row 9
        [btn(f"🔓 Auto:{auto}", data=b"op:toggle_auto",
              style="success"),
         btn(f"⚙️ Free:{get_free_count()}", data=b"op:setfree",
              style="primary")],
        # Row 10
        [btn("🎛️ Features", data=b"op:features", style="primary"),
         btn("💰 Prices", data=b"op:plan_prices", style="success")],
        # Row 11
        [btn("💎 PAID FEATURES", data=b"op:paid_features",
              style="danger")],
        # Row 12
        [btn("📢 Force Ch", data=b"op:force_channels",
              style="primary"),
         btn("👥 Team", data=b"op:team", style="success")],
        # Row 13
        [btn("🎨 Custom Packs", data=b"op:emoji_packs",
              style="primary"),
         btn("📡 Watchers", data=b"op:watchers", style="primary")],
        # Row 14
        [btn("🎁 Referrals", data=b"op:referrals", style="success"),
         btn("⏰ Queue", data=b"op:queue", style="primary")],
        # Row 15: Pool status (both)
        [btn("📊 Pool", data=b"op:pool_status", style="primary"),
         btn("🧹 RESET POOL", data=b"op:reset_pool",
              style="danger")],
        # Row 16
        [btn("🔄 Auto Backup", data=b"op:ghsync", style="success"),
         btn("➕ Add User", data=b"op:adduser", style="success")],
        # Row 17
        [btn("⏳ Pending", data=b"op:pending", style="danger"),
         btn("✅ Approved", data=b"op:approved", style="success")],
        # Row 18
        [btn("📜 Recent", data=b"op:recent", style="primary"),
         btn("🔙 Main", data=b"home", style="primary")],
    ]


# ══════════════════════ 🔥 SERVER MANAGEMENT ══════════════════════
def kb_server_panel(server):
    """Detailed server management panel"""
    pool = get_pool_status(server)
    label = get_server_label(server)
    other = "paid" if server == "free" else "free"
    other_label = get_server_label(other)

    # Get bot list preview
    bots = db_list_visible_bots(server=server)

    rows = [
        # Stats
        [btn(f"📊 Total: {pool['total']}", data=f"srv:refresh:{server}",
              style="primary"),
         btn(f"🟢 Free: {pool['free']}", data=f"srv:refresh:{server}",
              style="success")],
        [btn(f"🔴 Busy: {pool['busy']}", data=f"srv:refresh:{server}",
              style="danger"),
         btn(f"🌊 Flooded: {pool['flooded']}",
              data=f"srv:refresh:{server}", style="primary")],
        # Actions
        [btn("🔄 Refresh", data=f"srv:refresh:{server}",
              style="success")],
        [btn("📋 List All Bots", data=f"srv:list:{server}",
              style="primary")],
        [btn("🌊 Clear Floods", data=f"srv:clear_floods:{server}",
              style="danger")],
        [btn("🧹 Reset Pool", data=f"srv:reset:{server}",
              style="danger")],
        [btn(f"🔀 Move All → {other_label}",
              data=f"srv:move_all:{server}", style="danger")],
        [btn("📤 Bulk Move", data=f"srv:bulk_move:{server}",
              style="primary")],
        [btn("➕ Add Bot to Server",
              data=f"srv:add_bot:{server}", style="success")],
        [btn("🧪 Test All Bots", data=f"srv:test_all:{server}",
              style="primary")],
        [btn("🔙 Back", data=b"owner_panel", style="primary")],
    ]
    return rows


def kb_bot_list(server, page=0):
    """Paginated bot list for a server"""
    bots = db_list_visible_bots(server=server)
    per_page = 10
    start = page * per_page
    end = start + per_page
    page_bots = bots[start:end]
    total = len(bots)
    total_pages = (total + per_page - 1) // per_page

    now = datetime.now()
    flood_map = get_flood_map(server)
    pool = get_pool(server)

    rows = []
    for i, b in enumerate(page_bots, start=start+1):
        tok, uname, bid, added = b
        # Status
        st = "🟢"
        if tok in flood_map and flood_map[tok] > now:
            st = "🌊"
        else:
            info = pool.get(tok)
            if (isinstance(info, dict) and info.get("busy_until")
                    and info["busy_until"] > now):
                st = "🔴"
        rows.append([btn(f"{st} {i}. @{uname}",
                         data=f"bot:info:{server}:{tok[:20]}",
                         style="primary")])

    # Pagination
    nav = []
    if page > 0:
        nav.append(btn("⬅️ Prev",
                       data=f"srv:list:{server}:{page-1}".encode(),
                       style="primary"))
    if page < total_pages - 1:
        nav.append(btn("Next ➡️",
                       data=f"srv:list:{server}:{page+1}".encode(),
                       style="primary"))
    if nav:
        rows.append(nav)

    rows.append([
        btn(f"📄 Page {page+1}/{total_pages}",
            data=f"srv:list:{server}:{page}".encode(),
            style="success")
    ])
    rows.append([
        btn(f"🔙 {get_server_label(server)}",
            data=f"srv:panel:{server}".encode(),
            style="danger")
    ])
    return rows


# ══════════════════════ USER SERVER ASSIGNMENT ══════════════════════
def kb_user_server(tuid):
    """Server assignment keyboard for a user"""
    u = db_get_user_full(tuid)
    if not u:
        return [[btn("❌ Not found", data=b"op:users",
                     style="danger")]]

    current = get_user_server(tuid)
    plan = u[15] or "free"
    override = u[27] if len(u) > 27 else None

    return [
        [btn(f"👤 User: `{tuid}`",
              data=f"um:panel:{tuid}".encode(), style="primary")],
        [btn(f"💰 Plan: {plan}",
              data=f"um:panel:{tuid}".encode(), style="success")],
        [btn(f"🖥️ Current Server: {get_server_label(current)}",
              data=f"usrv:refresh:{tuid}".encode(), style="primary")],
        [btn(f"📝 Override: {override or 'None'}",
              data=f"usrv:refresh:{tuid}".encode(), style="primary")],
        [btn("🆓 Force FREE Server",
              data=f"usrv:set:free:{tuid}".encode(),
              style="success")],
        [btn("💎 Force PAID Server",
              data=f"usrv:set:paid:{tuid}".encode(),
              style="success")],
        [btn("🔄 Reset (Use Plan Default)",
              data=f"usrv:reset:{tuid}".encode(),
              style="primary")],
        [btn("🔙 Back",
              data=f"um:panel:{tuid}".encode(),
              style="danger")],
    ]


def kb_bulk_move(server):
    """Bulk move bots panel"""
    other = "paid" if server == "free" else "free"
    return [
        [btn("🔀 Move ALL bots", data=f"srv:move_all:{server}".encode(),
              style="danger")],
        [btn("📊 Move only FLOODED",
              data=f"srv:move_flooded:{server}".encode(),
              style="primary")],
        [btn("📊 Move only BUSY",
              data=f"srv:move_busy:{server}".encode(),
              style="primary")],
        [btn("🔙 Back",
              data=f"srv:panel:{server}".encode(),
              style="primary")],
    ]


# ══════════════════════ FEATURES ══════════════════════
def kb_features():
    def t(k, l):
        return f"{'✅' if cfg_bool(k) else '❌'} {l}"
    return [
        [btn(t("channel_enabled", "Channel"),
             data=b"ft:toggle:channel_enabled", style="primary")],
        [btn(t("group_enabled", "Group"),
             data=b"ft:toggle:group_enabled", style="success")],
        [btn(t("manual_enabled", "Manual"),
             data=b"ft:toggle:manual_enabled", style="primary")],
        [btn(t("autowatch_enabled", "Auto-Watch"),
             data=b"ft:toggle:autowatch_enabled", style="success")],
        [btn(t("custom_emoji_enabled", "Custom Emoji"),
             data=b"ft:toggle:custom_emoji_enabled", style="primary")],
        [btn(t("force_join_enabled", "Force Join"),
             data=b"ft:toggle:force_join_enabled", style="success")],
        [btn(t("paid_plans_enabled", "Paid Plans"),
             data=b"ft:toggle:paid_plans_enabled", style="primary")],
        [btn(t("referral_enabled", "Referral"),
             data=b"ft:toggle:referral_enabled", style="success")],
        [btn(t("multi_lang_enabled", "Multi-Lang"),
             data=b"ft:toggle:multi_lang_enabled", style="primary")],
        [btn(t("templates_enabled", "Templates"),
             data=b"ft:toggle:templates_enabled", style="success")],
        [btn(t("notifications_enabled", "Notifications"),
             data=b"ft:toggle:notifications_enabled", style="primary")],
        [btn(t("queue_enabled", "Queue"),
             data=b"ft:toggle:queue_enabled", style="success")],
        [btn(t("bulk_enabled", "Bulk"),
             data=b"ft:toggle:bulk_enabled", style="primary")],
        [btn(t("daily_summary_enabled", "Summary"),
             data=b"ft:toggle:daily_summary_enabled", style="primary")],
        [btn(t("team_enabled", "Team"),
             data=b"ft:toggle:team_enabled", style="success")],
        [btn(t("realaccounts_enabled", "Real Accounts"),
             data=b"ft:toggle:realaccounts_enabled", style="primary")],
        [btn(t("daily_bonus_enabled", "Daily Bonus"),
             data=b"ft:toggle:daily_bonus_enabled", style="success")],
        [btn(t("auto_retry_enabled", "Auto-Retry"),
             data=b"ft:toggle:auto_retry_enabled", style="primary")],
        [btn(t("smart_notif_enabled", "Smart Notif"),
             data=b"ft:toggle:smart_notif_enabled", style="success")],
        [btn(t("coupon_enabled", "Coupons"),
             data=b"ft:toggle:coupon_enabled", style="primary")],
        [btn(t("emoji_store_enabled", "Emoji Store"),
             data=b"ft:toggle:emoji_store_enabled", style="success")],
        [btn(t("post_analytics_enabled", "Post Analytics"),
             data=b"ft:toggle:post_analytics_enabled", style="primary")],
        [btn(t("team_reseller_enabled", "Reseller"),
             data=b"ft:toggle:team_reseller_enabled", style="success")],
        [btn(t("upsell_enabled", "Upsell"),
             data=b"ft:toggle:upsell_enabled", style="primary")],
        [btn(t("smart_reaction_enabled", "Smart Reaction"),
             data=b"ft:toggle:smart_reaction_enabled", style="success")],
        [btn(t("fallback_enabled", "Fallback Reactions"),
             data=b"ft:toggle:fallback_enabled", style="primary")],
        [btn(t("dual_server_enabled", "Dual Server"),
             data=b"ft:toggle:dual_server_enabled", style="success")],
        [btn("🔙 Back", data=b"owner_panel", style="danger")],
    ]


def kb_plan_prices():
    rows = [
        [btn(f"💰 {PLAN_NAMES[p]}",
             data=f"pp:plan:{p}".encode(), style="primary")]
        for p in ["basic", "pro", "premium"]
    ]
    rows.append([btn("🔙 Back", data=b"owner_panel", style="primary")])
    return rows


def kb_plan_prices_durations(plan):
    rows = [
        [btn(f"📅 {label}: {get_plan_price(plan, days)}rs",
             data=f"pp:edit:{plan}:{days}".encode(), style="primary")]
        for days, label in DURATIONS.items()
    ]
    rows.append([btn("🔙 Back", data=b"op:plan_prices",
                     style="primary")])
    return rows


def kb_paid_features():
    def t(k, l):
        paid = cfg_bool(f"paid_{k}", False)
        st = "💎 PAID" if paid else "🆓 FREE"
        return btn(f"{st} — {l}",
                   data=f"pf:toggle:{k}".encode(),
                   style="danger" if paid else "success")
    return [
        [t("autowatch", "Auto-Watch")],
        [t("custom_emoji", "Custom Emoji")],
        [t("templates", "Templates")],
        [t("multilang", "Multi-Language")],
        [t("referral", "Referral")],
        [t("balance", "Free Balance")],
        [t("channel", "Channel")],
        [t("group", "Group")],
        [t("manual", "Manual")],
        [t("realaccounts", "Real Accounts")],
        [btn("🔙 Back", data=b"owner_panel", style="primary")],
    ]


# ══════════════════════ FORCE / TEAM / PACKS ══════════════════════
def kb_force_channels():
    rows = []
    for fc in db_list_force_channels(only_active=False):
        fid, ch, url, name, act = fc
        st = "🟢" if act else "🔴"
        rows.append([
            btn(f"{st} {name} ({ch})",
                data=f"fc:toggle:{fid}".encode(), style="primary"),
            btn("🗑️", data=f"fc:del:{fid}".encode(),
                style="danger")
        ])
    rows.append([btn("➕ Add", data=b"fc:add", style="success")])
    rows.append([btn("🔙 Back", data=b"owner_panel", style="primary")])
    return rows


def kb_team():
    rows = []
    for m in db_list_team()[:10]:
        uid, role, perms, comm, sales, total_comm, added = m
        rows.append([btn(f"👤 {uid} — {role} ({comm}%)",
                         data=f"team:view:{uid}".encode(),
                         style="primary")])
    rows.append([btn("➕ Add", data=b"team:add", style="success")])
    rows.append([btn("🔙 Back", data=b"owner_panel", style="primary")])
    return rows


def kb_emoji_packs_manage():
    rows = []
    for cp in db_list_custom_packs():
        cpid, name, emojis, price, is_paid = cp
        pre = "💎" if is_paid else "🎨"
        rows.append([
            btn(f"{pre} {name} — {price}rs",
                data=f"cp:view:{cpid}".encode(), style="primary"),
            btn("🗑️", data=f"cp:del:{cpid}".encode(),
                style="danger")
        ])
    rows.append([btn("➕ New Pack", data=b"cp:new", style="success")])
    rows.append([btn("🔙 Back", data=b"owner_panel", style="primary")])
    return rows


# ══════════════════════ USER MANAGEMENT ══════════════════════
def kb_user_manage(uid):
    u = db_get_user_full(uid)
    if not u:
        return [[btn("❌ Not found", data=b"op:users",
                     style="danger")]]
    def yn(v):
        return "✅" if v else "❌"
    plan = u[15] or "free"
    fb = u[17] or 0
    try:
        ra_ov = u[26] if len(u) > 26 else -1
    except Exception:
        ra_ov = -1
    ra_lbl = ra_ov if ra_ov >= 0 else "Plan"
    current_server = get_user_server(uid)
    server_label = get_server_label(current_server)

    return [
        [btn(f"{yn(not u[5])} {'BANNED' if u[5] else 'Active'}",
              data=f"um:ban:{uid}".encode(),
              style="danger" if u[5] else "success")],
        [btn(f"🎁 Limit: {u[8] if u[8] > 0 else get_free_count()}",
              data=f"um:limit:{uid}".encode(), style="primary")],
        [btn(f"💰 Plan: {plan}", data=f"um:plan:{uid}".encode(),
             style="success")],
        [btn(f"🎁 Balance: {fb}", data=f"um:balance:{uid}".encode(),
             style="primary")],
        [btn(f"🖥️ Server: {server_label}",
              data=f"usrv:panel:{uid}".encode(), style="success")],
        [btn(f"👤 RA Limit: {ra_lbl}",
              data=f"um:ra:{uid}".encode(), style="success")],
        [btn(f"👥 Team: {u[23] or 'user'}",
              data=f"um:team:{uid}".encode(), style="primary")],
        [btn(f"{yn(u[10])} Channel",
              data=f"um:channel:{uid}".encode(), style="primary")],
        [btn(f"{yn(u[11])} Group",
              data=f"um:group:{uid}".encode(), style="success")],
        [btn(f"{yn(u[12])} Manual",
              data=f"um:manual:{uid}".encode(), style="primary")],
        [btn(f"{yn(u[13])} Auto-Watch",
              data=f"um:autowatch:{uid}".encode(), style="success")],
        [btn(f"{yn(u[14])} Custom Emoji",
              data=f"um:custom:{uid}".encode(), style="primary")],
        [btn(f"{yn(u[9])} AW Unlock",
              data=f"um:unlock:{uid}".encode(), style="success")],
        [btn("🔙 Back", data=b"op:users", style="danger")],
    ]


def kb_user_plan_durations(tuid):
    rows = []
    for p in ["basic", "pro", "premium"]:
        for d in [1, 7, 15, 30]:
            rows.append([btn(f"{PLAN_NAMES[p]} {DURATIONS[d]}",
                             data=f"um:activate:{p}:{d}:{tuid}".encode(),
                             style="primary")])
    rows.append([btn("🆓 Free",
                     data=f"um:activate:free:9999:{tuid}".encode(),
                     style="success")])
    rows.append([btn("🔙 Back",
                     data=f"um:panel:{tuid}".encode(),
                     style="danger")])
    return rows


def kb_approval_actions(tuid):
    return [[
        btn("✅ Approve", data=f"approve:{tuid}".encode(),
            style="success"),
        btn("❌ Reject", data=f"reject:{tuid}".encode(),
            style="danger")
    ]]


def kb_payment_actions(pid):
    return [[
        btn("✅ Verify", data=f"payv:approve:{pid}".encode(),
            style="success"),
        btn("❌ Reject", data=f"payv:reject:{pid}".encode(),
            style="danger")
    ]]


# ══════════════════════ COUPONS / STORE MANAGE ══════════════════════
def kb_coupons_manage():
    rows = []
    for c in coupon_list()[:15]:
        cid, code, pct, flat, mx, used, exp, act = c
        st = "🟢" if act else "🔴"
        val = f"{pct}%" if pct > 0 else f"{flat}rs"
        rows.append([
            btn(f"{st} {code} — {val} ({used}/{mx})",
                data=f"cop:view:{cid}".encode(), style="primary"),
            btn("🗑️", data=f"cop:del:{cid}".encode(),
                style="danger")
        ])
    rows.append([btn("➕ New Coupon", data=b"cop:new",
                     style="success")])
    rows.append([btn("🔙 Back", data=b"owner_panel", style="primary")])
    return rows


def kb_store_manage():
    rows = []
    for p in store_list(active_only=False):
        pid = p[0]
        name = p[1]
        price = p[3]
        act = p[5] if len(p) > 5 else 1
        st = "🟢" if act else "🔴"
        rows.append([
            btn(f"{st} {name} — {price}rs",
                data=f"storem:view:{pid}".encode(), style="primary"),
            btn("🗑️", data=f"storem:del:{pid}".encode(),
                style="danger")
        ])
    rows.append([btn("➕ New Pack", data=b"storem:new",
                     style="success")])
    rows.append([btn("🔙 Back", data=b"owner_panel", style="primary")])
    return rows


def kb_retry_menu():
    return [
        [btn("🔄 Process Now", data=b"retry:process_now",
             style="success")],
        [btn("📋 View Pending", data=b"retry:list",
             style="primary")],
        [btn("🧹 Clear All", data=b"retry:clear", style="danger")],
        [btn("🔙 Back", data=b"owner_panel", style="primary")],
    ]


def kb_rate_limits():
    return [
        [btn("🔄 Refresh", data=b"op:rate_limits",
             style="success")],
        [btn("🔙 Back", data=b"owner_panel", style="primary")],
    ]


def kb_bulk_users():
    return [
        [btn("🚫 Ban All Pending", data=b"bulk:ban_pending",
             style="danger")],
        [btn("✅ Approve All Pending", data=b"bulk:approve_pending",
             style="success")],
        [btn("💎 Grant Premium 7d to Free",
             data=b"bulk:premium_all", style="success")],
        [btn("🔙 Back", data=b"owner_panel", style="primary")],
    ]


# ══════════════════════ RA PANELS (FIXED) ══════════════════════
def kb_ra_panel():
    status = real_get_status()
    rows = [
        [btn(f"📊 Total: {status['total']}", data=b"op:ra",
             style="primary"),
         btn(f"✅ Free: {status['available']}", data=b"op:ra",
             style="success")],
        [btn(f"🌊 Flooded: {status['flooded']}", data=b"op:ra",
             style="danger"),
         btn(f"💾 Loaded: {status['loaded']}/{status['max_clients']}",
             data=b"op:ra", style="primary")],
        [btn("🔄 Refresh", data=b"op:ra", style="success")],
        [btn("📋 List Sessions", data=b"ra:list",
             style="primary")],
        [btn("🌊 Clear Floods", data=b"ra:clear_floods",
             style="danger")],
        [btn("🔌 Disconnect All", data=b"ra:disconnect_all",
             style="danger")],
        [btn("🧪 Test All", data=b"ra:test_all", style="success")],
        [btn("📤 Upload Info", data=b"ra:upload_info",
             style="primary")],
        [btn("🔙 Back", data=b"owner_panel", style="primary")],
    ]
    return rows


def kb_ra_plans():
    rows = []
    for plan in ["free", "basic", "pro", "premium"]:
        lim = plan_ra_limit(plan)
        enabled = plan_has_realaccounts(plan)
        st = "✅" if enabled else "❌"
        rows.append([
            btn(f"{st} {PLAN_NAMES[plan]}",
                data=f"rap:toggle:{plan}".encode(),
                style="success" if enabled else "danger"),
            btn(f"👤 {lim}",
                data=f"rap:edit:{plan}".encode(),
                style="primary"),
        ])
    rows.append([btn("🔙 Back", data=b"owner_panel",
                     style="primary")])
    return rows


def kb_sessions_panel():
    files = discover_session_files()
    status = real_get_status()
    rows = [
        [btn(f"📁 {status['total']} sessions", data=b"op:ra",
             style="primary"),
         btn(f"🌊 {status['flooded']} flooded", data=b"op:ra",
             style="danger")],
    ]
    for i, sf in enumerate(files[:10], 1):
        flooded = "🌊" if is_real_flooded(sf) else "🟢"
        loaded = "💾" if sf in REAL_CLIENTS else "📁"
        rows.append([
            btn(f"{flooded}{loaded} {sf.replace('.session','')[:20]}",
                data=f"ra:info:{sf}".encode(),
                style="danger" if flooded == "🌊" else "primary"),
        ])
    if len(files) > 10:
        rows.append([btn(f"... +{len(files)-10} more",
                         data=b"ra:list", style="primary")])
    rows.append([btn("🔄 Refresh", data=b"op:ra", style="success")])
    rows.append([btn("🔙 Back", data=b"op:ra", style="primary")])
    return rows


def kb_session_info(sf):
    flooded = is_real_flooded(sf)
    loaded = sf in REAL_CLIENTS
    flood_until = REAL_FLOOD_UNTIL.get(sf)
    flood_txt = "—"
    if flood_until:
        remaining = int((flood_until - datetime.now()).total_seconds())
        flood_txt = f"{remaining}s" if remaining > 0 else "expired"
    return [
        [btn(f"📁 {sf[:30]}", data=b"op:ra", style="primary")],
        [btn(f"🌊 Flooded: {'✅' if flooded else '❌'}",
             data=b"op:ra",
             style="danger" if flooded else "success")],
        [btn(f"💾 Loaded: {'✅' if loaded else '❌'}",
             data=b"op:ra", style="primary")],
        [btn(f"⏱️ Flood till: {flood_txt}", data=b"op:ra",
             style="primary")],
        [btn("🧪 Test", data=f"ra:test:{sf}".encode(),
             style="success"),
         btn("🔄 Reset", data=f"ra:reset:{sf}".encode(),
             style="primary")],
        [btn("🔌 Disconnect", data=f"ra:disconnect:{sf}".encode(),
             style="danger")],
        [btn("🔙 Back", data=b"ra:list", style="primary")],
    ]


# ══════════════════════ END OF PART 10 ══════════════════════
D("✅ Part 10 loaded — Owner Keyboards + Server Management", "ok")
# ══════════════════════ MESSAGE TEMPLATES ══════════════════════
def get_admin_needed_message(chat_title, uid=None):
    """Owner admin required message"""
    return (
        f"{STAR_LINE}\n"
        f"⚠️ **IMPORTANT — READ FIRST** ⚠️\n"
        f"{STAR_LINE}\n\n"
        f"📢 **{chat_title}**\n\n"
        f"❌ Before sending reactions, make the OWNER admin in your "
        f"channel/group!\n\n"
        f"{DIV}\n"
        f"👑 **Owner:** @{get_owner_username()}\n"
        f"🆔 **Owner ID:** `{get_owner_id()}`\n"
        f"{DIV}\n\n"
        f"📋 **Required Permissions:**\n"
        f"   ⭐ Add New Admins\n"
        f"   ⭐ Post Messages\n"
        f"   ⭐ Delete Messages\n"
        f"   ⭐ Invite Users\n\n"
        f"{DIV}\n"
        f"🔧 **HOW TO ADD ADMIN**\n"
        f"{DIV}\n"
        f"1️⃣ Open your channel/group\n"
        f"2️⃣ Tap name → Administrators\n"
        f"3️⃣ Add Admin → @{get_owner_username()}\n"
        f"4️⃣ Enable ALL permissions above\n"
        f"5️⃣ Save\n"
        f"{DIV}\n\n"
        f"💬 @{get_owner_username()}  |  🆔 `{get_owner_id()}`\n\n"
        f"📖 Tap **Help** below for full guide"
    )


def get_welcome_message(first_name, uid, auto_approved=True):
    """Welcome message with server info"""
    limit = get_user_limit(uid)
    u = db_get_user_full(uid)
    aw = u[9] if u else 0
    plan = u[15] if u else "free"
    fb = u[17] if u else 0
    plan_name = PLAN_NAMES.get(plan, PLAN_NAMES['free'])
    yes_no = "✅ YES" if auto_approved else "⏳ NO"
    aw_state = "✅" if aw else "🔒"

    # Server info
    server = get_user_server(uid)
    server_label = get_server_label(server)
    server_bot_count = db_count_visible_bots(server=server)

    stats = stats_get(uid)
    total = stats[1] if stats and len(stats) > 1 else 0
    streak = stats[8] if stats and len(stats) > 8 else 0

    return (
        f"{STAR_LINE}\n"
        f"👻 **GHOST REACTION BOT** 👻\n"
        f"{STAR_LINE}\n\n"
        f"👋 Welcome, **{first_name}**!\n\n"
        f"{DIV}\n"
        f"⚠️ **QUICK START**\n"
        f"{DIV}\n\n"
        f"❌ Make the OWNER admin in your chat first!\n\n"
        f"👑 **Owner:** @{get_owner_username()}\n"
        f"🆔 **ID:** `{get_owner_id()}`\n\n"
        f"❓ Tap **Help** button for full guide\n\n"
        f"{DIV}\n"
        f"📊 **YOUR INFO**\n"
        f"{DIV}\n"
        f"🖥️ Server: **{server_label}** ({server_bot_count} bots)\n"
        f"💰 Plan: **{plan_name}**\n"
        f"🎁 Limit: **{limit}** per post\n"
        f"💎 Balance: **{fb}**\n"
        f"📡 Auto-Watch: **{aw_state}**\n"
        f"✅ Approved: **{yes_no}**\n"
        f"💫 Total Sent: **{total}**\n"
        f"🔥 Streak: **{streak}** days\n"
        f"{DIV}\n\n"
        f"✅ Ready! Tap a button below"
    )


def get_approved_notify_message(first_name, uid=None):
    """Approval notification — server-aware"""
    limit = get_user_limit(uid) if uid else DEFAULT_FREE_COUNT
    server = get_user_server(uid) if uid else "free"
    server_label = get_server_label(server)
    server_bots = db_count_visible_bots(server=server) if uid else 0

    return (
        f"{STAR_LINE}\n"
        f"{SPARKLE} 🎉 **APPROVED** 🎉 {SPARKLE}\n"
        f"{STAR_LINE}\n\n"
        f"👋 Welcome, **{first_name}**!\n"
        f"✅ Access granted!\n\n"
        f"{DIV}\n"
        f"🖥️ Your Server: **{server_label}**\n"
        f"🤖 Available Bots: **{server_bots}**\n"
        f"🎁 Limit: **{limit}** per post\n"
        f"{DIV}\n\n"
        f"{DIV}\n"
        f"👑 Owner: @{get_owner_username()}\n"
        f"🆔 ID: `{get_owner_id()}`\n"
        f"{DIV}\n\n"
        f"⚠️ Make owner admin in your chat!\n\n"
        f"🚀 Send /start to begin!"
    )


def get_pending_message(uid=None):
    """Pending approval message"""
    return (
        f"{STAR_LINE}\n"
        f"⏳ **PENDING APPROVAL**\n"
        f"{STAR_LINE}\n\n"
        f"Your request is under review.\n\n"
        f"{DIV}\n"
        f"📞 Contact: @{get_owner_username()}\n"
        f"🆔 ID: `{get_owner_id()}`\n"
        f"{DIV}\n\n"
        f"✅ You'll be notified once approved.\n"
        f"⏱️ Usually within 24 hours."
    )


def get_rejected_message(uid=None):
    """Rejected approval message"""
    return (
        f"{STAR_LINE}\n"
        f"❌ **REQUEST REJECTED**\n"
        f"{STAR_LINE}\n\n"
        f"Your access request was rejected.\n\n"
        f"{DIV}\n"
        f"📞 Contact: @{get_owner_username()}\n"
        f"🆔 ID: `{get_owner_id()}`\n"
        f"{DIV}\n\n"
        f"💬 You can appeal by contacting the owner."
    )


def get_banned_message(uid=None):
    return (
        f"{STAR_LINE}\n"
        f"🚫 **BANNED**\n"
        f"{STAR_LINE}\n\n"
        f"You have been banned from using this bot.\n\n"
        f"{DIV}\n"
        f"📞 Contact: @{get_owner_username()}\n"
        f"{DIV}"
    )


# ══════════════════════ SERVER INFO HELPERS ══════════════════════
def get_server_summary_text(server):
    """Short server summary for display"""
    pool = get_pool_status(server)
    label = get_server_label(server)
    return (
        f"{label} Server\n"
        f"🤖 Total: **{pool['visible']}** bots\n"
        f"🟢 Free: **{pool['free']}**\n"
        f"🔴 Busy: **{pool['busy']}**\n"
        f"🌊 Flooded: **{pool['flooded']}**"
    )


def get_dual_server_status_text():
    """Full dual-server status text"""
    fs = get_pool_status("free")
    ps = get_pool_status("paid")
    stats = db_bot_stats()
    return (
        f"🖥️ **DUAL SERVER STATUS**\n"
        f"{STAR_LINE}\n\n"
        f"🆓 **FREE SERVER**\n"
        f"   📊 Total: **{fs['total']}** bots\n"
        f"   🟢 Free: **{fs['free']}**\n"
        f"   🔴 Busy: **{fs['busy']}**\n"
        f"   🌊 Flooded: **{fs['flooded']}**\n\n"
        f"💎 **PAID SERVER**\n"
        f"   📊 Total: **{ps['total']}** bots\n"
        f"   🟢 Free: **{ps['free']}**\n"
        f"   🔴 Busy: **{ps['busy']}**\n"
        f"   🌊 Flooded: **{ps['flooded']}**\n\n"
        f"{DIV}\n"
        f"📊 Total: **{stats['total']}** bots\n"
        f"🆓 Free: **{stats['free']}** | 💎 Paid: **{stats['paid']}**\n"
        f"🔒 Permanent: **{stats['permanent']}**"
    )


def get_user_plan_info_text(uid):
    """User's plan & server info"""
    u = db_get_user_full(uid)
    if not u:
        return "❌ User not found"
    plan = u[15] or "free"
    exp = u[16] or "N/A"
    fb = u[17] or 0
    limit = get_user_limit(uid)
    server = get_user_server(uid)
    server_label = get_server_label(server)
    ra_lim, ra_src = get_user_ra_limit(uid)
    return (
        f"👤 **YOUR ACCOUNT INFO**\n"
        f"{STAR_LINE}\n\n"
        f"🆔 ID: `{uid}`\n"
        f"📛 Name: **{u[1] or '—'}**\n\n"
        f"{DIV}\n"
        f"🖥️ Server: **{server_label}**\n"
        f"💰 Plan: **{PLAN_NAMES.get(plan, PLAN_NAMES['free'])}**\n"
        f"📅 Expires: **{exp[:10] if exp != 'N/A' else 'N/A'}**\n"
        f"🎁 Limit: **{limit}** per post\n"
        f"💎 Balance: **{fb}**\n"
        f"👤 RA Limit: **{ra_lim}** ({ra_src})\n"
        f"{DIV}"
    )


def get_bot_info_text(bot_row):
    """Bot info display"""
    if not bot_row:
        return "❌ Bot not found"
    tok, uname, bid, added = bot_row[:4]
    server = bot_row[4] if len(bot_row) > 4 else "free"
    label = get_server_label(server)
    now = datetime.now()
    st = "🟢 Active"
    if is_bot_flooded(tok, server):
        st = "🌊 Flooded"
    else:
        pool = get_pool(server)
        info = pool.get(tok)
        if (isinstance(info, dict) and info.get("busy_until")
                and info["busy_until"] > now):
            st = "🔴 Busy"
    return (
        f"🤖 **BOT INFO**\n"
        f"{DIV}\n\n"
        f"👤 @{uname}\n"
        f"🆔 `{bid}`\n"
        f"🖥️ Server: **{label}**\n"
        f"📊 Status: **{st}**\n"
        f"📅 Added: **{added[:16] if added else '—'}**\n\n"
        f"{DIV}\n"
        f"🔑 Token: `{tok[:20]}...`"
    )


# ══════════════════════ END OF PART 11 ══════════════════════
D("✅ Part 11 loaded — Message Templates (Server-Aware)", "ok")
# ══════════════════════ /start COMMAND ══════════════════════
@bot.on(events.NewMessage(pattern="/start"))
async def on_start(event):
    try:
        if event.is_channel:
            return
        uid = event.sender_id
        if uid is None:
            return

        # Parse referral code
        text = event.text or ""
        ref_code = None
        if " " in text:
            parts = text.split()
            if len(parts) > 1 and parts[1].startswith("ref_"):
                ref_code = parts[1][4:]

        # Get sender
        try:
            sender = await event.get_sender()
            if sender is None or isinstance(sender, (Channel, Chat)):
                fn, un = "User", None
            else:
                fn = getattr(sender, "first_name", None) or "User"
                un = getattr(sender, "username", None)
        except Exception:
            fn, un = "User", None

        existing = db_get_user(uid)
        is_new = existing is None
        db_save_user(uid, fn, un)

        # Referral
        if is_new and ref_code and feat_referral() and not OWNER_IS(uid):
            rid = db_find_user_by_ref_code(ref_code)
            if rid and rid != uid:
                db_add_referral(rid, uid)

        # Banned
        if db_is_banned(uid):
            await event.reply(get_banned_message(uid))
            return

        # Auto-approve
        auto = is_auto_approve()
        if not OWNER_IS(uid):
            status = db_approval_status(uid)
            if status is None or status == "pending":
                if auto:
                    db_set_approval(uid, "approved",
                                    approved_by=get_owner_id())

        # Force join
        if not await is_joined(uid):
            await event.reply(
                f"{STAR_LINE}\n"
                f"👻 **GHOST REACTION BOT**\n"
                f"{STAR_LINE}\n\n"
                f"🔐 **ACCESS LOCKED**\n\n"
                f"Join all channels to continue!",
                buttons=kb_join())
            return

        # Validate referral
        if feat_referral():
            referrer = db_validate_referral(uid)
            if referrer:
                try:
                    await bot.send_message(
                        referrer,
                        f"🎁 **Referral validated!**\n"
                        f"💰 +{REFERRAL_REWARD + FRIEND_VALID_REWARD} "
                        f"free reactions added!")
                except Exception:
                    pass

        # Owner dashboard
        if OWNER_IS(uid):
            stats = db_bot_stats()
            real_status = real_get_status()
            await event.reply(
                f"{STAR_LINE}\n"
                f"👑 **OWNER DASHBOARD**\n"
                f"{STAR_LINE}\n\n"
                f"🤖 Total Bots: **{stats['total']}**\n"
                f"   🆓 Free: **{stats['free']}**\n"
                f"   💎 Paid: **{stats['paid']}**\n\n"
                f"👥 Users: **{db_total_users()}**\n"
                f"👤 Sessions: **{real_status['available']}/"
                f"{real_status['total']}**\n"
                f"📡 Watchers: **{len(db_list_watchers())}**\n"
                f"⏰ Queue: **{len(db_list_queue(status='pending'))}**\n\n"
                f"{SPARKLE} Welcome back, boss! 👑",
                buttons=kb_welcome(uid))
            return

        # Normal user
        status = db_approval_status(uid)
        if auto or status == "approved":
            await event.reply(
                get_welcome_message(fn, uid, auto_approved=True),
                buttons=kb_welcome(uid))
            return

        if status == "pending":
            await event.reply(
                get_pending_message(uid),
                buttons=kb_request_access(uid))
            return

        if status == "rejected":
            await event.reply(get_rejected_message(uid))
            return

        db_set_approval(uid, "approved", approved_by=get_owner_id())
        await event.reply(
            get_welcome_message(fn, uid, auto_approved=True),
            buttons=kb_welcome(uid))

    except Exception as e:
        D_err(e, "on_start")


# ══════════════════════ MESSAGE HANDLER ══════════════════════
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

        # Save user
        try:
            sender = await event.get_sender()
            if sender is None or isinstance(sender, (Channel, Chat)):
                fn, un = "User", None
            else:
                fn = getattr(sender, "first_name", None) or "User"
                un = getattr(sender, "username", None)
        except Exception:
            fn, un = "User", None

        db_save_user(uid, fn, un)

        if db_is_banned(uid):
            return

        text = (event.text or "").strip()
        if not text:
            return

        # ══════════════════════════════════════════
        # ═════ OWNER STATES ═════
        # ══════════════════════════════════════════
        if OWNER_IS(uid) and uid in USER_STATES:
            state = USER_STATES[uid]
            step = state.get("step")

            # ── Owner info edit ──
            if step == "oi_wait_uname":
                t = text.lstrip("@")
                if not t or len(t) > 32:
                    await event.reply("❌ Invalid username")
                    return
                cfg_set("owner_username", t)
                clear_owner_cache()
                del USER_STATES[uid]
                await event.reply(f"✅ Owner username → @{t}",
                                  buttons=kb_owner())
                return

            if step == "oi_wait_oid":
                if not text.lstrip("-").isdigit():
                    await event.reply("❌ Numeric ID required")
                    return
                cfg_set("owner_id", int(text))
                clear_owner_cache()
                del USER_STATES[uid]
                await event.reply(f"✅ Owner ID → `{text}`",
                                  buttons=kb_owner())
                return

            # ── Coupon flow ──
            if step == "cop_wait_code":
                t = text.upper()
                if len(t) < 3 or len(t) > 30:
                    await event.reply("❌ 3-30 chars")
                    return
                if coupon_get(t):
                    await event.reply("❌ Already exists")
                    return
                state["cop_code"] = t
                state["step"] = "cop_wait_percent"
                USER_STATES[uid] = state
                await event.reply("✏️ Discount % (0 for none):")
                return

            if step == "cop_wait_percent":
                if not text.isdigit():
                    await event.reply("❌ Number required")
                    return
                state["cop_pct"] = int(text)
                state["step"] = "cop_wait_flat"
                USER_STATES[uid] = state
                await event.reply("✏️ Flat Rs (0 for none):")
                return

            if step == "cop_wait_flat":
                if not text.isdigit():
                    await event.reply("❌ Number required")
                    return
                state["cop_flat"] = int(text)
                state["step"] = "cop_wait_max"
                USER_STATES[uid] = state
                await event.reply("✏️ Max uses (0 = unlimited):")
                return

            if step == "cop_wait_max":
                if not text.isdigit():
                    await event.reply("❌ Number required")
                    return
                max_u = int(text)
                code = state.get("cop_code", "NEW")
                pct = state.get("cop_pct", 0)
                flat = state.get("cop_flat", 0)
                coupon_create(code, pct, flat, max_u, None)
                del USER_STATES[uid]
                await event.reply(
                    f"✅ **Coupon created!**\n\n"
                    f"🎟️ Code: `{code}`\n"
                    f"💰 {pct}% + {flat}rs\n"
                    f"📊 Max uses: {max_u if max_u else '∞'}",
                    buttons=kb_coupons_manage())
                return

            # ── Store pack add ──
            if step == "storem_wait_name":
                state["sm_name"] = text[:40]
                state["step"] = "storem_wait_emojis"
                USER_STATES[uid] = state
                await event.reply("✏️ Send emojis (space/comma):")
                return

            if step == "storem_wait_emojis":
                emojis = [p.strip() for p in re.split(r"[,\s]+", text)
                          if p.strip() in ALL_REACTIONS]
                if not emojis:
                    await event.reply("❌ No valid emojis")
                    return
                state["sm_emojis"] = emojis[:30]
                state["step"] = "storem_wait_price"
                USER_STATES[uid] = state
                await event.reply("💰 Price in Rs (0 for free):")
                return

            if step == "storem_wait_price":
                if not text.isdigit():
                    await event.reply("❌ Number required")
                    return
                state["sm_price"] = int(text)
                state["step"] = "storem_wait_desc"
                USER_STATES[uid] = state
                await event.reply("📝 Description (or 'skip'):")
                return

            if step == "storem_wait_desc":
                desc = "" if text.lower() == "skip" else text[:100]
                name = state.get("sm_name", "Pack")
                emojis = state.get("sm_emojis", [])
                price = state.get("sm_price", 0)
                pid = store_add(name, emojis, price, desc)
                del USER_STATES[uid]
                await event.reply(
                    f"✅ **Store pack added!**\n\n"
                    f"🏪 {name}\n"
                    f"💰 {price}rs\n"
                    f"🎨 {len(emojis)} emojis",
                    buttons=kb_store_manage())
                return

            # ── RA limit set ──
            if step == "ra_set_user_limit":
                if not text.lstrip("-").isdigit():
                    await event.reply("❌ Number required")
                    return
                target = state.get("target")
                set_user_ra_limit(target, int(text))
                del USER_STATES[uid]
                await event.reply(
                    f"✅ RA limit set to {text}",
                    buttons=[[btn("🔙",
                                  data=f"um:ra:{target}".encode(),
                                  style="primary")]])
                return

            # ── RA plan edit ──
            if step == "rap_edit_limit":
                if not text.isdigit():
                    await event.reply("❌ Number required")
                    return
                plan = state.get("plan")
                cfg_set(f"plan_ra_limit_{plan}", int(text))
                del USER_STATES[uid]
                await event.reply(
                    f"✅ {PLAN_NAMES[plan]} RA limit → {text}",
                    buttons=kb_ra_plans())
                return

            # ── Plan price edit ──
            if step == "pp_edit_price":
                if not text.isdigit():
                    await event.reply("❌ Number required")
                    return
                plan = state["plan"]
                days = state["days"]
                cfg_set(f"price_{plan}_{days}", text)
                del USER_STATES[uid]
                await event.reply(
                    f"✅ Price updated!",
                    buttons=kb_plan_prices_durations(plan))
                return

            # ── Force channel add ──
            if step == "fc_wait_channel":
                ch = text
                if not ch.startswith("@") and not ch.lstrip("-").isdigit():
                    await event.reply("❌ Send @channel or numeric ID")
                    return
                url = (f"https://t.me/{ch[1:]}"
                       if ch.startswith("@")
                       else f"https://t.me/c/{ch.lstrip('-')}")
                db_add_force_channel(ch, url, ch)
                del USER_STATES[uid]
                await event.reply(f"✅ Added {ch}",
                                  buttons=kb_force_channels())
                return

            # ── Team add ──
            if step == "team_wait_id":
                if not text.lstrip("-").isdigit():
                    await event.reply("❌ Numeric ID required")
                    return
                USER_STATES[uid] = {
                    "step": "team_wait_commission",
                    "target": int(text)
                }
                await event.reply("Commission %:",
                                  buttons=kb_owner())
                return

            if step == "team_wait_commission":
                if not text.isdigit():
                    await event.reply("❌ Number required")
                    return
                db_add_team_member(state["target"], "reseller", int(text))
                del USER_STATES[uid]
                await event.reply("✅ Added",
                                  buttons=kb_team())
                return

            # ── Custom pack add ──
            if step == "cp_wait_name":
                state["cp_name"] = text[:20]
                state["step"] = "cp_wait_emojis"
                USER_STATES[uid] = state
                await event.reply("✏️ Send emojis:")
                return

            if step == "cp_wait_emojis":
                emojis = [p.strip() for p in re.split(r"[,\s]+", text)
                          if p.strip() in ALL_REACTIONS]
                if not emojis:
                    await event.reply("❌ No valid emojis")
                    return
                state["cp_emojis"] = emojis[:30]
                state["step"] = "cp_wait_price"
                USER_STATES[uid] = state
                await event.reply("💰 Price (0 = free):")
                return

            if step == "cp_wait_price":
                if not text.isdigit():
                    await event.reply("❌ Number required")
                    return
                price = int(text)
                db_add_custom_pack(
                    state.get("cp_name", "Custom"),
                    state.get("cp_emojis", []),
                    price, 1 if price > 0 else 0)
                del USER_STATES[uid]
                await event.reply("✅ Created!",
                                  buttons=kb_emoji_packs_manage())
                return

            # ── Broadcast ──
            if step == "wait_bc_text":
                del USER_STATES[uid]
                msg = await event.reply("📢 Broadcasting...")

                async def on_prog(i, t, ok):
                    if i % 5 == 0:
                        try:
                            await msg.edit(
                                f"📢 Progress: {i}/{t} (✅{ok})")
                        except Exception:
                            pass

                ok, fail, total = await broadcast_message(
                    text=text, on_progress=on_prog)
                await msg.edit(
                    f"✅ **BROADCAST DONE**\n"
                    f"{DIV}\n"
                    f"📊 Total: **{total}**\n"
                    f"✅ Success: **{ok}**\n"
                    f"❌ Failed: **{fail}**")
                return

            # ── Set free count ──
            if step == "wait_setfree":
                if not text.isdigit():
                    await event.reply("❌ Number required")
                    return
                cfg_set("free_count", int(text))
                del USER_STATES[uid]
                await event.reply(f"✅ Free count → {text}",
                                  buttons=kb_owner())
                return

            # ── Add user ──
            if step == "wait_add_user_id":
                if not text.lstrip("-").isdigit():
                    await event.reply("❌ Numeric ID required")
                    return
                db_set_approval(int(text), "approved",
                                approved_by=get_owner_id())
                del USER_STATES[uid]
                await event.reply("✅ User approved!",
                                  buttons=kb_owner())
                return

            # ── User limit set ──
            if step == "user_set_limit":
                if not text.isdigit():
                    await event.reply("❌ Number required")
                    return
                target = state.get("target")
                db_set_user_limit(target, int(text))
                del USER_STATES[uid]
                await event.reply("✅ Limit set",
                                  buttons=kb_user_manage(target))
                return

            # ── User balance add ──
            if step == "user_add_balance":
                if not text.lstrip("-").isdigit():
                    await event.reply("❌ Number required")
                    return
                target = state.get("target")
                db_add_free_balance(target, int(text))
                del USER_STATES[uid]
                await event.reply("✅ Balance added",
                                  buttons=kb_user_manage(target))
                return

            # ── Server bulk move ──
            if step == "srv_add_bot_token":
                if ":" not in text or len(text) < 30:
                    await event.reply("❌ Invalid bot token")
                    return
                srv = state.get("server", "free")
                info = bot_get_me(text.strip())
                if not info:
                    await event.reply("❌ Invalid token (getMe failed)")
                    return
                db_add_bot(text.strip(), info["username"], info["id"],
                           server=srv)
                del USER_STATES[uid]
                await event.reply(
                    f"✅ Bot added to {get_server_label(srv)}\n"
                    f"👤 @{info['username']}",
                    buttons=kb_server_panel(srv))
                return

            # ── Server test ──
            if step == "srv_test_token":
                srv = state.get("server", "free")
                tok = text.strip()
                info = bot_get_me(tok)
                if info:
                    await event.reply(
                        f"✅ **Bot OK**\n"
                        f"👤 @{info['username']}\n"
                        f"🆔 `{info['id']}`",
                        buttons=kb_server_panel(srv))
                else:
                    await event.reply("❌ Invalid token")
                return

        # ══════════════════════════════════════════
        # ═════ USER VALIDATION ═════
        # ══════════════════════════════════════════
        if not await is_joined(uid):
            await event.reply("Join all channels first:",
                              buttons=kb_join())
            return

        if not OWNER_IS(uid) and not is_approved(uid):
            status = db_approval_status(uid)
            if status == "rejected":
                await event.reply(get_rejected_message(uid))
                return
            db_set_approval(uid, "approved", approved_by=get_owner_id())

        if uid not in USER_STATES:
            await event.reply("👉 Send /start",
                              buttons=kb_welcome(uid))
            return

        state = USER_STATES[uid]
        step = state.get("step")

        # ══════════════════════════════════════════
        # ═════ USER INPUT FLOWS ═════
        # ══════════════════════════════════════════

        # ── Queue ──
        if step == "queue_wait_chat":
            state["q_chat"] = text
            state["step"] = "queue_wait_post"
            USER_STATES[uid] = state
            await event.reply("✅ Chat saved. Send post link:",
                              buttons=kb_back(uid))
            return

        if step == "queue_wait_post":
            state["q_post"] = text
            state["step"] = "queue_wait_count"
            USER_STATES[uid] = state
            limit = get_user_limit(uid)
            await event.reply(
                f"✅ How many? (max {limit}):",
                buttons=kb_reaction_count(uid))
            return

        # ── Bulk ──
        if step == "bulk_wait_chat":
            state["b_chat"] = text
            state["step"] = "bulk_wait_posts"
            USER_STATES[uid] = state
            await event.reply("✅ Post links (one per line):",
                              buttons=kb_back(uid))
            return

        if step == "bulk_wait_posts":
            posts = [p.strip() for p in re.split(r"[,\n]+", text)
                     if p.strip()]
            if not posts:
                await event.reply("❌ No valid posts")
                return
            state["b_posts"] = posts
            state["step"] = "bulk_wait_count"
            USER_STATES[uid] = state
            await event.reply(
                f"✅ {len(posts)} posts. Per post?:",
                buttons=kb_reaction_count(uid))
            return

        # ── Template ──
        if step == "tpl_wait_name":
            state["tpl_name"] = text[:20]
            state["step"] = "tpl_wait_emojis"
            USER_STATES[uid] = state
            await event.reply("✏️ Send emojis:")
            return

        if step == "tpl_wait_emojis":
            emojis = [p.strip() for p in re.split(r"[,\s]+", text)
                      if p.strip() in ALL_REACTIONS]
            if not emojis:
                await event.reply("❌ No valid emojis")
                return
            db_add_template(uid, state.get("tpl_name", "Template"),
                            emojis[:20])
            del USER_STATES[uid]
            await event.reply("✅ Template saved!",
                              buttons=kb_templates_menu(uid))
            return

        # ── Reaction flow ──
        if step == "wait_channel":
            state["channel_link"] = text
            state["step"] = "wait_post"
            USER_STATES[uid] = state
            await event.reply("✅ Chat saved. Send post link:",
                              buttons=kb_back(uid))
            return

        if step == "wait_post":
            state["post_link"] = text
            state["step"] = "wait_count"
            USER_STATES[uid] = state
            limit = get_user_limit(uid)
            await event.reply(
                f"✅ Post saved. How many? (max {limit}):",
                buttons=kb_reaction_count(uid))
            return

        # ── Custom emoji ──
        if step == "wait_custom_emoji":
            emojis = []
            for p in re.split(r"[,\s]+", text):
                p = p.strip()
                if p and p in ALL_REACTIONS and p not in emojis:
                    emojis.append(p)
            if not emojis:
                await event.reply("❌ No valid emojis",
                                  buttons=kb_back(uid))
                return
            state["custom_emojis"] = emojis[:30]
            state["emoji_mode"] = "custom"
            USER_STATES[uid] = state
            await event.reply("✨ Starting...")
            await _run_reactions(event, uid)
            return

        # ── Watch add ──
        if step == "watch_wait_link":
            state["watch_link"] = text
            state["watch_chat_type"] = state.get("chat_type", "channel")
            state["step"] = "watch_wait_count"
            USER_STATES[uid] = state
            await event.reply("✅ Count per post (1-50):",
                              buttons=kb_back(uid))
            return

        if step == "watch_wait_count":
            if not text.isdigit():
                await event.reply("❌ Number required")
                return
            state["watch_count"] = min(int(text), 50)
            state["step"] = "watch_wait_emoji"
            USER_STATES[uid] = state
            await event.reply(
                f"✅ Count: {state['watch_count']}\n\nEmoji mode:",
                buttons=[
                    [btn("🎯 Default", data=b"watch_emoji:default",
                         style="success")],
                    [btn("✏️ Custom", data=b"watch_emoji:custom",
                         style="primary")],
                    [btn("🔙 Cancel", data=b"watch_flow",
                         style="danger")],
                ])
            return

        if step == "watch_wait_custom_emoji":
            emojis = [p.strip() for p in re.split(r"[,\s]+", text)
                      if p.strip() in ALL_REACTIONS]
            if not emojis:
                await event.reply("❌ No valid emojis")
                return
            state["watch_custom_emojis"] = emojis[:30]
            USER_STATES[uid] = state
            await _finalize_watch_add(event, uid)
            return

        # ── Watch edit ──
        if step == "watch_edit_count":
            if not text.isdigit():
                await event.reply("❌ Number required")
                return
            wid = state.get("wid")
            db_update_watcher(wid, reaction_count=min(int(text), 200))
            del USER_STATES[uid]
            await event.reply(
                "✅ Updated!",
                buttons=[[btn("🔙",
                              data=f"watch:manage:{wid}".encode(),
                              style="primary")]])
            return

        if step == "watch_edit_emoji":
            emojis = [p.strip() for p in re.split(r"[,\s]+", text)
                      if p.strip() in ALL_REACTIONS]
            if not emojis:
                await event.reply("❌ No valid emojis")
                return
            wid = state.get("wid")
            db_update_watcher(wid, emoji_mode="custom",
                              custom_emojis=",".join(emojis[:30]))
            del USER_STATES[uid]
            await event.reply(
                "✅ Updated!",
                buttons=[[btn("🔙",
                              data=f"watch:manage:{wid}".encode(),
                              style="primary")]])
            return

        # ── Default fallback ──
        await event.reply("👉 Use the buttons or /start",
                          buttons=kb_welcome(uid))

    except Exception as e:
        D_err(e, "on_msg")


# ══════════════════════ FINALIZERS ══════════════════════
async def _finalize_watch_add(event, uid):
    try:
        state = USER_STATES.get(uid, {})
        link = state.get("watch_link")
        cty = state.get("watch_chat_type", "channel")
        count = state.get("watch_count", 5)
        custom = state.get("watch_custom_emojis")
        mode = "custom" if custom else "default"
        server = get_user_server(uid)

        try:
            chat_ref, invite = parse_channel_link(link)
            if invite:
                try:
                    await admin_client(ImportChatInviteRequest(invite))
                except Exception:
                    pass
                entity = await safe_get_entity(
                    f"https://t.me/+{invite}",
                    cache_key=f"chat:{invite}")
            else:
                entity = await safe_get_entity(
                    chat_ref, cache_key=f"chat:{chat_ref}")
        except Exception as e:
            await event.reply(f"❌ Resolve failed: {str(e)[:80]}")
            if uid in USER_STATES:
                USER_STATES[uid] = {}
            return

        chat_id = entity.id
        chat_title = getattr(entity, "title", "Unknown")

        for w in db_list_watchers(uid):
            if w[2] == chat_id:
                await event.reply(f"⚠️ Already watching {chat_title}")
                if uid in USER_STATES:
                    USER_STATES[uid] = {}
                return

        try:
            msgs = await asyncio.wait_for(
                admin_client.get_messages(entity, limit=1), timeout=15)
            last = msgs[0].id if msgs else 0
        except Exception:
            last = 0

        db_add_watcher(uid, chat_id, chat_title, link, cty,
                       count, mode, custom, last, server=server)

        await event.reply(
            f"🎉 **WATCH ADDED**\n"
            f"{DIV}\n\n"
            f"📢 {chat_title}\n"
            f"🎯 {count}/post\n"
            f"✏️ {mode}\n"
            f"🖥️ {get_server_label(server)}\n"
            f"🟢 **ACTIVE!**",
            buttons=[
                [btn("📋 My Watches", data=b"watch:list",
                     style="primary")],
                [btn("🏠 Home", data=b"home", style="success")],
            ])
        if uid in USER_STATES:
            USER_STATES[uid] = {}
    except Exception as e:
        D_err(e, "_finalize_watch_add")


async def _run_reactions(event, uid):
    """Launch reaction flow with server-aware mode"""
    global TASK_RUNNING, TASK_OWNER_UID

    now = time.time()
    last = USER_LAST_REQUEST.get(uid, 0)
    if now - last < USER_COOLDOWN:
        wait = int(USER_COOLDOWN - (now - last))
        try:
            await event.answer(f"⏳ Wait {wait}s", alert=True)
        except Exception:
            pass
        return

    if TASK_RUNNING:
        try:
            await safe_edit(event, "⏳ Another task running...",
                            buttons=kb_back(uid))
        except Exception:
            pass
        if uid in USER_STATES:
            USER_STATES[uid] = {}
        return

    state = USER_STATES.get(uid, {})
    cl = state.get("channel_link")
    pl = state.get("post_link")
    count = state.get("reaction_count", 0)
    em = state.get("emoji_mode", "default")
    ce = state.get("custom_emojis")
    chosen_mode = state.get("reaction_mode", "auto")

    if not cl or not pl or count <= 0:
        try:
            await event.answer("❌ Missing data", alert=True)
        except Exception:
            pass
        return

    USER_LAST_REQUEST[uid] = now

    server = get_user_server(uid)
    user_ra_limit, _ = get_user_ra_limit(uid)

    if chosen_mode == "without_admin":
        use_real = (user_has_realaccounts(uid)
                    and real_count_available() > 0
                    and user_ra_limit > 0)
    elif chosen_mode == "with_admin":
        use_real = False
    else:
        use_real = (user_has_realaccounts(uid)
                    and real_count_available() > 0
                    and user_ra_limit > 0)

    TASK_RUNNING = True
    TASK_OWNER_UID = uid
    try:
        if use_real:
            post_ref, msg_id = parse_post_link(pl)
            if not msg_id:
                await safe_edit(event, "❌ Invalid post link",
                                buttons=kb_back(uid))
                return
            chat_ref, invite = parse_channel_link(cl)
            target = post_ref or chat_ref
            if invite and not post_ref:
                try:
                    await admin_client(ImportChatInviteRequest(invite))
                except Exception:
                    pass
                target = f"https://t.me/+{invite}"

            emoji_pool = ce if (em == "custom" and ce) else None
            real_count = min(count, user_ra_limit,
                             real_count_available())

            await safe_edit(
                event,
                f"👤 **WITHOUT ADMIN MODE**\n"
                f"{DIV}\n\n"
                f"🎯 Sending {real_count}\n"
                f"🔓 No admin needed ✅\n"
                f"⚡ Processing...")

            async def on_prog(i, total, ok):
                if i % 5 == 0 or i == total:
                    bar = progress_bar(i, total)
                    try:
                        await event.edit(
                            f"👤 **WITHOUT ADMIN**\n"
                            f"{DIV}\n\n"
                            f"📊 `{bar}` {i}/{total}\n"
                            f"✅ Success: **{ok}**")
                    except Exception:
                        pass

            res = await send_reactions_real(
                target, msg_id, real_count,
                emoji_pool=emoji_pool, on_progress=on_prog)

            bar = progress_bar(res["ok"], max(real_count, 1))
            await safe_edit(
                event,
                f"🎉 **COMPLETE!** 🎉\n"
                f"{STAR_LINE}\n\n"
                f"👤 Mode: **Without Admin**\n"
                f"📩 Post: **#{msg_id}**\n\n"
                f"{DIV}\n"
                f"🎯 Requested: **{real_count}**\n"
                f"✅ Success: **{res['ok']}**\n"
                f"❌ Failed: **{res['fail']}**\n"
                f"🌊 Flooded: **{res['flooded']}**\n"
                f"{DIV}\n\n"
                f"🚀 **{bar}** {res['ok']}/{real_count}",
                buttons=kb_back(uid))
        else:
            await process_reactions_rotating(
                event, uid, cl, pl, count,
                emoji_mode=em, custom_emojis=ce)
    except Exception as e:
        D_err(e, "_run_reactions")
        try:
            await safe_edit(event, f"❌ {str(e)[:100]}",
                            buttons=kb_back(uid))
        except Exception:
            pass
    finally:
        TASK_RUNNING = False
        TASK_OWNER_UID = None


# ══════════════════════ END OF PART 12 ══════════════════════
D("✅ Part 12 loaded — /start + on_msg + Owner States (Server-Aware)", "ok")
# ══════════════════════ USER CALLBACK HANDLER ══════════════════════
@bot.on(events.CallbackQuery)
async def on_cb_user(event):
    try:
        data = event.data.decode()
        uid = event.sender_id
    except Exception:
        return

    try:
        # ══════════════════════════════════════════
        # ═════ SKIP OWNER-ONLY (handled by on_cb_owner) ═════
        # ══════════════════════════════════════════
        if data.startswith(("op:", "um:", "ft:", "pp:", "pf:",
                            "fc:", "team:", "cp:", "cop:", "storem:",
                            "retry:", "gh:", "bc:", "payv:",
                            "bulk:", "ra:", "rap:", "oi:",
                            "srv:", "usrv:", "bot:")):
            return

        # ══════════════════════════════════════════
        # ═════ SUPPORT / HELP ═════
        # ══════════════════════════════════════════
        if data == "support":
            await safe_answer(event, "💬")
            await safe_edit(
                event,
                f"{STAR_LINE}\n"
                f"💬 **SUPPORT**\n"
                f"{STAR_LINE}\n\n"
                f"Contact the owner directly:\n\n"
                f"👑 @{get_owner_username()}\n"
                f"🆔 `{get_owner_id()}`",
                buttons=kb_support(uid))
            return

        # ═════ HELP ═════
        if data == "help":
            await safe_answer(event, "❓")
            await safe_edit(
                event,
                f"{STAR_LINE}\n"
                f"❓ **HELP CENTER**\n"
                f"{STAR_LINE}\n\n"
                f"{DIV}\n"
                f"📖 **Full Guide** — How to make owner admin\n"
                f"👑 **Owner Username** — Get owner's @\n"
                f"🆔 **Owner ID** — Get owner's numeric ID\n"
                f"💬 **Contact** — Direct chat with owner\n"
                f"{DIV}\n\n"
                f"❓ Choose an option below:",
                buttons=kb_help(uid))
            return

        if data == "help_full":
            await safe_answer(event, "📖")
            await safe_edit(event, get_help_text(uid),
                            buttons=kb_help(uid))
            return

        if data == "help_username":
            await safe_answer(event,
                              f"@{get_owner_username()}", alert=True)
            await safe_edit(
                event,
                f"{STAR_LINE}\n"
                f"👑 **OWNER USERNAME**\n"
                f"{STAR_LINE}\n\n"
                f"👤 **@{get_owner_username()}**\n\n"
                f"{DIV}\n"
                f"📋 **How to use:**\n"
                f"1️⃣ Open your channel/group\n"
                f"2️⃣ Administrators → Add Admin\n"
                f"3️⃣ Type: `@{get_owner_username()}`\n"
                f"4️⃣ Give all permissions\n"
                f"5️⃣ Save\n"
                f"{DIV}\n\n"
                f"💡 Tap the username above to copy",
                buttons=[
                    [btn("📖 Full Guide", data=b"help_full",
                         style="success")],
                    [btn("🔙 Back", data=b"help",
                         style="primary")],
                ])
            return

        if data == "help_ownerid":
            await safe_answer(event, f"ID: {get_owner_id()}",
                              alert=True)
            await safe_edit(
                event,
                f"{STAR_LINE}\n"
                f"🆔 **OWNER TELEGRAM ID**\n"
                f"{STAR_LINE}\n\n"
                f"🆔 `{get_owner_id()}`\n\n"
                f"{DIV}\n"
                f"📋 **How to use:**\n"
                f"1️⃣ Open your channel/group\n"
                f"2️⃣ Administrators → Add Admin\n"
                f"3️⃣ Type ID: `{get_owner_id()}`\n"
                f"4️⃣ Give all permissions\n"
                f"5️⃣ Save\n"
                f"{DIV}\n\n"
                f"💡 Tap the ID above to copy",
                buttons=[
                    [btn("📖 Full Guide", data=b"help_full",
                         style="success")],
                    [btn("🔙 Back", data=b"help",
                         style="primary")],
                ])
            return

        # ═════ REQUEST ACCESS ═════
        if data == "request_access":
            if is_auto_approve():
                db_set_approval(uid, "approved",
                                approved_by=get_owner_id())
                await safe_answer(event, "✅ Approved!", alert=True)
                await safe_edit(event, "✅ Approved!",
                                buttons=kb_welcome(uid))
                return
            if db_has_requested(uid):
                await safe_answer(event, "⏳ Already requested",
                                  alert=True)
                return
            try:
                sender = await event.get_sender()
                fn = getattr(sender, "first_name", None) or "User"
                un = getattr(sender, "username", None)
            except Exception:
                fn, un = "User", None
            ok, reason = db_create_approval(uid, fn, un)
            if not ok:
                await safe_answer(event, f"⏳ {reason}", alert=True)
                return
            try:
                await bot.send_message(
                    get_owner_id(),
                    f"🔔 **NEW REQUEST**\n"
                    f"👤 {fn}\n"
                    f"🆔 `{uid}`\n"
                    f"📛 @{un or 'no_username'}",
                    buttons=kb_approval_actions(uid))
            except Exception:
                pass
            await safe_answer(event, "✅ Sent!", alert=True)
            await safe_edit(event,
                            f"{STAR_LINE}\n"
                            f"⏳ **PENDING**\n"
                            f"{STAR_LINE}\n\n"
                            f"Your request has been sent to the owner.\n\n"
                            f"{DIV}\n"
                            f"📞 @{get_owner_username()}\n"
                            f"{DIV}",
                            buttons=kb_request_access(uid))
            return

        # ═════ APPROVE / REJECT (owner) ═════
        if data.startswith("approve:"):
            if not OWNER_IS(uid):
                return
            target = int(data.split(":")[1])
            db_set_approval(target, "approved",
                            approved_by=get_owner_id())
            await safe_answer(event, "✅", alert=True)
            try:
                tu = db_get_user(target)
                tn = tu[1] if tu else "User"
                await bot.send_message(
                    target, get_approved_notify_message(tn, target),
                    buttons=kb_welcome(target))
            except Exception:
                pass
            return

        if data.startswith("reject:"):
            if not OWNER_IS(uid):
                return
            target = int(data.split(":")[1])
            db_set_approval(target, "rejected",
                            approved_by=get_owner_id())
            await safe_answer(event, "❌", alert=True)
            try:
                await bot.send_message(target,
                                       get_rejected_message(target))
            except Exception:
                pass
            return

        # ═════ CHECK JOIN ═════
        if data == "check_join":
            if await is_joined(uid):
                await safe_answer(event, "✅ Verified!", alert=True)
                if feat_referral():
                    db_validate_referral(uid)
                status = db_approval_status(uid)
                auto = is_auto_approve()
                if OWNER_IS(uid) or status == "approved" or auto:
                    await safe_edit(event, "👑 Welcome",
                                    buttons=kb_welcome(uid))
                else:
                    db_set_approval(uid, "approved",
                                    approved_by=get_owner_id())
                    await safe_edit(event, "👑 Welcome",
                                    buttons=kb_welcome(uid))
            else:
                await safe_answer(event, "❌ Join all channels first!",
                                  alert=True)
            return

        # ═════ BAN CHECK ═════
        if db_is_banned(uid):
            await safe_answer(event, "🚫 Banned!", alert=True)
            return

        # ═════ AUTO-APPROVE ═════
        if not OWNER_IS(uid) and not is_approved(uid):
            status = db_approval_status(uid)
            if status == "rejected":
                await safe_answer(event, "❌ Rejected", alert=True)
                await safe_edit(event, get_rejected_message(uid))
                return
            db_set_approval(uid, "approved",
                            approved_by=get_owner_id())

        # ═════ HOME ═════
        if data == "home":
            await safe_answer(event, "🏠")
            await safe_edit(event, "🏠 **MAIN MENU**",
                            buttons=kb_welcome(uid))
            return

        # ═════ INFO ═════
        if data == "info":
            await safe_edit(event, get_user_plan_info_text(uid),
                            buttons=kb_back(uid))
            return

        # ══════════════════════════════════════════
        # ═════ DASHBOARD ═════
        # ══════════════════════════════════════════
        if data == "dashboard":
            s = stats_get(uid)
            if not s or len(s) < 12:
                s = (uid, 0, 0, None, 0, None, 0, 0, 0, None, 100, None)
            total = s[1]
            today = s[2]
            week = s[4]
            ok_c = s[6]
            fail_c = s[7]
            streak = s[8]
            trust = s[10]
            last_a = s[11]
            u = db_get_user_full(uid)
            fb = u[17] if u else 0
            plan = u[15] if u else "free"
            success_rate = int(ok_c / max(1, ok_c + fail_c) * 100)
            can_bonus = ("✅ Available"
                         if bonus_can_claim(uid) else "⏳ Claimed")
            server = get_user_server(uid)
            server_label = get_server_label(server)
            server_bots = db_count_visible_bots(server=server)
            await safe_edit(
                event,
                f"📊 **YOUR DASHBOARD**\n"
                f"{STAR_LINE}\n\n"
                f"👤 ID: `{uid}`\n"
                f"🖥️ Server: **{server_label}** ({server_bots} bots)\n\n"
                f"{DIV}\n"
                f"💫 **Total Sent:** {total}\n"
                f"📅 **Today:** {today}\n"
                f"📆 **This Week:** {week}\n"
                f"✅ **Success:** {ok_c}\n"
                f"❌ **Failed:** {fail_c}\n"
                f"📈 **Success Rate:** {success_rate}%\n"
                f"{DIV}\n"
                f"🔥 **Streak:** {streak} days\n"
                f"🎁 **Daily Bonus:** {can_bonus}\n"
                f"⭐ **Trust Score:** {trust}/100\n"
                f"{DIV}\n"
                f"💰 Plan: **{PLAN_NAMES.get(plan, PLAN_NAMES['free'])}**\n"
                f"💎 Balance: **{fb}**\n"
                f"{DIV}\n"
                f"🕒 Last Active: {last_a[:16] if last_a else '—'}",
                buttons=kb_dashboard(uid))
            return

        # ══════════════════════════════════════════
        # ═════ DAILY BONUS ═════
        # ══════════════════════════════════════════
        if data == "daily_bonus":
            if not feat_daily_bonus():
                await safe_answer(event, "❌ Disabled", alert=True)
                return
            streak = bonus_get_streak(uid)
            can = bonus_can_claim(uid)
            days_left = 7 - (streak % 7) if streak > 0 else 7
            await safe_edit(
                event,
                f"🎁 **DAILY BONUS**\n"
                f"{STAR_LINE}\n\n"
                f"🔥 Your Streak: **{streak}** days\n"
                f"📅 Next streak bonus in: **{days_left}** days\n\n"
                f"{DIV}\n"
                f"💰 Base Bonus: **+1 free reaction**\n"
                f"🎉 7-day Streak: **+5 free reactions**\n"
                f"{DIV}\n\n"
                f"Status: "
                f"{'✅ Ready to claim!' if can else '⏳ Already claimed today'}",
                buttons=kb_daily_bonus(uid))
            return

        if data == "bonus_claim":
            ok, amount, new_streak = bonus_claim(uid)
            if not ok:
                await safe_answer(event, "⏳ Already claimed",
                                  alert=True)
                return
            await safe_answer(event, f"🎁 +{amount}!", alert=True)
            await safe_edit(
                event,
                f"🎉 **BONUS CLAIMED!**\n"
                f"{STAR_LINE}\n\n"
                f"💰 You got: **+{amount}** free reactions\n"
                f"🔥 Streak: **{new_streak}** days\n\n"
                f"💎 Check your balance in Dashboard!",
                buttons=kb_dashboard(uid))
            return

        # ══════════════════════════════════════════
        # ═════ POST HISTORY ═════
        # ══════════════════════════════════════════
        if data == "post_history":
            rows = post_analytics_user(uid, 10)
            txt = f"📜 **POST HISTORY**\n{STAR_LINE}\n\n"
            if not rows:
                txt += "_No posts yet._"
            else:
                for i, r in enumerate(rows, 1):
                    ct, pid, sent, req, dt = r
                    rate = int(sent / max(1, req) * 100)
                    txt += (f"**{i}.** {ct[:25]}\n"
                            f"   📩 #{pid} | 💫 {sent}/{req} ({rate}%)\n"
                            f"   🕒 {dt[:16]}\n\n")
            await safe_edit(event, txt[:4000],
                            buttons=kb_post_history(uid))
            return

        if data == "post_analytics":
            stats = post_analytics_stats(uid)
            await safe_edit(
                event,
                f"📊 **ANALYTICS**\n"
                f"{STAR_LINE}\n\n"
                f"📝 **Total Posts:** {stats['posts']}\n"
                f"💫 **Sent:** {stats['sent']}\n"
                f"🎯 **Requested:** {stats['requested']}\n"
                f"📈 **Success Rate:** {stats['rate']}%\n\n"
                f"{DIV}\n"
                f"Keep sending reactions to improve!",
                buttons=kb_post_history(uid))
            return

        # ══════════════════════════════════════════
        # ═════ EMOJI STORE ═════
        # ══════════════════════════════════════════
        if data == "store_menu":
            if not feat_store():
                await safe_answer(event, "❌ Disabled", alert=True)
                return
            await safe_edit(
                event,
                f"🏪 **EMOJI STORE**\n"
                f"{STAR_LINE}\n\n"
                f"Buy premium emoji packs with your balance!",
                buttons=kb_store(uid))
            return

        if data.startswith("store_view:"):
            pid = int(data.split(":")[1])
            p = store_get(pid)
            if not p:
                await safe_answer(event, "❌ Not found", alert=True)
                return
            _, name, emojis, price, desc, act = p
            owned = store_user_owns(uid, pid)
            await safe_edit(
                event,
                f"🏪 **{name}**\n"
                f"{STAR_LINE}\n\n"
                f"💰 Price: **{price}rs**\n"
                f"📝 {desc or 'No description'}\n\n"
                f"🎨 **Emojis:**\n{emojis[:200]}\n\n"
                f"Status: {'✅ You own this' if owned else '🏪 Not owned'}",
                buttons=kb_store_view(pid, uid))
            return

        if data.startswith("store_buy:"):
            pid = int(data.split(":")[1])
            p = store_get(pid)
            if not p:
                await safe_answer(event, "❌", alert=True)
                return
            _, name, emojis, price, desc, act = p
            u = db_get_user_full(uid)
            fb = u[17] if u else 0
            if fb < price:
                await safe_answer(
                    event, f"❌ Need {price}rs, you have {fb}",
                    alert=True)
                return
            conn = sqlite3.connect(DB_FILE)
            try:
                conn.execute("""UPDATE users SET free_balance =
                    free_balance - ? WHERE user_id=?""", (price, uid))
                conn.commit()
            finally:
                conn.close()
            _dirty()
            store_buy(uid, pid, price)
            await safe_answer(event, "✅ Purchased!", alert=True)
            await safe_edit(
                event,
                f"🎉 **PURCHASED!**\n\n"
                f"🏪 {name}\n"
                f"💰 Paid: {price}rs\n"
                f"💎 New Balance: {fb - price}",
                buttons=kb_store_view(pid, uid))
            return

        if data.startswith("store_use:"):
            pid = int(data.split(":")[1])
            if not store_user_owns(uid, pid):
                await safe_answer(event, "❌ Not owned", alert=True)
                return
            p = store_get(pid)
            if not p:
                await safe_answer(event, "❌", alert=True)
                return
            _, name, emojis, price, desc, act = p
            state = USER_STATES.get(uid, {})
            state["custom_emojis"] = emojis.split(",")[:30]
            state["emoji_mode"] = "custom"
            USER_STATES[uid] = state
            await safe_answer(event, "✅ Loaded!", alert=True)
            await safe_edit(
                event,
                f"✅ **{name}** loaded!\n\n"
                f"Now send reactions to use this pack.",
                buttons=kb_back(uid))
            return

        if data == "store_mine":
            purchases = store_user_purchases(uid)
            txt = f"🛍️ **MY PURCHASES**\n{STAR_LINE}\n\n"
            if not purchases:
                txt += "_No purchases yet._"
            else:
                for p in purchases[:10]:
                    bid, name, emojis, paid, dt = p
                    txt += (f"🏪 **{name or 'Unknown'}**\n"
                            f"   💰 {paid}rs | 🕒 {dt[:16]}\n\n")
            await safe_edit(event, txt[:4000],
                            buttons=kb_store_mine(uid))
            return

        # ══════════════════════════════════════════
        # ═════ QUEUE ═════
        # ══════════════════════════════════════════
        if data == "queue_menu":
            if not feat_queue():
                await safe_answer(event, "💎 PAID!", alert=True)
                return
            await safe_edit(
                event,
                f"⏰ **QUEUE**\n"
                f"{STAR_LINE}\n\n"
                f"Schedule reactions for later!",
                buttons=kb_queue_menu(uid))
            return

        if data == "queue:add":
            USER_STATES[uid] = {
                "step": "queue_wait_chat",
                "chat_type": "channel"
            }
            await safe_edit(event, "⏰ Send chat link:",
                            buttons=kb_back(uid))
            return

        if data == "queue:list":
            jobs = db_list_queue(user_id=uid)
            if not jobs:
                await safe_edit(event, "📋 No jobs.",
                                buttons=kb_queue_menu(uid))
                return
            txt = f"📋 **MY JOBS ({len(jobs)})**\n{DIV}\n\n"
            rows = []
            for j in jobs[:10]:
                qid = j[0]
                rc = j[4]
                st = j[7]
                status = j[8]
                icon = {"pending": "⏳", "done": "✅",
                        "failed": "❌"}.get(status, "•")
                txt += f"{icon} **#{qid}** {rc}x — {status}\n"
                if st:
                    txt += f"   ⏰ {st[:16]}\n"
                if status == "pending":
                    rows.append([btn(f"🗑️ Cancel #{qid}",
                                     data=f"queue:del:{qid}".encode(),
                                     style="danger")])
            rows.append([btn("🔙 Back", data=b"queue_menu",
                             style="primary")])
            await safe_edit(event, txt[:4000], buttons=rows)
            return

        if data.startswith("queue:del:"):
            qid = int(data.split(":")[2])
            db_delete_queue(qid, uid)
            await safe_answer(event, "🗑️ Deleted", alert=True)
            await safe_edit(event, "✅ Deleted",
                            buttons=kb_queue_menu(uid))
            return

        # ══════════════════════════════════════════
        # ═════ BULK ═════
        # ══════════════════════════════════════════
        if data == "bulk_menu":
            if not feat_bulk():
                await safe_answer(event, "💎 PAID!", alert=True)
                return
            await safe_edit(
                event,
                f"📦 **BULK MODE**\n"
                f"{STAR_LINE}\n\n"
                f"Send reactions to multiple posts!",
                buttons=kb_bulk_menu(uid))
            return

        if data == "bulk:multi_post":
            USER_STATES[uid] = {"step": "bulk_wait_chat"}
            await safe_edit(event, "📦 Send chat link:",
                            buttons=kb_back(uid))
            return

        if data == "bulk:list":
            jobs = db_list_bulk_jobs(uid, 10)
            txt = f"📋 **BULK JOBS**\n{DIV}\n\n"
            if not jobs:
                txt += "_No jobs._"
            else:
                for j in jobs:
                    jid, _, jt, total, comp, fail, status, dt, _ = j
                    icon = {"pending": "⏳", "running": "🔄",
                            "done": "✅", "failed": "❌"}.get(status, "•")
                    txt += (f"{icon} **#{jid}** {jt}\n"
                            f"   {comp}/{total} ✅  {fail} ❌\n")
            await safe_edit(event, txt[:4000],
                            buttons=kb_bulk_menu(uid))
            return

        # ══════════════════════════════════════════
        # ═════ TEMPLATES ═════
        # ══════════════════════════════════════════
        if data == "templates_menu":
            if not feat_templates():
                await safe_answer(event, "💎 PAID!", alert=True)
                return
            await safe_edit(
                event,
                f"📝 **TEMPLATES**\n"
                f"{STAR_LINE}\n\n"
                f"Save emoji combinations for quick use!",
                buttons=kb_templates_menu(uid))
            return

        if data == "tpl:new":
            USER_STATES[uid] = {"step": "tpl_wait_name"}
            await safe_edit(event, "📝 Template name:",
                            buttons=kb_back(uid))
            return

        if data.startswith("tpl:use:"):
            tid = int(data.split(":")[2])
            for t in db_list_templates(uid):
                if t[0] == tid:
                    state = USER_STATES.get(uid, {})
                    state["custom_emojis"] = t[2].split(",")
                    state["emoji_mode"] = "custom"
                    USER_STATES[uid] = state
                    await safe_answer(event, "✅ Loaded", alert=True)
                    if state.get("reaction_count"):
                        await _run_reactions(event, uid)
                    else:
                        await safe_edit(
                            event,
                            f"✅ **{t[1]}** loaded!",
                            buttons=kb_back(uid))
                    return
            return

        if data.startswith("tpl:del:"):
            tid = int(data.split(":")[2])
            db_delete_template(tid, uid)
            await safe_answer(event, "🗑️", alert=True)
            await safe_edit(event, "Deleted",
                            buttons=kb_templates_menu(uid))
            return

        # ══════════════════════════════════════════
        # ═════ REFERRAL ═════
        # ══════════════════════════════════════════
        if data == "referral_menu":
            if not feat_referral():
                await safe_answer(event, "❌", alert=True)
                return
            await safe_edit(
                event,
                f"🎁 **REFERRAL**\n"
                f"{STAR_LINE}\n\n"
                f"Invite friends & earn free reactions!",
                buttons=kb_referral_menu(uid))
            return

        if data == "ref:link":
            code = db_get_referral_code(uid) or gen_referral_code(uid)
            try:
                conn = sqlite3.connect(DB_FILE)
                conn.execute(
                    "UPDATE users SET referral_code=? WHERE user_id=?",
                    (code, uid))
                conn.commit()
                conn.close()
                _dirty()
            except Exception:
                pass
            me = await bot.get_me()
            link = f"https://t.me/{me.username}?start=ref_{code}"
            await safe_edit(
                event,
                f"🔗 **YOUR LINK**\n"
                f"{DIV}\n\n"
                f"`{link}`\n\n"
                f"💰 You get **+{REFERRAL_REWARD + FRIEND_VALID_REWARD}**\n"
                f"🎁 Friend gets **+{FRIEND_VALID_REWARD}** too!",
                buttons=kb_referral_menu(uid))
            return

        if data == "ref:stats":
            c, e_earned = db_get_referral_stats(uid)
            await safe_edit(
                event,
                f"📊 **REFERRAL STATS**\n"
                f"{DIV}\n\n"
                f"🎁 Referrals: **{c}**\n"
                f"💰 Earned: **{e_earned}**",
                buttons=kb_referral_menu(uid))
            return

        if data == "ref:leaderboard":
            rows = db_top_referrers(10)
            txt = f"🏆 **LEADERBOARD**\n{DIV}\n\n"
            if not rows:
                txt += "_No referrals yet_"
            else:
                for i, r in enumerate(rows, 1):
                    u_id, fn, cnt, earned = r
                    medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"{i}."
                    txt += (f"{medal} **{fn or 'User'}** — "
                            f"{cnt} refs ({earned} earned)\n")
            await safe_edit(event, txt, buttons=kb_referral_menu(uid))
            return

        # ══════════════════════════════════════════
        # ═════ PLANS ═════
        # ══════════════════════════════════════════
        if data == "plans_menu":
            if not feat_plans():
                await safe_answer(event, "❌ Disabled", alert=True)
                return
            await safe_edit(
                event,
                f"💰 **BUY PLAN**\n"
                f"{STAR_LINE}\n\n"
                f"{DIV}\n"
                f"🥉 Basic — 20/post\n"
                f"🥈 Pro — 50/post\n"
                f"🥇 Premium — 200/post\n"
                f"{DIV}\n\n"
                f"💎 Unlock premium features!\n"
                f"💎 Premium unlocks PAID server!\n\n"
                f"Choose a plan:",
                buttons=kb_plans_menu(uid))
            return

        if data.startswith("plan:"):
            plan_key = data.split(":")[1]
            if plan_key == "free":
                db_set_user_plan(uid, "free", 9999)
                await safe_answer(event, "✅ Free active", alert=True)
                await safe_edit(event, "✅ **FREE PLAN**",
                                buttons=kb_welcome(uid))
                return
            if plan_key not in PLAN_LIMITS:
                return
            await safe_edit(
                event,
                f"{PLAN_NAMES[plan_key]}\n"
                f"{DIV}\n\n"
                f"🎁 Limit: **{PLAN_LIMITS[plan_key]}/post**\n"
                f"🖥️ Server: **💎 PAID**\n\n"
                f"Choose duration:",
                buttons=kb_plan_durations(plan_key, uid))
            return

        if data.startswith("pland:"):
            parts = data.split(":")
            plan_key = parts[1]
            days = int(parts[2])
            if plan_key not in PLAN_LIMITS:
                return
            price = get_plan_price(plan_key, days)
            await safe_edit(
                event,
                f"💰 **ORDER SUMMARY**\n"
                f"{STAR_LINE}\n\n"
                f"📦 **{PLAN_NAMES[plan_key]}**\n"
                f"📅 Duration: **{DURATIONS[days]}**\n"
                f"💰 Price: **{price}rs**\n"
                f"🖥️ Server: **💎 PAID**\n\n"
                f"{DIV}\n"
                f"📞 Contact the owner to purchase:\n\n"
                f"👑 @{get_owner_username()}",
                buttons=[
                    [btn("💬 Contact Owner",
                         url=f"https://t.me/{get_owner_username()}",
                         style="success")],
                    [btn("🔙 Back", data=b"plans_menu",
                         style="primary")],
                ])
            return

        # ══════════════════════════════════════════
        # ═════ LANGUAGE ═════
        # ══════════════════════════════════════════
        if data == "lang_menu":
            if not feat_multilang():
                await safe_answer(event, "❌ Disabled", alert=True)
                return
            await safe_edit(
                event,
                f"🌍 **CHOOSE LANGUAGE**\n"
                f"{DIV}\n\n"
                f"Current: **{L(uid, 'language')}**",
                buttons=kb_lang_menu(uid))
            return

        if data.startswith("lang:"):
            code = data.split(":")[1]
            if code not in LANGUAGES:
                return
            db_set_user_lang(uid, code)
            await safe_answer(event, f"✅ {LANGUAGES[code]}",
                              alert=True)
            await safe_edit(
                event,
                f"✅ Language changed to **{LANGUAGES[code]}**!",
                buttons=kb_welcome(uid))
            return

        # ══════════════════════════════════════════
        # ═════ NOTIFICATIONS ═════
        # ══════════════════════════════════════════
        if data == "notif_menu":
            if not feat_notifications():
                await safe_answer(event, "❌ Disabled", alert=True)
                return
            unread = db_count_unread_notifications(uid)
            await safe_edit(
                event,
                f"🔔 **NOTIFICATIONS**\n"
                f"{DIV}\n\n"
                f"📬 Unread: **{unread}**",
                buttons=kb_notif_menu(uid))
            return

        if data == "notif:list":
            notifs = db_get_notifications(uid, 10)
            txt = f"📬 **NOTIFICATIONS**\n{DIV}\n\n"
            if not notifs:
                txt += "_None_"
            for n in notifs:
                icon = "📭" if n[2] else "📬"
                txt += (f"{icon} {n[1][:100]}\n"
                        f"   🕒 {n[3][:16]}\n\n")
            await safe_edit(event, txt[:4000],
                            buttons=kb_notif_menu(uid))
            return

        if data == "notif:read":
            db_mark_notifications_read(uid)
            await safe_answer(event, "✅", alert=True)
            await safe_edit(event, "✅ All marked read",
                            buttons=kb_notif_menu(uid))
            return

        if data == "notif:clear":
            db_clear_notifications(uid)
            await safe_answer(event, "🗑️ Cleared", alert=True)
            await safe_edit(event, "🗑️ All notifications cleared",
                            buttons=kb_notif_menu(uid))
            return

        # ══════════════════════════════════════════
        # ═════ REACTION MODE ═════
        # ══════════════════════════════════════════
        if data == "react_flow":
            if not feat_manual():
                await safe_answer(event, "💎 PAID!", alert=True)
                return
            server = get_user_server(uid)
            server_label = get_server_label(server)
            server_bots = db_count_visible_bots(server=server)
            await safe_edit(
                event,
                f"🎯 **SEND REACTIONS**\n"
                f"{STAR_LINE}\n\n"
                f"🖥️ Your Server: **{server_label}**\n"
                f"🤖 Available: **{server_bots}** bots\n\n"
                f"**Choose your mode:**\n\n"
                f"👑 **With Admin** — Bots handle it\n"
                f"   _Owner must be admin in your chat_\n\n"
                f"🔓 **Without Admin** — Real accounts\n"
                f"   _No admin needed, faster_ 💎",
                buttons=kb_mode_choice(uid))
            return

        if data == "mode:with":
            USER_STATES[uid] = {
                "step": "wait_chat_type",
                "reaction_mode": "with_admin"
            }
            await safe_edit(
                event,
                f"👑 **WITH ADMIN MODE**\n"
                f"{DIV}\n\n"
                f"✅ Bots will send reactions\n"
                f"⚠️ Owner must be admin\n\n"
                f"Choose chat type:",
                buttons=kb_chat_type(uid))
            return

        if data == "mode:without":
            if not user_has_realaccounts(uid):
                await safe_answer(event, "💎 PAID feature!",
                                  alert=True)
                await safe_edit(
                    event,
                    f"🔓 **WITHOUT ADMIN — PAID**\n"
                    f"{DIV}\n\n"
                    f"❌ Not available in your plan\n\n"
                    f"💎 Upgrade to unlock:\n"
                    f"• Basic: 3 accounts\n"
                    f"• Pro: 8 accounts\n"
                    f"• Premium: 20 accounts",
                    buttons=kb_plans_menu(uid))
                return
            if real_count_available() <= 0:
                await safe_answer(event, "⚠️ All busy", alert=True)
                await safe_edit(
                    event,
                    f"🔓 **WITHOUT ADMIN**\n"
                    f"{DIV}\n\n"
                    f"⚠️ All accounts busy. Try 1-2 min later.\n\n"
                    f"Or use 👑 With Admin mode",
                    buttons=[
                        [btn("👑 With Admin", data=b"mode:with",
                             style="primary")],
                        [btn("🔙 Back", data=b"react_flow",
                             style="danger")],
                    ])
                return
            ra_lim, _ = get_user_ra_limit(uid)
            USER_STATES[uid] = {
                "step": "wait_chat_type",
                "reaction_mode": "without_admin"
            }
            await safe_edit(
                event,
                f"🔓 **WITHOUT ADMIN MODE**\n"
                f"{DIV}\n\n"
                f"✅ No admin needed\n"
                f"👥 Available: **{real_count_available()}**\n"
                f"⚙️ Your limit: **{ra_lim}**\n\n"
                f"Choose chat type:",
                buttons=kb_chat_type(uid))
            return

        if data == "chattype:channel":
            state = USER_STATES.get(uid, {})
            state["chat_type"] = "channel"
            state["step"] = "wait_channel"
            USER_STATES[uid] = state
            await safe_edit(event, "📢 Send channel link:",
                            buttons=kb_back(uid))
            return

        if data == "chattype:group":
            state = USER_STATES.get(uid, {})
            state["chat_type"] = "group"
            state["step"] = "wait_channel"
            USER_STATES[uid] = state
            await safe_edit(event, "👥 Send group link:",
                            buttons=kb_back(uid))
            return

        # ══════════════════════════════════════════
        # ═════ EMOJI MODE ═════
        # ══════════════════════════════════════════
        if data == "emoji:default":
            state = USER_STATES.get(uid, {})
            state["emoji_mode"] = "default"
            state["custom_emojis"] = None
            USER_STATES[uid] = state
            await safe_answer(event, "🎯", alert=True)
            await _run_reactions(event, uid)
            return

        if data == "emoji:custom":
            if not feat_custom_emoji():
                await safe_answer(event, "💎 PAID!", alert=True)
                return
            state = USER_STATES.get(uid, {})
            state["step"] = "wait_custom_emoji"
            USER_STATES[uid] = state
            await safe_edit(
                event,
                f"✏️ **CUSTOM EMOJI**\n{DIV}\n\n"
                f"Send emojis separated by space or comma:\n"
                f"_Example: ❤️ 🔥 😍_",
                buttons=kb_back(uid))
            return

        if data == "emoji:packs":
            await safe_edit(
                event,
                f"🎨 **EMOJI PACKS**\n{DIV}",
                buttons=kb_emoji_packs(uid))
            return

        if data.startswith("pack:"):
            pkey = data.split(":")[1]
            if pkey not in EMOJI_PACKS:
                return
            state = USER_STATES.get(uid, {})
            state["custom_emojis"] = EMOJI_PACKS[pkey]
            state["emoji_mode"] = "custom"
            USER_STATES[uid] = state
            await safe_answer(event, f"✅ {pkey.title()}", alert=True)
            if state.get("reaction_count"):
                await _run_reactions(event, uid)
            else:
                await safe_edit(event, "✅ Loaded",
                                buttons=kb_back(uid))
            return

        if data.startswith("cpack:"):
            cpid = int(data.split(":")[1])
            for p in db_list_custom_packs():
                if p[0] == cpid:
                    state = USER_STATES.get(uid, {})
                    state["custom_emojis"] = p[2].split(",")
                    state["emoji_mode"] = "custom"
                    USER_STATES[uid] = state
                    await safe_answer(event, "✅", alert=True)
                    if state.get("reaction_count"):
                        await _run_reactions(event, uid)
                    else:
                        await safe_edit(event, "✅ Loaded",
                                        buttons=kb_back(uid))
                    return
            return

        if data == "emoji:templates":
            await safe_edit(
                event,
                f"📝 **TEMPLATES**\n{DIV}",
                buttons=kb_templates_menu(uid))
            return

        # ══════════════════════════════════════════
        # ═════ REACTION COUNT ═════
        # ══════════════════════════════════════════
        if data == "rc:all":
            if not OWNER_IS(uid):
                return
            server = get_user_server(uid)
            count = db_count_visible_bots(server=server)
            state = USER_STATES.get(uid, {})
            state["reaction_count"] = count
            USER_STATES[uid] = state
            await safe_answer(event, f"✅ ALL {count}", alert=True)
            await safe_edit(
                event,
                f"🎯 Count: **{count}**\n\nEmoji mode:",
                buttons=kb_emoji_choice(uid))
            return

        if data.startswith("rc:"):
            try:
                count = int(data.split(":")[1])
            except Exception:
                return
            server = get_user_server(uid)
            visible = db_count_visible_bots(server=server)
            if not OWNER_IS(uid):
                limit = get_user_limit(uid)
                if count > limit:
                    await safe_answer(event, f"❌ Max {limit}",
                                      alert=True)
                    return
            actual = min(count, visible)
            await safe_answer(event, f"✅ {actual}", alert=True)
            state = USER_STATES.get(uid, {})
            state["reaction_count"] = actual
            USER_STATES[uid] = state
            await safe_edit(
                event,
                f"🎯 Count: **{actual}**\n\nEmoji mode:",
                buttons=kb_emoji_choice(uid))
            return

        if data == "rc_more":
            limit = get_user_limit(uid)
            await safe_answer(event, f"💎 Max {limit}", alert=True)
            await safe_edit(
                event,
                f"💎 **UPGRADE TO UNLOCK MORE**\n"
                f"{DIV}\n\n"
                f"Current limit: **{limit}/post**\n\n"
                f"Upgrade to send more reactions!",
                buttons=kb_plans_menu(uid))
            return

        # ══════════════════════════════════════════
        # ═════ AUTO-WATCH ═════
        # ══════════════════════════════════════════
        if data == "watch_flow":
            if not feat_autowatch():
                await safe_answer(event, "💎 PAID!", alert=True)
                return
            watchers = db_list_watchers(uid)
            await safe_edit(
                event,
                f"📡 **AUTO-WATCH**\n"
                f"{STAR_LINE}\n\n"
                f"Automatically react to new posts!\n\n"
                f"📊 Active: **{sum(1 for w in watchers if w[10])}**",
                buttons=kb_watch_menu(uid))
            return

        if data == "watch:add":
            USER_STATES[uid] = {"step": "watch_wait_chat_type"}
            await safe_edit(
                event,
                f"📡 **ADD WATCH**\n{DIV}\n\n"
                f"Choose chat type:",
                buttons=[
                    [btn("📢 Channel",
                         data=b"watch:chattype:channel",
                         style="primary")],
                    [btn("👥 Group",
                         data=b"watch:chattype:group",
                         style="success")],
                    [btn("🔙 Cancel", data=b"watch_flow",
                         style="danger")],
                ])
            return

        if data == "watch:chattype:channel":
            USER_STATES[uid] = {
                "step": "watch_wait_link",
                "chat_type": "channel"
            }
            await safe_edit(event, "📢 Send channel link:",
                            buttons=kb_back(uid))
            return

        if data == "watch:chattype:group":
            USER_STATES[uid] = {
                "step": "watch_wait_link",
                "chat_type": "group"
            }
            await safe_edit(event, "👥 Send group link:",
                            buttons=kb_back(uid))
            return

        if data == "watch:list":
            watchers = db_list_watchers(
                uid if not OWNER_IS(uid) else None)
            if not watchers:
                await safe_edit(event, "📋 No watchers.",
                                buttons=kb_watch_menu(uid))
                return
            txt = f"📋 **WATCHES ({len(watchers)})**\n{DIV}\n\n"
            rows = []
            for w in watchers[:10]:
                wid = w[0]
                ct = w[3]
                rc = w[6]
                act = w[10]
                st = "🟢" if act else "🔴"
                txt += f"{st} **#{wid}** {ct[:25]} • {rc}x\n"
                rows.append([
                    btn(f"⚙️ #{wid} {ct[:15]}",
                        data=f"watch:manage:{wid}".encode(),
                        style="primary")
                ])
            rows.append([btn("🔙 Back", data=b"watch_flow",
                             style="primary")])
            await safe_edit(event, txt[:4000], buttons=rows)
            return

        if data.startswith("watch:manage:"):
            wid = int(data.split(":")[2])
            w = db_get_watcher(wid)
            if not w or (not OWNER_IS(uid) and w[1] != uid):
                await safe_answer(event, "❌", alert=True)
                return
            wid, wuid, cid, ct, cl, cty, rc, em, ce, lpid, act, cr, lr, sv = w
            st = "🟢 ACTIVE" if act else "🔴 PAUSED"
            last_run_txt = lr[:16] if lr else "Never"
            await safe_edit(
                event,
                f"📡 **WATCH #{wid}**\n"
                f"{DIV}\n\n"
                f"📢 {ct}\n"
                f"🎯 {rc} reactions/post\n"
                f"✏️ Emoji: {em}\n"
                f"📊 Last post: #{lpid}\n"
                f"🕒 Last run: {last_run_txt}\n"
                f"🖥️ Server: {get_server_label(sv)}\n"
                f"🔄 Status: {st}",
                buttons=[
                    [btn("🔴 OFF" if act else "🟢 ON",
                         data=f"watch:toggle:{wid}".encode(),
                         style="danger" if act else "success")],
                    [btn("✏️ Count",
                         data=f"watch:edit_count:{wid}".encode(),
                         style="primary")],
                    [btn("✏️ Emoji",
                         data=f"watch:edit_emoji:{wid}".encode(),
                         style="primary")],
                    [btn("🗑️ Delete",
                         data=f"watch:delete:{wid}".encode(),
                         style="danger")],
                    [btn("🔙 Back", data=b"watch:list",
                         style="primary")],
                ])
            return

        if data.startswith("watch:toggle:"):
            wid = int(data.split(":")[2])
            w = db_get_watcher(wid)
            if not w or (not OWNER_IS(uid) and w[1] != uid):
                return
            new_state = 0 if w[10] else 1
            db_update_watcher(wid, is_active=new_state)
            await safe_answer(
                event, "🟢 ON" if new_state else "🔴 OFF", alert=True)
            await safe_edit(
                event, "✅ Updated",
                buttons=[[btn("🔙",
                              data=f"watch:manage:{wid}".encode(),
                              style="primary")]])
            return

        if data.startswith("watch:edit_count:"):
            wid = int(data.split(":")[2])
            USER_STATES[uid] = {"step": "watch_edit_count", "wid": wid}
            await safe_edit(event, "✏️ Count (1-200):",
                            buttons=kb_back(uid))
            return

        if data.startswith("watch:edit_emoji:"):
            wid = int(data.split(":")[2])
            await safe_edit(
                event,
                f"✏️ **EMOJI MODE**\n{DIV}\n\nChoose:",
                buttons=[
                    [btn("🎯 Default",
                         data=f"watch:emoji:default:{wid}".encode(),
                         style="success")],
                    [btn("✏️ Custom",
                         data=f"watch:emoji:custom:{wid}".encode(),
                         style="primary")],
                    [btn("🔙 Back",
                         data=f"watch:manage:{wid}".encode(),
                         style="danger")],
                ])
            return

        if data.startswith("watch:emoji:default:"):
            wid = int(data.split(":")[3])
            db_update_watcher(wid, emoji_mode="default",
                              custom_emojis=None)
            await safe_answer(event, "✅", alert=True)
            await safe_edit(
                event, "✅ Default emoji set",
                buttons=[[btn("🔙",
                              data=f"watch:manage:{wid}".encode(),
                              style="primary")]])
            return

        if data.startswith("watch:emoji:custom:"):
            wid = int(data.split(":")[3])
            USER_STATES[uid] = {
                "step": "watch_edit_emoji",
                "wid": wid
            }
            await safe_edit(event, "✏️ Send emojis:",
                            buttons=kb_back(uid))
            return

        if data.startswith("watch:delete:"):
            wid = int(data.split(":")[2])
            w = db_get_watcher(wid)
            if not w or (not OWNER_IS(uid) and w[1] != uid):
                return
            db_delete_watcher(wid)
            await safe_answer(event, "🗑️ Deleted", alert=True)
            await safe_edit(event, "✅ Deleted",
                            buttons=kb_watch_menu(uid))
            return

        if data == "watch_emoji:default":
            state = USER_STATES.get(uid, {})
            state["watch_custom_emojis"] = None
            USER_STATES[uid] = state
            await safe_answer(event, "🎯", alert=True)
            await _finalize_watch_add(event, uid)
            return

        if data == "watch_emoji:custom":
            state = USER_STATES.get(uid, {})
            state["step"] = "watch_wait_custom_emoji"
            USER_STATES[uid] = state
            await safe_edit(event, "✏️ Send emojis:",
                            buttons=kb_back(uid))
            return

        # ═════ Unknown ═════
        await safe_answer(event, "⚠️ Not implemented", alert=True)

    except Exception as e:
        D_err(e, "on_cb_user")
        try:
            await safe_answer(event, "❌ Error", alert=True)
        except Exception:
            pass


# ══════════════════════ END OF PART 13 ══════════════════════
D("✅ Part 13 loaded — User Callbacks (Server-Aware)", "ok")
# ══════════════════════ OWNER CALLBACK HANDLER ══════════════════════
@bot.on(events.CallbackQuery)
async def on_cb_owner(event):
    try:
        data = event.data.decode()
        uid = event.sender_id
    except Exception:
        return

    # ═════ OWNER-ONLY GUARD ═════
    owner_prefixes = (
        "op:", "um:", "ft:", "pp:", "pf:", "fc:", "team:",
        "cp:", "cop:", "storem:", "retry:", "gh:", "bc:",
        "payv:", "ra:", "rap:", "oi:", "bulk:",
        "srv:", "usrv:", "bot:",
    )
    if not data.startswith(owner_prefixes) and data != "owner_panel":
        return

    if not OWNER_IS(uid):
        await safe_answer(event, "❌ Owner only", alert=True)
        return

    try:
        # ══════════════════════════════════════════
        # ═════ MAIN OWNER PANEL ═════
        # ══════════════════════════════════════════
        if data == "owner_panel":
            await safe_answer(event, "👑")
            stats = db_bot_stats()
            real_status = real_get_status()
            fs = get_pool_status("free")
            ps = get_pool_status("paid")
            await safe_edit(
                event,
                f"👑 **OWNER PANEL**\n"
                f"{STAR_LINE}\n\n"
                f"🖥️ **DUAL SERVER**\n"
                f"   🆓 Free: {stats['free']} | 💎 Paid: {stats['paid']}\n"
                f"   🔒 Permanent: {stats['permanent']}\n\n"
                f"📊 **POOL STATUS**\n"
                f"   🆓 F: 🟢{fs['free']} 🔴{fs['busy']} 🌊{fs['flooded']}\n"
                f"   💎 P: 🟢{ps['free']} 🔴{ps['busy']} 🌊{ps['flooded']}\n\n"
                f"👥 Users: **{db_total_users()}**\n"
                f"💫 Reactions: **{db_total_reactions()}**\n"
                f"📅 Today: **{db_reactions_today()}**\n"
                f"👤 Sessions: **{real_status['available']}/"
                f"{real_status['total']}**\n"
                f"📡 Watchers: **{len(db_list_watchers())}**\n"
                f"⏰ Queue: **{len(db_list_queue(status='pending'))}**\n"
                f"🎟️ Coupons: **{len(coupon_list())}**\n"
                f"🏪 Store: **{store_count_active()}**\n"
                f"🔓 Auto: **{'✅' if is_auto_approve() else '❌'}**\n"
                f"🎁 Free: **{get_free_count()}**",
                buttons=kb_owner())
            return

        # ══════════════════════════════════════════
        # ═════ SERVER MANAGEMENT 🔥 ═════
        # ══════════════════════════════════════════
        if data.startswith("srv:panel:"):
            server = data.split(":")[2]
            pool = get_pool_status(server)
            label = get_server_label(server)
            await safe_edit(
                event,
                f"{label} **SERVER**\n"
                f"{STAR_LINE}\n\n"
                f"🤖 Total: **{pool['total']}** bots\n"
                f"🟢 Free: **{pool['free']}**\n"
                f"🔴 Busy: **{pool['busy']}**\n"
                f"🌊 Flooded: **{pool['flooded']}**\n"
                f"🔒 Permanent: **{pool['permanent']}**\n\n"
                f"{DIV}\n"
                f"Manage bots on this server:",
                buttons=kb_server_panel(server))
            return

        if data.startswith("srv:refresh:"):
            server = data.split(":")[2]
            await safe_answer(event, "🔄", alert=True)
            pool = get_pool_status(server)
            label = get_server_label(server)
            await safe_edit(
                event,
                f"{label} **SERVER**\n"
                f"{STAR_LINE}\n\n"
                f"🤖 Total: **{pool['total']}**\n"
                f"🟢 Free: **{pool['free']}**\n"
                f"🔴 Busy: **{pool['busy']}**\n"
                f"🌊 Flooded: **{pool['flooded']}**",
                buttons=kb_server_panel(server))
            return

        if data.startswith("srv:list:"):
            parts = data.split(":")
            server = parts[2]
            page = int(parts[3]) if len(parts) > 3 else 0
            bots = db_list_visible_bots(server=server)
            total = len(bots)
            await safe_answer(event, f"📋 {total} bots", alert=True)
            await safe_edit(
                event,
                f"📋 **{get_server_label(server)} BOTS** "
                f"({total})\n{DIV}",
                buttons=kb_bot_list(server, page))
            return

        if data.startswith("srv:clear_floods:"):
            server = data.split(":")[2]
            flood_map = get_flood_map(server)
            n = len(flood_map)
            flood_map.clear()
            if server == "free":
                FLOOD_UNTIL.pop if False else None
            await safe_answer(event, f"🌊 Cleared {n}", alert=True)
            await safe_edit(
                event,
                f"✅ Cleared {n} floods on "
                f"{get_server_label(server)}",
                buttons=kb_server_panel(server))
            return

        if data.startswith("srv:reset:"):
            server = data.split(":")[2]
            op, of = reset_bot_pool(server)
            await safe_answer(event, "🧹 Reset", alert=True)
            await safe_edit(
                event,
                f"🧹 **RESET {get_server_label(server)}**\n\n"
                f"Cleared {op} busy bots\n"
                f"Cleared {of} floods",
                buttons=kb_server_panel(server))
            return

        if data.startswith("srv:move_all:"):
            server = data.split(":")[2]
            other = "paid" if server == "free" else "free"
            bots = db_list_visible_bots(server=server)
            moved = 0
            for b in bots:
                tok = b[0]
                if db_move_bot_server(tok, other):
                    moved += 1
            await safe_answer(event, f"🔀 {moved} moved", alert=True)
            await safe_edit(
                event,
                f"✅ Moved {moved} bots\n"
                f"From: {get_server_label(server)}\n"
                f"To: {get_server_label(other)}",
                buttons=[
                    [btn(f"🔙 {get_server_label(server)}",
                         data=f"srv:panel:{server}".encode(),
                         style="primary")],
                    [btn(f"👉 {get_server_label(other)}",
                         data=f"srv:panel:{other}".encode(),
                         style="success")],
                ])
            return

        if data.startswith("srv:bulk_move:"):
            server = data.split(":")[2]
            await safe_edit(
                event,
                f"📦 **BULK MOVE**\n"
                f"{DIV}\n\n"
                f"From: {get_server_label(server)}\n"
                f"Choose option:",
                buttons=kb_bulk_move(server))
            return

        if data.startswith("srv:move_flooded:"):
            server = data.split(":")[2]
            other = "paid" if server == "free" else "free"
            flood_map = get_flood_map(server)
            bots = db_list_visible_bots(server=server)
            moved = 0
            for b in bots:
                if b[0] in flood_map:
                    if db_move_bot_server(b[0], other):
                        moved += 1
                        flood_map.pop(b[0], None)
            await safe_answer(event, f"🔀 {moved}", alert=True)
            await safe_edit(
                event,
                f"✅ Moved {moved} flooded bots → "
                f"{get_server_label(other)}",
                buttons=kb_server_panel(server))
            return

        if data.startswith("srv:move_busy:"):
            server = data.split(":")[2]
            other = "paid" if server == "free" else "free"
            pool = get_pool(server)
            bots = db_list_visible_bots(server=server)
            moved = 0
            now = datetime.now()
            for b in bots:
                info = pool.get(b[0])
                if (isinstance(info, dict) and info.get("busy_until")
                        and info["busy_until"] > now):
                    if db_move_bot_server(b[0], other):
                        moved += 1
                        pool.pop(b[0], None)
            await safe_answer(event, f"🔀 {moved}", alert=True)
            await safe_edit(
                event,
                f"✅ Moved {moved} busy bots → "
                f"{get_server_label(other)}",
                buttons=kb_server_panel(server))
            return

        if data.startswith("srv:add_bot:"):
            server = data.split(":")[2]
            USER_STATES[uid] = {
                "step": "srv_add_bot_token",
                "server": server
            }
            await safe_edit(
                event,
                f"➕ **ADD BOT TO {get_server_label(server)}**\n"
                f"{DIV}\n\n"
                f"Send bot token (from @BotFather):\n"
                f"_Format:_ `123456:ABC-DEF...`",
                buttons=[[btn("🔙 Cancel",
                              data=f"srv:panel:{server}".encode(),
                              style="danger")]])
            return

        if data.startswith("srv:test_all:"):
            server = data.split(":")[2]
            await safe_answer(event, "🧪 Testing...", alert=True)
            bots = db_list_visible_bots(server=server)
            if not bots:
                await safe_edit(event, "❌ No bots",
                                buttons=kb_server_panel(server))
                return
            msg = await event.edit(
                f"🧪 Testing {len(bots)} bots...")
            results = []
            for i, b in enumerate(bots[:20], 1):
                tok, uname = b[0], b[1]
                info = bot_get_me(tok)
                if info:
                    results.append(f"✅ @{uname}")
                else:
                    results.append(f"❌ @{uname}")
                if i % 5 == 0:
                    try:
                        await msg.edit(
                            f"🧪 Testing... {i}/{min(20, len(bots))}\n\n"
                            + "\n".join(results[-5:]))
                    except Exception:
                        pass
            final = (f"🧪 **TEST RESULTS**\n"
                     f"{DIV}\n\n" + "\n".join(results))
            try:
                await msg.edit(final[:4000],
                               buttons=kb_server_panel(server))
            except Exception:
                pass
            return

        if data.startswith("bot:info:"):
            parts = data.split(":", 3)
            if len(parts) < 4:
                return
            server = parts[2]
            tok_prefix = parts[3]
            # Find bot by prefix
            bots = db_list_bots(server=server)
            found = None
            for b in bots:
                if b[0].startswith(tok_prefix):
                    found = b
                    break
            if not found:
                await safe_answer(event, "❌ Not found", alert=True)
                return
            tok, uname, bid, added = found[0], found[1], found[2], found[3]
            now = datetime.now()
            flood_map = get_flood_map(server)
            pool = get_pool(server)
            if tok in flood_map and flood_map[tok] > now:
                st = "🌊 Flooded"
            else:
                info = pool.get(tok)
                if (isinstance(info, dict) and info.get("busy_until")
                        and info["busy_until"] > now):
                    st = "🔴 Busy"
                else:
                    st = "🟢 Active"
            other = "paid" if server == "free" else "free"
            await safe_edit(
                event,
                f"🤖 **BOT INFO**\n"
                f"{DIV}\n\n"
                f"👤 @{uname}\n"
                f"🆔 `{bid}`\n"
                f"🖥️ Server: **{get_server_label(server)}**\n"
                f"📊 Status: **{st}**\n"
                f"📅 Added: **{added[:16] if added else '—'}**\n\n"
                f"🔑 `{tok[:25]}...`",
                buttons=[
                    [btn(f"🔀 Move to {get_server_label(other)}",
                         data=f"bot:move:{server}:{uname}".encode(),
                         style="primary")],
                    [btn("🌊 Reset Flood",
                         data=f"bot:reset:{server}:{uname}".encode(),
                         style="success")],
                    [btn("🗑️ Remove",
                         data=f"bot:del:{server}:{uname}".encode(),
                         style="danger")],
                    [btn("🔙 Back",
                         data=f"srv:list:{server}".encode(),
                         style="primary")],
                ])
            return

        if data.startswith("bot:move:"):
            parts = data.split(":")
            server = parts[2]
            uname = parts[3]
            other = "paid" if server == "free" else "free"
            bots = db_list_bots(server=server)
            for b in bots:
                if b[1] == uname:
                    db_move_bot_server(b[0], other)
                    await safe_answer(event, f"✅ → {other}", alert=True)
                    await safe_edit(
                        event,
                        f"✅ @{uname} moved to "
                        f"{get_server_label(other)}",
                        buttons=kb_server_panel(server))
                    return
            return

        if data.startswith("bot:reset:"):
            parts = data.split(":")
            server = parts[2]
            uname = parts[3]
            bots = db_list_bots(server=server)
            for b in bots:
                if b[1] == uname:
                    flood_map = get_flood_map(server)
                    flood_map.pop(b[0], None)
                    await safe_answer(event, "🌊 Reset", alert=True)
                    await safe_edit(
                        event,
                        f"✅ @{uname} flood reset",
                        buttons=kb_server_panel(server))
                    return
            return

        if data.startswith("bot:del:"):
            parts = data.split(":")
            server = parts[2]
            uname = parts[3]
            bots = db_list_bots(server=server)
            for b in bots:
                if b[1] == uname:
                    db_remove_bot(b[0])
                    await safe_answer(event, "🗑️", alert=True)
                    await safe_edit(
                        event,
                        f"✅ @{uname} removed",
                        buttons=kb_server_panel(server))
                    return
            return

        # ══════════════════════════════════════════
        # ═════ USER SERVER ASSIGNMENT 🔥 ═════
        # ══════════════════════════════════════════
        if data.startswith("usrv:panel:"):
            tuid = int(data.split(":")[2])
            u = db_get_user_full(tuid)
            if not u:
                await safe_answer(event, "❌ User not found", alert=True)
                return
            current = get_user_server(tuid)
            plan = u[15] or "free"
            override = u[27] if len(u) > 27 else None
            server_label = get_server_label(current)
            await safe_edit(
                event,
                f"🖥️ **USER SERVER**\n"
                f"{STAR_LINE}\n\n"
                f"👤 `{tuid}`\n"
                f"💰 Plan: **{plan}**\n"
                f"🖥️ Current: **{server_label}**\n"
                f"📝 Override: **{override or 'None'}**\n\n"
                f"{DIV}\n"
                f"Force user to specific server:",
                buttons=kb_user_server(tuid))
            return

        if data.startswith("usrv:refresh:"):
            tuid = int(data.split(":")[2])
            await safe_answer(event, "🔄", alert=True)
            await safe_edit(
                event,
                f"🖥️ **USER SERVER**",
                buttons=kb_user_server(tuid))
            return

        if data.startswith("usrv:set:"):
            parts = data.split(":")
            server = parts[2]
            tuid = int(parts[3])
            set_user_server_override(tuid, server)
            await safe_answer(event, f"✅ → {server}", alert=True)
            # Notify user
            try:
                await bot.send_message(
                    tuid,
                    f"🖥️ **Server Updated**\n\n"
                    f"Your server: **{get_server_label(server)}**")
            except Exception:
                pass
            await safe_edit(
                event,
                f"✅ User `{tuid}` → {get_server_label(server)}",
                buttons=kb_user_server(tuid))
            return

        if data.startswith("usrv:reset:"):
            tuid = int(data.split(":")[2])
            set_user_server_override(tuid, None)
            await safe_answer(event, "🔄 Reset", alert=True)
            await safe_edit(
                event,
                f"✅ Override removed — using plan default",
                buttons=kb_user_server(tuid))
            return

        # ══════════════════════════════════════════
        # ═════ ANALYTICS / REVENUE / PAYMENTS ═════
        # ══════════════════════════════════════════
        if data == "op:analytics":
            dd = db_reactions_by_day(7)
            tu = db_top_users_by_reactions(5)
            tg = db_top_groups(5)
            chart = ""
            mx = max([n for _, n in dd], default=1)
            for d, n in dd:
                bl = int((n / mx) * 10) if mx > 0 else 0
                chart += f"`{d[5:]}` {'█' * bl}{'░' * (10 - bl)} {n}\n"
            txt = f"📊 **ANALYTICS (7 Days)**\n{DIV}\n\n{chart}\n"
            txt += f"{DIV}\n\n**🏆 Top Users:**\n"
            if not tu:
                txt += "_None_\n"
            for i, u_d in enumerate(tu, 1):
                txt += f"{i}. {u_d[1] or '—'} — **{u_d[2]}**\n"
            txt += "\n**📢 Top Chats:**\n"
            if not tg:
                txt += "_None_\n"
            for i, g in enumerate(tg, 1):
                title = g[0][:20] if g[0] else "—"
                txt += f"{i}. {title} — **{g[2]}**\n"
            await safe_edit(event, txt[:4000], buttons=kb_owner())
            return

        if data == "op:revenue":
            t, tr, mr = db_revenue_stats()
            await safe_edit(
                event,
                f"💰 **REVENUE**\n"
                f"{STAR_LINE}\n\n"
                f"📅 Today: **{tr}rs**\n"
                f"📆 Month: **{mr}rs**\n"
                f"💎 Total: **{t}rs**\n\n"
                f"{DIV}\n"
                f"💳 Payments: **{db_count_payments()}**\n"
                f"⏳ Pending: **{db_count_payments('pending')}**",
                buttons=kb_owner())
            return

        if data == "op:payments":
            pend = db_list_payments(status="pending", l=10)
            if not pend:
                await safe_edit(event, "✅ No pending payments.",
                                buttons=kb_owner())
                return
            for p in pend[:5]:
                try:
                    await bot.send_message(
                        get_owner_id(),
                        f"💳 **PAYMENT #{p[0]}**\n"
                        f"👤 `{p[1]}`\n"
                        f"💰 {p[2]}rs | {p[3]} {p[4]}d\n"
                        f"📝 {p[5]}",
                        buttons=kb_payment_actions(p[0]))
                    await asyncio.sleep(0.3)
                except Exception:
                    pass
            await safe_edit(event,
                            f"⏳ Sent {len(pend[:5])} payments.",
                            buttons=kb_owner())
            return

        if data.startswith("payv:"):
            parts = data.split(":")
            action = parts[1]
            pid = int(parts[2])
            payment = db_get_payment(pid)
            if not payment:
                await safe_answer(event, "❌", alert=True)
                return
            if action == "approve":
                db_update_payment(
                    pid, status="approved",
                    verified_at=datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"),
                    verified_by=get_owner_id())
                tuid = payment[1]
                pk = payment[3]
                ds = payment[4]
                db_set_user_plan(tuid, pk, ds)
                await safe_answer(event, "✅ Approved", alert=True)
                try:
                    await bot.send_message(
                        tuid,
                        f"🎉 **PLAN ACTIVATED!**\n"
                        f"{DIV}\n\n"
                        f"💰 {PLAN_NAMES.get(pk, pk)}\n"
                        f"📅 {DURATIONS.get(ds, ds)}\n"
                        f"🖥️ Server: 💎 PAID\n\n"
                        f"🚀 Enjoy!")
                except Exception:
                    pass
            else:
                db_update_payment(
                    pid, status="rejected",
                    verified_at=datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"),
                    verified_by=get_owner_id())
                await safe_answer(event, "❌ Rejected", alert=True)
                try:
                    await bot.send_message(
                        payment[1],
                        f"❌ **Payment Rejected**\n\n"
                        f"Contact: @{get_owner_username()}")
                except Exception:
                    pass
            return

        # ══════════════════════════════════════════
        # ═════ RA PANELS ═════
        # ══════════════════════════════════════════
        if data == "op:ra":
            status = real_get_status()
            await safe_answer(event, "👤")
            await safe_edit(
                event,
                f"👤 **REAL ACCOUNTS**\n"
                f"{STAR_LINE}\n\n"
                f"📁 Total: **{status['total']}**\n"
                f"✅ Available: **{status['available']}**\n"
                f"🌊 Flooded: **{status['flooded']}**\n"
                f"💾 Loaded: **{status['loaded']}/"
                f"{status['max_clients']}**",
                buttons=kb_ra_panel())
            return

        if data == "op:ra_plans":
            await safe_answer(event, "⚙️")
            rows = []
            for plan in ["free", "basic", "pro", "premium"]:
                lim = plan_ra_limit(plan)
                enabled = plan_has_realaccounts(plan)
                st = "✅" if enabled else "❌"
                rows.append(f"{st} **{PLAN_NAMES[plan]}** — {lim} sessions")
            await safe_edit(
                event,
                f"⚙️ **RA PLANS**\n"
                f"{STAR_LINE}\n\n"
                + "\n".join(rows) +
                f"\n\n{DIV}\n"
                f"Tap to toggle enable/disable or edit limits",
                buttons=kb_ra_plans())
            return

        if data == "ra:list":
            files = discover_session_files()
            if not files:
                await safe_edit(event, "📁 No sessions found.",
                                buttons=kb_ra_panel())
                return
            await safe_edit(event, "📋 **SESSIONS**",
                            buttons=kb_sessions_panel())
            return

        if data.startswith("ra:info:"):
            sf = data.split(":", 2)[2]
            await safe_answer(event, "📁")
            await safe_edit(
                event,
                f"📁 **SESSION INFO**\n"
                f"{DIV}\n\n"
                f"📄 File: `{sf}`",
                buttons=kb_session_info(sf))
            return

        if data.startswith("ra:test:"):
            sf = data.split(":", 2)[2]
            await safe_answer(event, "🧪 Testing...", alert=True)
            try:
                client = await get_real_client(sf)
                if client:
                    me = await asyncio.wait_for(client.get_me(),
                                                timeout=10)
                    name = getattr(me, "first_name", "?")
                    uname = getattr(me, "username", "") or "—"
                    await safe_edit(
                        event,
                        f"✅ **SESSION OK**\n"
                        f"{DIV}\n\n"
                        f"📄 `{sf}`\n"
                        f"👤 {name}\n"
                        f"📛 @{uname}",
                        buttons=kb_session_info(sf))
                else:
                    await safe_edit(
                        event,
                        f"❌ **FAILED**\n\n`{sf}`",
                        buttons=kb_session_info(sf))
            except Exception as e:
                await safe_edit(
                    event,
                    f"❌ **ERROR**\n\n`{sf}`\n{str(e)[:100]}",
                    buttons=kb_session_info(sf))
            return

        if data.startswith("ra:reset:"):
            sf = data.split(":", 2)[2]
            REAL_FLOOD_UNTIL.pop(sf, None)
            await safe_answer(event, "🔄 Reset", alert=True)
            await safe_edit(event, f"✅ Flood reset for `{sf}`",
                            buttons=kb_session_info(sf))
            return

        if data.startswith("ra:disconnect:"):
            sf = data.split(":", 2)[2]
            client = REAL_CLIENTS.pop(sf, None)
            if client:
                try:
                    await client.disconnect()
                except Exception:
                    pass
            await safe_answer(event, "🔌", alert=True)
            await safe_edit(event, f"✅ Disconnected `{sf}`",
                            buttons=kb_session_info(sf))
            return

        if data == "ra:clear_floods":
            n = len(REAL_FLOOD_UNTIL)
            REAL_FLOOD_UNTIL.clear()
            await safe_answer(event, f"🌊 {n}", alert=True)
            await safe_edit(event, f"✅ Cleared {n} floods",
                            buttons=kb_ra_panel())
            return

        if data == "ra:disconnect_all":
            n = len(REAL_CLIENTS)
            await close_all_real_clients()
            await safe_answer(event, f"🔌 {n}", alert=True)
            await safe_edit(event,
                            f"✅ Disconnected {n} clients",
                            buttons=kb_ra_panel())
            return

        if data == "ra:test_all":
            await safe_answer(event, "🧪 Testing...", alert=True)
            files = discover_session_files()
            if not files:
                await safe_edit(event, "❌ No sessions",
                                buttons=kb_ra_panel())
                return
            msg = await event.edit("🧪 Testing sessions...")
            results = []
            for i, sf in enumerate(files[:20], 1):
                try:
                    client = await get_real_client(sf)
                    if client:
                        me = await asyncio.wait_for(
                            client.get_me(), timeout=8)
                        results.append(
                            f"✅ `{sf[:25]}` — "
                            f"{getattr(me, 'first_name', '?')}")
                    else:
                        results.append(f"❌ `{sf[:25]}` — fail")
                except Exception:
                    results.append(f"❌ `{sf[:25]}` — error")
                if i % 3 == 0:
                    try:
                        await msg.edit(
                            f"🧪 Testing... {i}/{len(files[:20])}\n\n" +
                            "\n".join(results[-5:]))
                    except Exception:
                        pass
            final = (f"🧪 **TEST RESULTS**\n"
                     f"{DIV}\n\n" + "\n".join(results))
            try:
                await msg.edit(final[:4000],
                               buttons=kb_ra_panel())
            except Exception:
                pass
            return

        if data == "ra:upload_info":
            await safe_answer(event, "📤")
            await safe_edit(
                event,
                f"📤 **HOW TO ADD SESSIONS**\n"
                f"{STAR_LINE}\n\n"
                f"**Method 1: Manual Upload**\n"
                f"1️⃣ Create `.session` files\n"
                f"2️⃣ Place in: `{SESSIONS_DIR}`\n"
                f"3️⃣ Auto-load on next use\n\n"
                f"{DIV}\n"
                f"**Method 2: StringSession**\n"
                f"Save as `.session` using:\n"
                f"`TelegramClient(StringSession('...'), API_ID, API_HASH)`",
                buttons=kb_ra_panel())
            return

        if data.startswith("rap:toggle:"):
            plan = data.split(":")[2]
            new_val = not plan_has_realaccounts(plan)
            cfg_set(f"plan_realaccounts_{plan}",
                    "1" if new_val else "0")
            await safe_answer(event,
                              f"{'✅' if new_val else '❌'} {plan}",
                              alert=True)
            await safe_edit(
                event, f"⚙️ **RA PLANS**\n{DIV}",
                buttons=kb_ra_plans())
            return

        if data.startswith("rap:edit:"):
            plan = data.split(":")[2]
            USER_STATES[uid] = {"step": "rap_edit_limit", "plan": plan}
            await safe_edit(
                event,
                f"✏️ **EDIT RA LIMIT**\n\n"
                f"Plan: {PLAN_NAMES[plan]}\n"
                f"Current: {plan_ra_limit(plan)}\n\n"
                f"Send new limit (0-100):",
                buttons=[[btn("🔙 Cancel", data=b"op:ra_plans",
                              style="danger")]])
            return

        # ══════════════════════════════════════════
        # ═════ OWNER INFO ═════
        # ══════════════════════════════════════════
        if data == "op:owner_info":
            await safe_answer(event, "👤")
            await safe_edit(
                event,
                f"👤 **OWNER INFO**\n"
                f"{DIV}\n\n"
                f"👑 Username: **@{get_owner_username()}**\n"
                f"🆔 Owner ID: `{get_owner_id()}`\n\n"
                f"{DIV}\n"
                f"💡 Changes take effect immediately",
                buttons=[
                    [btn("✏️ Edit Username", data=b"oi:edit_uname",
                         style="primary")],
                    [btn("✏️ Edit Owner ID", data=b"oi:edit_oid",
                         style="primary")],
                    [btn("🔙 Back", data=b"owner_panel",
                         style="primary")],
                ])
            return

        if data == "oi:edit_uname":
            USER_STATES[uid] = {"step": "oi_wait_uname"}
            await safe_edit(
                event,
                f"✏️ **EDIT USERNAME**\n\n"
                f"Current: @{get_owner_username()}\n\n"
                f"Send new username (without @):",
                buttons=[[btn("🔙 Cancel", data=b"op:owner_info",
                              style="danger")]])
            return

        if data == "oi:edit_oid":
            USER_STATES[uid] = {"step": "oi_wait_oid"}
            await safe_edit(
                event,
                f"✏️ **EDIT OWNER ID**\n\n"
                f"Current: `{get_owner_id()}`\n\n"
                f"Send new Telegram ID:",
                buttons=[[btn("🔙 Cancel", data=b"op:owner_info",
                              style="danger")]])
            return

        # ══════════════════════════════════════════
        # ═════ COUPONS ═════
        # ══════════════════════════════════════════
        if data == "op:coupons":
            await safe_answer(event, "🎟️")
            await safe_edit(
                event,
                f"🎟️ **COUPONS**\n"
                f"{DIV}\n\n"
                f"Total: **{len(coupon_list())}**\n"
                f"Active: **{coupon_count_active()}**",
                buttons=kb_coupons_manage())
            return

        if data == "cop:new":
            USER_STATES[uid] = {"step": "cop_wait_code"}
            await safe_edit(
                event, "✏️ Send coupon code (e.g., SAVE20):",
                buttons=[[btn("🔙 Cancel", data=b"op:coupons",
                              style="danger")]])
            return

        if data.startswith("cop:del:"):
            cid = int(data.split(":")[2])
            coupon_delete(cid)
            await safe_answer(event, "🗑️", alert=True)
            await safe_edit(event, "Deleted",
                            buttons=kb_coupons_manage())
            return

        if data.startswith("cop:view:"):
            cid = int(data.split(":")[2])
            c = None
            for x in coupon_list():
                if x[0] == cid:
                    c = x
                    break
            if not c:
                await safe_answer(event, "❌", alert=True)
                return
            cid, code, pct, flat, mx, used, exp, act = c
            await safe_edit(
                event,
                f"🎟️ **COUPON**\n"
                f"{DIV}\n\n"
                f"Code: `{code}`\n"
                f"Discount: **{pct}%** + **{flat}rs**\n"
                f"Uses: **{used}/{mx or '∞'}**\n"
                f"Expires: **{exp or 'Never'}**\n"
                f"Status: **{'🟢 Active' if act else '🔴 Disabled'}**",
                buttons=[
                    [btn("🔄 Toggle",
                         data=f"cop:toggle:{cid}".encode(),
                         style="primary")],
                    [btn("🗑️ Delete",
                         data=f"cop:del:{cid}".encode(),
                         style="danger")],
                    [btn("🔙 Back", data=b"op:coupons",
                         style="primary")],
                ])
            return

        if data.startswith("cop:toggle:"):
            cid = int(data.split(":")[2])
            coupon_toggle(cid)
            await safe_answer(event, "✅", alert=True)
            await safe_edit(event, "Updated",
                            buttons=kb_coupons_manage())
            return

        # ══════════════════════════════════════════
        # ═════ EMOJI STORE MANAGE ═════
        # ══════════════════════════════════════════
        if data == "op:store":
            await safe_answer(event, "🏪")
            await safe_edit(
                event,
                f"🏪 **EMOJI STORE**\n"
                f"{DIV}\n\n"
                f"Total: **{len(store_list(active_only=False))}**\n"
                f"Active: **{store_count_active()}**",
                buttons=kb_store_manage())
            return

        if data == "storem:new":
            USER_STATES[uid] = {"step": "storem_wait_name"}
            await safe_edit(
                event, "✏️ Pack name:",
                buttons=[[btn("🔙 Cancel", data=b"op:store",
                              style="danger")]])
            return

        if data.startswith("storem:del:"):
            pid = int(data.split(":")[2])
            store_delete(pid)
            await safe_answer(event, "🗑️", alert=True)
            await safe_edit(event, "Deleted",
                            buttons=kb_store_manage())
            return

        if data.startswith("storem:view:"):
            pid = int(data.split(":")[2])
            p = store_get(pid)
            if not p:
                await safe_answer(event, "❌", alert=True)
                return
            _, name, emojis, price, desc, act = p
            await safe_edit(
                event,
                f"🏪 **{name}**\n"
                f"{DIV}\n\n"
                f"💰 Price: **{price}rs**\n"
                f"📝 {desc or '—'}\n\n"
                f"🎨 {emojis[:250]}\n\n"
                f"Status: **{'🟢 Active' if act else '🔴 Disabled'}**",
                buttons=[
                    [btn("🔄 Toggle",
                         data=f"storem:toggle:{pid}".encode(),
                         style="primary")],
                    [btn("🗑️ Delete",
                         data=f"storem:del:{pid}".encode(),
                         style="danger")],
                    [btn("🔙 Back", data=b"op:store",
                         style="primary")],
                ])
            return

        if data.startswith("storem:toggle:"):
            pid = int(data.split(":")[2])
            store_toggle(pid)
            await safe_answer(event, "✅", alert=True)
            await safe_edit(event, "Updated",
                            buttons=kb_store_manage())
            return

        # ══════════════════════════════════════════
        # ═════ AUTO-RETRY ═════
        # ══════════════════════════════════════════
        if data == "op:retry":
            await safe_answer(event, "🔄")
            pending = retry_list_pending()
            await safe_edit(
                event,
                f"🔄 **AUTO-RETRY**\n"
                f"{DIV}\n\n"
                f"⏳ Pending: **{len(pending)}**\n"
                f"⚙️ Enabled: "
                f"**{'✅' if feat_auto_retry() else '❌'}**\n"
                f"📊 Max attempts: **{cfg_get('auto_retry_max', '3')}**",
                buttons=kb_retry_menu())
            return

        if data == "retry:process_now":
            await safe_answer(event, "🔄 Processing...", alert=True)
            await safe_edit(event,
                            "✅ Retry loop running in background",
                            buttons=kb_retry_menu())
            return

        if data == "retry:list":
            jobs = retry_list_pending()
            txt = f"📋 **PENDING RETRIES**\n{DIV}\n\n"
            if not jobs:
                txt += "_None_"
            for j in jobs[:15]:
                rid = j[0]
                u_id = j[1]
                count = j[4]
                att = j[7]
                mx = j[8]
                txt += (f"🔄 **#{rid}** `{u_id}` — {count}x "
                        f"({att}/{mx})\n")
            await safe_edit(event, txt[:4000],
                            buttons=kb_retry_menu())
            return

        if data == "retry:clear":
            retry_clear_all()
            await safe_answer(event, "🧹", alert=True)
            await safe_edit(event, "✅ Cleared",
                            buttons=kb_retry_menu())
            return

        # ══════════════════════════════════════════
        # ═════ RATE LIMITS ═════
        # ══════════════════════════════════════════
        if data == "op:rate_limits":
            await safe_answer(event, "📈")
            conn = sqlite3.connect(DB_FILE)
            try:
                top = conn.execute("""SELECT user_id, today_sent,
                    week_sent, total_sent FROM user_stats
                    WHERE today_sent > 0
                    ORDER BY today_sent DESC LIMIT 10""").fetchall()
            except Exception:
                top = []
            finally:
                conn.close()
            txt = (f"📈 **RATE LIMITS**\n"
                   f"{DIV}\n\n"
                   f"**Top senders today:**\n\n")
            if not top:
                txt += "_None_"
            for i, r in enumerate(top, 1):
                u_id, td, wk, tot = r
                txt += (f"{i}. `{u_id}` — Today: **{td}** | "
                        f"Wk: {wk} | Tot: {tot}\n")
            await safe_edit(event, txt[:4000],
                            buttons=kb_rate_limits())
            return

        # ══════════════════════════════════════════
        # ═════ BULK USERS ═════
        # ══════════════════════════════════════════
        if data == "op:bulk_users":
            await safe_answer(event, "👥")
            await safe_edit(
                event,
                f"👥 **BULK USER ACTIONS**\n"
                f"{DIV}\n\n"
                f"⚠️ These affect ALL users!\n\n"
                f"⏳ Pending: **{db_count_pending_approvals()}**\n"
                f"✅ Approved: **{db_count_approved_users()}**\n"
                f"🚫 Banned: **{db_count_banned_users()}**",
                buttons=kb_bulk_users())
            return

        if data == "bulk:approve_pending":
            conn = sqlite3.connect(DB_FILE)
            try:
                c = conn.cursor()
                c.execute("""UPDATE approvals SET status='approved',
                    decided_at=CURRENT_TIMESTAMP
                    WHERE status='pending'""")
                n = c.rowcount
                conn.commit()
            finally:
                conn.close()
            _dirty()
            await safe_answer(event, f"✅ {n}", alert=True)
            await safe_edit(event, f"✅ Approved {n} users",
                            buttons=kb_bulk_users())
            return

        if data == "bulk:ban_pending":
            conn = sqlite3.connect(DB_FILE)
            try:
                c = conn.cursor()
                c.execute("""UPDATE users SET is_banned=1
                    WHERE user_id IN (SELECT user_id FROM approvals
                    WHERE status='pending')""")
                n = c.rowcount
                conn.commit()
            finally:
                conn.close()
            _dirty()
            await safe_answer(event, f"🚫 {n}", alert=True)
            await safe_edit(event, f"Banned {n}",
                            buttons=kb_bulk_users())
            return

        if data == "bulk:premium_all":
            exp = (datetime.now()
                   + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect(DB_FILE)
            try:
                c = conn.cursor()
                c.execute("""UPDATE users SET plan='premium',
                    plan_expires=? WHERE plan='free'""", (exp,))
                n = c.rowcount
                conn.commit()
            finally:
                conn.close()
            _dirty()
            await safe_answer(event, f"💎 {n}", alert=True)
            await safe_edit(event,
                            f"💎 Premium granted to {n}",
                            buttons=kb_bulk_users())
            return

        # ══════════════════════════════════════════
        # ═════ FEATURES ═════
        # ══════════════════════════════════════════
        if data == "op:features":
            await safe_answer(event, "🎛️")
            await safe_edit(
                event,
                f"🎛️ **FEATURES**\n"
                f"{STAR_LINE}\n\n"
                f"Tap to toggle features:\n\n"
                f"💎 = Paid feature\n"
                f"🆓 = Free feature",
                buttons=kb_features())
            return

        if data.startswith("ft:toggle:"):
            key = data.split(":", 2)[2]
            nv = cfg_toggle(key)
            await safe_answer(event,
                              f"{'✅ ON' if nv else '❌ OFF'}",
                              alert=True)
            await safe_edit(
                event, f"🎛️ **FEATURES**\n{DIV}",
                buttons=kb_features())
            return

        # ══════════════════════════════════════════
        # ═════ PLAN PRICES ═════
        # ══════════════════════════════════════════
        if data == "op:plan_prices":
            await safe_answer(event, "💰")
            await safe_edit(
                event,
                f"💰 **PLAN PRICES**\n"
                f"{DIV}\n\n"
                f"Tap a plan to edit prices:",
                buttons=kb_plan_prices())
            return

        if data.startswith("pp:plan:"):
            plan = data.split(":")[2]
            await safe_edit(
                event,
                f"💰 **{PLAN_NAMES[plan]}**\n"
                f"{DIV}\n\n"
                f"Tap duration to edit price:",
                buttons=kb_plan_prices_durations(plan))
            return

        if data.startswith("pp:edit:"):
            parts = data.split(":")
            plan = parts[2]
            days = int(parts[3])
            USER_STATES[uid] = {
                "step": "pp_edit_price",
                "plan": plan,
                "days": days
            }
            await safe_edit(
                event,
                f"✏️ **EDIT PRICE**\n\n"
                f"{PLAN_NAMES[plan]} — {DURATIONS[days]}\n"
                f"Current: {get_plan_price(plan, days)}rs\n\n"
                f"Send new price:",
                buttons=kb_back(uid))
            return

        # ══════════════════════════════════════════
        # ═════ PAID FEATURES ═════
        # ══════════════════════════════════════════
        if data == "op:paid_features":
            await safe_answer(event, "💎")
            await safe_edit(
                event,
                f"💎 **PAID FEATURES**\n"
                f"{STAR_LINE}\n\n"
                f"Toggle which features require paid plan:",
                buttons=kb_paid_features())
            return

        if data.startswith("pf:toggle:"):
            feature = data.split(":", 2)[2]
            nv = cfg_toggle(f"paid_{feature}")
            await safe_answer(event,
                              "💎 PAID" if nv else "🆓 FREE",
                              alert=True)
            await safe_edit(
                event, f"💎 **PAID FEATURES**\n{DIV}",
                buttons=kb_paid_features())
            return

        # ══════════════════════════════════════════
        # ═════ FORCE / TEAM / PACKS ═════
        # ══════════════════════════════════════════
        if data == "op:force_channels":
            await safe_answer(event, "📢")
            await safe_edit(
                event,
                f"📢 **FORCE CHANNELS**\n"
                f"{DIV}\n\n"
                f"Active: **{db_count_force_channels(True)}**\n"
                f"Total: **{db_count_force_channels(False)}**",
                buttons=kb_force_channels())
            return

        if data.startswith("fc:toggle:"):
            fid = int(data.split(":")[2])
            db_toggle_force_channel(fid)
            await safe_answer(event, "✅", alert=True)
            await safe_edit(event, "Updated",
                            buttons=kb_force_channels())
            return

        if data.startswith("fc:del:"):
            fid = int(data.split(":")[2])
            db_delete_force_channel(fid)
            await safe_answer(event, "🗑️", alert=True)
            await safe_edit(event, "Deleted",
                            buttons=kb_force_channels())
            return

        if data == "fc:add":
            USER_STATES[uid] = {"step": "fc_wait_channel"}
            await safe_edit(
                event,
                f"📢 **ADD FORCE CHANNEL**\n\n"
                f"Send @channel or -100XXXXX:",
                buttons=[[btn("🔙 Cancel",
                              data=b"op:force_channels",
                              style="danger")]])
            return

        if data == "op:team":
            await safe_answer(event, "👥")
            await safe_edit(
                event,
                f"👥 **TEAM MEMBERS**\n"
                f"{DIV}\n\n"
                f"Total: **{db_count_team_members()}**",
                buttons=kb_team())
            return

        if data == "team:add":
            USER_STATES[uid] = {"step": "team_wait_id"}
            await safe_edit(
                event, "👤 Send user ID:",
                buttons=[[btn("🔙 Cancel", data=b"op:team",
                              style="danger")]])
            return

        if data.startswith("team:view:"):
            target = int(data.split(":")[2])
            m = db_get_team_member(target)
            if not m:
                await safe_answer(event, "❌", alert=True)
                return
            await safe_edit(
                event,
                f"👤 **TEAM MEMBER**\n"
                f"{DIV}\n\n"
                f"🆔 `{m[0]}`\n"
                f"👑 Role: **{m[1]}**\n"
                f"💰 Commission: **{m[3]}%**",
                buttons=[
                    [btn("🗑️ Remove",
                         data=f"team:del:{target}".encode(),
                         style="danger")],
                    [btn("🔙 Back", data=b"op:team",
                         style="primary")],
                ])
            return

        if data.startswith("team:del:"):
            target = int(data.split(":")[2])
            db_remove_team_member(target)
            await safe_answer(event, "✅", alert=True)
            await safe_edit(event, "Removed", buttons=kb_team())
            return

        if data == "op:emoji_packs":
            await safe_answer(event, "🎨")
            await safe_edit(
                event,
                f"🎨 **CUSTOM PACKS**\n"
                f"{DIV}\n\n"
                f"Total: **{db_count_custom_packs()}**",
                buttons=kb_emoji_packs_manage())
            return

        if data == "cp:new":
            USER_STATES[uid] = {"step": "cp_wait_name"}
            await safe_edit(
                event, "🎨 Pack name:",
                buttons=[[btn("🔙 Cancel", data=b"op:emoji_packs",
                              style="danger")]])
            return

        if data.startswith("cp:del:"):
            cpid = int(data.split(":")[2])
            db_delete_custom_pack(cpid)
            await safe_answer(event, "🗑️", alert=True)
            await safe_edit(event, "Deleted",
                            buttons=kb_emoji_packs_manage())
            return

        if data.startswith("cp:view:"):
            cpid = int(data.split(":")[2])
            cp = db_get_custom_pack(cpid)
            if not cp:
                await safe_answer(event, "❌", alert=True)
                return
            cpid, name, emojis, price, is_paid = cp
            await safe_edit(
                event,
                f"🎨 **{name}**\n"
                f"{DIV}\n\n"
                f"💰 Price: **{price}rs**\n"
                f"💎 Paid: **{'✅' if is_paid else '❌'}**\n\n"
                f"{emojis[:250]}",
                buttons=[
                    [btn("🗑️ Delete",
                         data=f"cp:del:{cpid}".encode(),
                         style="danger")],
                    [btn("🔙 Back", data=b"op:emoji_packs",
                         style="primary")],
                ])
            return

        # ══════════════════════════════════════════
        # ═════ WATCHERS / REFERRALS / QUEUE ═════
        # ══════════════════════════════════════════
        if data == "op:watchers":
            ws = db_list_watchers()
            txt = f"📡 **ALL WATCHERS ({len(ws)})**\n{DIV}\n\n"
            if not ws:
                txt += "_None_"
            for w in ws[:15]:
                st = "🟢" if w[10] else "🔴"
                txt += f"{st} **#{w[0]}** {w[3][:25]} • {w[6]}x\n"
            await safe_edit(event, txt[:4000], buttons=kb_owner())
            return

        if data == "op:referrals":
            stats = db_count_referrals()
            await safe_edit(
                event,
                f"🎁 **REFERRALS**\n"
                f"{DIV}\n\n"
                f"✅ Valid: **{stats['valid']}**\n"
                f"⏳ Pending: **{stats['pending']}**\n"
                f"📊 Total: **{stats['total']}**",
                buttons=kb_owner())
            return

        if data == "op:queue":
            pend = db_list_queue(status="pending")
            txt = f"⏰ **QUEUE ({len(pend)})**\n{DIV}\n\n"
            if not pend:
                txt += "_None_"
            for j in pend[:10]:
                txt += f"⏳ **#{j[0]}** `{j[1]}` — {j[4]}x\n"
            await safe_edit(event, txt[:4000], buttons=kb_owner())
            return

        # ══════════════════════════════════════════
        # ═════ POOL STATUS / RESET ═════
        # ══════════════════════════════════════════
        if data == "op:pool_status":
            await safe_edit(
                event,
                get_dual_server_status_text(),
                buttons=kb_owner())
            return

        if data == "op:reset_pool":
            op, of = reset_bot_pool()
            global TASK_RUNNING, TASK_OWNER_UID
            TASK_RUNNING = False
            TASK_OWNER_UID = None
            await safe_answer(event, "🧹 Reset", alert=True)
            await safe_edit(
                event,
                f"🧹 **POOL RESET**\n\n"
                f"Cleared {op} busy bots (both)\n"
                f"Cleared {of} floods",
                buttons=kb_owner())
            return

        # ══════════════════════════════════════════
        # ═════ TOGGLE AUTO / SET FREE ═════
        # ══════════════════════════════════════════
        if data == "op:toggle_auto":
            nv = not is_auto_approve()
            set_auto_approve(nv)
            await safe_answer(event,
                              f"{'✅' if nv else '❌'}",
                              alert=True)
            await safe_edit(
                event,
                f"👑 **AUTO-APPROVE**\n{DIV}\n\n"
                f"Status: **{'✅ ON' if nv else '❌ OFF'}**",
                buttons=kb_owner())
            return

        if data == "op:setfree":
            USER_STATES[uid] = {"step": "wait_setfree"}
            await safe_edit(
                event,
                f"⚙️ **SET FREE COUNT**\n\n"
                f"Current: **{get_free_count()}**\n\n"
                f"Send new number:",
                buttons=[[btn("🔙 Cancel", data=b"owner_panel",
                              style="danger")]])
            return

        # ══════════════════════════════════════════
        # ═════ BOTS LIST / USERS ═════
        # ══════════════════════════════════════════
        if data == "op:bots":
            stats = db_bot_stats()
            await safe_edit(
                event,
                f"🤖 **BOTS**\n"
                f"{DIV}\n\n"
                f"📊 Total: **{stats['total']}**\n"
                f"🆓 Free: **{stats['free']}**\n"
                f"💎 Paid: **{stats['paid']}**\n"
                f"🔒 Permanent: **{stats['permanent']}**\n\n"
                f"{DIV}\n"
                f"Choose server to manage:",
                buttons=[
                    [btn(f"🆓 Free Server ({stats['free']})",
                         data=b"srv:panel:free", style="success")],
                    [btn(f"💎 Paid Server ({stats['paid']})",
                         data=b"srv:panel:paid", style="primary")],
                    [btn("🔙 Back", data=b"owner_panel",
                         style="primary")],
                ])
            return

        if data == "op:users":
            rows = db_all_users(10, 0)
            txt = f"👥 **USERS**\n{DIV}\n\n"
            br = []
            for r in rows:
                ic = "🚫" if r[5] else "✅"
                lim = get_user_limit(r[0])
                server = get_user_server(r[0])
                srv_icon = "🆓" if server == "free" else "💎"
                txt += (f"{ic}{srv_icon} **{r[1] or '—'}** "
                        f"`{r[0]}` 🎁 {lim}\n")
                br.append([
                    btn(f"⚙️ {r[1] or 'User'}",
                        data=f"um:panel:{r[0]}".encode(),
                        style="primary")
                ])
            br.append([btn("🔙", data=b"owner_panel",
                           style="danger")])
            await safe_edit(event, txt[:4000], buttons=br)
            return

        if data.startswith("um:panel:"):
            target = int(data.split(":")[2])
            u = db_get_user_full(target)
            if not u:
                await safe_answer(event, "❌", alert=True)
                return
            await safe_answer(event, "⚙️")
            plan = u[15] or "free"
            fb = u[17] or 0
            ban_st = "🚫 BANNED" if u[5] else "✅ Active"
            server = get_user_server(target)
            await safe_edit(
                event,
                f"⚙️ **USER PANEL**\n"
                f"{DIV}\n\n"
                f"👤 **{u[1] or '—'}**\n"
                f"🆔 `{u[0]}`\n"
                f"Status: **{ban_st}**\n"
                f"💰 Plan: **{plan}**\n"
                f"💎 Balance: **{fb}**\n"
                f"🖥️ Server: **{get_server_label(server)}**",
                buttons=kb_user_manage(target))
            return

        if data.startswith("um:ban:"):
            target = int(data.split(":")[2])
            u = db_get_user_full(target)
            nb = not u[5]
            db_ban_user(target, ban=nb)
            await safe_answer(event,
                              f"{'🚫' if nb else '✅'}",
                              alert=True)
            await safe_edit(event, "Updated",
                            buttons=kb_user_manage(target))
            return

        if data.startswith("um:limit:"):
            target = int(data.split(":")[2])
            USER_STATES[uid] = {
                "step": "user_set_limit",
                "target": target
            }
            await safe_edit(
                event, "✏️ Send reaction limit:",
                buttons=[[btn("🔙", data=f"um:panel:{target}".encode(),
                              style="danger")]])
            return

        if data.startswith("um:plan:"):
            target = int(data.split(":")[2])
            await safe_edit(
                event,
                f"💰 **PLAN FOR** `{target}`",
                buttons=kb_user_plan_durations(target))
            return

        if data.startswith("um:activate:"):
            parts = data.split(":")
            pk = parts[2]
            ds = int(parts[3])
            target = int(parts[4])
            if pk == "free":
                db_set_user_plan(target, "free", 9999)
            else:
                db_set_user_plan(target, pk, ds)
            await safe_answer(event, "✅", alert=True)
            try:
                await bot.send_message(
                    target,
                    f"🎉 **PLAN ACTIVATED**\n\n"
                    f"💰 {PLAN_NAMES.get(pk, pk)}")
            except Exception:
                pass
            await safe_edit(event, "✅ Activated",
                            buttons=kb_user_manage(target))
            return

        if data.startswith("um:balance:"):
            target = int(data.split(":")[2])
            USER_STATES[uid] = {
                "step": "user_add_balance",
                "target": target
            }
            await safe_edit(
                event, "💎 Send amount to add:",
                buttons=[[btn("🔙",
                              data=f"um:panel:{target}".encode(),
                              style="danger")]])
            return

        if data.startswith("um:ra:"):
            target = int(data.split(":")[2])
            u = db_get_user_full(target)
            if not u:
                await safe_answer(event, "❌", alert=True)
                return
            try:
                override = u[26] if len(u) > 26 else -1
            except Exception:
                override = -1
            plan = u[15] or "free"
            plan_lim = plan_ra_limit(plan)
            ov_txt = override if override >= 0 else "None (plan)"
            eff = override if override >= 0 else plan_lim
            await safe_edit(
                event,
                f"👤 **RA LIMIT**\n"
                f"{DIV}\n\n"
                f"User: `{target}`\n"
                f"Plan: **{PLAN_NAMES.get(plan, plan)}**\n"
                f"Plan limit: **{plan_lim}**\n"
                f"Override: **{ov_txt}**\n"
                f"Effective: **{eff}**",
                buttons=[
                    [btn("✏️ Set Custom",
                         data=f"um:ra_set:{target}".encode(),
                         style="primary")],
                    [btn("🔄 Reset",
                         data=f"um:ra_reset:{target}".encode(),
                         style="danger")],
                    [btn("🔙 Back",
                         data=f"um:panel:{target}".encode(),
                         style="success")],
                ])
            return

        if data.startswith("um:ra_set:"):
            target = int(data.split(":")[2])
            USER_STATES[uid] = {
                "step": "ra_set_user_limit",
                "target": target
            }
            await safe_edit(
                event,
                f"✏️ RA limit for `{target}` (0-100, -1 reset):",
                buttons=[[btn("🔙",
                              data=f"um:ra:{target}".encode(),
                              style="danger")]])
            return

        if data.startswith("um:ra_reset:"):
            target = int(data.split(":")[2])
            set_user_ra_limit(target, -1)
            await safe_answer(event, "✅ Reset", alert=True)
            await safe_edit(
                event, "✅ RA limit reset",
                buttons=[[btn("🔙",
                              data=f"um:ra:{target}".encode(),
                              style="primary")]])
            return

        if data.startswith("um:team:"):
            target = int(data.split(":")[2])
            await safe_edit(
                event,
                f"👥 **TEAM ROLE** for `{target}`",
                buttons=[
                    [btn("👤 User",
                         data=f"um:setteam:user:{target}".encode(),
                         style="primary")],
                    [btn("💼 Reseller",
                         data=f"um:setteam:reseller:{target}".encode(),
                         style="success")],
                    [btn("👑 Sub-Admin",
                         data=f"um:setteam:admin:{target}".encode(),
                         style="danger")],
                    [btn("🔙",
                         data=f"um:panel:{target}".encode(),
                         style="primary")],
                ])
            return

        if data.startswith("um:setteam:"):
            parts = data.split(":")
            role = parts[2]
            target = int(parts[3])
            if role == "user":
                db_remove_team_member(target)
            else:
                comm = 10 if role == "reseller" else 15
                db_add_team_member(target, role, comm)
            await safe_answer(event, f"✅ {role}", alert=True)
            await safe_edit(event, "Updated",
                            buttons=kb_user_manage(target))
            return

        # User permissions
        for fk in ["channel", "group", "manual", "autowatch", "custom"]:
            prefix = f"um:{fk}:"
            if data.startswith(prefix):
                target = int(data.split(":")[2])
                u = db_get_user_full(target)
                if not u:
                    return
                idx = {"channel": 10, "group": 11, "manual": 12,
                       "autowatch": 13, "custom": 14}[fk]
                feature = fk if fk != "custom" else "custom_emoji"
                db_set_user_perm(target, feature, not u[idx])
                await safe_answer(event, "✅", alert=True)
                await safe_edit(event, "Updated",
                                buttons=kb_user_manage(target))
                return

        if data.startswith("um:unlock:"):
            target = int(data.split(":")[2])
            u = db_get_user_full(target)
            db_set_user_perm(target, "auto_watch_unlocked", not u[9])
            await safe_answer(event, "✅", alert=True)
            await safe_edit(event, "Updated",
                            buttons=kb_user_manage(target))
            return

        # ══════════════════════════════════════════
        # ═════ BROADCAST / ADD USER / PENDING ═════
        # ══════════════════════════════════════════
        if data == "op:broadcast":
            ch = await get_admin_chats()
            await safe_edit(
                event,
                f"📢 **BROADCAST**\n"
                f"{DIV}\n\n"
                f"📊 Chats: **{len(ch)}**\n\n"
                f"⚠️ Sends to all admin chats",
                buttons=[
                    [btn("📝 Text", data=b"bc:text",
                         style="primary")],
                    [btn("🔙", data=b"owner_panel",
                         style="danger")],
                ])
            return

        if data == "bc:text":
            USER_STATES[uid] = {"step": "wait_bc_text"}
            await safe_edit(
                event, "📝 Send broadcast text:",
                buttons=[[btn("🔙", data=b"owner_panel",
                              style="danger")]])
            return

        if data == "op:adduser":
            USER_STATES[uid] = {"step": "wait_add_user_id"}
            await safe_edit(
                event, "➕ Send user ID to approve:",
                buttons=[[btn("🔙", data=b"owner_panel",
                              style="danger")]])
            return

        if data == "op:recent":
            rows = db_recent_reactions(15)
            txt = "📜 **RECENT REACTIONS**\n\n"
            if not rows:
                txt += "_None_"
            for r in rows:
                ic = "✅" if r[6] == "ok" else "❌"
                m = r[8] if len(r) > 8 else "bot"
                sv = r[9] if len(r) > 9 else "free"
                txt += (f"{ic} {r[4]} @{r[5]} [{m}/{sv}] "
                        f"{r[7][:16]}\n")
            await safe_edit(event, txt[:4000],
                            buttons=kb_owner())
            return

        if data == "op:pending":
            rows = db_pending_approvals(10)
            if not rows:
                await safe_edit(event, "✅ No pending users.",
                                buttons=kb_owner())
                return
            for r in rows:
                try:
                    await bot.send_message(
                        get_owner_id(),
                        f"🔔 **APPROVAL**\n"
                        f"👤 {r[1]}\n"
                        f"🆔 `{r[0]}`\n"
                        f"📛 @{r[2] or 'no_username'}\n"
                        f"🕒 {r[3][:16]}",
                        buttons=kb_approval_actions(r[0]))
                    await asyncio.sleep(0.4)
                except Exception:
                    pass
            await safe_edit(event,
                            f"⏳ Sent {len(rows)} requests",
                            buttons=kb_owner())
            return

        if data == "op:approved":
            rows = db_approved_users(20)
            txt = f"✅ **APPROVED USERS ({len(rows)})**\n\n"
            if not rows:
                txt += "_None_"
            for r in rows:
                txt += f"👤 {r[1] or '—'} `{r[0]}`\n"
            await safe_edit(event, txt[:4000],
                            buttons=kb_owner())
            return

        # ══════════════════════════════════════════
        # ═════ GITHUB SYNC ═════
        # ══════════════════════════════════════════
        if data == "op:ghsync":
            s = github_sync.get_stats()
            enabled = (HAS_GH_SYNC
                       and hasattr(github_sync, "is_enabled")
                       and github_sync.is_enabled())
            await safe_edit(
                event,
                f"🔄 **AUTO BACKUP**\n"
                f"{DIV}\n\n"
                f"🔌 Enabled: **{'✅' if enabled else '❌'}**\n"
                f"📊 Uploads: **{s['uploads']}**\n"
                f"📥 Downloads: **{s['downloads']}**\n"
                f"❌ Errors: **{s['errors']}**\n"
                f"🕒 Last: **{s['last_sync'] or '—'}**",
                buttons=[
                    [btn("⬆️ Push", data=b"gh:push",
                         style="success"),
                     btn("⬇️ Pull", data=b"gh:pull",
                         style="primary")],
                    [btn("🔙 Back", data=b"owner_panel",
                         style="primary")],
                ])
            return

        if data == "gh:push":
            await safe_answer(event, "⬆️", alert=True)
            try:
                ok, msg = github_sync.upload_db(force=True)
            except Exception as e:
                ok, msg = False, str(e)[:80]
            await safe_edit(
                event,
                f"{'✅' if ok else '❌'} {msg}",
                buttons=[[btn("🔙", data=b"op:ghsync",
                              style="primary")]])
            return

        if data == "gh:pull":
            await safe_answer(event, "⬇️", alert=True)
            try:
                ok, msg = github_sync.download_db()
            except Exception as e:
                ok, msg = False, str(e)[:80]
            await safe_edit(
                event,
                f"{'✅' if ok else '❌'} {msg}",
                buttons=[[btn("🔙", data=b"op:ghsync",
                              style="primary")]])
            return

        # ═════ Unknown ═════
        await safe_answer(event, "⚠️ Not implemented", alert=True)

    except Exception as e:
        D_err(e, "on_cb_owner")
        try:
            await safe_answer(event, "❌ Error", alert=True)
        except Exception:
            pass


# ══════════════════════ END OF PART 14 ══════════════════════
D("✅ Part 14 loaded — Owner Callbacks + Server Management", "ok")
# ══════════════════════ HTTP HEALTH SERVER ══════════════════════
async def start_health_server():
    """aiohttp health server for uptime monitoring"""
    async def health_handler(request):
        return web.Response(text="OK", status=200)

    async def status_handler(request):
        fs = get_pool_status("free")
        ps = get_pool_status("paid")
        real_status = real_get_status()
        stats = db_bot_stats()
        return web.json_response({
            "status": "online",
            "uptime_sec": int(time.time() - _start_time),
            "task_running": TASK_RUNNING,
            "task_owner": TASK_OWNER_UID,
            "users": db_total_users(),
            "reactions_total": db_total_reactions(),
            "reactions_today": db_reactions_today(),
            "bots": {
                "total": stats["total"],
                "free": stats["free"],
                "paid": stats["paid"],
                "permanent": stats["permanent"],
            },
            "free_server": {
                "total": fs["total"],
                "free": fs["free"],
                "busy": fs["busy"],
                "flooded": fs["flooded"],
            },
            "paid_server": {
                "total": ps["total"],
                "free": ps["free"],
                "busy": ps["busy"],
                "flooded": ps["flooded"],
            },
            "sessions": {
                "total": real_status["total"],
                "available": real_status["available"],
                "flooded": real_status["flooded"],
                "loaded": real_status["loaded"],
            },
            "watchers": len(db_list_watchers()),
            "queue_pending": len(db_list_queue(status="pending")),
            "retry_pending": retry_count_pending(),
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
    D(f"HTTP health server → port {port}", "ok")


# ══════════════════════ /ping COMMAND ══════════════════════
@bot.on(events.NewMessage(pattern="/ping"))
async def on_ping(event):
    try:
        if event.is_channel:
            return
        uptime = int(time.time() - _start_time)
        hrs = uptime // 3600
        mins = (uptime % 3600) // 60
        secs = uptime % 60
        stats = db_bot_stats()
        fs = get_pool_status("free")
        ps = get_pool_status("paid")
        real_status = real_get_status()
        await event.reply(
            f"🏓 **PONG!**\n"
            f"{DIV}\n\n"
            f"⏱️ Uptime: **{hrs}h {mins}m {secs}s**\n"
            f"👥 Users: **{db_total_users()}**\n"
            f"💫 Reactions: **{db_total_reactions()}**\n"
            f"📅 Today: **{db_reactions_today()}**\n\n"
            f"🤖 **BOTS: {stats['total']}**\n"
            f"   🆓 Free: **{stats['free']}**\n"
            f"      🟢{fs['free']} 🔴{fs['busy']} 🌊{fs['flooded']}\n"
            f"   💎 Paid: **{stats['paid']}**\n"
            f"      🟢{ps['free']} 🔴{ps['busy']} 🌊{ps['flooded']}\n\n"
            f"👤 Sessions: **{real_status['available']}/"
            f"{real_status['total']}**\n"
            f"📡 Watchers: **{len(db_list_watchers())}**\n"
            f"⏰ Queue: **{len(db_list_queue(status='pending'))}**\n"
            f"🎯 Task: "
            f"**{'🔴 Running' if TASK_RUNNING else '🟢 Idle'}**")
    except Exception as e:
        D_err(e, "on_ping")


# ══════════════════════ /status COMMAND (OWNER) ══════════════════════
@bot.on(events.NewMessage(pattern="/status"))
async def on_status(event):
    try:
        if event.is_channel:
            return
        if not OWNER_IS(event.sender_id):
            return
        stats = db_bot_stats()
        fs = get_pool_status("free")
        ps = get_pool_status("paid")
        real_status = real_get_status()
        await event.reply(
            f"📊 **SYSTEM STATUS**\n"
            f"{STAR_LINE}\n\n"
            f"**🆓 FREE SERVER:**\n"
            f"   🤖 Total: **{fs['total']}**\n"
            f"   🟢 Free: **{fs['free']}**\n"
            f"   🔴 Busy: **{fs['busy']}**\n"
            f"   🌊 Flooded: **{fs['flooded']}**\n\n"
            f"**💎 PAID SERVER:**\n"
            f"   🤖 Total: **{ps['total']}**\n"
            f"   🟢 Free: **{ps['free']}**\n"
            f"   🔴 Busy: **{ps['busy']}**\n"
            f"   🌊 Flooded: **{ps['flooded']}**\n\n"
            f"**📊 TOTAL:**\n"
            f"   🤖 Bots: **{stats['total']}**\n"
            f"   🔒 Permanent: **{stats['permanent']}**\n\n"
            f"**👤 Real Accounts:**\n"
            f"   📁 Total: **{real_status['total']}**\n"
            f"   ✅ Available: **{real_status['available']}**\n"
            f"   🌊 Flooded: **{real_status['flooded']}**\n"
            f"   💾 Loaded: **{real_status['loaded']}/"
            f"{real_status['max_clients']}**\n\n"
            f"**Task:** "
            f"**{'🔴 RUNNING' if TASK_RUNNING else '🟢 IDLE'}**\n"
            f"**Owner UID:** `{TASK_OWNER_UID or '—'}`\n\n"
            f"**Queue:** **{len(db_list_queue(status='pending'))}** pending\n"
            f"**Retry:** **{retry_count_pending()}** pending\n"
            f"**Watchers:** **{len(db_list_watchers())}**")
    except Exception as e:
        D_err(e, "on_status")


# ══════════════════════ MAIN ══════════════════════
async def main():
    global admin_client, backup_client, TASK_RUNNING, TASK_OWNER_UID

    # Global exception handler
    try:
        loop = asyncio.get_running_loop()
        loop.set_exception_handler(global_exception_handler)
    except Exception:
        pass

    # ═════ DB init (creates ALL tables) ═════
    db_init()

    # ═════ Clear stale in-memory state ═════
    FREE_POOL.clear()
    PAID_POOL.clear()
    FREE_FLOOD_UNTIL.clear()
    PAID_FLOOD_UNTIL.clear()
    FLOOD_UNTIL.clear()
    BOT_POOL.clear()
    ADMIN_CACHE.clear()
    ENTITY_CACHE.clear()
    BOT_ENTITY_CACHE.clear()
    OWNER_ENTITY_CACHE["entity"] = None
    OWNER_ENTITY_CACHE["expires_at"] = None
    FAILED_BOTS_TRACKER.clear()
    TASK_RUNNING = False
    TASK_OWNER_UID = None
    D("Cleared stale state (dual pools)", "pool")

    # ═════ Admin client ═════
    D("Starting admin client...", "step")
    admin_client = TelegramClient(StringSession(ADMIN_SESSION),
                                   API_ID, API_HASH)
    await admin_client.start()
    if not await admin_client.is_user_authorized():
        print("❌ Primary session invalid. Exiting.")
        return

    # ═════ Backup client (optional) ═════
    if BACKUP_SESSION_1 and len(BACKUP_SESSION_1) > 250:
        try:
            backup_client = TelegramClient(
                StringSession(BACKUP_SESSION_1), API_ID, API_HASH)
            await backup_client.start()
            if await backup_client.is_user_authorized():
                D("✅ Backup client ready", "backup")
            else:
                await backup_client.disconnect()
                backup_client = None
                D("⚠️ Backup not authorized", "warn")
        except Exception as e:
            backup_client = None
            D(f"⚠️ Backup failed: {str(e)[:80]}", "warn")

    # ═════ Admin info ═════
    me = await admin_client.get_me()

    # ═════ Sync bots to DB (with server split) ═════
    D(f"Bot tokens loaded: {len(BOT_TOKENS)} (deduped)", "ok")
    D(f"  → Free server: {len(FREE_SERVER_TOKENS)}", "free")
    D(f"  → Paid server: {len(PAID_SERVER_TOKENS)}", "paid")
    added = sync_bots()

    # ═════ Startup banner ═════
    D_sep("👻 GHOST REACTION BOT v73 — DUAL SERVER EDITION")
    D(f"Admin: {me.first_name} (@{me.username or 'no_username'})", "ok")
    D(f"Owner: @{get_owner_username()} (ID {get_owner_id()})", "ok")

    stats = db_bot_stats()
    D(f"Bots in DB: {stats['total']} "
      f"(F:{stats['free']} P:{stats['paid']} 🔒{stats['permanent']})", "ok")
    D(f"New bots added: {added}", "ok")

    D(f"Sessions: {real_count_available()}/"
      f"{len(discover_session_files())}", "real")
    D(f"MAX_CLIENTS: {MAX_CLIENTS}", "pool")
    D(f"BATCH_SIZE: {BATCH_SIZE} (Telegram limit: "
      f"{TELEGRAM_ADMIN_LIMIT})", "batch")
    D(f"Auto-approve: {'ON' if is_auto_approve() else 'OFF'}", "info")
    D(f"Languages: {len(LANGUAGES)}", "lang")
    D(f"Store packs: {store_count_active()}", "store")
    D(f"Coupons: {coupon_count_active()} active", "info")
    D(f"Daily Bonus: {'ON' if feat_daily_bonus() else 'OFF'}", "info")
    D(f"Auto-Retry: {'ON' if feat_auto_retry() else 'OFF'}", "rot")
    D(f"Smart Reaction: {'ON' if feat_smart_reaction() else 'OFF'}",
      "smart")
    D(f"Fallback: {'ON' if feat_fallback() else 'OFF'}", "fallback")
    D(f"Dual Server: {'ON' if feat_dual_server() else 'OFF'}", "server")
    D(f"GitHub sync: {'ON' if (HAS_GH_SYNC and github_sync.is_enabled())
                    else 'OFF'}", "gh")
    D("Bot online ✨", "ok")
    D_sep("READY — Listening for messages")

    # ═════ Background tasks ═════
    asyncio.create_task(start_health_server())
    asyncio.create_task(watcher_loop())
    asyncio.create_task(pool_cleaner_loop())
    asyncio.create_task(health_check_loop())
    asyncio.create_task(queue_loop())
    asyncio.create_task(retry_loop())
    asyncio.create_task(daily_summary_loop())
    asyncio.create_task(startup_bot_sync())
    D("Background tasks started (8 loops)", "ok")

    # ═════ Bot client start (with retry) ═════
    while True:
        try:
            await bot.start(bot_token=BOT_TOKEN)
            D("✅ Bot client connected", "ok")
            break
        except FloodWaitError as e:
            wait_sec = e.seconds + 30
            D(f"⚠️ Bot FloodWait — {wait_sec}s "
              f"({wait_sec // 60}min)", "flood")
            await asyncio.sleep(wait_sec)
        except Exception as e:
            D(f"⚠️ Bot start error: {str(e)[:100]}", "fail")
            await asyncio.sleep(30)

    # ═════ Run until disconnect ═════
    try:
        await bot.run_until_disconnected()
    finally:
        D("Shutting down...", "warn")
        # Final backup
        try:
            if HAS_GH_SYNC and github_sync.is_enabled():
                github_sync.upload_db(force=True)
                D("Final GitHub sync done", "gh")
        except Exception:
            pass
        # Close real clients
        try:
            await close_all_real_clients()
        except Exception:
            pass
        # Disconnect admin/backup
        try:
            if admin_client:
                await admin_client.disconnect()
        except Exception:
            pass
        try:
            if backup_client:
                await backup_client.disconnect()
        except Exception:
            pass
        D("Shutdown complete", "ok")


# ══════════════════════ ENTRY POINT ══════════════════════
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Stopped by user", flush=True)
    except Exception as e:
        print(f"\n❌ FATAL: {e}", flush=True)
        traceback.print_exc()
        sys.exit(1)
