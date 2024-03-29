from typing import TYPE_CHECKING, List, Dict

from fastapi import HTTPException
from pydantic import BaseModel, Field, conlist
from mcdreforged.api.types import PluginServerInterface

from bot.bot import Bot
from bot.exceptions import *
from bot.location import Location

if TYPE_CHECKING:
    from bot.plugin import Plugin


class LocationModel(BaseModel):
    position: conlist(float, min_length=3, max_length=3)
    facing: conlist(float, min_length=2, max_length=2) = [0.0, 0.0]
    dimension: int = Field(ge=-1, le=1)


class BotModel(BaseModel):
    name: str
    location: LocationModel
    comment: str
    actions: List[str]
    tags: List[str]
    auto_login: bool
    auto_run_actions: bool
    auto_update: bool
    online: bool
    saved: bool


class BaseBotRequest(BaseModel):
    location: LocationModel | None = None
    comment: str | None = None
    actions: List[str] | None = None
    tags: List[str] | None = None
    auto_login: bool | None = None
    auto_run_actions: bool | None = None
    auto_update: bool | None = None
    online: bool | None = None


class PostBotRequest(BaseBotRequest):
    name: str
    location: LocationModel


class PatchBotRequest(BaseBotRequest):
    pass


class FastAPIManager:
    def __init__(self, plugin: 'Plugin'):
        self.__plugin: 'Plugin' = plugin

        # check fast api ready
        if (
                self.__plugin.fastapi_mcdr is not None and
                self.__plugin.fastapi_mcdr.is_ready()
        ):
            self.__register_apis(self.__plugin.server)

        # register event listener
        self.__plugin.server.register_event_listener(
            "fastapi_mcdr.accept",
            self.__register_apis
        )

    @property
    def __logger(self):
        return self.__plugin.server.logger

    @property
    def __command_handler(self):
        return self.__plugin.command_handler

    @property
    def __bot_manager(self):
        return self.__plugin.bot_manager

    def __register_apis(self, server: PluginServerInterface):
        id_ = self.__plugin.server.get_self_metadata().id
        self.__plugin.fastapi_mcdr.add_api_route(
            id_,
            path="/bots",
            endpoint=self.__get_bots,
            response_model=Dict[str, BotModel],
            methods=["GET"],
        )
        self.__plugin.fastapi_mcdr.add_api_route(
            id_,
            path="/bots",
            endpoint=self.__post_bots,
            methods=["POST"],
        )
        self.__plugin.fastapi_mcdr.add_api_route(
            id_,
            path="/bots/{bot_name}",
            endpoint=self.__patch_bot,
            methods=["PATCH"],
        )
        self.__plugin.fastapi_mcdr.add_api_route(
            id_,
            path="/bots/{bot_name}",
            endpoint=self.__delete_bot,
            methods=["DELETE"],
        )

    def unload(self):
        if self.__plugin.fastapi_mcdr is not None:
            self.__plugin.fastapi_mcdr.delete_routes(
                self.__plugin.server.get_self_metadata().id
            )

    def __update_bot_data(self, bot: Bot, request: BaseBotRequest) -> None:
        # location
        if request.location is not None:
            bot.set_location(
                Location(
                    request.location.position,
                    request.location.facing,
                    request.location.dimension
                )
            )

        # comment
        if request.comment is not None:
            bot.set_comment(request.comment)

        # actions
        if request.actions is not None:
            bot.set_actions(request.actions)

        # auto login
        if request.auto_login is not None:
            bot.set_auto_login(request.auto_login)

        # auto run actions
        if request.auto_run_actions is not None:
            bot.set_auto_run_actions(request.auto_run_actions)

        # auto update
        if request.auto_update is not None:
            bot.set_auto_update(request.auto_update)

        # spawn or kill
        if request.online is not None:
            if request.online and bot.online:
                raise HTTPException(
                    status_code=400,
                    detail=f'Bot "{bot.name}" is already online.'
                )
            elif request.online and not bot.online:
                bot.spawn()
            elif not request.online and bot.online:
                bot.kill()
            elif not request.online and not bot.online:
                raise HTTPException(
                    status_code=400,
                    detail=f'Bot "{bot.name}" is not online.'
                )

        # save data
        self.__plugin.bot_manager.save_data()

    async def __get_bots(self) -> Dict[str, BotModel]:
        return self.__bot_manager.bots

    async def __post_bots(self, request: PostBotRequest) -> BotModel:
        # parse name
        name = self.__command_handler.parse_name(request.name)

        # create bot
        try:
            bot = self.__plugin.bot_manager.save(
                name,
                None,
                Location(
                    request.location.position,
                    request.location.facing,
                    request.location.dimension
                )
            )

            # update data
            self.__update_bot_data(bot, request)

            # log
            self.__logger.debug(
                f'Created "{name}" with PostBotRequest({request})'
            )

            # return
            return bot

        except BotAlreadySavedException:
            raise HTTPException(
                status_code=400,
                detail=f'Bot "{name}" is already saved.'
            )

    async def __patch_bot(
            self,
            bot_name: str,
            request: PatchBotRequest
    ) -> BotModel:
        # parse name
        name = self.__command_handler.parse_name(bot_name)

        # check request params
        if (
                request.location is None and
                request.comment is None and
                request.actions is None and
                request.auto_login is None and
                request.auto_run_actions is None and
                request.auto_update is None and
                request.online is None
        ):
            raise HTTPException(
                status_code=400,
                detail='No parameter is provided.'
            )

        # patch
        try:
            bot = self.__bot_manager.get_bot(name)

            # update data
            self.__update_bot_data(bot, request)

            # log
            self.__logger.debug(
                f'Patched "{name}" with PatchBotRequest({request})'
            )

            # return
            return bot
        except BotNotExistsException:
            raise HTTPException(
                status_code=400,
                detail=f'Bot "{name}" is not found.'
            )

    async def __delete_bot(self, bot_name: str) -> None:
        name = self.__command_handler.parse_name(bot_name)
        try:
            self.__bot_manager.delete(name)
            self.__logger.debug(f'Deleted "{name}"')
            return None
        except BotNotExistsException:
            raise HTTPException(
                status_code=400,
                detail=f'Bot "{name}" is not found.'
            )
        except BotNotSavedException:
            raise HTTPException(
                status_code=400,
                detail=f'Bot "{name}" is not saved.'
            )
