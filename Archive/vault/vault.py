# -*- coding: utf-8 -*
import os
import time
import uuid
from decimal import Decimal
from typing import Dict, List, Any

from sqlalchemy import Column, Text, Integer, CheckConstraint

from plugins.DatabaseAPI import TableBase, DataManager

PLUGIN_METADATA = {
    'id': 'vault',
    'version': '0.0.1',
    'name': 'vault',
    'description': 'vault',
    'author': 'zhang_anzhi',
    'link': 'https://github.com/AnzhiZhang/MCDReforgedPlugins/tree/master/Archive/vault',
    'dependencies': {
        'database_api': '*'
    }
}


class Data(TableBase):
    __tablename__ = 'data'
    name = Column(Text, primary_key=True, nullable=False)
    create_at = Column(Integer, nullable=False)
    update_at = Column(Integer, nullable=False)
    balance = Column(Text, CheckConstraint('balance>=0'), nullable=False)


class Log(TableBase):
    __tablename__ = 'log'
    id = Column(Text, primary_key=True, nullable=False)
    create_at = Column(Integer, nullable=False)
    debit = Column(Text, nullable=False)
    credit = Column(Text, nullable=False)
    amount = Column(Text, nullable=False)


class AccountNotExistsError(Exception):
    def __init__(self, username: str = None):
        if username is not None:
            super().__init__(f'User "{username}" not exists')
        else:
            super().__init__()


class AmountIllegalError(Exception):
    def __init__(self, amount: Decimal = None):
        if amount is not None:
            super().__init__(f'Amount "{amount}" is illegal')
        else:
            super().__init__()


class InsufficientBalanceError(Exception):
    def __init__(self):
        super().__init__(f'Balance is insufficient')


