from punq import Container, Scope

from bot.database import async_session_maker
from bot.handlers.main_teacher_handler import MainTeacherHandler
from bot.repositories.teacher_student_repo import TeacherStudentRepository
from bot.repositories.user_repository import UserRepository
from bot.repositories.subject_repository import SubjectRepository
from bot.repositories.user_subject_repo import UserSubjectRepository
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

    # Register Services
    container.register(
        UserService,
        instance=UserService(
            user_repo=container.resolve(UserRepository),
            user_subject_repo=container.resolve(UserSubjectRepository),
            teacher_student_repo=container.resolve(TeacherStudentRepository)
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

    return container