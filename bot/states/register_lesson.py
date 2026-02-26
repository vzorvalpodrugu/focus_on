from aiogram.fsm.state import StatesGroup, State


class RegisterLesson(StatesGroup):
    choosing_student = State()
    choosing_subject = State()
    choosing_topic = State()
    waiting_for_lesson_screenshots = State()
    waiting_for_homework = State()
