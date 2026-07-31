#!/usr/bin/env python3
"""
Автономный скрипт для скачивания видео целиком (картинка + звук) — локально,
без Telegram-бота. Использует yt-dlp напрямую.

Установка зависимостей:
    pip install yt-dlp
    # ffmpeg должен быть установлен в системе (apt install ffmpeg / brew install ffmpeg)

Примеры использования:
    python video_downloader.py https://youtu.be/XXXXXXXXXXX
    python video_downloader.py URL1 URL2 URL3 -q 1080
    python video_downloader.py "https://youtube.com/playlist?list=XXXX" -o my_videos
    python video_downloader.py URL --no-playlist   # только конкретное видео, не весь плейлист
"""

import argparse
import os
import sys

from yt_dlp import YoutubeDL

QUALITIES = {
    "360": "bestvideo[height<=360]+bestaudio/best[height<=360]",
    "480": "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "720": "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "1080": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "2160": "bestvideo[height<=2160]+bestaudio/best[height<=2160]",
    "best": "bestvideo+bestaudio/best",
}


def progress_hook(d: dict):
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "").strip()
        speed = d.get("_speed_str", "").strip()
        eta = d.get("_eta_str", "").strip()
        sys.stdout.write(f"\r⏳ {percent}  |  скорость: {speed}  |  осталось: {eta}   ")
        sys.stdout.flush()
    elif d["status"] == "finished":
        sys.stdout.write("\n✅ Скачано, объединяю дорожки/добавляю метаданные...\n")


def download(url: str, output_dir: str, quality: str, no_playlist: bool):
    ydl_opts = {
        "format": f"{QUALITIES.get(quality, QUALITIES['best'])}/best",
        "outtmpl": os.path.join(output_dir, "%(title).100s.%(ext)s"),
        "merge_output_format": "mp4",
        "noplaylist": no_playlist,
        "postprocessors": [{"key": "FFmpegMetadata", "add_metadata": True}],
        "progress_hooks": [progress_hook],
        "quiet": True,
        "no_warnings": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def main():
    parser = argparse.ArgumentParser(
        description="Скачивание видео целиком (YouTube и другие сайты, через yt-dlp) — локально, без Telegram."
    )
    parser.add_argument("urls", nargs="+", help="Одна или несколько ссылок на видео/плейлисты")
    parser.add_argument(
        "-q", "--quality",
        choices=list(QUALITIES.keys()),
        default="720",
        help="Максимальное качество видео (по умолчанию 720p)",
    )
    parser.add_argument(
        "-o", "--output",
        default="downloads_video",
        help="Папка для сохранения (по умолчанию ./downloads_video)",
    )
    parser.add_argument(
        "--no-playlist",
        action="store_true",
        help="Скачать только конкретное видео, даже если ссылка ведёт на плейлист",
    )
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    for i, url in enumerate(args.urls, 1):
        print(f"\n[{i}/{len(args.urls)}] {url}")
        try:
            download(url, args.output, args.quality, args.no_playlist)
        except Exception as e:
            print(f"❌ Ошибка при скачивании {url}: {e}")

    print("\nГотово.")


if __name__ == "__main__":
    main()
