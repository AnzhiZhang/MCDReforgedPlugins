import asyncio
import weakref
from time import time_ns
from typing import override, Optional

from fastapi import FastAPI, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from mcdreforged import PluginCommandSource, RTextBase, ServerInterface
from mcdreforged.api.types import PluginServerInterface
from mcdreforged.plugin.type.plugin import AbstractPlugin
from mcdreforged.utils import misc_utils
from mcdreforged.utils.string_utils import clean_minecraft_color_code
from mcdreforged.utils.types.message import MessageText
from pydantic import BaseModel

from .config import Config

app = FastAPI()
bearer_scheme = HTTPBearer()

__server: PluginServerInterface
__config: Config


class _ReplayHolder:
    def __init__(self):
        self.replays: list[str] = []
        self.done_event = asyncio.Event()


class FastAPICommandSource(PluginCommandSource):
    def __init__(self, server: 'ServerInterface', plugin: Optional['AbstractPlugin'] = None):
        self.holder = _ReplayHolder()
        self._finalize = weakref.finalize(self, self.holder.done_event.set)
        super().__init__(server, plugin)

    @override
    def reply(self, message: MessageText, **kwargs) -> None:
        if self.holder.done_event.is_set():
            self.get_server().logger.warning(
                f"the fallowing reply(id: {id(self.holder.replays)}) can't reach to http response: "
            )
            misc_utils.print_text_to_console(self.get_server().logger, message)
        self.holder.replays.append(clean_minecraft_color_code(
            message.to_plain_text() if isinstance(message, RTextBase) else message
        ))

    @staticmethod
    def from_server_interface(server: PluginServerInterface) -> 'FastAPICommandSource':
        return FastAPICommandSource(server, server.get_plugin_instance(server.get_self_metadata().id))


class ExecuteRequest(BaseModel):
    command: str
    timeout: int = 10_000


def verify_token(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    if credentials.credentials != __config.token:
        raise HTTPException(status_code=401, detail="Invalid token")
    return credentials.credentials


@app.post("/execute")
async def execute_command(
        request: ExecuteRequest,
        _token: str = Security(verify_token),
):
    time_before_execute = time_ns()
    source = FastAPICommandSource.from_server_interface(__server)
    holder = source.holder  # add references of holder
    __server.execute_command(request.command, source)
    del source  # remove source's references

    time_time_before_wait = time_ns()
    # In normal cases, the reference count of `source` at this line has already to 0.
    # But if the Command Callback passes `source` to another thread
    # or put outside of Command Callback scope
    # causing `source` not to be finalized, then the following waiting logic will be executed.
    try:
        await asyncio.wait_for(holder.done_event.wait(), timeout=request.timeout / 1000)
    except asyncio.TimeoutError:
        __server.logger.info(
            f"source.reply timeout, {len(holder.replays)} line(s) reply "
            f"will be response, reply_id: {id(holder.replays)}"
        )

    time_before_response = time_ns()
    __server.logger.debug(
        f"Total cost: {(time_before_response - time_before_execute)/1_000_000}ms, "
        f"command handler cost: {(time_time_before_wait - time_before_execute)/1_000_000}ms, "
        f"wait cost: {(time_before_response - time_time_before_wait)/1_000_000}ms."
    )

    return {
        "status": "ok",
        "command": request.command,
        "reply": {
            "id": id(holder.replays),
            "is_finished": holder.done_event.is_set(),
            "messages": holder.replays,
        }
    }


def on_load(server: PluginServerInterface, prev_module):
    # mount if fastapi_mcdr is ready
    global __server, __config
    __server = server
    __config = server.load_config_simple(target_class=Config)

    fastapi_mcdr = server.get_plugin_instance('fastapi_mcdr')
    if fastapi_mcdr is not None and fastapi_mcdr.is_ready():
        mount_app(server)

    server.register_event_listener(
        fastapi_mcdr.COLLECT_EVENT,
        mount_app
    )


def on_unload(server: PluginServerInterface):
    # save plugin id and fastapi_mcdr instance
    id_ = server.get_self_metadata().id
    fastapi_mcdr = server.get_plugin_instance('fastapi_mcdr')

    # unmount app
    fastapi_mcdr.unmount(id_)


def mount_app(server: PluginServerInterface):
    # save plugin id and fastapi_mcdr instance
    id_ = server.get_self_metadata().id
    fastapi_mcdr = server.get_plugin_instance('fastapi_mcdr')

    # mount app
    fastapi_mcdr.mount(id_, app)
