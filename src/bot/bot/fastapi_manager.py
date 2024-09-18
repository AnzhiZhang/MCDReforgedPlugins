from typing import TYPE_CHECKING, List

from fastapi import FastAPI, HTTPException
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
    autoLogin: bool
    autoRunActions: bool
    autoUpdate: bool
    online: bool
    saved: bool


class BaseBotRequest(BaseModel):
    name: str | None = None
    location: LocationModel | None = None
    comment: str | None = None
    actions: List[str] | None = None
    tags: List[str] | None = None
    autoLogin: bool | None = None
    autoRunActions: bool | None = None
    autoUpdate: bool | None = None
    online: bool | None = None


class PostBotRequest(BaseBotRequest):
    name: str
    location: LocationModel


class PatchBotRequest(BaseBotRequest):
    pass


class BotsGetResponse(BaseModel):
    bots: List[BotModel]


def to_bot_model(bot: Bot) -> BotModel:
    return BotModel(
        name=bot.name,
        location=LocationModel(
            position=bot.location.position,
            facing=bot.location.facing,
            dimension=bot.location.dimension
        ),
        comment=bot.comment,
        actions=bot.actions,
        tags=bot.tags,
        autoLogin=bot.auto_login,
        autoRunActions=bot.auto_run_actions,
        autoUpdate=bot.auto_update,
        online=bot.online,
        saved=bot.saved
    )


class FastAPIManager:
    def __init__(self, plugin: 'Plugin'):
        self.__plugin: 'Plugin' = plugin

        # check fast api ready
        if (
                self.__plugin.fastapi_mcdr is not None and
                self.__plugin.fastapi_mcdr.is_ready()
        ):
            self.__mount_app(self.__plugin.server)

        # register event listener
        self.__plugin.server.register_event_listener(
            self.__plugin.fastapi_mcdr.COLLECT_EVENT,
            self.__mount_app
        )

    @property
    def __logger(self):
        return self.__plugin.server.logger

    @property
    def __bot_manager(self):
        return self.__plugin.bot_manager

    def __update_bot_data(self, bot: Bot, request: BaseBotRequest) -> None:
        # spawn or kill checking
        if request.online is not None:
            if request.online and bot.online:
                raise HTTPException(
                    status_code=422,
                    detail=f'Bot "{bot.name}" is already online.'
                )
            elif not request.online and not bot.online:
                raise HTTPException(
                    status_code=422,
                    detail=f'Bot "{bot.name}" is not online.'
                )

        # name
        if request.name is not None:
            bot.set_name(self.__plugin.parse_name(request.name))
            self.__plugin.bot_manager.update_list()

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

        # tags
        if request.tags is not None:
            bot.set_tags(request.tags)

        # auto login
        if request.autoLogin is not None:
            bot.set_auto_login(request.autoLogin)

        # auto run actions
        if request.autoRunActions is not None:
            bot.set_auto_run_actions(request.autoRunActions)

        # auto update
        if request.autoUpdate is not None:
            bot.set_auto_update(request.autoUpdate)

        # spawn or kill perform
        if request.online is not None:
            if request.online and not bot.online:
                bot.spawn()
            elif not request.online and bot.online:
                bot.kill()

        # save data
        self.__plugin.bot_manager.save_data()

    def __mount_app(self, server: PluginServerInterface):
        # create app
        app = FastAPI()

        @app.get("/bots")
        async def __get_bots() -> BotsGetResponse:
            bots = [
                to_bot_model(bot)
                for bot in self.__bot_manager.bots.values()
            ]
            return BotsGetResponse(bots=bots)

        @app.post("/bots")
        async def __post_bots(request: PostBotRequest) -> BotModel:
            # parse name
            name = self.__plugin.parse_name(request.name)

            # create bot
            try:
                bot = self.__plugin.bot_manager.save(
                    name,
                    location=Location(
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
                return to_bot_model(bot)
            except BotAlreadySavedException:
                raise HTTPException(
                    status_code=422,
                    detail=f'Bot "{name}" is already saved.'
                )

        @app.patch("/bots/{bot_name}")
        async def __patch_bot(
                bot_name: str,
                request: PatchBotRequest
        ) -> BotModel:
            # parse name
            name = self.__plugin.parse_name(bot_name)

            # check request params
            if (
                    request.name is None and
                    request.location is None and
                    request.comment is None and
                    request.actions is None and
                    request.tags is None and
                    request.autoLogin is None and
                    request.autoRunActions is None and
                    request.autoUpdate is None and
                    request.online is None
            ):
                raise HTTPException(
                    status_code=422,
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
                return to_bot_model(bot)
            except BotNotExistsException:
                raise HTTPException(
                    status_code=422,
                    detail=f'Bot "{name}" is not found.'
                )

        @app.delete("/bots/{bot_name}")
        async def __delete_bot(bot_name: str) -> None:
            name = self.__plugin.parse_name(bot_name)
            try:
                self.__bot_manager.delete(name)
                self.__logger.debug(f'Deleted "{name}"')
                return None
            except BotNotExistsException:
                raise HTTPException(
                    status_code=422,
                    detail=f'Bot "{name}" is not found.'
                )
            except BotNotSavedException:
                raise HTTPException(
                    status_code=422,
                    detail=f'Bot "{name}" is not saved.'
                )

        # mount
        self.__plugin.fastapi_mcdr.mount(self.__plugin.plugin_id, app)

    def unload(self):
        if self.__plugin.fastapi_mcdr is not None:
            self.__plugin.fastapi_mcdr.unmount(self.__plugin.plugin_id)
