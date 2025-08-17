# -*- coding: utf-8 -*-
import time
import threading
from math import ceil, floor
from typing import Optional, Any, Set, Callable

from mcdreforged.api.types import PluginServerInterface, PlayerCommandSource
from mcdreforged.api.command import *
from mcdreforged.api.decorator import new_thread
from mcdreforged.api.utils import Serializable


class LoopManager:
    def __init__(self, run_function: Callable, interval: int):
        self.run_function = run_function
        self.interval = interval
        self._stop_event = threading.Event()
        self.thread = None

    def start(self):
        def loop():
            while not self._stop_event.wait(self.interval):
                self.run_function()

        # If a thread is already running, stop it before starting a new one
        if self.thread is not None and self.thread.is_alive():
            self.stop()
        self.thread = threading.Thread(target=loop, daemon=True)
        self.thread.start()

    def stop(self):
        if self.thread is not None:
            self._stop_event.set()
            self.thread.join()
            self.thread = None
            self._stop_event.clear()


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

HUMDIMS = {
    'minecraft:overworld': '主世界',
    'minecraft:the_nether': '下界',
    'minecraft:the_end': '末地'
}

DEFAULT_CONFIG = {
    'spec': 1,
    'spec_other': 2,
    'tp': 1,
    'back': 1
}

HELP_MESSAGE = '''§6!!spec §7旁观/生存切换
§6!!spec <player> §7切换他人模式
§6!!tp [dimension] [position] §7传送至指定地点
§6!!back §7返回上个地点'''


class Config(Serializable):
    short_command: bool = True
    spec: int = 1
    spec_other: int = 2
    tp: int = 1
    back: int = 1

    class RangeLimit(Serializable):
        check_interval: int = 0
        x: int = 50
        y: int = 50
        z: int = 50

    range_limit: RangeLimit = RangeLimit()


config: Config
data: dict
monitor_players: Set[str] = set()
minecraft_data_api: Optional[Any]
loop_manager: Optional[LoopManager]


def nether_to_overworld(x, z):
    return int(float(x)) * 8, int(float(z)) * 8


def overworld_to_nether(x, z):
    return floor(float(x) / 8 + 0.5), floor(float(z) / 8 + 0.5)


