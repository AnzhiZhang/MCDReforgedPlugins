# -*- coding: utf-8 -*-
import re
import time
import json
import asyncio
import threading
from logging import INFO, DEBUG

import psutil
import requests
import websockets
from flask import Flask, request

from config import Config
from logger import Logger

help_msg = '''stop 关闭 QQBridge
help 获取帮助
reload config 重载配置文件
debug thread 查看线程列表
'''


class Console(threading.Thread):
    def __init__(self, logger, config):
        super().__init__(name='Console')
        self.process = psutil.Process()
        self.logger = logger
        self.config = config
        self.cmd = []
        self.logger.info('After startup, type "help" for help')

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
            except EOFError or KeyboardInterrupt:
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
            self.logger.info(
                f'当前线程列表, 共 {len(thread_list)} 个活跃线程:'
            )
            for i in thread_list:
                self.logger.info(f'    - {i.name}')

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
        self.process.terminate()


class BaseWebsocket:
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.event_loop = asyncio.get_event_loop()
        self.websocket: websockets.WebSocketClientProtocol = None

    def send(self, message: dict):
        if self.websocket is not None:
            self.event_loop.create_task(
                self.websocket.send(json.dumps(message))
            )

    def start(self):
        raise NotImplementedError


class UpstreamWebsocket(BaseWebsocket):
    def __init__(
            self,
            logger,
            config,
            downstream_list: list['DownstreamWebsocket']
    ):
        super().__init__(logger, config)
        self.downstream_list = downstream_list

    async def recv(self, websocket):
        self.websocket = websocket
        self.logger.info("Connected to the upstream server")
        while True:
            try:
                # parse data
                data = json.loads(await websocket.recv())

                # pass heartbeat
                if data.get("meta_event_type") == "heartbeat":
                    continue

                # log
                self.logger.info(
                    f'Received data from upstream {self.config["host"]}'
                )
                self.logger.debug(json.dumps(
                    data,
                    indent=4,
                    ensure_ascii=False
                ))

                # dispatch to servers
                for i in self.downstream_list:
                    i.send(data)
            except websockets.ConnectionClosed:
                self.logger.warning('Upstream WebSocket connection closed')
                break

    def start(self):
        self.logger.info(
            f'WebSocket server for upstream starting with '
            f'{self.config["host"]}:{self.config["port"]}'
        )
        self.event_loop.run_until_complete(websockets.serve(
            self.recv,
            self.config['host'],
            self.config['port']
        ))
        self.event_loop.run_forever()


class DownstreamWebsocket(BaseWebsocket):
    def __init__(
            self, logger, config, upstream_websocket: 'UpstreamWebsocket',
            name: str, host: str, port: int
    ):
        super().__init__(logger, config)
        self.upstream_websocket = upstream_websocket
        self.name = name
        self.url = f'ws://{host}:{port}/ws/'

    async def recv(self):
        self.logger.info(
            f'Connecting to the server "{self.name}" at {self.url}'
        )

        # connect
        async with websockets.connect(
                self.url,
                extra_headers={
                    "Content-Type": "application/json",
                    "User-Agent": "QQBridge",
                    "X-Self-ID": None,
                    "X-Client-Role": "Universal"
                }
        ) as websocket:
            # save websocket
            self.websocket = websocket
            self.logger.info(f'Connected to the server "{self.name}"')

            # main loop
            while True:
                # parse data
                data = json.loads(await websocket.recv())

                # log
                self.logger.info(
                    f'Received data from downstream "{self.name}"'
                )
                self.logger.debug(json.dumps(
                    data,
                    indent=4,
                    ensure_ascii=False
                ))

                # send to upstream
                self.upstream_websocket.send(data)

    def send(self, data):
        data['server'] = self.name
        super().send(data)

    def start(self):
        def retry():
            self.logger.warning(f'Reconnecting...')
            time.sleep(1)

        async def run():
            while True:
                try:
                    await self.recv()
                except websockets.ConnectionClosed:
                    self.logger.error(
                        f'Downstream WebSocket connection "{self.name}" closed'
                    )
                    retry()
                except ConnectionRefusedError:
                    self.logger.error(f'Cannot connect to "{self.name}"')
                    retry()

        self.event_loop.create_task(run())


class QQBridge:
    def __init__(self):
        self.logger = Logger()
        self.config = Config(self.logger)
        if self.config['debug_mode']:
            self.logger.set_level(DEBUG)

        # Console
        self.console = Console(self.logger, self.config)
        self.console.start()

        if self.config['websocket'] is True:
            self.start_websocket()
        else:
            self.start_http()

    def start_http(self):
        app = Flask(__name__)

        @app.route('/', methods=['POST'])
        def recv():
            data = json.loads(request.get_data().decode('utf-8'))
            headers = request.headers
            self.logger.info(f'Received data from {request.remote_addr}')
            self.logger.debug(json.dumps(data, indent=4, ensure_ascii=False))
            self.send(data, headers)
            return ''

        self.logger.info(
            f'HTTP server starting up with '
            f'{self.config["host"]}:{self.config["port"]}'
        )
        app.run(
            host=self.config['host'],
            port=self.config['port'],
            threaded=False
        )

    def start_websocket(self):
        # init
        downstream_list = []
        upstream_websocket = UpstreamWebsocket(
            self.logger,
            self.config,
            downstream_list
        )

        # start downstream websockets
        for server_name, i in self.config['server_list'].items():
            downstream_websocket = DownstreamWebsocket(
                self.logger,
                self.config,
                upstream_websocket,
                server_name,
                i['host'],
                i['port']
            )
            downstream_websocket.start()
            downstream_list.append(downstream_websocket)

        # start upstream websocket
        upstream_websocket.start()

    def send(self, data, headers):
        self.logger.debug(
            f'All server list: '
            f'{json.dumps(self.config["server_list"], indent=4)}'
        )
        for server_name, i in self.config['server_list'].items():
            target = f'http://{i["host"]}:{i["port"]}'
            self.logger.info(f'Transmitting to the server {server_name}')
            self.logger.debug(f'Server address {target}')
            # 添加标识
            data['server'] = server_name
            try:
                requests.post(target, json=data, headers=headers)
                self.logger.info(f'Transmit to {server_name} success')
            except:
                self.logger.warning(f'Transmit to {server_name} failed')


bridge = QQBridge()
