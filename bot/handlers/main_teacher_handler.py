from aiogram.types import CallbackQuery
from aiogram import F
from bot.handlers.base_handler import BaseHandler
from bot.keyboards.teacher_inline import add_students
from bot.keyboards.teacher_inline import teacher_inline

class MainTeacherHandler(BaseHandler):
    def __init__(self, user_service):
        self.user_service = user_service
        super().__init__()

    def _register_handlers(self):
        @self.router.callback_query(F.data == 'back_to_teacher_menu')
        async def back_to_teacher_menu(callback: CallbackQuery):
            teacher_tg_id = callback.from_user.id
            teacher = await self.user_service.repo.get_by_tg_id(teacher_tg_id)

            await callback.message.edit_text(
                f'<b>{teacher.name}</b>, выберите действие:\n\n',
                parse_mode='HTML',
                reply_markup=await teacher_inline()
            )

        @self.router.callback_query(F.data == 'show_students')
        async def get_students(callback: CallbackQuery):
            teacher_tg_id = callback.from_user.id

            teacher = await self.user_service.repo.get_by_tg_id(teacher_tg_id)
            students = await self.user_service.teacher_student_repo.get_students_by_teacher(teacher.id)

            text = ''
            if not students:
                text = '<b>К сожалению, у вас ещё нет учеников 👨‍🎓.</b>\n\nМожет вы забыли их добавить?'

            if students:
                text = '<b>Ваши ученики 👨‍🎓:</b>'

            await callback.message.edit_text(
                text,
                parse_mode='HTML',
                reply_markup=await add_students()
            )




