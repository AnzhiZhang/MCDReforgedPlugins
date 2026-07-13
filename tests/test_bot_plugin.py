import pathlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch


REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / 'src' / 'bot'))
sys.path.insert(0, str(REPOSITORY_ROOT / 'src' / 'more_command_nodes'))


# The plugin imports MinecraftDataAPI at package import time, but none of these
# unit tests query a live Minecraft server.  A module stub keeps the tests
# independent from optional MCDR plugins installed in the test environment.
sys.modules.setdefault('minecraft_data_api', types.ModuleType('minecraft_data_api'))


# Importing an MCDR entry point normally registers decorated event listeners
# against the running server.  There is intentionally no running MCDR server
# in this unit-test process, so make both decorators synchronous no-ops while
# importing the production modules.
import mcdreforged.api.decorator as mcdr_decorator


def _synchronous_new_thread(arg=None):
    def decorate(function):
        function.original = function
        return function

    return decorate(arg) if callable(arg) else decorate


def _inert_event_listener(_event, **_kwargs):
    return lambda function: function


_original_new_thread = mcdr_decorator.new_thread
_original_event_listener = mcdr_decorator.event_listener
mcdr_decorator.new_thread = _synchronous_new_thread
mcdr_decorator.event_listener = _inert_event_listener
try:
    from bot.bot import Bot
    from bot.bot_manager import BotManager
    from bot.command_handler import CommandHandler
    from bot.event_handler import CARPET_LOCAL_LOGIN, EventHandler
    import bot.event_handler as event_handler_module
    from bot.exceptions import BotOnlineException
    from bot.location import Location
finally:
    mcdr_decorator.new_thread = _original_new_thread
    mcdr_decorator.event_listener = _original_event_listener


from mcdreforged.api.types import CommandSource


DEFAULT_PERMISSIONS = {
    'list': 1,
    'spawn': 1,
    'kill': 1,
    'action': 1,
    'tags': 1,
    'info': 1,
    'save': 2,
    'del': 2,
    'config': 2,
}


class FakeLogger:
    def __init__(self):
        self.warning_calls = []
        self.debug_calls = []

    def warning(self, *args, **kwargs):
        self.warning_calls.append((args, kwargs))

    def debug(self, *args, **kwargs):
        self.debug_calls.append((args, kwargs))


class FakeServer:
    def __init__(self):
        self.executed = []
        self.logger = FakeLogger()
        self.command_root = None
        self.help_messages = []
        self.say_messages = []

    def execute(self, command):
        self.executed.append(command)

    def register_command(self, root):
        self.command_root = root

    def register_help_message(self, *args, **kwargs):
        self.help_messages.append((args, kwargs))

    def rtr(self, key, *args):
        return (key, args)

    def say(self, message):
        self.say_messages.append(message)


class FakePlugin:
    def __init__(
            self,
            *,
            force_gamemode=False,
            gamemode='survival',
            spawn_timeout=30.0,
            post_join_delay=0,
    ):
        self.server = FakeServer()
        self.config = SimpleNamespace(
            force_gamemode=force_gamemode,
            gamemode=gamemode,
            spawn_timeout=spawn_timeout,
            post_join_delay=post_join_delay,
            permissions=dict(DEFAULT_PERMISSIONS),
            name_prefix='bot_',
            name_suffix='',
        )
        self.bot_manager = SimpleNamespace(save_data=Mock())
        self.get_location = Mock()

    @staticmethod
    def parse_name(name):
        return name.lower()


def make_bot(plugin, *, name='bot_alex', auto_update=False, actions=None):
    return Bot(
        plugin,
        name,
        Location([1.0, 64.0, -2.5], [90.0, 10.0], 0),
        '',
        [] if actions is None else actions,
        [],
        False,
        False,
        auto_update,
    )


class ImmediateCallbackInvoker:
    """Minimal ScheduledCallback invoker used after MCDR parses a command."""

    @staticmethod
    def invoke_sync(callback, args):
        return callback(*args)

    @staticmethod
    def invoke_async(callback, args):
        raise AssertionError(f'Unexpected async command callback: {callback!r}')


class FakeCommandSource(CommandSource):
    def __init__(self, server, permission_level=4):
        self._server = server
        self._permission_level = permission_level
        self.replies = []

    def get_server(self):
        return self._server

    def get_permission_level(self):
        return self._permission_level

    def reply(self, message, **kwargs):
        self.replies.append((message, kwargs))


