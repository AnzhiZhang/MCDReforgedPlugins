import minecraft_data_api
from mcdreforged.api.types import PluginServerInterface

from bot.constants import CONFIG_FILE_NAME, DIMENSION
from bot.config import Config
from bot.bot_manager import BotManager
from bot.command_handler import CommandHandler
from bot.event_handler import EventHandler
from bot.location import Location

# FastAPIManager
fastapi_error = None
try:
    from bot.fastapi_manager import FastAPIManager
except ImportError:
    FastAPIManager = None
except Exception as e:
    FastAPIManager = None
    fastapi_error = e


class Plugin:
    def __init__(self, server: PluginServerInterface, prev_module):
        self.__server = server
        self.__config = self.__server.load_config_simple(
            CONFIG_FILE_NAME,
            target_class=Config
        )
        self.__check_config()

        self.__bot_manager = BotManager(self, prev_module)
        self.__fastapi_manager = None
        self.load_fastapi_manager()
        self.__command_handler = CommandHandler(self)
        self.__event_handler = EventHandler(self)

    @property
    def plugin_id(self):
        return self.__server.get_self_metadata().id

    @property
    def server(self):
        return self.__server

    @property
    def fastapi_mcdr(self):
        return self.__server.get_plugin_instance('fastapi_mcdr')

    @property
    def minecraft_data_api(self):
        return minecraft_data_api

    @property
    def config(self):
        return self.__config

    @property
    def bot_manager(self):
        return self.__bot_manager

    @property
    def fastapi_manager(self):
        return self.__fastapi_manager

    @property
    def command_handler(self):
        return self.__command_handler

    def __check_config(self):
        # flag
        save_flag = False

        # permission
        for name, level in Config.permissions.items():
            if name not in self.__config.permissions:
                self.server.logger.warning(
                    'During checking config, '
                    'permission "{}" not found, '
                    'will add it to config.'.format(name)
                )
                self.__config.permissions[name] = level
                save_flag = True

        # save
        if save_flag:
            self.server.save_config_simple(self.__config, CONFIG_FILE_NAME)

    def load_fastapi_manager(self):
        if FastAPIManager is not None:
            self.__fastapi_manager = FastAPIManager(self)
        else:
            if fastapi_error is None:
                self.server.logger.debug(
                    "FastAPI libraries is not installed, "
                    "will not register APIs with FastAPI MCDR."
                )
            else:
                self.server.logger.warning(
                    "Failed to load FastAPI manager, "
                    "please check the error message below. "
                    "If you do not intent to use FastAPI, "
                    "you may ignore this message.",
                    exc_info=fastapi_error
                )

    def unload_fastapi_manager(self):
        if self.__fastapi_manager is not None:
            self.__fastapi_manager.unload()

    def parse_name(self, name: str) -> str:
        """
        Parse the name of the bot.
        :param name: Name of the bot.
        :return: Parsed bot name string.
        """
        # Lowercase
        name = name.lower()

        # Prefix
        if not name.startswith(self.config.name_prefix):
            name = self.config.name_prefix + name

        # Suffix
        if not name.endswith(self.config.name_suffix):
            name = name + self.config.name_suffix

        # Return
        return name

    def get_location(self, name: str) -> Location:
        """
        Get location from a player or bot.
        :param name: Name of player or bot.
        :return: A Location.
        """
        api = self.minecraft_data_api
        info = api.get_player_info(name)
        dimension = DIMENSION.INT_TRANSLATION.get(info['Dimension'])
        return Location(info['Pos'], info['Rotation'], dimension)
