import logging
import sys

# Настройка логирования с поддержкой UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def log_command_usage(user_id: int, command: str):
    """Логирование использования команд"""
    logger.info(f"User {user_id} used /{command}")


def log_api_request(endpoint: str, status: str = "started"):
    """Логирование API запросов"""
    logger.info(f"API request to {endpoint} - {status}")


def log_api_success(endpoint: str, data_type: str, count: int = 1):
    """Логирование успешных API ответов"""
    logger.info(f"API success: {endpoint} returned {count} {data_type}")


def log_api_error(endpoint: str, error: str):
    """Логирование ошибок API"""
    logger.error(f"API error: {endpoint} - {error}")


def log_cache_hit(cache_key: str):
    """Логирование попадания в кэш"""
    logger.info(f"Cache hit: {cache_key}")


def log_cache_miss(cache_key: str):
    """Логирование промаха кэша"""
    logger.info(f"Cache miss: {cache_key}")
