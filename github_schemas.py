
"""SQL schemas for GitHub sync."""
from github_sync import GH_FILES  # noqa

SCHEMAS = {
    "users": (
        """CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY, first_name TEXT, username TEXT,
            joined_at TEXT, last_active TEXT, is_banned INTEGER DEFAULT 0,
            total_reactions INTEGER DEFAULT 0, total_bots INTEGER DEFAULT 0,
            custom_limit INTEGER DEFAULT 0, auto_watch_unlocked INTEGER DEFAULT 0,
            allow_channel INTEGER DEFAULT 1, allow_group INTEGER DEFAULT 1,
            allow_manual INTEGER DEFAULT 1, allow_autowatch INTEGER DEFAULT 0,
            allow_custom_emoji INTEGER DEFAULT 1, plan TEXT DEFAULT 'free',
            plan_expires TEXT, free_balance INTEGER DEFAULT 0,
            language TEXT DEFAULT 'en', referral_code TEXT,
            referred_by INTEGER DEFAULT 0, referral_count INTEGER DEFAULT 0,
            referral_earned INTEGER DEFAULT 0, team_role TEXT DEFAULT 'user',
            team_commission INTEGER DEFAULT 0, total_spent INTEGER DEFAULT 0)""",
        ["user_id","first_name","username","joined_at","last_active","is_banned",
         "total_reactions","total_bots","custom_limit","auto_watch_unlocked",
         "allow_channel","allow_group","allow_manual","allow_autowatch",
         "allow_custom_emoji","plan","plan_expires","free_balance","language",
         "referral_code","referred_by","referral_count","referral_earned",
         "team_role","team_commission","total_spent"]
    ),
    "approvals": (
        """CREATE TABLE IF NOT EXISTS approvals (
            user_id INTEGER PRIMARY KEY, first_name TEXT, username TEXT,
            status TEXT, requested_at TEXT, decided_at TEXT, approved_by INTEGER)""",
        ["user_id","first_name","username","status","requested_at","decided_at","approved_by"]
    ),
    "bots": (
        """CREATE TABLE IF NOT EXISTS bots (
            token TEXT PRIMARY KEY, username TEXT, bot_id INTEGER, added_at TEXT)""",
        ["token","username","bot_id","added_at"]
    ),
    "watchers": (
        """CREATE TABLE IF NOT EXISTS watchers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            chat_id INTEGER, chat_title TEXT, chat_link TEXT, chat_type TEXT,
            reaction_count INTEGER DEFAULT 5, emoji_mode TEXT DEFAULT 'default',
            custom_emojis TEXT, last_post_id INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1, created_at TEXT, last_run TEXT)""",
        ["id","user_id","chat_id","chat_title","chat_link","chat_type",
         "reaction_count","emoji_mode","custom_emojis","last_post_id",
         "is_active","created_at","last_run"]
    ),
    "templates": (
        """CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            name TEXT, emojis TEXT, created_at TEXT)""",
        ["id","user_id","name","emojis","created_at"]
    ),
    "referrals": (
        """CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT, referrer_id INTEGER,
            new_user_id INTEGER, status TEXT, reward_given INTEGER DEFAULT 0,
            created_at TEXT, validated_at TEXT)""",
        ["id","referrer_id","new_user_id","status","reward_given","created_at","validated_at"]
    ),
    "notifications": (
        """CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            message TEXT, is_read INTEGER DEFAULT 0, created_at TEXT)""",
        ["id","user_id","message","is_read","created_at"]
    ),
    "queue": (
        """CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            chat_link TEXT, post_link TEXT, reaction_count INTEGER,
            emoji_mode TEXT DEFAULT 'default', custom_emojis TEXT,
            scheduled_time TEXT, status TEXT DEFAULT 'pending',
            created_at TEXT, executed_at TEXT, error TEXT)""",
        ["id","user_id","chat_link","post_link","reaction_count","emoji_mode",
         "custom_emojis","scheduled_time","status","created_at","executed_at","error"]
    ),
    "payments": (
        """CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            amount INTEGER, plan TEXT, days INTEGER, method TEXT,
            screenshot TEXT, status TEXT DEFAULT 'pending',
            created_at TEXT, verified_at TEXT, verified_by INTEGER, notes TEXT)""",
        ["id","user_id","amount","plan","days","method","screenshot","status",
         "created_at","verified_at","verified_by","notes"]
    ),
    "force_channels": (
        """CREATE TABLE IF NOT EXISTS force_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT, channel TEXT UNIQUE,
            url TEXT, name TEXT, active INTEGER DEFAULT 1, added_at TEXT)""",
        ["id","channel","url","name","active","added_at"]
    ),
    "team": (
        """CREATE TABLE IF NOT EXISTS team_members (
            user_id INTEGER PRIMARY KEY, role TEXT, permissions TEXT,
            commission_percent INTEGER DEFAULT 0, total_sales INTEGER DEFAULT 0,
            total_commission INTEGER DEFAULT 0, added_at TEXT)""",
        ["user_id","role","permissions","commission_percent",
         "total_sales","total_commission","added_at"]
    ),
    "custom_packs": (
        """CREATE TABLE IF NOT EXISTS custom_packs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, emojis TEXT,
            price INTEGER DEFAULT 0, is_paid INTEGER DEFAULT 0, created_at TEXT)""",
        ["id","name","emojis","price","is_paid","created_at"]
    ),
    "reactions": (
        """CREATE TABLE IF NOT EXISTS reactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            chat_title TEXT, chat_id INTEGER, post_link TEXT, post_id INTEGER,
            emoji TEXT, bot_username TEXT, status TEXT, created_at TEXT)""",
        ["id","user_id","chat_title","chat_id","post_link","post_id",
         "emoji","bot_username","status","created_at"]
    ),
    "config": (
        """CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY, value TEXT)""",
        ["key","value"]
    ),
    "security_logs": (
        """CREATE TABLE IF NOT EXISTS security_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,
            action TEXT, details TEXT, ip TEXT, created_at TEXT)""",
        ["id","user_id","action","details","ip","created_at"]
    ),
}
