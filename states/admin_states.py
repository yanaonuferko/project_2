"""
FSM состояния для административных команд
"""
from aiogram.fsm.state import State, StatesGroup


class BroadcastState(StatesGroup):
    """Состояния для рассылки сообщений"""
    waiting_for_message = State()
    waiting_for_confirmation = State()


class BanState(StatesGroup):
    """Состояния для блокировки пользователей"""
    waiting_for_user_id = State()
    waiting_for_confirmation = State()


class UnbanState(StatesGroup):
    """Состояния для разблокировки пользователей"""
    waiting_for_user_id = State()
    waiting_for_confirmation = State()
