from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_USERNAME, START_IMG
from database.db import get_language, get_start_img
from helpers.language import get_string


@Client.on_message(filters.new_chat_members)
async def welcome_cmd(client: Client, message: Message):
    me = await client.get_me()
    for member in message.new_chat_members:
        if member.id == me.id:
            lang = await get_language(message.chat.id)
            text = get_string(lang, "added_to_group").format(
                bot_username=BOT_USERNAME,
                mention=message.from_user.mention if message.from_user else "Someone",
                chat_title=message.chat.title,
                chat_id=message.chat.id,
            )
            kb = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🌐 LANGUAGE", callback_data="open_help")],
                ]
            )
            img = await get_start_img() or START_IMG
            await message.reply_photo(img, caption=text, reply_markup=kb)
