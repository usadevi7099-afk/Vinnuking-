import os


def _int_env(name: str, default: str = "0") -> int:
    """Safely reads an int env var — treats missing AND blank values as the default."""
    value = os.environ.get(name) or default
    try:
        return int(value)
    except ValueError:
        return int(default)


# ==== Telegram Bot Credentials ====
API_ID = _int_env("API_ID" 31366247)
API_HASH = os.environ.get("API_HASH", "675f45eb05a46634c8726adac3c9929f")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8449062687:AAHC_l21QGdvYLP_2MSlGMKdxtGxnFX9eio")

# ==== Assistant Account (userbot) ====
# Generate this with a "string session generator" script (Pyrogram).
STRING_SESSION = os.environ.get("STRING_SESSION", "BQHenGcAQUNZAmPiw1McPr3T9hy-7ckpBky5UaGFJFA0_xf14yd-9IVxcZbEbX-X6U96KTcP0HsTKnIHPBIYWQ33l4HNuHod65Qs1jorIB2QImHiNF3TuDQYxYj8T6KqNpj9UvLZ4nqhZWgLvfJ3jvQ8liVnakLkvlLTiisr84dCSBsf8yB2MeG6lQPeGp2Dk5x8OWIoqhv9ELOaDcSFJLlptrFnN_D-NIkE-nXB1rxJpW-cVCjznEN6vw2dCXP4EYFBuYHwvFGKvdA4JpI4LvNAOMaglrtz1VonGa81KEmyq3_RSwgCYHB7kN6ecJdcFlkGLCHghIHlNgR-GqAv2MjTGPTywAAAAAISrr17AA")

# ==== Database ====
MONGO_DB_URI = os.environ.get("MONGO_DB_URI") or "mongodb://localhost:27017"

# ==== Owner / Admin ====
OWNER_ID = _int_env("OWNER_ID"7450836393 )

# ==== Logger group where /vclogger events get sent (optional) ====
LOG_GROUP_ID = _int_env("LOG_GROUP_ID")

# ==== Branding ====
BOT_NAME = os.environ.get("BOT_NAME", "Vani X Music")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "your_bot_username")
START_IMG = os.environ.get(
    "START_IMG",
    "https://telegra.ph/file/example-start-image.jpg",
)
SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", "https://t.me/+1UEpse66cugyZWNl")
UPDATES_CHANNEL = os.environ.get("UPDATES_CHANNEL", "https://t.me/Vinnu_channel_1")

# ==== Spotify (optional — for resolving Spotify links) ====
# From https://developer.spotify.com/dashboard (free, just needs an account)
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")

# ==== Defaults ====
DEFAULT_LANG = "en"
DEFAULT_PLAY_MODE = "user"  # "user" or "admin"
DEFAULT_AUTOPLAY = False

# ==== Download folder ====
DOWNLOADS_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
