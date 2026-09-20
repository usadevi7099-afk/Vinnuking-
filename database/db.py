import time
import motor.motor_asyncio
from config import MONGO_DB_URI, DEFAULT_LANG, DEFAULT_PLAY_MODE, DEFAULT_AUTOPLAY

mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DB_URI)
db = mongo_client["VaniMusicDB"]
chats_db = db["chats"]
users_db = db["users"]          # tracks every user who has DM'd the bot (for /broadcast)
gban_db = db["gbanned_users"]   # globally banned users
bot_settings_db = db["bot_settings"]  # single-document global bot settings

DEFAULT_SETTINGS = {
    "language": DEFAULT_LANG,
    "play_mode": DEFAULT_PLAY_MODE,   # "user" or "admin"
    "auth_users": [],
    "vclogger": False,
    "autoplay": DEFAULT_AUTOPLAY,
}


async def get_chat_settings(chat_id: int) -> dict:
    chat = await chats_db.find_one({"chat_id": chat_id})
    if not chat:
        settings = DEFAULT_SETTINGS.copy()
        settings["chat_id"] = chat_id
        await chats_db.insert_one(settings)
        return settings
    return chat


# ---------------- Language ----------------
async def get_language(chat_id: int) -> str:
    chat = await get_chat_settings(chat_id)
    return chat.get("language", DEFAULT_LANG)


async def set_language(chat_id: int, lang: str):
    await chats_db.update_one(
        {"chat_id": chat_id}, {"$set": {"language": lang}}, upsert=True
    )


# ---------------- Play Permission Mode ----------------
async def get_play_mode(chat_id: int) -> str:
    chat = await get_chat_settings(chat_id)
    return chat.get("play_mode", DEFAULT_PLAY_MODE)


async def set_play_mode(chat_id: int, mode: str):
    await chats_db.update_one(
        {"chat_id": chat_id}, {"$set": {"play_mode": mode}}, upsert=True
    )


# ---------------- Authorized Users (for Admin Mode) ----------------
async def get_auth_users(chat_id: int) -> list:
    chat = await get_chat_settings(chat_id)
    return chat.get("auth_users", [])


async def add_auth_user(chat_id: int, user_id: int):
    await chats_db.update_one(
        {"chat_id": chat_id}, {"$addToSet": {"auth_users": user_id}}, upsert=True
    )


async def remove_auth_user(chat_id: int, user_id: int):
    await chats_db.update_one(
        {"chat_id": chat_id}, {"$pull": {"auth_users": user_id}}
    )


# ---------------- VC Logger toggle ----------------
async def get_vclogger(chat_id: int) -> bool:
    chat = await get_chat_settings(chat_id)
    return chat.get("vclogger", False)


async def set_vclogger(chat_id: int, value: bool):
    await chats_db.update_one(
        {"chat_id": chat_id}, {"$set": {"vclogger": value}}, upsert=True
    )


# ---------------- Autoplay ----------------
async def get_autoplay(chat_id: int) -> bool:
    chat = await get_chat_settings(chat_id)
    return chat.get("autoplay", DEFAULT_AUTOPLAY)


async def set_autoplay(chat_id: int, value: bool):
    await chats_db.update_one(
        {"chat_id": chat_id}, {"$set": {"autoplay": value}}, upsert=True
    )


# ---------------- Utility ----------------
async def get_all_chats() -> list:
    chats = []
    async for chat in chats_db.find({}):
        chats.append(chat["chat_id"])
    return chats


# ---------------- Users (for /broadcast to reach private chats too) ----------------
async def add_served_user(user_id: int):
    await users_db.update_one(
        {"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True
    )


async def get_all_users() -> list:
    users = []
    async for user in users_db.find({}):
        users.append(user["user_id"])
    return users


# ---------------- Global Ban ----------------
async def gban_user(user_id: int, reason: str = "No reason given"):
    await gban_db.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, "reason": reason, "banned_at": time.time()}},
        upsert=True,
    )


async def ungban_user(user_id: int):
    await gban_db.delete_one({"user_id": user_id})


async def is_gbanned(user_id: int) -> bool:
    return await gban_db.find_one({"user_id": user_id}) is not None


async def get_gban_list() -> list:
    banned = []
    async for entry in gban_db.find({}):
        banned.append(entry)
    return banned


# ---------------- Global bot settings (maintenance mode, dynamic start image) ----------------
async def _get_bot_settings() -> dict:
    settings = await bot_settings_db.find_one({"_id": "global"})
    if not settings:
        settings = {"_id": "global", "maintenance": False, "start_img": None}
        await bot_settings_db.insert_one(settings)
    return settings


async def get_maintenance() -> bool:
    settings = await _get_bot_settings()
    return settings.get("maintenance", False)


async def set_maintenance(value: bool):
    await bot_settings_db.update_one(
        {"_id": "global"}, {"$set": {"maintenance": value}}, upsert=True
    )


async def get_start_img() -> str | None:
    """Returns the DB-stored start image (file_id or URL), or None if unset."""
    settings = await _get_bot_settings()
    return settings.get("start_img")


async def set_start_img(value: str):
    await bot_settings_db.update_one(
        {"_id": "global"}, {"$set": {"start_img": value}}, upsert=True
    )
