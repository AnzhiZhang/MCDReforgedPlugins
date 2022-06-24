# -*- coding: utf-8 -*-
import requests
import os

# Set manual_mode as a bool if you uuid is not concerned server.properties
# Example: BungeeCord server turned on the online mode
MANUAL_MODE = None
PLUGIN_METADATA = {
    'id': 'uuid_api',
    'version': '0.0.1',
    'name': 'UUIDAPI',
    'description': 'UUID API',
    'author': 'Andy Zhang',
    'link': 'https://github.com/AnzhiZhang/MCDReforgedPlugins/tree/master/uuid_api'
}

# Do not change these
properties_path = os.path.join('server', 'server.properties')
online_mode = True


def on_load(server, old):
    global online_mode
    online_mode = get_online_mode(server)
    server.logger.debug(f'服务器在线模式为: {online_mode}')


def get_online_mode(server):
    if MANUAL_MODE is not None:
        server.logger.info(f'使用手动设置的在线模式: {manual_mode}')
        return MANUAL_MODE
    if not os.path.isfile(properties_path):
        return server.logger.error('未找到服务器配置文件')
    with open(properties_path) as f:
        for i in f.readlines():
            if 'online-mode' in i:
                break
        server.logger.debug(f'查找到配置项: {i}')
        i = i.split('=')[1].replace('\n', '')
    if i == 'true':
        return True
    elif i == 'false':
        return False
    else:
        server.logger.error('服务器配置项错误，使用默认配置True')
        return True


def online_uuid(name):
    url = f'http://api.mojang.com/users/profiles/minecraft/{name}'
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
            r = requests.get(url).json()
            return r
        except:
            pass
    return None


def get_uuid(name: str):
    if online_mode:
        uuid = online_uuid(name)
    else:
        uuid = offline_uuid(name)
    return uuid
