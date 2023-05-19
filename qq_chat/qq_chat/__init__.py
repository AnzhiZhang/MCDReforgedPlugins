from typing import List, Dict
from asyncio import AbstractEventLoop

from qq_api import MessageEvent
from aiocqhttp import CQHttp, Event
from mcdreforged.api.command import *
from mcdreforged.api.utils import Serializable
from mcdreforged.api.types import PluginServerInterface
from enum import Enum, unique


class Config(Serializable):
    # 服务器主群
    main_group: List[int] = [123456]
    # 服务器管理群
    manage_groups: List[int] = [1234563, 1234564]
    # 服务器消息同步群
    message_sync_groups: List[int] = [1234567, 1234568]
    server_name = 'survival'
    admins: List[int] = [1234565, 1234566]
    sync_group_only_admin: bool = True

    # 白名单部分
    whitelist_add_with_bound: bool = False
    whitelist_remove_with_leave: bool = True

    # 转发是否开启
    forwards: Dict[str, bool] = {
        'mc_to_qq': False,
        'qq_to_mc': False
    }

    # command权限开关
    commands: Dict[str, bool] = {
        'command': True,
        'list': True,
        'mc': True,
        'qq': True,
        'mcdr': False,
    }

    # 指令前缀配置
    command_prefix: List[str] = [
        '/',
    ]


@unique
class EventType(Enum):
    NONE = 0
    PRIVATE_ADMIN_CHAT = 1
    PRIVATE_NOT_ADMIN_CHAT = 2
    GROUP_MAIN_ADMIN_CHAT = 3
    GROUP_MAIN_NOT_ADMIN_CHAT = 4
    GROUP_MSG_SYNC_ADMIN_CHAT = 5
    GROUP_MSG_SYNC_NOT_ADMIN_CHAT = 6
    GROUP_MANAGE_CHAT = 7


admin_event = [
    EventType.PRIVATE_ADMIN_CHAT,
    EventType.GROUP_MAIN_ADMIN_CHAT,
    EventType.GROUP_MSG_SYNC_ADMIN_CHAT,
    EventType.GROUP_MANAGE_CHAT
]
not_admin_event = [
    EventType.PRIVATE_NOT_ADMIN_CHAT,
    EventType.GROUP_MAIN_NOT_ADMIN_CHAT,
    EventType.GROUP_MSG_SYNC_NOT_ADMIN_CHAT
]

config: Config
data: dict
final_bot: CQHttp
event_loop: AbstractEventLoop
main_group: int

