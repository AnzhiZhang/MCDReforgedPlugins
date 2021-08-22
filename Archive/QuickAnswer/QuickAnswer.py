# -*- coding: utf-8 -*-
import time
import random
from threading import Thread
from decimal import Decimal

PLUGIN_METADATA = {
    'id': 'quick_answer',
    'version': '0.0.1',
    'name': 'QuickAnswer',
    'description': 'Quick answerr some math questions',
    'author': 'zhang_anzhi',
    'link': 'https://github.com/zhang-anzhi/MCDReforgedPlugins/tree/master/QuickAnswer',
    'dependencies': {
        'vault': '*'
    }
}
ask_time = 300
prize = 100


def ask(server):
    global answer
    answer = 0
    charcacter = random.choice(['+', '-', '*', '/'])
    if charcacter in ['+', '-']:
        first = random.randint(1, 100)
        second = random.randint(1, 100)
        if charcacter == '+':
            answer = first + second
            server.say('§8>>> §b快速回答: ' + str(first) + '+' + str(second))
        elif charcacter == '-':
            answer = first - second
            server.say('§8>>> §b快速回答: ' + str(first) + '-' + str(second))
    if charcacter in ['*', '/']:
        first = random.randint(1, 20)
        second = random.randint(1, 20)
        if charcacter == '*':
            answer = first * second
            server.say('§8>>> §b快速回答: ' + str(first) + '*' + str(second))
        if charcacter == '/':
            while first % second != 0:
                first = random.randint(1, 20)
                second = random.randint(1, 20)
                answer = int(first / second)
            server.say('§8>>> §b快速回答: ' + str(first) + '/' + str(second))


class QuickAnswer(Thread):
    def __init__(self, server):
        super().__init__(name='QuickAnswer')
        self.shutdown_flag = False
        self.server = server

    def run(self):
        global ask_on, ask_wait
        while (not self.shutdown_flag):
            time.sleep(ask_time)
            if self.shutdown_flag:
                ask_on = False
                return
            if ask_on:
                if ask_wait < 2:
                    ask_wait += 1
                if ask_wait >= 2:
                    ask_wait = 0
                    ask(self.server)
                    ask_on = True
            else:
                ask(self.server)
                ask_on = True

    def shutdown(self):
        self.shutdown_flag = True


def on_load(server, old):
    global quickanswer, ask_on, ask_wait
    ask_on = False
    ask_wait = 0
    quickanswer = QuickAnswer(server)
    quickanswer.start()

    global vault
    vault = server.get_plugin_instance('vault').vault


def on_user_info(server, info):
    global ask_on, ask_wait
    if ask_on and info.is_player:
        if info.content.isdigit() or info.content.startswith('-'):
            if info.content.startswith('-'):
                if not info.content.lstrip('-').isdigit():
                    return
            if int(info.content) == answer:
                ask_on = False
                server.say('§a' + info.player + ' 回答正确!')
                vault.give(info.player, Decimal(prize))
                server.tell(info.player, '§a恭喜您获得回答正确奖励: ' + str(prize))
                ask_wait = 0
            else:
                server.tell(info.player, '§c回答错误!')


def on_unload(server):
    quickanswer.shutdown()


def on_mcdr_stop(server):
    quickanswer.shutdown()
