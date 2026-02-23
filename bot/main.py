import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers.main_teacher_handler import MainTeacherHandler
from bot.handlers.teacher_schedules_handler import TeacherSchedulesHandler
from bot.services.schedule_service import ScheduleService
from bot.services.user_service import UserService
from bot.container import get_container
from bot.handlers.start_handler import StartHandler

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

storage = MemoryStorage()
tg_token = os.getenv('TG_TOKEN')

async def main():
    bot = Bot(token=tg_token)
    dp = Dispatcher(storage=storage)
    container = get_container()

    start_handler = container.resolve(StartHandler)
    teacher_handler = container.resolve(MainTeacherHandler)
    teacher_schedules_handler = container.resolve(TeacherSchedulesHandler)

    dp.include_router(start_handler.router)
    dp.include_router(teacher_handler.router)
    dp.include_router(teacher_schedules_handler.router)

    async with bot:
        await dp.start_polling(
            bot,
            user_service=container.resolve(UserService),
            schedule_service=container.resolve(ScheduleService)
        )

    logger.info('Bot have been run')

if __name__ == '__main__':
    asyncio.run(main())
