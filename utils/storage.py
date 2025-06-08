"""
Модуль для работы с хранилищем избранных цитат пользователей
"""
import json
import os
from typing import Dict, List, Optional, Any
from utils.logger import logger


# Путь к файлу хранилища
STORAGE_PATH = os.path.join(os.path.dirname(__file__), '..', 'storage', 'quotes.json')


def load_data() -> Dict[str, List[Dict[str, Any]]]:
    """
    Загрузка данных из JSON файла
    
    Returns:
        Dict[str, List[Dict]]: Словарь с избранными цитатами пользователей
    """
    try:
        if os.path.exists(STORAGE_PATH):
            with open(STORAGE_PATH, 'r', encoding='utf-8') as file:
                data = json.load(file)
                logger.info(f"Loaded {len(data)} users' favorites from storage")
                return data
        else:
            logger.info("Storage file doesn't exist, creating empty storage")
            return {}
    except Exception as e:
        logger.error(f"Error loading data from storage: {e}")
        return {}


def save_data(data: Dict[str, List[Dict[str, Any]]]) -> bool:
    """
    Сохранение данных в JSON файл
    
    Args:
        data: Словарь с избранными цитатами пользователей
        
    Returns:
        bool: True если сохранение успешно, False в противном случае
    """
    try:
        # Создаем директорию если она не существует
        os.makedirs(os.path.dirname(STORAGE_PATH), exist_ok=True)
        
        with open(STORAGE_PATH, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(data)} users' favorites to storage")
        return True
    except Exception as e:
        logger.error(f"Error saving data to storage: {e}")
        return False


def add_to_favorites(user_id: int, quote_dict: Dict[str, Any]) -> bool:
    """
    Добавление цитаты в избранное пользователя
    
    Args:
        user_id: ID пользователя
        quote_dict: Словарь с данными цитаты
        
    Returns:
        bool: True если добавление успешно, False если цитата уже существует
    """
    try:
        data = load_data()
        user_id_str = str(user_id)
        
        # Инициализируем список для нового пользователя
        if user_id_str not in data:
            data[user_id_str] = []
        
        # Проверяем, есть ли уже такая цитата
        quote_id = quote_dict.get('_id') or quote_dict.get('id')
        if quote_id:
            for existing_quote in data[user_id_str]:
                if existing_quote.get('_id') == quote_id or existing_quote.get('id') == quote_id:
                    logger.info(f"Quote {quote_id} already exists in favorites for user {user_id}")
                    return False
        
        # Добавляем цитату
        data[user_id_str].append(quote_dict)
        
        # Сохраняем данные
        if save_data(data):
            logger.info(f"Added quote to favorites for user {user_id}")
            return True
        else:
            return False
            
    except Exception as e:
        logger.error(f"Error adding quote to favorites: {e}")
        return False


def remove_from_favorites(user_id: int, quote_id: str) -> bool:
    """
    Удаление цитаты из избранного пользователя
    
    Args:
        user_id: ID пользователя
        quote_id: ID цитаты для удаления
        
    Returns:
        bool: True если удаление успешно, False в противном случае
    """
    try:
        data = load_data()
        user_id_str = str(user_id)
        
        if user_id_str not in data:
            logger.info(f"User {user_id} has no favorites")
            return False
        
        # Находим и удаляем цитату
        initial_count = len(data[user_id_str])
        data[user_id_str] = [
            quote for quote in data[user_id_str] 
            if quote.get('_id') != quote_id and quote.get('id') != quote_id
        ]
        
        if len(data[user_id_str]) < initial_count:
            # Сохраняем данные
            if save_data(data):
                logger.info(f"Removed quote {quote_id} from favorites for user {user_id}")
                return True
            else:
                return False
        else:
            logger.info(f"Quote {quote_id} not found in favorites for user {user_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error removing quote from favorites: {e}")
        return False


def get_user_favorites(user_id: int) -> List[Dict[str, Any]]:
    """
    Получение списка избранных цитат пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        List[Dict]: Список избранных цитат пользователя
    """
    try:
        data = load_data()
        user_id_str = str(user_id)
        
        favorites = data.get(user_id_str, [])
        logger.info(f"Retrieved {len(favorites)} favorites for user {user_id}")
        return favorites
        
    except Exception as e:
        logger.error(f"Error getting user favorites: {e}")
        return []


def get_favorites_count(user_id: int) -> int:
    """
    Получение количества избранных цитат пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        int: Количество избранных цитат
    """
    return len(get_user_favorites(user_id))


def is_quote_in_favorites(user_id: int, quote_id: str) -> bool:
    """
    Проверка, есть ли цитата в избранном пользователя
    
    Args:
        user_id: ID пользователя
        quote_id: ID цитаты
        
    Returns:
        bool: True если цитата в избранном, False в противном случае
    """
    try:
        favorites = get_user_favorites(user_id)
        for quote in favorites:
            if quote.get('_id') == quote_id or quote.get('id') == quote_id:
                return True
        return False
    except Exception as e:
        logger.error(f"Error checking if quote is in favorites: {e}")
        return False


def clear_user_favorites(user_id: int) -> bool:
    """
    Очистка всех избранных цитат пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        bool: True если очистка успешна, False в противном случае
    """
    try:
        data = load_data()
        user_id_str = str(user_id)
        
        if user_id_str in data:
            data[user_id_str] = []
            if save_data(data):
                logger.info(f"Cleared all favorites for user {user_id}")
                return True
        
        return False
    except Exception as e:
        logger.error(f"Error clearing user favorites: {e}")
        return False
