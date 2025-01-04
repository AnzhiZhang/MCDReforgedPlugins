from typing import Any, Dict, Optional, Callable

from mcdreforged.api.all import *

from im_api.core.driver import DriverManager
from im_api.core.context import Context
from im_api.models.parser import Event, Message


class MessageBridge:
    """消息桥接器，负责在 MCDR 和 IM 平台之间转换消息"""

    def __init__(self, server: ServerInterface, driver_manager: DriverManager):
        """初始化消息桥接器

        Args:
            server: MCDR 服务器接口
            driver_manager: 驱动管理器
        """
        self.server = server
        self.driver_manager = driver_manager
        self.logger = Context.get_instance().logger

        # 注册 MCDR 事件监听器
        self.server.register_event_listener(
            "mcdr.server_startup", self.on_server_startup)
        self.server.register_event_listener(
            "mcdr.server_stop", self.on_server_stop)
        self.server.register_event_listener(
            "mcdr.player_joined", self.on_player_joined)
        self.server.register_event_listener(
            "mcdr.player_left", self.on_player_left)
        self.server.register_event_listener(
            "mcdr.server_startup_done", self.on_server_startup_done)
        self.server.register_event_listener(
            "mcdr.server_interface.on_info", self.on_info)

        # 注册消息发送事件监听器
        self.server.register_event_listener(
            "im_api.send_message", self.on_send_message)

    def on_send_message(self, server: ServerInterface, args: tuple, kwargs: dict):
        """处理发送消息事件

        Args:
            server: MCDR 服务器接口
            args: 位置参数 (platform, channel_id, content)
            kwargs: 关键字参数
        """
        if len(args) != 3:
            self.logger.error(f"Invalid arguments for send_message: {args}")
            return
            
        platform, channel_id, content = args
        self.logger.debug(f"Sending message to {platform}:{channel_id}: {content}")
        message_id = self.send_message(platform, channel_id, content, **kwargs)
        if message_id:
            self.logger.info(f"Message sent to {platform}:{channel_id}: {content}")
        

    def send_message(self, platform: str, channel_id: str, content: str, **kwargs) -> Optional[str]:
        """发送消息到 IM 平台

        Args:
            platform: 平台标识
            channel_id: 目标频道ID
            content: 消息内容
            props: 其他平台特定参数

        Returns:
            消息ID, 如果发送失败则返回 None
        """
        driver = self.driver_manager.get_driver(platform)
        if not driver:
            self.logger.error(f"No driver found for platform: {platform}")
            return None

        try:
            return driver.send_message(channel_id, content, **kwargs)
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            return None

    def on_server_startup(self, server: ServerInterface):
        """处理服务器启动事件"""
        self.logger.debug("Server starting up")
        event = Event(
            id="server_startup",
            type="server.startup",
            platform="minecraft",
            data={
                "status": "starting"
            }
        )
        self.server.dispatch_event(LiteralEvent("im_api.event"), (event,))

    def on_server_startup_done(self, server: ServerInterface):
        """处理服务器启动完成事件"""
        self.logger.debug("Server startup completed")
        event = Event(
            id="server_startup_done",
            type="server.startup",
            platform="minecraft",
            data={
                "status": "started"
            }
        )
        self.server.dispatch_event(LiteralEvent("im_api.event"), (event,))

    def on_server_stop(self, server: ServerInterface):
        """处理服务器停止事件"""
        self.logger.debug("Server stopping")
        event = Event(
            id="server_stop",
            type="server.stop",
            platform="minecraft",
            data={
                "status": "stopping"
            }
        )
        self.server.dispatch_event(LiteralEvent("im_api.event"), (event,))

    def on_player_joined(self, server: ServerInterface, player: str):
        """处理玩家加入事件"""
        self.logger.debug(f"Player joined: {player}")
        event = Event(
            id=f"player_joined_{player}",
            type="guild.member.join",
            platform="minecraft",
            user={
                "id": player,
                "name": player
            }
        )
        self.server.dispatch_event(LiteralEvent("im_api.event"), (event,))

    def on_player_left(self, server: ServerInterface, player: str):
        """处理玩家离开事件"""
        self.logger.debug(f"Player left: {player}")
        event = Event(
            id=f"player_left_{player}",
            type="guild.member.leave",
            platform="minecraft",
            user={
                "id": player,
                "name": player
            }
        )
        self.server.dispatch_event(LiteralEvent("im_api.event"), (event,))

    def on_info(self, server: ServerInterface, info: Info):
        """处理服务器消息事件"""
        if not info.is_player:
            return

        message = Message(
            id=str(info.hour * 10000 + info.min *
                   100 + info.sec),  # 使用时间作为消息ID
            content=info.content,
            channel={
                "id": "minecraft",
                "type": "game"
            },
            user={
                "id": info.player,
                "name": info.player
            }
        )
        self.logger.debug(f"Game message from {info.player}: {info.content}")
        self.server.dispatch_event(LiteralEvent("im_api.message"), (message,))


# 导出
__all__ = ["MessageBridge"]
