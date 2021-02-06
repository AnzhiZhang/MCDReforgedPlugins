# -*- coding: utf-8 -*-
import re
import time

from JsonDataAPI import Json
from mcdreforged.plugin.server_interface import ServerInterface
from mcdreforged.api.command import *

PERMISSIONS = {
    'help': 2,
    'kick': 2,
    'ban': 3,
    'tempban': 3,
    'unban': 3,
    'banlist': 3
}

PLUGIN_METADATA = {
    'id': 'advanced_ban',
    'version': '0.0.1',
    'name': 'AdvancedBan',
    'description': 'A player manage plugin',
    'author': 'zhang_anzhi',
    'link': 'https://github.com/zhang-anzhi/MCDReforgedPlugins/tree/master/AdvancedBan',
    'dependencies': {
        'json_data_api': '*'
    }
}
data = Json(PLUGIN_METADATA['name'])
HELP_MESSAGE = '''------AdvancedBan 玩家管理插件------
§6!!ab §7显示帮助
§6!!kick <§6§oplayer§6> [§6§oreason§6] §7踢出玩家
§6!!ban <§6§oplayer§6> [§6§oreason§6] §7封禁玩家
§6!!tempban <§6§oplayer§6> <§6§otime§6> [§6§oreason§6] §7封禁玩家一段时间
§6!!unban <§6§oplayer§6> §7解禁玩家
§6!!banlist §7封禁列表'''


def register_command(server: ServerInterface):
    """Register commands"""
    # ab
    server.register_command(
        Literal('!!ab').
            requires(lambda src: src.has_permission(PERMISSIONS['help']),
                     lambda: '§c权限不足').
            runs(lambda src: src.reply(HELP_MESSAGE))
    )

    # kick
    server.register_command(
        Literal('!!kick').
            requires(lambda src: src.has_permission(PERMISSIONS['kick']),
                     failure_message_getter=lambda: '§c权限不足').
            then(
            Text('player').
                runs(lambda src, ctx: kick(src.get_server(), ctx['player'])).
                then(
                GreedyText('reason').
                    runs(lambda src, ctx: kick(src.get_server(), ctx['player'],
                                               ctx['reason']))
            )
        )
    )

    # ban
    def ban(src, ctx):
        player = ctx['player']
        if player in data.keys():
            return src.reply('§c该玩家已被封禁')
        data[player] = {
            'operator': src.player if src.is_player else None,
            'ban_time': int(time.time()),
            'unban_time': -1,
            'reason': ctx.get('reason', None)
        }
        data.save()
        baned_check(src.get_server(), player)
        src.reply(f'§c已封禁{player}')

    server.register_command(
        Literal('!!ban').
            requires(lambda src: src.has_permission(PERMISSIONS['ban']),
                     failure_message_getter=lambda: '§c权限不足').
            then(
            Text('player').
                runs(ban).
                then(
                GreedyText('reason').runs(ban)
            )
        )
    )

    # tempban
    def tempban(src, ctx):
        player = ctx['player']
        if player in data.keys():
            return src.reply('§c该玩家已被封禁')
        ban_time = int(time.time())
        try:
            unban_time = ban_time + calc_time(ctx['time'])
        except ValueError:
            return src.reply('§c时间不合法')
        data[player] = {
            'operator': src.player if src.is_player else None,
            'ban_time': ban_time,
            'unban_time': unban_time,
            'reason': ctx.get('reason', None)
        }
        data.save()
        baned_check(server, player)
        src.reply(f'§c已封禁{player}')

    server.register_command(
        Literal('!!tempban').
            requires(lambda src: src.has_permission(PERMISSIONS['tempban']),
                     failure_message_getter=lambda: '§c权限不足').
            then(
            Text('player').
                then(
                Text('time').
                    runs(tempban).
                    then(GreedyText('reason').runs(tempban)
                         )
            )
        )
    )

    # unban
    def unban(src, ctx):
        player = ctx['player']
        if player in data.keys():
            del data[player]
            src.reply(f'§a已解禁{player}')
            data.save()
        else:
            src.reply('§c该玩家未被封禁')

    server.register_command(
        Literal('!!unban').
            requires(lambda src: src.has_permission(PERMISSIONS['unban']),
                     failure_message_getter=lambda: '§c权限不足').
            then(Text('player').runs(unban))
    )

    # banlist
    def banlist(src):
        i = 0
        src.reply('§8>>> §7Banlist:')
        src.reply('§cPlayer §8| §e Duration §8| §7Banned by')
        src.reply('§cType §8> §7Reason')
        for player, info in data.items():
            i += 1
            if info['unban_time'] == -1:
                duration = 'permanent'
                ban_type = 'Ban'
            else:
                duration = f'{int(info["unban_time"] - time.time())}秒'
                ban_type = 'Tempban'
            src.reply('')
            src.reply('§8[§e{}§8]'.format(
                time.strftime(
                    '%Y.%m.%d-%H:%M', time.localtime(info['ban_time'])
                )
            ))
            src.reply(f'§c{player} §8| §e{duration} §8| §7{info["operator"]}')
            src.reply(f'§c{ban_type} §8> §7{info["reason"]}')

    server.register_command(
        Literal('!!banlist').
            requires(lambda src: src.has_permission(PERMISSIONS['banlist']),
                     failure_message_getter=lambda: '§c权限不足').
            runs(banlist)
    )


def on_load(server: ServerInterface, old):
    server.register_help_message('!!ab', 'AdvancedBan帮助信息',
                                 permission=min(PERMISSIONS.values()))
    register_command(server)


def on_player_joined(server, player, info):
    baned_check(server, player)


def kick(server, player, reason=None):
    reason = '' if reason is None else f' 原因: {reason}'
    reason = f'§c你被踢出游戏!' + reason
    server.logger.info(reason)
    server.execute(' '.join(['kick', player, reason]).rstrip(' '))


def calc_time(s):
    time_list = re.findall(r'[0-9]+|[a-z]{1,3}', s)
    total_time = 0

    if not time_list[0].isdigit() or len(time_list) % 2 != 0:
        raise ValueError('Not one value and one unit')

    while not len(time_list) == 0:
        unit = time_list[1]
        value = int(time_list[0])
        if unit == 's':
            total_time += value
        elif unit == 'm':
            total_time += value * 60
        elif unit == 'h':
            total_time += value * 60 * 60
        elif unit == 'd':
            total_time += value * 60 * 60 * 24
        elif unit == 'w':
            total_time += value * 60 * 60 * 24 * 7
        elif unit == 'mon':
            total_time += value * 60 * 60 * 24 * 30
        elif unit == 'y':
            total_time += value * 60 * 60 * 24 * 365
        else:
            raise ValueError('Unit of time is undefined')
        time_list.remove(time_list[0])
        time_list.remove(time_list[0])
    return total_time


def baned_check(server, player):
    if player in data.keys():
        reason = data[player]['reason']
        server.logger.info(reason)
        if data[player]['unban_time'] == -1:
            reason = f'永久封禁{"" if reason is None else f"（{reason}）"}'
            kick(server, player, reason)
        elif data[player]['unban_time'] > time.time():
            reason = '§c{}, 解禁时间: {}'.format(
                reason,
                time.strftime(
                    '%Y-%m-%d %H:%M:%S',
                    time.localtime(data[player]['unban_time'])
                )
            )
            kick(server, player, reason)
        elif data[player]['unban_time'] < time.time():
            del data[player]
            data.save()
