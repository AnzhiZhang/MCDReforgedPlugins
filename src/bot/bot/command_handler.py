from enum import Enum
from typing import TYPE_CHECKING, List, Set, Callable

from mcdreforged.api.types import CommandSource
from mcdreforged.api.command import *
from mcdreforged.api.rtext import *
from mcdreforged.api.decorator import new_thread
from mcdreforged.api.utils.serializer import Serializable
from more_command_nodes import Position, Facing, EnumeratedText

from bot.exceptions import *
from bot.constants import DIMENSION
from bot.location import Location

if TYPE_CHECKING:
    from bot.plugin import Plugin


class PermissionsRequirements(Serializable):
    LIST: Callable
    SPAWN: Callable
    KILL: Callable
    ACTION: Callable
    TAGS: Callable
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

        def bot_list(online: bool = None) -> Callable[[], List[str]]:
            return lambda: [
                name for name, bot in
                self.__plugin.bot_manager.bots.items()
                if online is None or bot.online == online
            ]

        list_literal = (
            Literal('list')
            .requires(permissions.LIST)
            .runs(self.__command_list)
            .then(
                Integer('index')
                .runs(self.__command_list)
                .then(
                    EnumeratedText('arg', ListArguments)
                    .runs(self.__command_list)
                )
            )
        )
        spawn_literal = (
            Literal('spawn')
            .requires(permissions.SPAWN)
            .then(
                Text('name')
                .runs(self.__command_spawn)
                .suggests(bot_list(False))
            )
        )
        kill_literal = (
            Literal('kill')
            .requires(permissions.KILL)
            .then(
                Text('name')
                .runs(self.__command_kill)
                .suggests(bot_list(True))
            )
        )
        action_literal = (
            Literal('action')
            .requires(permissions.ACTION)
            .then(
                Text('name')
                .runs(self.__command_action)
                .suggests(bot_list(True))
                .then(
                    Integer('index')
                    .runs(self.__command_action)
                )
            )
        )
        tags_literal = (
            Literal('tags')
            .requires(permissions.TAGS)
            .runs(self.__command_tag_list)
            .then(
                Text('tag')
                .suggests(self.tag_list)
                .then(
                    Literal('spawn')
                    .runs(self.__command_tag_spawn)
                )
                .then(
                    Literal('kill')
                    .runs(self.__command_tag_kill)
                )
            )
        )
        info_literal = (
            Literal('info')
            .requires(permissions.INFO)
            .then(
                Text('name')
                .runs(self.__command_info)
                .suggests(bot_list())
            )
        )
        save_literal = (
            Literal('save')
            .requires(permissions.SAVE)
            .then(
                Text('name')
                .runs(self.__command_save)
                .then(
                    Position('position')
                    .runs(self.__command_save)
                    .then(
                        Facing('facing')
                        .runs(self.__command_save)
                        .then(
                            Text('dimension')
                            .runs(self.__command_save)
                        )
                    )
                )
            )
        )
        del_literal = (
            Literal('del')
            .requires(permissions.DEL)
            .then(
                Text('name')
                .runs(self.__command_del)
                .suggests(bot_list())
            )
        )
        config_literal = (
            Literal('config')
            .requires(permissions.CONFIG)
            .then(
                Text('name')
                .suggests(bot_list())
                .then(
                    Literal('name')
                    .then(
                        Text('newName')
                        .runs(self.__command_config_name)
                    )
                )
                .then(
                    Literal('position')
                    .then(
                        Position('position')
                        .runs(self.__command_config_position)
                    )
                )
                .then(
                    Literal('facing')
                    .then(
                        Facing('facing')
                        .runs(self.__command_config_facing)
                    )
                )
                .then(
                    Literal('dimension')
                    .then(
                        Text('dimension')
                        .runs(self.__command_config_dimension)
                    )
                )
                .then(
                    Literal('comment')
                    .then(
                        GreedyText('comment')
                        .runs(self.__command_config_comment)
                    )
                )
                .then(
                    Literal('actions')
                    .then(
                        Literal('append')
                        .then(
                            GreedyText('action')
                            .runs(self.__command_config_actions_append)
                        )
                    )
                    .then(
                        Literal('insert')
                        .then(
                            Integer('index')
                            .then(
                                GreedyText('action')
                                .runs(self.__command_config_actions_insert)
                            )
                        )
                    )
                    .then(
                        Literal('delete')
                        .then(
                            Integer('index')
                            .runs(self.__command_config_actions_delete)
                        )
                    )
                    .then(
                        Literal('edit')
                        .then(
                            Integer('index')
                            .then(
                                GreedyText('action')
                                .runs(self.__command_config_actions_edit)
                            )
                        )
                    )
                    .then(
                        Literal('clear')
                        .runs(self.__command_config_actions_clear)
                    )
                )
                .then(
                    Literal('tags')
                    .then(
                        Literal('append')
                        .then(
                            Text('tag')
                            .runs(self.__command_config_tags_append)
                        )
                    )
                    .then(
                        Literal('insert')
                        .then(
                            Integer('index')
                            .then(
                                Text('tag')
                                .runs(self.__command_config_tags_insert)
                            )
                        )
                    )
                    .then(
                        Literal('delete')
                        .then(
                            Integer('index')
                            .runs(self.__command_config_tags_delete)
                        )
                    )
                    .then(
                        Literal('edit')
                        .then(
                            Integer('index')
                            .then(
                                Text('tag')
                                .runs(self.__command_config_tags_edit)
                            )
                        )
                    )
                    .then(
                        Literal('clear')
                        .runs(self.__command_config_tags_clear)
                    )
                )
                .then(
                    Literal('autoLogin')
                    .then(
                        Boolean('autoLogin')
                        .runs(self.__command_config_auto_login)
                    )
                )
                .then(
                    Literal('autoRunActions')
                    .then(
                        Boolean('autoRunActions')
                        .runs(self.__command_config_auto_run_actions)
                    )
                )
                .then(
                    Literal('autoUpdate')
                    .then(
                        Boolean('autoUpdate')
                        .runs(self.__command_config_auto_update)
                    )
                )
            )
        )
        self.__plugin.server.register_help_message(
            '!!bot',
            RTextMCDRTranslation('bot.help.message')
            .c(RAction.run_command, '!!bot list')
            .h(RTextMCDRTranslation('bot.help.message.hover'))
        )
        self.__plugin.server.register_command(
            Literal('!!bot')
            .runs(
                lambda src: src.reply(
                    self.__plugin.server.rtr('bot.help.content')
                )
            )
            .then(list_literal)
            .then(spawn_literal)
            .then(kill_literal)
            .then(action_literal)
            .then(tags_literal)
            .then(info_literal)
            .then(save_literal)
            .then(del_literal)
            .then(config_literal)
        )

    def tag_list(self) -> Set[str]:
        tags = []
        for bot in self.__plugin.bot_manager.bots.values():
            tags += bot.tags
        return set(tags)

    def parse_name(self, name: str) -> str:
        """
        Parse the name of the bot.
        :param name: Name of the bot.
        :return: Parsed bot name string.
        """
        # Lowercase
        name = name.lower()

        # Prefix
        if not name.startswith(self.__plugin.config.name_prefix):
            name = self.__plugin.config.name_prefix + name

        # Suffix
        if not name.endswith(self.__plugin.config.name_suffix):
            name = name + self.__plugin.config.name_suffix

        # Return
        return name

    def __command_list(self, src: CommandSource, ctx: CommandContext):
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
                            bot.comment, bot.actions, bot.tags,
                            bot.auto_login, bot.auto_run_actions,
                            bot.auto_update
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
    def __command_spawn(self, src: CommandSource, ctx: CommandContext):
        name = self.parse_name(ctx['name'])
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

    def __command_kill(self, src: CommandSource, ctx: CommandContext):
        name = self.parse_name(ctx['name'])
        try:
            self.__plugin.bot_manager.kill(name)
            src.reply(RTextMCDRTranslation('bot.command.killed', name))
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))
        except BotOfflineException as e:
            src.reply(RTextMCDRTranslation('bot.error.botOffline', e.name))

    def __command_action(self, src: CommandSource, ctx: CommandContext):
        name = self.parse_name(ctx['name'])
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

    def __command_tag_list(self, src: CommandSource):
        src.reply(RTextMCDRTranslation(
            'bot.command.tag.list',
            list(self.tag_list())
        ))

    def __command_tag_spawn(self, src: CommandSource, ctx: CommandContext):
        tag = ctx['tag']
        try:
            # check tag exists
            if tag not in self.tag_list():
                raise TagNotExistsException(tag)

            # spawn
            counter = 0
            for bot in self.__plugin.bot_manager.get_bots_by_tag(tag):
                if not bot.online:
                    bot.spawn()
                    counter += 1

            # reply
            src.reply(RTextMCDRTranslation(
                'bot.command.tag.spawn', counter, tag
            ))
        except TagNotExistsException:
            src.reply(RTextMCDRTranslation('bot.error.tagNotExists', tag))

    def __command_tag_kill(self, src: CommandSource, ctx: CommandContext):
        tag = ctx['tag']
        try:
            # check tag exists
            if tag not in self.tag_list():
                raise TagNotExistsException(tag)

            # spawn
            counter = 0
            for bot in self.__plugin.bot_manager.get_bots_by_tag(tag):
                if bot.online:
                    bot.kill()
                    counter += 1

            # reply
            src.reply(RTextMCDRTranslation(
                'bot.command.tag.kill', counter, tag
            ))
        except TagNotExistsException:
            src.reply(RTextMCDRTranslation('bot.error.tagNotExists', tag))

    def __command_info(self, src: CommandSource, ctx: CommandContext):
        name = self.parse_name(ctx['name'])

        def get_config_button(
                bot_name: str,
                config: str,
                default_value: str = None
        ) -> RText:
            """
            Get a RText config button.
            :param bot_name: Name of the bot.
            :param config: Config name.
            :param default_value: Default value of the config.
            :return: RText.
            """
            if default_value is None:
                default_value = ''

            return (
                RText('[✐]', color=RColor.gray)
                .h(
                    RTextMCDRTranslation('bot.command.info.configButtonHover')
                )
                .c(
                    RAction.suggest_command,
                    f'!!bot config {bot_name} {config} {default_value}'
                )
            )

        try:
            bot = self.__plugin.bot_manager.get_bot(name)
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
            tags_info = RTextList(
                RTextMCDRTranslation('bot.command.info.tags'), ' ',
                RText('[×]', color=RColor.red)
                .h(
                    RTextMCDRTranslation(
                        'bot.command.info.tags.clearButton'
                    )
                )
                .c(
                    RAction.run_command,
                    f'!!bot config {bot.name} tags clear'
                ),
                *[
                    RTextList(
                        '\n', '  ',
                        get_config_button(
                            bot.name, f'tags edit {index}', tag
                        ), ' ',
                        RText('[×]', color=RColor.red)
                        .h(
                            RTextMCDRTranslation(
                                'bot.command.info.tags.deleteButton', index
                            )
                        )
                        .c(
                            RAction.run_command,
                            f'!!bot config {bot.name} tags delete {index}'
                        ), ' ',
                        f'§3{index}. {tag}',
                    )
                    for index, tag
                    in enumerate(bot.tags)
                ], '\n', '                ',
                RText('[+]', color=RColor.green)
                .h(
                    RTextMCDRTranslation(
                        'bot.command.info.tags.appendButton'
                    )
                )
                .c(
                    RAction.suggest_command,
                    f'!!bot config {bot.name} tags append '
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
                    bot.name, 'actions'
                ), ' ',
                actions_info, '\n',
                get_config_button(
                    bot.name, 'tags'
                ), ' ',
                tags_info, '\n',
                get_config_button(
                    bot.name, 'autoLogin'
                ), ' ',
                RTextMCDRTranslation(
                    'bot.command.info.autoLogin',
                    bot.auto_login
                ), '\n',
                get_config_button(
                    bot.name, 'autoRunActions'
                ), ' ',
                RTextMCDRTranslation(
                    'bot.command.info.autoRunActions',
                    bot.auto_run_actions
                ), '\n',
                get_config_button(
                    bot.name, 'autoUpdate'
                ), ' ',
                RTextMCDRTranslation(
                    'bot.command.info.autoUpdate',
                    bot.auto_update
                ), '\n',
            ))
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))

    @new_thread('commandSave')
    def __command_save(self, src: CommandSource, ctx: CommandContext):
        name = self.parse_name(ctx['name'])
        position = ctx.get('position')
        facing = ctx.get('facing', [0.0, 0.0])
        dimension = ctx.get('dimension', '0')
        try:
            self.__plugin.bot_manager.save(
                name,
                src.player if src.is_player else None,
                Location(
                    position, facing,
                    DIMENSION.INT_TRANSLATION.get(dimension)
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

    def __command_del(self, src: CommandSource, ctx: CommandContext):
        name = self.parse_name(ctx['name'])
        try:
            self.__plugin.bot_manager.delete(name)
            src.reply(RTextMCDRTranslation('bot.command.deleted', name))
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))
        except BotNotSavedException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotSaved', e.name))

    def __command_config_name(self, src: CommandSource, ctx: CommandContext):
        name = self.parse_name(ctx['name'])
        new_name = self.parse_name(ctx['newName'])
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

    def __command_config_position(
            self, src: CommandSource, ctx: CommandContext
    ):
        name = self.parse_name(ctx['name'])
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

    def __command_config_facing(self, src: CommandSource, ctx: CommandContext):
        name = self.parse_name(ctx['name'])
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

    def __command_config_dimension(
            self, src: CommandSource, ctx: CommandContext
    ):
        name = self.parse_name(ctx['name'])
        dimension = ctx['dimension']
        try:
            bot = self.__plugin.bot_manager.get_bot(name)
            location = bot.location
            location.dimension = DIMENSION.INT_TRANSLATION.get(dimension)

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

    def __command_config_comment(
            self, src: CommandSource, ctx: CommandContext
    ):
        name = self.parse_name(ctx['name'])
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
            self, src: CommandSource, ctx: CommandContext
    ):
        name = self.parse_name(ctx['name'])
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
            self, src: CommandSource, ctx: CommandContext
    ):
        name = self.parse_name(ctx['name'])
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
            self, src: CommandSource, ctx: CommandContext
    ):
        name = self.parse_name(ctx['name'])
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

    def __command_config_actions_edit(
            self, src: CommandSource, ctx: CommandContext
    ):
        name = self.parse_name(ctx['name'])
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

    def __command_config_actions_clear(
            self, src: CommandSource, ctx: CommandContext
    ):
        name = self.parse_name(ctx['name'])
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

    def __command_config_tags_append(
            self, src: CommandSource, ctx: CommandContext
    ):
        name = self.parse_name(ctx['name'])
        tag = ctx['tag']
        try:
            bot = self.__plugin.bot_manager.get_bot(name)
            tags = bot.tags
            tags.append(tag)
            bot.set_tags(tags)
            self.__plugin.bot_manager.save_data()
            src.reply(
                RTextMCDRTranslation(
                    'bot.command.config', name, 'tags', tags
                )
            )
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))

    def __command_config_tags_insert(
            self, src: CommandSource, ctx: CommandContext
    ):
        name = self.parse_name(ctx['name'])
        index = ctx['index']
        tag = ctx['tag']
        try:
            bot = self.__plugin.bot_manager.get_bot(name)
            tags = bot.tags

            if not 0 <= index <= len(tags):
                raise IllegalTagIndexException(index)

            tags.insert(index, tag)
            bot.set_tags(tags)
            self.__plugin.bot_manager.save_data()
            src.reply(
                RTextMCDRTranslation(
                    'bot.command.config', name, 'tags', tags
                )
            )
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))
        except IllegalTagIndexException as e:
            src.reply(RTextMCDRTranslation(
                'bot.error.illegalTagIndex', e.index
            ))

    def __command_config_tags_delete(
            self, src: CommandSource, ctx: CommandContext
    ):
        name = self.parse_name(ctx['name'])
        index = ctx['index']
        try:
            bot = self.__plugin.bot_manager.get_bot(name)
            tags = bot.tags

            if not 0 <= index < len(tags):
                raise IllegalTagIndexException(index)

            tags.pop(index)
            bot.set_tags(tags)
            self.__plugin.bot_manager.save_data()
            src.reply(
                RTextMCDRTranslation(
                    'bot.command.config', name, 'tags', tags
                )
            )
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))
        except IllegalTagIndexException as e:
            src.reply(RTextMCDRTranslation(
                'bot.error.illegalTagIndex', e.index
            ))

    def __command_config_tags_edit(
            self, src: CommandSource, ctx: CommandContext
    ):
        name = self.parse_name(ctx['name'])
        index = ctx['index']
        tag = ctx['tag']
        try:
            bot = self.__plugin.bot_manager.get_bot(name)
            tags = bot.tags

            if not 0 <= index < len(tags):
                raise IllegalTagIndexException(index)

            tags[index] = tag
            bot.set_tags(tags)
            self.__plugin.bot_manager.save_data()
            src.reply(
                RTextMCDRTranslation(
                    'bot.command.config', name, 'tags', tags
                )
            )
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))
        except IllegalTagIndexException as e:
            src.reply(RTextMCDRTranslation(
                'bot.error.illegalTagIndex', e.index
            ))

    def __command_config_tags_clear(
            self, src: CommandSource, ctx: CommandContext
    ):
        name = self.parse_name(ctx['name'])
        try:
            self.__plugin.bot_manager.get_bot(name).set_tags([])
            self.__plugin.bot_manager.save_data()
            src.reply(
                RTextMCDRTranslation(
                    'bot.command.config', name, 'tags', []
                )
            )
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))

    def __command_config_auto_login(
            self, src: CommandSource, ctx: CommandContext
    ):
        name = self.parse_name(ctx['name'])
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
            self, src: CommandSource, ctx: CommandContext
    ):
        name = self.parse_name(ctx['name'])
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

    def __command_config_auto_update(
            self, src: CommandSource, ctx: CommandContext
    ):
        name = self.parse_name(ctx['name'])
        auto_update = ctx['autoUpdate']
        try:
            self.__plugin.bot_manager.get_bot(name).set_auto_update(
                auto_update
            )
            self.__plugin.bot_manager.save_data()
            src.reply(
                RTextMCDRTranslation(
                    'bot.command.config', name, 'autoUpdate',
                    auto_update
                )
            )
        except BotNotExistsException as e:
            src.reply(RTextMCDRTranslation('bot.error.botNotExists', e.name))
