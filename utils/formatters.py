"""
Форматтеры для текстовых сообщений бота
"""
import math
from typing import Dict, Any, List, Optional
from services.models import Quote
from utils.localization import get_text


def format_quote_message(quote: Quote, show_tags: bool = True, user_id: int = 0) -> str:
    """
    Форматирование цитаты для отправки в сообщении
    
    Args:
        quote: Объект цитаты
        show_tags: Показывать ли теги
        user_id: ID пользователя для локализации
        
    Returns:
        str: Отформатированное сообщение с цитатой
    """
    message = f'💭 "{quote.content}"\n\n— {quote.author}'
    
    if show_tags and quote.tags:
        tags_label = get_text(user_id, "formatters.tags_label")
        message += f'\n\n{tags_label} {", ".join(quote.tags)}'
    
    return message


def format_quote_dict_message(quote_dict: Dict[str, Any], index: Optional[int] = None, user_id: int = 0) -> str:
    """
    Форматирование цитаты из словаря для отправки в сообщении
    
    Args:
        quote_dict: Словарь с данными цитаты
        index: Номер цитаты (для нумерации)
        user_id: ID пользователя для локализации
        
    Returns:
        str: Отформатированное сообщение с цитатой
    """
    content = quote_dict.get('content', get_text(user_id, "formatters.no_content"))
    author = quote_dict.get('author', get_text(user_id, "formatters.unknown_author"))
    tags = quote_dict.get('tags', [])
    
    # Добавляем номер цитаты, если указан
    prefix = f"{index}. " if index is not None else ""
    
    message = f'{prefix}💭 "{content}"\n\n— {author}'
    
    if tags:
        tags_label = get_text(user_id, "formatters.tags_label")
        message += f'\n\n{tags_label} {", ".join(tags)}'
    
    return message


def format_favorites_list(favorites: List[Dict[str, Any]], page: int = 0, per_page: int = 3, user_id: int = 0) -> str:
    """
    Форматирование списка избранных цитат для отправки
    
    Args:
        favorites: Список избранных цитат
        page: Номер страницы (начиная с 0)
        per_page: Количество цитат на странице
        user_id: ID пользователя для локализации
        
    Returns:
        str: Отформатированный список цитат
    """
    if not favorites:
        return get_text(user_id, "favorites_empty")
    
    total_pages = math.ceil(len(favorites) / per_page)
    start_idx = page * per_page
    end_idx = min(start_idx + per_page, len(favorites))
    
    page_favorites = favorites[start_idx:end_idx]
    message = f"{get_text(user_id, 'favorites_title')} {get_text(user_id, 'formatters.page_info').format(page=page + 1, total_pages=total_pages)}:\n\n"
    
    for i, quote in enumerate(page_favorites, 1):
        message += format_quote_dict_message(quote, i, user_id) + "\n\n"
    
    total_text = get_text(user_id, "formatters.total_favorites")
    message += total_text.format(count=len(favorites))
    
    return message


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Обрезание текста до максимальной длины
    
    Args:
        text: Исходный текст
        max_length: Максимальная длина
        
    Returns:
        str: Обрезанный текст с многоточием если необходимо
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


def format_success_message(action: str, user_id: int = 0, quote_author: Optional[str] = None) -> str:
    """
    Форматирование сообщения об успешном действии
    
    Args:
        action: Выполненное действие
        user_id: ID пользователя для локализации
        quote_author: Автор цитаты (опционально)
        
    Returns:
        str: Отформатированное сообщение об успехе
    """
    author_info = f' — {quote_author}' if quote_author else ''
    
    message_keys = {
        'added_to_favorites': 'formatters.success_added_to_favorites',
        'removed_from_favorites': 'formatters.success_removed_from_favorites',
        'cleared_favorites': 'formatters.success_cleared_favorites',
        'already_in_favorites': 'formatters.success_already_in_favorites'
    }
    
    key = message_keys.get(action, 'formatters.success_added_to_favorites')
    message = get_text(user_id, key)
    
    return message.format(author_info=author_info)


def format_error_message(error_type: str, user_id: int = 0) -> str:
    """
    Форматирование сообщения об ошибке
    
    Args:
        error_type: Тип ошибки
        user_id: ID пользователя для локализации
        
    Returns:
        str: Отформатированное сообщение об ошибке
    """
    error_keys = {
        'quote_not_found': 'formatters.error_quote_not_found',
        'already_in_favorites': 'formatters.error_already_in_favorites',
        'not_in_favorites': 'formatters.error_not_in_favorites',
        'storage_error': 'formatters.error_storage_error',
        'api_error': 'formatters.error_api_error'
    }
    
    key = error_keys.get(error_type, 'formatters.error_api_error')
    return get_text(user_id, key)
