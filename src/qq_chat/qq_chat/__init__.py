import re
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
    server_name: str = "survival"

    # 是否开启群组服消息拦截
    multi_server: bool = False
    admins: List[int] = [1234565, 1234566]
    sync_group_only_admin: bool = True

    # 白名单部分
    whitelist_add_with_bound: bool = False
    whitelist_add_cmd_template: str = "/whitelist add {}"
    whitelist_remove_with_leave: bool = True

    # command 权限开关
    commands: Dict[str, bool] = {
        "command": True,
        "list": True,
        "mc": True,
        "qq": True,
        "mcdr": False,
    }

    # 指令前缀配置
    command_prefix: List[str] = [
        "/",
    ]

    # 玩家列表分类
    player_list_regex: Dict[str, str] = {
        "玩家": "^(?!bot_).*$",
        "假人": "^bot_.*$",
    }


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


ADMIN_EVENT_TYPES = [
    EventType.PRIVATE_ADMIN_CHAT,
    EventType.GROUP_MAIN_ADMIN_CHAT,
    EventType.GROUP_MSG_SYNC_ADMIN_CHAT,
    EventType.GROUP_MANAGE_CHAT
]

NOT_ADMIN_EVENT_TYPES = [
    EventType.PRIVATE_NOT_ADMIN_CHAT,
    EventType.GROUP_MAIN_NOT_ADMIN_CHAT,
    EventType.GROUP_MSG_SYNC_NOT_ADMIN_CHAT
]

config: Config
data: dict
user_cache: dict
final_bot: CQHttp
event_loop: AbstractEventLoop
main_group: int

group_help = """命令帮助如下:
/list 获取在线玩家列表
/bound <ID> 绑定你的游戏ID
/mc <msg> 向游戏内发送消息
/server 查看已连接或可连接的服务器
/server <server_name> 连接到指定服务器
"""

admin_help = """管理员命令帮助如下
/bound 查看绑定相关帮助
/whitelist 查看白名单相关帮助
/command <command> 执行任意指令
/mc <msg> 向游戏内发送消息
/mcdr <mcdr command> 执行mcdr指令(可不添加`!!`前缀，无回显，谨慎使用)
"""

bound_help = """/bound list 查看绑定列表
/bound check <qq number> 查询绑定ID
/bound unbound <qq number> 解除绑定
/bound <qq number> <ID> 绑定新ID
"""

whitelist_help = """/whitelist add <target> 添加白名单成员
/whitelist list 列出白名单成员
/whitelist off 关闭白名单
/whitelist on 开启白名单
/whitelist reload 重载白名单
/whitelist remove <target> 删除白名单成员
<target> 可以是玩家名/目标选择器/UUID
"""


# -------------------------
# MCDR event listener
# -------------------------

def on_load(server: PluginServerInterface, old):
    global config, data, final_bot, event_loop, main_group, user_cache
    config = server.load_config_simple(target_class=Config)
    all_data = server.load_config_simple(
        "data.json",
        default_config={"data": {}, "user_cache": {}},
        echo_in_console=False
    )
    # 存储用户bound信息
    data = all_data["data"]
    # 存储群组服操作该服务器的用户信息
    user_cache = all_data["user_cache"]

    qq_api = server.get_plugin_instance("qq_api")
    final_bot = qq_api.get_bot()
    event_loop = qq_api.get_event_loop()
    main_group = parse_main_group()

    def qq(src, ctx):
        if config.commands["qq"] is True:
            player = src.player if src.is_player else "Console"
            # 通过qq指令发送的消息会同步发送到主群中
            msg = f"[{config.server_name}] <{player}> {ctx['message']}"
            send_msg_to_main_groups(msg)
            send_msg_to_message_sync_groups(msg)

    server.register_help_message("!!qq <msg>", "向QQ群发送消息")
    server.register_command(
        Literal("!!qq").then(GreedyText("message").runs(qq))
    )
    server.register_event_listener("qq_api.on_message", on_message)
    server.register_event_listener("qq_api.on_notice", on_notice)


