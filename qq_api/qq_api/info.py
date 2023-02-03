# -*- coding: utf-8 -*-
import json
import re
from typing import TYPE_CHECKING

from flask import request
from mcdreforged.api.event import LiteralEvent

if TYPE_CHECKING:
    from .factory import Factory


class Info:
    def __init__(self, factory: 'Factory', data: dict):
        self.__server = factory.mcdr_server
        self.__config = factory.config
        self.__bot = factory.bot
        self.__data = data

        # parse
        # global
        self.raw = None
        self.time = None
        self.post_type = None
        self.source_type = None
        self.source_id = None
        self.server = None

        # message
        self.message_id = None
        self.user_id = None
        self.source_sub_type = None
        self.raw_content = None
        self.content = None

        # notice
        self.notice_type = None

        # group_ban
        self.duration = None
        self.operator_id = None
        self.notice_sub_type = None

        # group_upload
        self.file_busid = None
        self.file_id = None
        self.file_name = None
        self.file_size = None

        self.__server.logger.debug(
            f'接收上报数据 {json.dumps(self.__data, indent=4, ensure_ascii=False)}'
        )

        # shutdown:
        if 'shutdown' in self.__data.keys() and self.__data['shutdown'] is True:
            self.__shutdown()
            return

        # global
        self.raw = self.__data
        self.time = self.__data['time']
        self.post_type = self.__data['post_type']
        if 'server' in self.__data.keys():
            self.server = self.__data['server']

        # message and notice
        if self.post_type == 'message':
            self.message_parse()
        elif self.post_type == 'notice':
            self.notice_parse()

    def message_parse(self):
        self.message_id = self.__data['message_id']
        self.user_id = self.__data['user_id']
        self.source_type = self.__data['message_type']
        self.source_sub_type = self.__data['sub_type']
        self.raw_content = self.__data['message']
        self.content_parse()
        if self.source_type == 'private':
            self.source_id = self.__data['user_id']
        elif self.source_type == 'group':
            self.source_id = self.__data['group_id']

        # call on_qq_info
        self.__server.dispatch_event(
            LiteralEvent('cool_q_api.on_qq_info'),
            (self, self.__bot)
        )
        # call on_qq_command
        if self.content.startswith(self.__config['command_prefix']):
            self.__server.dispatch_event(
                LiteralEvent('cool_q_api.on_qq_command'),
                (self, self.__bot)
            )

    def notice_parse(self):
        self.notice_type = self.__data['notice_type']
        # group_ban
        if self.notice_type == 'group_ban':
            self.source_type = 'group'
            self.source_id = self.__data['group_id']
            self.user_id = self.__data['user_id']
            self.duration = self.__data['duration']
            self.operator_id = self.__data['operator_id']
            self.notice_sub_type = self.__data['sub_type']

        # group_upload
        elif self.notice_type == 'group_upload':
            self.source_type = 'group'
            self.source_id = self.__data['group_id']
            self.user_id = self.__data['user_id']
            self.file_busid = self.__data['file']['busid']
            self.file_id = self.__data['file']['id']
            self.file_name = self.__data['file']['name']
            self.file_size = self.__data['file']['size']

        # group_increase
        elif self.notice_type == 'group_increase':
            self.source_type = 'group'
            self.source_id = self.__data['group_id']
            self.user_id = self.__data['user_id']
            self.operator_id = self.__data['operator_id']
            self.notice_sub_type = self.__data['sub_type']

        # group_decrease
        elif self.notice_type == 'group_decrease':
            self.source_type = 'group'
            self.source_id = self.__data['group_id']
            self.user_id = self.__data['user_id']
            self.operator_id = self.__data['operator_id']
            self.notice_sub_type = self.__data['sub_type']

        # call on_qq_notice
        self.__server.dispatch_event(
            LiteralEvent('cool_q_api.on_qq_notice'),
            (self, self.__bot,)
        )

    def content_parse(self):
        content = self.__data['raw_message']
        content = re.sub(r'\[CQ:image,file=.*?]', '[图片]', content)
        content = re.sub(r'\[CQ:share,file=.*?]', '[链接]', content)
        content = re.sub(r'\[CQ:face,id=.*?]', '[表情]', content)
        content = re.sub(r'\[CQ:record,file=.*?]', '[语音]', content)
        content = content.replace('CQ:at,qq=', '@')
        self.content = content

    @staticmethod
    def __shutdown():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError
        func()

    def __getitem__(self, item):
        return self.raw[item]
