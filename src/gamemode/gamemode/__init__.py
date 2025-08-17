# -*- coding: utf-8 -*-
import time
from math import ceil, floor
from typing import Optional, Any
from os import path
import json

from mcdreforged.api.types import PluginServerInterface, PlayerCommandSource
from mcdreforged.api.command import *
from mcdreforged.api.decorator import new_thread
from mcdreforged.api.utils import Serializable

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

HELP_MESSAGE = '''§6!!spec §7旁观/生存切换
§6!!spec <player> §7切换他人模式
§6!!tp [dimension] [position] §7传送至指定地点
§6!!back §7返回上个地点'''


class ConfigV1(Serializable):
    short_command: bool = True
    spec: int = 1
    spec_other: int = 2
    tp: int = 1
    back: int = 1

    config_version: int = 1

    def migrate_to_config_v2(self) -> "ConfigV2":
        config_v2 = ConfigV2()
        config_v2.short_command.enabled = self.short_command
        config_v2.permissions.spec = self.spec
        config_v2.permissions.spec_other = self.spec_other
        config_v2.permissions.tp = self.tp
        config_v2.permissions.back = self.back
        return config_v2

class ConfigV2(Serializable):
    class Permissions(Serializable):
        spec: int = 1
        spec_other: int = 2
        tp: int = 1
        back: int = 1
    class ShortCommand(Serializable):
        enabled: bool = False

    config_version: int = 2
    permissions: Permissions = Permissions()
    short_command: ShortCommand = ShortCommand()

config: ConfigV2
data: dict
minecraft_data_api: Optional[Any]


def nether_to_overworld(x, z):
    return int(float(x)) * 8, int(float(z)) * 8


def overworld_to_nether(x, z):
    return floor(float(x) / 8 + 0.5), floor(float(z) / 8 + 0.5)


