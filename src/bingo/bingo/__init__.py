# -*- coding: utf-8 -*-
import math
import random

from mcdreforged.api.types import PluginServerInterface, CommandSource
from mcdreforged.api.command import *
from mcdreforged.api.rtext import *

TEAM_NAME = ['§cRed', '§eYellow', '§aGreen', '§3Blue']
HELP_MSG = '''§7!!bingo team <num> §6按在线玩家随机分组
§7!!bingo end §6结束游戏'''


def on_load(server: PluginServerInterface, old):
    server.register_command(
        Literal('!!bingo').
            runs(lambda src: src.reply(HELP_MSG)).
            then(
            Literal('team').
                runs(team).
                then(
                Integer('num').
                    in_range(1, 4).
                    runs(team)
            )
        ).
            then(
            Literal('end').
                requires(
                lambda src: src.has_permission(2),
                failure_message_getter=lambda: '§c权限不足！'
            ).runs(
                lambda src: src.get_server().execute('function flytre:win/all'))
        )
    )


def team(src: CommandSource, ctx):
    team_num = ctx.get('num', 4)

    # Make random team
    player_list = src.get_server().rcon_query('list').split(': ')[1].split(', ')
    random.shuffle(player_list)
    max_player = math.ceil(len(player_list) / team_num)
    result = []
    for i in range(0, len(player_list), max_player):
        result.append(player_list[i:i + max_player])

    # Show result
    src.get_server().say(RText('§6§l分组结果如下：'))
    for i, players in enumerate(result):
        src.get_server().say(f'{TEAM_NAME[i]}: §r{", ".join(players)}')
