import re
import time
import logging
import threading
from asyncio import AbstractEventLoop, new_event_loop

from uvicorn import Config, Server
from aiocqhttp import CQHttp, Event
from mcdreforged.api.utils import Serializable
from mcdreforged.api.event import LiteralEvent
from mcdreforged.api.types import PluginServerInterface

__all__ = [
    "MessageEvent",
    "get_event_loop",
    "get_bot",
]

__mcdr_server: PluginServerInterface
__event_loop: AbstractEventLoop
__bot: CQHttp
__uvicorn_server: Server


class MessageEvent(Event):
    content: str


class PluginConfig(Serializable):
    api_host: str = "127.0.0.1"
    api_port: int = 5700
    post_host: str = "127.0.0.1"
    post_port: int = 5701


def on_load(server: PluginServerInterface, old):
    global __mcdr_server

    # mcdr init
    __mcdr_server = server
    config = server.load_config_simple(target_class=PluginConfig)

    # cqhttp init
    cqhttp_init_event = threading.Event()

    def cqhttp_init():
        global __event_loop
        __event_loop = new_event_loop()

        async def cqhttp_main():
            global __bot, __uvicorn_server
            __bot = CQHttp(
                api_root=f"http://{config.api_host}:{config.api_port}"
            )
            __uvicorn_server = Server(Config(
                __bot.server_app,
                host=config.post_host,
                port=config.post_port,
                loop="none",
                log_level=logging.CRITICAL
            ))

            @__bot.on_message
            async def on_message(event: Event):
                # parse content
                event.content = event.raw_message
                event.content = re.sub(
                    r'\[CQ:image,file=.*?]',
                    '[图片]',
                    event.content
                )
                event.content = re.sub(
                    r'\[CQ:share,file=.*?]',
                    '[链接]',
                    event.content
                )
                event.content = re.sub(
                    r'\[CQ:face,id=.*?]',
                    '[表情]',
                    event.content
                )
                event.content = re.sub(
                    r'\[CQ:record,file=.*?]',
                    '[语音]',
                    event.content
                )
                event.content = event.content.replace('CQ:at,qq=', '@')
                event: MessageEvent

                # dispatch event
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
            async def on_meta_event(event: Event):
                server.logger.debug(f"on meta event: {event}")
                server.dispatch_event(
                    LiteralEvent("qq_api.on_meta_event"),
                    (__bot, event)
                )

            cqhttp_init_event.set()
            await __uvicorn_server.serve()

        __event_loop.run_until_complete(cqhttp_main())

    threading.Thread(target=cqhttp_init, name="QQ API Server").start()
    cqhttp_init_event.wait()
    server.logger.info("Bot listener server started.")


def on_unload(server: PluginServerInterface):
    __mcdr_server.logger.info("Exiting bot listener server.")
    __uvicorn_server.should_exit = True
    time.sleep(0.1)


def get_event_loop() -> AbstractEventLoop:
    """
    Get asyncio event loop
    :return: AbstractEventLoop.
    """
    return __event_loop


def get_bot() -> CQHttp:
    """
    Get CQHttp instance.
    :return: CQHttp.
    """
    return __bot
