# -*- coding: utf-8 -*-
import re
import os
import json
import time
import typing
import threading
from math import ceil, floor
from dataclasses import dataclass
from typing import Optional, Any, Text, Set, List, Callable

from mcdreforged.api.types import PluginServerInterface, CommandSource, \
    PlayerCommandSource
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
        self.thread = threading.Thread(
            target=loop,
            name='Gamemode-LoopManager',
            daemon=True
        )
        self.thread.start()

    def stop(self):
        if self.thread is not None:
            self._stop_event.set()
            self.thread.join()
            self.thread = None
            self._stop_event.clear()


class BaseConfig(Serializable):
    version: int

    def migrate(self) -> 'BaseConfig':
        """
        Migrate the config to the latest version.
        This method should be overridden in subclasses.
        """
        raise NotImplementedError


class ConfigV1(BaseConfig):
    version: int = 1

    short_command: bool = True
    spec: int = 1
    spec_other: int = 2
    tp: int = 1
    back: int = 1

    def migrate(self) -> 'ConfigV2':
        config_v2 = ConfigV2()
        config_v2.short_commands = ['!s'] if self.short_command else []
        config_v2.permissions.spec = self.spec
        config_v2.permissions.spec_other = self.spec_other
        config_v2.permissions.tp = self.tp
        config_v2.permissions.back = self.back
        return config_v2


class ConfigV2(BaseConfig):
    class Permissions(Serializable):
        spec: int = 1
        spec_other: int = 2
        tp: int = 1
        back: int = 1

    class RangeLimit(Serializable):
        check_interval: int = 0
        x: int = 50
        y: int = 50
        z: int = 50

    version: int = 2

    data_path: Optional[str] = None
    short_commands: List[str] = ['!s']
    permissions: Permissions = Permissions()
    range_limit: RangeLimit = RangeLimit()


LatestConfig = ConfigV2

OVERWORLD = 'minecraft:overworld'
THE_NETHER = 'minecraft:the_nether'
THE_END = 'minecraft:the_end'

DIMENSIONS = {
    '0': OVERWORLD,
    '-1': THE_NETHER,
    '1': THE_END,
    'overworld': OVERWORLD,
    'the_nether': THE_NETHER,
    'the_end': THE_END,
    'nether': THE_NETHER,
    'end': THE_END,
    'minecraft:overworld': OVERWORLD,
    'minecraft:the_nether': THE_NETHER,
    'minecraft:the_end': THE_END
}

HUMAN_READABLE_DIMENSIONS = {
    OVERWORLD: '主世界',
    THE_NETHER: '下界',
    THE_END: '末地'
}

HELP_MESSAGE = '''§6!!spec §7切换旁观/生存
§6!!spec <player> §7切换他人模式
§6!!tp <player> §7传送至指定玩家
§6!!tp <dimension> §7传送至指定维度（主世界与下界自动换算坐标）
§6!!tp [dimension] <x> <y> <z> §7传送至（指定维度的）指定坐标
§6!!back §7返回上个地点'''

CONFIG_FILE_NAME = 'config.json'
DATA_FILE_NAME = 'data.json'

CONFIG_LATEST_VERSION = 2
CONFIG_VERSION_MAP = {
    1: ConfigV1,
    2: ConfigV2,
}

config: LatestConfig
data: dict
monitor_players: Set[str] = set()
loop_manager: Optional[LoopManager] = None
minecraft_data_api: Optional[Any] = None
online_player_api: Optional[Any] = None


def nether_to_overworld(x, z) -> tuple[int, int]:
    """Convert nether coordinates to overworld coordinates."""
    return int(float(x)) * 8, int(float(z)) * 8


def overworld_to_nether(x, z) -> tuple[int, int]:
    """Convert overworld coordinates to nether coordinates."""
    return floor(float(x) / 8 + 0.5), floor(float(z) / 8 + 0.5)


def is_coord_valid(coord: str):
    """Check if a coordinate is valid."""
    # ~
    if coord == '~':
        return True

    # number
    pattern = re.compile(r'^-?(?:\d+(\.\d*)?|\.\d+)$')
    return pattern.match(coord) is not None


def is_coord_in_range(x: float, y: float, z: float):
    """Check if coordinates are in range"""
    # Destinated position's <x> or <z> exceeds the range of
    # [-30000000, 30000000), or <y> exceeds the range of
    # [-20000000, 20000000) will cause tp to fail
    return (
        x <= 30000000 and x > -30000000 and
        y <= 20000000 and y > -20000000 and
        z <= 30000000 and z > -30000000
    )