class SpawnCommandTests(unittest.TestCase):
    def test_saved_bot_spawn_includes_configured_gamemode(self):
        plugin = FakePlugin(gamemode='survival', force_gamemode=False)
        bot = make_bot(plugin)
        bot.set_saved(True)

        bot.spawn()

        self.assertEqual(
            [
                'player bot_alex spawn at 1.0 64.0 -2.5 '
                'facing 90.0 10.0 in minecraft:overworld in survival'
            ],
            plugin.server.executed,
        )

    def test_unsaved_bot_preserves_carpet_default_when_not_forced(self):
        plugin = FakePlugin(gamemode='survival', force_gamemode=False)
        bot = make_bot(plugin)

        bot.spawn()

        self.assertEqual(
            [
                'player bot_alex spawn at 1.0 64.0 -2.5 '
                'facing 90.0 10.0 in minecraft:overworld'
            ],
            plugin.server.executed,
        )

    def test_force_gamemode_applies_to_unsaved_bot(self):
        plugin = FakePlugin(gamemode='adventure', force_gamemode=True)
        bot = make_bot(plugin)

        bot.spawn()

        self.assertEqual(
            [
                'player bot_alex spawn at 1.0 64.0 -2.5 '
                'facing 90.0 10.0 in minecraft:overworld in adventure'
            ],
            plugin.server.executed,
        )


class PendingSpawnTests(unittest.TestCase):
    def test_pending_spawn_rejects_duplicate_request(self):
        plugin = FakePlugin(spawn_timeout=30.0)
        bot = make_bot(plugin)

        with patch('bot.bot.time.monotonic', side_effect=[100.0, 101.0]):
            bot.spawn()
            with self.assertRaises(BotOnlineException):
                bot.spawn()

        self.assertEqual(1, len(plugin.server.executed))

    def test_pending_spawn_expires_and_allows_retry(self):
        plugin = FakePlugin(spawn_timeout=5.0)
        bot = make_bot(plugin)

        with patch(
                'bot.bot.time.monotonic',
                side_effect=[100.0, 106.0, 107.0]
        ):
            bot.spawn()
            self.assertFalse(bot.spawning)
            bot.spawn()

        self.assertEqual(2, len(plugin.server.executed))
        self.assertEqual(1, len(plugin.server.logger.warning_calls))
        self.assertIn(
            'Timed out waiting for bot "bot_alex" to join',
            plugin.server.logger.warning_calls[0][0][0],
        )


class CommandParsingTests(unittest.TestCase):
    def setUp(self):
        self.plugin = FakePlugin()
        self.plugin.bot_manager = SimpleNamespace(
            bots={},
            action=Mock(),
            direct_action=Mock(),
        )
        CommandHandler(self.plugin)
        self.root = self.plugin.server.command_root
        self.source = FakeCommandSource(self.plugin.server)

    def execute(self, command):
        executions = self.root._entry_execute(self.source, command)
        # MCDR 2.12 executes callbacks inline; newer releases return a list of
        # scheduled executions.  Exercise the real parser in either form.
        if executions is None:
            return None
        self.assertEqual(1, len(executions))
        return executions[0].scheduled_callback.invoke(
            ImmediateCallbackInvoker()
        )

    def test_direct_carpet_action_is_parsed_as_action_text(self):
        self.execute('!!bot action bot_alex use once')

        self.plugin.bot_manager.direct_action.assert_called_once_with(
            'bot_alex', 'use once'
        )
        self.plugin.bot_manager.action.assert_not_called()

    def test_legacy_numeric_index_still_uses_saved_action_path(self):
        self.execute('!!bot action bot_alex 2')

        self.plugin.bot_manager.action.assert_called_once_with('bot_alex', 2)
        self.plugin.bot_manager.direct_action.assert_not_called()


class EventBotManager:
    def __init__(self, plugin):
        self.plugin = plugin
        self.bots = {}

    def is_in_list(self, name):
        return name in self.bots

    def get_bot(self, name):
        return self.bots[name]

    def new_bot(self, name, location):
        bot = Bot(
            self.plugin,
            name,
            location,
            '',
            [],
            [],
            False,
            False,
            False,
        )
        self.bots[name] = bot
        return bot

    def update_list(self):
        return None

    def save_data(self):
        return None


