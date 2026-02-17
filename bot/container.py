from punq import Container, Scope

from bot.database import async_session_maker
from repositories.UserRepository import UserRepository
from repositories.SubjectRepository import SubjectRepository
from services.UserService import UserService
from handlers.start_handler import StartHandler

def get_container() -> Container():
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
        instance=UserRepository(session_factory=async_session_maker),
        scope=Scope.singleton
    )

    container.register(
        SubjectRepository,
        instance=SubjectRepository(session_factory=async_session_maker),
        scope=Scope.singleton
    )

    # Register Services
    container.register(
        UserService,
        instance=UserService(UserRepository(session_factory=async_session_maker)),
        scope=Scope.singleton
    )

    # Register Handlers
    container.register(
        StartHandler,
        instance=StartHandler(),
        scope=Scope.singleton
    )

    return container