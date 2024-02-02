from bot.plugin import Plugin

plugin: Plugin


def on_load(server, prev_module):
    global plugin
    plugin = Plugin(server, prev_module)
