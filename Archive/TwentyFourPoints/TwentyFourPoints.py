# -*- coding: utf-8 -*-
import time
import re
import itertools
import random
from threading import Thread
from decimal import Decimal

PLUGIN_METADATA = {
    'id': 'twenty_four_points',
    'version': '0.0.1',
    'name': 'TwentyFourPoints',
    'description': 'Twenty-four points game',
    'author': 'zhang_anzhi',
    'link': 'https://github.com/zhang-anzhi/MCDReforgedPlugins/tree/master/TwentyFourPoints',
    'dependencies': {
        'vault': '*'
    }
}
ask_time = 300
prize = 100

# ops list
operations = ('+', '-', '*', '/')
ops_list = [[x, y, z] for x in operations
            for y in operations
            for z in operations]


def on_unload(server):
    tfp.shutdown()


def on_mcdr_stop(server):
    tfp.shutdown()


def make_nums():
    while True:
        tfp.num_list = []
        for i in range(1, 5):
            tfp.num_list.append(random.randint(1, 12))
        if check_random():
            break


def ask(server):
    str_num_list = [str(i) for i in tfp.num_list]
    server.say('§8>>> §b使用 §a' + ' '.join(str_num_list) +
               ' §b计算24， 以 "24=" 开始你的表达式')


class TwentyFourPoints(Thread):
    def __init__(self, server):
        super().__init__(name='TwentyFourPoints')
        self.shutdown_flag = False
        self.server = server
        self.ask_on = False
        self.ans_correct = False
        self.ask_wait = 0
        self.num_list = []

    def run(self):
        while not self.shutdown_flag:
            time.sleep(ask_time)
            if self.shutdown_flag:
                self.ask_on = False
                return
            self.ask_on = True

            if self.ask_wait != 0 and self.ask_wait < 2:
                ask(self.server)
            else:
                make_nums()
                ask(self.server)
                self.ask_wait = 0
                self.ans_correct = False

            if not self.ans_correct:
                self.ask_wait += 1

    def shutdown(self):
        self.shutdown_flag = True


def on_load(server, old):
    global tfp
    tfp = TwentyFourPoints(server)
    tfp.start()

    global vault
    vault = server.get_plugin_instance('vault').vault


def on_user_info(server, info):
    if tfp.ask_on and info.is_player:
        if info.content.startswith('24='):
            answer = info.content[3:]
            check = check_answer(answer)
            if check == 0:
                tfp.ask_on = False
                tfp.ask_wait = 0
                tfp.ans_correct = True
                server.say('§a' + info.player + ' 回答正确!')
                vault.give(info.player, Decimal(prize))
                server.tell(info.player, '§a恭喜您获得回答正确奖励: ' + str(prize))
            elif check == 1:
                server.tell(info.player, '§c你使用的数字不正确!')
            elif check == 2:
                server.tell(info.player, '§c你的表达式结果不是24!')
            elif check == 3:
                server.tell(info.player, '§c你的表达式无法计算!')


def check_answer(expression):
    # check expression use whitelist symbol
    whitelist = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                 '+', '-', '*', '/', '(', ')']
    for c in expression:
        if c not in whitelist:
            return 3

    # check use number_list numbers
    num_check = re.split('\\+|-|\\*|/|\\(|\\)', expression)
    while '' in num_check:
        num_check.remove('')
    if len(num_check) != 4:
        return 1
    else:
        int_num_check = [int(x) for x in num_check]
        if sorted(int_num_check) != sorted(tfp.num_list):
            return 1

    # calc
    try:
        calc = eval(expression)
        if calc == 24:
            return 0
        else:
            return 2
    except Exception:
        return 3


def check_random():
    # num list
    each_num_list = []
    for number in itertools.permutations(tfp.num_list, 4):
        str_list = [str(numb) for numb in number]
        each_num_list.append(str_list)

    # exp list
    exp_list = []
    for a in each_num_list:
        for o in ops_list:
            o.append('')
            exp_list.append(list(itertools.chain.from_iterable(zip(a, o))))

    # brackets
    for exp in exp_list:
        for left in range(0, 8):
            for right in range(left + 1, 9):
                exp.insert(left, '(')
                exp.insert(right, ')')
                if exp[exp.index('(') - 1].isdigit():
                    exp.insert(exp.index('('), '*')
                    if check_working(exp):
                        return True
                    del exp[exp.index('(') - 1]
                else:
                    if check_working(exp):
                        return True
                exp.remove('(')
                exp.remove(')')


def check_working(expression):
    try:
        ans = eval(''.join(expression[:-1]))
        if ans == 24:
            return True
    except Exception:
        return False