class Vault:
    AccountNotExistsError = AccountNotExistsError
    AmountIllegalError = AmountIllegalError
    InsufficientBalanceError = InsufficientBalanceError

    def __init__(self):
        dir_ = os.path.join('config', PLUGIN_METADATA['name'])
        if not os.path.exists(dir_):
            os.makedirs(dir_)
        path = os.path.join(dir_, 'data.db')
        self.__data_manager = DataManager(path)

    # ----
    # Data
    # ----

    def __get_all_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all data.
        :return: Dict, name: Dict
        """
        with self.__data_manager.get_session() as session:
            return {
                data.name: {
                    'create_at': data.create_at,
                    'update_at': data.update_at,
                    'balance': Decimal(data.balance)
                }
                for data in session.query(Data).all()
            }

    def __get_balance(self, name: str) -> Decimal:
        """
        Get account balance.
        :param name: Account name.
        :return: Decimal, balance.
        """
        return self.__get_all_data()[name]['balance']

    def __get_open_time(self, name: str) -> int:
        """
        Get account open time.
        :param name: Account name.
        :return: int, open timestamp.
        """
        return self.__get_all_data()[name]['create_at']

    def __get_log(self) -> List[Dict[str, Any]]:
        """
        Get all log.
        :return: Log dict list.
        """
        with self.__data_manager.get_session() as session:
            return [
                {
                    'id': log.id,
                    'create_at': log.create_at,
                    'debit': log.debit,
                    'credit': log.credit,
                    'amount': log.amount
                }
                for log in session.query(Log).all()
            ]

    def __set_balance(self, name: str, balance: Decimal) -> None:
        """
        Set a account's balance.
        :param name: Account name.
        :param balance: New balance.
        :return: None
        """
        with self.__data_manager.get_session() as session:
            (
                session.query(Data)
                    .filter_by(name=name)
                    .update(
                    {
                        'balance': str(balance),
                        'update_at': int(time.time())
                    }
                )
            )

    def __log(self, debit: str, credit: str, amount: Decimal) -> None:
        """
        Create a new transfer log.
        :param debit: Debit, the source of capital.
        :param credit: Credit, the went of capital.
        :param amount: Amount of capital.
        :return: None
        """
        with self.__data_manager.get_session() as session:
            log = Log(
                id=str(uuid.uuid4()),
                create_at=int(time.time()),
                debit=debit,
                credit=credit,
                amount=str(amount)
            )
            session.add(log)

    # ---
    # API
    # ---

    def is_account(self, name) -> bool:
        """
        Check the account is exists.
        :param name: Account name.
        :return: Account is exists or not.
        """
        return name in self.__get_all_data().keys()

    def create_account(self, name: str) -> None:
        """
        Create new account that balance is 0.0 for a player.
        :param name: The name of player.
        """
        if not self.is_account(name):
            with self.__data_manager.get_session() as session:
                time_ = int(time.time())
                session.add(
                    Data(
                        name=name,
                        create_at=time_,
                        update_at=time_,
                        balance='0.00'
                    )
                )

    def get_open_time(self, name: str) -> int:
        """
        Get account open time.
        :param name: Account name.
        :return: int, open timestamp.
        :raise AccountNotExistsError when account is not exists.
        """
        if self.is_account(name):
            return self.__get_open_time(name)
        else:
            raise AccountNotExistsError(name)

    def get_balance(self, name: str) -> Decimal:
        """
        Get account balance.
        :param name: Account name.
        :return: Decimal, balance.
        :raise AccountNotExistsError when account is not exists.
        """
        if self.is_account(name):
            return self.__get_balance(name)
        else:
            raise AccountNotExistsError(name)

    def get_logs(self) -> List[Dict[str, Any]]:
        """
        Get all logs
        :return: A list includes all logs.
        Each log tuple format: (id, time, debit, credit, amount)
        """
        return self.__get_log()

    def get_ranking(self) -> Dict[str, Decimal]:
        """
        Get a amount ranking dict.
        :return: Dict, example: {'a': Decimal('1.5'), 'b': Decimal('1.4')}
        """
        data = {a: b['balance'] for a, b in self.__get_all_data().items()}
        return dict(sorted(data.items(), key=lambda d: d[1], reverse=True))

    def give(self, name: str, amount: Decimal, operator: str = 'Admin') -> None:
        """
        Give a account some money.
        :param name: Account name.
        :param amount: Amount.
        :param operator: The operator will show at 'debit' in logs.
        :return: None
        :raise AccountNotExistsError when account is not exists.
        :raise AmountIllegalError when amount less or equal 0.
        """
        if self.is_account(name):
            if amount <= 0:
                raise AmountIllegalError(amount)
            else:
                balance_old = self.__get_balance(name)
                balance_new = balance_old + amount
                self.__set_balance(name, balance_new)
                self.__log(operator, name, amount)
        else:
            raise AccountNotExistsError(name)

    def take(self, name: str, amount: Decimal, operator: str = 'Admin') -> None:
        """
        Take a account some money.
        :param name: Account name.
        :param amount: Amount.
        :param operator: The operator will show at 'debit' in logs.
        :return: None
        :raise AccountNotExistsError when account is not exists.
        :raise AmountIllegalError when amount less or equal 0.
        :raise InsufficientBalanceError when debit's balance is insufficient.
        """
        if self.is_account(name):
            if amount <= 0:
                raise AmountIllegalError(amount)
            elif amount > self.__get_balance(name):
                raise InsufficientBalanceError()
            else:
                balance_old = self.__get_balance(name)
                balance_new = balance_old - amount
                self.__set_balance(name, balance_new)
                self.__log(operator, name, -amount)
        else:
            raise AccountNotExistsError(name)

    def set(self, name: str, amount: Decimal, operator: str = 'Admin') -> None:
        """
        Set a account's balance.
        :param name: Account name.
        :param amount: Amount.
        :param operator: The operator will show at 'debit' in logs.
        :return: None
        :raise AccountNotExistsError when account is not exists.
        :raise AmountIllegalError when amount less 0.
        """
        if self.is_account(name):
            if amount < 0:
                raise AmountIllegalError(amount)
            else:
                balance_old = self.__get_balance(name)
                self.__set_balance(name, amount)
                self.__log(operator, name, amount - balance_old)
        else:
            raise AccountNotExistsError(name)

    def transfer(self, debit: str, credit: str, amount: Decimal) -> None:
        """
        Transfer amount between two account.
        :param debit: Debit, the source of capital.
        :param credit: Credit, the went of capital.
        :param amount: Amount of capital.
        :return: None
        :raise AccountNotExistsError when account is not exists.
        :raise AmountIllegalError when amount is 0.
        :raise InsufficientBalanceError when debit's balance is insufficient.
        """
        if self.is_account(debit) and self.is_account(credit):
            if amount <= 0:
                raise AmountIllegalError(amount)
            elif amount > self.__get_balance(debit):
                raise InsufficientBalanceError()
            else:
                debit_old = self.get_balance(debit)
                credit_old = self.get_balance(credit)
                debit_new = debit_old - amount
                credit_new = credit_old + amount
                self.__set_balance(debit, debit_new)
                self.__set_balance(credit, credit_new)
                self.__log(debit, credit, amount)
        else:
            raise AccountNotExistsError(f'{debit} or {credit}')


vault = Vault()
