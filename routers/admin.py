"""
Административные команды для бота
"""
import logging
import asyncio
from typing import Union, cast, Optional
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from filters.admin_filter import AdminFilter
from states.admin_states import BroadcastState, BanState, UnbanState
from utils.logger import log_command_usage
from utils.storage import load_data, clear_user_favorites
from utils.user_management import (
    get_user_stats, get_all_user_ids, ban_user, unban_user, 
    is_user_banned, get_banned_users_list, get_user_info
)
from services.api_client import clear_cache, get_cache_stats
from keyboards.admin import (
    get_admin_main_keyboard, get_broadcast_confirmation_keyboard,
    get_ban_management_keyboard, get_ban_confirmation_keyboard,
    get_unban_confirmation_keyboard, get_back_to_admin_keyboard
)

router = Router()
logger = logging.getLogger(__name__)


# Основные команды админ-панели

@router.message(Command("admin"), AdminFilter())
async def cmd_admin(message: Message):
    """Команда /admin - главная панель администратора"""
    if not message.from_user:
        return
    
    user_id = message.from_user.id
    log_command_usage(user_id, "admin")
    
    admin_text = (
        "🔐 Административная панель\n\n"
        "Добро пожаловать в панель администратора!\n"
        "Выберите нужное действие:"
    )
    
    keyboard = get_admin_main_keyboard(user_id)
    await message.answer(admin_text, reply_markup=keyboard)


