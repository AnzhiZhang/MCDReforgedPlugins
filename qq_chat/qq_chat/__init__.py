from typing import List, Dict
from asyncio import AbstractEventLoop

from qq_api import MessageEvent
from aiocqhttp import CQHttp, Event
from mcdreforged.api.command import *
from mcdreforged.api.utils import Serializable
from mcdreforged.api.types import PluginServerInterface


class Config(Serializable):
    groups: List[int] = [1234561, 1234562]
    admins: List[int] = [1234563, 1234564]
    whitelist_add_with_bound: bool = False
    whitelist_remove_with_leave: bool = True
    forwards: Dict[str, bool] = {
        'mc_to_qq': False,
        'qq_to_mc': False
    }
    commands: Dict[str, bool] = {
        'list': True,
        'mc': True,
        'qq': True,
    }


config: Config
data: dict
final_bot: CQHttp
event_loop: AbstractEventLoop
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


# -------------------------
# MCDR event listener
# -------------------------

def on_load(server: PluginServerInterface, old):
    global config, data, final_bot, event_loop
    config = server.load_config_simple(target_class=Config)
    data = server.load_config_simple(
        'data.json',
        default_config={'data': {}},
        echo_in_console=False
    )['data']
    qq_api = server.get_plugin_instance('qq_api')
    final_bot = qq_api.get_bot()
    event_loop = qq_api.get_event_loop()

    def qq(src, ctx):
        if config.commands['qq']:
            player = src.player if src.is_player else 'Console'
            send_msg_to_all_groups(f'[{player}] {ctx["message"]}')

    server.register_help_message('!!qq <msg>', '向QQ群发送消息')
    server.register_command(
        Literal('!!qq')
        .then(
            GreedyText('message').runs(qq)
        )
    )
    server.register_event_listener('qq_api.on_message', on_message)
    server.register_event_listener('qq_api.on_notice', on_notice)


def on_server_startup(server: PluginServerInterface):
    send_msg_to_all_groups('Server is started up')


def on_user_info(server: PluginServerInterface, info):
    if info.is_player and config.forwards['mc_to_qq']:
        send_msg_to_all_groups(f'[{info.player}] {info.content}')


# -------------------------
# qq_api event listener
# -------------------------

def on_message(server: PluginServerInterface, bot: CQHttp,
               event: MessageEvent):
    # command
    if event.content.startswith('/'):
        return on_qq_command(server, bot, event)

    # forward
    if config.forwards['qq_to_mc'] and event.group_id in config.groups:
        user_id = str(event.user_id)
        if user_id in data.keys():
            server.say(f'§7[QQ] [{data[user_id]}] {event.content}')
        else:
            bot.sync.send_group_msg(
                group_id=event.group_id,
                message=f'[CQ:at,qq={user_id}] 无法转发您的消息, 请绑定游戏ID'
            )


def on_notice(server: PluginServerInterface, bot: CQHttp, event: Event):
    # group only
    if event.group_id not in config.groups:
        return

    is_group_decrease = (event.detail_type == 'group_decrease')
    if is_group_decrease and config.whitelist_remove_with_leave:
        user_id = str(event.user_id)
        if user_id in data.keys():
            command = f'whitelist remove {data[user_id]}'
            server.execute(command)
            reply(event, f'{data[user_id]} 已退群，移除他的白名单')
            del data[user_id]
            save_data(server)


# -------------------------
# listener functions
# -------------------------

