from enum import Enum
from typing import Any, Callable, Dict, Iterable, List, Type, Union

from mcdreforged.api.command import *

from .exceptions import MissingRequiredAttribute
from .node_type import NodeType


class Node:
    def __init__(self, data: Dict[str, Any]):
        self.__data = data

        # name
        self.__name: str = data.get("name")
        if self.__name is None:
            raise MissingRequiredAttribute("name")

        # node
        self.__node: Union[Literal, ArgumentNode] = data.get("node")

        # literal
        self.__literal: Union[str, Iterable[str]] = data.get(
            "literal",
            self.__name
        )

        # type
        self.__type: Union[NodeType, Type[ArgumentNode]] = data.get(
            "type",
            NodeType.LITERAL
        )

        # enumeration
        self.__enumeration: Dict[str, Any] = data.get("enumeration", {})

        # args
        self.__args: List[Any] = data.get("args", [])

        # kwargs
        self.__kwargs: Dict[str, Any] = data.get("kwargs", {})

        # runs
        self.__runs: Callable = data.get("runs")

        # requires
        self.__requires: Union[Callable, List[Callable]] = data.get("requires")

        # redirects
        self.__redirects: AbstractNode = data.get("redirects")

        # suggests
        self.__suggests: Callable = data.get("suggests")

        # on_error
        self.__on_error: Dict[str, Any] = data.get("on_error")

        # on_child_error
        self.__on_child_error: Dict[str, Any] = data.get("on_child_error")

        # children
        self.__children: List[Node] = []
        for i in data.get("children", []):
            self.__children.append(Node(i))

    @property
    def literal(self) -> Union[str, Iterable[str]]:
        return self.__literal

    def to_mcdr_node(self) -> Union[Literal, ArgumentNode]:
        if self.__node is None:
            # instantiate node
            mcdr_node: Union[Literal, ArgumentNode]
            if type(self.__type) == NodeType:
                if self.__type == NodeType.LITERAL:
                    mcdr_node = self.__type.value(self.__literal)
                elif self.__type == NodeType.ENUMERATION:
                    mcdr_node = self.__type.value(
                        self.__name,
                        Enum(self.__name, self.__enumeration)
                    )
                else:
                    mcdr_node = self.__type.value(self.__name)
            else:
                mcdr_node = self.__type(
                    self.__name,
                    *self.__args,
                    **self.__kwargs
                )

            # runs
            if self.__runs is not None:
                mcdr_node.runs(self.__runs)

            # requires
            if self.__requires is not None:
                if isinstance(self.__requires, list):
                    for i in self.__requires:
                        mcdr_node.requires(i)
                elif isinstance(self.__requires, Callable):
                    mcdr_node.requires(self.__requires)
                else:
                    raise TypeError(
                        f"Error requires type: {type(self.__requires)}"
                    )

            # redirects
            if self.__redirects is not None:
                mcdr_node.redirects(self.__redirects)

            # suggests
            if self.__suggests is not None:
                mcdr_node.suggests(self.__suggests)

            # on_error
            if self.__on_error is not None:
                mcdr_node.on_error(
                    self.__on_error.get("error_type", CommandError),
                    self.__on_error.get("handler", lambda *args: None),
                    handled=self.__on_error.get("handled", False),
                )

            # on_child_error
            if self.__on_child_error is not None:
                mcdr_node.on_child_error(
                    self.__on_child_error.get("error_type", CommandError),
                    self.__on_child_error.get("handler", lambda *args: None),
                    handled=self.__on_child_error.get("handled", False),
                )

            # runs
            if self.__runs is not None:
                mcdr_node.runs(self.__runs)

            # add children
            for i in self.__children:
                mcdr_node.then(i.to_mcdr_node())

            # return
            return mcdr_node
        else:
            return self.__node
