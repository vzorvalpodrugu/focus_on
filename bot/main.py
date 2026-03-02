import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers.lesson_create_handler import LessonCreateHandler
from bot.handlers.lesson_view_handler import LessonViewHandler
from bot.handlers.main_teacher_handler import MainTeacherHandler
from bot.handlers.student_handler import StudentHandler
from bot.handlers.teacher_schedules_handler import TeacherSchedulesHandler
from bot.middlewares.album_middleware import AlbumMiddleware
from bot.services.homework_service import HomeworkService
from bot.services.lesson_service import LessonService
from bot.services.schedule_service import ScheduleService
from bot.services.user_service import UserService
from bot.container import get_container
from bot.handlers.start_handler import StartHandler
from config import TG_TOKEN

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

storage = MemoryStorage()
tg_token = TG_TOKEN

async def main():
    bot = Bot(token=tg_token)
    dp = Dispatcher(storage=storage)
    container = get_container()

    start_handler = container.resolve(StartHandler)
    teacher_handler = container.resolve(MainTeacherHandler)
    teacher_schedules_handler = container.resolve(TeacherSchedulesHandler)
    student_handler = container.resolve(StudentHandler)
    lesson_create_handler = container.resolve(LessonCreateHandler)
    album_middleware = container.resolve(AlbumMiddleware)
    lesson_view_handler = container.resolve(LessonViewHandler)

    dp.include_router(start_handler.router)
    dp.include_router(teacher_handler.router)
    dp.include_router(teacher_schedules_handler.router)
    dp.include_router(student_handler.router)
    dp.include_router(lesson_create_handler.router)
    dp.include_router(lesson_view_handler.router)
    dp.message.middleware(album_middleware)

    async with bot:
        await dp.start_polling(
            bot,
            user_service=container.resolve(UserService),
            schedule_service=container.resolve(ScheduleService),
            lesson_service=container.resolve(LessonService),
            homework_service=container.resolve(HomeworkService)
        )

    logger.info('Bot have been run')

if __name__ == '__main__':
    asyncio.run(main())
