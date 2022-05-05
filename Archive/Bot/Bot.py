# -*- coding: utf-8 -*-
from mcdreforged.api.types import PluginServerInterface
from mcdreforged.api.command import *
from mcdreforged.api.rtext import *

PLUGIN_METADATA = {
    'id': 'bot',
    'version': '0.0.1',
    'name': 'Bot',
    'description': 'Carpet bot easy manage and set',
    'author': 'zhang_anzhi',
    'link': 'https://github.com/AnzhiZhang/MCDReforgedPlugins/tree/master/Archive/Bot',
    'dependencies': {
        'config_api': '*',
        'json_data_api': '*'
    }
}
DIMENSIONS = {
    '0': 'minecraft:overworld',
    '-1': 'minecraft:the_nether',
    '1': 'minecraft:the_end',
    'overworld': 'minecraft:overworld',
    'the_nether': 'minecraft:the_nether',
    'the_end': 'minecraft:the_end',
    'nether': 'minecraft:the_nether',
    'end': 'minecraft:the_end',
    'minecraft:overworld': 'minecraft:overworld',
    'minecraft:the_nether': 'minecraft:the_nether',
    'minecraft:the_end': 'minecraft:the_end'
}
DEFAULT_CONFIG = {
    'gamemode': 'survival',
    'permissions': {
        'list': 1,
        'spawn': 2,
        'kill': 2,
        'add': 3,
        'remove': 3
    }
}
HELP_MESSAGE = '''§6!!bot §7显示机器人列表
§6!!bot spawn <name> §7生成机器人
§6!!bot kill <name> §7移除机器人
§6!!bot add <name> <dim> <x> <y> <z> <facing_level> <facing_pitch> §7添加机器人到机器人列表
§6!!bot remove <name> §7从机器人列表移除机器人'''


def on_load(server: PluginServerInterface, old):
    from ConfigAPI import Config
    from JsonDataAPI import Json
    config = Config(PLUGIN_METADATA['name'], DEFAULT_CONFIG)
    data = Json(PLUGIN_METADATA['name'])
    permissions = config['permissions']
    server.register_help_message('!!bot help', '显示Bot插件帮助')
    server.register_help_message(
        '!!bot',
        RText('显示机器人列表').c(RAction.run_command, '!!bot').h('点击显示机器人列表')
    )

    def show_list(src):
        c = []
        for a, b in data.items():
            bot_info = RTextList(
                '\n'
                f'§7----------- §6{a}§7 -----------\n',
                f'§7Dimension:§6 {b["dim"]}\n',
                f'§7Position:§6 {b["pos"]}\n',
                f'§7Facing:§6 {b["facing"]}\n',
                RText('§d点击放置\n').c(
                    RAction.run_command, f'!!bot spawn {a}').h(f'放置§6{a}'),
                RText('§d点击移除\n').c(
                    RAction.run_command, f'!!bot kill {a}').h(f'移除§6{a}')
            )
            c.append(bot_info)
        src.reply(RTextList(*c))

    def spawn(src, ctx):
        name = ctx['name']
        if name in data.keys():
            dim = data[name]['dim']
            pos = ' '.join([str(i) for i in data[name]['pos']])
            facing = data[name]['facing']
            command = f'player {name} spawn at {pos} facing {facing} in {dim}'
            src.get_server().execute(command)
            src.get_server().execute(f'gamemode {config["gamemode"]} {name}')
        else:
            src.reply('§c机器人名称不正确')

    def kill(src, ctx):
        name = ctx['name']
        if name in data.keys():
            server.execute(f'player {name} kill')
        else:
            src.reply('§c机器人名称不正确')

    def add(src, ctx):
        if ctx['dim'] in DIMENSIONS.keys():
            dim = DIMENSIONS[ctx['dim']]
            pos = [ctx['x'], ctx['y'], ctx['z']]
            facing = f'{ctx["facing_level"]} {ctx["facing_pitch"]}'
            data[ctx['name']] = {
                'dim': dim,
                'pos': pos,
                'facing': facing
            }
            data.save()
            src.reply(f'§a已添加机器人{ctx["name"]}')
        else:
            src.reply('§c无法识别的维度')

    def remove(src, ctx):
        name = ctx['name']
        if name in data.keys():
            del data[name]
            data.save()
            src.reply(f'§a已删除机器人{name}')
        else:
            src.reply('§c机器人名称不正确')

    server.register_command(
        Literal('!!bot').
            requires(lambda src: src.has_permission(permissions['list'])).
            runs(show_list).
            then(
            Literal('help').runs(lambda src: src.reply(HELP_MESSAGE))
        ).
            then(
            Literal('spawn').
                requires(lambda src: src.has_permission(permissions['spawn'])).
                then(
                Text('name').runs(spawn)
            )
        ).
            then(
            Literal('kill').
                requires(lambda src: src.has_permission(permissions['kill'])).
                then(
                Text('name').runs(kill)
            )
        ).
            then(
            Literal('add').
                requires(lambda src: src.has_permission(permissions['add'])).
                then(
                Text('name').then(
                    Text('dim').then(
                        Integer('x').then(
                            Integer('y').then(
                                Integer('z').then(
                                    Float('facing_level').then(
                                        Float('facing_pitch').runs(add)
                                    )
                                )
                            )
                        )
                    )))
        ).
            then(
            Literal('remove').
                requires(lambda src: src.has_permission(permissions['remove'])).
                then(
                Text('name').runs(remove)
            )
        )
    )
