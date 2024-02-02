from typing import Any, Dict, Union

from mcdreforged.api.rtext import RTextBase
from mcdreforged.api.types import PluginServerInterface

from .exceptions import MissingRequiredAttribute
from .node_type import NodeType
from .node import Node

__all__ = [
    "MissingRequiredAttribute",
    "NodeType",
    "Node",
    "register",
]


def register(
        server: PluginServerInterface,
        command: Dict[str, Any],
        help_message: Union[
            str, RTextBase, Dict[str, Union[str, RTextBase]]
        ] = None,
        help_message_permission: int = 0
) -> None:
    """
    Register a command.
    See also: https://github.com/AnzhiZhang/MCDReforgedPlugins/blob/master/dict_command_registration/readme.md#register
    :param PluginServerInterface server: the PluginServerInterface instance of
        your plugin, to ensure that this command is registered by your plugin.
    :param dict command: Command, please find more information in the document.
    :param str help_message: Provide a string value if you want register
        help message for this command.
    :param int help_message_permission: The minimum permission level to see
        this help message. See also in MCDReforged document.
    :return: None.
    """
    # parse dict
    root_node = Node(command)
    server.logger.debug("Registering command tree:")
    root_node.to_mcdr_node().print_tree(server.logger.debug)

    # register command
    server.register_command(root_node.to_mcdr_node())

    # register help message
    if help_message is not None:
        # get literal
        if isinstance(root_node.literal, str):
            literal = root_node.literal
        else:
            literal = root_node.literal[0]

        # register
        server.register_help_message(
            literal,
            help_message,
            help_message_permission
        )
