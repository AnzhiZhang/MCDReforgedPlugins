from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Union

from mcdreforged.api.types import ConsoleCommandSource, PlayerCommandSource
from mcdreforged.api.command import *
from mcdreforged.api.rtext import *
from mcdreforged.api.decorator import new_thread
from mcdreforged.api.utils.serializer import Serializable
from dict_command_registration import NodeType, register
from more_command_nodes import Position, Facing, EnumeratedText

from bot.exceptions import *
from bot.constants import DIMENSION
from bot.location import Location

if TYPE_CHECKING:
    from bot.plugin import Plugin

Source = Union[ConsoleCommandSource, PlayerCommandSource]


class PermissionsRequirements(Serializable):
    LIST: Callable
    SPAWN: Callable
    KILL: Callable
    ACTION: Callable
    INFO: Callable
    SAVE: Callable
    DEL: Callable
    CONFIG: Callable


class ListArguments(Enum):
    ALL = '--all'
    ONLINE = '--online'
    SAVED = '--saved'


class CommandHandler:
    def __init__(self, plugin: 'Plugin'):
        self.__plugin: 'Plugin' = plugin
        permissions = PermissionsRequirements(
            **{
                key.upper(): Requirements.has_permission(value)
                for key, value
                in self.__plugin.config.permissions.items()
            }
        )

        def bot_list(online: bool = None) -> Callable[[bool], List[str]]:
            return lambda: [
                name for name, bot in
                self.__plugin.bot_manager.bots.items()
                if online is None or bot.online == online
            ]

        # generate command tree
        command_tree = {
            'name': '!!bot',
            'runs': lambda src: src.reply(
                self.__plugin.server.rtr('bot.help.content')
            ),
            'children': [
                {
                    'name': 'list',
                    'requires': permissions.LIST,
                    'runs': self.__command_list,
                    'children': [
                        {
                            'name': 'index',
                            'type': NodeType.INTEGER,
                            'runs': self.__command_list,
                            'children': [
                                {
                                    'name': 'arg',
                                    'type': EnumeratedText,
                                    'runs': self.__command_list,
                                    'args': [ListArguments]
                                }
                            ]
                        }
                    ]
                },
                {
                    'name': 'spawn',
                    'requires': permissions.SPAWN,
                    'children': [
                        {
                            'name': 'name',
                            'type': NodeType.TEXT,
                            'runs': self.__command_spawn,
                            'suggests': bot_list(False)
                        }
                    ]
                },
                {
                    'name': 'kill',
                    'requires': permissions.KILL,
                    'children': [
                        {
                            'name': 'name',
                            'type': NodeType.TEXT,
                            'runs': self.__command_kill,
                            'suggests': bot_list(True)
                        }
                    ]
                },
                {
                    'name': 'action',
                    'requires': permissions.ACTION,
                    'children': [
                        {
                            'name': 'name',
                            'type': NodeType.TEXT,
                            'runs': self.__command_action,
                            'suggests': bot_list(True),
                            'children': [
                                {
                                    'name': 'index',
                                    'type': NodeType.INTEGER,
                                    'runs': self.__command_action
                                }
                            ]
                        }
                    ]
                },
                {
                    'name': 'info',
                    'requires': permissions.INFO,
                    'children': [
                        {
                            'name': 'name',
                            'type': NodeType.TEXT,
                            'runs': self.__command_info,
                            'suggests': bot_list()
                        }
                    ]
                },
                {
                    'name': 'save',
                    'requires': permissions.SAVE,
                    'children': [
                        {
                            'name': 'name',
                            'type': NodeType.TEXT,
                            'runs': self.__command_save,
                            'children': [
                                {
                                    'name': 'position',
                                    'type': Position,
                                    'runs': self.__command_save,
                                    'children': [
                                        {
                                            'name': 'facing',
                                            'type': Facing,
                                            'runs': self.__command_save,
                                            'children': [
                                                {
                                                    'name': 'dimension',
                                                    'type': NodeType.TEXT,
                                                    'runs': self.__command_save
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    'name': 'del',
                    'requires': permissions.DEL,
                    'children': [
                        {
                            'name': 'name',
                            'type': NodeType.TEXT,
                            'runs': self.__command_del,
                            'suggests': bot_list()
                        }
                    ]
                },
                {
                    'name': 'config',
                    'requires': permissions.CONFIG,
                    'children': [
                        {
                            'name': 'name',
                            'type': NodeType.TEXT,
                            'suggests': bot_list(),
                            'children': [
                                {
                                    'name': 'name',
                                    'children': [
                                        {
                                            'name': 'new_name',
                                            'type': NodeType.TEXT,
                                            'runs': self.__command_config_name
                                        }
                                    ]
                                },
                                {
                                    'name': 'position',
                                    'children': [
                                        {
                                            'name': 'position',
                                            'type': Position,
                                            'runs': self.__command_config_position
                                        }
                                    ]
                                },
                                {
                                    'name': 'facing',
                                    'children': [
                                        {
                                            'name': 'facing',
                                            'type': Facing,
                                            'runs': self.__command_config_facing
                                        }
                                    ]
                                },
                                {
                                    'name': 'dimension',
                                    'children': [
                                        {
                                            'name': 'dimension',
                                            'type': NodeType.TEXT,
                                            'runs': self.__command_config_dimension
                                        }
                                    ]
                                },
                                {
                                    'name': 'comment',
                                    'children': [
                                        {
                                            'name': 'comment',
                                            'type': NodeType.GREEDY_TEXT,
                                            'runs': self.__command_config_comment
                                        }
                                    ]
                                },
                                {
                                    'name': 'actions',
                                    'children': [
                                        {
                                            'name': 'append',
                                            'children': [
                                                {
                                                    'name': 'action',
                                                    'type': NodeType.GREEDY_TEXT,
                                                    'runs': self.__command_config_actions_append
                                                }
                                            ]
                                        },
                                        {
                                            'name': 'insert',
                                            'children': [
                                                {
                                                    'name': 'index',
                                                    'type': NodeType.INTEGER,
                                                    'children': [
                                                        {
                                                            'name': 'action',
                                                            'type': NodeType.GREEDY_TEXT,
                                                            'runs': self.__command_config_actions_insert
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                        {
                                            'name': 'delete',
                                            'children': [
                                                {
                                                    'name': 'index',
                                                    'type': NodeType.INTEGER,
                                                    'runs': self.__command_config_actions_delete
                                                }
                                            ]
                                        },
                                        {
                                            'name': 'edit',
                                            'children': [
                                                {
                                                    'name': 'index',
                                                    'type': NodeType.INTEGER,
                                                    'children': [
                                                        {
                                                            'name': 'action',
                                                            'type': NodeType.GREEDY_TEXT,
                                                            'runs': self.__command_config_actions_edit
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                        {
                                            'name': 'clear',
                                            'runs': self.__command_config_actions_clear
                                        }
                                    ]
                                },
                                {
                                    'name': 'autoLogin',
                                    'children': [
                                        {
                                            'name': 'autoLogin',
                                            'type': NodeType.BOOLEAN,
                                            'runs': self.__command_config_auto_login
                                        }
                                    ]
                                },
                                {
                                    'name': 'autoRunActions',
                                    'children': [
                                        {
                                            'name': 'autoRunActions',
                                            'type': NodeType.BOOLEAN,
                                            'runs': self.__command_config_auto_run_actions
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        register(
            self.__plugin.server,
            command_tree,
            RTextMCDRTranslation('bot.help.message')
            .c(RAction.run_command, '!!bot list')
            .h(RTextMCDRTranslation('bot.help.message.hover'))
        )

    def __parse_name(self, name: str) -> str:
        """
        Parse the name of the bot.
        :param name: Name of the bot.
        :return: Parsed bot name string.
        """
        # Prefix
        if not name.startswith(self.__plugin.config.name_prefix):
            name = self.__plugin.config.name_prefix + name

        # Suffix
        if not name.endswith(self.__plugin.config.name_suffix):
            name = name + self.__plugin.config.name_suffix

        # Lowercase
        name = name.lower()

        # Return
        return name

    def __command_list(self, src: Source, ctx: Dict[str, Any]):
        index = ctx.get('index', 0)
        arg = ctx.get('arg', ListArguments.ALL)
        try:
            bot_list, max_index = self.__plugin.bot_manager.list(
                index,
                arg == ListArguments.ALL or arg == ListArguments.ONLINE,
                arg == ListArguments.ALL or arg == ListArguments.SAVED
            )

            # Header
            message = RTextList('-------- List --------')

            # Body
            for bot in bot_list:
                spawn_button = (
                    RText(
                        '[↑]', color=RColor.green
                    )
                    .h(RTextMCDRTranslation('bot.list.spawnButton'))
                    .c(RAction.run_command, f'!!bot spawn {bot.name}')
                )
                kill_button = (
                    RText(
                        '[↓]', color=RColor.yellow
                    )
                    .h(RTextMCDRTranslation('bot.list.killButton'))
                    .c(RAction.run_command, f'!!bot kill {bot.name}')
                )
                action_button = (
                    RText(
                        '[▶]', color=RColor.blue
                    )
                    .h(RTextMCDRTranslation('bot.list.actionButton'))
                    .c(RAction.run_command, f'!!bot action {bot.name}')
                )
                info_button = (
                    RText(
                        '[?]', color=RColor.gray
                    )
                    .h(
                        RTextMCDRTranslation(
                            'bot.list.infoButton',
                            bot.name, bot.location.rounded_position,
                            bot.location.rounded_facing,
                            bot.location.display_dimension,
                            bot.comment, bot.actions, bot.auto_login,
                            bot.auto_run_actions
                        )
                    )
                    .c(RAction.run_command, f'!!bot info {bot.name}')
                )
                delete_button = (
                    RText(
                        '[×]', color=RColor.red
                    )
                    .h(RTextMCDRTranslation('bot.list.deleteButton'))
                    .c(RAction.run_command, f'!!bot del {bot.name}')
                )
                name = RText(
                    bot.display_name,
                    color=RColor.green if bot.online else RColor.gray
                )
                message.append(RTextList(
                    '\n',
                    spawn_button, ' ', kill_button, ' ', action_button, ' ',
                    info_button, ' ', delete_button, ' ', name
                ))

            # Index footer
            left_color = RColor.green if index != 0 else RColor.dark_gray
            right_color = (
                RColor.green
                if index != max_index
                else RColor.dark_gray
            )
            message.append(RTextList(
                '\n',
                RText('<<< ', color=left_color).c(
                    RAction.run_command, f'!!bot list {index - 1}'
                ),
                index, ' / ', max_index,
                RText(' >>>', color=right_color).c(
                    RAction.run_command, f'!!bot list {index + 1}'
                )
            ))

            # Reply
            src.reply(message)
        except IllegalListIndexException:
            src.reply(
                RTextMCDRTranslation('bot.error.illegalListIndex', index)
            )

    @new_thread('commandSpawn')
    def __command_spawn(self, src: Source, ctx: Dict[str, Any]):
        name = self.__parse_name(ctx['name'])
        try:
            self.__plugin.bot_manager.spawn(
                name,
                src.player if src.is_player else None
            )
            src.reply(RTextMCDRTranslation('bot.command.spawned', name))
        except BotNotSavedException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotSaved', e.name))
        except BotOnlineException as e:
            src.reply(RTextMCDRTranslation('bot.error.botOnline', e.name))

    def __command_kill(self, src: Source, ctx: Dict[str, Any]):
        name = ctx['name']
        try:
            self.__plugin.bot_manager.kill(name)
            src.reply(RTextMCDRTranslation('bot.command.killed', name))
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))
        except BotOfflineException as e:
            src.reply(RTextMCDRTranslation('bot.error.botOffline', e.name))

    def __command_action(self, src: Source, ctx: Dict[str, Any]):
        name = ctx['name']
        try:
            self.__plugin.bot_manager.action(
                name, ctx.get('index')
            )
            src.reply(RTextMCDRTranslation('bot.command.action', name))
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))
        except BotOfflineException as e:
            src.reply(RTextMCDRTranslation('bot.error.botOffline', e.name))
        except IllegalActionIndexException as e:
            src.reply(RTextMCDRTranslation(
                'bot.error.illegalActionIndex', e.index
            ))

    def __command_info(self, src: Source, ctx: Dict[str, Any]):
        def get_config_button(
                name: str,
                config: str,
                default_value: str
        ) -> RText:
            """
            Get a RText config button.
            :param name: Name of the bot.
            :param config: Config name.
            :param default_value: Default value of the config.
            :return: RText.
            """
            return (
                RText('[✐]', color=RColor.gray)
                .h(
                    RTextMCDRTranslation('bot.command.info.configButtonHover')
                )
                .c(
                    RAction.suggest_command,
                    f'!!bot config {name} {config} {default_value}'
                )
            )

        try:
            bot = self.__plugin.bot_manager.get_bot(ctx['name'])
            minimap_button = RTextList(
                RText('[+V]', color=RColor.aqua)
                .h(
                    RTextMCDRTranslation(
                        'bot.command.info.position.voxelButton'
                    )
                )
                .c(
                    RAction.run_command,
                    '/newWaypoint x:{}, y:{}, z:{}, dim:{}'.format(
                        int(bot.location.position[0]),
                        int(bot.location.position[1]),
                        int(bot.location.position[2]),
                        bot.location.str_dimension
                    )
                ),
                ' ',
                RText('[+X]', color=RColor.gold)
                .h(
                    RTextMCDRTranslation(
                        'bot.command.info.position.xearosButton'
                    )
                )
                .c(
                    RAction.run_command,
                    (
                        "xaero_waypoint_add:{}'s Location"
                        ":{}:{}:{}:{}:6:false:0:Internal_{}_waypoints"
                    ).format(
                        bot.name,
                        bot.name[0],
                        int(bot.location.position[0]),
                        int(bot.location.position[1]),
                        int(bot.location.position[2]),
                        bot.location.str_dimension.replace('minecraft:', '')
                    )
                )
            )
            actions_info = RTextList(
                RTextMCDRTranslation('bot.command.info.actions'), ' ',
                RText('[▶]', color=RColor.blue)
                .h(
                    RTextMCDRTranslation(
                        'bot.command.info.actions.actionButtonAll'
                    )
                )
                .c(RAction.run_command, f'!!bot action {bot.name}'), ' ',
                RText('[×]', color=RColor.red)
                .h(
                    RTextMCDRTranslation(
                        'bot.command.info.actions.clearButton'
                    )
                )
                .c(
                    RAction.run_command,
                    f'!!bot config {bot.name} actions clear'
                ),
                *[
                    RTextList(
                        '\n', '  ',
                        get_config_button(
                            bot.name, f'actions edit {index}', action
                        ), ' ',
                        RText('[▶]', color=RColor.blue)
                        .h(
                            RTextMCDRTranslation(
                                'bot.command.info.actions.actionButtonIndex',
                                index
                            )
                        )
                        .c(
                            RAction.run_command,
                            f'!!bot action {bot.name} {index}'
                        ), ' ',
                        RText('[×]', color=RColor.red)
                        .h(
                            RTextMCDRTranslation(
                                'bot.command.info.actions.deleteButton', index
                            )
                        )
                        .c(
                            RAction.run_command,
                            f'!!bot config {bot.name} actions delete {index}'
                        ), ' ',
                        f'§3{index}. {action}',
                    )
                    for index, action
                    in enumerate(bot.actions)
                ], '\n', '                ',
                RText('[+]', color=RColor.green)
                .h(
                    RTextMCDRTranslation(
                        'bot.command.info.actions.appendButton'
                    )
                )
                .c(
                    RAction.suggest_command,
                    f'!!bot config {bot.name} actions append '
                )
            )
            src.reply(RTextList(
                '----------------', '\n',
                get_config_button(
                    bot.name, 'name', bot.name
                ), ' ',
                RTextMCDRTranslation(
                    'bot.command.info.name',
                    bot.name
                ), '\n',
                get_config_button(
                    bot.name, 'position',
                    ' '.join(map(str, bot.location.position))
                ), ' ',
                RTextMCDRTranslation(
                    'bot.command.info.position',
                    bot.location.rounded_position
                ), ' ', minimap_button, '\n',
                get_config_button(
                    bot.name, 'facing',
                    ' '.join(map(str, bot.location.facing))
                ), ' ',
                RTextMCDRTranslation(
                    'bot.command.info.facing',
                    bot.location.rounded_facing
                ), '\n',
                get_config_button(
                    bot.name, 'dimension', bot.location.dimension
                ), ' ',
                RTextMCDRTranslation(
                    'bot.command.info.dimension',
                    bot.location.display_dimension
                ), '\n',
                get_config_button(
                    bot.name, 'comment', bot.comment
                ), ' ',
                RTextMCDRTranslation(
                    'bot.command.info.comment',
                    bot.comment
                ), '\n',
                get_config_button(
                    bot.name, 'actions', ''
                ), ' ',
                actions_info, '\n',
                get_config_button(
                    bot.name, 'autoLogin', bot.auto_login
                ), ' ',
                RTextMCDRTranslation(
                    'bot.command.info.autoLogin',
                    bot.auto_login
                ), '\n',
                get_config_button(
                    bot.name, 'autoRunActions', bot.auto_run_actions
                ), ' ',
                RTextMCDRTranslation(
                    'bot.command.info.autoRunActions',
                    bot.auto_run_actions
                ), '\n',
            ))
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))

    @new_thread('commandSave')
    def __command_save(self, src: Source, ctx: Dict[str, Any]):
        name = self.__parse_name(ctx['name'])
        position = ctx.get('position')
        facing = ctx.get('facing', [0.0, 0.0])
        dimension = ctx.get('dimension', '0')
        try:
            self.__plugin.bot_manager.save(
                name,
                src.player if src.is_player else None,
                Location(
                    position, facing,
                    DIMENSION.COMMAND_TRANSLATION.get(dimension)
                ) if len(ctx.keys()) > 1 else None
            )
            src.reply(RTextMCDRTranslation('bot.command.saved', name))
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))
        except IllegalDimensionException:
            src.reply(
                RTextMCDRTranslation('bot.error.illegalDimension', dimension)
            )
        except BotAlreadySavedException as e:
            src.reply(
                RTextMCDRTranslation('bot.error.botAlreadySaved', e.name)
            )

    def __command_del(self, src: Source, ctx: Dict[str, Any]):
        name = ctx['name']
        try:
            self.__plugin.bot_manager.delete(name)
            src.reply(RTextMCDRTranslation('bot.command.deleted', name))
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))
        except BotNotSavedException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotSaved', e.name))

    def __command_config_name(self, src: Source, ctx: Dict[str, Any]):
        name = ctx['name']
        new_name = self.__parse_name(ctx['new_name'])
        try:
            self.__plugin.bot_manager.get_bot(name).set_name(new_name)
            self.__plugin.bot_manager.update_list()
            self.__plugin.bot_manager.save_data()
            src.reply(
                RTextMCDRTranslation(
                    'bot.command.config', name, 'name', new_name
                )
            )
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))

    def __command_config_position(self, src: Source, ctx: Dict[str, Any]):
        name = ctx['name']
        position = ctx['position']
        try:
            bot = self.__plugin.bot_manager.get_bot(name)
            location = bot.location
            location.position = position
            bot.set_location(location)
            self.__plugin.bot_manager.save_data()
            src.reply(
                RTextMCDRTranslation(
                    'bot.command.config', name, 'position',
                    location.rounded_position
                )
            )
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))

    def __command_config_facing(self, src: Source, ctx: Dict[str, Any]):
        name = ctx['name']
        facing = ctx['facing']
        try:
            bot = self.__plugin.bot_manager.get_bot(name)
            location = bot.location
            location.facing = facing
            bot.set_location(location)
            self.__plugin.bot_manager.save_data()
            src.reply(
                RTextMCDRTranslation(
                    'bot.command.config', name, 'facing',
                    location.rounded_facing
                )
            )
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))

    def __command_config_dimension(self, src: Source, ctx: Dict[str, Any]):
        name = ctx['name']
        dimension = ctx['dimension']
        try:
            bot = self.__plugin.bot_manager.get_bot(name)
            location = bot.location
            location.dimension = DIMENSION.COMMAND_TRANSLATION.get(dimension)

            # Check dimension
            if location.dimension is None:
                raise IllegalDimensionException(dimension)

            bot.set_location(location)
            self.__plugin.bot_manager.save_data()
            src.reply(
                RTextMCDRTranslation(
                    'bot.command.config', name, 'dimension',
                    location.display_dimension
                )
            )
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))
        except IllegalDimensionException as e:
            src.reply(
                RTextMCDRTranslation('bot.error.illegalDimension', e.dimension)
            )

    def __command_config_comment(self, src: Source, ctx: Dict[str, Any]):
        name = ctx['name']
        comment = ctx['comment']
        try:
            if comment.startswith('"') and comment.endswith('"'):
                comment = comment[1:-1]
            self.__plugin.bot_manager.get_bot(name).set_comment(comment)
            self.__plugin.bot_manager.save_data()
            src.reply(
                RTextMCDRTranslation(
                    'bot.command.config', name, 'comment', comment
                )
            )
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))

    def __command_config_actions_append(
            self, src: Source, ctx: Dict[str, Any]
    ):
        name = ctx['name']
        action = ctx['action']
        try:
            bot = self.__plugin.bot_manager.get_bot(name)
            actions = bot.actions
            actions.append(action)
            bot.set_actions(actions)
            self.__plugin.bot_manager.save_data()
            src.reply(
                RTextMCDRTranslation(
                    'bot.command.config', name, 'actions', actions
                )
            )
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))

    def __command_config_actions_insert(
            self, src: Source, ctx: Dict[str, Any]
    ):
        name = ctx['name']
        index = ctx['index']
        action = ctx['action']
        try:
            bot = self.__plugin.bot_manager.get_bot(name)
            actions = bot.actions

            if not 0 <= index <= len(actions):
                raise IllegalActionIndexException(index)

            actions.insert(index, action)
            bot.set_actions(actions)
            self.__plugin.bot_manager.save_data()
            src.reply(
                RTextMCDRTranslation(
                    'bot.command.config', name, 'actions', actions
                )
            )
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))
        except IllegalActionIndexException as e:
            src.reply(RTextMCDRTranslation(
                'bot.error.illegalActionIndex', e.index
            ))

    def __command_config_actions_delete(
            self, src: Source, ctx: Dict[str, Any]
    ):
        name = ctx['name']
        index = ctx['index']
        try:
            bot = self.__plugin.bot_manager.get_bot(name)
            actions = bot.actions

            if not 0 <= index < len(actions):
                raise IllegalActionIndexException(index)

            actions.pop(index)
            bot.set_actions(actions)
            self.__plugin.bot_manager.save_data()
            src.reply(
                RTextMCDRTranslation(
                    'bot.command.config', name, 'actions', actions
                )
            )
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))
        except IllegalActionIndexException as e:
            src.reply(RTextMCDRTranslation(
                'bot.error.illegalActionIndex', e.index
            ))

    def __command_config_actions_edit(self, src: Source, ctx: Dict[str, Any]):
        name = ctx['name']
        index = ctx['index']
        action = ctx['action']
        try:
            bot = self.__plugin.bot_manager.get_bot(name)
            actions = bot.actions

            if not 0 <= index < len(actions):
                raise IllegalActionIndexException(index)

            actions[index] = action
            bot.set_actions(actions)
            self.__plugin.bot_manager.save_data()
            src.reply(
                RTextMCDRTranslation(
                    'bot.command.config', name, 'actions', actions
                )
            )
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))
        except IllegalActionIndexException as e:
            src.reply(RTextMCDRTranslation(
                'bot.error.illegalActionIndex', e.index
            ))

    def __command_config_actions_clear(self, src: Source, ctx: Dict[str, Any]):
        name = ctx['name']
        try:
            self.__plugin.bot_manager.get_bot(name).set_actions([])
            self.__plugin.bot_manager.save_data()
            src.reply(
                RTextMCDRTranslation(
                    'bot.command.config', name, 'actions', []
                )
            )
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))

    def __command_config_auto_login(self, src: Source, ctx: Dict[str, Any]):
        name = ctx['name']
        auto_login = ctx['autoLogin']
        try:
            self.__plugin.bot_manager.get_bot(name).set_auto_login(auto_login)
            self.__plugin.bot_manager.save_data()
            src.reply(
                RTextMCDRTranslation(
                    'bot.command.config', name, 'autoLogin', auto_login
                )
            )
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))

    def __command_config_auto_run_actions(
            self, src: Source, ctx: Dict[str, Any]
    ):
        name = ctx['name']
        auto_run_actions = ctx['autoRunActions']
        try:
            self.__plugin.bot_manager.get_bot(name).set_auto_run_actions(
                auto_run_actions
            )
            self.__plugin.bot_manager.save_data()
            src.reply(
                RTextMCDRTranslation(
                    'bot.command.config', name, 'autoRunActions',
                    auto_run_actions
                )
            )
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))
