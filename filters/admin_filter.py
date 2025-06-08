"""
Фильтры для проверки административных прав
"""
import logging
from typing import List, Union, Optional
from aiogram import types
from aiogram.filters import Filter
from config import settings

logger = logging.getLogger(__name__)


class AdminFilter(Filter):
    """
    Фильтр для проверки, является ли пользователь администратором
    """
    
    def __init__(self, admin_ids: Optional[List[int]] = None):
        """
        Args:
            admin_ids: Список ID администраторов. 
                      Если не указан, берется из настроек
        """
        self.admin_ids = admin_ids or self._get_admin_ids_from_config()
        logger.info(f"AdminFilter initialized with {len(self.admin_ids)} admin(s)")
    
    def _get_admin_ids_from_config(self) -> List[int]:
        """
        Получение списка ID администраторов из конфигурации
        
        Returns:
            List[int]: Список ID администраторов
        """
        try:
            # Получаем список администраторов из настроек
            admin_ids_str = getattr(settings, 'ADMIN_IDS', '')
            
            if not admin_ids_str:
                logger.warning("No admin IDs configured in settings")
                return []
            
            # Парсим строку с ID (разделенными запятыми)
            admin_ids = []
            for admin_id in admin_ids_str.split(','):
                try:
                    admin_ids.append(int(admin_id.strip()))
                except ValueError:
                    logger.warning(f"Invalid admin ID format: {admin_id}")
            
            return admin_ids
        
        except Exception as e:
            logger.error(f"Error getting admin IDs from config: {e}")
            return []
    
    async def __call__(self, message: Union[types.Message, types.CallbackQuery]) -> bool:
        """
        Проверка, является ли пользователь администратором
        
        Args:
            message: Сообщение или callback query
            
        Returns:
            bool: True если пользователь администратор, False в противном случае
        """
        try:
            # Получаем пользователя
            user = None
            if isinstance(message, types.Message):
                user = message.from_user
            elif isinstance(message, types.CallbackQuery):
                user = message.from_user
            
            if not user:
                return False
            
            # Проверяем, есть ли пользователь в списке админов
            is_admin = user.id in self.admin_ids
            
            if is_admin:
                logger.info(f"Admin access granted for user {user.id}")
            else:
                logger.debug(f"Admin access denied for user {user.id}")
            
            return is_admin
        
        except Exception as e:
            logger.error(f"Error in AdminFilter: {e}")
            return False