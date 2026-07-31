from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import storage

router = Router()


def _history_text(user: dict) -> str:
    history = user.get("history", [])
    if not history:
        return "История пуста — ты пока ничего не скачивал."
    lines = [f"{i + 1}. {h['title']}" for i, h in enumerate(history[:20])]
    return "🕒 <b>Последние треки:</b>\n\n" + "\n".join(lines)


@router.message(Command("history"))
async def cmd_history(message: Message):
    user = storage.get_user(message.from_user.id)
    await message.answer(_history_text(user))


@router.callback_query(F.data == "menu:history")
async def cb_history(call: CallbackQuery):
    user = storage.get_user(call.from_user.id)
    await call.message.edit_text(_history_text(user))
    await call.answer()
