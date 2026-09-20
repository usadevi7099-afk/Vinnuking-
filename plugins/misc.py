import time
import os
import sys

from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import Message

from config import OWNER_ID
from database.db import get_language, set_vclogger, get_vclogger
from helpers.language import get_string
from helpers.decorators import is_chat_admin


@Client.on_message(filters.command("ping"))
async def ping_cmd(client: Client, message: Message):
    lang = await get_language(message.chat.id)
    start = time.time()
    msg = await message.reply_text("🏓")
    ping_ms = round((time.time() - start) * 1000, 2)
    await msg.edit_text(get_string(lang, "pong").format(ping=ping_ms))


@Client.on_message(filters.command("reload") & filters.group)
async def reload_cmd(client: Client, message: Message):
    lang = await get_language(message.chat.id)
    if not await is_chat_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text(get_string(lang, "not_admin"))
    # Refresh admin cache for this chat
    async for _ in client.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
        pass
    await message.reply_text(get_string(lang, "reloaded"))


@Client.on_message(filters.command("reboot"))
async def reboot_cmd(client: Client, message: Message):
    lang = await get_language(message.chat.id)
    if message.from_user.id != OWNER_ID:
        return await message.reply_text(get_string(lang, "owner_only"))
    await message.reply_text(get_string(lang, "rebooting"))
    os.execl(sys.executable, sys.executable, *sys.argv)


@Client.on_message(filters.command("vclogger") & filters.group)
async def vclogger_cmd(client: Client, message: Message):
    lang = await get_language(message.chat.id)
    if not await is_chat_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text(get_string(lang, "not_admin"))

    chat_id = message.chat.id
    new_val = not await get_vclogger(chat_id)
    await set_vclogger(chat_id, new_val)
    await message.reply_text(get_string(lang, "vclogger_on" if new_val else "vclogger_off"))
