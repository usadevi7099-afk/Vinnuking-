"""
Resolves links from multiple platforms into something yt-dlp / ffmpeg
can actually stream:

- YouTube links       -> passed straight through to yt-dlp
- SoundCloud links    -> passed straight through (yt-dlp supports it natively)
- M3U8 links          -> passed straight through (ffmpeg streams it directly)
- Spotify track links -> resolved to "<track> <artist>" text, then searched
                         on YouTube (requires SPOTIFY_CLIENT_ID/SECRET)
- Apple Music links   -> page title scraped, then searched on YouTube
- Resso links         -> page title scraped, then searched on YouTube
- Plain text          -> returned as-is (treated as a YouTube search query)
"""

import re
import asyncio
import requests

from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

SPOTIFY_TRACK_RE = re.compile(r"open\.spotify\.com/track/([A-Za-z0-9]+)")
APPLE_MUSIC_RE = re.compile(r"music\.apple\.com/.+")
SOUNDCLOUD_RE = re.compile(r"soundcloud\.com/.+")
YOUTUBE_RE = re.compile(r"(youtube\.com|youtu\.be)/.+")
M3U8_RE = re.compile(r"\.m3u8($|\?)")
RESSO_RE = re.compile(r"resso\.com/.+")

_spotify_token_cache = {"token": None}


def _get_spotify_token() -> str | None:
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        return None
    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
        timeout=10,
    )
    if resp.status_code != 200:
        return None
    return resp.json().get("access_token")


def _resolve_spotify_track(track_id: str) -> str | None:
    token = _get_spotify_token()
    if not token:
        return None
    resp = requests.get(
        f"https://api.spotify.com/v1/tracks/{track_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    if resp.status_code != 200:
        return None
    data = resp.json()
    name = data.get("name", "")
    artists = ", ".join(a["name"] for a in data.get("artists", []))
    return f"{name} {artists}".strip()


def _scrape_og_title(url: str) -> str | None:
    """Generic fallback: grabs the <meta property="og:title"> from a page."""
    try:
        resp = requests.get(
            url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10
        )
        match = re.search(
            r'<meta property="og:title" content="([^"]+)"', resp.text
        )
        if match:
            return match.group(1)
    except Exception:
        return None
    return None


async def resolve_query(text: str) -> dict:
    """
    Returns:
        {"mode": "search", "query": "<text to search on YouTube>"}
        or
        {"mode": "direct", "url": "<url yt-dlp/ffmpeg can stream directly>"}
    """
    text = text.strip()

    def _run():
        if M3U8_RE.search(text) or YOUTUBE_RE.search(text) or SOUNDCLOUD_RE.search(text):
            return {"mode": "direct", "url": text}

        spotify_match = SPOTIFY_TRACK_RE.search(text)
        if spotify_match:
            query = _resolve_spotify_track(spotify_match.group(1))
            if query:
                return {"mode": "search", "query": query}
            return {"mode": "search", "query": text}

        if APPLE_MUSIC_RE.search(text) or RESSO_RE.search(text):
            title = _scrape_og_title(text)
            if title:
                return {"mode": "search", "query": title}
            return {"mode": "search", "query": text}

        # Plain text query (e.g. "king tu aake dekhle")
        return {"mode": "search", "query": text}

    return await asyncio.to_thread(_run)
