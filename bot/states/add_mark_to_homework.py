from aiogram.fsm.state import StatesGroup, State


class AddMarkToHomework(StatesGroup):
    choosing_lesson = State()
    choosing_mark = State()