# -*- coding: utf-8 -*-
from typing import List

online_player = []
PLUGIN_METADATA = {
    'id': 'online_player_api',
    'version': '0.0.1',
    'name': 'OnlinePlayerAPI',
    'description': 'Online Player API',
    'author': 'zhang_anzhi',
    'link': 'https://github.com/zhang-anzhi/MCDReforgedPlugins/tree/master/OnlinePlayerAPI'
}


def on_load(server, old):
    global online_player
    server.register_help_message('!!list', '获取在线玩家列表')
    if old is not None and hasattr(old, 'online_player'):
        online_player = old.online_player
    else:
        online_player = []


def on_server_stop(server, return_code):
    global online_player
    online_player = []


def on_player_joined(server, player, info):
    if player not in online_player:
        online_player.append(player)


def on_player_left(server, player):
    if player in online_player:
        online_player.remove(player)


def on_info(server, info):
    if info.content == '!!list':
        server.reply(
            info,
            '当前共有{}名玩家在线: {}'.format(len(online_player),
                                     ', '.join(online_player))
        )


def check_online(player: str) -> bool:
    """Check a player is online"""
    return True if player in online_player else False


def get_player_list() -> List[str]:
    """Get all online player list"""
    return online_player
