import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import BaseFilter

from config import DOWNLOAD_DIR, TOKEN, WHITELIST
from handlers import download, history, search, settings, start

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


class WhitelistFilter(BaseFilter):
    """Работает и для Message, и для CallbackQuery — у обоих есть from_user."""

    async def __call__(self, event) -> bool:
        if not WHITELIST:
            return True
        return event.from_user.id in WHITELIST


dp.message.filter(WhitelistFilter())
dp.callback_query.filter(WhitelistFilter())

# Порядок важен: специфичные хендлеры (команды, callback'и) регистрируем
# раньше общего "ловца ссылок" в download.py, у которого нет фильтра.
dp.include_router(start.router)
dp.include_router(settings.router)
dp.include_router(history.router)
dp.include_router(search.router)
dp.include_router(download.router)


async def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs("data", exist_ok=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
