# -*- coding: utf-8 -*-
import os
import json
import time
from threading import Thread

from mcdreforged.api.types import PluginServerInterface
from mcdreforged.api.command import *

PLUGIN_METADATA = {
    'id': 'mined_ranking',
    'version': '0.0.1',
    'name': 'MinedRanking',
    'description': 'Set mined ranking on scoreboard',
    'author': 'Andy Zhang',
    'link': 'https://github.com/AnzhiZhang/MCDReforgedPlugins/tree/master/.archived/MinedRanking',
    'dependencies': {
        'config_api': '*'
    }
}
USERCACHE_PATH = os.path.join('server', 'usercache.json')
STATS_DIR = os.path.join('server', 'world', 'stats')
DEFAULT_CONFIG = {
    'scoreboard_id': 'mined',
    'scoreboard_name': '{"text": "§6挖掘榜§r"}',
    'update_message': '§6挖掘榜已更新',
    'update_time': 60 * 60 * 2,
    'send_command_feedback': True,
    'auto_set_scoreboard': True,
    'update_permission': 3
}


class MinedRanking(Thread):
    def __init__(self, server: ServerInterface, config):
        super().__init__()
        self.setName(PLUGIN_METADATA['name'])
        self.server = server
        self.stop_flag = False
        self.config = config

    @property
    def uuid_list(self):
        with open(USERCACHE_PATH) as f:
            usercache = json.load(f)
        return {user['uuid']: user['name'] for user in usercache}

    def update(self):
        if not self.config['send_command_feedback']:
            self.server.execute('gamerule sendCommandFeedback false')
        if self.config['auto_set_scoreboard']:
            self.server.execute(
                f'scoreboard objectives remove {self.config["scoreboard_id"]}'
            )
            self.server.execute(
                f'scoreboard objectives add {self.config["scoreboard_id"]} '
                f'dummy {self.config["scoreboard_name"]}'
            )
            self.server.execute(
                f'scoreboard objectives setdisplay sidebar mined'
            )
        self.server.execute('save-off')
        self.server.execute('save-all')
        uuid_list = self.uuid_list
        for uuid in uuid_list.keys():
            try:
                with open(os.path.join(STATS_DIR, f'{uuid}.json')) as f:
                    stats = json.load(f)['stats']
                mined = sum(stats['minecraft:mined'].values())
            except (KeyError, FileNotFoundError):
                continue
            else:
                self.server.execute(
                    f'scoreboard players set {uuid_list[uuid]} '
                    f'{self.config["scoreboard_id"]} {mined}'
                )
        self.server.execute('save-on')
        self.server.say(self.config['update_message'])
        if not self.config['send_command_feedback']:
            self.server.execute('gamerule sendCommandFeedback true')

    def run(self) -> None:
        while not self.stop_flag:
            time.sleep(self.config['update_time'])
            if self.stop_flag:
                break
            self.update()


def on_load(server: PluginServerInterface, old):
    global mined_ranking
    from ConfigAPI import Config
    config = Config(PLUGIN_METADATA['name'], DEFAULT_CONFIG)
    mined_ranking = MinedRanking(server, config)
    mined_ranking.start()
    server.register_help_message('!!update mined', '更新挖掘榜')
    server.register_command(
        Literal('!!update').
            then(
            Literal('mined').
                requires(
                lambda src: src.has_permission(config['update_permission'])).
                runs(mined_ranking.update)
        )
    )


def on_unload(server):
    mined_ranking.stop_flag = True
