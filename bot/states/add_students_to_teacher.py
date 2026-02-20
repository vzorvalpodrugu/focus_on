from aiogram.fsm.state import StatesGroup, State


class AddStudentsToTeacher(StatesGroup):
    choosing_subject = State()
    choosing_students = State()