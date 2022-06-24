# -*- coding: utf-8 -*-
from typing import Dict

PLUGIN_METADATA = {
    'id': 'language_api',
    'version': '0.0.1',
    'name': 'LanguageAPI',
    'description': 'Language API',
    'author': 'Andy Zhang',
    'link': 'https://github.com/AnzhiZhang/MCDReforgedPlugins/tree/master/.archived/LanguageAPI'
}


class LanguageNotExistError(Exception):
    def __init__(self, language: str = None):
        if language is not None:
            super().__init__(f'Language "{language}" not exists')
        else:
            super().__init__()


class MessageNotFindError(Exception):
    def __init__(self, msg_id: str = None):
        if msg_id is not None:
            super().__init__(f'Cannot find message for msg_id "{msg_id}"')
        else:
            super().__init__()


class Language:
    def __init__(self, language_data: Dict[str, Dict[str, str]],
                 language: str = None):
        self.data = language_data
        self.language = (
            list(self.data.keys())[0]
            if language is None else language
        )

    def set_language(self, language: str) -> None:
        """
        Set current language.
        :param language: Language.
        :return: None.
        """
        self.language = language

    def get_msg_str(self, msg_id: str, language: str = None) -> str:
        """
        Get a message str for message id.
        :param msg_id: Message id.
        :param language: Language.
        :return: Message str.
        """
        if language is None:
            language = self.language
        msg_dict = self.data.get(language)
        if msg_dict is None:
            raise LanguageNotExistError(language)
        msg_str = msg_dict.get(msg_id)
        if msg_str is None:
            raise MessageNotFindError(msg_id)
        return msg_str

    def __getitem__(self, msg_id: str) -> str:
        """
        A easy way to get message str.
        :param msg_id: Message id.
        :return: Message str.
        """
        return self.get_msg_str(msg_id)