def on_qq_command(server: PluginServerInterface, bot: CQHttp,
                  event: MessageEvent):
    # not in config list
    if not (event.group_id in config.groups or event.user_id in config.admins):
        return

    # parse command
    command = event.content.split(' ')
    command[0] = command[0].replace('/', '')

    # common commands
    if config.commands['list'] and command[0] == 'list':
        online_player_api = server.get_plugin_instance('online_player_api')
        reply(
            event,
            '在线玩家共{}人，玩家列表: {}'.format(
                len(online_player_api.get_player_list()),
                ', '.join(online_player_api.get_player_list())
            )
        )
    elif config.commands['mc'] and command[0] == 'mc':
        user_id = str(event.user_id)
        if user_id in data.keys():
            server.say(f'§7[QQ] [{data[user_id]}] {event.content[4:]}')
        else:
            reply(
                event,
                f'[CQ:at,qq={user_id}] 请使用 /bound <ID> 绑定游戏 ID'
            )
    # other commands
    else:
        if event.detail_type == 'private':
            private_command(server, bot, event, command)
        elif event.detail_type == 'group':
            group_command(server, bot, event, command)


def private_command(server: PluginServerInterface, bot: CQHttp,
                    event: MessageEvent, command: List[str]):
    if event.content == '/help':
        reply(event, admin_help_msg)
    # bound
    elif event.content.startswith('/bound'):
        if event.content == '/bound':
            reply(event, bound_help)
        elif len(command) == 2 and command[1] == 'list':
            bound_list = [f'{a} - {b}' for a, b in data.items()]
            reply_msg = ''
            for i in range(0, len(bound_list)):
                reply_msg += f'{i + 1}. {bound_list[i]}\n'
            reply_msg = '还没有人绑定' if reply_msg == '' else reply_msg
            reply(event, reply_msg)
        elif len(command) == 3 and command[1] == 'check':
            if command[2] in data:
                reply(event, f'{command[2]} 绑定的ID是{data[command[2]]}')
            else:
                reply(event, f'{command[2]} 未绑定')
        elif len(command) == 3 and command[1] == 'unbound':
            if command[2] in data:
                del data[command[2]]
                save_data(server)
                reply(event, f'已解除 {command[2]} 绑定的ID')
            else:
                reply(event, f'{command[2]} 未绑定')
        elif len(command) == 3 and command[1].isdigit():
            data[command[1]] = command[2]
            save_data(server)
            reply(event, '已成功绑定')
    # whitelist
    elif event.content.startswith('/whitelist'):
        if event.content == '/whitelist':
            reply(event, whitelist_help)
        elif command[1] in ['add', 'remove', 'list', 'on', 'off', 'reload']:
            execute(server, event, event.content)
    # command
    elif event.content.startswith('/command '):
        command = event.content[9:]
        command = command.replace('&#91;', '[').replace('&#93;', ']')
        execute(server, event, command)


def group_command(server: PluginServerInterface, bot: CQHttp,
                  event: MessageEvent, command: List[str]):
    if event.content == '/help':
        reply(event, group_help_msg)
    # bound
    elif len(command) == 2 and command[0] == 'bound':
        user_id = str(event.user_id)
        if user_id in data.keys():
            _id = data[user_id]
            reply(
                event,
                f'[CQ:at,qq={user_id}] 您已绑定ID: {_id}, 请联系管理员修改'
            )
        else:
            data[user_id] = command[1]
            save_data(server)
            reply(event, f'[CQ:at,qq={user_id}] 已成功绑定')
            if config.whitelist_add_with_bound:
                server.execute(f'whitelist add {command[1]}')
                reply(event, f'[CQ:at,qq={user_id}] 已将您添加到服务器白名单')


# -------------------------
# utils
# -------------------------

def save_data(server: PluginServerInterface):
    server.save_config_simple({'data': data}, 'data.json')


def execute(server: PluginServerInterface, event: Event, command: str):
    if server.is_rcon_running():
        result = server.rcon_query(command)
        if result == '':
            result = '该指令没有返回值'
    else:
        server.execute(command)
        result = '由于未启用 RCON，没有返回结果'
    reply(event, result)


def reply(event: Event, message: str):
    event_loop.create_task(final_bot.send(event, message))


def send_msg_to_all_groups(message: str):
    for i in config.groups:
        event_loop.create_task(
            final_bot.send_group_msg(group_id=i, message=message)
        )
