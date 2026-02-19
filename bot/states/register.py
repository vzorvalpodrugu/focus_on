from aiogram.fsm.state import StatesGroup, State

class RegisterStates(StatesGroup):
    """Состояния регистрации"""
    choosing_role = State()
    entering_name = State()
    choosing_class = State()
    choosing_subjects = State()