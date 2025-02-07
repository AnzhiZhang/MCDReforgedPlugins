import re
from typing import List, Dict

from mcdreforged.api.all import *
from enum import Enum, unique

from im_api.drivers.base import Platform
from im_api.models.message import Event, Message
from im_api.models.request import MessageType, SendMessageRequest, ChannelInfo


class Config(Serializable):
    # 服务器主群
    main_group: List[str] = ['123456']

    # 服务器管理群
    manage_groups: List[str] = ['1234563', '1234564']

    # 服务器消息同步群
    message_sync_groups: List[str] = ['1234567', '1234568']
    server_name: str = "survival"

    admins: List[str] = ['1234565', '1234566']
    sync_group_only_admin: bool = True
    # 是否开启群组服消息拦截
    force_bound: bool = False

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
main_group: int
server: PluginServerInterface = None

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

def on_load(mcdr_server: PluginServerInterface, old):
    global config, data, main_group, user_cache, server
    server = mcdr_server
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
    server.register_event_listener("im_api.message", on_message)
    server.register_event_listener("im_api.event", on_notice)


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
# im_api event listener
# -------------------------

def on_message(server: PluginServerInterface, platform: Platform, message: Message):
    if platform != Platform.QQ:
        return

    # is command?
    content = message.content
    is_command = False
    prefix = None
    for prefix in config.command_prefix:
        if prefix != "" and content.startswith(prefix):
            is_command = True
            prefix = prefix
            break

    # if it's a command, process it and stop here
    if is_command:
        return on_qq_command(server, message, prefix)

    # 非 command，目前只支持 msg_sync 群中直接发送消息到服务器
    if message.channel.id in config.message_sync_groups:
        user_id = str(message.user.id)
        # 优先级: 是否在绑定列表中 -> 是否提示需要绑定 -> 转发到游戏中
        if user_id in data.keys():
            nickname = data[user_id]
        else:
            nickname = message.user.name
        # 管理员提示为绿色ID
        if user_id in config.admins:
            server.say(f"§7[QQ] §a[{nickname}]§7 {message.content}")
        else:
            server.say(f"§7[QQ] [{nickname}] {message.content}")


def on_notice(server: PluginServerInterface, platform: str, event: Event):
    if platform != Platform.QQ:
        return
    server.logger.info(f"qq_chat: on_notice: {event}")
    # 只看主群的成员
    if event.channel.id != main_group:
        return

    # Remove whitelist with leave
    if event.type == "guild.member.leave" and config.whitelist_remove_with_leave:
        user_id = str(event.user.id)
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
        message: Message,
        command_prefix: str
):
    # Event did not trigger
    event_type = parse_event_type(message)
    if event_type == EventType.NONE:
        return

    # parse command
    command = parse_command_list(message.content, command_prefix)
    # /help 指令
    if command[0] == "help":
        help_command_handle(server, message, event_type)
    # /list 指令
    elif command[0] == "list":
        list_command_handle(server, message)
    # /bound 绑定指令
    elif command[0] == "bound":
        bound_command_handle(server, message, command, event_type)
    # /mc 发送消息指令
    elif command[0] == "mc":
        mc_command_handle(server, message, command, event_type)
    # /whitelist 操作白名单
    elif command[0] == "whitelist":
        whitelist_command_handle(server, message, command, event_type)
    # /command 执行原版指令
    elif command[0] == "command":
        command_command_handle(server, message, command, event_type)
    # /mcdr 执行MCDR指令
    elif command[0] == "mcdr":
        mcdr_command_handle(server, message, command, event_type)


# -------------------------
# utils
# -------------------------

def parse_command_list(msg: str, prefix: str):
    """解析命令列表"""
    # 如果prefix长度大于1，与实际指令之间需要加空格
    if len(prefix) > 1:
        msg = msg[len(prefix) + 1:]
    else:
        msg = msg[len(prefix):]
    return msg.split()


def parse_main_group():
    """解析主群"""
    if len(config.main_group) == 0:
        return 0
    return config.main_group[0]


def save_data(server: PluginServerInterface):
    """保存数据"""
    server.save_config_simple({
        "data": data,
        "user_cache": user_cache
    }, "data.json")


def execute(server: PluginServerInterface, message: Message, command: str):
    """执行命令"""
    if server.is_rcon_running():
        result = server.rcon_query(command)
        if result == "":
            result = "该指令没有返回值"
    else:
        server.execute(command)
        result = "由于未启用 RCON，没有返回结果"
    reply_with_server_name(message, result)


def reply(message: Message, content: str):
    """回复消息"""
    request = SendMessageRequest(
        platforms=[Platform.QQ],
        channel=ChannelInfo(id=message.channel.id, type=message.channel.type),
        content=content
    )
    server.dispatch_event(LiteralEvent("im_api.send_message"), (request,))


