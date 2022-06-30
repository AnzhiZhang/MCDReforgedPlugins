# -*- coding: utf-8 -*-
from typing import Dict

from mcdreforged.api.types import PluginServerInterface
from mcdreforged.api.command import *
from mcdreforged.api.utils import Serializable


class Config(Serializable):
    permissions: Dict[str, int] = {
        'help': 3,
        'start': 3,
        'stop': 3,
        'stop_exit': 4,
        'restart': 3,
        'exit': 4,
    }


config: Config


def on_load(server: PluginServerInterface, prev_module):
    global config
    config = server.load_config_simple('config.json', target_class=Config)
    permissions = config.permissions
    server.register_help_message(
        '!!server',
        {
            'en_us': 'Start and stop server helper',
            'zh_cn': '开关服助手'
        }
    )
    server.register_command(
        Literal('!!server').
            requires(lambda src: src.has_permission(permissions['help'])).
            runs(
            lambda src: src.reply(server.rtr('start_stop_helper_r.help'))
        ).
            then(
            Literal('start').
                requires(lambda src: src.has_permission(permissions['start'])).
                runs(lambda src: server.start())
        ).
            then(
            Literal('stop').
                requires(lambda src: src.has_permission(permissions['stop'])).
                runs(lambda src: server.stop())
        ).
            then(
            Literal('stop_exit').
                requires(
                lambda src: src.has_permission(permissions['stop_exit'])).
                runs(lambda src: server.stop_exit())
        ).
            then(
            Literal('restart').
                requires(
                lambda src: src.has_permission(permissions['restart'])).
                runs(lambda src: server.restart())
        ).
            then(
            Literal('exit').
                requires(lambda src: src.has_permission(permissions['exit'])).
                runs(lambda src: server.exit())
        )
    )