def on_server_startup(server: PluginServerInterface):
    send_msg_to_all_groups(f"Server [{config.server_name}] is started up")


def on_user_info(server: PluginServerInterface, info):
    if info.is_player is True:
        # 所有信息都会发到同步群中
        if not info.content.startswith("!!qq"):
            send_msg_to_message_sync_groups(
                f"[{config.server_name}] <{info.player}> {info.content}"
            )


# -------------------------
# qq_api event listener
# -------------------------

def on_message(server: PluginServerInterface, bot: CQHttp,
               event: MessageEvent):
    # 判断指令是否需要处理，如果是多服模式，只处理设置了此服的用户
    need_process = (
            config.multi_server is False
            or (
                    config.multi_server is True
                    and str(event.user_id) in user_cache.keys()
                    and user_cache[str(event.user_id)] is True
            )
    )

    # is command?
    content = event.content
    is_command = False
    prefix = None
    for prefix in config.command_prefix:
        if prefix != "" and content.startswith(prefix):
            is_command = True
            prefix = prefix
            break

    # if it's a command, process it and stop here
    if is_command:
        return on_qq_command(server, bot, event, prefix, need_process)

    # 非 command，目前只支持 msg_sync 群中直接发送消息到服务器
    if event.group_id in config.message_sync_groups:
        user_id = str(event.user_id)
        if user_id in data.keys():
            # 管理员提示为绿色ID
            if user_id in config.admins:
                server.say(f"§7[QQ] §a[{data[user_id]}]§7 {event.content}")
            else:
                server.say(f"§7[QQ] [{data[user_id]}] {event.content}")
        else:
            reply_with_server_name(
                event,
                f"[CQ:at,qq={user_id}] 无法转发您的消息，请通过/bound <Player>绑定游戏ID"
            )


def on_notice(server: PluginServerInterface, bot: CQHttp, event: Event):
    # 只看主群的成员
    if event.group_id != main_group:
        return

    # Remove whitelist with leave
    is_group_decrease = (event.detail_type == "group_decrease")
    if is_group_decrease and config.whitelist_remove_with_leave:
        user_id = str(event.user_id)
        if user_id in data.keys():
            command = f"whitelist remove {data[user_id]}"
            server.execute(command)
            reply(
                event,
                f"{data[user_id]} 已退群，移除[{config.server_name}]白名单"
            )
            del data[user_id]
            save_data(server)


# -------------------------
# listener functions
# -------------------------

def on_qq_command(
        server: PluginServerInterface,
        bot: CQHttp,
        event: MessageEvent,
        command_prefix: str,
        need_process: bool
):
    # Event did not trigger
    event_type = parse_event_type(event)
    if event_type == EventType.NONE:
        return

    # parse command
    command = parse_command_list(event.content, command_prefix)

    # /server 设置操作服务器指令，检测到set需要做处理
    if command[0] == "server":
        server_command_handle(server, event, command, event_type)

    # 无需处理直接返回
    if not need_process:
        return

    # /help 指令
    if command[0] == "help":
        help_command_handle(server, event, event_type)
    # /list 指令
    elif command[0] == "list":
        list_command_handle(server, event)
    # /bound 绑定指令
    elif command[0] == "bound":
        bound_command_handle(server, event, command, event_type)
    # /mc 发送消息指令
    elif command[0] == "mc":
        mc_command_handle(server, event, command, event_type)
    # /whitelist 操作白名单
    elif command[0] == "whitelist":
        whitelist_command_handle(server, event, command, event_type)
    # /command 执行原版指令
    elif command[0] == "command":
        command_command_handle(server, event, command, event_type)
    # /mcdr 执行MCDR指令
    elif command[0] == "mcdr":
        mcdr_command_handle(server, event, command, event_type)


# -------------------------
# utils
# -------------------------

def parse_command_list(msg: str, prefix: str):
    # 如果prefix长度大于1，与实际指令之间需要加空格
    if len(prefix) > 1:
        command = msg.split(" ")
        if len(command) == 1 and command[0] == prefix:
            # 只有指令前缀，则当做help
            return ["help"]
        else:
            # 去掉前缀，保留指令本身
            return command[1:]
    else:
        return msg[1:].split(" ")


