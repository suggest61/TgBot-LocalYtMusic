import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

import downloader
from handlers import download

router = Router()


@router.message(Command("search"))
async def cmd_search(message: Message):
    query = message.text.partition(" ")[2].strip()
    if not query:
        await message.answer("Использование: <code>/search название трека</code>")
        return

    wait = await message.answer("🔎 Ищу...")
    try:
        results = downloader.search_tracks(query)
    except Exception as e:
        logging.error(f"Ошибка поиска: {e}")
        await wait.edit_text("❌ Не удалось выполнить поиск.")
        return

    if not results:
        await wait.edit_text("Ничего не нашлось.")
        return

    b = InlineKeyboardBuilder()
    for r in results:
        video_id = r.get("id")
        if not video_id:
            continue
        title = (r.get("title") or "Без названия")[:60]
        b.button(text=title, callback_data=f"dl:{video_id}")
    b.adjust(1)
    await wait.edit_text("Выбери трек:", reply_markup=b.as_markup())


@router.callback_query(F.data.startswith("dl:"))
async def cb_download_result(call: CallbackQuery):
    video_id = call.data.split(":", 1)[1]
    url = f"https://www.youtube.com/watch?v={video_id}"
    await call.answer("Скачиваю...")
    await download.process_urls(call.message, [url], user_id=call.from_user.id)