class LocalLoginRecognitionTests(unittest.TestCase):
    def setUp(self):
        self.plugin = FakePlugin()
        self.plugin.bot_manager = EventBotManager(self.plugin)
        self.plugin.get_location.return_value = Location(
            [0.0, 64.0, 0.0], [0.0, 0.0], 0
        )
        event_handler_module.plugin = self.plugin

    def recognize(self, player, address):
        content = (
            f'{player}[{address}] logged in with entity id 42 '
            'at (0.0, 64.0, 0.0)'
        )
        EventHandler.on_player_joined(
            self.plugin.server,
            player,
            SimpleNamespace(content=content),
        )
        return self.plugin.bot_manager.get_bot(player.lower())

    def test_plain_local_login_is_recognized(self):
        self.assertIsNotNone(CARPET_LOCAL_LOGIN.search(
            'bot_plain[local] logged in with entity id 42 '
            'at (0.0, 64.0, 0.0)'
        ))

        bot = self.recognize('bot_plain', 'local')

        self.assertTrue(bot.online)
        self.assertEqual('bot_plain', bot.mc_name)

    def test_local_entity_address_login_is_recognized(self):
        self.assertIsNotNone(CARPET_LOCAL_LOGIN.search(
            'bot_entity[local:E:1234] logged in with entity id 42 '
            'at (0.0, 64.0, 0.0)'
        ))

        bot = self.recognize('bot_entity', 'local:E:1234')

        self.assertTrue(bot.online)
        self.assertEqual('bot_entity', bot.mc_name)

    def test_pending_spawn_does_not_consume_normalized_name_collision(self):
        self.plugin.parse_name = lambda player: (
            player.lower()
            if player.lower().startswith('bot_')
            else f'bot_{player.lower()}'
        )
        bot = make_bot(self.plugin, name='bot_alex')
        self.plugin.bot_manager.bots[bot.name] = bot
        bot.spawn()

        EventHandler.on_player_joined(
            self.plugin.server,
            'alex',
            SimpleNamespace(content=(
                'alex[local] logged in with entity id 42 '
                'at (0.0, 64.0, 0.0)'
            )),
        )

        self.assertTrue(bot.spawning)
        self.assertFalse(bot.online)
        self.assertEqual(1, len(self.plugin.server.executed))
        self.assertIn(
            'Ignored local player "alex"',
            self.plugin.server.logger.warning_calls[-1][0][0],
        )

    def test_pending_spawn_requires_local_login_marker(self):
        bot = make_bot(self.plugin, name='bot_alex')
        self.plugin.bot_manager.bots[bot.name] = bot
        bot.spawn()

        EventHandler.on_player_joined(
            self.plugin.server,
            'bot_alex',
            SimpleNamespace(content=(
                'bot_alex[/127.0.0.1:25565] logged in with entity id 42 '
                'at (0.0, 64.0, 0.0)'
            )),
        )

        self.assertTrue(bot.spawning)
        self.assertFalse(bot.online)

    def test_exact_local_join_completes_pending_spawn(self):
        bot = make_bot(self.plugin, name='bot_alex')
        self.plugin.bot_manager.bots[bot.name] = bot
        bot.spawn()

        EventHandler.on_player_joined(
            self.plugin.server,
            'Bot_Alex',
            SimpleNamespace(content=(
                'Bot_Alex[local:E:1234] logged in with entity id 42 '
                'at (0.0, 64.0, 0.0)'
            )),
        )

        self.assertTrue(bot.online)
        self.assertFalse(bot.spawning)
        self.assertEqual('Bot_Alex', bot.mc_name)


class AutoUpdateKillTests(unittest.TestCase):
    def test_location_query_failure_does_not_prevent_carpet_kill(self):
        plugin = FakePlugin()
        plugin.get_location.side_effect = TimeoutError('query timed out')
        bot = make_bot(plugin, auto_update=True)
        original_location = bot.location
        bot.restore_runtime_state('Bot_Alex', online=True)

        bot.kill()

        self.assertEqual(['player Bot_Alex kill'], plugin.server.executed)
        self.assertFalse(bot.online)
        self.assertIs(original_location, bot.location)
        plugin.bot_manager.save_data.assert_not_called()
        self.assertEqual(1, len(plugin.server.logger.warning_calls))
        self.assertTrue(
            plugin.server.logger.warning_calls[0][1].get('exc_info')
        )

    def test_kill_command_failure_keeps_online_state(self):
        plugin = FakePlugin()
        plugin.server.execute = Mock(side_effect=RuntimeError('kill failed'))
        bot = make_bot(plugin)
        bot.restore_runtime_state('Bot_Alex', online=True)

        with self.assertRaisesRegex(RuntimeError, 'kill failed'):
            bot.kill()

        self.assertTrue(bot.online)

    def test_save_failure_restores_location_and_still_kills(self):
        plugin = FakePlugin()
        plugin.get_location.return_value = Location(
            [10.0, 80.0, 20.0], [0.0, 0.0], 0
        )
        plugin.bot_manager.save_data.side_effect = OSError('disk full')
        bot = make_bot(plugin, auto_update=True)
        original_location = bot.location
        bot.restore_runtime_state('Bot_Alex', online=True)

        bot.kill()

        self.assertIs(original_location, bot.location)
        self.assertEqual(['player Bot_Alex kill'], plugin.server.executed)
        self.assertFalse(bot.online)


