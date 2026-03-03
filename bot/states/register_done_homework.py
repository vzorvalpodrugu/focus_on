from aiogram.fsm.state import StatesGroup, State


class RegisterDoneHomework(StatesGroup):
    choosing_lesson_id = State()
    choosing_done_homework_screenshots = State()