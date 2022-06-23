# -*- coding: utf-8 -*-
from mcdreforged.api.types import PluginServerInterface, Info

writing_mode = False
player_name = None
code = ''


def on_user_info(server: PluginServerInterface, info: Info):
    global writing_mode, player_name, code
    if info.content == '!!xhh start':
        if writing_mode:
            server.reply(info, f'§c {player_name} 正在编写，请稍等！')
        else:
            writing_mode = True
            player_name = info.player
            code = ''
            server.reply(info, '§6请直接输入开始编写，以 !!xhh stop 结束')
            server.logger.debug(f'{info.player} 开始编写程序')
    elif info.content == '!!xhh stop':
        writing_mode = False
        try:
            server.logger.debug(f'执行 {code}')
            exec(code)
        except Exception as e:
            server.reply(info, f'§6{str(e)}')
    elif info.player == player_name:
        server.logger.debug(f'添加一行 {info.content}')
        code += info.content.replace('$', ' ') + '\n'
