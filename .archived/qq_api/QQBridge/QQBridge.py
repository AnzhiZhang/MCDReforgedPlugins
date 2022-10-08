# -*- coding: utf-8 -*-
import requests
import json
import re
import psutil
import threading
from flask import Flask, request
from logging import INFO, DEBUG

from config import Config
from logger import Logger

help_msg = '''stop 关闭QQBridge
help 获取帮助
reload config 重载配置文件
debug thread 查看线程列表
'''


class Console(threading.Thread):

    def __init__(self, logger, config):
        super().__init__(name='Console')
        self.p = psutil.Process()
        self.logger = logger
        self.config = config
        self.cmd = []
        self.logger.info('After server startup, type "help" for help')

    def run(self):
        while True:
            try:
                raw_input = input()
                # 直接回车
                if raw_input == '':
                    continue
                # 拆分清理
                cmd_list = re.split(r'\s+', raw_input)
                self.cmd = [i for i in cmd_list if i != '']
                self.logger.debug('Console input: ')
                self.logger.debug(f'    Raw input: "{raw_input}"')
                self.logger.debug(f'    Split result: {self.cmd}')
                self.cmd_parser()
            except EOFError or KeyboardInterrupt as e:
                self.exit()

    def send_msg(self, msg):
        for i in msg.splitlines():
            self.logger.info(i)

    def cmd_parser(self):
        if self.cmd[0] in ['stop', '__stop__', 'exit']:
            self.exit()
        elif self.cmd[0] == 'help':
            self.send_msg(help_msg)
        elif self.cmd[0] == 'reload':
            self.cmd_reload_parser()
        elif self.cmd[0] == 'debug':
            self.cmd_debug_parser()

    def cmd_reload_parser(self):
        if self.cmd[1] == 'config':
            self.reload_config()

    def cmd_debug_parser(self):
        if self.cmd[1] == 'thread':
            thread_list = threading.enumerate()
            self.logger.info(f'当前线程列表, 共 {len(thread_list)} 个活跃线程:')
            for i in thread_list:
                self.logger.info(f'    - {i.getName()}')

    def reload_config(self):
        self.logger.info('正在重载配置文件')
        self.config.reload()
        if self.config['debug_mode']:
            self.logger.set_level(DEBUG)
        else:
            self.logger.set_level(INFO)
        self.logger.info('重载配置文件完成')

    def exit(self):
        self.logger.info('Exiting QQBridge')
        self.p.terminate()


class QQBridge:
    def __init__(self):
        self.logger = Logger()
        self.config = Config(self.logger)
        if self.config['debug_mode']:
            self.logger.set_level(DEBUG)
        self.server = Flask(__name__)

        # Console
        self.console = Console(self.logger, self.config)
        self.console.start()

        # Flask server
        self.start()

    def start(self):
        @self.server.route(self.config['post_url'], methods=['POST'])
        def recv():
            data = json.loads(request.get_data().decode('utf-8'))
            self.logger.info(f'Received data from {request.remote_addr}')
            self.logger.debug(json.dumps(data, indent=4, ensure_ascii=False))
            self.send(data)
            return ''

        self.logger.info(f'Server starting up with {self.config["post_host"]}:'
                         f'{self.config["post_port"]}'
                         f'{self.config["post_url"]}')
        self.server.run(port=self.config['post_port'],
                        host=self.config['post_host'],
                        threaded=False)

    def send(self, data):
        self.logger.debug(f'All server list: '
                          f'{json.dumps(self.config["server_list"], indent=4)}')
        for server_name, i in self.config['server_list'].items():
            target = f'http://{i["host"]}:{i["port"]}/{i["url"]}'
            self.logger.info(f'Transmitting to the server {server_name}')
            self.logger.debug(f'Server address {target}')
            # 添加标识
            data['server'] = server_name
            try:
                requests.post(target, json=data)
                self.logger.info(f'Transmit to {server_name} success')
            except:
                self.logger.warning(f'Transmit to {server_name} failed')


bridge = QQBridge()
