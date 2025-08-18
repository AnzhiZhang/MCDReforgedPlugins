from typing import List

online_players: List[str] = []


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


def is_online(player: str, case_sensitive: bool = True) -> bool:
    """Check a player is online."""
    if case_sensitive:
        return player in online_players
    else:
        player = player.lower()
        return player in [i.lower() for i in online_players]


def check_online(player: str, case_sensitive: bool = True) -> bool:
    """Check a player is online."""
    return is_online(player, case_sensitive)


def get_player_list() -> List[str]:
    """Get all online players."""
    return online_players.copy()
