from aiogram.fsm.state import StatesGroup, State

class LessonViewStates(StatesGroup):
    choosing_period = State()
    choosing_lesson_id = State()