__all__ = [
    'IllegalDimensionException',
    'IllegalListIndexException',
    'IllegalActionIndexException',
    'BotAlreadyExistsException',
    'BotNotExistsException',
    'BotOnlineException',
    'BotOfflineException',
    'BotAlreadySavedException',
    'BotNotSavedException',
]


class IllegalDimensionException(Exception):
    def __init__(self, dimension: str):
        super().__init__(f'Dimension {dimension} is illegal')
        self.dimension = dimension


class IllegalListIndexException(IndexError):
    def __init__(self, index: int):
        super().__init__(f'List index {index} out of range')
        self.index = index


class IllegalActionIndexException(IndexError):
    def __init__(self, index: int):
        super().__init__(f'Action index {index} out of range')
        self.index = index


class BotException(Exception):
    def __init__(self, msg: str, name: str):
        super().__init__(msg)
        self.__name = name

    @property
    def name(self):
        return self.__name


class BotAlreadyExistsException(BotException):
    def __init__(self, name: str):
        super().__init__(f'Bot {name} is already exists!', name)


class BotNotExistsException(BotException):
    def __init__(self, name: str):
        super().__init__(f'Bot {name} is not exists!', name)


class BotOnlineException(BotException):
    def __init__(self, name: str):
        super().__init__(f'Bot {name} is online!', name)


class BotOfflineException(BotException):
    def __init__(self, name: str):
        super().__init__(f'Bot {name} is offline!', name)


class BotAlreadySavedException(BotException):
    def __init__(self, name: str):
        super().__init__(f'Bot {name} is already saved!', name)


class BotNotSavedException(BotException):
    def __init__(self, name: str):
        super().__init__(f'Bot {name} is not saved!', name)
