import asyncio
import logging

from pyrogram import Client, idle
from pytgcalls import PyTgCalls
from pytgcalls.types import Update as PyTgCallsUpdate

from config import API_ID, API_HASH, BOT_TOKEN, STRING_SESSION, BOT_NAME
from database.db import get_language, get_autoplay
from helpers.language import get_string
from helpers.trackqueue import advance_queue, current_track, push_queue, add_history, get_history
from helpers.ytdl import find_autoplay_track
from helpers import calls as calls_helper

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler(),
    ],
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

# Bot client (runs as a bot, handles all commands)
bot = Client(
    name="VaniMusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins"),
)

# Assistant/userbot client (joins the actual voice chat and streams audio/video)
assistant = Client(
    name="VaniMusicAssistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION,
)

call_py = PyTgCalls(assistant)
calls_helper.bind(call_py)


@call_py.on_update()
async def on_stream_update(client: PyTgCalls, update: PyTgCallsUpdate):
    """
    Handles stream-end events: auto-advances the queue, or sends the
    'stream has ended' message and leaves the call if the queue is empty.
    """
    chat_id = getattr(update, "chat_id", None)
    if chat_id is None:
        return

    # Only react to "stream finished" style updates.
    if update.__class__.__name__ not in ("StreamAudioEnded", "StreamVideoEnded"):
        return

    finished_track = current_track(chat_id)
    if finished_track:
        add_history(chat_id, finished_track["title"])

    nxt = advance_queue(chat_id)

    if nxt is None and await get_autoplay(chat_id) and finished_track:
        # Queue is empty but autoplay is on — find and queue a similar track.
        try:
            auto_track = await find_autoplay_track(
                finished_track["title"], get_history(chat_id)
            )
            if auto_track:
                auto_track["requester"] = "Autoplay 🔄"
                push_queue(chat_id, auto_track)
                nxt = auto_track
        except Exception as e:
            LOGGER.warning(f"Autoplay lookup failed: {e}")

    if nxt is None:
        lang = await get_language(chat_id)
        try:
            await calls_helper.leave_call(chat_id)
            await bot.send_message(chat_id, get_string(lang, "stream_ended"))
        except Exception as e:
            LOGGER.warning(f"Could not send stream-ended message: {e}")
    else:
        try:
            await calls_helper.start_stream(chat_id, nxt)
            lang = await get_language(chat_id)
            await bot.send_message(
                chat_id,
                get_string(lang, "streaming").format(
                    title=nxt["title"],
                    duration=nxt["duration"],
                    requester=nxt["requester"],
                ),
            )
        except Exception as e:
            LOGGER.warning(f"Could not auto-play next track: {e}")


async def main():
    await bot.start()
    await assistant.start()
    await call_py.start()

    me = await bot.get_me()
    LOGGER.info(f"{BOT_NAME} started as @{me.username}")

    await idle()

    await call_py.stop()
    await assistant.stop()
    await bot.stop()
    LOGGER.info("Bot stopped. Bye!")


if __name__ == "__main__":
    asyncio.run(main())
