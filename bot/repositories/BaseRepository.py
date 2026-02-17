from bot.database import async_session_maker

class BaseRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