@router.callback_query(F.data == "admin_main")
async def callback_admin_main(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню админ-панели"""
    if not callback.from_user or not callback.message:
        return
        
    await state.clear()  # Очищаем любое состояние FSM
    
    admin_text = (
        "🔐 Административная панель\n\n"
        "Добро пожаловать в панель администратора!\n"
        "Выберите нужное действие:"
    )
    
    keyboard = get_admin_main_keyboard(callback.from_user.id)
    
    # Безопасная проверка типа сообщения
    if hasattr(callback.message, 'edit_text'):
        await callback.message.edit_text(admin_text, reply_markup=keyboard)
    
    await callback.answer()


# Статистика

@router.message(Command("stats"), AdminFilter())
@router.callback_query(F.data == "admin_stats")
async def cmd_admin_stats(update: Union[Message, CallbackQuery], state: FSMContext):
    """Команда /stats - статистика использования"""
    # Определяем тип события
    if isinstance(update, CallbackQuery):
        user_id = update.from_user.id if update.from_user else 0
        is_callback = True
    else:
        user_id = update.from_user.id if update.from_user else 0
        is_callback = False
    
    log_command_usage(user_id, "stats")
    
    try:
        # Получаем статистику пользователей
        user_stats = get_user_stats()
        
        # Получаем данные о цитатах
        quotes_data = load_data()
        total_favorites = sum(len(favorites) for favorites in quotes_data.values())
        users_with_favorites = len([u for u in quotes_data.values() if u])
        
        # Получаем статистику кэша
        cache_stats = get_cache_stats()
        
        # Получаем количество заблокированных пользователей
        banned_count = len(get_banned_users_list())
        
        stats_text = (
            f"📊 Статистика бота:\n\n"
            f"👥 Всего пользователей: {user_stats.get('total_users', 0)}\n"
            f"✅ Активных пользователей: {user_stats.get('active_users', 0)}\n"
            f"📅 Активных за месяц: {user_stats.get('recent_users', 0)}\n"
            f"🚫 Заблокированных: {banned_count}\n\n"
            f"⭐ Всего избранных цитат: {total_favorites}\n"
            f"📚 Пользователей с избранными: {users_with_favorites}\n\n"
            f"💾 Кэш: {cache_stats.get('valid_entries', 0)} записей\n"
            f"⏰ TTL кэша: {cache_stats.get('cache_ttl', 0)} сек\n"
            f"🗑️ Устаревших записей: {cache_stats.get('expired_entries', 0)}"
        )
        
        keyboard = get_back_to_admin_keyboard(user_id)
        
        if is_callback and hasattr(update, 'message') and update.message:
            await update.message.edit_text(stats_text, reply_markup=keyboard)
            await update.answer()
        else:
            await update.answer(stats_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}")
        error_text = "❌ Ошибка при получении статистики"
        
        if is_callback:
            await update.answer(error_text, show_alert=True)
        else:
            await update.answer(error_text)


# Управление пользователями

@router.callback_query(F.data == "admin_users")
async def callback_admin_users(callback: CallbackQuery):
    """Информация о пользователях"""
    if not callback.from_user or not callback.message:
        return
        
    user_id = callback.from_user.id
    log_command_usage(user_id, "admin_users")
    
    try:
        quotes_data = load_data()
        
        if not quotes_data:
            users_text = "📝 Нет зарегистрированных пользователей с избранными цитатами"
        else:
            users_text = "👥 Пользователи с избранными цитатами:\n\n"
            
            for user_id_str, favorites in quotes_data.items():
                favorites_count = len(favorites)
                banned_status = " (🚫 заблокирован)" if is_user_banned(int(user_id_str)) else ""
                users_text += f"🆔 {user_id_str}: {favorites_count} избранных{banned_status}\n"
        
        keyboard = get_back_to_admin_keyboard(user_id)
        await callback.message.edit_text(users_text, reply_markup=keyboard)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error getting users info: {e}")
        await callback.answer("❌ Ошибка при получении информации о пользователях", show_alert=True)


# Очистка кэша

@router.callback_query(F.data == "admin_clear_cache")
async def callback_admin_clear_cache(callback: CallbackQuery):
    """Очистка кэша API"""
    if not callback.from_user or not callback.message:
        return
        
    user_id = callback.from_user.id
    
    try:
        clear_cache()
        keyboard = get_back_to_admin_keyboard(user_id)
        await callback.message.edit_text("✅ Кэш очищен успешно!", reply_markup=keyboard)
        await callback.answer("Кэш очищен!")
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        await callback.answer("❌ Ошибка при очистке кэша", show_alert=True)


# Система рассылки

@router.message(Command("broadcast"), AdminFilter())
@router.callback_query(F.data == "admin_broadcast")
async def cmd_admin_broadcast(update: Union[Message, CallbackQuery], state: FSMContext):
    """Команда /broadcast - начало рассылки"""
    # Определяем тип события
    if isinstance(update, CallbackQuery):
        user_id = update.from_user.id if update.from_user else 0
        is_callback = True
    else:
        user_id = update.from_user.id if update.from_user else 0
        is_callback = False
    
    log_command_usage(user_id, "broadcast")
    
    await state.set_state(BroadcastState.waiting_for_message)
    
    broadcast_text = (
        "📢 Система рассылки\n\n"
        "Отправьте сообщение, которое хотите разослать всем пользователям бота.\n\n"
        "⚠️ Будьте осторожны! Сообщение будет отправлено всем активным пользователям."
    )
    
    if is_callback and hasattr(update, 'message') and update.message:
        await update.message.edit_text(broadcast_text)
        await update.answer()
    else:
        await update.answer(broadcast_text)


@router.message(BroadcastState.waiting_for_message)
async def process_broadcast_message(message: Message, state: FSMContext):
    """Обработка сообщения для рассылки"""
    if not message.from_user:
        return
        
    user_id = message.from_user.id
    
    # Сохраняем сообщение в состоянии
    await state.update_data(broadcast_text=message.text or message.caption or "")
    await state.set_state(BroadcastState.waiting_for_confirmation)
    
    # Получаем статистику для подтверждения
    all_users = get_all_user_ids()
    banned_users = get_banned_users_list()
    target_users = len([uid for uid in all_users if uid not in banned_users])
    
    confirmation_text = (
        f"📢 Подтверждение рассылки\n\n"
        f"Текст сообщения:\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{message.text or message.caption or 'Без текста'}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Получателей: {target_users} пользователей\n"
        f"🚫 Заблокированных: {len(banned_users)}\n\n"
        f"Подтвердите отправку:"
    )
    
    keyboard = get_broadcast_confirmation_keyboard(user_id)
    await message.answer(confirmation_text, reply_markup=keyboard)


@router.callback_query(F.data == "confirm_broadcast", BroadcastState.waiting_for_confirmation)
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext):
    """Подтверждение и выполнение рассылки"""
    if not callback.from_user or not callback.message:
        return
        
    user_id = callback.from_user.id
    
    try:
        # Получаем данные из состояния
        data = await state.get_data()
        broadcast_text = data.get('broadcast_text', '')
        
        if not broadcast_text:
            await callback.answer("❌ Нет текста для рассылки", show_alert=True)
            return
        
        # Получаем список пользователей для рассылки
        all_users = get_all_user_ids()
        banned_users = get_banned_users_list()
        target_users = [uid for uid in all_users if uid not in banned_users]
        
        if not target_users:
            await callback.answer("❌ Нет пользователей для рассылки", show_alert=True)
            return
        
        # Обновляем сообщение о начале рассылки
        await callback.message.edit_text(
            f"📤 Начинаю рассылку...\n"
            f"Пользователей: {len(target_users)}"
        )
        await callback.answer()
        
        # Выполняем рассылку
        bot = callback.bot
        sent_count = 0
        failed_count = 0
        
        for user_id_target in target_users:
            try:
                await bot.send_message(user_id_target, broadcast_text)
                sent_count += 1
                
                # Небольшая пауза между отправками
                await asyncio.sleep(0.05)
            except Exception as e:
                failed_count += 1
                logger.warning(f"Failed to send broadcast to user {user_id_target}: {e}")
        
        # Отчет о результатах
        result_text = (
            f"✅ Рассылка завершена!\n\n"
            f"📤 Отправлено: {sent_count}\n"
            f"❌ Ошибок: {failed_count}\n"
            f"📊 Всего пользователей: {len(target_users)}"
        )
        
        keyboard = get_back_to_admin_keyboard(user_id)
        await callback.message.edit_text(result_text, reply_markup=keyboard)
        
        # Очищаем состояние
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error during broadcast: {e}")
        await callback.answer("❌ Ошибка при рассылке", show_alert=True)
        await state.clear()


@router.callback_query(F.data == "cancel_broadcast", BroadcastState.waiting_for_confirmation)
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    """Отмена рассылки"""
    if not callback.from_user or not callback.message:
        return
        
    await state.clear()
    
    keyboard = get_back_to_admin_keyboard(callback.from_user.id)
    await callback.message.edit_text("❌ Рассылка отменена", reply_markup=keyboard)
    await callback.answer("Рассылка отменена")


@router.callback_query(F.data == "edit_broadcast", BroadcastState.waiting_for_confirmation)
async def edit_broadcast(callback: CallbackQuery, state: FSMContext):
    """Изменение текста рассылки"""
    if not callback.message:
        return
        
    await state.set_state(BroadcastState.waiting_for_message)
    
    await callback.message.edit_text(
        "✏️ Отправьте новый текст для рассылки:"
    )
    await callback.answer()


# Система банов

@router.callback_query(F.data == "admin_bans")
async def callback_admin_bans(callback: CallbackQuery):
    """Меню управления банами"""
    if not callback.from_user or not callback.message:
        return
        
    user_id = callback.from_user.id
    
    banned_users = get_banned_users_list()
    
    bans_text = (
        f"🚫 Управление блокировками\n\n"
        f"Заблокированных пользователей: {len(banned_users)}\n\n"
        f"Выберите действие:"
    )
    
    keyboard = get_ban_management_keyboard(user_id)
    await callback.message.edit_text(bans_text, reply_markup=keyboard)
    await callback.answer()


@router.message(Command("ban"), AdminFilter())
@router.callback_query(F.data == "admin_ban_user")
async def cmd_ban_user(update: Union[Message, CallbackQuery], state: FSMContext):
    """Команда /ban - начало блокировки пользователя"""
    # Определяем тип события
    if isinstance(update, CallbackQuery):
        user_id = update.from_user.id if update.from_user else 0
        is_callback = True
    else:
        user_id = update.from_user.id if update.from_user else 0
        is_callback = False
    
    log_command_usage(user_id, "ban")
    
    await state.set_state(BanState.waiting_for_user_id)
    
    ban_text = (
        "🚫 Блокировка пользователя\n\n"
        "Отправьте ID пользователя, которого хотите заблокировать.\n\n"
        "Пример: 123456789"
    )
    
    if is_callback and hasattr(update, 'message') and update.message:
        await update.message.edit_text(ban_text)
        await update.answer()
    else:
        await update.answer(ban_text)


@router.message(BanState.waiting_for_user_id)
async def process_ban_user_id(message: Message, state: FSMContext):
    """Обработка ID пользователя для блокировки"""
    if not message.from_user or not message.text:
        return
        
    try:
        target_user_id = int(message.text.strip())
        
        # Проверяем, не пытается ли админ заблокировать сам себя
        if target_user_id == message.from_user.id:
            await message.answer("❌ Вы не можете заблокировать сами себя!")
            return
        
        # Проверяем, не заблокирован ли уже пользователь
        if is_user_banned(target_user_id):
            await message.answer(f"⚠️ Пользователь {target_user_id} уже заблокирован!")
            return
        
        # Получаем информацию о пользователе
        user_info = get_user_info(target_user_id)
        
        await state.update_data(target_user_id=target_user_id)
        await state.set_state(BanState.waiting_for_confirmation)
        
        if user_info:
            username = user_info.get('username', 'неизвестно')
            first_name = user_info.get('first_name', 'неизвестно')
            confirmation_text = (
                f"🚫 Подтверждение блокировки\n\n"
                f"Пользователь: {target_user_id}\n"
                f"Имя: {first_name}\n"
                f"Username: @{username}\n\n"
                f"Подтвердите блокировку:"
            )
        else:
            confirmation_text = (
                f"🚫 Подтверждение блокировки\n\n"
                f"Пользователь: {target_user_id}\n"
                f"(Информация о пользователе не найдена)\n\n"
                f"Подтвердите блокировку:"
            )
        
        keyboard = get_ban_confirmation_keyboard(message.from_user.id, target_user_id)
        await message.answer(confirmation_text, reply_markup=keyboard)
        
    except ValueError:
        await message.answer("❌ Некорректный ID пользователя. Введите число.")
    except Exception as e:
        logger.error(f"Error processing ban user ID: {e}")
        await message.answer("❌ Произошла ошибка")


@router.callback_query(F.data.startswith("confirm_ban_"), BanState.waiting_for_confirmation)
async def confirm_ban_user(callback: CallbackQuery, state: FSMContext):
    """Подтверждение блокировки пользователя"""
    if not callback.from_user or not callback.data or not callback.message:
        return
        
    try:
        target_user_id = int(callback.data.replace("confirm_ban_", ""))
        
        # Получаем данные из состояния для проверки
        data = await state.get_data()
        stored_user_id = data.get('target_user_id')
        
        if target_user_id != stored_user_id:
            await callback.answer("❌ Ошибка: несоответствие ID", show_alert=True)
            return
        
        # Блокируем пользователя
        if ban_user(target_user_id):
            success_text = f"✅ Пользователь {target_user_id} заблокирован!"
            keyboard = get_back_to_admin_keyboard(callback.from_user.id)
            await callback.message.edit_text(success_text, reply_markup=keyboard)
            await callback.answer("Пользователь заблокирован")
        else:
            await callback.answer("❌ Пользователь уже был заблокирован", show_alert=True)
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error confirming ban: {e}")
        await callback.answer("❌ Ошибка при блокировке", show_alert=True)
        await state.clear()


@router.callback_query(F.data == "cancel_ban", BanState.waiting_for_confirmation)
async def cancel_ban_user(callback: CallbackQuery, state: FSMContext):
    """Отмена блокировки пользователя"""
    if not callback.from_user or not callback.message:
        return
        
    await state.clear()
    
    keyboard = get_ban_management_keyboard(callback.from_user.id)
    await callback.message.edit_text("❌ Блокировка отменена", reply_markup=keyboard)
    await callback.answer("Блокировка отменена")


# Разблокировка пользователей

@router.message(Command("unban"), AdminFilter())
@router.callback_query(F.data == "admin_unban_user")
async def cmd_unban_user(update: Union[Message, CallbackQuery], state: FSMContext):
    """Команда /unban - начало разблокировки пользователя"""
    # Определяем тип события
    if isinstance(update, CallbackQuery):
        user_id = update.from_user.id if update.from_user else 0
        is_callback = True
    else:
        user_id = update.from_user.id if update.from_user else 0
        is_callback = False
    
    log_command_usage(user_id, "unban")
    
    await state.set_state(UnbanState.waiting_for_user_id)
    
    unban_text = (
        "✅ Разблокировка пользователя\n\n"
        "Отправьте ID пользователя, которого хотите разблокировать.\n\n"
        "Пример: 123456789"
    )
    
    if is_callback and hasattr(update, 'message') and update.message:
        await update.message.edit_text(unban_text)
        await update.answer()
    else:
        await update.answer(unban_text)


@router.message(UnbanState.waiting_for_user_id)
async def process_unban_user_id(message: Message, state: FSMContext):
    """Обработка ID пользователя для разблокировки"""
    if not message.from_user or not message.text:
        return
        
    try:
        target_user_id = int(message.text.strip())
        
        # Проверяем, заблокирован ли пользователь
        if not is_user_banned(target_user_id):
            await message.answer(f"⚠️ Пользователь {target_user_id} не заблокирован!")
            return
        
        await state.update_data(target_user_id=target_user_id)
        await state.set_state(UnbanState.waiting_for_confirmation)
        
        confirmation_text = (
            f"✅ Подтверждение разблокировки\n\n"
            f"Пользователь: {target_user_id}\n\n"
            f"Подтвердите разблокировку:"
        )
        
        keyboard = get_unban_confirmation_keyboard(message.from_user.id, target_user_id)
        await message.answer(confirmation_text, reply_markup=keyboard)
        
    except ValueError:
        await message.answer("❌ Некорректный ID пользователя. Введите число.")
    except Exception as e:
        logger.error(f"Error processing unban user ID: {e}")
        await message.answer("❌ Произошла ошибка")


@router.callback_query(F.data.startswith("confirm_unban_"), UnbanState.waiting_for_confirmation)
async def confirm_unban_user(callback: CallbackQuery, state: FSMContext):
    """Подтверждение разблокировки пользователя"""
    if not callback.from_user or not callback.data or not callback.message:
        return
        
    try:
        target_user_id = int(callback.data.replace("confirm_unban_", ""))
        
        # Получаем данные из состояния для проверки
        data = await state.get_data()
        stored_user_id = data.get('target_user_id')
        
        if target_user_id != stored_user_id:
            await callback.answer("❌ Ошибка: несоответствие ID", show_alert=True)
            return
        
        # Разблокируем пользователя
        if unban_user(target_user_id):
            success_text = f"✅ Пользователь {target_user_id} разблокирован!"
            keyboard = get_back_to_admin_keyboard(callback.from_user.id)
            await callback.message.edit_text(success_text, reply_markup=keyboard)
            await callback.answer("Пользователь разблокирован")
        else:
            await callback.answer("❌ Пользователь не был заблокирован", show_alert=True)
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error confirming unban: {e}")
        await callback.answer("❌ Ошибка при разблокировке", show_alert=True)
        await state.clear()


@router.callback_query(F.data == "cancel_unban", UnbanState.waiting_for_confirmation)
async def cancel_unban_user(callback: CallbackQuery, state: FSMContext):
    """Отмена разблокировки пользователя"""
    if not callback.from_user or not callback.message:
        return
        
    await state.clear()
    
    keyboard = get_ban_management_keyboard(callback.from_user.id)
    await callback.message.edit_text("❌ Разблокировка отменена", reply_markup=keyboard)
    await callback.answer("Разблокировка отменена")


# Список заблокированных пользователей

@router.callback_query(F.data == "admin_banned_list")
async def callback_banned_list(callback: CallbackQuery):
    """Показать список заблокированных пользователей"""
    if not callback.from_user or not callback.message:
        return
        
    user_id = callback.from_user.id
    
    banned_users = get_banned_users_list()
    
    if not banned_users:
        banned_text = "✅ Нет заблокированных пользователей"
    else:
        banned_text = f"🚫 Заблокированные пользователи ({len(banned_users)}):\n\n"
        
        for banned_id in banned_users:
            user_info = get_user_info(banned_id)
            if user_info:
                username = user_info.get('username', 'неизвестно')
                first_name = user_info.get('first_name', 'неизвестно')
                banned_text += f"👤 {banned_id} (@{username}) - {first_name}\n"
            else:
                banned_text += f"👤 {banned_id} (информация недоступна)\n"
    
    keyboard = get_ban_management_keyboard(user_id)
    await callback.message.edit_text(banned_text, reply_markup=keyboard)
    await callback.answer()


# Старые команды для совместимости

@router.message(Command("admin_clear_user"), AdminFilter())
async def cmd_admin_clear_user(message: Message):
    """Команда /admin_clear_user - очистка данных пользователя (только для супер-админа)"""
    if not message.from_user or not message.text:
        return
        
    user_id = message.from_user.id
    log_command_usage(user_id, "admin_clear_user")
    
    try:
        # Получаем ID пользователя из команды
        command_parts = message.text.split()
        if len(command_parts) < 2:
            await message.answer(
                "❌ Укажите ID пользователя:\n"
                "Пример: /admin_clear_user 12345"
            )
            return
        
        target_user_id = int(command_parts[1])
        
        # Очищаем избранные пользователя
        if clear_user_favorites(target_user_id):
            await message.answer(f"✅ Данные пользователя {target_user_id} очищены")
        else:
            await message.answer(f"⚠️ Пользователь {target_user_id} не найден")
        
    except ValueError:
        await message.answer("❌ Некорректный ID пользователя")
    except Exception as e:
        logger.error(f"Error clearing user data: {e}")
        await message.answer("❌ Ошибка при очистке данных пользователя")
