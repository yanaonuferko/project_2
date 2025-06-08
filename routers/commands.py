from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InaccessibleMessage
from aiogram.fsm.context import FSMContext
import logging
import math
from typing import Union, Optional

from states.quote_states import DeleteConfirmationState
from utils.logger import log_command_usage
from utils.storage import (
    add_to_favorites, remove_from_favorites, get_user_favorites, 
    clear_user_favorites, is_quote_in_favorites
)
from utils.localization import get_text, set_user_language, get_user_language
from utils.formatters import format_quote_message, format_favorites_list
from services.api_client import get_random_quote, clear_cache, get_cache_stats
from keyboards.inline import (
    get_quote_keyboard, get_favorites_navigation_keyboard, 
    get_confirmation_keyboard, get_language_keyboard,
    get_delete_confirmation_keyboard, get_clear_all_confirmation_keyboard
)
from filters.favorite_filter import extract_quote_id_from_callback
from states import DeleteConfirmationState

router = Router()
logger = logging.getLogger(__name__)


def is_accessible_message(message: Union[Message, InaccessibleMessage, None]) -> bool:
    """Check if message is accessible and has required attributes"""
    return message is not None and not isinstance(message, InaccessibleMessage)


def safe_get_message_text(message: Union[Message, InaccessibleMessage, None]) -> Optional[str]:
    """Safely get text from message, return None if inaccessible"""
    if is_accessible_message(message):
        return message.text  # type: ignore
    return None


async def safe_edit_text(
    message: Union[Message, InaccessibleMessage, None], 
    text: str, 
    reply_markup=None
) -> bool:
    """Safely edit message text, return True if successful"""
    try:
        if is_accessible_message(message):
            await message.edit_text(text, reply_markup=reply_markup)  # type: ignore
            return True
    except Exception:
        pass
    return False


async def safe_edit_reply_markup(
    message: Union[Message, InaccessibleMessage, None], 
    reply_markup=None
) -> bool:
    """Safely edit message reply markup, return True if successful"""
    try:
        if is_accessible_message(message):
            await message.edit_reply_markup(reply_markup=reply_markup)  # type: ignore
            return True
    except Exception:
        pass
    return False


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Команда /start - приветствие и краткая инструкция"""
    user_id = message.from_user.id if message.from_user else 0
    log_command_usage(user_id, "start")
    
    welcome_text = get_text(user_id, "start")
    
    await message.answer(welcome_text)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Команда /help - описание всех доступных команд"""
    user_id = message.from_user.id if message.from_user else 0
    log_command_usage(user_id, "help")
    
    help_text = get_text(user_id, "help")
    
    await message.answer(help_text)


@router.message(Command("quote"))
async def cmd_quote(message: Message):
    """Команда /quote - вывод случайной цитаты с кнопками избранного"""
    user_id = message.from_user.id if message.from_user else 0
    log_command_usage(user_id, "quote")
    
    try:
        quote = await get_random_quote()
        if quote:
            quote_text = format_quote_message(quote, user_id=user_id)
            # Создаем клавиатуру с кнопками
            keyboard = get_quote_keyboard(quote._id, user_id)
            await message.answer(quote_text, reply_markup=keyboard)
        else:
            quote_text = get_text(user_id, "quote_fetch_error")
            await message.answer(quote_text)
            
    except Exception as e:
        logger.error(f"Error fetching random quote: {e}")
        quote_text = get_text(user_id, "api_error")
        await message.answer(quote_text)


