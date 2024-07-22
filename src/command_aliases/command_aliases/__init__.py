from mcdreforged.api.command import *
from mcdreforged.api.types import PluginServerInterface
from mcdreforged.api.utils.serializer import Serializable


class Config(Serializable):
    alias: dict[str, str] = {}


def on_load(server: PluginServerInterface, prev_module):
    config = server.load_config_simple(target_class=Config)

    for alias, command in config.alias.items():
        server.register_command(
            Literal(alias)
            .runs(get_handler(command))
            .then(
                GreedyText('content')
                .runs(get_handler(command))
            )
        )


def get_handler(command):
    def handler(src, ctx):
        src.get_server().execute_command(
            f'{command} {ctx.get("content", "")}',
            src
        )

    return handler