def reply_with_server_name(message: Message, content: str):
    """带服务器名称回复消息"""
    request = SendMessageRequest(
        platforms=[Platform.QQ],
        channel=ChannelInfo(id=message.channel.id, type=message.channel.type),
        content=f"[{config.server_name}] {content}"
    )
    server.dispatch_event(LiteralEvent("im_api.send_message"), (request,))


def send_msg_to_all_groups(message: str):
    """发送消息到所有群"""
    request = SendMessageRequest(
        platforms=[Platform.QQ],
        channel=ChannelInfo(id=main_group, type=MessageType.CHANNEL),
        content=message
    )
    server.dispatch_event(LiteralEvent("im_api.send_message"), (request,))


def send_msg_to_main_groups(message: str):
    """发送消息到主群"""
    # 如没有配置主群，不发送
    if main_group == 0:
        return
    request = SendMessageRequest(
        platforms=[Platform.QQ],
        channel=ChannelInfo(id=main_group, type=MessageType.CHANNEL),
        content=message
    )
    server.dispatch_event(LiteralEvent("im_api.send_message"), (request,))


def send_msg_to_manage_groups(message: str):
    """发送消息到管理群"""
    for group in config.manage_groups:
        request = SendMessageRequest(
            platforms=[Platform.QQ],
            channel=ChannelInfo(id=main_group, type=MessageType.CHANNEL),
            content=message
        )
        server.dispatch_event(LiteralEvent("im_api.send_message"), (request,))


def send_msg_to_message_sync_groups(message: str):
    """发送消息到同步群"""
    for group in config.message_sync_groups:
        request = SendMessageRequest(
            platforms=[Platform.QQ],
            channel=ChannelInfo(id=main_group, type=MessageType.CHANNEL),
            content=message
        )
        server.dispatch_event(LiteralEvent("im_api.send_message"), (request,))


def parse_event_type(message: Message) -> EventType:
    """解析事件类型"""
    # 私聊
    if message.channel.type == "private":
        if str(message.user.id) in config.admins:
            return EventType.PRIVATE_ADMIN_CHAT
        return EventType.PRIVATE_NOT_ADMIN_CHAT

    # 群聊
    channel_id = message.channel.id
    user_id = str(message.user.id)
    is_admin = user_id in config.admins

    # 主群
    if channel_id == main_group:
        if is_admin:
            return EventType.GROUP_MAIN_ADMIN_CHAT
        return EventType.GROUP_MAIN_NOT_ADMIN_CHAT

    # 同步群
    if channel_id in config.message_sync_groups:
        if is_admin:
            return EventType.GROUP_MSG_SYNC_ADMIN_CHAT
        return EventType.GROUP_MSG_SYNC_NOT_ADMIN_CHAT

    # 管理群
    if channel_id in config.manage_groups:
        return EventType.GROUP_MANAGE_CHAT

    return EventType.NONE


# -------------------------
#  command handle
# -------------------------

def help_command_handle(
        server: PluginServerInterface,
        message: Message,
        event_type: EventType
):
    """处理帮助命令"""
    if event_type in ADMIN_EVENT_TYPES:
        reply(message, admin_help)
    else:
        reply(message, group_help)


def list_command_handle(server: PluginServerInterface, message: Message):
    """处理列表命令"""
    if config.commands["list"] is False:
        reply_with_server_name(message, "该指令已禁用")
        return

    online_player_api = server.get_plugin_instance("online_player_api")
    if online_player_api is None:
        reply_with_server_name(message, "未安装 online_player_api")
        return

    online_players = online_player_api.get_player_list()
    if len(online_players) == 0:
        reply_with_server_name(message, "当前没有玩家在线")
        return

    # 分类玩家
    player_list = {}
    for player in online_players:
        for name, regex in config.player_list_regex.items():
            if re.match(regex, player):
                if name not in player_list:
                    player_list[name] = []
                player_list[name].append(player)
                break

    # 生成消息
    msg = []
    for name, players in player_list.items():
        msg.append(f"{name} ({len(players)}): {', '.join(players)}")
    reply_with_server_name(message, "\n".join(msg))