@router.message(Command("favorites"))
async def cmd_favorites(message: Message):
    """Команда /favorites - вывод списка избранных цитат"""
    user_id = message.from_user.id if message.from_user else 0
    log_command_usage(user_id, "favorites")
    
    try:
        favorites = get_user_favorites(user_id)
        if not favorites:
            favorites_text = get_text(user_id, "favorites_empty")
            await message.answer(favorites_text)
        else:
            # Показываем первую страницу избранных
            favorites_text = format_favorites_list(favorites, page=0, user_id=user_id)
            keyboard = get_favorites_navigation_keyboard(
                current_page=0,
                total_pages=math.ceil(len(favorites) / 3),
                quotes_on_page=favorites[:3],
                user_id=user_id
            )
            await message.answer(favorites_text, reply_markup=keyboard)
            
    except Exception as e:
        logger.error(f"Error accessing favorites: {e}")
        error_text = get_text(user_id, "api_error")
        await message.answer(error_text)


@router.message(Command("cache_stats"))
async def cmd_cache_stats(message: Message):
    """Скрытая команда для просмотра статистики кэша"""
    user_id = message.from_user.id if message.from_user else 0
    log_command_usage(user_id, "cache_stats")
    
    stats = get_cache_stats()
    stats_text = (
        f"📊 Cache Statistics:\n\n"
        f"Total entries: {stats['total_entries']}\n"
        f"Valid entries: {stats['valid_entries']}\n"
        f"Expired entries: {stats['expired_entries']}\n"
        f"Cache TTL: {stats['cache_ttl']} seconds"
    )
    
    await message.answer(stats_text)


@router.message(Command("clear_cache"))
async def cmd_clear_cache(message: Message):
    """Скрытая команда для очистки кэша"""
    user_id = message.from_user.id if message.from_user else 0
    log_command_usage(user_id, "clear_cache")
    
    clear_cache()
    await message.answer("🗑️ Cache cleared successfully!")


@router.message(Command("language"))
async def cmd_language(message: Message):
    """Команда /language - выбор языка интерфейса"""
    user_id = message.from_user.id if message.from_user else 0
    log_command_usage(user_id, "language")
    
    # Получаем текст на текущем языке пользователя
    text = get_text(user_id, "language_select")
    keyboard = get_language_keyboard()
    
    await message.answer(text, reply_markup=keyboard)


# Обработчик выбора языка
@router.callback_query(F.data.startswith("set_language_"))
async def callback_set_language(callback: CallbackQuery):
    """Обработчик установки языка пользователя"""
    user_id = callback.from_user.id
    language_code = (callback.data or "").replace("set_language_", "")
    
    try:
        if set_user_language(user_id, language_code):
            # Получаем подтверждение на новом языке
            success_text = get_text(user_id, "language_changed")
            await callback.answer(success_text, show_alert=True)
            
            # Обновляем сообщение с новым языком
            language_text = get_text(user_id, "language_select")
            keyboard = get_language_keyboard()
            await safe_edit_text(callback.message, language_text, keyboard)
            
        else:
            await callback.answer("❌ Неподдерживаемый язык", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error setting language: {e}")
        await callback.answer("❌ Ошибка при смене языка", show_alert=True)


# Обработчики callback-кнопок для избранного

@router.callback_query(F.data.startswith("add_favorite_"))
async def callback_add_favorite(callback: CallbackQuery):
    """Обработчик добавления цитаты в избранное"""
    user_id = callback.from_user.id
    quote_id = extract_quote_id_from_callback(callback.data or "", "add_favorite_")
    
    try:
        # Получаем данные цитаты из сообщения
        message_text = safe_get_message_text(callback.message)
        if message_text:
            # Парсим цитату из сообщения
            lines = message_text.split('\n')
            if len(lines) >= 3:
                content = lines[0].replace('💭 "', '').replace('"', '')
                author = lines[2].replace('— ', '')
                tags = []
                
                # Ищем теги если есть
                for line in lines:
                    if line.startswith('🏷️ Tags:'):
                        tags_str = line.replace('🏷️ Tags: ', '')
                        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip() != 'None']
                
                quote_dict = {
                    '_id': quote_id,
                    'content': content,
                    'author': author,
                    'tags': tags
                }
                
                # Добавляем в избранное
                if add_to_favorites(user_id, quote_dict):
                    success_text = get_text(user_id, "quote_added_to_favorites")
                    await callback.answer(success_text, show_alert=True)
                    
                    # Обновляем клавиатуру
                    new_keyboard = get_quote_keyboard(quote_id, user_id)
                    await safe_edit_reply_markup(callback.message, new_keyboard)
                else:
                    already_in_text = get_text(user_id, "quote_already_in_favorites")
                    await callback.answer(already_in_text, show_alert=True)
            else:
                error_text = get_text(user_id, "error_quote_processing")
                await callback.answer(error_text, show_alert=True)
        else:
            not_found_text = get_text(user_id, "message_not_found")
            await callback.answer(not_found_text, show_alert=True)
            
    except Exception as e:
        logger.error(f"Error adding quote to favorites: {e}")
        error_text = get_text(user_id, "error_adding_favorite")
        await callback.answer(error_text, show_alert=True)


