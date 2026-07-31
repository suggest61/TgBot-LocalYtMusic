from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import storage
from config import FORMATS, QUALITIES
from keyboards import settings_menu

router = Router()


def _settings_text(user: dict) -> str:
    fmt = FORMATS[user["format"]]["label"]
    qual = QUALITIES[user["quality"]]
    return f"⚙️ <b>Настройки</b>\n\nФормат: {fmt}\nКачество: {qual}"


@router.message(Command("settings"))
async def cmd_settings(message: Message):
    user = storage.get_user(message.from_user.id)
    await message.answer(_settings_text(user), reply_markup=settings_menu(user["format"], user["quality"]))


@router.callback_query(F.data == "menu:settings")
async def cb_settings(call: CallbackQuery):
    user = storage.get_user(call.from_user.id)
    await call.message.edit_text(_settings_text(user), reply_markup=settings_menu(user["format"], user["quality"]))
    await call.answer()


@router.callback_query(F.data.startswith("fmt:"))
async def cb_set_format(call: CallbackQuery):
    fmt = call.data.split(":", 1)[1]
    storage.set_user_setting(call.from_user.id, "format", fmt)
    user = storage.get_user(call.from_user.id)
    await call.message.edit_text(_settings_text(user), reply_markup=settings_menu(user["format"], user["quality"]))
    await call.answer("Формат обновлён")


@router.callback_query(F.data.startswith("qual:"))
async def cb_set_quality(call: CallbackQuery):
    qual = call.data.split(":", 1)[1]
    storage.set_user_setting(call.from_user.id, "quality", qual)
    user = storage.get_user(call.from_user.id)
    await call.message.edit_text(_settings_text(user), reply_markup=settings_menu(user["format"], user["quality"]))
    await call.answer("Качество обновлено")
