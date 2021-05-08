# -*- coding: utf-8 -*-
import requests

from mcdreforged.plugin.server_interface import ServerInterface
from mcdreforged.api.command import *

PLUGIN_METADATA = {
    'id': 'qq_chat',
    'version': '0.0.3',
    'name': 'QQChat',
    'description': 'Connect Minecraft and QQ',
    'author': 'zhang_anzhi',
    'link': 'https://github.com/zhang-anzhi/MCDReforgedPlugins/tree/master/QQChat',
    'dependencies': {
        'cool_q_api': '*',
        'online_player_api': '*',
        'config_api': '*',
        'json_data_api': '*'
    }
}
DEFAULT_CONFIG = {
    'group_id': [1234561, 1234562],
    'admin_id': [1234563, 1234564],
    'whitelist_add_with_bound': False,
    'whitelist_remove_with_leave': True,
    'forward': {
        'mc_to_qq': False,
        'qq_to_mc': False
    },
    'command': {
        'list': True,
        'mc': True,
        'qq': True,
    }
}
group_help_msg = '''命令帮助如下:
/list 获取在线玩家列表
/bound <ID> 绑定你的游戏ID
/mc <msg> 向游戏内发送消息
'''
admin_help_msg = '''管理员命令帮助如下
/bound 查看绑定相关帮助
/whitelist 查看白名单相关帮助
/command <command> 执行任意指令
'''
bound_help = '''/bound list 查看绑定列表
/bound check <qq number> 查询绑定ID
/bound unbound <qq number> 解除绑定
/bound <qq number> <ID> 绑定新ID
'''
whitelist_help = '''/whitelist add <target> 添加白名单成员
/whitelist list 列出白名单成员
/whitelist off 关闭白名单
/whitelist on 开启白名单
/whitelist reload 重载白名单
/whitelist remove <target> 删除白名单成员
<target> 可以是玩家名/目标选择器/UUID
'''


def on_load(server: ServerInterface, old):
    global config, data, host, port
    from ConfigAPI import Config
    from JsonDataAPI import Json
    config = Config(PLUGIN_METADATA['name'], DEFAULT_CONFIG)
    data = Json(PLUGIN_METADATA['name'])
    host = server.get_plugin_instance('cool_q_api').get_config()['api_host']
    port = server.get_plugin_instance('cool_q_api').get_config()['api_port']

    def qq(src, ctx):
        if config['command']['qq']:
            player = src.player if src.is_player else 'Console'
            for i in config['group_id']:
                send_group_msg(f'[{player}] {ctx["message"]}', i)

    server.register_help_message('!!qq <msg>', '向QQ群发送消息')
    server.register_command(
        Literal('!!qq').
            then(
            GreedyText('message').runs(qq)
        )
    )
    server.register_event_listener('cool_q_api.on_qq_info', on_qq_info)
    server.register_event_listener('cool_q_api.on_qq_command', on_qq_command)
    server.register_event_listener('cool_q_api.on_qq_notice', on_qq_notice)


def on_server_startup(server):
    for i in config['group_id']:
        send_group_msg('Server is started up', i)


def on_user_info(server, info):
    if info.is_player and config['forward']['mc_to_qq']:
        for i in config['group_id']:
            send_group_msg(f'[{info.player}] {info.content}', i)


def on_qq_info(server, info, bot):
    if config['forward']['qq_to_mc'] and info.source_id in config['group_id']:
        user_id = str(info.user_id)
        if user_id in data.keys():
            server.say(f'§7[QQ] [{data[user_id]}] {info.content}')
        else:
            bot.reply(
                info,
                f'[CQ:at,qq={user_id}] 您未绑定游戏ID, 无法转发您的消息到游戏内, 请绑定您的游戏ID'
            )


