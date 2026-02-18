import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

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

    dp.include_router(start_handler.router)

    async with bot:
        await dp.start_polling(
            bot,
            user_service=container.resolve(UserService)
        )

    logger.info('Bot have been run')

if __name__ == '__main__':
    asyncio.run(main())