@router.callback_query(F.data.startswith("remove_favorite_"))
async def callback_remove_favorite(callback: CallbackQuery, state: FSMContext):
    """Обработчик начала удаления цитаты из избранного с подтверждением"""
    user_id = callback.from_user.id
    quote_id = extract_quote_id_from_callback(callback.data or "", "remove_favorite_")
    
    try:
        # Получаем информацию о цитате
        favorites = get_user_favorites(user_id)
        quote_to_delete = None
        
        for quote in favorites:
            if quote.get('_id') == quote_id:
                quote_to_delete = quote
                break
        
        if quote_to_delete:
            # Сохраняем ID цитаты в состоянии
            await state.update_data(quote_id=quote_id)
            await state.set_state(DeleteConfirmationState.waiting_for_confirmation)
            
            # Формируем сообщение подтверждения
            quote_text = quote_to_delete.get('content', 'Unknown quote')[:100]
            if len(quote_to_delete.get('content', '')) > 100:
                quote_text += '...'
            author = quote_to_delete.get('author', 'Unknown Author')
            
            confirm_text = get_text(user_id, "confirm_delete_quote").format(
                quote_text=quote_text,
                author=author
            )
            
            keyboard = get_delete_confirmation_keyboard(quote_id, user_id)
            await safe_edit_text(callback.message, confirm_text, keyboard)
            
        else:
            not_found_text = get_text(user_id, "quote_not_in_favorites")
            await callback.answer(not_found_text, show_alert=True)
            
    except Exception as e:
        logger.error(f"Error starting quote deletion: {e}")
        error_text = get_text(user_id, "error_removing_favorite")
        await callback.answer(error_text, show_alert=True)


@router.callback_query(F.data.startswith("favorites_page_"))
async def callback_favorites_page(callback: CallbackQuery):
    """Обработчик навигации по страницам избранного"""
    user_id = callback.from_user.id
    try:
        page = int((callback.data or "").replace("favorites_page_", "") or "0")
    except ValueError:
        page = 0
    
    try:
        favorites = get_user_favorites(user_id)
        if not favorites:
            await callback.answer("❌ У вас нет избранных цитат", show_alert=True)
            return
        
        total_pages = math.ceil(len(favorites) / 3)
        if page < 0 or page >= total_pages:
            await callback.answer("❌ Неверная страница", show_alert=True)
            return
        
        # Формируем текст для страницы
        start_idx = page * 3
        end_idx = min(start_idx + 3, len(favorites))
        quotes_on_page = favorites[start_idx:end_idx]
        favorites_text = format_favorites_list(favorites, page=page, user_id=user_id)
        keyboard = get_favorites_navigation_keyboard(
            current_page=page,
            total_pages=total_pages,
            quotes_on_page=quotes_on_page,
            user_id=user_id
        )
        
        await safe_edit_text(callback.message, favorites_text, keyboard)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error navigating favorites: {e}")
        await callback.answer("❌ Ошибка при навигации", show_alert=True)





