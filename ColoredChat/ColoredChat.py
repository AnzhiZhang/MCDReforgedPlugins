# -*- coding: utf-8 -*-
import re
from mcdreforged.api.rtext import *

force_refresh = True


PLUGIN_METADATA = {
    'id': 'colored_chat',
    'version': '0.0.1',
    'name': 'ColoredChat',
    'description': 'Support colored and styled message ingame for vanilla',
    'author': 'zhang_anzhi',
    'link': 'https://github.com/zhang-anzhi/MCDReforgedPlugins/tree/master/ColoredChat'
}
msg_list = []
msg_length = 100 if force_refresh else 10


def on_load(server, old):
    global msg_list
    if old and old.msg_list:
        msg_list = old.msg_list


def on_user_info(server, info):
    if info.is_player:
        if re.search(r'&[0-9a-z]', info.content):
            append_msg(f'<{info.player}> {info.content.replace("&", "§")}')
            server.say(RTextList(*[f'\n{i}' for i in msg_list[:msg_length]]))
        else:
            append_msg(f'<{info.player}> {info.content}')


def on_player_joined(server, player, info):
    append_msg(f'§e{player} joined the game')


def on_player_left(server, player):
    append_msg(f'§e{player} left the game')


def on_death_message(server, death_message):
    append_msg(death_message)


def append_msg(msg):
    global msg_list
    msg_list.append(f'{msg}§r')
    if len(msg_list) > 100:
        msg_list = msg_list[-100:]
