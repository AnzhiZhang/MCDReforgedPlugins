from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional

from im_api.core.context import Context
from im_api.models.parser import Event, Message

class BaseDriver(ABC):
    """驱动基类，定义了驱动的基本接口"""
    
    platform: str = "base"
    
    def __init__(self, config: Dict[str, Any]):
        """初始化驱动
        
        Args:
            config: 驱动配置
        """
        self.config = config
        self.connected = False
        self.message_callback: Optional[Callable[[str, Message], None]] = None
        self.event_callback: Optional[Callable[[str, Event], None]] = None
        self.logger = Context.get_instance().logger
        
    @abstractmethod
    def connect(self) -> None:
        """连接到平台"""
        pass
        
    @abstractmethod
    def disconnect(self) -> None:
        """断开与平台的连接"""
        pass
        
    @abstractmethod
    def send_message(self, channel_id: str, content: str, **kwargs) -> Optional[str]:
        """发送消息
        
        Args:
            channel_id: 目标频道ID
            content: 消息内容
            **kwargs: 其他平台特定参数
            
        Returns:
            消息ID, 如果发送失败则返回 None
        """
        pass
        
    @abstractmethod
    def delete_message(self, channel_id: str, message_id: str) -> bool:
        """删除消息
        
        Args:
            channel_id: 频道ID
            message_id: 消息ID
            
        Returns:
            是否删除成功
        """
        pass
        
    def register_callbacks(self, message_callback: Callable[[str, Message], None], event_callback: Callable[[str, Event], None]):
        """注册回调函数
        
        Args:
            message_callback: 消息回调函数
            event_callback: 事件回调函数
        """
        self.message_callback = message_callback
        self.event_callback = event_callback
        self.logger.debug(f"Registered callbacks for {self.platform} driver")

# 导出
__all__ = ["BaseDriver"]
