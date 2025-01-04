from typing import Any, Dict, Optional

from mcdreforged.api.all import *

from im_api.core.driver import DriverManager
from im_api.core.bridge import MessageBridge
from im_api.core.context import Context
from im_api.models.parser import Event, Message


class EventProcessor:
    """事件处理器，负责处理所有事件"""

    def __init__(self, server: ServerInterface, driver_manager: DriverManager, message_bridge: MessageBridge):
        """初始化事件处理器

        Args:
            server: MCDR 服务器接口
            driver_manager: 驱动管理器
            message_bridge: 消息桥接器
        """
        self.server = server
        self.driver_manager = driver_manager
        self.message_bridge = message_bridge
        self.logger = Context.get_instance().logger

    def on_message(self, platform: str, message: Message):
        """处理来自驱动的消息

        Args:
            platform: 平台标识
            message: 消息对象
        """
        # 触发消息事件
        self.logger.info(f"Received message from {platform}: {message.content}")
        self.server.dispatch_event(LiteralEvent("im_api.message"), (platform, message))
        # 触发回复消息事件
        # if message.channel.get("id") == '3110942575':
        #     kwargs = {"message_type": message.channel.get("type", "group")}
        #     args = (platform, message.channel.get("id"), f'echo: {message.content}')
        #     self.server.dispatch_event(LiteralEvent("im_api.send_message"), (args, kwargs))

    def on_event(self, platform: str, event: Event):
        """处理来自驱动的事件

        Args:
            platform: 平台标识
            event: 事件对象
        """
        # 触发事件
        self.logger.debug(f"Received event from {platform}: {event.type}")
        self.server.dispatch_event(LiteralEvent("im_api.event"), (platform, event))


# 导出
__all__ = ["EventProcessor"]
