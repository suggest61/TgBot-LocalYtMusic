import logging
import os

from aiogram import Router
from aiogram.types import FSInputFile, Message

import downloader
import storage
from config import MAX_FILE_SIZE_MB

router = Router()


def _plural_links(n: int) -> str:
    return "у" if n == 1 else ("и" if n < 5 else "ок")


async def _build_tracks(urls: list[str]) -> list[str]:
    """Разворачивает ссылки (плейлисты -> список треков) в плоский список."""
    tracks: list[str] = []
    for url in urls:
        try:
            tracks.extend(downloader.expand_to_tracks(url))
        except Exception as e:
            logging.error(f"Не удалось разобрать ссылку {url}: {e}")
    return tracks


async def process_jobs(message: Message, tracks: list[str], user_id: int):
    """
    Качает список треков по очереди, шлёт статус и результаты в чат.
    Используется и основным хендлером ссылок, и /search.

    user_id передаём явно (а не берём из message.from_user), потому что при
    вызове из callback_query message — это сообщение БОТА (с кнопками),
    а не пользователя, и message.from_user там был бы ID бота.
    """
    if not tracks:
        await message.answer("❌ Не удалось распознать ни одной ссылки.")
        return

    user = storage.get_user(user_id)
    fmt, quality = user["format"], user["quality"]

    total = len(tracks)
    status = await message.answer(f"⏳ Скачиваю 1/{total}...")
    done, failed = 0, 0

    for idx, url in enumerate(tracks, 1):
        try:
            await status.edit_text(f"⏳ Скачиваю {idx}/{total}...")
        except Exception:
            pass  # Telegram может ругаться, если текст не изменился — не критично

        try:
            file_path, title = await downloader.download_audio_async(url, fmt, quality)
            size_mb = os.path.getsize(file_path) / (1024 * 1024)

            if size_mb > MAX_FILE_SIZE_MB:
                await message.answer(
                    f"⚠️ «{title}» весит {size_mb:.0f} МБ — это больше лимита Telegram "
                    f"({MAX_FILE_SIZE_MB} МБ), пропускаю."
                )
                os.remove(file_path)
                failed += 1
                continue

            audio = FSInputFile(file_path)
            await message.answer_audio(audio=audio, title=title)
            storage.add_history(user_id, title, url)
            os.remove(file_path)
            done += 1
        except Exception as e:
            logging.error(f"Ошибка при скачивании {url}: {e}")
            failed += 1

    summary = f"✅ Готово: {done}/{total}"
    if failed:
        summary += f" | ❌ Ошибок: {failed}"
    await status.edit_text(summary)


async def process_urls(message: Message, urls: list[str], user_id: int):
    """Публичная точка входа: строит список треков из ссылок и качает их."""
    tracks = await _build_tracks(urls)
    await process_jobs(message, tracks, user_id)


@router.message()
async def handle_message(message: Message):
    """
    Ловит любое сообщение со ссылками: одна ссылка, несколько ссылок
    (каждая с новой строки/через пробел) или ссылка на плейлист.
    """
    if not message.text:
        return

    urls = downloader.extract_urls(message.text)
    if not urls:
        return  # не похоже на ссылку — ничего не делаем

    await message.answer(
        f"🔎 Проверяю {len(urls)} ссылк{_plural_links(len(urls))}..."
    )
    await process_urls(message, urls, user_id=message.from_user.id)
