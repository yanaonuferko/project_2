"""
Клавиатуры для административных команд
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.localization import get_text


def get_admin_main_keyboard(user_id: int = 0) -> InlineKeyboardMarkup:
    """
    Создание главной клавиатуры админ-панели
    
    Args:
        user_id: ID пользователя для локализации
        
    Returns:
        InlineKeyboardMarkup: Главная админ-клавиатура
    """
    buttons = [
        [
            InlineKeyboardButton(
                text="📊 Статистика",
                callback_data="admin_stats"
            ),
            InlineKeyboardButton(
                text="👥 Пользователи",
                callback_data="admin_users"
            )
        ],
        [
            InlineKeyboardButton(
                text="📢 Рассылка",
                callback_data="admin_broadcast"
            ),
            InlineKeyboardButton(
                text="🚫 Управление банами",
                callback_data="admin_bans"
            )
        ],
        [
            InlineKeyboardButton(
                text="🗑️ Очистить кэш",
                callback_data="admin_clear_cache"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_broadcast_confirmation_keyboard(user_id: int = 0) -> InlineKeyboardMarkup:
    """
    Клавиатура подтверждения рассылки
    
    Args:
        user_id: ID пользователя для локализации
        
    Returns:
        InlineKeyboardMarkup: Клавиатура подтверждения рассылки
    """
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Отправить рассылку",
                callback_data="confirm_broadcast"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Отменить",
                callback_data="cancel_broadcast"
            )
        ],
        [
            InlineKeyboardButton(
                text="✏️ Изменить текст",
                callback_data="edit_broadcast"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_ban_management_keyboard(user_id: int = 0) -> InlineKeyboardMarkup:
    """
    Клавиатура управления банами
    
    Args:
        user_id: ID пользователя для локализации
        
    Returns:
        InlineKeyboardMarkup: Клавиатура управления банами
    """
    buttons = [
        [
            InlineKeyboardButton(
                text="🚫 Заблокировать пользователя",
                callback_data="admin_ban_user"
            )
        ],
        [
            InlineKeyboardButton(
                text="✅ Разблокировать пользователя",
                callback_data="admin_unban_user"
            )
        ],
        [
            InlineKeyboardButton(
                text="📋 Список заблокированных",
                callback_data="admin_banned_list"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="admin_main"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_ban_confirmation_keyboard(user_id: int, target_user_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура подтверждения блокировки пользователя
    
    Args:
        user_id: ID администратора
        target_user_id: ID пользователя для блокировки
        
    Returns:
        InlineKeyboardMarkup: Клавиатура подтверждения блокировки
    """
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Подтвердить блокировку",
                callback_data=f"confirm_ban_{target_user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Отменить",
                callback_data="cancel_ban"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_unban_confirmation_keyboard(user_id: int, target_user_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура подтверждения разблокировки пользователя
    
    Args:
        user_id: ID администратора
        target_user_id: ID пользователя для разблокировки
        
    Returns:
        InlineKeyboardMarkup: Клавиатура подтверждения разблокировки
    """
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Подтвердить разблокировку",
                callback_data=f"confirm_unban_{target_user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Отменить",
                callback_data="cancel_unban"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_to_admin_keyboard(user_id: int = 0) -> InlineKeyboardMarkup:
    """
    Клавиатура возврата в админ-панель
    
    Args:
        user_id: ID пользователя для локализации
        
    Returns:
        InlineKeyboardMarkup: Клавиатура возврата
    """
    buttons = [
        [
            InlineKeyboardButton(
                text="⬅️ Назад в админ-панель",
                callback_data="admin_main"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
