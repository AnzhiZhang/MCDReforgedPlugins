# -*- coding: utf-8 -*-
from .config import Config
from .bot import Bot
from .post_server import PostServer

from mcdreforged.plugin.server_interface import ServerInterface


class Factory:
    def __init__(self):
        self.__mcdr_server = None
        self.__config = None
        self.__bot = None
        self.__post_server = None

    def injection(self, mcdr_server: ServerInterface):
        self.__mcdr_server = mcdr_server
        self.__config = Config()
        self.__bot = Bot(self)
        self.__post_server = PostServer(self)

    @property
    def mcdr_server(self) -> ServerInterface:
        return self.__mcdr_server

    @property
    def config(self):
        return self.__config

    @property
    def bot(self):
        return self.__bot

    @property
    def post_server(self):
        return self.__post_server
