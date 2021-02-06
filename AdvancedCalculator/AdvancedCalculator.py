# -*- coding: utf-8 -*-
from mcdreforged.plugin.server_interface import ServerInterface
from mcdreforged.api.command import *
from mcdreforged.api.rtext import *

PLUGIN_METADATA = {
    'id': 'advanced_calculator',
    'version': '0.0.1',
    'name': 'AdvancedCalculator',
    'description': 'In game multiple calculator',
    'author': 'zhang_anzhi',
    'link': 'https://github.com/zhang-anzhi/MCDReforgedPlugins/tree/master/AdvancedCalculator'
}
HELP_MSG = '''§7!!calc <expression> §6计算表达式
§7!!calc item <count> §6物品数转换堆叠数
§7!!calc item <box> <stack> <single> §6堆叠数转换物品数
§7!!calc color <red> <green> <blue> §610进制RGB转16进制
§7!!calc color <#HEX> §616十进制RGB转10进制'''


class Stack:
    def __init__(self, box=0, stack=0, single=0):
        self.box = box
        self.stack = stack
        self.single = single


def on_load(server: ServerInterface, old):
    server.register_help_message('!!calc', '查看计算插件使用帮助')
    server.register_command(
        Literal('!!calc').
            requires(lambda src: src.is_player).
            runs(lambda src: src.reply(HELP_MSG)).
            then(
            Literal('item').
                then(
                Integer('box/count').
                    runs(calc_item).
                    then(
                    Integer('stack').
                        then(
                        Integer('single').runs(calc_item)
                    )
                )
            )
        ).
            then(
            Literal('color').
                then(
                Text('red/#HEX').
                    runs(calc_color).
                    then(
                    Integer('green').
                        then(
                        Integer('blue').runs(calc_color)
                    )
                )
            )
        ).
            then(
            GreedyText('expression').runs(calc_expression)
        )
    )


def calc_expression(src, ctx):
    exp = ctx['expression']
    try:
        message = f'§7{exp}=§6{eval(exp)}'
    except (NameError, SyntaxError, ZeroDivisionError) as e:
        message = RText(f'§c计算 §6{exp} §c出错: §6{type(e).__name__}').h(e)
    src.get_server().say(message)


def calc_item(src, ctx):
    if len(ctx) == 1:
        count = ctx['box/count']
        s = Stack()
        s.single = count % 64
        s.box = count // (64 * 27)
        s.stack = (count - s.box * 64 * 27) // 64
        src.get_server().say(RTextList(
            f'§6{count}§7个物品为',
            RText(f'{s.box}盒', color=RColor.yellow),
            RText(f'{s.stack}组', color=RColor.green),
            RText(f'{s.single}个', color=RColor.aqua)
        ))
    else:
        s = Stack(ctx['box/count'], ctx['stack'], ctx['single'])
        count = (s.box * 64 * 27) + (s.stack * 64) + s.single
        src.get_server().say(RTextList(
            RText(f'{s.box}盒', color=RColor.yellow),
            RText(f'{s.stack}组', color=RColor.green),
            RText(f'{s.single}个', color=RColor.aqua),
            f'§7为§6{count}§7个物品',
        ))


def calc_color(src, ctx):
    def rgb_to_hex(red, green, blue):
        c = ''
        src.get_server().logger.info((red, green, blue))
        for color in (red, green, blue):
            color = int(color)
            if not (0 <= color <= 255):
                raise ValueError('Color must between 0-255')
            c += hex(color)[-2:].replace('x', '0').zfill(2)
        return c.upper()

    def hex_to_rgb(red, green, blue):
        rgb = []
        for i in (red, green, blue):
            color = int(i.lower(), 16)
            if not (0 <= color <= 255):
                raise ValueError('Color must between 00-ff')
            rgb.append(color)
        return tuple(rgb)

    try:
        if len(ctx) == 1:
            _hex = ctx['red/#HEX'].upper()
            result = hex_to_rgb(_hex[1:3], _hex[3:5], _hex[5:])
            message = f'§6{_hex} §7-> §6{result}'
        else:
            ctx['red/#HEX'] = int(ctx['red/#HEX'])
            message = f'§6{tuple(ctx.values())} §7-> §6#{rgb_to_hex(*ctx.values())}'
    except Exception as e:
        message = RText(f'§c计算出错: §6{type(e).__name__}').h(e)
    src.get_server().say(message)
