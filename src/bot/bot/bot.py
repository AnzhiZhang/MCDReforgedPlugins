from typing import TYPE_CHECKING, List, Dict, Any

from mcdreforged.api.decorator import new_thread

from bot.exceptions import *
from bot.location import Location

if TYPE_CHECKING:
    from bot.plugin import Plugin


class Bot:
    def __init__(
            self,
            plugin: 'Plugin',
            name: str,
            location: Location,
            comment: str,
            actions: List[str],
            tags: List[str],
            auto_login: bool,
            auto_run_actions: bool,
            auto_update: bool
    ):
        """
        :param plugin: Plugin.
        :param name: A string, name.
        :param location: A Location.
        :param comment: A string, comment.
        :param actions: A list of string, action commands.
        :param tags: A list of string, tags.
        :param auto_login: A bool, auto login.
        :param auto_run_actions: A bool, auto run actions.
        :param auto_update: A bool, auto update location when logout.
        """
        self.__plugin: 'Plugin' = plugin
        self.__server = plugin.server
        self.__name = name
        self.__location = location
        self.__comment = comment
        self.__actions = actions
        self.__tags = tags
        self.__auto_login = auto_login
        self.__auto_run_actions = auto_run_actions
        self.__auto_update = auto_update

        self.__mc_name: str = ''
        self.__online: bool = False
        self.__saved: bool = False

    @property
    def name(self):
        return self.__name

    @property
    def display_name(self):
        return self.name if self.comment == '' else self.comment

    @property
    def location(self):
        return self.__location

    @property
    def comment(self):
        return self.__comment

    @property
    def actions(self):
        return self.__actions

    @property
    def tags(self):
        return self.__tags

    @property
    def auto_login(self):
        return self.__auto_login

    @property
    def auto_run_actions(self):
        return self.__auto_run_actions

    @property
    def auto_update(self):
        return self.__auto_update

    @property
    def mc_name(self):
        return self.__mc_name

    @property
    def online(self):
        return self.__online

    @property
    def saved(self):
        return self.__saved

    @property
    def saving_data(self) -> Dict[str, Any]:
        """
        Get data used to save to file.
        :return: A dict.
        """
        return {
            'name': self.name,
            'location': {
                'position': self.location.position,
                'facing': self.location.facing,
                'dimension': self.location.dimension,
            },
            'comment': self.comment,
            'actions': self.actions,
            'tags': self.tags,
            'autoLogin': self.auto_login,
            'autoRunActions': self.auto_run_actions,
            'autoUpdate': self.auto_update,
        }

    def set_name(self, name: str) -> None:
        """
        Set name.
        :param name: Name.
        """
        self.__name = name

    def set_location(self, location: Location) -> None:
        """
        Set location.
        :param location: Location.
        """
        self.__location = location

    def set_comment(self, comment: str) -> None:
        """
        Set comment.
        :param comment: Comment.
        """
        self.__comment = comment

    def set_actions(self, actions: List[str]) -> None:
        """
        Set actions.
        :param actions: Actions.
        """
        self.__actions = actions

    def set_tags(self, tags: List[str]) -> None:
        """
        Set tags.
        :param tags: Tags.
        """
        self.__tags = tags

    def set_auto_login(self, auto_login: bool) -> None:
        """
        Set auto login.
        :param auto_login: Auto login.
        """
        self.__auto_login = auto_login

    def set_auto_run_actions(self, auto_run_actions: bool) -> None:
        """
        Set auto run actions.
        :param auto_run_actions: Auto run actions.
        """
        self.__auto_run_actions = auto_run_actions

    def set_auto_update(self, auto_update: bool) -> None:
        """
        Set auto update.
        :param auto_update: Auto update.
        """
        self.__auto_update = auto_update

    def set_online(self, online: bool) -> None:
        """
        Set online status.
        :param online: A bool.
        """
        self.__online = online

    def set_saved(self, saved: bool) -> None:
        """
        Set saved status.
        :param saved: A bool.
        """
        self.__saved = saved

    def spawn(self) -> None:
        """
        Spawn the bot.
        """
        if not self.__online:
            self.__server.execute(
                'player {} spawn at {} facing {} in {}'.format(
                    self.name,
                    ' '.join(map(str, self.location.position)),
                    ' '.join(map(str, self.location.facing)),
                    self.location.str_dimension
                )
            )
        else:
            raise BotOnlineException(self.name)

    def spawned(self, mc_name: str) -> None:
        """
        Handler when bot spawned.
        """
        # set mc name
        self.__mc_name = mc_name

        # update online status
        self.set_online(True)

        # set gamemode
        if self.saved or self.__plugin.config.force_gamemode:
            self.__server.execute(
                f'gamemode {self.__plugin.config.gamemode} {self.mc_name}'
            )

        # auto run actions
        if self.auto_run_actions:
            self.run_actions()

    @new_thread('killBot')
    def kill(self) -> None:
        """
        Kill the bot.
        """
        if self.__online:
            # auto update location
            if self.auto_update:
                self.set_location(self.__plugin.get_location(self.mc_name))
                self.__plugin.bot_manager.save_data()

            # kill
            self.set_online(False)
            self.__server.execute(f'player {self.mc_name} kill')
        else:
            raise BotOfflineException(self.name)

    def run_actions(self, index: int = None) -> None:
        """
        :param index: Index of action. Run all actions if it's None.
        Run actions.
        """
        # Get run actions.
        run_actions = []
        if index is None:
            run_actions = self.actions
        elif isinstance(index, int):
            if 0 <= index < len(self.actions):
                run_actions = [self.actions[index]]
            else:
                raise IllegalActionIndexException(index)

        # Run actions
        for action in run_actions:
            self.__server.execute(f'player {self.mc_name} {action}')

    def __str__(self):
        return (
                self.__class__.__name__ +
                dict(**self.saving_data, **{
                    'online': self.online,
                    'saved': self.saved
                }).__str__()
        )

    def __repr__(self):
        return self.__str__()