def bound_command_handle(server: PluginServerInterface, message: Message,
                     command: List[str], event_type: EventType):
    """处理绑定命令"""
    # 管理权限
    if event_type in ADMIN_EVENT_TYPES:
        # 查看帮助
        if len(command) == 1:
            reply(message, bound_help)
            return

        # 查看绑定列表
        if command[1] == "list":
            msg = []
            for user_id, player_name in data.items():
                msg.append(f"{user_id}: {player_name}")
            reply_with_server_name(message, "\n".join(msg))
            return

        # 查询绑定ID
        if command[1] == "check":
            if len(command) < 3:
                reply_with_server_name(message, "请输入QQ号")
                return
            user_id = command[2]
            if user_id in data.keys():
                reply_with_server_name(message, f"{user_id} 已绑定 {data[user_id]}")
            else:
                reply_with_server_name(message, f"{user_id} 未绑定")
            return

        # 解除绑定
        if command[1] == "unbound":
            if len(command) < 3:
                reply_with_server_name(message, "请输入QQ号")
                return
            user_id = command[2]
            if user_id in data.keys():
                player_name = data[user_id]
                del data[user_id]
                save_data(server)
                reply_with_server_name(message, f"已解除 {user_id} 与 {player_name} 的绑定")
            else:
                reply_with_server_name(message, f"{user_id} 未绑定")
            return

        # 绑定新ID
        if len(command) < 3:
            reply_with_server_name(message, "请输入QQ号和ID")
            return
        user_id = command[1]
        player_name = command[2]
        data[user_id] = player_name
        save_data(server)
        after_bound(server, message, user_id, player_name)
        return

    # 非管理权限
    if len(command) == 1:
        user_id = str(message.user.id)
        if user_id in data.keys():
            reply_with_server_name(message, f"你已经绑定了 {data[user_id]}")
        else:
            reply_with_server_name(message, "请输入要绑定的ID")
        return

    # 绑定QQ号到玩家名
    bound_qq_to_player(server, message, command[1])


def mc_command_handle(
        server: PluginServerInterface,
        message: Message,
        command: List[str],
        event_type: EventType
):
    """处理mc命令"""
    if config.commands["mc"] is False:
        reply_with_server_name(message, "该指令已禁用")
        return

    if len(command) == 1:
        reply_with_server_name(message, "请输入要发送的消息")
        return

    # 获取昵称
    user_id = str(message.user.id)
    if user_id in data.keys():
        nickname = data[user_id]
    else:
        nickname = message.user.name

    # 发送消息
    msg = " ".join(command[1:])
    if event_type in ADMIN_EVENT_TYPES:
        server.say(f"§7[QQ] §a[{nickname}]§7 {msg}")
    else:
        server.say(f"§7[QQ] [{nickname}] {msg}")


def whitelist_command_handle(
        server: PluginServerInterface,
        message: Message,
        command: List[str],
        event_type: EventType
):
    """处理白名单命令"""
    if event_type not in ADMIN_EVENT_TYPES:
        reply_with_server_name(message, "你没有权限使用该指令")
        return

    if len(command) == 1:
        reply(message, whitelist_help)
        return

    execute(server, message, " ".join(command))


def mcdr_command_handle(server: PluginServerInterface, message: Message,
                    command: List[str], event_type: EventType):
    """处理mcdr命令"""
    if config.commands["mcdr"] is False:
        reply_with_server_name(message, "该指令已禁用")
        return

    if event_type not in ADMIN_EVENT_TYPES:
        reply_with_server_name(message, "你没有权限使用该指令")
        return

    if len(command) == 1:
        reply_with_server_name(message, "请输入要执行的指令")
        return

    # 执行指令
    command = " ".join(command[1:])
    if not command.startswith("!!"):
        command = "!!" + command
    execute(server, message, command)


def command_command_handle(server: PluginServerInterface, message: Message,
                       command: List[str], event_type: EventType):
    """处理command命令"""
    if config.commands["command"] is False:
        reply_with_server_name(message, "该指令已禁用")
        return

    if event_type not in ADMIN_EVENT_TYPES:
        reply_with_server_name(message, "你没有权限使用该指令")
        return

    if len(command) == 1:
        reply_with_server_name(message, "请输入要执行的指令")
        return

    # 执行指令
    execute(server, message, " ".join(command[1:]))


def bound_qq_to_player(server, message: Message, player_name):
    """绑定QQ号到玩家名"""
    user_id = str(message.user.id)
    # 检查是否已经绑定
    if user_id in data.keys():
        reply_with_server_name(message, f"你已经绑定了 {data[user_id]}")
        return

    # 检查玩家名是否已被绑定
    for bound_user_id, bound_player_name in data.items():
        if bound_player_name == player_name:
            reply_with_server_name(message, f"{player_name} 已被 {bound_user_id} 绑定")
            return

    # 绑定
    data[user_id] = player_name
    save_data(server)
    after_bound(server, message, user_id, player_name)


def after_bound(server, message: Message, user_id: str, player_name: str):
    """绑定后的操作"""
    reply_with_server_name(message, f"已绑定 {player_name}")

    # 添加白名单
    if config.whitelist_add_with_bound:
        command = config.whitelist_add_cmd_template.format(player_name)
        server.execute(command)
        reply_with_server_name(message, f"已添加 {player_name} 到白名单")
