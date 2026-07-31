import os

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не задана!")

# Пример строки: "123456789,987654321"
WHITELIST_RAW = os.getenv("WHITELIST", "")
WHITELIST = [int(x.strip()) for x in WHITELIST_RAW.split(",") if x.strip().isdigit()]

DOWNLOAD_DIR = "downloads"
DATA_FILE = "data/users.json"

# Сколько загрузок может выполняться параллельно (защита от перегрузки CPU/сети)
MAX_CONCURRENT_DOWNLOADS = int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "2"))

# Максимальное число треков, которые скачиваются из одного плейлиста за раз
MAX_PLAYLIST_SIZE = int(os.getenv("MAX_PLAYLIST_SIZE", "50"))

# Лимит Telegram Bot API на размер файла при отправке через обычный (не self-hosted) сервер
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "49"))

FORMATS = {
    "mp3": {"label": "MP3", },
    "opus": {"label": "Opus (легче)"},
    "flac": {"label": "FLAC (без потерь)"},
}

QUALITIES = {
    "128": "128 kbps",
    "192": "192 kbps",
    "320": "320 kbps",
}

DEFAULT_FORMAT = "mp3"
DEFAULT_QUALITY = "320"