def on_qq_command(server, info, bot):
    if not (info.source_id in config['group_id'] or
            info.source_id in config['admin_id']):
        return
    command = info.content.split(' ')
    command[0] = command[0].replace('/', '')

    if config['command']['list'] and command[0] == 'list':
        online_player_api = server.get_plugin_instance('online_player_api')
        bot.reply(info, '在线玩家共{}人，玩家列表: {}'.format(
            len(online_player_api.get_player_list()),
            ', '.join(online_player_api.get_player_list())))
    elif config['command']['mc'] and command[0] == 'mc':
        user_id = str(info.user_id)
        if user_id in data.keys():
            server.say(f'§7[QQ] [{data[user_id]}] {info.content[4:]}')
        else:
            bot.reply(info, f'[CQ:at,qq={user_id}] 请使用/bound <ID>绑定游戏ID')
    if info.source_type == 'private':
        private_command(server, info, bot, command, data)
    elif info.source_type == 'group':
        group_command(server, info, bot, command, data)


def on_qq_notice(server, info, bot):
    if info.source_id not in config['group_id']:
        return
    notice_type = (info.notice_type == 'group_decrease')
    if notice_type and config['whitelist_remove_with_leave']:
        user_id = str(info.user_id)
        if user_id in data.keys():
            command = f'whitelist remove {data[user_id]}'
            server.execute(command)
            bot.reply(info, f'{data[user_id]} 已退群，移除他的白名单')
            del data[user_id]
            data.save()


def private_command(server, info, bot, command, data):
    if info.content == '/help':
        bot.reply(info, admin_help_msg)
    # bound
    elif info.content.startswith('/bound'):
        if info.content == '/bound':
            bot.reply(info, bound_help)
        elif len(command) == 2 and command[1] == 'list':
            bound_list = [f'{a} - {b}' for a, b in data.items()]
            reply_msg = ''
            for i in range(0, len(bound_list)):
                reply_msg += f'{i + 1}. {bound_list[i]}\n'
            reply_msg = '还没有人绑定' if reply_msg == '' else reply_msg
            bot.reply(info, reply_msg)
        elif len(command) == 3 and command[1] == 'check':
            if command[2] in data:
                bot.reply(info,
                          f'{command[2]} 绑定的ID是{data[command[2]]}')
            else:
                bot.reply(info, f'{command[2]} 未绑定')
        elif len(command) == 3 and command[1] == 'unbound':
            if command[2] in data:
                del data[command[2]]
                data.save()
                bot.reply(info, f'已解除 {command[2]} 绑定的ID')
            else:
                bot.reply(info, f'{command[2]} 未绑定')
        elif len(command) == 3 and command[1].isdigit():
            data[command[1]] = command[2]
            data.save()
            bot.reply(info, '已成功绑定')
    # whitelist
    elif info.content.startswith('/whitelist'):
        if info.content == '/whitelist':
            bot.reply(info, whitelist_help)
        elif command[1] in ['add', 'remove', 'list', 'on', 'off', 'reload']:
            if server.is_rcon_running():
                bot.reply(info, server.rcon_query(info.content))
            else:
                server.execute(info.content)
    # command
    elif info.content.startswith('/command '):
        c = info.content[9:]
        c = c.replace('&#91;', '[').replace('&#93;', ']')
        if server.is_rcon_running():
            bot.reply(info, server.rcon_query(c))
        else:
            server.execute(c)


def group_command(server, info, bot, command, data):
    if info.content == '/help':
        bot.reply(info, group_help_msg)
    # bound
    elif len(command) == 2 and command[0] == 'bound':
        user_id = str(info.user_id)
        if user_id in data.keys():
            _id = data[user_id]
            bot.reply(info, f'[CQ:at,qq={user_id}] 您已绑定ID: {_id}, 请联系管理员修改')
        else:
            data[user_id] = command[1]
            data.save()
            bot.reply(info, f'[CQ:at,qq={user_id}] 已成功绑定')
            if config['whitelist_add_with_bound']:
                server.execute(f'whitelist add {command[1]}')
                bot.reply(info, f'[CQ:at,qq={user_id}] 已将您添加到服务器白名单')


def send_group_msg(msg, group):
    requests.post(f'http://{host}:{port}/send_group_msg', json={
        'group_id': group,
        'message': msg
    })
