# -*- coding: utf-8 -*-
import os
import time
import logging

from colorlog import ColoredFormatter


class Logger:
    console_fmt = ColoredFormatter(
        '[%(asctime)s] [%(log_color)s%(levelname)s%(reset)s]: '
        '%(message_log_color)s%(message)s%(reset)s',
        log_colors={
            'DEBUG': 'blue',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        },
        secondary_log_colors={
            'message': {
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red'
            }
        },
        datefmt='%H:%M:%S'
    )
    file_fmt = logging.Formatter(
        '[%(asctime)s] [%(levelname)s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    def __init__(self):
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        self.file_path = 'logs/log.log'
        if not os.path.isdir('logs'):
            os.mkdir('logs')
        self.set_file()

        # Logger
        self.logger = logging.getLogger('QQBridge')
        self.logger.setLevel(logging.INFO)

        # Console Handler
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.INFO)
        self.ch.setFormatter(self.console_fmt)
        self.logger.addHandler(self.ch)

        # File handler
        self.fh = logging.FileHandler(self.file_path, encoding='utf-8')
        self.fh.setLevel(logging.INFO)
        self.fh.setFormatter(self.file_fmt)
        self.logger.addHandler(self.fh)

        self.debug = self.logger.debug
        self.info = self.logger.info
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical
        self.exception = self.logger.exception

    def set_file(self):
        if os.path.isfile(self.file_path):
            modify_time = time.strftime(
                '%Y-%m-%d',
                time.localtime(os.stat(self.file_path).st_mtime)
            )
            c = 0
            while c := c + 1:
                backup_file_name = f'logs/{modify_time}-{c}.log'
                if not os.path.isfile(backup_file_name):
                    os.rename('logs/log.log', backup_file_name)
                    break

    def set_level(self, level):
        self.logger.setLevel(level)
        self.ch.setLevel(level)
        self.fh.setLevel(level)
