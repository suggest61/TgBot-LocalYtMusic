from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from keyboards import back_to_main, main_menu

router = Router()

WELCOME = (
    "👋 Привет! Я скачиваю музыку из YouTube и других сайтов.\n\n"
    "Пришли ссылку — и получишь MP3. Можно прислать сразу несколько ссылок "
    "(каждую с новой строки), а ссылку на плейлист я разверну в отдельные треки.\n\n"
    "Ещё умею искать треки по названию: /search название"
)

HELP = (
    "📖 <b>Как пользоваться</b>\n\n"
    "• Одна ссылка — получишь один трек\n"
    "• Несколько ссылок в одном сообщении (с новой строки) — скачаю все по очереди\n"
    "• Ссылка на плейлист/альбом — скачаю все треки из него\n"
    "• /search название — найти трек, если нет ссылки\n"
    "• /settings — выбрать формат и качество аудио\n"
    "• /history — последние скачанные треки"
)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(WELCOME, reply_markup=main_menu())


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(HELP, reply_markup=back_to_main())


@router.callback_query(F.data == "menu:main")
async def cb_main(call: CallbackQuery):
    await call.message.edit_text(WELCOME, reply_markup=main_menu())
    await call.answer()


@router.callback_query(F.data == "menu:help")
async def cb_help(call: CallbackQuery):
    await call.message.edit_text(HELP, reply_markup=back_to_main())
    await call.answer()
