from punq import Container, Scope

from bot.database import async_session_maker
from bot.handlers.LessonHandler import LessonHandler
from bot.handlers.main_teacher_handler import MainTeacherHandler
from bot.handlers.student_handler import StudentHandler
from bot.handlers.teacher_schedules_handler import TeacherSchedulesHandler
from bot.models import Schedule
from bot.repositories.lesson_repository import LessonRepository
from bot.repositories.schedule_repo import ScheduleRepository
from bot.repositories.teacher_student_repo import TeacherStudentRepository
from bot.repositories.user_repository import UserRepository
from bot.repositories.subject_repository import SubjectRepository
from bot.repositories.user_subject_repo import UserSubjectRepository
from bot.services.lesson_service import LessonService
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
        LessonHandler,
        instance=LessonHandler(
            lesson_service=container.resolve(LessonService),
            user_service=container.resolve(UserService)
        ),
        scope=Scope.singleton
    )

    return container