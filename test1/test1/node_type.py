from enum import Enum

from mcdreforged.api.command import *


class NodeType(Enum):
    LITERAL = Literal
    NUMBER = Number
    INTEGER = Integer
    FLOAT = Float
    TEXT = Text
    QUOTABLE_TEXT = QuotableText
    GREEDY_TEXT = GreedyText
    BOOLEAN = Boolean
    ENUMERATION = Enumeration
