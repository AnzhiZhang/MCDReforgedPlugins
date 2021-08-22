# -*- coding: utf-8 -*-
import os
import threading

from mcdreforged.api.command import *

PLUGIN_METADATA = {
    'id': 'mapcrafter_render',
    'version': '0.0.1',
    'name': 'MapcrafterRender',
    'description': 'User command to make new Mapcrafter.',
    'author': 'zhang_anzhi',
    'link': 'https://github.com/zhang-anzhi/MCDReforgedPlugins/tree/master/MapcrafterRender'
}
mapcrafter_path = 'mapcrafter'
output_path = ''
thread_num = 4


class Render(threading.Thread):
    def __init__(self, server):
        super().__init__(name='RenderMap')
        self.server = server
        self.is_render = False

    def run(self):
        self.is_render = True
        self.server.execute('save-off')
        self.server.execute('save-all')
        os.system(rf'rd /s /q {output_path}')
        os.system(rf'rd /s /q {mapcrafter_path}\world')
        os.system(rf'xcopy /e /y /q /i server\world {mapcrafter_path}\world')
        self.server.execute('save-on')
        os.system(rf'{mapcrafter_path}\mapcrafter.exe' +
                  rf' -c {mapcrafter_path}\config.conf -j {thread_num}')
        self.is_render = False


def on_load(server, old):
    global thread
    if old is not None and old.thread is not None:
        thread = old.thread
    else:
        thread = Render(server)
    server.logger.debug(f'当前渲染状态： {thread.is_render}')
    server.register_help_message('!!map', '渲染卫星图')

    def command(src):
        global thread
        if thread.is_render:
            return src.reply('§c正在渲染中, 请勿重复渲染!')
        try:
            thread.start()
        except RuntimeError:
            thread = Render(server)
            thread.start()
        src.get_server().logger.info('正在渲染卫星图')
        src.get_server().say('§6正在渲染服务器卫星图, 可能会导致游戏卡顿')

    server.register_command(
        Literal('!!map').
            requires(lambda src: src.has_permission(2)).
            runs(command)
    )
