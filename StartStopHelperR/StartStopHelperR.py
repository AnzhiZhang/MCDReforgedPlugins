# -*- coding: utf-8 -*-
import time

from mcdreforged.plugin.server_interface import ServerInterface
from mcdreforged.api.command import *
from mcdreforged.api.rtext import *
from mcdreforged.api.decorator import new_thread

PLUGIN_METADATA = {
    'id': 'start_stop_helper_r',
    'version': '0.0.1',
    'name': 'StartStopHelperR',
    'description': 'Start and stop server helper',
    'author': ['Fallen_Breath', 'zhang_anzhi'],
    'link': 'https://github.com/zhang-anzhi/MCDReforgedPlugins/tree/master/StartStopHelperR'
}
PERMISSIONS = {
    'help': 2,
    'abort': 2,
    'start': 3,
    'stop': 3,
    'stop_exit': 4,
    'restart': 2,
    'exit': 4,
}
DEFAULT_WAIT_TIME = 10
HELP_MESSAGE = '''§6!!server §7显示帮助信息
§6!!server abort §7中止
§6!!server start §7启动服务器
§6!!server stop [time] §7关闭服务器
§6!!server stop_exit [time] §7关闭服务器并退出MCDR
§6!!server restart [time] §7重启服务器
§6!!server exit §7退出MCDR'''
abort_flag = False


def wait(server, command, time_wait=DEFAULT_WAIT_TIME):
    global abort_flag
    for countdown in range(0, time_wait):
        server.say(
            RText(
                f'Server will §c{command}§r in §e{time_wait - countdown}§r '
                f'second! Use §7!!server abort§r to abort'
            )
                .set_click_event(RAction.run_command, '!!server abort')
                .set_hover_text('§cClick to abort')
        )
        for i in range(10):
            time.sleep(0.1)
            if abort_flag:
                abort_flag = False
                server.say('§cAborted!')
                return False
    else:
        return True


def on_load(server: ServerInterface, old):
    def abort():
        global abort_flag
        abort_flag = True

    @new_thread(PLUGIN_METADATA['name'])
    def stop(src, ctx):
        if wait(server, 'stop', ctx.get('time', DEFAULT_WAIT_TIME)):
            server.stop()

    @new_thread(PLUGIN_METADATA['name'])
    def stop_exit(src, ctx):
        if wait(server, 'stop', ctx.get('time', DEFAULT_WAIT_TIME)):
            server.stop_exit()

    @new_thread(PLUGIN_METADATA['name'])
    def restart(src, ctx):
        if wait(server, 'restart', ctx.get('time', DEFAULT_WAIT_TIME)):
            server.restart()

    server.register_help_message('!!server', '服务器控制指令')
    server.register_command(
        Literal('!!server').
            requires(lambda src: src.has_permission(PERMISSIONS['help'])).
            runs(lambda src: src.reply(HELP_MESSAGE)).
            then(
            Literal('abort').
                requires(lambda src: src.has_permission(PERMISSIONS['abort'])).
                runs(abort)
        ).
            then(
            Literal('start').
                requires(lambda src: src.has_permission(PERMISSIONS['start'])).
                runs(lambda src: server.start())
        ).
            then(
            Literal('stop').
                requires(lambda src: src.has_permission(PERMISSIONS['stop'])).
                runs(stop).
                then(
                Integer('time').
                    runs(stop)
            )
        ).
            then(
            Literal('stop_exit').
                requires(
                lambda src: src.has_permission(PERMISSIONS['stop_exit'])).
                runs(stop_exit).
                then(
                Integer('time').
                    runs(stop_exit)
            )
        ).
            then(
            Literal('restart').
                requires(
                lambda src: src.has_permission(PERMISSIONS['restart'])).
                runs(restart).
                then(
                Integer('time').
                    runs(restart)
            )
        ).
            then(
            Literal('exit').
                requires(lambda src: src.has_permission(PERMISSIONS['exit'])).
                runs(lambda src: server.exit())
        )
    )
