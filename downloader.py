import asyncio
import logging
import os
import re

from yt_dlp import YoutubeDL

from config import DOWNLOAD_DIR, MAX_CONCURRENT_DOWNLOADS, MAX_PLAYLIST_SIZE

URL_RE = re.compile(r"https?://\S+")

# Общий семафор на весь бот — ограничивает число одновременных скачиваний,
# чтобы не перегружать CPU (ffmpeg) и канал сети, даже если несколько
# пользователей одновременно прислали ссылки.
_semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)


def extract_urls(text: str) -> list[str]:
    """Достаёт все http(s)-ссылки из сообщения (по одной на строку или через пробел)."""
    return URL_RE.findall(text)


def _looks_like_playlist(url: str) -> bool:
    return "list=" in url or "/playlist" in url or "/sets/" in url or "/album/" in url


def probe_playlist(url: str) -> dict:
    """Быстрый разбор ссылки без скачивания аудио — для получения списка треков."""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
        "skip_download": True,
    }
    with YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=False)


def expand_to_tracks(url: str) -> list[str]:
    """
    Если ссылка ведёт на плейлист/альбом — возвращает список ссылок на
    отдельные треки (не более MAX_PLAYLIST_SIZE). Иначе возвращает [url].
    """
    if not _looks_like_playlist(url):
        return [url]

    info = probe_playlist(url)
    entries = info.get("entries")
    if not entries:
        return [url]

    urls = []
    for entry in entries:
        if not entry:
            continue
        track_url = entry.get("url") or entry.get("webpage_url")
        if track_url and not track_url.startswith("http"):
            # extract_flat иногда возвращает просто id вместо полной ссылки
            track_url = f"https://www.youtube.com/watch?v={track_url}"
        if track_url:
            urls.append(track_url)
        if len(urls) >= MAX_PLAYLIST_SIZE:
            break

    return urls or [url]


def download_audio(url: str, fmt: str = "mp3", quality: str = "320") -> tuple[str, str]:
    """
    Скачивает аудио, встраивает обложку и метаданные.
    Возвращает (путь_к_файлу, название_трека).
    """
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title).50s.%(ext)s"),
        "noplaylist": True,  # плейлисты уже разворачиваем сами в expand_to_tracks
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": fmt, "preferredquality": quality},
            {"key": "FFmpegThumbnailsConvertor", "format": "jpg", "when": "before_dl"},
            {"key": "FFmpegMetadata", "add_metadata": True},
            {"key": "EmbedThumbnail", "already_have_thumbnail": False},
        ],
        "writethumbnails": True,
        "quiet": True,
        "no_warnings": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        base_name, _ = os.path.splitext(filename)
        title = info.get("title", "audio")
    return f"{base_name}.{fmt}", title


async def download_audio_async(url: str, fmt: str, quality: str) -> tuple[str, str]:
    """Асинхронная обёртка со общим лимитом одновременных загрузок."""
    loop = asyncio.get_event_loop()
    async with _semaphore:
        return await loop.run_in_executor(None, download_audio, url, fmt, quality)


def search_tracks(query: str, limit: int = 5) -> list[dict]:
    """Ищет треки по названию (используется для /search)."""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist",
        "default_search": f"ytsearch{limit}",
    }
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(query, download=False)
    return info.get("entries") or []