def parse_main_group():
    if len(config.main_group) == 0:
        return None
    else:
        # 若填多个只取第一个
        return config.main_group[0]


def save_data(server: PluginServerInterface):
    server.save_config_simple(
        {
            "data": data,
            "user_cache": user_cache
        },
        "data.json"
    )


def execute(server: PluginServerInterface, event: MessageEvent, command: str):
    if server.is_rcon_running():
        result = server.rcon_query(command)
        if result == "":
            result = "该指令没有返回值"
    else:
        server.execute(command)
        result = "由于未启用 RCON，没有返回结果"
    reply_with_server_name(event, result)


def reply(event: Event, message: str):
    event_loop.create_task(final_bot.send(event, message))


def reply_with_server_name(event: MessageEvent, msg: str):
    if config.multi_server:
        reply(event, f"[{config.server_name}] {msg}")
    else:
        reply(event, msg)


def send_msg_to_all_groups(message: str):
    send_msg_to_manage_groups(message)
    send_msg_to_main_groups(message)
    send_msg_to_message_sync_groups(message)


def send_msg_to_main_groups(message: str):
    # 如没有配置主群，不发送
    if main_group is None:
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
    if event.detail_type == "private":
        if event.user_id in config.admins:
            return EventType.PRIVATE_ADMIN_CHAT
        else:
            return EventType.PRIVATE_NOT_ADMIN_CHAT
    # 群聊
    elif event.detail_type == "group":
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

def server_command_handle(server: PluginServerInterface, event: MessageEvent,
                          command: List[str], event_type: EventType):
    """
    Server command handle.
    User can choose to connect a server or switch to another server.
    To use this command, the config "multi_server" must be set to True.

    When user type /server without any arguments:
        If user is not connected to any server, reply with this server's name.
        If user is connected to this server, say already connected to this.
        If user is connected to another server, ignore that command.

    When user type /server <server_name>:
        If user is already connected to this server, reply it's connected.
        If user is connecting this server, reply and save status.
        If user is connecting another server, save this status and ignore.
    """
    # 检查是否开启多服务器配置
    if not config.multi_server:
        reply(
            event,
            f"[{config.server_name}] 服务器并未开启多服务器配置，server 功能暂不开放"
        )
        return

    # save status of is user connected to this server
    user_id = str(event.user_id)
    is_on_this_server = user_cache.get(user_id)

    # 输入 /server 查询当前连接到了哪个服务器(不规范的操作可能导致连接多个)
    if len(command) == 1:
        # 已连接到此服务器
        if is_on_this_server is True:
            reply(event, f"当前已连接到 [{config.server_name}]")

        # 未连接到此服务器
        elif is_on_this_server is False:
            pass

        # 未连接到任何服务器
        elif is_on_this_server is None:
            reply(event, f"您可以连接到 [{config.server_name}]")

    # 输入 /server <server_name> 连接到指定服务器
    elif len(command) == 2:
        new_server_name = command[1]

        # 已经连接到此服务器
        if new_server_name == config.server_name and is_on_this_server:
            reply(
                event,
                f"[CQ:at,qq={event.user_id}] 你已经连接到 [{new_server_name}] 了！"
            )

        # 连接到当前服务器
        elif new_server_name == config.server_name and not is_on_this_server:
            user_cache[user_id] = True
            save_data(server)
            reply(
                event,
                f"[CQ:at,qq={event.user_id}] 聊天服务器已连接至 [{new_server_name}]"
            )

        # 连接到其他服务器
        else:
            user_cache[user_id] = False
            save_data(server)


