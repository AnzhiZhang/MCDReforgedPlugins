from typing import List

online_players = []


def on_load(server, old):
    global online_players
    if old is not None and hasattr(old, 'online_players'):
        online_players = old.online_players


def on_server_stop(server, return_code):
    global online_players
    online_players = []


def on_player_joined(server, player, info):
    if player not in online_players:
        online_players.append(player)


def on_player_left(server, player):
    if player in online_players:
        online_players.remove(player)


def check_online(player: str) -> bool:
    """Check a player is online"""
    return player in online_players


def get_player_list() -> List[str]:
    """Get all online player list"""
    return online_players.copy()
