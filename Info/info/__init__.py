# -*- coding: utf-8 -*-
import os
import platform
from typing import List

import psutil

from mcdreforged.api.types import ServerInterface, \
    PluginServerInterface
from mcdreforged.api.rtext import *
from mcdreforged.api.command import *
from mcdreforged.api.utils import Serializable


class Config(Serializable):
    world_names: List[str] = ['world']


config: Config


def on_load(server: PluginServerInterface, prev_module):
    global config
    config = server.load_config_simple(target_class=Config)
    server.register_help_message(
        '!!info',
        {
            'en_us': 'Get server info',
            'zh_cn': '获取服务器信息'
        }
    )
    server.register_command(
        Literal('!!info').
            runs(
            lambda src: src.reply(get_server_info(src.get_server()))
        )
    )


def get_server_info(server: ServerInterface) -> RTextList:
    def get_cpu_use():
        return f'{average(*psutil.cpu_percent(percpu=True))}%'

    def get_memory_use():
        used = psutil.virtual_memory().used
        total = psutil.virtual_memory().total
        return (
            f'{round_size(used)}/{round_size(total)} '
            f'({round(used / total * 100, 2)}%)'
        )

    def get_world_size():
        def get_dir_size(dir_name):
            s = 0
            for root, dirs, files in os.walk(os.path.join('server', dir_name)):
                s += sum(
                    [os.path.getsize(os.path.join(root, name)) for name in
                     files])
            return s

        size = 0
        for i in config.world_names:
            size += get_dir_size(i)
        return round_size(size)

    return RTextList(
        f'§7============ §6{server.tr("info.title")} §7============\n',
        f'§7{server.tr("info.systemVersion")}:§6 {platform.platform()}\n',
        f'§7{server.tr("info.pythonVersion")}:§6 {platform.python_version()}\n',
        f'§7{server.tr("info.cpuUsed")}:§6 {get_cpu_use()}\n',
        f'§7{server.tr("info.memoryUsed")}:§6 {get_memory_use()}\n',
        f'§7{server.tr("info.worldSize")}:§6 {get_world_size()}'
    )


def round_size(size):
    if size < (2 ** 30):
        return f'{round(size / (2 ** 20), 2)} MB'
    else:
        return f'{round(size / (2 ** 30), 2)} GB'


def average(*args):
    count = 0
    for i in args:
        count += i
    return round(count / len(args), 2)