def on_load(server: PluginServerInterface, old):
    global config, data, minecraft_data_api
    config = load_config(server)
    data = server.load_config_simple(
        'data.json',
        default_config={'data': {}},
        echo_in_console=False
    )['data']
    minecraft_data_api = server.get_plugin_instance('minecraft_data_api')

    server.register_help_message('!!spec help', 'Gamemode 插件帮助')

    @new_thread('Gamemode switch mode')
    def change_mode(src: PlayerCommandSource, ctx):
        if src.is_console:
            return src.reply('§c仅允许玩家使用')
        player = src.player
        # is spec_other (!!spec Steve)
        if not ctx == {}:
            # Check if the player exists and correct the capitalization of the player name
            player = check_player_online_and_get_player_correct_name(ctx['player'])
            if (player == False):
                return src.reply(f'§c指定的玩家 §d{ctx['player']}§c 不在线或不存在')
        if player not in data.keys():
            server.tell(player, '§a已切换至旁观模式')
            sur_to_spec(server, player)
        elif player in data.keys():
            use_time = ceil((time.time() - data[player]['time']) / 60)
            server.tell(player, f'§a您使用了§e{use_time}min')
            spec_to_sur(server, player)

    @new_thread('Gamemode tp')
    def tp(src: PlayerCommandSource, ctx):
        def coordValid(a):
            if a.count('-') > 1 or a.count('.') > 1 or a.startswith(
                    '.') or a.endswith('.'):
                return False
            a = a.replace('-', '')
            a = a.replace('.', '')
            if a.isdigit():
                return True
            return False

        if src.is_console:
            return src.reply('§c仅允许玩家使用')
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

        player_original_pos = minecraft_data_api.get_player_coordinate(src.player)
        player_original_dim = DIMENSIONS[str(minecraft_data_api.get_player_dimension(src.player))]

        if len(params) == 1:  # only dimension
            if params[0] not in DIMENSIONS.keys():
                src.reply('§c没有此维度')
            elif DIMENSIONS[params[0]] == player_original_dim:
                src.reply('§c您正在此维度！')
            elif (DIMENSIONS[params[0]] == 'minecraft:the_nether') and (player_original_dim == 'minecraft:overworld'):
                dim = DIMENSIONS[params[0]]
                orgpos = [
                    str(x) for x in player_original_pos
                ]
                newposx, newposz = overworld_to_nether(orgpos[0], orgpos[2])
                pos = ' '.join((str(newposx), orgpos[1], str(newposz)))
                humpos = ' '.join(
                    (str(newposx), str(int(float(orgpos[1]))), str(newposz))
                )
            elif (DIMENSIONS[params[0]] == 'minecraft:overworld') and (player_original_dim == 'minecraft:the_nether'):
                dim = DIMENSIONS[params[0]]
                orgpos = [
                    str(x) for x in player_original_pos
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
            if not coordValid(params[0]):
                src.reply('§c坐标不合法')
            else:
                dim = player_original_dim
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
        if src.is_console:
            return src.reply('§c仅允许玩家使用')
        if src.player not in data.keys():
            return src.reply('§c您只能在旁观模式下传送')
        else:
            dim = data[src.player]['back']['dim']
            pos = [str(x) for x in data[src.player]['back']['pos']]
            data[src.player]['back'] = {
                'dim': DIMENSIONS[str(minecraft_data_api.get_player_dimension(src.player))],
                'pos': minecraft_data_api.get_player_coordinate(src.player)
            }
            save_data(server)
            server.execute(
                f'execute in {dim} run tp {src.player} {" ".join(pos)}'
            )
            src.reply('§a已将您传送至上个地点')

    # spec literals
    spec_literals = ['!!spec']
    if config.short_command.enabled:
        spec_literals.append('!s')

    # register
    server.register_command(
        Literal(spec_literals)
        .requires(lambda src: src.has_permission(config.permissions.spec))
        .runs(change_mode)
        .then(
            Literal('help')
            .runs(lambda src: src.reply(HELP_MESSAGE))
        )
        .then(
            Text('player')
            .requires(
                lambda src: src.has_permission(config.permissions.spec_other)
            )
            .runs(change_mode)
        )
    )
    server.register_command(
        Literal('!!tp')
        .requires(lambda src: src.has_permission(config.permissions.tp))
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
        .requires(lambda src: src.has_permission(config.permissions.back))
        .runs(back)
    )


def save_data(server: PluginServerInterface):
    server.save_config_simple({'data': data}, 'data.json')


def sur_to_spec(server, player):
    dim = DIMENSIONS[str(minecraft_data_api.get_player_dimension(player))]
    pos = minecraft_data_api.get_player_coordinate(player)
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


def check_player_online_and_get_player_correct_name(player):
    """
    Check if a player with the given name (case-insensitive) is online,
    returning the correctly-cased name if online, otherwise `False`.

    :param minecraft_data_api: Minecraft data api
    :param player: Case-insensitive player name
    
    :return: Correctly-cased player name if online, False if offline
    """
    all_online_players = minecraft_data_api.get_server_player_list()[2]
    for a_online_player in all_online_players:
        if player.lower() == a_online_player.lower():
            return a_online_player
    return False



def load_config(server: PluginServerInterface) -> "ConfigV2":
    """
    Load config file with automatic version migration
    """
    # Did not use PluginServerInterface.load_config_simple due to its excessive limitations,
    # and instead implemented manual reading. After extensive testing, version migration 
    # couldn't be achieved through the API (not unusable but would require double file
    # reading, wasting I/O resources).
    #
    # Key limitations encountered:
    # - Either `default_config` or `target_class` must be provided (both cannot be None)
    # - Automatically deletes keys present in config file but missing in `default_config`,
    #   making it impossible to pass `default_config={}` for pure file reading
    # - Certain edge cases cause file overwriting even when `data_processor` returns False,
    #   leading to potential config loss

    config_file_path = path.join(server.get_data_folder(), 'config.json')
    # create a config file if none exists
    if not path.isfile(config_file_path):
        config_v2 = ConfigV2()
        server.save_config_simple(config_v2, 'config.json')
        return config_v2
    # try to read config file
    try:
        with open(config_file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except Exception as e:
        server.logger.error(f"配置文件读取失败: {e}，正在使用默认配置 (不会覆盖保存原有配置, 以免丢失配置. 请修复或删除 {config_file_path})")
        return ConfigV2()
    # get config file version, `v1` if none
    config_version = raw_data.get('config_version', 1)
    if config_version == 1:
        # migrate to v2
        config_v1 = ConfigV1.deserialize(raw_data)
        config_v2 = config_v1.migrate_to_config_v2()
        server.save_config_simple(config_v2, 'config.json')
        return config_v2
    elif config_version == 2:
        return ConfigV2.deserialize(raw_data)
    else:
        server.logger.warning(f"未知配置版本 {config_version}，正在使用默认配置")
        return ConfigV2()


def on_player_joined(server, player, info):
    if player in data.keys():
        server.execute(f'gamemode spectator {player}')
