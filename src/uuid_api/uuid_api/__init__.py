# -*- coding: utf-8 -*-
import os
import requests
from typing import Union

from mcdreforged.api.types import PluginServerInterface
from mcdreforged.api.utils import Serializable


class Config(Serializable):
    online_mode: Union[bool, None] = None


properties_path = os.path.join('server', 'server.properties')
online_mode = True
config: Config


def on_load(server: PluginServerInterface, old):
    global config, online_mode
    config = server.load_config_simple(
        'config.json',
        target_class=Config
    )
    online_mode = get_online_mode(server)
    server.logger.debug(f'服务器在线模式为: {online_mode}')


def get_online_mode(server):
    global config
    # 手动设置覆盖
    server.logger.info(config.online_mode)
    if config.online_mode is not None and isinstance(config.online_mode, bool):
        server.logger.info(f'使用手动设置的在线模式: {config.online_mode}')
        return config.online_mode

    # 读取服务器配置
    if not os.path.isfile(properties_path):
        server.logger.error('未找到服务器配置文件，使用默认配置 True')
        return True
    else:
        with open(properties_path) as f:
            for i in f.readlines():
                if 'online-mode' in i:
                    server.logger.debug(f'查找到配置项: {i}')
                    server_properties_config = i.split('=')[1].replace('\n', '')
                    break
        if server_properties_config == 'true':
            return True
        elif server_properties_config == 'false':
            return False
        else:
            server.logger.error('服务器配置项错误，使用默认配置 True')
            return True


def online_uuid(name):
    url = f'https://api.mojang.com/users/profiles/minecraft/{name}'
    r = get_try(url)
    if r is None:
        return None
    else:
        return r['id']


def offline_uuid(name):
    url = f'http://tools.glowingmines.eu/convertor/nick/{name}'
    r = get_try(url)
    if r is None:
        return None
    else:
        return r['offlineuuid']


def get_try(url):
    for i in range(0, 5):
        try:
            return requests.get(url).json()
        except:
            pass
    return None


def get_uuid(name: str):
    if online_mode:
        uuid = online_uuid(name)
    else:
        uuid = offline_uuid(name)
    return uuid