@router.callback_query(F.data == "get_another_quote")
async def callback_another_quote(callback: CallbackQuery):
    """Обработчик получения новой цитаты"""
    user_id = callback.from_user.id
    
    try:
        logger.info(f"User {user_id} requested another quote")
        quote = await get_random_quote()
        if quote:
            logger.info(f"Got quote with ID: {quote._id}")
            quote_text = format_quote_message(quote, user_id=user_id)
            keyboard = get_quote_keyboard(quote._id, user_id)
            await safe_edit_text(callback.message, quote_text, keyboard)
            await callback.answer()
        else:
            logger.warning("No quote received from API")
            error_text = get_text(user_id, "quote_fetch_error")
            await callback.answer(error_text, show_alert=True)
        
    except Exception as e:
        logger.error(f"Error getting another quote: {e}")
        error_text = get_text(user_id, "api_error")
        await callback.answer(error_text, show_alert=True)


@router.callback_query(F.data.startswith("already_favorite_"))
async def callback_already_favorite(callback: CallbackQuery):
    """Обработчик для цитат уже находящихся в избранном"""
    user_id = callback.from_user.id
    already_text = get_text(user_id, "quote_already_in_favorites")
    await callback.answer(already_text, show_alert=False)


# FSM обработчики для подтверждения удаления

@router.callback_query(F.data.startswith("confirm_delete_"), DeleteConfirmationState.waiting_for_confirmation)
async def callback_confirm_delete(callback: CallbackQuery, state: FSMContext):
    """Обработчик подтверждения удаления цитаты"""
    user_id = callback.from_user.id
    quote_id = (callback.data or "").replace("confirm_delete_", "")
    
    try:
        # Получаем данные из состояния
        state_data = await state.get_data()
        stored_quote_id = state_data.get('quote_id')
        
        # Проверяем, что ID совпадают
        if quote_id != stored_quote_id:
            await callback.answer("❌ Ошибка: неверный ID цитаты", show_alert=True)
            await state.clear()
            return
        
        # Удаляем цитату
        if remove_from_favorites(user_id, quote_id):
            success_text = get_text(user_id, "quote_removed_from_favorites")
            await callback.answer(success_text, show_alert=True)
            
            # Обновляем список избранных
            favorites = get_user_favorites(user_id)
            if not favorites:
                empty_text = get_text(user_id, "favorites_empty")
                await safe_edit_text(callback.message, empty_text)
            else:
                # Показываем обновленный список избранных
                favorites_text = format_favorites_list(favorites, page=0, user_id=user_id)
                keyboard = get_favorites_navigation_keyboard(
                    current_page=0,
                    total_pages=math.ceil(len(favorites) / 3),
                    quotes_on_page=favorites[:3],
                    user_id=user_id
                )
                await safe_edit_text(callback.message, favorites_text, keyboard)
        else:
            not_found_text = get_text(user_id, "quote_not_in_favorites")
            await callback.answer(not_found_text, show_alert=True)
        
        # Очищаем состояние
        await state.clear()
            
    except Exception as e:
        logger.error(f"Error confirming quote deletion: {e}")
        error_text = get_text(user_id, "error_removing_favorite")
        await callback.answer(error_text, show_alert=True)
        await state.clear()


@router.callback_query(F.data == "cancel_delete", DeleteConfirmationState.waiting_for_confirmation)
async def callback_cancel_delete(callback: CallbackQuery, state: FSMContext):
    """Обработчик отмены удаления цитаты"""
    user_id = callback.from_user.id
    
    try:
        # Получаем текст отмены
        cancel_text = get_text(user_id, "delete_cancelled")
        await callback.answer(cancel_text)
        
        # Возвращаемся к списку избранных
        favorites = get_user_favorites(user_id)
        if favorites:
            favorites_text = format_favorites_list(favorites, page=0, user_id=user_id)
            keyboard = get_favorites_navigation_keyboard(
                current_page=0,
                total_pages=math.ceil(len(favorites) / 3),
                quotes_on_page=favorites[:3],
                user_id=user_id
            )
            await safe_edit_text(callback.message, favorites_text, keyboard)
        else:
            empty_text = get_text(user_id, "favorites_empty")
            await safe_edit_text(callback.message, empty_text)
        
        # Очищаем состояние
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error canceling quote deletion: {e}")
        await callback.answer("Ошибка при отмене", show_alert=True)
        await state.clear()


