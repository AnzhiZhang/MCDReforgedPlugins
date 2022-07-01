from typing import Dict

from mcdreforged.api.utils.serializer import Serializable


class Config(Serializable):
    gamemode: str = 'survival'
    permissions: Dict[str, int] = {
        'list': 1,
        'spawn': 2,
        'kill': 2,
        'add': 3,
        'remove': 3
    }
