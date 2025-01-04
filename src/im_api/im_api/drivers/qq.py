import asyncio
import json
import socket
import threading
import time
from typing import Any, Optional

from aiohttp import web
from aiocqhttp import CQHttp, Event as CQEvent
from mcdreforged.api.all import *

from im_api.drivers.base import BaseDriver
from im_api.models.parser import Event, Message

class QQDriver(BaseDriver):
    """QQ 驱动实现，使用 aiocqhttp 对接 OneBot 反向 WebSocket 接口"""
    
    platform = "qq"
    
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)
        self.host = config.get("host", "127.0.0.1")
        self.port = config.get("port", 8080)
        self.access_token = config.get("access_token", "")
        
        self.logger.info(f"Initializing QQ driver with host={self.host}, port={self.port}")
        
        # 创建 bot 实例
        self.bot = CQHttp(
            api_root=None,  # 不使用 HTTP API
            access_token=self.access_token
        )
        self.event_loop = None
        self.server_thread = None
        self.app = web.Application()
        self.runner = None
        self.site = None
        self.startup_event = threading.Event()
        self.ws_connections = {}  # 存储所有 WebSocket 连接及其锁
        self.ws_locks = {}  # WebSocket 连接的锁

        # 注册事件处理器
        @self.bot.on_message
        async def handle_msg(event: CQEvent):
            self.logger.debug(f"Received message: {event.message} from {event.user_id}")
            # 转换为 Satori 消息格式
            message = Message(
                id=str(event.message_id),
                content=event.message,
                channel={
                    "id": str(event.group_id) if event.group_id else str(event.user_id),
                    "type": "group" if event.group_id else "private"
                },
                user={
                    "id": str(event.user_id),
                    "name": event.sender.get("nickname", ""),
                    "avatar": f"http://q1.qlogo.cn/g?b=qq&nk={event.user_id}&s=640"
                }
            )
            self.logger.debug(f"Received message: {message.content} from {message.user['id']} in {message.channel['id']}")
            # 触发消息事件
            if self.message_callback:
                self.message_callback(self.platform, message)
                self.logger.debug("Message forwarded to MCDR")
            else:
                self.logger.warning("No message callback registered")
            
        @self.bot.on_notice
        async def handle_notice(event: CQEvent):
            self.logger.debug(f"Received notice: {event.notice_type} from {event.user_id}")
            # 转换为 Satori 事件格式
            if event.notice_type == "group_increase":
                evt = Event(
                    id=str(event.time),
                    type="guild.member.join",
                    platform=self.platform,
                    channel={
                        "id": str(event.group_id),
                        "type": "group"
                    },
                    user={
                        "id": str(event.user_id)
                    }
                )
            elif event.notice_type == "group_decrease":
                evt = Event(
                    id=str(event.time),
                    type="guild.member.leave",
                    platform=self.platform,
                    channel={
                        "id": str(event.group_id),
                        "type": "group"
                    },
                    user={
                        "id": str(event.user_id)
                    }
                )
            else:
                self.logger.debug(f"Ignoring unsupported notice type: {event.notice_type}")
                return
                
            # 触发事件
            if self.event_callback:
                self.logger.debug(f"Forwarding event to MCDR: {evt}")
                self.event_callback(self.platform, evt)
            else:
                self.logger.warning("No event callback registered")
            
        async def handle_ws(request):
            """处理 WebSocket 连接"""
            self.logger.info("New WebSocket connection")
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            
            # 为新连接创建锁
            ws_id = id(ws)
            self.ws_connections[ws_id] = ws
            self.ws_locks[ws_id] = asyncio.Lock()
            
            try:
                async for msg in ws:
                    if msg.type == web.WSMsgType.TEXT:
                        try:
                            data = json.loads(msg.data)
                            # 忽略心跳消息和响应消息
                            if data.get("meta_event_type") == "lifecycle" or \
                               data.get("meta_event_type") == "heartbeat" or \
                               data.get("status") == "ok":  # 忽略响应消息
                                continue
                                
                            self.logger.info(f"Received WebSocket message: {data}")
                            # 创建事件对象并处理
                            event = CQEvent.from_payload(data)
                            if event.type == "message":
                                await handle_msg(event)
                            elif event.type == "notice":
                                await handle_notice(event)
                        except Exception as e:
                            self.logger.error(f"Error handling WebSocket message: {e}")
                    elif msg.type == web.WSMsgType.ERROR:
                        self.logger.error(f"WebSocket connection closed with exception {ws.exception()}")
            finally:
                # 清理连接和锁
                del self.ws_connections[ws_id]
                del self.ws_locks[ws_id]
                self.logger.info("WebSocket connection closed")
                return ws
            
        self.app.router.add_get("/ws/", handle_ws)
            
    def connect(self) -> None:
        """连接到 OneBot 服务器"""
        if self.connected:
            self.logger.info("Already connected")
            return
            
        async def start_server():
            self.logger.info("Starting WebSocket server...")
            try:
                self.runner = web.AppRunner(self.app)
                await self.runner.setup()
                self.logger.debug("Runner setup completed")
                
                self.site = web.TCPSite(self.runner, self.host, self.port)
                self.logger.debug("Site created")
                
                await self.site.start()
                self.logger.info(f"WebSocket server started at ws://{self.host}:{self.port}/ws/")
                self.startup_event.set()  # 标记服务器启动成功
            except Exception as e:
                self.logger.error(f"Failed to start WebSocket server: {e}")
                self.startup_event.set()  # 标记启动失败
            
        def run_server():
            try:
                self.logger.debug("Creating event loop")
                self.event_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.event_loop)
                
                self.logger.debug("Starting server")
                self.event_loop.run_until_complete(start_server())
                self.logger.debug("Event loop started")
                self.event_loop.run_forever()
            except Exception as e:
                self.logger.error(f"Error in server thread: {e}")
                self.startup_event.set()  # 标记启动失败
            
        self.logger.info("Starting server thread")
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        # 等待服务器启动完成
        self.logger.info("Waiting for server startup")
        self.startup_event.wait(timeout=5)
        if self.site is not None:
            self.connected = True
            self.logger.info("QQ driver connected successfully")
        else:
            self.logger.error("Failed to connect QQ driver: server not started")
        
    async def cleanup(self):
        """清理资源"""
        self.logger.info("Cleaning up resources...")
        try:
            # 关闭所有 WebSocket 连接
            for ws in set(self.app._state.get('websockets', [])):
                try:
                    await asyncio.wait_for(ws.close(code=1000, message='Server shutdown'), timeout=0.5)
                except asyncio.TimeoutError:
                    self.logger.warning("WebSocket close timeout")
                except Exception as e:
                    self.logger.error(f"Error closing WebSocket: {e}")
            self.logger.debug("WebSocket connections closed")
            
            # 停止站点
            if self.site:
                try:
                    await asyncio.wait_for(self.site.stop(), timeout=1.0)
                    self.logger.debug("WebSocket site stopped")
                except asyncio.TimeoutError:
                    self.logger.warning("Site stop timeout")
                except Exception as e:
                    self.logger.error(f"Error stopping site: {e}")
                
            # 清理运行器
            if self.runner:
                try:
                    await asyncio.wait_for(self.runner.cleanup(), timeout=1.0)
                    self.logger.debug("Runner cleaned up")
                except asyncio.TimeoutError:
                    self.logger.warning("Runner cleanup timeout")
                except Exception as e:
                    self.logger.error(f"Error cleaning up runner: {e}")
                
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
        self.logger.debug("Cleanup completed")
        
    def disconnect(self) -> None:
        """断开与 OneBot 服务器的连接"""
        if not self.connected:
            return
            
        self.logger.info("Disconnecting QQ driver...")
        if self.event_loop:
            try:
                # 确保清理任务完成
                future = asyncio.run_coroutine_threadsafe(self.cleanup(), self.event_loop)
                future.result(timeout=2)  # 减少等待时间
                
                # 停止事件循环
                self.event_loop.call_soon_threadsafe(self.event_loop.stop)
                
                # 等待事件循环结束
                if self.server_thread and self.server_thread.is_alive():
                    self.server_thread.join(timeout=2)  # 减少等待时间
                    
                # 关闭事件循环
                try:
                    self.event_loop.close()
                except:
                    pass
                    
            except Exception as e:
                self.logger.error(f"Error during disconnect: {e}")
            
        # 清理资源
        self.connected = False
        self.event_loop = None
        self.server_thread = None
        self.site = None
        self.runner = None
        self.app = web.Application()  # 重置应用
        self.logger.info("QQ driver disconnected")
        
    async def send_ws_message(self, data: dict) -> Optional[dict]:
        """发送 WebSocket 消息
        
        Args:
            data: 要发送的数据
            
        Returns:
            总是返回 True, 表示消息已发送
        """
        # 遍历所有活跃的连接
        for ws_id, ws in list(self.ws_connections.items()):
            if ws.closed:
                continue
            try:
                # 获取连接的锁
                async with self.ws_locks[ws_id]:
                    # 发送消息
                    await ws.send_json(data)
                    return True  # 发送成功就返回
            except Exception as e:
                self.logger.error(f"Error in WebSocket communication: {e}")
                continue
                
        self.logger.warning("No active WebSocket connections")
        return False
        
    def send_message(self, channel_id: str, content: str, **kwargs) -> Optional[str]:
        """发送消息
        
        Args:
            channel_id: 目标频道ID (群号或用户ID)
            content: 消息内容
            **kwargs: 其他参数
                - message_type: 消息类型 (group/private)
        """
        if not self.connected or not self.event_loop:
            self.logger.error("Cannot send message: driver not connected")
            return None
            
        message_type = kwargs.get("message_type", "group")
        self.logger.info(f"Sending {message_type} message to {channel_id}: {content}")
        
        # 构造消息
        action = "send_group_msg" if message_type == "group" else "send_private_msg"
        data = {
            "action": action,
            "params": {
                "message": content,
                "group_id" if message_type == "group" else "user_id": int(channel_id)
            }
        }
        
        async def _send():
            success = await self.send_ws_message(data)
            return "success" if success else None
            
        future = asyncio.run_coroutine_threadsafe(_send(), self.event_loop)
        try:
            return future.result(timeout=10)
        except Exception as e:
            self.logger.error(f"Error waiting for message result: {e}")
            return None
        
    def delete_message(self, channel_id: str, message_id: str) -> bool:
        """删除消息
        
        Args:
            channel_id: 频道ID (不使用)
            message_id: 消息ID
        """
        if not self.connected or not self.event_loop:
            self.logger.error("Cannot delete message: driver not connected")
            return False
            
        self.logger.info(f"Deleting message {message_id}")
        
        # 构造消息
        data = {
            "action": "delete_msg",
            "params": {
                "message_id": int(message_id)
            }
        }
        
        async def _delete():
            return await self.send_ws_message(data)
                
        future = asyncio.run_coroutine_threadsafe(_delete(), self.event_loop)
        try:
            return future.result(timeout=10)
        except Exception as e:
            self.logger.error(f"Error waiting for delete result: {e}")
            return False

# 导出
__all__ = ["QQDriver"] 