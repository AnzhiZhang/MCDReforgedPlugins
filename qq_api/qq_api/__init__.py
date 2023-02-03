# -*- coding: utf-8 -*-
import requests
import os
from threading import Thread

from mcdreforged.api.command import *
from mcdreforged.api.event import LiteralEvent

from qq_api.constant import NAME, VERSION, RELEASE_URL, FilePath
from qq_api.functions import touch_folder, version_compare
from qq_api.factory import Factory

HELP_MESSAGE = '§6!!cq update §7检查并自动更新'

touch_folder(FilePath.DATA_DIR)
factory = Factory()


def on_load(server, old):
    server.register_help_message('!!cq', 'CoolQAPI插件帮助')
    server.register_command(
        Literal('!!cq').
            runs(lambda src: src.reply(HELP_MESSAGE)).
            then(
            Literal('update').
                runs(
                lambda src: Thread(
                    target=check_update,
                    args=(src.get_server(), src),
                    name=NAME
                ).start()
            )
        )
    )

    Thread(target=check_update, args=(server,), name=NAME).start()
    factory.injection(server)
    server.dispatch_event(LiteralEvent('cool_q_api.on_qq_load'), (factory.bot,))
    factory.post_server.start()


def on_unload(server):
    stop()


def on_mcdr_stop(server):
    stop()


def stop():
    requests.post(
        f'http://{factory.config["post_host"]}:{factory.config["post_port"]}/'
        f'{factory.config["post_path"]}',
        json={'shutdown': True}
    )


def check_update(server, src=None):
    def download(link, path):
        if not os.path.isdir(FilePath.UPDATE_DIR):
            os.mkdir(FilePath.UPDATE_DIR)
        with open(path, 'wb') as f:
            f.write(requests.get(link).content)

    try:
        server.logger.info('检测更新中')
        r = requests.get(RELEASE_URL).json()
        try:
            compare = version_compare(r['tag_name'], VERSION)
        except ValueError:
            server.logger.error('您的版本号错误, 自动为您下载最新版中')
            compare = 1
        if compare == 0:
            server.logger.info('qq_api 已为最新版')
        elif compare == 1:
            server.logger.info('发现新版本: ' + r['tag_name'])
            file_path = os.path.join(
                FilePath.UPDATE_DIR,
                f'{NAME}-{r["tag_name"]}.zip'
            )
            download(r['assets'][0]['browser_download_url'], file_path)
            server.logger.info(f'更新下载完成, 文件位于 {file_path}')
        elif compare == -1:
            server.logger.info('检测到 qq_api 为开发版')
    except:
        if src is None:
            server.logger.error('qq_api 更新失败')
        else:
            src.reply('§cCoolQAPI 更新失败')


def get_bot():
    """return bot object"""
    return factory.bot


def get_config():
    """get the api config"""
    return factory.config
