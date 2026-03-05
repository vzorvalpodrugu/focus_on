from aiogram.fsm.state import StatesGroup, State


class ViewStudentsWithoutDoneHw(StatesGroup):
    choosing_student = State()
    choosing_lesson = State()