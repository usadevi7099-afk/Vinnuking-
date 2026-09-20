from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus, ChatType

from database.db import get_play_mode, get_auth_users


async def is_chat_admin(client: Client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
        )
    except Exception:
        return False


async def can_user_play(client: Client, message: Message) -> bool:
    """Checks Play Permission Mode (User Mode / Admin Mode)."""
    if message.chat.type == ChatType.PRIVATE:
        return True

    chat_id = message.chat.id
    user_id = message.from_user.id
    mode = await get_play_mode(chat_id)

    if mode == "user":
        return True

    # Admin mode: allow admins + authorized users
    if user_id in await get_auth_users(chat_id):
        return True

    return await is_chat_admin(client, chat_id, user_id)
