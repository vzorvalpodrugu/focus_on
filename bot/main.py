import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from container import get_container
from handlers.start_handler import StartHandler

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
        await dp.start_polling(bot)

    logger.info('Bot have been run')

if __name__ == '__main__':
    asyncio.run(main())
