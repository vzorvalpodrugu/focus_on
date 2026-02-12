from abc import ABC
from aiogram import Router

class BaseHandler(ABC):
    def __init__(self):
        self.router = Router()
        self._register_handlers()

    def _register_handlers(self):
        pass