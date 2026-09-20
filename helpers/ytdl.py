import os
import asyncio
import yt_dlp

from config import DOWNLOADS_DIR


def _human_duration(seconds: int) -> str:
    if not seconds:
        return "Live"
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def _base_opts(video: bool) -> dict:
    return {
        "format": "best[height<=?720]" if video else "bestaudio/best",
        "outtmpl": os.path.join(DOWNLOADS_DIR, "%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch",
        "geo_bypass": True,
        "postprocessors": (
            []
            if video
            else [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]
        ),
    }


def _download_sync(target: str, video: bool) -> dict:
    """target can be a search query OR a direct URL (YouTube/SoundCloud/M3U8)."""
    with yt_dlp.YoutubeDL(_base_opts(video)) as ydl:
        info = ydl.extract_info(target, download=True)
        if "entries" in info:
            info = info["entries"][0]
        file_path = ydl.prepare_filename(info)
        if not video:
            file_path = os.path.splitext(file_path)[0] + ".mp3"
        return {
            "title": info.get("title", "Unknown"),
            "duration": _human_duration(info.get("duration", 0)),
            "file_path": file_path,
            "webpage_url": info.get("webpage_url", target),
            "is_video": video,
        }


async def download_resolved(resolved: dict, video: bool = False) -> dict:
    """
    Takes the output of helpers.link_resolver.resolve_query() and downloads
    it — works for a plain search query, a YouTube link, a SoundCloud link,
    or a raw M3U8 stream URL.
    """
    target = resolved["query"] if resolved["mode"] == "search" else resolved["url"]
    return await asyncio.to_thread(_download_sync, target, video)


async def search_and_download(query: str, video: bool = False) -> dict:
    """Back-compat helper: plain YouTube search + download."""
    return await asyncio.to_thread(_download_sync, query, video)


async def find_autoplay_track(previous_title: str, already_played: list) -> dict | None:
    """
    Very lightweight 'autoplay': searches YouTube using the previous track's
    title and picks the first result that hasn't already been played in
    this session, then downloads it.
    """

    def _run():
        opts = _base_opts(video=False)
        opts["noplaylist"] = True
        with yt_dlp.YoutubeDL({**opts, "extract_flat": True}) as ydl:
            info = ydl.extract_info(f"ytsearch5:{previous_title}", download=False)
            entries = info.get("entries", []) if info else []
            for entry in entries:
                if entry and entry.get("title") not in already_played:
                    return entry.get("webpage_url") or entry.get("url")
        return None

    next_url = await asyncio.to_thread(_run)
    if not next_url:
        return None
    return await asyncio.to_thread(_download_sync, next_url, False)
