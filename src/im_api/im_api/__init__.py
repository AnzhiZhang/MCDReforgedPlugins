from typing import Optional, TYPE_CHECKING

from mcdreforged.api.all import *

from im_api.core.context import Context

if TYPE_CHECKING:
    from im_api.core.entry import ImAPI

def get_api(server: ServerInterface) -> Optional['ImAPI']:
    """获取 ImAPI 实例
    
    Args:
        server: MCDR 服务器接口
        
    Returns:
        ImAPI 实例，如果未加载则返回 None
    """
    return Context.get_instance().get_api()

def set_api(api: Optional['ImAPI']) -> None:
    """设置 ImAPI 实例
    
    Args:
        api: ImAPI 实例，如果为 None 则清除当前实例
    """
    Context.get_instance().set_api(api)

# 导出
__all__ = ['get_api', 'set_api']
