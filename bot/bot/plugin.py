from mcdreforged.api.types import PluginServerInterface

from bot.constants import CONFIG_FILE_NAME
from bot.config import Config
from bot.bot_manager import BotManager
from bot.command_handler import CommandHandler
from bot.event_handler import EventHandler
from bot.location import Location


class Plugin:
    def __init__(self, server: PluginServerInterface, prev_module):
        self.__server = server
        self.__minecraft_data_api = self.__server.get_plugin_instance(
            'minecraft_data_api'
        )
        self.__config = self.__server.load_config_simple(
            CONFIG_FILE_NAME,
            target_class=Config
        )

        self.__bot_manager = BotManager(self, prev_module)
        self.__command_handler = CommandHandler(self)
        self.__event_handler = EventHandler(self)

    @property
    def server(self):
        return self.__server

    @property
    def minecraft_data_api(self):
        return self.__minecraft_data_api

    @property
    def config(self):
        return self.__config

    @property
    def bot_manager(self):
        return self.__bot_manager

    @property
    def command_handler(self):
        return self.__command_handler

    def get_location(self, name: str) -> Location:
        """
        Get location from a player or bot.
        :param name: Name of player or bot.
        :return: A Location.
        """
        api = self.minecraft_data_api
        info = api.get_player_info(name)
        dimension = api.get_player_dimension(name)
        return Location(info['Pos'], info['Rotation'], dimension)
