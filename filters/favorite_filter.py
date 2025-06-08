"""
Фильтры для работы с избранными цитатами
"""
from typing import Dict, Any
from aiogram import types
from aiogram.filters import Filter
from utils.storage import is_quote_in_favorites


class FavoriteFilter(Filter):
    """
    Фильтр для проверки, есть ли цитата в избранном пользователя
    """
    
    def __init__(self, is_favorite: bool = True):
        """
        Args:
            is_favorite: True для проверки наличия в избранном,
                        False для проверки отсутствия в избранном
        """
        self.is_favorite = is_favorite
    
    async def __call__(self, callback: types.CallbackQuery) -> bool:
        """
        Проверка callback данных на наличие цитаты в избранном
        
        Args:
            callback: Callback query от пользователя
            
        Returns:
            bool: True если условие выполнено, False в противном случае
        """
        try:
            if not callback.data or not callback.data.startswith('add_favorite_'):
                return False
            
            # Извлекаем ID цитаты из callback данных
            quote_id = callback.data.replace('add_favorite_', '')
            user_id = callback.from_user.id
            
            # Проверяем, есть ли цитата в избранном
            in_favorites = is_quote_in_favorites(user_id, quote_id)
            
            # Возвращаем результат в соответствии с настройкой фильтра
            return in_favorites == self.is_favorite
            
        except Exception:
            # В случае ошибки возвращаем False
            return False


class RemoveFavoriteFilter(Filter):
    """
    Фильтр для обработки удаления цитат из избранного
    """
    
    async def __call__(self, callback: types.CallbackQuery) -> bool:
        """
        Проверка callback данных на команду удаления из избранного
        
        Args:
            callback: Callback query от пользователя
            
        Returns:
            bool: True если это команда удаления из избранного
        """
        try:
            return bool(callback.data and 
                        callback.data.startswith('remove_favorite_'))
        except Exception:
            return False


def extract_quote_id_from_callback(callback_data: str, prefix: str) -> str:
    """
    Извлечение ID цитаты из callback данных
    
    Args:
        callback_data: Данные callback query
        prefix: Префикс для удаления
        
    Returns:
        str: ID цитаты
    """
    if callback_data and callback_data.startswith(prefix):
        return callback_data.replace(prefix, '')
    return ''
