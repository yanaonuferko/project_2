from aiogram.fsm.state import State, StatesGroup


class QuoteState(StatesGroup):
    pass


class DeleteConfirmationState(StatesGroup):
    """Состояния для подтверждения удаления цитат из избранного"""
    waiting_for_confirmation = State()  # Ожидание подтверждения удаления конкретной цитаты
    waiting_for_clear_all_confirmation = State()  # Ожидание подтверждения очистки всех избранных