def on_load(server: PluginServerInterface, old):
    global config, data, minecraft_data_api, loop_manager
    config = server.load_config_simple(
        'config.json',
        default_config=DEFAULT_CONFIG,
        target_class=Config
    )
    data = server.load_config_simple(
        'data.json',
        default_config={'data': {}},
        echo_in_console=False
    )['data']
    minecraft_data_api = server.get_plugin_instance('minecraft_data_api')

    server.register_help_message('!!spec help', 'Gamemode 插件帮助')

    def check_player_pos():
        radius = [
            config.range_limit.x,
            config.range_limit.y,
            config.range_limit.z
        ]
        for player in monitor_players.copy():
            center = [x for x in data[player]['pos']]
            pos = minecraft_data_api.get_player_info(player, 'Pos')
            if pos is None:
                server.logger.warning(
                    f'无法获取玩家 {player} 的位置，可能是玩家不在线'
                )
                continue

            valid_ranges = [
                (center[i] - radius[i], center[i] + radius[i])
                if radius[i] > 0
                else None
                for i in range(3)
            ]

            need_teleport = False
            for i in range(3):
                if valid_ranges[i] is None:
                    continue
                if pos[i] < valid_ranges[i][0]:
                    need_teleport = True
                    pos[i] = valid_ranges[i][0] + 0.5
                elif pos[i] > valid_ranges[i][1]:
                    need_teleport = True
                    pos[i] = valid_ranges[i][1] - 0.5

            if need_teleport:
                server.execute(f'tp {player} {pos[0]} {pos[1]} {pos[2]}')
                server.tell(
                    player,
                    '§c您已超出活动范围，已被自动传送回活动范围内'
                )

    @new_thread('Gamemode switch mode')
    def change_mode(src: PlayerCommandSource, ctx: CommandContext):
        player = src.player if ctx == {} else ctx['player']
        if player not in data.keys():
            server.tell(player, '§a已切换至旁观模式')
            sur_to_spec(server, player)
            if not src.has_permission(config.tp):
                monitor_players.add(player)
        elif player in data.keys():
            use_time = ceil((time.time() - data[player]['time']) / 60)
            server.tell(player, f'§a您使用了§e{use_time}min')
            spec_to_sur(server, player)
            if player in monitor_players:
                monitor_players.discard(player)

    @new_thread('Gamemode tp')
    def tp(src: PlayerCommandSource, ctx: CommandContext):
        def is_coord_valid(a):
            if (
                    a.count('-') > 1 or
                    a.count('.') > 1 or
                    a.startswith('.') or
                    a.endswith('.')
            ):
                return False
            a = a.replace('-', '')
            a = a.replace('.', '')
            if a.isdigit():
                return True
            return False

        if src.player not in data.keys():
            src.reply('§c您只能在旁观模式下传送')

        params = []

        if ctx.get('param1', '') != '':
            params.append(ctx['param1'])
            if ctx.get('param2', '') != '':
                params.append(ctx['param2'])
                if ctx.get('param3', '') != '':
                    params.append(ctx['param3'])
                    if ctx.get('param4', '') != '':
                        params.append(ctx['param4'])

        dim = ''
        pos = ''
        humpos = ''

        if len(params) == 1:  # only dimension
            if params[0] not in DIMENSIONS.keys():
                src.reply('§c没有此维度')
            elif DIMENSIONS[params[0]] == DIMENSIONS[
                minecraft_data_api.get_player_info(src.player, 'Dimension')
            ]:
                src.reply('§c您正在此维度！')
            elif (DIMENSIONS[params[0]] == 'minecraft:the_nether') and (
                    DIMENSIONS[
                        minecraft_data_api.get_player_info(
                            src.player, 'Dimension'
                        )
                    ] == 'minecraft:overworld'):
                dim = DIMENSIONS[params[0]]
                orgpos = [
                    str(x) for x in
                    minecraft_data_api.get_player_info(src.player, 'Pos')
                ]
                newposx, newposz = overworld_to_nether(orgpos[0], orgpos[2])
                pos = ' '.join((str(newposx), orgpos[1], str(newposz)))
                humpos = ' '.join(
                    (str(newposx), str(int(float(orgpos[1]))), str(newposz))
                )
            elif (DIMENSIONS[params[0]] == 'minecraft:overworld') and (
                    DIMENSIONS[
                        minecraft_data_api.get_player_info(
                            src.player, 'Dimension'
                        )
                    ] == 'minecraft:the_nether'):
                dim = DIMENSIONS[params[0]]
                orgpos = [
                    str(x) for x in
                    minecraft_data_api.get_player_info(src.player, 'Pos')
                ]
                newposx, newposz = nether_to_overworld(orgpos[0], orgpos[2])
                pos = ' '.join((str(newposx), orgpos[1], str(newposz)))
                humpos = ' '.join(
                    (str(newposx), str(int(float(orgpos[1]))), str(newposz))
                )
            else:
                dim = DIMENSIONS[params[0]]
                pos = '0 80 0'
                humpos = '0 80 0'

        elif len(params) == 3:  # only position
            if not is_coord_valid(params[0]):
                src.reply('§c坐标不合法')
            else:
                dim = DIMENSIONS[
                    minecraft_data_api.get_player_info(src.player, 'Dimension')
                ]
                pos = ' '.join(
                    (
                        str(float(params[0])),
                        str(params[1]),
                        str(params[2])
                    )
                )
                humpos = ' '.join(
                    (
                        str(int(float(params[0]))),
                        str(int(params[1])),
                        str(int(params[2]))
                    )
                )

        elif len(params) == 4:  # dimension + position
            if params[0] not in DIMENSIONS.keys():
                src.reply('§c没有此维度')
            else:
                dim = DIMENSIONS[params[0]]

            pos = ' '.join((str(params[1]), str(params[2]), str(params[3])))
            humpos = ' '.join(
                (str(int(params[1])), str(int(params[2])), str(int(params[3])))
            )

        if dim != '' and pos != '' and params != '':
            data[src.player]['back'] = {
                'dim': DIMENSIONS[
                    minecraft_data_api.get_player_info(src.player, 'Dimension')
                ],
                'pos': minecraft_data_api.get_player_info(src.player, 'Pos')
            }
            save_data(server)
            server.execute(f'execute in {dim} run tp {src.player} {pos}')
            humdim = HUMDIMS[dim]
            src.reply(f'§a传送至§e{humdim}§a, 坐标§e{humpos}')

    @new_thread('Gamemode back')
    def back(src: PlayerCommandSource):
        if src.player not in data.keys():
            src.reply('§c您只能在旁观模式下传送')
        else:
            dim = data[src.player]['back']['dim']
            pos = [str(x) for x in data[src.player]['back']['pos']]
            data[src.player]['back'] = {
                'dim': DIMENSIONS[
                    minecraft_data_api.get_player_info(
                        src.player, 'Dimension'
                    )
                ],
                'pos': minecraft_data_api.get_player_info(src.player, 'Pos')
            }
            save_data(server)
            server.execute(
                f'execute in {dim} run tp {src.player} {" ".join(pos)}'
            )
            src.reply('§a已将您传送至上个地点')

    # enable range check
    range_check_enabled = (
            config.range_limit.check_interval > 0 and
            (
                    config.range_limit.x > 0 or
                    config.range_limit.y > 0 or
                    config.range_limit.z > 0
            )
    )
    if range_check_enabled:
        loop_manager = LoopManager(
            check_player_pos,
            config.range_limit.check_interval
        )
        loop_manager.start()

    # spec literals
    spec_literals = ['!!spec']
    if config.short_command:
        spec_literals.append('!s')

    # register
    server.register_command(
        Literal(spec_literals)
        .requires(Requirements.is_player(), lambda: '§c仅允许玩家使用')
        .requires(
            Requirements.has_permission(config.spec),
            lambda: '§c权限不足'
        )
        .runs(change_mode)
        .then(
            Literal('help')
            .runs(lambda src: src.reply(HELP_MESSAGE))
        )
        .then(
            Text('player')
            .requires(
                Requirements.has_permission(config.spec_other),
                lambda: '§c权限不足'
            )
            .runs(change_mode)
        )
    )
    server.register_command(
        Literal('!!tp')
        .requires(Requirements.is_player(), lambda: '§c仅允许玩家使用')
        .requires(Requirements.has_permission(config.tp), lambda: '§c权限不足')
        .then(
            Text('param1')
            .runs(tp).  # !!tp <dimension> -- param1 = dimension
            then(
                Float('param2')
                .then(
                    Float('param3')
                    # !!tp <x> <y> <z> -- param1 = x, param2 = y, param3 = z
                    .runs(tp)
                    .then(
                        # !!tp <dimension> <x> <y> <z> -- param1 = dimension, param2 = x, param3 = y, param4 = z
                        Float('param4')
                        .runs(tp)
                    )
                )
            )
        )
    )
    server.register_command(
        Literal('!!back')
        .requires(Requirements.is_player(), lambda: '§c仅允许玩家使用')
        .requires(
            Requirements.has_permission(config.back),
            lambda: '§c权限不足'
        )
        .runs(back)
    )


def save_data(server: PluginServerInterface):
    server.save_config_simple({'data': data}, 'data.json')


def sur_to_spec(server, player):
    dim = DIMENSIONS[minecraft_data_api.get_player_info(player, 'Dimension')]
    pos = minecraft_data_api.get_player_info(player, 'Pos')
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
    save_data(server)


def spec_to_sur(server, player):
    dim = data[player]['dim']
    pos = [str(x) for x in data[player]['pos']]
    server.execute(
        'execute in {} run tp {} {}'.format(dim, player, ' '.join(pos)))
    server.execute(f'gamemode survival {player}')
    del data[player]
    save_data(server)


def on_player_joined(server: PluginServerInterface, player, info):
    if player in data.keys():
        server.execute(f'gamemode spectator {player}')
        if server.get_permission_level(player) < config.tp:
            monitor_players.add(player)


def on_player_left(server: PluginServerInterface, player):
    if player in data.keys():
        monitor_players.discard(player)


def on_unload(server: PluginServerInterface):
    global loop_manager
    if loop_manager is not None:
        loop_manager.stop()
        loop_manager = None