def has_dimension(dim: str):
    """Check if a dimension exists."""
    return dim in DIMENSIONS.keys()


def normalize_dimension(dim: str):
    """Normalize a dimension string to a standard format."""
    if dim in DIMENSIONS.keys():
        return DIMENSIONS[dim]
    else:
        raise ValueError(f'dimension {dim} not exist')


def load_config(server: PluginServerInterface) -> 'LatestConfig':
    """Load config file with migration."""
    # create a config file if none exists
    config_file_path = os.path.join(server.get_data_folder(), CONFIG_FILE_NAME)
    if not os.path.isfile(config_file_path):
        return server.load_config_simple(
            CONFIG_FILE_NAME, target_class=LatestConfig
        )

    # read the config file
    try:
        with open(config_file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except Exception as e:
        server.logger.exception('配置文件读取失败')
        raise e

    # get the config version
    version = raw_data.get('version', 1)

    # latest config version
    if version == CONFIG_LATEST_VERSION:
        return server.load_config_simple(
            CONFIG_FILE_NAME, target_class=LatestConfig
        )

    # load config based on the version
    target_class = CONFIG_VERSION_MAP.get(version, None)
    if target_class is None:
        server.logger.error(f'未知配置文件版本：{version}')
        raise RuntimeError(f'Unknown config version: {version}')
    current_config = server.load_config_simple(
        CONFIG_FILE_NAME, target_class=target_class
    )

    # migrate
    while current_config.version < CONFIG_LATEST_VERSION:
        current_config = current_config.migrate()
    server.save_config_simple(current_config, CONFIG_FILE_NAME)
    return current_config


def on_load(server: PluginServerInterface, old):
    global config, data, loop_manager, minecraft_data_api, online_player_api
    config = load_config(server)
    data = server.load_config_simple(
        DATA_FILE_NAME if config.data_path is None else config.data_path,
        default_config={'data': {}},
        in_data_folder=(config.data_path is None),
        echo_in_console=False
    )['data']
    minecraft_data_api = server.get_plugin_instance('minecraft_data_api')
    online_player_api = server.get_plugin_instance('online_player_api')

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
    def change_mode(src: CommandSource, ctx: CommandContext):
        # assert src is a PlayerCommandSource
        if not isinstance(src, PlayerCommandSource):
            raise TypeError('Not a PlayerCommandSource')

        # get player name
        player = src.player if ctx == {} else ctx['player']

        # if changing other's mode, check player is online and normalize name
        if ctx != {}:
            try:
                player = online_player_api.normalize_player_name(player)
            except ValueError:
                src.reply(f'§c指定的玩家 §e{ctx['player']} §c不在线')
                return

        # change mode
        if player not in data.keys():
            server.tell(player, '§a已切换至旁观模式')
            sur_to_spec(server, player)
            if not src.has_permission(config.permissions.tp):
                monitor_players.add(player)
        elif player in data.keys():
            use_time = ceil((time.time() - data[player]['time']) / 60)
            server.tell(player, f'§a您使用了§e{use_time}min')
            spec_to_sur(server, player)
            if player in monitor_players:
                monitor_players.discard(player)

    @new_thread('Gamemode tp')
    def tp(src: CommandSource, ctx: CommandContext):
        @dataclass
        class TeleportData:
            tp_type: typing.Literal[
                'to_player',
                'to_coordinate'
            ] = 'to_coordinate'
            player: str = ''
            dimension: str = ''
            x: str | int | float = 0
            y: str | int | float = 0
            z: str | int | float = 0

        # assert src is a PlayerCommandSource
        if not isinstance(src, PlayerCommandSource):
            raise TypeError('Not a PlayerCommandSource')

        # spec mode only
        if src.player not in data.keys():
            src.reply('§c您只能在旁观模式下传送')
            return

        # parse params
        params = []
        if ctx.get('param1', '') != '':
            params.append(ctx['param1'])
            if ctx.get('param2', '') != '':
                params.append(ctx['param2'])
                if ctx.get('param3', '') != '':
                    params.append(ctx['param3'])
                    if ctx.get('param4', '') != '':
                        params.append(ctx['param4'])

        # tp data
        tp_data = TeleportData(
            tp_type='to_coordinate',
            player='',
            dimension='',
            x=0,
            y=0,
            z=0
        )

        # get current position and dimension
        current_pos = minecraft_data_api.get_player_coordinate(
            src.player
        )
        current_dim = normalize_dimension(
            str(minecraft_data_api.get_player_dimension(src.player))
        )

        # only dimension, or player name
        # e.g. !!tp the_end / !!tp Steve
        if len(params) == 1:
            # not a dimension, validate if it's an online player name
            if not has_dimension(params[0]):
                player = params[0]
                try:
                    player = online_player_api.normalize_player_name(player)
                except ValueError:
                    src.reply(
                        f'§c指定的 §e{player} §c既不是维度，也不是一个在线的玩家'
                    )
                    return
                else:
                    tp_data.tp_type = 'to_player'
                    tp_data.player = player
            # player is already in the target dimension
            elif normalize_dimension(params[0]) == current_dim:
                src.reply('§c您正在此维度！')
                return
            # The player is in the Overworld and wishes to tp to the corresponding coordinates in the Nether
            elif (
                    normalize_dimension(params[0]) == THE_NETHER and
                    current_dim == OVERWORLD
            ):
                tp_data.tp_type = 'to_coordinate'
                tp_data.dimension = normalize_dimension(params[0])
                nether_x, nether_z = overworld_to_nether(
                    current_pos.x, current_pos.z
                )
                tp_data.x = nether_x
                tp_data.y = current_pos.y
                tp_data.z = nether_z
            # The player is in the Nether and wishes to tp to the corresponding coordinates in the Overworld
            elif (
                    normalize_dimension(params[0]) == OVERWORLD and
                    current_dim == THE_NETHER
            ):
                tp_data.tp_type = 'to_coordinate'
                tp_data.dimension = normalize_dimension(params[0])
                overworld_x, overworld_z = nether_to_overworld(
                    current_pos.x, current_pos.z
                )
                tp_data.x = overworld_x
                tp_data.y = current_pos.y
                tp_data.z = overworld_z
            # default position in the target dimension
            else:
                tp_data.tp_type = 'to_coordinate'
                tp_data.dimension = normalize_dimension(params[0])
                tp_data.x = 0
                tp_data.y = 80
                tp_data.z = 0

        # only position: e.g. !!tp x y z
        elif len(params) == 3:
            # invalid coordinates
            if (
                    (not is_coord_valid(params[0])) or
                    (not is_coord_valid(params[1])) or
                    (not is_coord_valid(params[2])) or
                    (not is_coord_in_range(float(params[0]), float(params[1]), float(params[2])))
            ):
                src.reply('§c坐标不合法')
                return

            # current position
            if params[0] == '~' and params[1] == '~' and params[2] == '~':
                src.reply('§c原地 tp 是吧 (doge)')
                return

            # convert to coordinate
            tp_data.tp_type = 'to_coordinate'
            tp_data.dimension = current_dim
            tp_data.x = float(params[0] if params[0] != '~' else current_pos.x)
            tp_data.y = float(params[1] if params[1] != '~' else current_pos.y)
            tp_data.z = float(params[2] if params[2] != '~' else current_pos.z)

        # dimension + position: e.g. !!tp the_end x y z
        elif len(params) == 4:
            # invalid dimension
            if not has_dimension(params[0]):
                src.reply('§c没有此维度')
                return

            # invalid coordinates
            if (
                    (not is_coord_valid(params[1])) or
                    (not is_coord_valid(params[2])) or
                    (not is_coord_valid(params[3])) or
                    (not is_coord_in_range(float(params[1]), float(params[2]), float(params[3])))
            ):
                src.reply('§c坐标不合法')
                return

            # current position
            if (
                    current_dim == normalize_dimension(params[0]) and
                    params[0] == '~' and params[1] == '~' and params[2] == '~'
            ):
                src.reply('§c原地 tp 是吧 (doge)')
                return

            # convert to coordinate
            tp_data.tp_type = 'to_coordinate'
            tp_data.dimension = normalize_dimension(params[0])
            tp_data.x = float(params[1] if params[1] != '~' else current_pos.x)
            tp_data.y = float(params[2] if params[2] != '~' else current_pos.y)
            tp_data.z = float(params[3] if params[3] != '~' else current_pos.z)

        # update back position
        data[src.player]['back'] = {
            'dim': current_dim,
            'pos': current_pos,
        }
        save_data(server)

        # teleport the player
        if tp_data.tp_type == 'to_player':
            server.execute(f'tp {src.player} {tp_data.player}')
            src.reply(f'§a已传送至玩家 §e{tp_data.player}')
        elif tp_data.tp_type == 'to_coordinate':
            server.execute(
                f'execute in {tp_data.dimension} '
                f'run tp {src.player} {tp_data.x} {tp_data.y} {tp_data.z}'
            )
            human_readable_dim = HUMAN_READABLE_DIMENSIONS[tp_data.dimension]
            human_readable_pos = ' '.join([
                str(int(tp_data.x)),
                str(int(tp_data.y)),
                str(int(tp_data.z))
            ])
            src.reply(
                f'§a传送至§e{human_readable_dim}§a，坐标 §e{human_readable_pos}'
            )

    @new_thread('Gamemode back')
    def back(src: CommandSource):
        # assert src is a PlayerCommandSource
        if not isinstance(src, PlayerCommandSource):
            raise TypeError('Not a PlayerCommandSource')

        # spec mode only
        if src.player not in data.keys():
            src.reply('§c您只能在旁观模式下传送')
            return

        # back to previous position
        back_dim = data[src.player]['back']['dim']
        back_pos = [str(x) for x in data[src.player]['back']['pos']]
        current_dim = normalize_dimension(
            str(minecraft_data_api.get_player_dimension(src.player))
        )
        current_pos = minecraft_data_api.get_player_coordinate(src.player)
        data[src.player]['back'] = {
            'dim': current_dim,
            'pos': current_pos,
        }
        save_data(server)
        server.execute(
            f'execute in {back_dim} run tp {src.player} {" ".join(back_pos)}'
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

        # load monitored players
        for p in data.keys():
            if server.get_permission_level(p) < config.permissions.tp:
                monitor_players.add(p)

    # spec literals
    spec_literals = ['!!spec']
    help_message = HELP_MESSAGE
    if len(config.short_commands) > 0:
        spec_literals.extend(config.short_commands)
        help_message += f'\n§6!!spec §7可以使用下列简写替代: §6{", ".join(config.short_commands)}'

    # register
    server.register_command(
        Literal(spec_literals)
        .requires(Requirements.is_player(), lambda: '§c仅允许玩家使用')
        .requires(
            Requirements.has_permission(config.permissions.spec),
            lambda: '§c权限不足'
        )
        .runs(change_mode)
        .then(
            Literal('help')
            .runs(lambda src: src.reply(help_message))
        )
        .then(
            Text('player')
            .requires(
                Requirements.has_permission(config.permissions.spec_other),
                lambda: '§c权限不足'
            )
            .runs(change_mode)
        )
    )
    server.register_command(
        Literal('!!tp')
        .requires(Requirements.is_player(), lambda: '§c仅允许玩家使用')
        .requires(
            Requirements.has_permission(config.permissions.tp),
            lambda: '§c权限不足'
        )
        .then(
            # !!tp <dimension | player> -- param1 = dimension or player name
            Text('param1')
            .runs(tp).
            then(
                Text('param2')
                .then(
                    # !!tp <x> <y> <z> -- param1 = x, param2 = y, param3 = z
                    Text('param3')
                    .runs(tp)
                    .then(
                        # !!tp <dimension> <x> <y> <z> -- param1 = dimension, param2 = x, param3 = y, param4 = z
                        Text('param4')
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
            Requirements.has_permission(config.permissions.back),
            lambda: '§c权限不足'
        )
        .runs(back)
    )


def on_player_joined(server: PluginServerInterface, player, info):
    if player in data.keys():
        server.execute(f'gamemode spectator {player}')
        if server.get_permission_level(player) < config.permissions.tp:
            monitor_players.add(player)


def on_player_left(server: PluginServerInterface, player):
    if player in data.keys():
        monitor_players.discard(player)


def on_unload(server: PluginServerInterface):
    global loop_manager
    if loop_manager is not None:
        loop_manager.stop()
        loop_manager = None


def save_data(server: PluginServerInterface):
    server.save_config_simple(
        {'data': data},
        DATA_FILE_NAME if config.data_path is None else config.data_path,
        in_data_folder=(config.data_path is None)
    )


def sur_to_spec(server, player):
    dim = normalize_dimension(
        str(minecraft_data_api.get_player_dimension(player))
    )
    pos = minecraft_data_api.get_player_coordinate(player)
    rotation = minecraft_data_api.get_player_info(player, 'Rotation')
    data[player] = {
        'dim': dim,
        'pos': pos,
        'rotation': rotation,
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
    rotation = data[player].get('rotation', [0, 0])
    server.execute(f'execute in {dim} run tp {player} {" ".join(pos)}')
    server.execute(f'rotate {player} {rotation[0]} {rotation[1]}')
    server.execute(f'gamemode survival {player}')
    del data[player]
    save_data(server)
