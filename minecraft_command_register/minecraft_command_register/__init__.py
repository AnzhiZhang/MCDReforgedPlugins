import json

from mcdreforged.api.types import PluginServerInterface
from mcdreforged.mcdr_server import MCDReforgedServer
from mcdreforged.plugin.plugin_registry import PluginCommandHolder

mcdr_server: MCDReforgedServer


class Node:
    def __init__(self, node):
        self.children = {}

        # Argument children
        for argument_child in node._children:
            child_name = f'<{argument_child._ArgumentNode__name}>'
            self.children[child_name] = Node(argument_child)

        # Literal children
        for key, literal_children in node._children_literal.items():
            self.children[key] = Node(literal_children[0])

    @property
    def dict(self):
        if self.children:
            return {key: value.dict for key, value in self.children.items()}
        else:
            return None


def register(server: PluginServerInterface):
    server.logger.debug('Register commands to minecraft')

    # return if server is not startup
    if not server.is_server_startup():
        return

    # get tree data
    root_nodes = mcdr_server.command_manager.root_nodes
    tree_data = {}
    for key, value in root_nodes.items():
        plugin_command_holder: PluginCommandHolder = value[0]
        tree_data[key] = Node(plugin_command_holder.node).dict

    # execute register command
    server.execute(f'mcdr register {json.dumps(tree_data)}')
    return tree_data


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
