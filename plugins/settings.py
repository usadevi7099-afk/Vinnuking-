from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from database.db import (
    get_language,
    get_play_mode,
    add_auth_user,
    remove_auth_user,
)
from helpers.language import get_string
from helpers.decorators import is_chat_admin
from plugins.callbacks import playmode_buttons


@Client.on_message(filters.command("lang"))
async def lang_cmd(client: Client, message: Message):
    lang = await get_language(message.chat.id)
    kb = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🇬🇧 English", callback_data="setlang_en"),
                InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="setlang_hi"),
            ]
        ]
    )
    await message.reply_text(get_string(lang, "lang_choose"), reply_markup=kb)


@Client.on_message(filters.command("settings") & filters.group)
async def settings_cmd(client: Client, message: Message):
    lang = await get_language(message.chat.id)
    if not await is_chat_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text(get_string(lang, "not_admin"))

    mode = await get_play_mode(message.chat.id)
    await message.reply_text(
        get_string(lang, "play_mode_title"),
        reply_markup=playmode_buttons(mode),
    )


@Client.on_message(filters.command("authuser") & filters.group)
async def authuser_cmd(client: Client, message: Message):
    lang = await get_language(message.chat.id)
    if not await is_chat_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text(get_string(lang, "not_admin"))
    if not message.reply_to_message:
        return await message.reply_text(get_string(lang, "auth_usage"))

    user = message.reply_to_message.from_user
    await add_auth_user(message.chat.id, user.id)
    await message.reply_text(get_string(lang, "auth_added").format(user=user.mention))


@Client.on_message(filters.command("unauthuser") & filters.group)
async def unauthuser_cmd(client: Client, message: Message):
    lang = await get_language(message.chat.id)
    if not await is_chat_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text(get_string(lang, "not_admin"))
    if not message.reply_to_message:
        return await message.reply_text(get_string(lang, "auth_usage"))

    user = message.reply_to_message.from_user
    await remove_auth_user(message.chat.id, user.id)
    await message.reply_text(get_string(lang, "auth_removed").format(user=user.mention))
