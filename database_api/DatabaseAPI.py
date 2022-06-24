# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

__all__ = [
    'TableBase',
    'DataManager',
]
PLUGIN_METADATA = {
    'id': 'database_api',
    'version': '0.0.1',
    'name': 'DatabaseAPI',
    'description': 'Database API to access database',
    'author': 'Andy Zhang',
    'link': 'https://github.com/AnzhiZhang/MCDReforgedPlugins/tree/master/database_api'
}


def repr_(self):
    """Rewrite __repr__ function of Model Base"""
    r = self.__dict__.copy()
    r.pop('_sa_instance_state')
    return str(r)


TableBase = declarative_base()
TableBase.__repr__ = repr_


class GetSession:
    """
    A context manager to get Session.
    It will close the session after use.
    It will commit after use, and roll back if exception raises.
    """

    def __init__(self, data_manager: 'DataManager'):
        self.__data_manager = data_manager

    def __enter__(self) -> Session:
        self.__session = self.__data_manager.Session()
        return self.__session

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.__session.rollback()
        else:
            self.__session.commit()
        self.__session.close()


class DataManager:
    def __init__(self, file_path: str):
        self.__engine = create_engine(f'sqlite:///{file_path}')
        self.__Session = sessionmaker(self.__engine)
        TableBase.metadata.create_all(self.__engine)

    def get_session(self) -> GetSession:
        """
        Return a Context manager of get_session
        """
        return GetSession(self)

    @property
    def Session(self):
        return self.__Session
