import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import BaseFilter, CommandStart
from aiogram.types import FSInputFile
from yt_dlp import YoutubeDL

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Безопасное получение токена из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не задана!")

# Белый список ID пользователей Telegram (загружается из переменной окружения)
# Пример строки: "123456789,987654321"
WHITELIST_RAW = os.getenv("WHITELIST", "")
WHITELIST = [int(x.strip()) for x in WHITELIST_RAW.split(",") if x.strip().isdigit()]

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Фильтр для проверки пользователя в белом списке
class WhitelistFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        # Если белый список пуст, бот доступен всем
        if not WHITELIST:
            return True
        return message.from_user.id in WHITELIST

# Применяем фильтр глобально на все сообщения диспетчера
dp.message.filter(WhitelistFilter())

def download_youtube_audio(url: str) -> str:
    """
    Скачивает аудио, встраивает обложку и метаданные, 
    возвращает путь к MP3-файлу с оригинальным названием.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'trim_file_name': 50,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            },
            {
                'key': 'FFmpegThumbnailsConvertor',
                'format': 'jpg',
                'when': 'before_dl',
            },
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            },
            {
                'key': 'EmbedThumbnail',
                'already_have_thumbnail': False,
            },
        ],
        'writethumbnails': True,
        'quiet': True,
        'no_warnings': True,
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        base_name, _ = os.path.splitext(filename)
        return f"{base_name}.mp3"

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Привет! Отправь мне ссылку на видео (YouTube и др.), и я пришлю тебе MP3-файл.")

@dp.message(F.text.startswith("http://") | F.text.startswith("https://"))
async def handle_link(message: types.Message):
    url = message.text.strip()
    status_msg = await message.answer("⏳ Скачиваю, добавляю обложку и конвертирую...")

    try:
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(None, download_youtube_audio, url)

        audio_file = FSInputFile(file_path)
        await message.answer_audio(audio=audio_file)
        await status_msg.delete()

        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        logging.error(f"Ошибка при обработке ссылки: {e}")
        await status_msg.edit_text("❌ Произошла ошибка при обработке файла. Проверьте ссылку.")

async def main():
    os.makedirs("downloads", exist_ok=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
