from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from pytgcalls.exceptions import NoActiveGroupCall

from helpers.trackqueue import current_track, advance_queue, clear_queue

call_py: PyTgCalls = None  # set from main.py after assistant client is created


def bind(pytgcalls_instance: PyTgCalls):
    global call_py
    call_py = pytgcalls_instance


async def start_stream(chat_id: int, track: dict):
    # MediaStream auto-detects audio/video from the file itself, so we
    # don't need to force any flags here — this keeps us on the stable,
    # documented part of the API instead of guessing at optional kwargs.
    stream = MediaStream(track["file_path"])
    try:
        await call_py.play(chat_id, stream)
    except NoActiveGroupCall:
        raise
    return True


async def pause_stream(chat_id: int):
    await call_py.pause(chat_id)


async def resume_stream(chat_id: int):
    await call_py.resume(chat_id)


async def leave_call(chat_id: int):
    clear_queue(chat_id)
    try:
        await call_py.leave_call(chat_id)
    except Exception:
        pass


async def skip_stream(chat_id: int):
    """Advances the queue and plays the next track, if any."""
    nxt = advance_queue(chat_id)
    if nxt is None:
        await leave_call(chat_id)
        return None
    await start_stream(chat_id, nxt)
    return nxt


def get_current(chat_id: int):
    return current_track(chat_id)
