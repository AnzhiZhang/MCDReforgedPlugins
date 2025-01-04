import os
import json
from typing import Any, Dict, Optional

from mcdreforged.api.types import PluginServerInterface, CommandSource, Info
from mcdreforged.api.command import Literal

from im_api.core.driver import DriverManager
from im_api.core.processor import EventProcessor
from im_api.core.bridge import MessageBridge
from im_api.core.context import Context
from im_api.drivers.qq import QQDriver


class ImAPI:
    """ImAPI 插件主类"""

    PLUGIN_ID = "im_api"

    def __init__(self, server: PluginServerInterface):
        self.server = server
        self.logger = server.logger
        self.config = self._load_config()

        # 初始化管理器
        self.driver_manager = DriverManager()
        self.message_bridge = MessageBridge(self.server, self.driver_manager)
        self.event_processor = EventProcessor(self.server, self.driver_manager, self.message_bridge)
        
        # 注册驱动
        self.driver_manager.register_driver("qq", QQDriver)

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        return self.server.load_config_simple("config.json", default_config={
            "drivers": {
                # 示例配置
                "qq": {
                    "enabled": False,
                    "config": {
                        "host": "127.0.0.1",
                        "port": 8080,
                        "access_token": ""
                    }
                },
                "kook": {
                    "enabled": False,
                    "config": {
                        "token": ""
                    }
                }
            }})

    def load(self):
        """加载插件"""
        self.logger.info("Loading ImAPI...")

        # 加载驱动
        for platform, driver_config in self.config["drivers"].items():
            if not driver_config.get("enabled", False):
                continue

            try:
                self.driver_manager.load_driver(
                    platform, driver_config["config"])
                self.logger.info(f"Loaded driver for platform: {platform}")
            except Exception as e:
                self.logger.error(
                    f"Failed to load driver for platform {platform}: {e}")

        # 注册驱动回调
        self.driver_manager.register_callbacks(
            lambda platform, msg: self.event_processor.on_message(platform, msg),
            lambda platform, evt: self.event_processor.on_event(platform, evt)
        )

        # 注册事件监听器
        # self.server.register_event_listener("im_api.send_message", self.event_processor.on_send_message)

        # 注册命令
        self.server.register_help_message("!!im", "ImAPI commands")
        self.server.register_command(
            Literal("!!im").
            then(
                Literal("reload").
                runs(lambda src: self.reload(src))
            ).
            then(
                Literal("status").
                runs(lambda src: self.show_status(src))
            )
        )

        self.logger.info("ImAPI loaded successfully")

    def unload(self):
        """卸载插件"""
        self.logger.info("Unloading ImAPI...")
        # 先关闭所有驱动
        self.driver_manager.shutdown()
        # 等待一段时间确保资源被释放
        import time
        time.sleep(1)
        self.logger.info("ImAPI unloaded successfully")

    def reload(self, source: CommandSource):
        """重载插件"""
        self.logger.info("Reloading ImAPI...")
        # 先卸载旧实例
        self.unload()
        # 重新加载配置
        self.config = self._load_config()
        # 重新加载插件
        self.load()
        source.reply("ImAPI reloaded successfully")

    def show_status(self, source: CommandSource):
        """显示插件状态"""
        drivers = self.driver_manager.get_all_drivers()
        if not drivers:
            source.reply("No drivers loaded")
            return

        status = ["ImAPI Status:"]
        for driver in drivers:
            status.append(
                f"- {driver.platform}: {'Connected' if driver.connected else 'Disconnected'}")
        source.reply("\n".join(status))


def on_load(server: PluginServerInterface, old_module):
    """插件加载入口"""
    # 初始化上下文
    context = Context.get_instance()
    context.initialize(server)
    
    # 如果是热重载，先卸载旧实例
    if old_module is not None:
        old_api = context.get_api()
        if old_api is not None:
            old_api.unload()
            context.set_api(None)
    
    # 创建新实例并加载
    api = ImAPI(server)
    api.load()  # 先完成加载
    context.set_api(api)  # 加载完成后再设置到 Context 中
    
    return api


def on_unload(server: PluginServerInterface):
    """插件卸载入口"""
    context = Context.get_instance()
    if context.is_initialized():
        server.logger.info("Unloading ImAPI plugin...")
        api = context.get_api()
        if api is not None:
            api.unload()
            context.set_api(None)
        context.reset_instance()
        server.logger.info("ImAPI plugin unloaded")
