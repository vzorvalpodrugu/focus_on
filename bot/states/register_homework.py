from aiogram.fsm.state import StatesGroup, State

class RegisterHomework(StatesGroup):
    choosing_lesson_id = State()
    choosing_homework_screenshots = State()