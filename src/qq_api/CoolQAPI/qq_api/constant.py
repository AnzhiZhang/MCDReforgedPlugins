# -*- coding: utf-8 -*-
import os

VERSION = '0.2.0'
NAME = 'qq_api'
RELEASE_URL = 'https://api.github.com/repos/zhang-anzhi/CoolQAPI/releases/latest'


class FilePath:
    DATA_DIR = os.path.join('config', NAME)
    CONFIG_NAME = os.path.join(DATA_DIR, 'config.yml')
    UPDATE_DIR = os.path.join(DATA_DIR, 'update')
