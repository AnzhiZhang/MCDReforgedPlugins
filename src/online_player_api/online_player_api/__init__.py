from typing import List

online_players = {}


def on_load(server, old):
    global online_players
    if old is not None and hasattr(old, 'online_players'):
        if isinstance(old.online_players, dict):
            online_players = old.online_players
        elif isinstance(old.online_players, list):
            for player in old.online_players:
                online_players[player.lower()] = player


def on_server_stop(server, return_code):
    global online_players
    online_players = {}


def on_player_joined(server, player, info):
    online_players[player.lower()] = player


def on_player_left(server, player):
    online_players.pop(player.lower(), None)


def check_online(player: str) -> bool:
    """Check a player is online"""
    return player.lower() in online_players


def get_player_list() -> List[str]:
    """Get all online player list"""
    return list(online_players.values())
