"""
Управление пользователями и системой банов
"""
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Set, Optional

logger = logging.getLogger(__name__)

# Пути к файлам
USERS_FILE = "storage/users.json"
BANNED_FILE = "storage/banned.json"


def ensure_storage_dir():
    """Создает директорию storage если её нет"""
    os.makedirs("storage", exist_ok=True)


def load_users() -> Dict[str, dict]:
    """
    Загружает данные о пользователях из users.json
    
    Returns:
        Dict[str, dict]: Словарь с данными пользователей
    """
    ensure_storage_dir()
    
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} users from storage")
                return data
        else:
            logger.info("Users file not found, creating empty database")
            return {}
    except Exception as e:
        logger.error(f"Error loading users: {e}")
        return {}


def save_users(users_data: Dict[str, dict]):
    """
    Сохраняет данные о пользователях в users.json
    
    Args:
        users_data: Словарь с данными пользователей
    """
    ensure_storage_dir()
    
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(users_data)} users to storage")
    except Exception as e:
        logger.error(f"Error saving users: {e}")


def register_user(user_id: int, username: str = None, first_name: str = None, last_name: str = None):
    """
    Регистрирует нового пользователя или обновляет существующего
    
    Args:
        user_id: ID пользователя
        username: Имя пользователя
        first_name: Имя
        last_name: Фамилия
    """
    users = load_users()
    user_id_str = str(user_id)
    
    current_time = datetime.now().isoformat()
    
    # Если пользователь новый
    if user_id_str not in users:
        users[user_id_str] = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "first_seen": current_time,
            "last_seen": current_time,
            "message_count": 1,
            "is_active": True
        }
        logger.info(f"Registered new user: {user_id} (@{username})")
    else:
        # Обновляем данные существующего пользователя
        users[user_id_str].update({
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "last_seen": current_time,
            "message_count": users[user_id_str].get("message_count", 0) + 1,
            "is_active": True
        })
    
    save_users(users)


def get_user_stats() -> Dict[str, int]:
    """
    Получает статистику пользователей
    
    Returns:
        Dict[str, int]: Статистика пользователей
    """
    users = load_users()
    
    total_users = len(users)
    active_users = sum(1 for user in users.values() if user.get("is_active", True))
    
    # Подсчитываем пользователей за последний месяц
    from datetime import datetime, timedelta
    one_month_ago = datetime.now() - timedelta(days=30)
    
    recent_users = 0
    for user in users.values():
        try:
            last_seen = datetime.fromisoformat(user.get("last_seen", ""))
            if last_seen > one_month_ago:
                recent_users += 1
        except:
            continue
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "recent_users": recent_users
    }


def get_all_user_ids() -> List[int]:
    """
    Получает список всех ID пользователей
    
    Returns:
        List[int]: Список ID пользователей
    """
    users = load_users()
    return [int(user_id) for user_id in users.keys()]


def load_banned_users() -> Set[int]:
    """
    Загружает список заблокированных пользователей
    
    Returns:
        Set[int]: Множество ID заблокированных пользователей
    """
    ensure_storage_dir()
    
    try:
        if os.path.exists(BANNED_FILE):
            with open(BANNED_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                banned_ids = set(data.get("banned_users", []))
                logger.info(f"Loaded {len(banned_ids)} banned users from storage")
                return banned_ids
        else:
            logger.info("Banned users file not found, creating empty set")
            return set()
    except Exception as e:
        logger.error(f"Error loading banned users: {e}")
        return set()


def save_banned_users(banned_users: Set[int]):
    """
    Сохраняет список заблокированных пользователей
    
    Args:
        banned_users: Множество ID заблокированных пользователей
    """
    ensure_storage_dir()
    
    try:
        data = {
            "banned_users": list(banned_users),
            "last_updated": datetime.now().isoformat()
        }
        
        with open(BANNED_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(banned_users)} banned users to storage")
    except Exception as e:
        logger.error(f"Error saving banned users: {e}")


def ban_user(user_id: int) -> bool:
    """
    Блокирует пользователя
    
    Args:
        user_id: ID пользователя для блокировки
        
    Returns:
        bool: True если пользователь заблокирован, False если уже был заблокирован
    """
    banned_users = load_banned_users()
    
    if user_id in banned_users:
        return False  # Уже заблокирован
    
    banned_users.add(user_id)
    save_banned_users(banned_users)
    
    logger.info(f"User {user_id} has been banned")
    return True


def unban_user(user_id: int) -> bool:
    """
    Разблокирует пользователя
    
    Args:
        user_id: ID пользователя для разблокировки
        
    Returns:
        bool: True если пользователь разблокирован, False если не был заблокирован
    """
    banned_users = load_banned_users()
    
    if user_id not in banned_users:
        return False  # Не был заблокирован
    
    banned_users.remove(user_id)
    save_banned_users(banned_users)
    
    logger.info(f"User {user_id} has been unbanned")
    return True


def is_user_banned(user_id: int) -> bool:
    """
    Проверяет, заблокирован ли пользователь
    
    Args:
        user_id: ID пользователя
        
    Returns:
        bool: True если заблокирован
    """
    banned_users = load_banned_users()
    return user_id in banned_users


def get_banned_users_list() -> List[int]:
    """
    Получает список заблокированных пользователей
    
    Returns:
        List[int]: Список ID заблокированных пользователей
    """
    banned_users = load_banned_users()
    return list(banned_users)


def get_user_info(user_id: int) -> Optional[dict]:
    """
    Получает информацию о пользователе
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Optional[dict]: Информация о пользователе или None если не найден
    """
    users = load_users()
    return users.get(str(user_id))
