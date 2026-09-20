from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatType

from config import BOT_USERNAME, START_IMG, SUPPORT_CHAT, UPDATES_CHANNEL
from database.db import get_language, get_start_img, add_served_user
from helpers.language import get_string

HELP_COMMANDS = [
    ("🎵 /play", "/play"),
    ("🎥 /vplay", "/vplay"),
    ("♻️ /reload", "/reload"),
    ("⏸ /pause", "/pause"),
    ("⏹ /end", "/end"),
    ("⏭ /skip", "/skip"),
    ("🌐 /lang", "/lang"),
    ("🎶 /queue", "/queue"),
    ("🔁 /loop", "/loop"),
    ("🔄 /autoplay", "/autoplay"),
    ("🎙 /vclogger", "/vclogger"),
    ("🏓 /ping", "/ping"),
]

COMMAND_DETAILS_EN = {
    "/play": "🎵 **/play [song name]**\nPlays a song in the group voice chat (audio only).",
    "/vplay": "🎥 **/vplay [song name]**\nPlays a song as video in the group voice chat.",
    "/reload": "♻️ **/reload**\nRefreshes the bot's admin cache for the current chat.",
    "/pause": "⏸ **/pause**\nPauses the current playback.",
    "/end": "⏹ **/end**\nStops playback and makes the bot leave the voice chat.",
    "/skip": "⏭ **/skip**\nSkips to the next track in the queue.",
    "/lang": "🌐 **/lang**\nChange the bot's language (English 🇬🇧 / Hindi 🇮🇳).",
    "/queue": "🎶 **/queue**\nShows all tracks currently in the queue.",
    "/loop": "🔁 **/loop**\nToggles loop mode for the current track.",
    "/autoplay": "🔄 **/autoplay**\nWhen enabled, auto-plays a similar track once the queue is empty.\nAlso: /play accepts YouTube, Spotify, Apple Music, SoundCloud, and direct M3U8 links.",
    "/vclogger": "🎙 **/vclogger**\nToggles logging of voice-chat activity (admin only).",
    "/ping": "🏓 **/ping**\nChecks the bot's response latency.",
}

COMMAND_DETAILS_HI = {
    "/play": "🎵 **/play [गाने का नाम]**\nग्रुप वॉइस चैट में गाना (ऑडियो) चलाता है।",
    "/vplay": "🎥 **/vplay [गाने का नाम]**\nग्रुप वॉइस चैट में गाना वीडियो के रूप में चलाता है।",
    "/reload": "♻️ **/reload**\nमौजूदा चैट के लिए बॉट का एडमिन कैश रीफ्रेश करता है।",
    "/pause": "⏸ **/pause**\nमौजूदा प्लेबैक को पॉज़ करता है।",
    "/end": "⏹ **/end**\nप्लेबैक रोकता है और बॉट को वॉइस चैट से बाहर करता है।",
    "/skip": "⏭ **/skip**\nक्यू में अगले ट्रैक पर जाता है।",
    "/lang": "🌐 **/lang**\nबॉट की भाषा बदलें (English 🇬🇧 / हिन्दी 🇮🇳)।",
    "/queue": "🎶 **/queue**\nक्यू में मौजूद सभी ट्रैक दिखाता है।",
    "/loop": "🔁 **/loop**\nमौजूदा ट्रैक के लिए लूप मोड चालू/बंद करता है।",
    "/autoplay": "🔄 **/autoplay**\nचालू होने पर, क्यू खाली होने पर मिलता-जुलता गाना अपने आप चलेगा।\n/play अब YouTube, Spotify, Apple Music, SoundCloud और M3U8 लिंक भी स्वीकार करता है।",
    "/vclogger": "🎙 **/vclogger**\nवॉइस चैट एक्टिविटी की लॉगिंग चालू/बंद करता है (सिर्फ एडमिन)।",
    "/ping": "🏓 **/ping**\nबॉट की रिस्पॉन्स स्पीड चेक करता है।",
}


def start_buttons(is_private: bool) -> InlineKeyboardMarkup:
    rows = []
    if is_private:
        rows.append(
            [InlineKeyboardButton(
                "➕ ADD ME", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
            )]
        )
    rows.append([InlineKeyboardButton("⚙️ SETTINGS / HELP", callback_data="open_help")])
    rows.append(
        [
            InlineKeyboardButton("📢 BOT UPDATES", url=UPDATES_CHANNEL),
            InlineKeyboardButton("💬 BOT SUPPORT", url=SUPPORT_CHAT),
        ]
    )
    return InlineKeyboardMarkup(rows)


def help_buttons() -> InlineKeyboardMarkup:
    rows = []
    row = []
    for i, (label, cmd) in enumerate(HELP_COMMANDS, 1):
        row.append(InlineKeyboardButton(label, callback_data=f"help_{cmd.strip('/')}"))
        if i % 3 == 0:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("⬅️ BACK", callback_data="back_start")])
    return InlineKeyboardMarkup(rows)


@Client.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    lang = await get_language(message.chat.id)
    if message.chat.type == ChatType.PRIVATE:
        await add_served_user(message.from_user.id)

    text = get_string(lang, "start").format(mention=message.from_user.mention)
    is_private = message.chat.type == ChatType.PRIVATE
    img = await get_start_img() or START_IMG
    await message.reply_photo(
        img,
        caption=text,
        reply_markup=start_buttons(is_private),
    )


@Client.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    lang = await get_language(message.chat.id)
    text = get_string(lang, "help_title")
    img = await get_start_img() or START_IMG
    await message.reply_photo(
        img,
        caption=text,
        reply_markup=help_buttons(),
    )
