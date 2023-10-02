import time
from asyncio import AbstractEventLoop, new_event_loop
from enum import Enum
from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
    Sequence,
    Type,
    Union,
)

from uvicorn import Config, Server
from fastapi import FastAPI, Depends, routing
from fastapi.datastructures import Default, DefaultPlaceholder
from fastapi.types import IncEx
from fastapi.utils import generate_unique_id
from starlette.responses import Response, JSONResponse
from mcdreforged.api.event import LiteralEvent
from mcdreforged.api.decorator import new_thread
from mcdreforged.api.types import PluginServerInterface
from mcdreforged.utils.serializer import Serializable

__app: FastAPI
__is_ready: bool = False
__mcdr_server: PluginServerInterface
__uvicorn_server: Server
__event_loop: AbstractEventLoop

__all__ = [
    "is_ready",
    "add_api_route",
    "ACCEPT_EVENT",
]

ACCEPT_EVENT = LiteralEvent("fastapi_mcdr.accept")


class PluginConfig(Serializable):
    host: str = "0.0.0.0"
    port: int = 8080


@new_thread("FastAPI")
def fastapi_main_thread(host: str, port: int):
    global __app, __uvicorn_server, __event_loop
    # init app and event loop
    __app = FastAPI()
    __event_loop = new_event_loop()

    # init uvicorn server
    __uvicorn_server = Server(Config(
        __app,
        host=host,
        port=port,
        loop="none",
        log_level="critical"
    ))

    # dispatch event to allow other plugins to add api routes
    __mcdr_server.dispatch_event(ACCEPT_EVENT, ())

    # start uvicorn server
    __event_loop.run_until_complete(__uvicorn_server.serve())


def on_load(server: PluginServerInterface, old):
    global __is_ready, __mcdr_server

    # mcdr init
    __mcdr_server = server

    # load config
    config = server.load_config_simple(
        "config.json",
        target_class=PluginConfig
    )

    # start fastapi server
    fastapi_main_thread(config.host, config.port)
    __is_ready = True
    server.logger.info("Fast API started.")


def on_unload(server: PluginServerInterface):
    __mcdr_server.logger.info("Exiting FastAPI.")
    __uvicorn_server.should_exit = True
    time.sleep(0.1)


def is_ready() -> bool:
    return __is_ready


def add_api_route(
        plugin_id: str,
        path: str,
        endpoint: Callable[..., Coroutine[Any, Any, Response]],
        *,
        response_model: Any = Default(None),
        status_code: Optional[int] = None,
        tags: Optional[List[Union[str, Enum]]] = None,
        dependencies: Optional[Sequence[Depends]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        deprecated: Optional[bool] = None,
        methods: Optional[List[str]] = None,
        operation_id: Optional[str] = None,
        response_model_include: Optional[IncEx] = None,
        response_model_exclude: Optional[IncEx] = None,
        response_model_by_alias: bool = True,
        response_model_exclude_unset: bool = False,
        response_model_exclude_defaults: bool = False,
        response_model_exclude_none: bool = False,
        include_in_schema: bool = True,
        response_class: Union[Type[Response], DefaultPlaceholder] = Default(
            JSONResponse
        ),
        name: Optional[str] = None,
        openapi_extra: Optional[Dict[str, Any]] = None,
        generate_unique_id_function: Callable[
            [routing.APIRoute], str] = Default(
            generate_unique_id
        ),
):
    """
    Add a new api route to FastAPI.
    """

    # check if fastapi is ready
    if not __is_ready:
        raise RuntimeError("FastAPI is not ready yet.")

    # add route
    __app.add_api_route(
        path=f"/{plugin_id}{path}",
        endpoint=endpoint,
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses,
        deprecated=deprecated,
        methods=methods,
        operation_id=operation_id,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_exclude_unset=response_model_exclude_unset,
        response_model_exclude_defaults=response_model_exclude_defaults,
        response_model_exclude_none=response_model_exclude_none,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
        openapi_extra=openapi_extra,
        generate_unique_id_function=generate_unique_id_function,
    )

    # update schema
    __app.openapi_schema = None
    __app.setup()

    # log
    __mcdr_server.logger.debug(
        f'Plugin "{plugin_id}" added a new api route '
        f'"/{plugin_id}{path}" with '
        f"methods={methods}"
    )


def delete_routes(plugin_id: str):
    # delete routes
    for i, route in enumerate(__app.routes):
        if route.path.startswith(f"/{plugin_id}"):
            del __app.routes[i]
            __mcdr_server.logger.debug(
                f'Plugin "{plugin_id}" deleted a api route '
                f'"{route.path}" with '
                f"methods={route.methods}"
            )

    # update schema
    __app.openapi_schema = None
    __app.setup()
