import os
import json
import requests
from uuid import UUID

from mcdreforged.api.types import PluginServerInterface
from mcdreforged.api.utils import Serializable

PROPERTIES_FILE_PATH = os.path.join('server', 'server.properties')
USERCACHE_FILE_PATH = os.path.join('server', 'usercache.json')


class Config(Serializable):
    use_usercache: bool = True
    override_online_mode: bool = False
    override_online_mode_value: bool = True


config: Config
online_mode: bool = True
uuid_cache: dict[str, UUID] = {}


def on_load(server: PluginServerInterface, old):
    global config, online_mode

    # load config
    config = server.load_config_simple(
        'config.json',
        target_class=Config
    )

    # update online mode
    if config.override_online_mode:
        online_mode = config.override_online_mode_value
    else:
        # get from server.properties
        online_mode = get_online_mode()
        server.logger.debug(
            f'Load online mode from server.properties: {online_mode}'
        )

        # if cannot determine online mode from server.properties
        if online_mode is None:
            server.logger.error(
                'Could not determine online mode from server.properties. '
                'Please check the file or set override_online_mode. '
                'Defaulting to online mode (True).'
            )
            online_mode = True

    # load uuids from usercache.json if enabled
    if config.use_usercache:
        read_usercache()


def get_online_mode() -> bool | None:
    """
    Get the online mode setting from server.properties.
    """
    # check if server.properties exists
    if not os.path.isfile(PROPERTIES_FILE_PATH):
        return None

    # read server.properties
    with open(PROPERTIES_FILE_PATH) as f:
        for i in f.readlines():
            if 'online-mode' in i:
                online_mode_setting = i.split('=')[1].replace('\n', '')
                break

    # return the online mode setting
    if online_mode_setting == 'true':
        return True
    elif online_mode_setting == 'false':
        return False
    else:
        return None


def read_usercache():
    """
    Reads the usercache.json and loads it into the cache.
    """
    global uuid_cache

    # check if usercache.json exists
    if not os.path.isfile(USERCACHE_FILE_PATH):
        return

    # read usercache.json
    uuid_cache = {}
    with open(USERCACHE_FILE_PATH, 'r', encoding='utf-8') as f:
        usercache = json.load(f)
        for cache in usercache:
            if 'name' in cache and 'uuid' in cache:
                uuid_cache[cache['name']] = UUID(cache['uuid'])


def online_uuid(name) -> UUID | None:
    url = f'https://api.mojang.com/users/profiles/minecraft/{name}'
    r = get_try(url)
    if r is None:
        return None
    else:
        uuid = r.get('id', None)
        return UUID(uuid) if uuid is not None else None


def offline_uuid(name) -> UUID | None:
    url = f'http://tools.glowingmines.eu/convertor/nick/{name}'
    r = get_try(url)
    if r is None:
        return None
    else:
        uuid = r.get('offlineuuid', None)
        return UUID(uuid) if uuid is not None else None


def get_try(url) -> dict | None:
    for i in range(0, 5):
        try:
            return requests.get(url).json()
        except requests.RequestException:
            pass
    return None


def get_uuid(name: str) -> UUID | None:
    # return cached uuid if exists
    if name in uuid_cache:
        return uuid_cache[name]

    # fetch uuid if not cached
    if online_mode:
        uuid = online_uuid(name)
    else:
        uuid = offline_uuid(name)

    # add to cache
    if uuid is not None:
        uuid_cache[name] = uuid

    # return the uuid
    return uuid
