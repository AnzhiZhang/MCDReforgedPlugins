import math
from typing import TYPE_CHECKING, Dict, List, Tuple

from mcdreforged.api.decorator import new_thread

from bot.bot import Bot
from bot.exceptions import *
from bot.location import Location
from bot.constants import DATA_FILE_NAME

if TYPE_CHECKING:
    from bot.plugin import Plugin


class BotManager:
    def __init__(self, plugin: 'Plugin', prev_module):
        self.__plugin: 'Plugin' = plugin
        self.__bots: Dict[str, Bot] = {}

        self.__load_data(prev_module)

    @property
    def bots(self) -> Dict[str, Bot]:
        return self.__bots

    @new_thread('loadBot')
    def __load_data(self, prev_module) -> None:
        # saved bots
        file_data = self.__plugin.server.load_config_simple(
            DATA_FILE_NAME,
            default_config={'botList': {}},
            echo_in_console=False
        )['botList']
        for bot_data in file_data:
            name = bot_data['name']
            self.__bots[name] = self.new_bot(
                name,
                Location.from_dict(bot_data.get('location', {
                    'position': [0.0, 0.0, 0.0],
                    'facing': [0.0, 0.0],
                    'dimension': 0
                })),
                bot_data.get('comment', ''),
                bot_data.get('actions', []),
                bot_data.get('tags', []),
                bot_data.get('autoLogin', False),
                bot_data.get('autoRunActions', False),
                bot_data.get('autoUpdate', False)
            )
            self.__bots[name].set_saved(True)

        # old bots
        if prev_module is not None:
            old_self: 'BotManager' = prev_module.plugin.bot_manager
            api = self.__plugin.minecraft_data_api
            online_list = api.get_server_player_list()[2]
            for name in online_list:
                name = self.__plugin.parse_name(name)
                if old_self.is_in_list(name):
                    self.__bots[name] = old_self.get_bot(name)
                    self.__bots[name].set_online(True)

        self.__plugin.server.logger.debug(f'Loaded {len(self.bots)} bots:')
        for i in self.__bots.values():
            self.__plugin.server.logger.debug(f'  - {i}')

    def save_data(self) -> None:
        self.__plugin.server.save_config_simple(
            {
                "botList": [
                    bot.saving_data
                    for bot in self.__bots.values()
                    if bot.saved
                ]
            },
            DATA_FILE_NAME
        )

    def update_list(self) -> None:
        """
        Remove bots that not online or saved to clean the list.
        """
        self.__bots = {
            bot.name: bot
            for bot in self.bots.values()
            if bot.online or bot.saved
        }

    def get_bots_by_tag(self, tag: str) -> List[Bot]:
        """
        Get bots by tag.
        :param tag: Tag.
        :return: A list of bots.
        """
        return [
            bot for bot in self.bots.values()
            if tag in bot.tags
        ]

    def get_bot(self, name: str) -> Bot:
        """
        Get a bot by its name.
        :param name: Name of bot.
        :return: Bot, return a new bot if not in the list.
        """
        if self.is_in_list(name):
            return self.__bots[name]
        else:
            raise BotNotExistsException(name)

    def new_bot(
            self,
            name: str,
            location: Location,
            comment: str = '',
            actions: List[str] = None,
            tags: List[str] = None,
            auto_login: bool = False,
            auto_run_actions: bool = False,
            auto_update: bool = False
    ) -> Bot:
        """
        :param name: A string, name.
        :param location: A Location.
        :param comment: A string, comment.
        :param actions: A list of string, action commands.
        :param tags: A list of string, tags.
        :param auto_login: A bool, auto login.
        :param auto_run_actions: A bool, auto run actions.
        :param auto_update: A bool, auto update location when logout.
        :return: Bot, return a new bot if not in the list.
        """
        if actions is None:
            actions = []
        if tags is None:
            tags = []

        if not self.is_in_list(name):
            self.__bots[name] = Bot(
                self.__plugin,
                name, location, comment, actions, tags,
                auto_login, auto_run_actions, auto_update
            )
            return self.__bots[name]
        else:
            raise BotAlreadyExistsException(name)

    def is_in_list(self, name: str) -> bool:
        """
        Get a bot is in the list or not.
        :param name: Name of bot.
        """
        return name in self.__bots.keys()

    def list(
            self,
            index: int,
            online: bool,
            saved: bool,
            tag: str = None
    ) -> Tuple[List[Bot], int]:
        """
        List bots with filters.
        :param index: Page index.
        :param online: Include online bots.
        :param saved: Include saved bots.
        :param tag: Tag, only include bots with this tag if not None.
        :return: A list of bots.
        """
        # Filter bots by online and saved
        bots = []
        for bot in self.bots.values():
            condition = (online and bot.online) or (saved and bot.saved)
            condition = condition and (tag is None or tag in bot.tags)
            if condition:
                bots.append(bot)

        # Check index and filter bots to page
        max_index = math.ceil(len(bots) / 10) - 1
        if max_index < 0:
            max_index = 0

        # Check index
        if not 0 <= index <= max_index:
            raise IllegalListIndexException(index)
        else:
            bot_index = index * 10
            return bots[bot_index:bot_index + 10], max_index

    def spawn(self, name: str, player: str = None) -> Bot:
        """
        Spawn a bot if bot is already in the list.
        Otherwise, create a bot at player's location.
        :param name: Name of the bot.
        :param player: Player name who runs the command.
        """
        # Get bot
        if self.is_in_list(name):
            bot = self.get_bot(name)
        else:
            if player is not None:
                bot = self.new_bot(name, self.__plugin.get_location(player))
            else:
                raise BotNotSavedException(name)

        # Spawn
        if not bot.online:
            bot.spawn()
            return bot
        else:
            raise BotOnlineException(name)

    def kill(self, name: str) -> Bot:
        """
        Kill a bot.
        :param name: Name of the bot.
        """
        if self.is_in_list(name):
            bot = self.get_bot(name)
            if bot.online:
                bot.kill()
                self.update_list()
                return bot
            else:
                raise BotOfflineException(name)
        else:
            raise BotNotExistsException(name)

    def action(self, name: str, index: int = None) -> Bot:
        """
        Run actions of a bot.
        :param name: Name of the bot.
        :param index: Index of the action.
        """
        if self.is_in_list(name):
            bot = self.get_bot(name)
            if bot.online:
                bot.run_actions(index)
                return bot
            else:
                raise BotOfflineException(name)
        else:
            raise BotNotExistsException(name)

    def save(
            self,
            name: str,
            player: str = None,
            location: Location = None
    ) -> Bot:
        """
        Save the data of a bot.
        :param name: Name of the bot.
        :param player: Player name who runs the command.
        :param location: Location of the command input.
        """

        # No location
        #   In the list -> Save
        #   Not in the list
        #     Player -> Get location and save
        #     Console -> Error
        # With location
        #   In the list -> Set location and save
        #   Not in the list -> New and save

        # Get Bot
        if location is None:
            if self.is_in_list(name):
                bot = self.get_bot(name)
            else:
                if player is not None:
                    bot = self.new_bot(
                        name,
                        self.__plugin.get_location(player)
                    )
                else:
                    raise BotNotExistsException(name)
        else:
            # Check dimension
            if location.dimension is None:
                raise IllegalDimensionException(str(location.dimension))

            if self.is_in_list(name):
                bot = self.get_bot(name)
                bot.set_location(location)
            else:
                bot = self.new_bot(name, location)

        # Save
        if not bot.saved:
            bot.set_saved(True)
            self.save_data()
            return bot
        else:
            raise BotAlreadySavedException(name)

    def delete(self, name: str) -> Bot:
        """
        Delete a saved bot.
        :param name: Name of the bot.
        """
        # Get Bot
        if self.is_in_list(name):
            bot = self.get_bot(name)
        else:
            raise BotNotExistsException(name)

        # Delete
        if bot.saved:
            bot.set_saved(False)
            self.update_list()
            self.save_data()
            return bot
        else:
            raise BotNotSavedException(name)
