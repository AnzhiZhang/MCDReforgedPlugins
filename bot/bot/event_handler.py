import re
from typing import TYPE_CHECKING

from mcdreforged.api.event import MCDRPluginEvents
from mcdreforged.api.types import PluginServerInterface, Info
from mcdreforged.api.decorator import event_listener, new_thread

if TYPE_CHECKING:
    from bot.plugin import Plugin

plugin: 'Plugin'


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
            if bot.online:
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
        if re.fullmatch(
                r'\w+\[local] logged in with entity id \d+ at \(.*\)',
                info.content
        ):
            server.logger.debug(f'Bot {player} joined')

            # Lowercase
            player = player.lower()

            # To Bot instance
            if plugin.bot_manager.is_in_list(player):
                plugin.bot_manager.get_bot(player).set_online(True)
            else:
                bot = plugin.bot_manager.new_bot(
                    player, plugin.get_location(player)
                )
                bot.set_online(True)

    @staticmethod
    @event_listener(MCDRPluginEvents.PLAYER_LEFT)
    def on_player_left(server: PluginServerInterface, player: str):
        # Lowercase
        player = player.lower()

        if plugin.bot_manager.is_in_list(player):
            server.logger.debug(f'Bot {player} left')
            plugin.bot_manager.get_bot(player).set_online(False)
            plugin.bot_manager.update_list()
