from punq import Container, Scope
from handlers.start_handler import StartHandler
def get_container() -> Container():
    container = Container()

    container.register(
        StartHandler,
        instance=StartHandler(),
        scope=Scope.singleton
    )

    return container