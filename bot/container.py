from aiogram import Bot
from punq import Container, Scope

from bot.config import TG_TOKEN
from bot.database import async_session_maker
from bot.handlers.lesson_create_handler import LessonCreateHandler
from bot.handlers.lesson_view_handler import LessonViewHandler
from bot.handlers.main_teacher_handler import MainTeacherHandler
from bot.handlers.student_handler import StudentHandler
from bot.handlers.teacher_schedules_handler import TeacherSchedulesHandler
from bot.middlewares.album_middleware import AlbumMiddleware
from bot.models import Schedule
from bot.repositories.homework_repository import HomeworkRepository
from bot.repositories.lesson_repository import LessonRepository
from bot.repositories.schedule_repo import ScheduleRepository
from bot.repositories.teacher_student_repo import TeacherStudentRepository
from bot.repositories.user_repository import UserRepository
from bot.repositories.subject_repository import SubjectRepository
from bot.repositories.user_subject_repo import UserSubjectRepository
from bot.services.homework_service import HomeworkService
from bot.services.lesson_service import LessonService
from bot.services.notification_service import NotificationService
from bot.services.schedule_service import ScheduleService
from bot.services.user_service import UserService
from bot.handlers.start_handler import StartHandler


def get_container() -> Container:
    container = Container()

    # Register Factory
    container.register(
        'session_factory',
        instance=async_session_maker,
        scope=Scope.singleton
    )

    # Register Repositories
    container.register(
        UserRepository,
        instance=UserRepository(session_factory = container.resolve('session_factory')),
        scope=Scope.singleton
    )

    container.register(
        SubjectRepository,
        instance=SubjectRepository(session_factory = container.resolve('session_factory')),
        scope=Scope.singleton
    )

    container.register(
        UserSubjectRepository,
        instance=UserSubjectRepository(session_factory = container.resolve('session_factory')),
        scope = Scope.singleton
    )

    container.register(
        TeacherStudentRepository,
        instance=TeacherStudentRepository(session_factory = container.resolve('session_factory')),
        scope=Scope.singleton
    )

    container.register(
        ScheduleRepository,
        instance=ScheduleRepository(session_factory=container.resolve('session_factory')),
        scope=Scope.singleton
    )

    container.register(
        LessonRepository,
        instance=LessonRepository(session_factory=container.resolve('session_factory')),
        scope=Scope.singleton
    )

    container.register(
        HomeworkRepository,
        instance=HomeworkRepository(session_factory=container.resolve('session_factory')),
        scope=Scope.singleton
    )


    # Register Services
    container.register(
        UserService,
        instance=UserService(
            user_repo=container.resolve(UserRepository),
            user_subject_repo=container.resolve(UserSubjectRepository),
            teacher_student_repo=container.resolve(TeacherStudentRepository),
            subject_repo=container.resolve(SubjectRepository)
        ),
        scope=Scope.singleton
    )

    container.register(
        ScheduleService,
        instance=ScheduleService(
            schedule_repo=container.resolve(ScheduleRepository),
            subject_repo=container.resolve(SubjectRepository)
        ),
        scope=Scope.singleton
    )

    container.register(
        LessonService,
        instance=LessonService(
            lesson_repo=container.resolve(LessonRepository)
        ),
        scope=Scope.singleton
    )

    container.register(
        HomeworkService,
        instance=HomeworkService(
            homework_repo=container.resolve(HomeworkRepository)
        ),
        scope=Scope.singleton
    )

    container.register(
        NotificationService,
        instance=NotificationService(
            bot = Bot(token=TG_TOKEN),
            schedule_repo=container.resolve(ScheduleRepository),
            lesson_repo=container.resolve(LessonRepository)
        ),
        scope=Scope.singleton
    )

    # Register Handlers
    container.register(
        StartHandler,
        instance=StartHandler(user_service=container.resolve(UserService)),
        scope=Scope.singleton
    )

    container.register(
        MainTeacherHandler,
        instance=MainTeacherHandler(user_service=container.resolve(UserService)),
        scope=Scope.singleton
    )

    container.register(
        TeacherSchedulesHandler,
        instance=TeacherSchedulesHandler(
            schedule_service=container.resolve(ScheduleService),
            user_service=container.resolve(UserService)
        ),
        scope=Scope.singleton
    )

    container.register(
        StudentHandler,
        instance=StudentHandler(
            user_service=container.resolve(UserService),
            schedule_service = container.resolve(ScheduleService)
        ),
        scope = Scope.singleton
    )

    container.register(
        LessonCreateHandler,
        instance=LessonCreateHandler(
            lesson_service=container.resolve(LessonService),
            user_service=container.resolve(UserService),
            homework_service=container.resolve(HomeworkService)
        ),
        scope=Scope.singleton
    )

    container.register(
        LessonViewHandler,
        instance=LessonViewHandler(
            lesson_service=container.resolve(LessonService),
            user_service=container.resolve(UserService),
            homework_service=container.resolve(HomeworkService)
        ),
        scope=Scope.singleton
    )


    # Register middlewares
    container.register(
        AlbumMiddleware,
        instance=AlbumMiddleware(latency=0.2),
        scope=Scope.singleton
    )
    return container