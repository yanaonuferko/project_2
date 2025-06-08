"""
Middleware для управления пользователями и проверки банов
"""
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from utils.user_management import register_user, is_user_banned

logger = logging.getLogger(__name__)


class UserManagementMiddleware(BaseMiddleware):
    """
    Middleware для регистрации пользователей и проверки банов
    """
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Обрабатывает входящие события
        
        Args:
            handler: Обработчик события
            event: Событие (Message, CallbackQuery и т.д.)
            data: Данные события
            
        Returns:
            Any: Результат обработки
        """
        user = None
        
        # Получаем пользователя из разных типов событий
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user
        
        if user:
            user_id = user.id
            
            # Проверяем, заблокирован ли пользователь
            if is_user_banned(user_id):
                logger.warning(f"Blocked message from banned user {user_id}")
                
                # Если это сообщение, отправляем уведомление о бане
                if isinstance(event, Message):
                    try:
                        await event.answer(
                            "🚫 Вы заблокированы и не можете использовать этого бота.\n"
                            "Если считаете это ошибкой, обратитесь к администратору."
                        )
                    except Exception as e:
                        logger.error(f"Error sending ban message to user {user_id}: {e}")
                
                return  # Прерываем обработку для заблокированного пользователя
            
            # Регистрируем/обновляем пользователя
            try:
                register_user(
                    user_id=user_id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
            except Exception as e:
                logger.error(f"Error registering user {user_id}: {e}")
        
        # Продолжаем обработку
        return await handler(event, data)
