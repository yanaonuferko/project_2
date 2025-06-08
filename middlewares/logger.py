"""
Middleware для логирования входящих сообщений
"""
import logging
import re
from typing import Dict, Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

logger = logging.getLogger(__name__)


def sanitize_for_logging(text: str) -> str:
    """
    Санитизация текста для безопасного логирования
    Удаляет или заменяет символы, которые могут вызвать проблемы с кодировкой
    """
    if not text:
        return text
    
    # Заменяем эмоджи и другие Unicode символы на безопасные альтернативы
    # Удаляем символы, которые могут вызывать проблемы с кодировкой
    sanitized = re.sub(r'[^\x00-\x7F]+', '[EMOJI]', text)
    return sanitized


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware для логирования всех входящих сообщений и callback запросов
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Обработка входящих событий с логированием
        
        Args:
            handler: Следующий обработчик в цепочке
            event: Telegram событие (Message, CallbackQuery, etc.)
            data: Данные контекста
            
        Returns:
            Результат выполнения обработчика
        """
        try:
            # Логирование сообщений
            if isinstance(event, Message):
                await self._log_message(event)
            
            # Логирование callback запросов
            elif isinstance(event, CallbackQuery):
                await self._log_callback(event)
            
            # Выполнение следующего обработчика
            return await handler(event, data)
        
        except Exception as e:
            logger.error(f"Error in LoggingMiddleware: {e}")
            # Продолжаем выполнение несмотря на ошибку в middleware
            return await handler(event, data)
    
    async def _log_message(self, message: Message) -> None:
        """
        Логирование входящего сообщения
        
        Args:
            message: Объект сообщения
        """
        try:
            user = message.from_user
            chat = message.chat
            
            user_info = (
                f"User: {user.id}"
                f"{'@' + user.username if user.username else ''}"
                f" ({user.first_name}"
                f"{' ' + user.last_name if user.last_name else ''})"
            ) if user else "Unknown user"
            
            chat_info = f"Chat: {chat.id} ({chat.type})"
            message_text = message.text or message.caption or "<no text>"
            # Обрезаем длинные сообщения для логов
            if len(message_text) > 100:
                message_text = message_text[:97] + "..."
            
            # Санитизируем текст для безопасного логирования
            safe_message_text = sanitize_for_logging(message_text)
            safe_user_info = sanitize_for_logging(user_info)
            safe_chat_info = sanitize_for_logging(chat_info)
            
            logger.info(
                f"[MSG] Message received | {safe_user_info} | {safe_chat_info} | "
                f"Text: '{safe_message_text}'"
            )
            
        except Exception as e:
            logger.error(f"Error logging message: {e}")
    
    async def _log_callback(self, callback: CallbackQuery) -> None:
        """
        Логирование входящего callback запроса
        
        Args:
            callback: Объект callback запроса
        """
        try:
            user = callback.from_user
            user_info = (
                f"User: {user.id}"
                f"{'@' + user.username if user.username else ''}"
                f" ({user.first_name}"
                f"{' ' + user.last_name if user.last_name else ''})"
            ) if user else "Unknown user"
            
            callback_data = callback.data or "<no data>"
            
            # Санитизируем текст для безопасного логирования
            safe_user_info = sanitize_for_logging(user_info)
            safe_callback_data = sanitize_for_logging(callback_data)
            
            logger.info(
                f"[CALLBACK] Callback received | {safe_user_info} | "
                f"Data: '{safe_callback_data}'"
            )
            
        except Exception as e:
            logger.error(f"Error logging callback: {e}")


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware для ограничения частоты запросов (антиспам)
    """
    
    def __init__(self, rate_limit: float = 1.0):
        """
        Args:
            rate_limit: Минимальный интервал между сообщениями в секундах
        """
        self.rate_limit = rate_limit
        self.user_timestamps = {}
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Проверка частоты запросов пользователя
        """
        import time
        
        try:
            current_time = time.time()
            
            # Получаем ID пользователя
            user_id = None
            if isinstance(event, Message) and event.from_user:
                user_id = event.from_user.id
            elif isinstance(event, CallbackQuery) and event.from_user:
                user_id = event.from_user.id
            
            if user_id:
                # Проверяем последнее время запроса пользователя
                last_time = self.user_timestamps.get(user_id, 0)
                
                if current_time - last_time < self.rate_limit:
                    # Слишком частые запросы
                    logger.warning(f"Rate limit exceeded for user {user_id}")
                    
                    # Отправляем предупреждение (только для сообщений)
                    if isinstance(event, Message):
                        await event.answer(
                            "⚠️ Пожалуйста, не отправляйте сообщения слишком часто."
                        )
                    
                    return  # Прерываем обработку
                
                # Обновляем время последнего запроса
                self.user_timestamps[user_id] = current_time
            
            # Выполняем следующий обработчик
            return await handler(event, data)
        
        except Exception as e:
            logger.error(f"Error in ThrottlingMiddleware: {e}")
            return await handler(event, data)
