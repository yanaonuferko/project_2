import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройки бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настройки API
QUOTABLE_API_URL = "https://api.quotable.io"

# Настройки логирования
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "bot.log")

# Настройки администраторов
ADMIN_IDS = os.getenv("ADMIN_IDS", "")  # Список ID админов через запятую

# Настройки middleware
RATE_LIMIT = float(os.getenv("RATE_LIMIT", "1.0"))  # Ограничение частоты запросов (сек)
