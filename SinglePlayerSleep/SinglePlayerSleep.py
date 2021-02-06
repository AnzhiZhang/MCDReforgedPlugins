# -*- coding: utf-8 -*-
import time
import re
from ConfigAPI import Config

from mcdreforged.api.rtext import *
from mcdreforged.api.command import *
from mcdreforged.api.decorator import new_thread
from mcdreforged.plugin.server_interface import ServerInterface

PLUGIN_METADATA = {
    'id': 'single_player_sleep',
    'version': '0.0.1',
    'name': 'SinglePlayerSleep',
    'description': 'Allowed single sleep in server to skip night',
    'author': 'zhang_anzhi',
    'link': 'https://github.com/zhang-anzhi/MCDReforgedPlugins/tree/master/SinglePlayerSleep',
    'dependencies': {
        'minecraft_data_api': '*',
        'config_api': '*'
    }
}
DEFAULT_CONFIG = {
    'skip_wait_time': 10,
    'wait_before_skip': 5,
    'waiting_for_skip': '§e{0} §c正在睡觉, §e{1} §c秒后开始跳过夜晚, 点击这条消息取消',
    'already_sleeping': '§c已经有人在睡觉了',
    'no_one_sleeping': '§c没有人在睡觉',
    'not_fall_asleep': '§c您还没有入睡',
    'skip_abort': '§a跳过夜晚已取消',
    'is_daytime': '§c当前为白天'
}


class Single:
    want_skip = False
    commend_sent = False
    now_time = 0
    config = Config('SinglePlayerSleep', DEFAULT_CONFIG)


single = Single()


def on_info(server, info):
    global single
    if single.commend_sent:
        parse_time_info(info.content)


def on_load(server: ServerInterface, old):
    global single

    @new_thread('SinglePlayerSleep')
    def sleep(src):
        get_time(src.get_server())
        if single.now_time >= 12542:
            fall_asleep = src.get_server().get_plugin_instance(
                'minecraft_data_api').get_player_info(src.player, 'SleepTimer')
            if fall_asleep != 100:
                return src.reply(single.config['not_fall_asleep'])
        else:
            return src.reply(single.config['is_daytime'])
        single.want_skip = True
        need_skip_time = 24000 - single.now_time
        for i in range(single.config['wait_before_skip'], 0, -1):
            if not single.want_skip:
                return
            msg = RText(
                single.config['waiting_for_skip'].format(src.player, i)).c(
                RAction.run_command, '!!sleep cancel'
            )
            src.get_server().say(msg)
            time.sleep(1)
        for i in range(0, single.config['skip_wait_time']):
            if not single.want_skip:
                return
            jump_times = int(need_skip_time / single.config['skip_wait_time'])
            if src.get_server().is_rcon_running():
                src.get_server().rcon_query(f'time add {jump_times}')
            else:
                src.get_server().execute(f'time add {jump_times}')
            time.sleep(1)
        single.want_skip = False

    def cancel(src):
        if single.want_skip:
            single.want_skip = False
            src.reply(single.config['skip_abort'])
        else:
            src.reply(single.config['no_one_sleeping'])

    single = Single()
    server.register_help_message('!!sleep', RText(
        '单人睡觉跳过夜晚').c(RAction.run_command, '!!sleep').h('点我跳过夜晚'))
    server.register_help_message('!!sleep cancel', '取消跳过夜晚')
    server.register_command(
        Literal('!!sleep').
            runs(sleep).
            then(
            Literal('cancel').
                runs(cancel)
        )
    )


def on_unload(server):
    global single
    if single.want_skip:
        server.say(single.config['skip_abort'])
        single.want_skip = False


def get_time(server):
    if server.is_rcon_running():
        parse_time_info(server.rcon_query('time query daytime'))
    else:
        server.execute('time query daytime')
        single.commend_sent = True


def parse_time_info(msg):
    global single
    if re.match(r'The time is .*', msg):
        single.now_time = int(msg.split('is ')[-1])