group_help_msg = '''命令帮助如下:
/list 获取在线玩家列表
/bound <ID> 绑定你的游戏ID
/mc <msg> 向游戏内发送消息
'''
admin_help_msg = '''管理员命令帮助如下
/bound 查看绑定相关帮助
/whitelist 查看白名单相关帮助
/command <command> 执行任意指令
/mc <msg> 向游戏内发送消息
/mcdr <mcdr command> 执行mcdr指令(可不添加`!!`前缀，无回显，谨慎使用)
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
    global config, data, final_bot, event_loop, main_group
    config = server.load_config_simple(target_class=Config)
    data = server.load_config_simple(
        'data.json',
        default_config={'data': {}},
        echo_in_console=False
    )['data']
    qq_api = server.get_plugin_instance('qq_api')
    final_bot = qq_api.get_bot()
    event_loop = qq_api.get_event_loop()
    main_group = parse_main_group()

    def qq(src, ctx):
        if config.commands['qq']:
            player = src.player if src.is_player else 'Console'
            # 通过qq指令发送的消息会同步发送到主群中
            send_msg_to_main_groups(f'[{config.server_name}][{player}]{ctx["message"]}')
            send_msg_to_message_sync_groups(f'[{config.server_name}][{player}]{ctx["message"]}')

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
    send_msg_to_all_groups(f'Server [{config.server_name}] is started up')


def on_user_info(server: PluginServerInterface, info):
    if info.is_player and config.forwards['mc_to_qq']:
        # 所有信息都会发到同步群中
        if not info.content.startswith('!!qq'):
            send_msg_to_message_sync_groups(f'[{config.server_name}][{info.player}] {info.content}')


# -------------------------
# qq_api event listener
# -------------------------

def on_message(server: PluginServerInterface, bot: CQHttp,
               event: MessageEvent):
    # is command?
    content =  event.content
    for prefix in config.command_prefix:
        if prefix != '' and content.startswith(prefix):
            return on_qq_command(server, bot, event, prefix)

    # 非command，目前只支持msg_sync群中直接发送消息到服务器
    if config.forwards['qq_to_mc'] and event.group_id in config.message_sync_groups:
        user_id = str(event.user_id)
        if user_id in data.keys():
            # 管理员提示为绿色ID
            if user_id in config.admins:
                server.say(f'§7[QQ] §a[{data[user_id]}]§7 {event.content}')
            else:
                server.say(f'§7[QQ] [{data[user_id]}] {event.content}')
        else:
            bot.sync.send_group_msg(
                group_id=event.group_id,
                message=f'[CQ:at,qq={user_id}] 无法转发您的消息, 请通过/bound <Player>绑定游戏ID'
            )


def on_notice(server: PluginServerInterface, bot: CQHttp, event: Event):
    # 只看主群的成员
    if event.group_id != main_group:
        return

    is_group_decrease = (event.detail_type == 'group_decrease')
    if is_group_decrease and config.whitelist_remove_with_leave:
        user_id = str(event.user_id)
        if user_id in data.keys():
            command = f'whitelist remove {data[user_id]}'
            server.execute(command)
            reply(event, f'{data[user_id]} 已退群，移除白名单')
            del data[user_id]
            save_data(server)


# -------------------------
# listener functions
# -------------------------

def on_qq_command(server: PluginServerInterface, bot: CQHttp, event: MessageEvent, command_prefix: str):
    # Event did not triggered
    event_type = parse_event_type(event)
    if event_type == EventType.NONE:
        return
    # parse command
    command = parse_command_list(event.content, command_prefix)
    # /help指令
    if command[0] == 'help':
        helper(server, event, event_type)
    # /list指令
    elif command[0] == 'list':
        list_command_handle(server, event)
    # /bound 绑定指令
    elif command[0] == 'bound':
        bound_command_handle(server, event, command, event_type)
    # /mc 发送消息指令
    elif command[0] == 'mc':
        mc_message_command_handle(server, event, command, event_type)
    # /whitelist 操作白名单
    elif command[0] == 'whitelist':
        whitelist_command_handle(server, event, command, event_type)
    # /command 执行原版指令
    elif command[0] == 'command':
        mc_cmd_command_handle(server, event, command, event_type)
    # /mcdr 执行MCDR指令
    elif command[0] == 'mcdr':
        mcdr_command_handle(server, event, command, event_type)


# -------------------------
# utils
# -------------------------

def parse_command_list(msg: str, prefix: str):
    # 如果prefix长度大于1，与实际指令之间需要加空格
    if len(prefix) > 1:
        command = msg.split(' ')
        if len(command) == 1:
            # 只有指令前缀，则当做help
            return ['help']
        else:
            # 去掉前缀，保留指令本身
            return command[1:]
    else:
        return msg[1:].split(' ')


def parse_main_group():
    if len(config.main_group) == 0:
        return None
    else:
        # 若填多个只取第一个
        return config.main_group[0]


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
    send_msg_to_manage_groups(message)
    send_msg_to_main_groups(message)
    send_msg_to_message_sync_groups(message)


def send_msg_to_main_groups(message: str):
    # 如没有配置主群，不发送
    if(main_group == None):
        return
    event_loop.create_task(
        final_bot.send_group_msg(group_id=main_group, message=message)
    )


def send_msg_to_manage_groups(message: str):
    for i in config.manage_groups:
        event_loop.create_task(
            final_bot.send_group_msg(group_id=i, message=message)
        )


def send_msg_to_message_sync_groups(message: str):
    for i in config.message_sync_groups:
        event_loop.create_task(
            final_bot.send_group_msg(group_id=i, message=message)
        )


def parse_event_type(event: MessageEvent) -> EventType:
    # 私聊
    if event.detail_type == 'private':
        if event.user_id in config.admins:
            return EventType.PRIVATE_ADMIN_CHAT
        else:
            return EventType.PRIVATE_NOT_ADMIN_CHAT
    # 群聊
    elif event.detail_type == 'group':
        if event.group_id == main_group:
            if event.user_id in config.admins:
                return EventType.GROUP_MAIN_ADMIN_CHAT
            else:
                return EventType.GROUP_MAIN_NOT_ADMIN_CHAT
        elif event.group_id in config.manage_groups:
            return EventType.GROUP_MANAGE_CHAT
        elif event.group_id in config.message_sync_groups:
            # 如果开启仅管理员选项，则默认全都具有admin权限
            if config.sync_group_only_admin:
                return EventType.GROUP_MSG_SYNC_ADMIN_CHAT
            if event.user_id in config.admins:
                return EventType.GROUP_MSG_SYNC_ADMIN_CHAT
            else:
                return EventType.GROUP_MSG_SYNC_NOT_ADMIN_CHAT
        else:
            return EventType.NONE

# -------------------------
#  command handle
# -------------------------

def helper(server: PluginServerInterface, event: MessageEvent, event_type: EventType):
    if event_type in [EventType.NONE, EventType.PRIVATE_NOT_ADMIN_CHAT]:
        return
    elif event_type in [EventType.GROUP_MAIN_NOT_ADMIN_CHAT,
                        EventType.GROUP_MAIN_ADMIN_CHAT,
                        EventType.GROUP_MSG_SYNC_NOT_ADMIN_CHAT]:
        reply(event, group_help_msg)
    elif event_type in [EventType.PRIVATE_ADMIN_CHAT,
                        EventType.GROUP_MANAGE_CHAT,
                        EventType.GROUP_MSG_SYNC_ADMIN_CHAT]:
        reply(event, admin_help_msg)


def list_command_handle(server: PluginServerInterface, event: MessageEvent):
    if not config.commands['list']:
        return
    online_player_api = server.get_plugin_instance('online_player_api')
    real_players = []
    bot_players = []
    all_players = online_player_api.get_player_list()
    for player in all_players:
        if str(player).lower().startswith('bot_'):
            bot_players.append(player)
        else:
            real_players.append(player)
    reply(
        event,
        '在线玩家共{}人\n--玩家列表--\n{}\n--bot列表--\n{}'.format(
            len(real_players),
            '\n'.join(real_players),
            '\n'.join(bot_players)
        )
    )


def bound_command_handle(server: PluginServerInterface, event: MessageEvent,
                         command: List[str], event_type: EventType):
    # 管理权限
    if event_type in admin_event:
        if len(command) == 1:
            reply(event, bound_help)
        elif len(command) == 2:
            if command[1] == 'list':
                bound_list = [f'{a} - {b}' for a, b in data.items()]
                reply_msg = ''
                for i in range(0, len(bound_list)):
                    reply_msg += f'{i + 1}. {bound_list[i]}\n'
                reply_msg = '还没有人绑定' if reply_msg == '' else reply_msg
                reply(event, reply_msg)
            else:
                return bound_qq_to_player(server, event, command[1])
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

    # 非管理权限
    elif event_type in [EventType.GROUP_MAIN_NOT_ADMIN_CHAT,
                        EventType.GROUP_MSG_SYNC_NOT_ADMIN_CHAT]:
        bound_qq_to_player(server, event, command[1])


def bound_qq_to_player(server, event, player_name):
    user_id = str(event.user_id)
    if user_id in data.keys():
        _id = data[user_id]
        reply(
            event,
            f'[CQ:at,qq={user_id}] 您已绑定ID: {_id}, 请联系管理员修改'
        )
    else:
        data[user_id] = player_name
        save_data(server)
        reply(event, f'[CQ:at,qq={user_id}] 已成功绑定')
        if config.whitelist_add_with_bound:
            server.execute(f'whitelist add {player_name}')
            reply(event, f'[CQ:at,qq={user_id}] 已将您添加到服务器白名单')


def mc_message_command_handle(server: PluginServerInterface, event: MessageEvent,
                              command: List[str], event_type: EventType):
    if config.commands['mc'] or event_type == EventType.NONE or not config.forwards['qq_to_mc']:
        return
    # 非管理不允许私聊机器人发送消息,发送消息需在群聊中
    if event_type not in [EventType.PRIVATE_NOT_ADMIN_CHAT]:
        user_id = str(event.user_id)
        if user_id in data.keys():
            # 管理员提示为绿色ID
            if user_id in config.admins:
                server.say(f'§7[QQ] §a[{data[user_id]}]§7 {event.content[4:]}')
            else:
                server.say(f'§7[QQ] [{data[user_id]}] {event.content[4:]}')
        else:
            reply(
                event,
                message=f'[CQ:at,qq={user_id}] 无法转发您的消息, 请通过/bound <Player>绑定游戏ID'
            )


def whitelist_command_handle(server: PluginServerInterface, event: MessageEvent,
                             command: List[str], event_type: EventType):
    if event_type == EventType.NONE:
        return
    # 非管理禁止操作白名单
    if event_type not in admin_event:
        reply(
            event,
            f'[CQ:at,qq={event.user_id}] 你不是管理员，无权执行此命令!'
        )
    else:
        if len(command) == 1:
            reply(event, whitelist_help)
        elif command[1] in ['add', 'remove', 'list', 'on', 'off', 'reload']:
            execute(server, event, event.content)
        else:
            reply(event, "错误的指令，请使用/whitelist查看指令帮助!")


def mcdr_command_handle(server: PluginServerInterface, event: MessageEvent,
                        command: List[str], event_type: EventType):
    if event_type == EventType.NONE:
        return
    # 非admin
    if event_type not in admin_event:
        reply(event, f"[CQ:at, qq={event.user_id}] 你不是管理员，无权执行此命令!")
    else:
        if not config.commands['mcdr']:
            reply(event, "未开启MCDR指令控制，请在配置文件指令中开启mcdr!")
        else:
            if len(command) > 1:
                cmd = ' '.join(command[1:])
                if cmd.startswith('!!'):
                    cmd = cmd[2:]
                server.execute_command('!!' + cmd)
                reply(event, f"已执行MCDR指令 >> !!{cmd}")
            else:
                reply(event, "请输入MCDR指令!")


def mc_cmd_command_handle(server: PluginServerInterface, event: MessageEvent,
                          command: List[str], event_type: EventType):
    if event_type == EventType.NONE:
        return
    # 非admin
    if event_type not in admin_event:
        reply(event, f"[CQ:at, qq={event.user_id}] 你不是管理员，无权执行此命令!")
    else:
        if not config.commands['command']:
            reply(event, "未开启原版指令控制，请在配置文件指令中开启command!")
        else:
            cmd = ' '.join(command[1:])
            cmd = cmd.replace('&#91;', '[').replace('&#93;', ']')
            execute(server, event, cmd)
