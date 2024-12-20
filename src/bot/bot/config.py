from typing import Dict

from mcdreforged.api.utils.serializer import Serializable


class Config(Serializable):
    gamemode: str = 'survival'
    force_gamemode: bool = False
    name_prefix: str = 'bot_'
    name_suffix: str = ''
    post_join_delay: int = 0
    permissions: Dict[str, int] = {
        'list': 1,
        'spawn': 1,
        'kill': 1,
        'action': 1,
        'tags': 1,
        'info': 1,
        'save': 2,
        'del': 2,
        'config': 2
    }