# Обработчик для кнопки "Clear All" с FSM
@router.callback_query(F.data == "clear_all_favorites")
async def callback_clear_all_favorites(callback: CallbackQuery, state: FSMContext):
    """Обработчик начала очистки всех избранных цитат с подтверждением"""
    user_id = callback.from_user.id
    
    try:
        favorites = get_user_favorites(user_id)
        if not favorites:
            empty_text = get_text(user_id, "favorites_empty")
            await callback.answer(empty_text, show_alert=True)
            return
        
        # Устанавливаем состояние ожидания подтверждения
        await state.set_state(DeleteConfirmationState.waiting_for_clear_all_confirmation)
        
        # Показываем сообщение подтверждения
        confirm_text = get_text(user_id, "confirm_clear_all_favorites")
        keyboard = get_clear_all_confirmation_keyboard(user_id)
        await safe_edit_text(callback.message, confirm_text, keyboard)
        
    except Exception as e:
        logger.error(f"Error starting clear all favorites: {e}")
        error_text = get_text(user_id, "error_clearing_favorites")
        await callback.answer(error_text, show_alert=True)


@router.callback_query(F.data == "confirm_clear_all", DeleteConfirmationState.waiting_for_clear_all_confirmation)
async def callback_confirm_clear_all(callback: CallbackQuery, state: FSMContext):
    """Обработчик подтверждения очистки всех избранных"""
    user_id = callback.from_user.id
    
    try:
        if clear_user_favorites(user_id):
            success_text = get_text(user_id, "all_favorites_cleared")
            await callback.answer(success_text, show_alert=True)
            
            cleared_text = get_text(user_id, "favorites_cleared")
            await safe_edit_text(callback.message, cleared_text)
        else:
            error_text = get_text(user_id, "error_clearing_favorites")
            await callback.answer(error_text, show_alert=True)
        
        # Очищаем состояние
        await state.clear()
            
    except Exception as e:
        logger.error(f"Error confirming clear all favorites: {e}")
        error_text = get_text(user_id, "error_clearing_favorites")
        await callback.answer(error_text, show_alert=True)
        await state.clear()


@router.callback_query(F.data == "cancel_clear_all", DeleteConfirmationState.waiting_for_clear_all_confirmation)
async def callback_cancel_clear_all(callback: CallbackQuery, state: FSMContext):
    """Обработчик отмены очистки всех избранных"""
    user_id = callback.from_user.id
    
    try:
        # Получаем текст отмены
        cancel_text = get_text(user_id, "clear_all_cancelled")
        await callback.answer(cancel_text)
        
        # Возвращаемся к списку избранных
        favorites = get_user_favorites(user_id)
        if favorites:
            favorites_text = format_favorites_list(favorites, page=0, user_id=user_id)
            keyboard = get_favorites_navigation_keyboard(
                current_page=0,
                total_pages=math.ceil(len(favorites) / 3),
                quotes_on_page=favorites[:3],
                user_id=user_id
            )
            await safe_edit_text(callback.message, favorites_text, keyboard)
        else:
            empty_text = get_text(user_id, "favorites_empty")
            await safe_edit_text(callback.message, empty_text)
        
        # Очищаем состояние
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error canceling clear all favorites: {e}")
        await callback.answer("Ошибка при отмене", show_alert=True)
        await state.clear()
