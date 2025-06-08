"""
Inline клавиатуры для бота
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any, Optional
from utils.storage import is_quote_in_favorites
from utils.localization import get_text, get_supported_languages


def get_language_keyboard() -> InlineKeyboardMarkup:
    """
    Создание клавиатуры для выбора языка
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с языками
    """
    buttons = []
    
    # Получаем поддерживаемые языки
    languages = get_supported_languages()
    
    for lang_code, lang_name in languages.items():
        buttons.append([
            InlineKeyboardButton(
                text=lang_name,
                callback_data=f"set_language_{lang_code}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_quote_keyboard(quote_id: str, user_id: int, show_remove: bool = False) -> InlineKeyboardMarkup:
    """
    Создание клавиатуры для цитаты с кнопками избранного
    
    Args:
        quote_id: ID цитаты
        user_id: ID пользователя  
        show_remove: Показать кнопку удаления вместо добавления
        
    Returns:
        InlineKeyboardMarkup: Клавиатура для цитаты
    """
    buttons = []
    
    # Проверяем, есть ли цитата в избранном
    is_favorite = is_quote_in_favorites(user_id, quote_id)
    
    # Кнопка избранного
    if is_favorite or show_remove:
        if show_remove:
            remove_text = get_text(user_id, "keyboard.remove_from_favorites")
            buttons.append([
                InlineKeyboardButton(
                    text=remove_text,
                    callback_data=f"remove_favorite_{quote_id}"
                )
            ])
        else:
            already_text = get_text(user_id, "keyboard.already_in_favorites")
            buttons.append([
                InlineKeyboardButton(
                    text=already_text,
                    callback_data=f"already_favorite_{quote_id}"
                )
            ])
    else:
        add_text = get_text(user_id, "keyboard.add_to_favorites")
        buttons.append([
            InlineKeyboardButton(
                text=add_text,
                callback_data=f"add_favorite_{quote_id}"
            )
        ])
    
    # Кнопка "Еще цитата"
    another_text = get_text(user_id, "keyboard.another_quote")
    buttons.append([
        InlineKeyboardButton(
            text=another_text,
            callback_data="get_another_quote"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_favorites_navigation_keyboard(
    current_page: int = 0,
    total_pages: int = 1,
    quotes_on_page: Optional[List[Dict[str, Any]]] = None,
    user_id: int = 0
) -> InlineKeyboardMarkup:
    """
    Создание клавиатуры для навигации по избранным цитатам
    
    Args:
        current_page: Текущая страница (начиная с 0)
        total_pages: Общее количество страниц
        quotes_on_page: Цитаты на текущей странице
        user_id: ID пользователя для локализации
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками навигации
    """
    buttons = []
    
    # Кнопки удаления цитат (если есть цитаты на странице)
    if quotes_on_page:
        remove_text = get_text(user_id, "keyboard.remove_quote")
        for i, quote in enumerate(quotes_on_page):
            quote_id = quote.get('_id') or quote.get('id', '')
            if quote_id:
                buttons.append([
                    InlineKeyboardButton(
                        text=f"{remove_text} {i + 1}",
                        callback_data=f"remove_favorite_{quote_id}"
                    )
                ])
    
    # Кнопки навигации
    nav_buttons = []
    
    if current_page > 0:
        prev_text = get_text(user_id, "keyboard.previous_page")
        nav_buttons.append(
            InlineKeyboardButton(
                text=prev_text,
                callback_data=f"favorites_page_{current_page - 1}"
            )
        )
    
    if current_page < total_pages - 1:
        next_text = get_text(user_id, "keyboard.next_page")
        nav_buttons.append(
            InlineKeyboardButton(
                text=next_text,
                callback_data=f"favorites_page_{current_page + 1}"
            )
        )
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    # Кнопка очистки всех избранных
    if quotes_on_page:
        clear_text = get_text(user_id, "keyboard.clear_all")
        buttons.append([
            InlineKeyboardButton(
                text=clear_text,
                callback_data="clear_all_favorites"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirmation_keyboard(action: str, quote_id: str = "", user_id: int = 0) -> InlineKeyboardMarkup:
    """
    Создание клавиатуры подтверждения действия
    
    Args:
        action: Действие для подтверждения
        quote_id: ID цитаты (если необходимо)
        user_id: ID пользователя для локализации
        
    Returns:
        InlineKeyboardMarkup: Клавиатура подтверждения
    """
    confirm_text = get_text(user_id, "keyboard.confirm")
    cancel_text = get_text(user_id, "keyboard.cancel")
    
    buttons = [
        [
            InlineKeyboardButton(
                text=confirm_text,
                callback_data=f"confirm_{action}_{quote_id}" if quote_id else f"confirm_{action}"
            ),
            InlineKeyboardButton(
                text=cancel_text,
                callback_data="cancel_action"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_delete_confirmation_keyboard(quote_id: str, user_id: int = 0) -> InlineKeyboardMarkup:
    """
    Создание клавиатуры для подтверждения удаления цитаты из избранного
    
    Args:
        quote_id: ID цитаты для удаления
        user_id: ID пользователя для локализации
        
    Returns:
        InlineKeyboardMarkup: Клавиатура подтверждения удаления
    """
    confirm_text = get_text(user_id, "keyboard.confirm")
    cancel_text = get_text(user_id, "keyboard.cancel")
    
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{confirm_text}",
                callback_data=f"confirm_delete_{quote_id}"
            ),
            InlineKeyboardButton(
                text=f"{cancel_text}",
                callback_data="cancel_delete"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_clear_all_confirmation_keyboard(user_id: int = 0) -> InlineKeyboardMarkup:
    """
    Создание клавиатуры для подтверждения очистки всех избранных цитат
    
    Args:
        user_id: ID пользователя для локализации
        
    Returns:
        InlineKeyboardMarkup: Клавиатура подтверждения очистки
    """
    confirm_text = get_text(user_id, "keyboard.confirm")
    cancel_text = get_text(user_id, "keyboard.cancel")
    
    buttons = [
        [
            InlineKeyboardButton(
                text=f"🗑️ {confirm_text}",
                callback_data="confirm_clear_all"
            ),
            InlineKeyboardButton(
                text=f"❌ {cancel_text}",
                callback_data="cancel_clear_all"
            )
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)



