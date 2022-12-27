from mcdreforged.api.command import *
from mcdreforged.api.types import PluginServerInterface
from mcdreforged.permission.permission_level import PermissionLevel
from mcdreforged.plugin.builtin.mcdreforged_plugin.mcdreforged_plugin import \
    MCDReforgedPlugin


def on_load(server: PluginServerInterface, prev_module):
    mcdr_plugin = MCDReforgedPlugin(server._mcdr_server.plugin_manager)
    server.register_command(
        Literal('!!mcdr')
        .requires(lambda src: src.has_permission(PermissionLevel.USER))
        .runs(mcdr_plugin.process_mcdr_command)
        .on_error(
            RequirementNotMet,
            mcdr_plugin.on_mcdr_command_permission_denied,
            handled=True
        )
        .on_child_error(
            RequirementNotMet,
            mcdr_plugin.on_mcdr_command_permission_denied,
            handled=True
        )
        .on_error(
            UnknownArgument,
            mcdr_plugin.on_mcdr_command_unknown_argument,
            handled=True
        )
        .then(mcdr_plugin.command_status.get_command_node())
        .then(mcdr_plugin.command_reload.get_command_node())
        .then(mcdr_plugin.command_permission.get_command_node())
        .then(mcdr_plugin.command_plugin.get_command_node())
        .then(mcdr_plugin.command_check_update.get_command_node())
        .then(mcdr_plugin.command_preference.get_command_node())
    )
