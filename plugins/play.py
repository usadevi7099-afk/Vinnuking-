from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls.exceptions import NoActiveGroupCall

from database.db import get_language
from helpers.language import get_string
from helpers.decorators import can_user_play
from helpers.ytdl import download_resolved
from helpers.link_resolver import resolve_query
from helpers.trackqueue import get_queue, push_queue, add_history
from helpers import calls


def now_playing_buttons() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⏸ Pause", callback_data="np_pause"),
                InlineKeyboardButton("▶️ Resume", callback_data="np_resume"),
                InlineKeyboardButton("⏭ Skip", callback_data="np_skip"),
            ]
        ]
    )


async def _play(client: Client, message: Message, video: bool):
    lang = await get_language(message.chat.id)

    if not await can_user_play(client, message):
        await message.reply_text(get_string(lang, "no_permission"))
        return

    if len(message.command) < 2:
        await message.reply_text("❓ " + ("Please give me a song name." if lang == "en" else "कृपया गाने का नाम दें।"))
        return

    query = message.text.split(None, 1)[1]
    search_msg = await message.reply_text(get_string(lang, "searching").format(query=query))

    # Detects YouTube / Spotify / Apple Music / SoundCloud / M3U8 links,
    # resolving each to something yt-dlp can actually stream.
    resolved = await resolve_query(query)

    try:
        track = await download_resolved(resolved, video=video)
    except Exception as e:
        await search_msg.edit_text(f"❌ Error: `{e}`")
        return

    track["requester"] = message.from_user.mention

    chat_id = message.chat.id
    position = push_queue(chat_id, track)
    add_history(chat_id, track["title"])

    try:
        if position == 1:
            await calls.start_stream(chat_id, track)
            await search_msg.edit_text(
                get_string(lang, "streaming").format(
                    title=track["title"],
                    duration=track["duration"],
                    requester=track["requester"],
                ),
                reply_markup=now_playing_buttons(),
            )
        else:
            await search_msg.edit_text(
                get_string(lang, "added_to_queue").format(
                    title=track["title"], position=position - 1
                )
            )
    except NoActiveGroupCall:
        # remove the track we just pushed since we couldn't start it
        q = get_queue(chat_id)
        if track in q:
            q.remove(track)
        await search_msg.edit_text(get_string(lang, "no_vc"))


@Client.on_message(filters.command("play") & filters.group)
async def play_cmd(client: Client, message: Message):
    await _play(client, message, video=False)


@Client.on_message(filters.command("vplay") & filters.group)
async def vplay_cmd(client: Client, message: Message):
    await _play(client, message, video=True)
