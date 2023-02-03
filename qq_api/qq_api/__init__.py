import logging
from threading import Thread

from uvicorn import Config, Server
from aiocqhttp import CQHttp, Event
from mcdreforged.api.utils import Serializable
from mcdreforged.api.event import LiteralEvent
from mcdreforged.api.types import PluginServerInterface

__all__ = [
    "get_bot"
]

__bot: CQHttp
__uvicorn_server: Server
__mcdr_server: PluginServerInterface


class PluginConfig(Serializable):
    api_host: str = "127.0.0.1"
    api_port: int = 5700
    post_host: str = "127.0.0.1"
    post_port: int = 5701


def on_load(server: PluginServerInterface, old):
    global __bot, __uvicorn_server, __mcdr_server

    # mcdr init
    __mcdr_server = server
    config = server.load_config_simple(target_class=PluginConfig)

    # cqhttp init
    __bot = CQHttp(api_root=f"http://{config.api_host}:{config.api_port}")
    __uvicorn_server = Server(Config(
        __bot.server_app,
        host=config.post_host,
        port=config.post_port,
        log_level=logging.CRITICAL
    ))

    @__bot.on_message
    async def on_message(event: Event):
        server.logger.debug(f"on message: {event}")
        server.dispatch_event(
            LiteralEvent("qq_api.on_message"),
            (__bot, event)
        )

    @__bot.on_notice
    async def on_notice(event: Event):
        server.logger.debug(f"on notice: {event}")
        server.dispatch_event(
            LiteralEvent("qq_api.on_notice"),
            (__bot, event)
        )

    @__bot.on_request
    async def on_request(event: Event):
        server.logger.debug(f"on request: {event}")
        server.dispatch_event(
            LiteralEvent("qq_api.on_request"),
            (__bot, event)
        )

    @__bot.on_meta_event
    async def on_message(event: Event):
        server.logger.debug(f"on meta event: {event}")
        server.dispatch_event(
            LiteralEvent("qq_api.on_meta_event"),
            (__bot, event)
        )

    Thread(target=__uvicorn_server.run, name="QQ API Server").start()
    server.logger.info("Bot listener server started.")


def on_unload(server: PluginServerInterface):
    __mcdr_server.logger.info("Exiting bot listener server.")
    __uvicorn_server.should_exit = True


def get_bot() -> CQHttp:
    """
    Get CQHttp instance.
    :return: CQHttp.
    """
    return __bot