class ReloadServer(FakeServer):
    def __init__(self, saved_bots=None):
        super().__init__()
        self.saved_bots = [] if saved_bots is None else saved_bots
        self.saved_data_loaded = False

    def load_config_simple(self, file_name, **_kwargs):
        if file_name == 'botList.json':
            self.saved_data_loaded = True
            return {'botList': self.saved_bots}
        return {'botList': []}


class HotReloadTests(unittest.TestCase):
    @staticmethod
    def make_previous(bot):
        old_manager = SimpleNamespace(bots={bot.name: bot})
        return SimpleNamespace(
            plugin=SimpleNamespace(bot_manager=old_manager)
        )

    @staticmethod
    def make_new_plugin(players, saved_bots=None):
        plugin = FakePlugin()
        plugin.server = ReloadServer(saved_bots)
        result = (
            None
            if players is None
            else SimpleNamespace(players=players)
        )
        plugin.minecraft_data_api = SimpleNamespace(
            get_server_player_list=Mock(return_value=result)
        )
        return plugin

    def test_online_bot_is_recreated_with_new_plugin_reference(self):
        old_plugin = FakePlugin()
        old_bot = make_bot(old_plugin)
        old_bot.restore_runtime_state('Bot_Alex', online=True)
        new_plugin = self.make_new_plugin(['Bot_Alex'])

        manager = BotManager(new_plugin, self.make_previous(old_bot))
        restored = manager.get_bot('bot_alex')

        self.assertIsNot(restored, old_bot)
        self.assertTrue(restored.online)
        self.assertEqual('Bot_Alex', restored.mc_name)
        restored.run_action('jump once')
        self.assertEqual(
            ['player Bot_Alex jump once'],
            new_plugin.server.executed,
        )
        self.assertEqual([], old_plugin.server.executed)

    def test_real_player_name_does_not_mark_prefixed_bot_online(self):
        old_plugin = FakePlugin()
        old_bot = make_bot(old_plugin, name='bot_alice')
        old_bot.set_saved(True)
        new_plugin = self.make_new_plugin(
            ['Alice'],
            saved_bots=[old_bot.saving_data],
        )

        manager = BotManager(new_plugin, self.make_previous(old_bot))

        self.assertFalse(manager.get_bot('bot_alice').online)
        new_plugin.minecraft_data_api.get_server_player_list \
            .assert_not_called()

    def test_pending_snapshot_is_restored_without_player_list_query(self):
        old_plugin = FakePlugin()
        old_bot = make_bot(old_plugin)
        old_bot.set_spawning(True)
        new_plugin = self.make_new_plugin(None)

        manager = BotManager(new_plugin, self.make_previous(old_bot))

        restored = manager.get_bot('bot_alex')
        self.assertTrue(restored.spawning)
        self.assertFalse(restored.online)
        new_plugin.minecraft_data_api.get_server_player_list \
            .assert_not_called()

    def test_confirmed_online_state_is_restored_without_list_snapshot(self):
        old_plugin = FakePlugin()
        old_bot = make_bot(old_plugin)
        old_bot.restore_runtime_state('Bot_Alex', online=True)
        new_plugin = self.make_new_plugin([])

        manager = BotManager(new_plugin, self.make_previous(old_bot))

        self.assertTrue(manager.get_bot('bot_alex').online)
        new_plugin.minecraft_data_api.get_server_player_list \
            .assert_not_called()

    def test_persistent_data_is_loaded_without_player_list_query(self):
        saved_plugin = FakePlugin()
        saved_bot = make_bot(saved_plugin)
        saved_bot.set_saved(True)
        new_plugin = self.make_new_plugin(
            None,
            saved_bots=[saved_bot.saving_data],
        )

        manager = BotManager(new_plugin, self.make_previous(saved_bot))

        self.assertTrue(new_plugin.server.saved_data_loaded)
        self.assertTrue(manager.get_bot('bot_alex').saved)
        new_plugin.minecraft_data_api.get_server_player_list \
            .assert_not_called()


if __name__ == '__main__':
    unittest.main()
