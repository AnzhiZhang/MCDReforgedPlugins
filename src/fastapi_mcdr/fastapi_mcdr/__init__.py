import time
from asyncio import AbstractEventLoop, new_event_loop

from fastapi import FastAPI
from uvicorn import Config, Server
from starlette.routing import Mount
from mcdreforged.api.command import *
from mcdreforged.api.event import LiteralEvent
from mcdreforged.api.decorator import new_thread
from mcdreforged.api.types import PluginServerInterface, CommandSource
from mcdreforged.api.utils.serializer import Serializable

__app: FastAPI
__is_ready: bool = False
__mcdr_server: PluginServerInterface
__uvicorn_server: Server
__event_loop: AbstractEventLoop

__all__ = [
    "is_ready",
    "mount",
    "unmount",
    "COLLECT_EVENT",
]

COLLECT_EVENT = LiteralEvent("fastapi_mcdr.collect")


class PluginConfig(Serializable):
    host: str = "0.0.0.0"
    port: int = 8080


@new_thread("FastAPI")
def fastapi_main_thread(host: str, port: int):
    global __app, __uvicorn_server, __event_loop
    # init app and event loop
    __app = FastAPI()
    __event_loop = new_event_loop()

    # init uvicorn server
    __uvicorn_server = Server(Config(
        __app,
        host=host,
        port=port,
        loop="none",
        log_level="critical"
    ))

    # dispatch event to allow other plugins to add api routes
    __mcdr_server.dispatch_event(COLLECT_EVENT, ())

    # start uvicorn server
    __event_loop.run_until_complete(__uvicorn_server.serve())


def on_load(server: PluginServerInterface, old):
    global __is_ready, __mcdr_server

    # mcdr init
    __mcdr_server = server

    # register command
    builder = SimpleCommandBuilder()
    builder.command('!!fastapi debug', command_debug_message)
    builder.literal('!!fastapi').requires(
        Requirements.is_console(),
        lambda: 'This command is only available in console.'
    )
    builder.register(server)

    # load config
    config = server.load_config_simple(
        "config.json",
        target_class=PluginConfig
    )

    # start fastapi server
    fastapi_main_thread(config.host, config.port)
    __is_ready = True
    server.logger.info("Fast API started.")


def on_unload(server: PluginServerInterface):
    __mcdr_server.logger.info("Exiting FastAPI.")
    __uvicorn_server.should_exit = True
    time.sleep(0.1)


def command_debug_message(src: CommandSource):
    for route in __app.routes:
        src.get_server().logger.debug(route)


def is_ready() -> bool:
    return __is_ready


def mount(
        plugin_id: str,
        sub_app: FastAPI
) -> None:
    """
    Mount a new app to FastAPI.
    :param plugin_id: plugin id.
    :param sub_app: sub app.
    :return: None
    """
    # check if fastapi is ready
    if not __is_ready:
        raise RuntimeError("FastAPI is not ready yet.")

    # add route
    __app.mount(f"/{plugin_id}", sub_app)

    # log
    __mcdr_server.logger.debug(f'Plugin "{plugin_id}" mounted')


def unmount(plugin_id: str) -> None:
    """
    Unmount app of a plugin.
    :param plugin_id: plugin id.
    :return: None
    """
    # delete routes
    for i, route in enumerate(__app.routes):
        if isinstance(route, Mount) and route.path.startswith(f"/{plugin_id}"):
            del __app.routes[i]
            __mcdr_server.logger.debug(f'Plugin "{plugin_id}" unmounted')
