from typing import Dict

from mcdreforged.api.utils.serializer import Serializable


class Config(Serializable):
    gamemode: str = 'survival'
    name_prefix: str = ''
    name_suffix: str = ''
    permissions: Dict[str, int] = {
        'list': 1,
        'spawn': 1,
        'kill': 1,
        'action': 1,
        'info': 1,
        'save': 2,
        'del': 2,
        'config': 2
    }
