# -*- coding: utf-8 -*-
import requests


class Bot:
    def __init__(self, factory):
        self.__factory = factory

    @property
    def __config(self):
        return self.__factory.config

    def reply(self, info, message: str):
        """auto reply"""
        if info.source_type == 'private':
            self.send_private_msg(info.source_id, message)
        elif info.source_type == 'group':
            self.send_group_msg(info.source_id, message)
        elif info.source_type == 'discuss':
            self.send_discuss_msg(info.source_id, message)

    def send_msg(self, message: str, **kwargs):
        """send msg"""
        data = {'message': message}
        for key, value in kwargs.items():
            if value is not None:
                data[key] = value
        if len(data) != 2:
            raise RuntimeError('Need a send message object id')
        return requests.post(
            f'http://{self.__config["api_host"]}:{self.__config["api_port"]}/send_msg',
            json=data)

    def send_private_msg(self, user_id: int, message: str):
        """send private msg"""
        data = {
            'user_id': user_id,
            'message': message
        }
        return requests.post(
            f'http://{self.__config["api_host"]}:{self.__config["api_port"]}/send_private_msg',
            json=data)

    def send_group_msg(self, group_id: int, message: str):
        """send group msg"""
        data = {
            'group_id': group_id,
            'message': message
        }
        return requests.post(
            f'http://{self.__config["api_host"]}:{self.__config["api_port"]}/send_group_msg',
            json=data)

    def send_discuss_msg(self, discuss_id: int, message: str):
        """send group msg"""
        data = {
            'discuss_id': discuss_id,
            'message': message
        }
        return requests.post(
            f'http://{self.__config["api_host"]}:{self.__config["api_port"]}/send_discuss_msg',
            json=data)

    def delete_msg(self, message_id: int):
        """delete msg"""
        data = {
            'message_id': message_id
        }
        return requests.post(
            f'http://{self.__config["api_host"]}:{self.__config["api_port"]}/delete_msg',
            json=data)

    def set_group_kick(self, group_id: int, user_id: int,
                       reject_add_request: bool = False):
        """set group kick"""
        data = {
            'group_id': group_id,
            'user_id': user_id,
            'reject_add_request': reject_add_request
        }
        return requests.post(
            f'http://{self.__config["api_host"]}:{self.__config["api_port"]}/set_group_kick',
            json=data)

    def set_group_ban(self, group_id: int, user_id: int, duration: int):
        """set group ban"""
        data = {
            'group_id': group_id,
            'user_id': user_id,
            'duration': duration
        }
        return requests.post(
            f'http://{self.__config["api_host"]}:{self.__config["api_port"]}/set_group_ban',
            json=data)

    def set_group_whole_ban(self, group_id: int, enable: bool):
        """set group whole ban"""
        data = {
            'group_id': group_id,
            'enable': enable
        }
        return requests.post(
            f'http://{self.__config["api_host"]}:{self.__config["api_port"]}/set_group_whole_ban',
            json=data)

    def set_group_card(self, group_id: int, user_id: int, card: str = ''):
        """set group card"""
        data = {
            'group_id': group_id,
            'user_id': user_id,
            'card': card
        }
        return requests.post(
            f'http://{self.__config["api_host"]}:{self.__config["api_port"]}/set_group_card',
            json=data)

    def set_group_special_title(self, group_id: int, user_id: int,
                                special_title: str = '', duration: int = -1):
        """set group special title"""
        data = {
            'group_id': group_id,
            'user_id': user_id,
            'special_title': special_title,
            'duration': duration
        }
        return requests.post(
            f'http://{self.__config["api_host"]}:{self.__config["api_port"]}/set_group_special_title',
            json=data)

    def set_friend_add_request(self, flag: str, approve: bool,
                               remark: str = ''):
        """set friend add request"""
        data = {
            'flag': flag,
            'approve': approve,
            'remark': remark
        }
        return requests.post(
            f'http://{self.__config["api_host"]}:{self.__config["api_port"]}/set_friend_add_request',
            json=data)

    def set_group_add_request(self, flag: str, type: str, approve: bool = True,
                              reason: str = ''):
        """set group add request"""
        data = {
            'flag': flag,
            'type': type,
            'approve': approve,
            'reason': reason
        }
        return requests.post(
            f'http://{self.__config["api_host"]}:{self.__config["api_port"]}/set_group_add_request',
            json=data)

    def get_login_info(self):
        """get login info"""
        return requests.post(
            f'http://{self.__config["api_host"]}:{self.__config["api_port"]}/get_login_info')

    def get_friend_list(self):
        """get friend list"""
        return requests.post(
            f'http://{self.__config["api_host"]}:{self.__config["api_port"]}/get_friend_list')

    def get_group_list(self):
        """get group list"""
        return requests.post(
            f'http://{self.__config["api_host"]}:{self.__config["api_port"]}/get_group_list')

    def get_group_info(self, group_id: int):
        """get group info"""
        data = {
            'group_id': group_id
        }
        return requests.post(
            f'http://{self.__config["api_host"]}:{self.__config["api_port"]}/get_group_info',
            json=data)

    def get_group_member_list(self, group_id: int):
        """get group member list"""
        data = {
            'group_id': group_id
        }
        return requests.post(
            f'http://{self.__config["api_host"]}:{self.__config["api_port"]}/get_group_member_list',
            json=data)

    def get_group_member_info(self, group_id: int, user_id: int):
        """get group member info"""
        data = {
            'group_id': group_id,
            'user_id': user_id
        }
        return requests.post(
            f'http://{self.__config["api_host"]}:{self.__config["api_port"]}/get_group_member_info',
            json=data)
