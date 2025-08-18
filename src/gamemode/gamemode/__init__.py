# -*- coding: utf-8 -*-
import os
import json
import time
import threading
from math import ceil, floor
from dataclasses import dataclass
from typing import Optional, Any, Literal, Text, Set, List, Callable

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


@dataclass
class Coordinate:
    x: float = 0
    y: float = 0
    z: float = 0


class BaseConfig(Serializable):
    version: int

    def migrate(self) -> "BaseConfig":
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

    def migrate(self) -> "ConfigV2":
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


def nether_to_overworld(x, z):
    return int(float(x)) * 8, int(float(z)) * 8


def overworld_to_nether(x, z):
    return floor(float(x) / 8 + 0.5), floor(float(z) / 8 + 0.5)


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
    def change_mode(src: PlayerCommandSource, ctx: CommandContext):
        player = src.player if ctx == {} else ctx['player']

        # check player is online if changing other's mode
        if ctx != {} and not online_player_api.is_online(player):
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
    def tp(src: PlayerCommandSource, ctx: CommandContext):
        def is_coord_valid(coord: str):
            if coord == '~':
                return True
            if (
                    coord.startswith('.') or
                    coord.endswith('.') or
                    coord.count('.') > 1 or
                    (coord.count('-') >= 1 and not coord.startswith('-'))
            ):
                return False
            coord = coord.replace('-', '')
            coord = coord.replace('.', '')
            if coord.isdigit():
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

        tp_type: Literal["to_player", "to_coordinate"] = 'to_coordinate'
        to_player = ''
        to_coordinate = Coordinate()
        to_coordinate_dim = ''


        player_original_pos = minecraft_data_api.get_player_coordinate(src.player)
        player_original_dim = DIMENSIONS[str(minecraft_data_api.get_player_dimension(src.player))]

        if len(params) == 1:  # only dimension, or player name: e.g. !!tp the_end / !!tp Steve
            if params[0] not in DIMENSIONS.keys():
                # not a dimension, validate if it's an online player name
                player = params[0]
                if not online_player_api.is_online(player):
                    return src.reply(
                        f'§c指定的 §e{params[0]} §c既不是维度，也不是一个在线的玩家'
                    )
                else:
                    tp_type = "to_player"
                    to_player = player
            elif DIMENSIONS[params[0]] == player_original_dim:
                # player is already in the target dimension
                return src.reply('§c您正在此维度！')
            elif (DIMENSIONS[params[0]] == 'minecraft:the_nether') and (player_original_dim == 'minecraft:overworld'):
                # The player is in the Overworld and wishes to tp to the corresponding coordinates in the Nether
                tp_type = "to_coordinate"
                to_coordinate_dim = DIMENSIONS[params[0]]
                newposx, newposz = overworld_to_nether(player_original_pos.x, player_original_pos.z)
                to_coordinate.x = float(newposx)
                to_coordinate.y = float(player_original_pos.y)
                to_coordinate.z = float(newposz)
            elif (DIMENSIONS[params[0]] == 'minecraft:overworld') and (player_original_dim == 'minecraft:the_nether'):
                # The player is in the Nether and wishes to tp to the corresponding coordinates in the Overworld
                tp_type = "to_coordinate"
                to_coordinate_dim = DIMENSIONS[params[0]]
                newposx, newposz = nether_to_overworld(player_original_pos.x, player_original_pos.z)
                to_coordinate.x = float(newposx)
                to_coordinate.y = float(player_original_pos.y)
                to_coordinate.z = float(newposz)
            else:
                # normal tp
                tp_type = "to_coordinate"
                to_coordinate_dim = DIMENSIONS[params[0]]
                to_coordinate.x = 0
                to_coordinate.y = 80
                to_coordinate.z = 0

        elif len(params) == 3:  # only position: e.g. !!tp x y z
            if (not is_coord_valid(params[0])) or (not is_coord_valid(params[1])) or (not is_coord_valid(params[2])):
                return src.reply('§c坐标不合法')
            if (params[0] == '~' and params[1] == '~' and params[2] == '~'):
                return src.reply('§c原地 tp 是吧 (doge)')
            to_coordinate_dim = player_original_dim
            to_coordinate.x = float(params[0] if params[0] != '~' else player_original_pos.x)
            to_coordinate.y = float(params[1] if params[1] != '~' else player_original_pos.y)
            to_coordinate.z = float(params[2] if params[2] != '~' else player_original_pos.z)

        elif len(params) == 4:  # dimension + position: e.g. !!tp the_end x y z
            if params[0] not in DIMENSIONS.keys():
                return src.reply('§c没有此维度')
            if (player_original_dim == DIMENSIONS[params[0]] and params[1] == '~' and params[2] == '~' and params[3] == '~'):
                return src.reply('§c原地 tp 是吧 (doge)')
            if (not is_coord_valid(params[1])) or (not is_coord_valid(params[2])) or (not is_coord_valid(params[3])):
                return src.reply('§c坐标不合法')
            
            tp_type = "to_coordinate"
            to_coordinate_dim = DIMENSIONS[params[0]]
            to_coordinate.x = float(params[1] if params[1] != '~' else player_original_pos.x)
            to_coordinate.y = float(params[2] if params[2] != '~' else player_original_pos.y)
            to_coordinate.z = float(params[3] if params[3] != '~' else player_original_pos.z)

        data[src.player]['back'] = {
            'dim': player_original_dim,
            'pos': player_original_pos,
        }
        save_data(server)
        if (tp_type == "to_player"):
            server.execute(f'tp {src.player} {to_player}')
            src.reply(f'§a已传送至玩家 §e{to_player}')
        else: # to_coordinate
            server.execute(f'execute in {to_coordinate_dim} run tp {src.player} {to_coordinate.x} {to_coordinate.y} {to_coordinate.z}')
            human_readable_dim = HUMDIMS[to_coordinate_dim]
            human_readable_pos = ' '.join([str(int(to_coordinate.x)), str(int(to_coordinate.y)), str(int(to_coordinate.z))])
            src.reply(f'§a传送至§e{human_readable_dim}§a，坐标 §e{human_readable_pos}')

    @new_thread('Gamemode back')
    def back(src: PlayerCommandSource):
        if src.player not in data.keys():
            return src.reply('§c您只能在旁观模式下传送')
        back_to_dim = data[src.player]['back']['dim']
        back_to_pos = [str(x) for x in data[src.player]['back']['pos']]
        data[src.player]['back'] = {
            'dim': DIMENSIONS[str(minecraft_data_api.get_player_dimension(src.player))],
            'pos': minecraft_data_api.get_player_coordinate(src.player)
        }
        save_data(server)
        server.execute(
            f'execute in {back_to_dim} run tp {src.player} {" ".join(back_to_pos)}'
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
        for player in data.keys():
            if server.get_permission_level(player) < config.permissions.tp:
                monitor_players.add(player)

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


def save_data(server: PluginServerInterface):
    server.save_config_simple(
        {'data': data},
        DATA_FILE_NAME if config.data_path is None else config.data_path,
        in_data_folder=(config.data_path is None)
    )


def sur_to_spec(server, player):
    dim = DIMENSIONS[str(minecraft_data_api.get_player_dimension(player))]
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
    server.execute(
        'execute in {} run tp {} {}'.format(dim, player, ' '.join(pos)))
    if 'rotation' in data[player]:
        rotation = data[player]['rotation']
        server.execute(f'rotate {player} {str(rotation[0])} {str(rotation[1])}')
    server.execute(f'gamemode survival {player}')
    del data[player]
    save_data(server)


def load_config(server: PluginServerInterface) -> "LatestConfig":
    """
    Load config file with migration.
    """
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
        server.logger.exception("配置文件读取失败")
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
        server.logger.error(f"未知配置文件版本：{version}")
        raise RuntimeError(f"Unknown config version: {version}")
    current_config = server.load_config_simple(
        CONFIG_FILE_NAME, target_class=target_class
    )

    # migrate
    while current_config.version < CONFIG_LATEST_VERSION:
        current_config = current_config.migrate()
    server.save_config_simple(current_config, CONFIG_FILE_NAME)
    return current_config


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
