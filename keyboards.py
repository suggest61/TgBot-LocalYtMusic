from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import FORMATS, QUALITIES


def main_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="⚙️ Настройки", callback_data="menu:settings")
    b.button(text="🕒 История", callback_data="menu:history")
    b.button(text="ℹ️ Помощь", callback_data="menu:help")
    b.adjust(2, 1)
    return b.as_markup()


def settings_menu(current_format: str, current_quality: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for key, meta in FORMATS.items():
        prefix = "✅ " if key == current_format else ""
        b.button(text=f"{prefix}{meta['label']}", callback_data=f"fmt:{key}")
    for key, label in QUALITIES.items():
        prefix = "✅ " if key == current_quality else ""
        b.button(text=f"{prefix}{label}", callback_data=f"qual:{key}")
    b.button(text="⬅️ Назад", callback_data="menu:main")
    b.adjust(len(FORMATS), len(QUALITIES), 1)
    return b.as_markup()


def back_to_main() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="⬅️ Назад", callback_data="menu:main")
    return b.as_markup()
