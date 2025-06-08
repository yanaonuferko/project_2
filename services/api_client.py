import asyncio
import time
from typing import Optional, Dict, Any, List
import aiohttp
import logging

from .models import Quote, QuoteList

# ZenQuotes API URL
ZENQUOTES_API_URL = "https://zenquotes.io/api"

# Настройка логгера для API клиента
logger = logging.getLogger(__name__)

# Кэш для хранения данных
_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = 30  # Время жизни кэша в секундах


class ZenQuotesAPIError(Exception):
    """Исключение для ошибок ZenQuotes API"""
    pass


def _is_cache_valid(cache_entry: Dict[str, Any]) -> bool:
    """Проверяет валидность записи в кэше"""
    return time.time() - cache_entry["timestamp"] < CACHE_TTL


def _get_from_cache(key: str) -> Optional[Any]:
    """Получает данные из кэша, если они валидны"""
    if key in _cache and _is_cache_valid(_cache[key]):
        logger.info(f"Cache hit for key: {key}")
        return _cache[key]["data"]
    return None


def _save_to_cache(key: str, data: Any) -> None:
    """Сохраняет данные в кэш"""
    _cache[key] = {
        "data": data,
        "timestamp": time.time()
    }
    logger.info(f"Cached data for key: {key}")


async def get_random_quote() -> Optional[Quote]:
    """
    Получает случайную цитату из ZenQuotes API
    
    Returns:
        Quote или None в случае ошибки API
    """
    # Не используем кэш для случайных цитат, чтобы каждый раз получать новую
    url = f"{ZENQUOTES_API_URL}/random"
    logger.info(f"Requesting random quote from: {url}")
    
    try:
        # Настройки таймаута для ZenQuotes
        timeout = aiohttp.ClientTimeout(
            total=30,  # Общий таймаут 30 секунд
            connect=10,  # Таймаут соединения 10 секунд
            sock_read=15  # Таймаут чтения 15 секунд
        )
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            logger.info("Attempting to connect to ZenQuotes API...")
            async with session.get(url) as response:
                logger.info(f"Received response with status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Successfully parsed JSON response: {type(data)}")
                    
                    # ZenQuotes API всегда возвращает массив
                    if isinstance(data, list) and len(data) > 0:
                        quote_data = data[0]
                          # ZenQuotes использует другую структуру:
                        # {"q": "quote text", "a": "author", "h": "html"}
                        quote = Quote(
                            _id=f"zen_{hash(quote_data.get('q', ''))}",  # Генерируем ID на основе хеша текста
                            author=quote_data.get("a", "Unknown"),
                            content=quote_data.get("q", ""),
                            tags=[],  # ZenQuotes не предоставляет теги в базовом API
                            length=len(quote_data.get("q", ""))
                        )
                        logger.info(f"Successfully fetched random quote by {quote.author}")
                        
                        # Не кэшируем случайные цитаты, чтобы каждый раз получать новую
                        return quote
                    else:
                        logger.error(f"Unexpected API response format: {type(data)}")
                        return None
                else:
                    logger.error(f"HTTP error {response.status}: {await response.text()}")
                    return None
                    
    except asyncio.TimeoutError:
        logger.error("Request timeout while fetching random quote")
        return None
    except aiohttp.ClientError as e:
        logger.error(f"Client error while fetching random quote: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while fetching random quote: {e}")
        return None


def clear_cache() -> None:
    """Очищает весь кэш"""
    global _cache
    _cache.clear()
    logger.info("Cache cleared")


def get_cache_stats() -> Dict[str, Any]:
    """Возвращает статистику кэша"""
    valid_entries = sum(1 for entry in _cache.values() if _is_cache_valid(entry))
    return {
        "total_entries": len(_cache),
        "valid_entries": valid_entries,
        "expired_entries": len(_cache) - valid_entries,
        "cache_ttl": CACHE_TTL
    }
