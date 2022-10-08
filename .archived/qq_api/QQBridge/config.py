# -*- coding: utf-8 -*-
import os
import yaml


class Config:
    def __init__(self, logger):
        self.data = {}
        self.logger = logger
        self.file_path = 'config.yml'
        self.reload()

    def reload(self):
        self.data = {}
        if os.path.isfile(self.file_path):
            self._load()
        self.check_config()

    def touch(self, key, default):
        if key not in self.data:
            self.logger.warning(f'Use default config {default} '
                                f'for missing option {key}')
            self.data[key] = default
            self._add(key, default)

    def check_config(self):
        self.touch('post_host', '127.0.0.1')
        self.touch('post_port', 5701)
        self.touch('post_url', '/post')
        self.touch('server_list', {
            'example': {
                'host': '127.0.0.1',
                'port': 5702,
                'url': 'post'
            }
        })
        self.touch('debug_mode', False)

    def _load(self):
        with open(self.file_path, encoding='utf8') as f:
            self.data = yaml.safe_load(f)

    def _save(self):
        with open(self.file_path, 'w', encoding='utf8') as f:
            yaml.dump(self.data, f)

    def _add(self, key, value):
        with open(self.file_path, 'a', encoding='utf8') as f:
            yaml.dump({key: value}, f)

    def __getitem__(self, item):
        try:
            return self.data[item]
        except KeyError:
            self.logger.error('Configuration item missing, checking')
            self.check_config()
