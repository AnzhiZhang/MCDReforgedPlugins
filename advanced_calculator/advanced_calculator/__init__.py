# -*- coding: utf-8 -*-
from mcdreforged.api.types import PluginServerInterface, Info
from mcdreforged.api.command import *
from mcdreforged.api.rtext import *

EXPRESSION_WHITELIST = [
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    ' ', '.', '+', '-', '*', '/', '(', ')', '<', '>', '='
]
HELP_MSG = '''§7!!calc <expression> §6计算表达式
§7!!calc item <count/expression> §6物品数转换堆叠数
§7!!calc item <box> <stack> <single> §6堆叠数转换物品数
§7!!calc color <red> <green> <blue> §610进制RGB转16进制
§7!!calc color <#HEX> §616十进制RGB转10进制'''


class Stack:
    def __init__(self, box=0, stack=0, single=0):
        self.box = box
        self.stack = stack
        self.single = single


class IllegalCharacterException(Exception):
    def __init__(self, character: str):
        super().__init__(f'§cCharacter §6{character} §cis illegal')


def security_eval(expression: str):
    """
    A security eval function.
    :param expression: String expression.
    :return: Eval result.
    """
    # Double *
    if "**" in expression:
        raise IllegalCharacterException("**")

    # Character whitelist
    for i in expression:
        if i not in EXPRESSION_WHITELIST:
            raise IllegalCharacterException(i)

    # return eval result
    return eval(expression)


def on_load(server: PluginServerInterface, old):
    server.register_help_message('!!calc', '查看计算插件使用帮助')
    server.register_help_message('=<expression>', '等同于 !!calc <expression>')
    server.register_help_message('==<count>', '等同于 !!calc item <count>')
    server.register_command(
        Literal('!!calc')
        .requires(lambda src: src.is_player)
        .runs(lambda src: src.reply(HELP_MSG))
        .then(
            Literal('item')
            .then(
                Text('box/count')
                .runs(calc_item)
                .then(
                    Integer('stack')
                    .then(
                        Integer('single').runs(calc_item)
                    )
                )
            )
        )
        .then(
            Literal('color')
            .then(
                Text('red/#HEX')
                .runs(calc_color)
                .then(
                    Integer('green')
                    .then(
                        Integer('blue').runs(calc_color)
                    )
                )
            )
        )
        .then(
            GreedyText('expression').runs(calc_expression)
        )
    )


def on_user_info(server: PluginServerInterface, info: Info):
    if info.content.startswith('=='):
        calc_item(
            info.get_command_source(),
            {'box/count': info.content[2:]}
        )
    elif info.content.startswith('='):
        calc_expression(
            info.get_command_source(),
            {'expression': info.content[1:]}
        )


def say_error_info(src, exp, error):
    return src.get_server().say(
        RText(f'§c计算 §6{exp} §c出错: §6{type(error).__name__}').h(error)
    )


def calc_expression(src, ctx):
    expression = ctx['expression']
    try:
        src.get_server().say(f'§7{expression}=§6{security_eval(expression)}')
    except (
            NameError,
            SyntaxError,
            ZeroDivisionError,
            IllegalCharacterException
    ) as e:
        say_error_info(src, expression, e)


def calc_item(src, ctx):
    if len(ctx) == 1:
        expression = ctx['box/count']
        try:
            count = security_eval(expression)
            s = Stack()
            s.single = count % 64
            s.box = count // (64 * 27)
            s.stack = (count - s.box * 64 * 27) // 64
            src.get_server().say(
                RTextList(
                    f'§6{count}§7个物品为',
                    RText(f'{s.box}盒', color=RColor.yellow),
                    RText(f'{s.stack}组', color=RColor.green),
                    RText(f'{s.single}个', color=RColor.aqua)
                )
            )
        except (
                NameError,
                SyntaxError,
                ZeroDivisionError,
                IllegalCharacterException
        ) as e:
            say_error_info(src, expression, e)
    else:
        try:
            ctx['box/count'] = int(ctx['box/count'])
            s = Stack(ctx['box/count'], ctx['stack'], ctx['single'])
            count = (s.box * 64 * 27) + (s.stack * 64) + s.single
            src.get_server().say(RTextList(
                RText(f'{s.box}盒', color=RColor.yellow),
                RText(f'{s.stack}组', color=RColor.green),
                RText(f'{s.single}个', color=RColor.aqua),
                f'§7为§6{count}§7个物品',
            ))
        except ValueError:
            src.get_server().say(RText('无效的整数', color=RColor.red))


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