def help_command_handle(
        server: PluginServerInterface,
        event: MessageEvent,
        event_type: EventType
):
    if event_type in [EventType.NONE, EventType.PRIVATE_NOT_ADMIN_CHAT]:
        return
    elif event_type in [EventType.GROUP_MAIN_NOT_ADMIN_CHAT,
                        EventType.GROUP_MAIN_ADMIN_CHAT,
                        EventType.GROUP_MSG_SYNC_NOT_ADMIN_CHAT]:
        reply(event, group_help)
    elif event_type in [EventType.PRIVATE_ADMIN_CHAT,
                        EventType.GROUP_MANAGE_CHAT,
                        EventType.GROUP_MSG_SYNC_ADMIN_CHAT]:
        reply(event, admin_help)


def list_command_handle(server: PluginServerInterface, event: MessageEvent):
    if not config.commands["list"]:
        return
    online_player_api = server.get_plugin_instance("online_player_api")
    players = online_player_api.get_player_list()

    # init groups
    regex_rules: Dict[str, re.Pattern] = {
        group: re.compile(regex)
        for group, regex in config.player_list_regex.items()
    }
    groups: Dict[str, List[str]] = {
        group: []
        for group in config.player_list_regex.keys()
    }
    groups["其它"] = []

    # sort players
    for player in players:
        for group, value in regex_rules.items():
            if value.match(player):
                groups[group].append(player)
                break
        else:
            groups["其它"].append(player)

    # remote empty groups
    new_groups = {}
    for group, players in groups.items():
        if len(players) != 0:
            new_groups[group] = players

    # generate message
    players_count = sum([len(players) for players in new_groups.values()])
    message = f"在线玩家共{players_count}人"
    if len(new_groups) != 0:
        message += "，玩家列表：\n"
    for group, players in new_groups.items():
        message += f"--{group}--\n"
        for player in players:
            message += f"{player}\n"

    reply_with_server_name(event, message)


def bound_command_handle(server: PluginServerInterface, event: MessageEvent,
                         command: List[str], event_type: EventType):
    # 管理权限
    if event_type in ADMIN_EVENT_TYPES:
        if len(command) == 1:
            reply(event, bound_help)
        elif len(command) == 2:
            if command[1] == "list":
                bound_list = [f"{a} - {b}" for a, b in data.items()]
                reply_msg = "已绑定的成员列表\n"
                for i in range(0, len(bound_list)):
                    reply_msg += f"{i + 1}. {bound_list[i]}\n"
                reply_msg = "还没有人绑定" if reply_msg == "" else reply_msg
                reply_with_server_name(event, reply_msg)
            else:
                return bound_qq_to_player(server, event, command[1])
        elif len(command) == 3 and command[1] == "check":
            qq_number = parse_at_message(command[2])
            if qq_number in data:
                reply_with_server_name(
                    event,
                    f"{qq_number} 绑定的ID是{data[qq_number]}"
                )
            else:
                reply_with_server_name(event, f"{qq_number} 未绑定")
        elif len(command) == 3 and command[1] == "unbound":
            qq_number = parse_at_message(command[2])
            if qq_number in data:
                del data[qq_number]
                save_data(server)
                reply_with_server_name(event, f"已解除 {qq_number} 绑定的ID")
            else:
                reply_with_server_name(event, f"{qq_number} 未绑定")
        elif len(command) == 3 and parse_at_message(command[1]).isdigit():
            data[parse_at_message(command[1])] = command[2]
            save_data(server)
            reply_with_server_name(event, "已成功绑定")
            after_bound(
                server,
                event,
                parse_at_message(command[1]),
                command[2]
            )

    # 非管理权限
    elif event_type in [EventType.GROUP_MAIN_NOT_ADMIN_CHAT,
                        EventType.GROUP_MSG_SYNC_NOT_ADMIN_CHAT]:
        bound_qq_to_player(server, event, command[1])


def parse_at_message(node: str) -> str:
    pattern = r'\[@([^\]]+)\]'
    match = re.search(pattern, node)
    if match:
        return match.group(1)
    else:
        return node


def bound_qq_to_player(server, event, player_name):
    user_id = str(event.user_id)
    if user_id in data.keys():
        _id = data[user_id]
        reply_with_server_name(
            event,
            f"[CQ:at,qq={user_id}] 您已绑定ID: {_id}, 请联系管理员修改"
        )
    else:
        data[user_id] = player_name
        save_data(server)
        reply_with_server_name(
            event,
            f"[CQ:at,qq={user_id}] 已成功绑定到{player_name}"
        )
        after_bound(server, event, user_id, player_name)


