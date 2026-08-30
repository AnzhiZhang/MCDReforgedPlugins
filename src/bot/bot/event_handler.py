import re
from typing import TYPE_CHECKING

from mcdreforged.api.event import MCDRPluginEvents
from mcdreforged.api.types import PluginServerInterface, Info
from mcdreforged.api.decorator import event_listener, new_thread
from mcdreforged.minecraft.rtext.style import RColor
from mcdreforged.minecraft.rtext.text import RText, RTextList

if TYPE_CHECKING:
    from bot.plugin import Plugin

plugin: 'Plugin'

CARPET_LOCAL_LOGIN = re.compile(
    r'\[(?:local(?::[^\]]*)?)\]'
)


class EventHandler:
    def __init__(self, plg: 'Plugin'):
        global plugin
        plugin = plg

    @staticmethod
    @event_listener(MCDRPluginEvents.SERVER_STARTUP)
    def on_server_startup(server: PluginServerInterface):
        for bot in plugin.bot_manager.bots.values():
            if bot.auto_login:
                bot.spawn()

    @staticmethod
    @event_listener(MCDRPluginEvents.SERVER_STOP)
    def on_server_stop(server: PluginServerInterface, server_return_code: int):
        for bot in plugin.bot_manager.bots.values():
            if bot.online or bot.spawning:
                bot.set_online(False)
        plugin.bot_manager.update_list()

    @staticmethod
    @event_listener(MCDRPluginEvents.PLAYER_JOINED)
    @new_thread('Bot joined')
    def on_player_joined(
            server: PluginServerInterface,
            player: str,
            info: Info
    ):
        # Carpet fake players use a local connection.  Requiring that marker
        # prevents a real player with a colliding configured prefix/suffix
        # from being treated as a bot while an asynchronous spawn is pending.
        is_local_login = (
            CARPET_LOCAL_LOGIN.search(info.content or '') is not None
        )
        if not is_local_login:
            return

        name = plugin.parse_name(player)
        known_bot = (
            plugin.bot_manager.get_bot(name)
            if plugin.bot_manager.is_in_list(name)
            else None
        )
        is_matching_pending = (
            known_bot is not None and
            known_bot.matches_pending_spawn(player)
        )

        # A differently named local login can normalize to the same logical
        # bot name.  Do not let it consume or overwrite an active request.
        if (
                known_bot is not None and
                known_bot.spawning and
                not is_matching_pending
        ):
            server.logger.warning(
                f'Ignored local player "{player}" while waiting for bot '
                f'"{known_bot.pending_spawn_name}"'
            )
            return

        if is_matching_pending or is_local_login:
            if name != player.lower():
                message = RText(
                    f'Warning: Bot "{player}" is not named correctly, '
                    f'it is suggested to use "{name}" as the name',
                    color=RColor.yellow
                )
                server.logger.warning(message)
                server.say(message)

            # debug log
            server.logger.debug(f'Bot {player} joined')

            # To Bot instance
            if known_bot is not None:
                bot = known_bot
            else:
                location = plugin.get_location(player)
                bot = plugin.bot_manager.new_bot(name, location)

            # Spawned handler
            bot.spawned(player)

    @staticmethod
    @event_listener(MCDRPluginEvents.PLAYER_LEFT)
    def on_player_left(server: PluginServerInterface, player: str):
        # parse name
        name = plugin.parse_name(player)

        # remove from list
        if plugin.bot_manager.is_in_list(name):
            bot = plugin.bot_manager.get_bot(name)
            if bot.online and bot.mc_name.lower() == player.lower():
                server.logger.debug(f'Bot {name} left')
                bot.set_online(False)
                plugin.bot_manager.update_list()

    @staticmethod
    @event_listener(MCDRPluginEvents.PLUGIN_UNLOADED)
    def on_unload(server: PluginServerInterface):
        plugin.unload_fastapi_manager()
