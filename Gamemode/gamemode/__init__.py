# -*- coding: utf-8 -*-
import time
from math import ceil

from mcdreforged.api.types import PluginServerInterface
from mcdreforged.api.command import *
from mcdreforged.api.decorator import new_thread

DIMENSIONS = {
    '0': 'minecraft:overworld',
    '-1': 'minecraft:the_nether',
    '1': 'minecraft:the_end',
    'overworld': 'minecraft:overworld',
    'the_nether': 'minecraft:the_nether',
    'the_end': 'minecraft:the_end',
    'nether': 'minecraft:the_nether',
    'end': 'minecraft:the_end',
    'minecraft:overworld': 'minecraft:overworld',
    'minecraft:the_nether': 'minecraft:the_nether',
    'minecraft:the_end': 'minecraft:the_end'
}
DEFAULT_CONFIG = {
    'permissions': {
        'spec': 1,
        'spec_other': 2,
        'tp': 1,
        'back': 1
    }
}
HELP_MESSAGE = '''§6!!spec §7旁观/生存切换
§6!!spec <player> §7切换他人模式
§6!!tp <dimension> [position] §7传送至指定地点
§6!!back §7返回上个地点'''


def on_load(server: PluginServerInterface, old):
    from gamemode.config import Config
    from gamemode.json import Json
    global api, data
    api = server.get_plugin_instance('minecraft_data_api')
    config = Config("gamemode", DEFAULT_CONFIG)
    data = Json("gamemode")
    permissions = config['permissions']
    server.register_help_message('!!spec help', 'Gamemode插件帮助')

    @new_thread('Gamemode switch mode')
    def change_mode(src, ctx):
        if src.is_console:
            return src.reply('§c仅允许玩家使用')
        player = src.player if ctx == {} else ctx['player']
        if player not in data.keys():
            server.tell(player, '§a已切换至旁观模式')
            sur_to_spec(server, player)
        elif player in data.keys():
            use_time = ceil((time.time() - data[player]['time']) / 60)
            server.tell(player, f'§a您使用了§e{use_time}min')
            spec_to_sur(server, player)

    @new_thread('Gamemode tp')
    def tp(src, ctx):
        if src.is_console:
            return src.reply('§c仅允许玩家使用')
        if src.player not in data.keys():
            src.reply('§c您只能在旁观模式下传送')
        elif ctx['dimension'] not in DIMENSIONS.keys():
            src.reply('§c没有此维度')
        else:
            pos = ' '.join((
                str(ctx.get('x', '0')),
                str(ctx.get('y', '80')),
                str(ctx.get('z', '0'))
            ))
            dim = DIMENSIONS[ctx['dimension']]
            data[src.player]['back'] = {
                'dim': DIMENSIONS[api.get_player_info(src.player, 'Dimension')],
                'pos': api.get_player_info(src.player, 'Pos')
            }
            data.save()
            server.execute(f'execute in {dim} run tp {src.player} {pos}')
            src.reply(f'§a传送至§e{dim}§a, 坐标§e{dim}')

    @new_thread('Gamemode back')
    def back(src):
        if src.is_console:
            return src.reply('§c仅允许玩家使用')
        if src.player not in data.keys():
            return src.reply('§c您只能在旁观模式下传送')
        else:
            dim = data[src.player]['back']['dim']
            pos = [str(x) for x in data[src.player]['back']['pos']]
            data[src.player]['back'] = {
                'dim': DIMENSIONS[api.get_player_info(src.player, 'Dimension')],
                'pos': api.get_player_info(src.player, 'Pos')
            }
            data.save()
            server.execute(
                f'execute in {dim} run tp {src.player} {" ".join(pos)}')
            src.reply('§a已将您传送至上个地点')

    server.register_command(
        Literal('!!spec').
            requires(lambda src: src.has_permission(permissions['spec'])).
            runs(change_mode).
            then(
            Literal('help').
                runs(lambda src: src.reply(HELP_MESSAGE))
        ).
            then(
            Text('player').
                requires(
                lambda src: src.has_permission(permissions['spec_other'])
            ).
                runs(change_mode)
        )
    )
    server.register_command(
        Literal('!!tp').
            requires(lambda src: src.has_permission(permissions['tp'])).
            then(
            Text('dimension').
                runs(tp).
                then(
                Float('x').
                    then(
                    Float('y').
                        then(
                        Float('z').runs(tp)
                    )
                )
            )
        )
    )
    server.register_command(
        Literal('!!back').
            requires(lambda src: src.has_permission(permissions['back'])).
            runs(back)
    )


def sur_to_spec(server, player):
    dim = DIMENSIONS[api.get_player_info(player, 'Dimension')]
    pos = api.get_player_info(player, 'Pos')
    data[player] = {
        'dim': dim,
        'pos': pos,
        'time': time.time(),
        'back': {
            'dim': dim,
            'pos': pos
        }
    }
    server.execute(f'gamemode spectator {player}')
    data.save()


def spec_to_sur(server, player):
    dim = data[player]['dim']
    pos = [str(x) for x in data[player]['pos']]
    server.execute(
        'execute in {} run tp {} {}'.format(dim, player, ' '.join(pos)))
    server.execute(f'gamemode survival {player}')
    del data[player]
    data.save()


def on_player_joined(server, player, info):
    if player in data.keys():
        server.execute(f'gamemode spectator {player}')
