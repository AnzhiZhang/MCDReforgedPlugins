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
    http: dict = {
        "enable": False,
        "api_host": "127.0.0.1",
        "api_port": 5700,
        "post_host": "127.0.0.1",
        "post_port": 5701,
    }
    websocket: dict = {
        "enable": False,
        "host": "127.0.0.1",
        "port": 5700,
    }


def on_load(server: PluginServerInterface, old):
    global __mcdr_server

    # mcdr init
    __mcdr_server = server
    config = server.load_config_simple(target_class=PluginConfig)

    # check config
    if config.http["enable"] is config.websocket["enable"]:
        server.logger.warning(
            "HTTP and WebSocket cannot be both enabled or disabled, "
            "websocket will be set to enabled"
        )
        config.http["enable"] = False
        config.websocket["enable"] = True
        server.save_config_simple(config)

    # calculate http or websocket
    if config.http["enable"]:
        api_root = (
            f"http://"
            f"{config.http['api_host']}:{config.http['api_port']}"
        )
        host = config.http["post_host"]
        port = config.http["post_port"]
        server.logger.info(
            "HTTP mode enabled, "
            f"API URL: {api_root}, "
            f"Event URL: http://{host}:{port}"
        )
    else:
        api_root = None
        host = config.websocket["host"]
        port = config.websocket["port"]
        server.logger.info(
            f"WebSocket mode enabled at {host}:{port}"
        )

    # cqhttp init
    cqhttp_init_event = threading.Event()

    def cqhttp_init():
        global __event_loop
        __event_loop = new_event_loop()

        async def cqhttp_main():
            global __bot, __uvicorn_server
            __bot = CQHttp(api_root=api_root)
            __uvicorn_server = Server(Config(
                __bot.server_app,
                host=host,
                port=port,
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
                event.content = re.sub(
                    r'\[CQ:video,file=.*?\]', 
                    '[视频]', 
                    event.content)
                event.content = re.sub(
                    r'\[CQ:rps\]', 
                    '[猜拳]', 
                    event.content)
                event.content = re.sub(
                    r'\[CQ:dice\]', 
                    '[掷骰子]', 
                    event.content)
                event.content = re.sub(
                    r'\[CQ:shake\]', 
                    '[窗口抖动]', 
                    event.content)
                event.content = re.sub(
                    r'\[CQ:poke,.*?\]', 
                    "[戳一戳]", 
                    event.content)
                event.content = re.sub(
                    r'\[CQ:anonymous.*?\]', 
                    "[匿名消息]", 
                    event.content)
                event.content = re.sub(
                    r'\[CQ:contact,type=qq.*?\]', 
                    "[推荐好友]", 
                    event.content)
                event.content = re.sub(
                    r'\[CQ:contact,type=group.*?\]', 
                    "[推荐群]", 
                    event.content)
                event.content = re.sub(
                    r'\[CQ:location,.*?\]', 
                    "[定位分享]", 
                    event.content)
                event.content = re.sub(
                    r'\[CQ:music,type=.*?\]', 
                    '[音乐]', 
                    event.content)
                event.content = re.sub(
                    r'\[CQ:forward,id=.*?\]', 
                    '[转发消息]', 
                    event.content)
                event.content = re.sub(
                    r'\[CQ:file(?:,.*?)*\]', 
                    '[文件]', 
                    event.content)
                event.content = re.sub(
                    r'\[CQ:redbag,title=.*?\]', 
                    '[红包]', 
                    event.content)
                event.content = re.sub(
                    r'\[CQ:mface,.*?\]', 
                    '[表情]', 
                    event.content)
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
                # ignore heartbeat
                if event.meta_event_type == "heartbeat":
                    return

                server.logger.debug(f"on meta event: {event}")
                server.dispatch_event(
                    LiteralEvent("qq_api.on_meta_event"),
                    (__bot, event)
                )

            cqhttp_init_event.set()
            await __uvicorn_server.serve()

        __event_loop.run_until_complete(cqhttp_main())

    threading.Thread(target=cqhttp_init, name="QQ API").start()
    cqhttp_init_event.wait()
    server.logger.info("QQ API started.")


def on_unload(server: PluginServerInterface):
    __mcdr_server.logger.info("Exiting QQ API.")
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
