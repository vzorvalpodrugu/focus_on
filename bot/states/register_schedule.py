from aiogram.fsm.state import StatesGroup, State


class RegisterSchedule(StatesGroup):
    choosing_student = State()
    choosing_day = State()
    choosing_time = State()
    choosing_duration = State()
    choosing_cost = State()