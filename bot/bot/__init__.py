from bot.main import Main

from mcdreforged.api.types import PluginServerInterface


def on_load(server: PluginServerInterface, prev_module):
    bot = Main(server)
    bot.init()
