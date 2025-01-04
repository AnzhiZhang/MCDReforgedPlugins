from typing import Any, Dict, List, Optional, Type, Callable

from im_api.core.context import Context
from im_api.drivers.base import BaseDriver
from im_api.models.parser import Event, Message


class DriverManager:
    """驱动管理器，负责管理所有驱动实例"""

    def __init__(self):
        """初始化驱动管理器"""
        self.drivers: Dict[str, Type[BaseDriver]] = {}  # 驱动类映射
        self.instances: Dict[str, BaseDriver] = {}  # 驱动实例映射
        self.logger = Context.get_instance().logger

    def register_driver(self, platform: str, driver_cls: Type[BaseDriver]) -> None:
        """注册驱动类

        Args:
            platform: 平台标识
            driver_cls: 驱动类
        """
        self.drivers[platform] = driver_cls
        self.logger.debug(f"Registered driver for platform: {platform}")

    def load_driver(self, platform: str, config: Dict[str, Any]) -> None:
        """加载驱动实例

        Args:
            platform: 平台标识
            config: 驱动配置
        """
        if platform not in self.drivers:
            self.logger.error(f"No driver registered for platform: {platform}")
            return

        try:
            driver = self.drivers[platform](config)
            driver.connect()
            self.instances[platform] = driver
            self.logger.info(f"Loaded driver for platform: {platform}")
        except Exception as e:
            self.logger.error(
                f"Failed to load driver for platform {platform}: {e}")
            raise

    def unload_driver(self, platform: str) -> None:
        """卸载驱动实例

        Args:
            platform: 平台标识
        """
        if platform not in self.instances:
            self.logger.warning(
                f"No driver instance found for platform: {platform}")
            return

        try:
            driver = self.instances[platform]
            driver.disconnect()
            del self.instances[platform]
            self.logger.info(f"Unloaded driver for platform: {platform}")
        except Exception as e:
            self.logger.error(
                f"Failed to unload driver for platform {platform}: {e}")
            raise

    def get_driver(self, platform: str) -> Optional[BaseDriver]:
        """获取驱动实例

        Args:
            platform: 平台标识

        Returns:
            驱动实例，如果不存在则返回 None
        """
        if platform not in self.instances:
            self.logger.warning(
                f"No driver instance found for platform: {platform}")
            return None
        return self.instances[platform]

    def get_all_drivers(self) -> List[BaseDriver]:
        """获取所有驱动实例

        Returns:
            驱动实例列表
        """
        return list(self.instances.values())

    def register_callbacks(self, message_callback: Callable[[str, Message], None], event_callback: Callable[[str, Event], None]) -> None:
        """为所有驱动注册回调函数

        Args:
            message_callback: 消息回调函数
            event_callback: 事件回调函数
        """
        for platform, driver in self.instances.items():
            try:
                driver.register_callbacks(message_callback, event_callback)
                self.logger.debug(
                    f"Registered callbacks for platform: {platform}")
            except Exception as e:
                self.logger.error(
                    f"Failed to register callbacks for platform {platform}: {e}")

    def shutdown(self) -> None:
        """关闭所有驱动"""
        self.logger.info("Shutting down all drivers...")
        for platform in list(self.instances.keys()):
            try:
                self.unload_driver(platform)
            except Exception as e:
                self.logger.error(
                    f"Error shutting down driver for platform {platform}: {e}")
        self.logger.info("All drivers shut down")


# 导出
__all__ = ["DriverManager"]
