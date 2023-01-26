from mcdreforged.api.command import *
from mcdreforged.api.types import PluginServerInterface


def on_load(server: PluginServerInterface, prev_module):
    server.register_command(
        Literal('!!mcdr')
        .runs(handler)
        .then(
            GreedyText('content')
            .runs(handler)
        )
    )


def handler(src, ctx):
    src.get_server().execute_command(f'!!MCDR {ctx.get("content", "")}', src)
