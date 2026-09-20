"""
Simple in-memory queue manager.
Structure: QUEUES[chat_id] = [track_dict, track_dict, ...]
track_dict = {
    "title": str,
    "duration": str,
    "file_path": str,
    "requester": str,
    "is_video": bool,
}
LOOP[chat_id] = bool
"""

QUEUES: dict[int, list] = {}
LOOP: dict[int, bool] = {}
HISTORY: dict[int, list] = {}  # titles already played, used by autoplay


def get_queue(chat_id: int) -> list:
    return QUEUES.setdefault(chat_id, [])


def push_queue(chat_id: int, track: dict) -> int:
    q = get_queue(chat_id)
    q.append(track)
    return len(q)


def pop_next(chat_id: int):
    q = get_queue(chat_id)
    if not q:
        return None
    if LOOP.get(chat_id):
        return q[0]
    return q.pop(0) if q else None


def clear_queue(chat_id: int):
    QUEUES[chat_id] = []
    LOOP[chat_id] = False
    HISTORY[chat_id] = []


def add_history(chat_id: int, title: str):
    HISTORY.setdefault(chat_id, []).append(title)
    # keep it bounded
    HISTORY[chat_id] = HISTORY[chat_id][-20:]


def get_history(chat_id: int) -> list:
    return HISTORY.get(chat_id, [])


def current_track(chat_id: int):
    q = get_queue(chat_id)
    return q[0] if q else None


def advance_queue(chat_id: int):
    """Removes the finished track (unless looping) and returns the next one."""
    q = get_queue(chat_id)
    if not q:
        return None
    if not LOOP.get(chat_id, False):
        q.pop(0)
    return q[0] if q else None


def set_loop(chat_id: int, value: bool):
    LOOP[chat_id] = value


def get_loop(chat_id: int) -> bool:
    return LOOP.get(chat_id, False)
