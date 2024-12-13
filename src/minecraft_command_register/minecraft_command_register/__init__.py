import json
from enum import Enum

from mcdreforged.api.command import *
from mcdreforged.api.types import PluginServerInterface
from mcdreforged.mcdr_server import MCDReforgedServer
from mcdreforged.plugin.plugin_registry import PluginCommandHolder

mcdr_server: MCDReforgedServer


class NodeTypes(Enum):
    LITERAL = Literal
    NUMBER = Number
    INTEGER = Integer
    FLOAT = Float
    TEXT = Text
    QUOTABLE_TEXT = QuotableText
    GREEDY_TEXT = GreedyText
    BOOLEAN = Boolean
    ENUMERATION = Enumeration


class Node:
    def __init__(self, name: str, node: AbstractNode):
        self.name = name
        self.type = None
        self.children = []

        # get type
        try:
            self.type = NodeTypes(node.__class__)
        except ValueError:
            self.type = NodeTypes.TEXT

        # Literal children
        for literal, literal_children in node._children_literal.items():
            self.children.append(Node(literal, literal_children[0]))

        # Argument children
        for argument_child in node._children:
            self.children.append(
                Node(
                    argument_child._ArgumentNode__name,
                    argument_child
                )
            )

    @property
    def dict(self):
        return {
            'name': self.name,
            'type': self.type.name,
            'children': [i.dict for i in self.children]
        }


def read_registered_commands(server: PluginServerInterface):
    # return if server is not startup
    if not server.is_server_startup():
        return

    # get tree data
    root_nodes = mcdr_server.command_manager.root_nodes
    data = {'data': []}
    for key, value in root_nodes.items():
        plugin_command_holder: PluginCommandHolder = value[0]
        data['data'].append(Node(key, plugin_command_holder.node).dict)

    # return
    return data


def register(server: PluginServerInterface):
    data = read_registered_commands(server)
    server.logger.debug(
        f'Register commands to minecraft, tree:'
        f'\n{json.dumps(data, indent=4)}'
    )
    server.execute(f'mcdr register {json.dumps(data)}')


def on_load(server: PluginServerInterface, prev_module):
    global mcdr_server
    mcdr_server = server._mcdr_server

    # Call register when register command
    old_on_plugin_registry_changed = mcdr_server.on_plugin_registry_changed

    def new_on_plugin_registry_changed():
        server.logger.debug('on_plugin_registry_changed')
        old_on_plugin_registry_changed()
        register(server)

    mcdr_server.on_plugin_registry_changed = new_on_plugin_registry_changed


def on_server_startup(server: PluginServerInterface):
    register(server)
