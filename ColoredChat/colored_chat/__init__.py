# -*- coding: utf-8 -*-
import re

from mcdreforged.plugin.server_interface import PluginServerInterface
from mcdreforged.api.types import Info
from mcdreforged.api.rtext import *
from mcdreforged.api.utils import Serializable


class Config(Serializable):
    force_refresh: bool = True


config: Config
msg_list = []


def on_load(server: PluginServerInterface, prev_module):
    global config, msg_list
    config = server.load_config_simple('config.json', target_class=Config)
    if prev_module and prev_module.msg_list:
        msg_list = prev_module.msg_list


def on_user_info(server: PluginServerInterface, info: Info):
    if info.is_player:
        content = re.sub(r'&([0-9a-z].)', r'§\1', info.content)
        append_msg(f'<{info.player}> {content}')
        refresh(server)


def on_player_joined(server: PluginServerInterface, player, info):
    append_msg(server.tr('colored_chat.joined', player))
    refresh(server)


def on_player_left(server: PluginServerInterface, player):
    append_msg(server.tr('colored_chat.left', player))
    refresh(server)


def append_msg(msg):
    global msg_list
    msg_list.append(f'\n{msg}§r')
    if len(msg_list) > 100:
        msg_list.pop(0)


def refresh(server: PluginServerInterface):
    server.say(RTextList(*msg_list[-(100 if config.force_refresh else 10):]))
