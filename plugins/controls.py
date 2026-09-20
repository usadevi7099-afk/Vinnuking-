from pyrogram import Client, filters
from pyrogram.types import Message

from database.db import get_language, get_autoplay, set_autoplay
from helpers.language import get_string
from helpers.decorators import can_user_play
from helpers.trackqueue import get_queue, get_loop, set_loop
from helpers import calls


@Client.on_message(filters.command("pause") & filters.group)
async def pause_cmd(client: Client, message: Message):
    lang = await get_language(message.chat.id)
    if not await can_user_play(client, message):
        return await message.reply_text(get_string(lang, "no_permission"))
    await calls.pause_stream(message.chat.id)
    await message.reply_text(get_string(lang, "paused"))


@Client.on_message(filters.command("resume") & filters.group)
async def resume_cmd(client: Client, message: Message):
    lang = await get_language(message.chat.id)
    if not await can_user_play(client, message):
        return await message.reply_text(get_string(lang, "no_permission"))
    await calls.resume_stream(message.chat.id)
    await message.reply_text(get_string(lang, "resumed"))


@Client.on_message(filters.command("skip") & filters.group)
async def skip_cmd(client: Client, message: Message):
    lang = await get_language(message.chat.id)
    if not await can_user_play(client, message):
        return await message.reply_text(get_string(lang, "no_permission"))

    nxt = await calls.skip_stream(message.chat.id)
    if nxt is None:
        await message.reply_text(get_string(lang, "queue_empty"))
    else:
        await message.reply_text(
            get_string(lang, "streaming").format(
                title=nxt["title"], duration=nxt["duration"], requester=nxt["requester"]
            )
        )


@Client.on_message(filters.command("end") & filters.group)
async def end_cmd(client: Client, message: Message):
    lang = await get_language(message.chat.id)
    if not await can_user_play(client, message):
        return await message.reply_text(get_string(lang, "no_permission"))
    await calls.leave_call(message.chat.id)
    await message.reply_text(get_string(lang, "ended"))


@Client.on_message(filters.command("queue") & filters.group)
async def queue_cmd(client: Client, message: Message):
    lang = await get_language(message.chat.id)
    q = get_queue(message.chat.id)
    if not q:
        return await message.reply_text(get_string(lang, "queue_empty"))

    lines = []
    for i, track in enumerate(q, 1):
        marker = "▶️" if i == 1 else f"{i}."
        lines.append(f"{marker} {track['title']} — {track['duration']}")
    await message.reply_text(get_string(lang, "queue_title").format(tracks="\n".join(lines)))


@Client.on_message(filters.command("loop") & filters.group)
async def loop_cmd(client: Client, message: Message):
    lang = await get_language(message.chat.id)
    if not await can_user_play(client, message):
        return await message.reply_text(get_string(lang, "no_permission"))

    chat_id = message.chat.id
    new_val = not get_loop(chat_id)
    set_loop(chat_id, new_val)
    await message.reply_text(get_string(lang, "loop_on" if new_val else "loop_off"))


@Client.on_message(filters.command("autoplay") & filters.group)
async def autoplay_cmd(client: Client, message: Message):
    lang = await get_language(message.chat.id)
    if not await can_user_play(client, message):
        return await message.reply_text(get_string(lang, "no_permission"))

    chat_id = message.chat.id
    new_val = not await get_autoplay(chat_id)
    await set_autoplay(chat_id, new_val)
    if lang == "hi":
        msg = "🔄 ऑटोप्ले चालू। क्यू खाली होने पर मिलता-जुलता गाना अपने आप चलेगा।" if new_val \
            else "🔄 ऑटोप्ले बंद।"
    else:
        msg = "🔄 Autoplay enabled. A similar track will auto-play when the queue is empty." if new_val \
            else "🔄 Autoplay disabled."
    await message.reply_text(msg)