def after_bound(server, event, user_id, player_name):
    if config.whitelist_add_with_bound:
        if config.whitelist_add_cmd_template is None or config.whitelist_add_cmd_template == '':
            server.execute(f"whitelist add {player_name}")
        else:
            cmd = config.whitelist_add_cmd_template.format(player_name)
            if config.whitelist_add_cmd_template.startswith("!!"):
                server.execute_command(cmd)
            else:
                server.execute(cmd)
        reply_with_server_name(
            event,
            f"[CQ:at,qq={user_id}] 已将您添加到服务器白名单"
        )


def mc_command_handle(
        server: PluginServerInterface,
        event: MessageEvent,
        command: List[str],
        event_type: EventType
):
    if (
            config.commands["mc"] is False
            or event_type == EventType.NONE
    ):
        return

    # 非管理不允许私聊机器人发送消息,发送消息需在群聊中
    if event_type not in [EventType.PRIVATE_NOT_ADMIN_CHAT]:
        user_id = str(event.user_id)
        if user_id in data.keys():
            # 管理员提示为绿色ID
            if user_id in config.admins:
                server.say(f"§7[QQ] §a<{data[user_id]}>§7 {event.content[4:]}")
            else:
                server.say(f"§7[QQ] <{data[user_id]}> {event.content[4:]}")
        else:
            reply_with_server_name(
                event,
                f"[CQ:at,qq={user_id}] 无法转发您的消息, 请通过/bound <Player>绑定游戏ID"
            )


def whitelist_command_handle(
        server: PluginServerInterface,
        event: MessageEvent,
        command: List[str],
        event_type: EventType
):
    if event_type == EventType.NONE:
        return
    # 非管理禁止操作白名单
    if event_type not in ADMIN_EVENT_TYPES:
        reply_with_server_name(
            event,
            f"[CQ:at,qq={event.user_id}] 你不是管理员，无权执行此命令!"
        )
    else:
        if len(command) == 1:
            reply(event, whitelist_help)
        elif command[1] in ["add", "remove", "list", "on", "off", "reload"]:
            execute(server, event, event.content)
        else:
            reply(event, "错误的指令，请使用/whitelist查看指令帮助!")


def mcdr_command_handle(server: PluginServerInterface, event: MessageEvent,
                        command: List[str], event_type: EventType):
    if event_type == EventType.NONE:
        return

    # not admin
    if event_type not in ADMIN_EVENT_TYPES:
        reply_with_server_name(
            event,
            f"[CQ:at,qq={event.user_id}] 你不是管理员，无权执行此命令!"
        )
    else:
        if not config.commands["mcdr"]:
            reply_with_server_name(
                event,
                "未开启MCDR指令控制，请在配置文件指令中开启mcdr!"
            )
        else:
            if len(command) > 1:
                cmd = " ".join(command[1:])
                if cmd.startswith("!!"):
                    cmd = cmd[2:]
                server.execute_command("!!" + cmd)
                reply_with_server_name(event, f"已执行MCDR指令 >> !!{cmd}")
            else:
                reply_with_server_name(event, "请输入MCDR指令!")


def command_command_handle(server: PluginServerInterface, event: MessageEvent,
                           command: List[str], event_type: EventType):
    if event_type == EventType.NONE:
        return

    # not admin
    if event_type not in ADMIN_EVENT_TYPES:
        reply_with_server_name(
            event,
            f"[CQ:at,qq={event.user_id}] 你不是管理员，无权执行此命令！"
        )
    else:
        if not config.commands["command"]:
            reply_with_server_name(
                event,
                "未开启原版指令控制，请在配置文件指令中开启！"
            )
        else:
            cmd = " ".join(command[1:])
            cmd = cmd.replace("&#91;", "[").replace("&#93;", "]")
            execute(server, event, cmd)
