from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database.db import (
    get_language,
    set_language,
    get_play_mode,
    set_play_mode,
)
from helpers.language import get_string
from helpers.decorators import is_chat_admin
from helpers import calls
from plugins.start import (
    start_buttons,
    help_buttons,
    COMMAND_DETAILS_EN,
    COMMAND_DETAILS_HI,
)


# ---------------- Help menu navigation ----------------
@Client.on_callback_query(filters.regex(r"^open_help$"))
async def open_help_cb(client: Client, cq: CallbackQuery):
    lang = await get_language(cq.message.chat.id)
    await cq.message.edit_caption(
        get_string(lang, "help_title"), reply_markup=help_buttons()
    )


@Client.on_callback_query(filters.regex(r"^back_start$"))
async def back_start_cb(client: Client, cq: CallbackQuery):
    lang = await get_language(cq.message.chat.id)
    text = get_string(lang, "start").format(mention=cq.from_user.mention)
    await cq.message.edit_caption(
        text, reply_markup=start_buttons(is_private=True)
    )


@Client.on_callback_query(filters.regex(r"^help_(.+)$"))
async def help_detail_cb(client: Client, cq: CallbackQuery):
    cmd = "/" + cq.matches[0].group(1)
    lang = await get_language(cq.message.chat.id)
    details = COMMAND_DETAILS_HI if lang == "hi" else COMMAND_DETAILS_EN
    text = details.get(cmd, cmd)
    back_kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ BACK", callback_data="open_help")]]
    )
    await cq.message.edit_caption(text, reply_markup=back_kb)


# ---------------- Language selection ----------------
@Client.on_callback_query(filters.regex(r"^setlang_(en|hi)$"))
async def set_lang_cb(client: Client, cq: CallbackQuery):
    new_lang = cq.matches[0].group(1)
    await set_language(cq.message.chat.id, new_lang)
    text = get_string(new_lang, "lang_changed").format(
        flag="🇬🇧" if new_lang == "en" else "🇮🇳",
        name="English" if new_lang == "en" else "हिन्दी",
    )
    await cq.answer(text, show_alert=True)
    await cq.message.edit_text(text)


# ---------------- Play permission mode toggle ----------------
@Client.on_callback_query(filters.regex(r"^toggle_playmode$"))
async def toggle_playmode_cb(client: Client, cq: CallbackQuery):
    if not await is_chat_admin(client, cq.message.chat.id, cq.from_user.id):
        lang = await get_language(cq.message.chat.id)
        await cq.answer(get_string(lang, "not_admin"), show_alert=True)
        return

    chat_id = cq.message.chat.id
    lang = await get_language(chat_id)
    current = await get_play_mode(chat_id)
    new_mode = "admin" if current == "user" else "user"
    await set_play_mode(chat_id, new_mode)

    mode_label = "User Mode" if lang == "en" else "यूज़र मोड"
    if new_mode == "admin":
        mode_label = "Admin Mode" if lang == "en" else "एडमिन मोड"

    text = get_string(lang, "play_mode_set").format(mode=mode_label)
    await cq.answer(text, show_alert=True)
    await cq.message.edit_text(
        get_string(lang, "play_mode_title"),
        reply_markup=playmode_buttons(new_mode),
    )


def playmode_buttons(current_mode: str) -> InlineKeyboardMarkup:
    user_label = "USER MODE " + ("✅" if current_mode == "user" else "")
    admin_label = "ADMIN MODE " + ("✅" if current_mode == "admin" else "")
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(user_label if current_mode == "user" else admin_label,
                                   callback_data="toggle_playmode")],
            [InlineKeyboardButton("👥 AUTH USERS", callback_data="show_authinfo")],
            [InlineKeyboardButton("⬅️ BACK", callback_data="close_settings")],
        ]
    )


@Client.on_callback_query(filters.regex(r"^show_authinfo$"))
async def show_authinfo_cb(client: Client, cq: CallbackQuery):
    lang = await get_language(cq.message.chat.id)
    text = get_string(lang, "auth_usage")
    await cq.answer(text, show_alert=True)


@Client.on_callback_query(filters.regex(r"^close_settings$"))
async def close_settings_cb(client: Client, cq: CallbackQuery):
    await cq.message.delete()


# ---------------- Now-playing card controls ----------------
@Client.on_callback_query(filters.regex(r"^np_pause$"))
async def np_pause_cb(client: Client, cq: CallbackQuery):
    lang = await get_language(cq.message.chat.id)
    await calls.pause_stream(cq.message.chat.id)
    await cq.answer(get_string(lang, "paused"))


@Client.on_callback_query(filters.regex(r"^np_resume$"))
async def np_resume_cb(client: Client, cq: CallbackQuery):
    lang = await get_language(cq.message.chat.id)
    await calls.resume_stream(cq.message.chat.id)
    await cq.answer(get_string(lang, "resumed"))


@Client.on_callback_query(filters.regex(r"^np_skip$"))
async def np_skip_cb(client: Client, cq: CallbackQuery):
    lang = await get_language(cq.message.chat.id)
    await calls.skip_stream(cq.message.chat.id)
    await cq.answer(get_string(lang, "skipped"))
