from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram import F
from bot.handlers.base_handler import BaseHandler
from bot.keyboards.teacher_inline import add_students, subjects_keyboard, back_to_teacher_menu_keyboard
from bot.keyboards.teacher_inline import teacher_inline, student_by_subject_keyboard
from bot.states.add_students_to_teacher import AddStudentsToTeacher

class MainTeacherHandler(BaseHandler):
    def __init__(self, user_service):
        self.user_service = user_service
        super().__init__()

    def _register_handlers(self):


        @self.router.callback_query(F.data == 'back_to_teacher_menu')
        # Кнопка назад
        async def process_back(callback: CallbackQuery):
            teacher_tg_id = callback.from_user.id
            teacher = await self.user_service.repo.get_by_tg_id(teacher_tg_id)

            await callback.message.edit_text(
                f'<b>{teacher.name}</b> 💬\n\nВыберите действие:\n\n',
                parse_mode='HTML',
                reply_markup=await teacher_inline()
            )


        # 1. Показать всех учеников, которые есть у учителя
        @self.router.callback_query(F.data == 'show_students')
        async def get_students(callback: CallbackQuery, state : FSMContext):
            teacher_tg_id = callback.from_user.id
            teacher = await self.user_service.repo.get_by_tg_id(teacher_tg_id)
            await state.update_data(teacher_id=teacher.id)

            students_all = await self.user_service.teacher_student_repo.get_students_by_teacher(teacher.id)
            students_all_id = [student.id for student in students_all]

            students = []
            for student in students_all:
                if student not in students:
                    students.append(student)

            text = ''
            if not students:
                text = '<b>К сожалению, у вас ещё нет учеников 👨‍🎓.</b>\n\nМожет вы забыли их добавить?'


            if students:
                students_text = '\n\n'
                for student in students:
                    subject_str = ''
                    subjects = await self.user_service.teacher_student_repo.get_user_subjects_by_teacher_id(student.id, teacher.id)
                    for subject in subjects:
                        subject_str += f'{subject.name.value}, '

                    students_text += f'<b>Имя</b> 🆔: {student.name}\n<b>Класс</b> 🏫: {student.class_number}\n<b>Предмет(ы)</b> 📚: {subject_str[:-2]}\n'
                text = '<b>Ваши ученики 👨‍🎓:</b>' + f'{students_text}'

            await callback.message.edit_text(
                text,
                parse_mode='HTML',
                reply_markup=await add_students()
            )

        # 2. Выбор предмета, по которому учитель добавляет ученика
        @self.router.callback_query(F.data == 'show_subjects')
        async def show_subjects(callback: CallbackQuery, state: FSMContext):
            teacher_tg_id = callback.from_user.id
            print(teacher_tg_id)

            teacher = await self.user_service.repo.get_by_tg_id(teacher_tg_id)
            print(teacher)


            subjects = await self.user_service.user_subject_repo.get_user_subjects(teacher.id)
            print(subjects)

            await state.set_state(AddStudentsToTeacher.choosing_subject)

            await callback.message.edit_text(
                f'<b>{teacher.name}, выберите предмет, по которому хотите добавить ученика:</b>',
                parse_mode='HTML',
                reply_markup=await subjects_keyboard(subjects)
            )

            # 3. Отображение всех доступных учеников по этому предмету
            @self.router.callback_query(AddStudentsToTeacher.choosing_subject, F.data.startswith('choose_student_with_subject_'))
            async def choose_student(callback: CallbackQuery, state : FSMContext):
                subject_id = int(callback.data.replace('choose_student_with_subject_', ''))

                await state.update_data(subject_id=subject_id)
                data = await state.get_data()
                teacher_id = data.get('teacher_id')

                subject = await self.user_service.subject_repo.get_subject_by_id(subject_id)
                await state.update_data(subject=subject)

                students_all = await self.user_service.user_subject_repo.get_users_by_subject_id(subject_id)
                students_with_teacher = await self.user_service.teacher_student_repo.get_students_with_teacher_by_subject_id(subject_id)
                students_id_with_teacher = [student.id for student in students_with_teacher]

                students = [student for student in students_all if student.id not in students_id_with_teacher]

                await state.set_state(AddStudentsToTeacher.choosing_students)

                await callback.message.edit_text(
                    f'<b>Доступные ученики с выбранным вами предметом</b>:\n\n',
                    reply_markup=await student_by_subject_keyboard(students),
                    parse_mode='HTML'
                )

            @self.router.callback_query(AddStudentsToTeacher.choosing_students, F.data.startswith('student_'))
            async def process_student(callback : CallbackQuery, state : FSMContext):
                student_id = int(callback.data.replace('student_', ''))

                student = await self.user_service.repo.get_user_by_id(student_id)

                teacher_tg_id = callback.from_user.id

                teacher = await self.user_service.repo.get_by_tg_id(teacher_tg_id)

                teacher_id = teacher.id

                data = await state.get_data()
                subject_id = data['subject_id']

                await self.user_service.teacher_student_repo.set_new_link(
                    teacher_id = teacher_id,
                    student_id=student_id,
                    subject_id=subject_id
                )

                await callback.message.edit_text(
                    f"<b>✅ Вы успешно добавили ученика {student.name} на предмет {data['subject'].name.value}!</b>",
                    parse_mode='HTML',
                    reply_markup=await back_to_teacher_menu_keyboard()
                )

                await state.clear()





