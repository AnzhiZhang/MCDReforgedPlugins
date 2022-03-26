# -*- coding: utf-8 -*-
from decimal import Decimal

from ConfigAPI import Config
from mcdreforged.plugin.server_interface import ServerInterface
from mcdreforged.api.command import *

PLUGIN_METADATA = {
    'id': 'economy',
    'version': '0.0.1',
    'name': 'Economy',
    'description': 'Economy plugin',
    'author': 'zhang_anzhi',
    'link': 'https://github.com/zhang-anzhi/MCDReforgedPlugins/tree/master/Economy',
    'dependencies': {
        'vault': '*',
        'config_api': '*'
    }
}
DEFAULT_CONFIG = {
    'MAXIMAL_TOPS': 10,
    'DEFAULT_BALANCE': 10.00,
    'REMINDER': False,
    'PERMISSIONS': {
        'top': 2,
        'check': 2,
        'give': 3,
        'take': 3,
        'set': 3
    }
}

HELP_MESSAGE = '''§6!!money §7查询余额
§6!!money top §7查看财富榜
§6!!money check <§6§oplayer§6> §7查询他人余额
§6!!money pay <§6§oplayer§6> <§6§oamount§6> §7将你的钱支付给他人
§6!!money give <§6§oplayer§6> <§6§oamount§6> §7给予他人钱
§6!!money take <§6§oplayer§6> <§6§oamount§6> §7拿取他人钱
§6!!money set <§6§oplayer§6> <§6§oamount§6> §7设置他人余额'''
REMINDER = True
PERMISSIONS = {}


def register_command(server: ServerInterface):
    def check_my(src):
        if src.is_player:
            src.reply(f'§a您的余额为: §e{vault.get_balance(src.player)}')
        else:
            src.reply(f'§a您没有账号')

    def top(src):
        i = 0
        for name, balance in vault.get_ranking().items():
            i += 1
            src.reply(f'§a{i}.§e{name}§a - §e{balance}')
            if i == config['MAXIMAL_TOPS']:
                break

    def check(src, ctx):
        try:
            amount = vault.get_balance(ctx['player'])
            src.reply(f'§e{ctx["player"]}§a的余额:§e {amount}')
        except vault.AccountNotExistsError:
            src.reply('§c账号不存在')

    def pay(src, ctx):
        try:
            if src.is_player:
                debit = src.player
                credit = ctx['player']
                amount = Decimal(str(round(ctx['amount'], 2)))
                vault.transfer(debit, credit, amount)
                src.reply(f'§a你向§e{credit}§a支付了§e{amount}')
                src.get_server().tell(credit, f'§e{debit}§a向你支付了§e{amount}')
            else:
                src.reply(f'§a您没有账号')
        except vault.AccountNotExistsError:
            src.reply('§c账号不存在')
        except vault.AmountIllegalError:
            src.reply('§c金额不合法')
        except vault.InsufficientBalanceError:
            src.reply('§c余额不足')

    def give(src, ctx):
        try:
            player = ctx['player']
            amount = Decimal(str(round(ctx['amount'], 2)))
            operator = f'Admin_{src.player}' if src.is_player else 'Admin'
            vault.give(player, amount, operator=operator)
            balance = vault.get_balance(player)
            src.reply(f'§a金钱已给予, §e{player}§a 现在有 §e{balance}')
            if REMINDER:
                src.get_server().tell(player, f'§a你被给予了金钱, 余额: §e{balance}')
        except vault.AccountNotExistsError:
            src.reply('§c账号不存在')
        except vault.AmountIllegalError:
            src.reply('§c金额不合法')

    def take(src, ctx):
        try:
            player = ctx['player']
            amount = Decimal(str(round(ctx['amount'], 2)))
            operator = f'Admin_{src.player}' if src.is_player else 'Admin'
            vault.take(player, amount, operator)
            balance = vault.get_balance(player)
            src.reply(f'§a金钱已拿取, §e{player}§a 现在有 §e{balance}')
            if REMINDER:
                src.get_server().tell(player, f'§a你被拿取了金钱, 余额: §e{balance}')
        except vault.AccountNotExistsError:
            src.reply('§c账号不存在')
        except vault.AmountIllegalError:
            src.reply('§c金额不合法')
        except vault.InsufficientBalanceError:
            src.reply('§c余额不足')

    def _set(src, ctx):
        try:
            player = ctx['player']
            amount = Decimal(str(round(ctx['amount'], 2)))
            operator = f'Admin_{src.player}' if src.is_player else 'Admin'
            vault.set(player, amount, operator)
            src.reply(f'§a金钱已设置, §e{player}§a 现在有 §e{amount}')
            if REMINDER:
                src.get_server().tell(player, f'§a你被设置了金钱, 余额: §e{amount}')
        except vault.AccountNotExistsError:
            src.reply('§c账号不存在')
        except vault.AmountIllegalError:
            src.reply('§c金额不合法')

    server.register_command(
        Literal('!!money').
            runs(check_my).
            then(
            Literal('help').
                runs(lambda src: src.reply(HELP_MESSAGE))
        ).
            then(
            Literal('top').
                requires(lambda src: src.has_permission(PERMISSIONS['top'])).
                runs(top)
        ).
            then(
            Literal('check').
                requires(lambda src: src.has_permission(PERMISSIONS['check'])).
                then(
                Text('player').runs(check)
            )
        ).
            then(
            Literal('pay').
                then(
                Text('player').
                    then(
                    Float('amount').runs(pay)
                )
            )
        ).
            then(
            Literal('give').
                requires(lambda src: src.has_permission(PERMISSIONS['give'])).
                then(
                Text('player').
                    then(
                    Float('amount').runs(give)
                )
            )
        ).
            then(
            Literal('take').
                requires(lambda src: src.has_permission(PERMISSIONS['take'])).
                then(
                Text('player').
                    then(
                    Float('amount').runs(take)
                )
            )
        ).
            then(
            Literal('set').
                requires(lambda src: src.has_permission(PERMISSIONS['set'])).
                then(
                Text('player').
                    then(
                    Float('amount').runs(_set)
                )
            )
        )
    )


def on_load(server, old):
    # Vault
    global vault
    vault = server.get_plugin_instance('vault').vault

    # Config
    global config, REMINDER, PERMISSIONS
    config = Config(PLUGIN_METADATA['name'], DEFAULT_CONFIG)
    REMINDER = config['REMINDER']
    PERMISSIONS = config['PERMISSIONS']

    # Help msg
    server.register_help_message('!!money help', '§a经济系统帮助')
    server.register_help_message('!!money', '§a查询余额')
    register_command(server)


def on_player_joined(server, player, info):
    if not vault.is_account(player):
        vault.create_account(player)
        vault.set(
            player,
            Decimal(round(config['DEFAULT_BALANCE'], 2)),
            f'Admin_{PLUGIN_METADATA["name"]}'
        )
