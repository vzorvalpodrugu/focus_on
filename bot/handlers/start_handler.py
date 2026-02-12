from aiogram.types import Message
from bot.handlers.base_handler import BaseHandler
from aiogram.filters import Command

class StartHandler(BaseHandler):
    def __init__(self):
        super().__init__()

    def _register_handlers(self):

        @self.router.message(Command('start'))
        async def cmd_start(message: Message):
            await message.answer(
                f'<b>Привет, {message.chat.first_name}</b>\n\n'
                'Я твой личный бот для проведения онлайн занятий!'
                'Здесь ты сможешь получать конспекты и домашнее задание после каждого урока.'
                'Приступим!',
                parse_mode='HTML'
            )
