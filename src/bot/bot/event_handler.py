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
            # parse name
            name = plugin.parse_name(player)
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
            if plugin.bot_manager.is_in_list(name):
                bot = plugin.bot_manager.get_bot(name)
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
            server.logger.debug(f'Bot {name} left')
            plugin.bot_manager.get_bot(name).set_online(False)
            plugin.bot_manager.update_list()

    @staticmethod
    @event_listener(MCDRPluginEvents.PLUGIN_UNLOADED)
    def on_unload(server: PluginServerInterface):
        plugin.unload_fastapi_manager()
