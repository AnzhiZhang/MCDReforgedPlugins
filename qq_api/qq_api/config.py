# -*- coding: utf-8 -*-
import os
import yaml

from .constant import FilePath


class Config:
    def __init__(self):
        self.file_path = FilePath.CONFIG_NAME
        self.data = None
        self.default = {
            'post_host': '127.0.0.1',
            'post_port': 5701,
            'post_path': 'post',
            'api_host': '127.0.0.1',
            'api_port': 5700,
            'command_prefix': '/',
        }
        self.__check()

    def __check(self):
        self.__load()
        save_flag = False
        for key, value in self.default.items():
            if key not in self.data.keys():
                self.data[key] = value
                save_flag = True
        if save_flag:
            self.__save()

    def __load(self):
        if os.path.isfile(self.file_path):
            with open(self.file_path, encoding='utf-8') as f:
                self.data = yaml.safe_load(f)
        else:
            self.data = self.default
            self.__save()

    def __save(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.data, f)

    def __getitem__(self, item):
        return self.data[item]
