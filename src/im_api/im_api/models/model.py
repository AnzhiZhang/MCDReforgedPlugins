# Copyright (c) 2024 Repository RF-Tar-Railt
# Licensed under the MIT License.
# See the LICENSE file in the root of the repository for more details.
import mimetypes
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime
from enum import IntEnum
from os import PathLike
from pathlib import Path
from typing import IO, Any, Callable, ClassVar, Generic, Literal, Optional, TypeVar, Union
from typing_extensions import TypeAlias

from .element import Element, transform
from .parser import Element as RawElement
from .parser import parse


@dataclass
class ModelBase:
    __converter__: ClassVar[dict[str, Callable[[Any], Any]]] = {}

    @classmethod
    def parse(cls, raw: dict):
        fs = fields(cls)
        data = {}
        for fd in fs:
            if fd.name in raw:
                if fd.name in cls.__converter__:
                    data[fd.name] = cls.__converter__[fd.name](raw[fd.name])
                else:
                    data[fd.name] = raw[fd.name]
        return cls(**data)  # type: ignore

    def dump(self) -> dict:
        raise NotImplementedError


class ChannelType(IntEnum):
    TEXT = 0
    DIRECT = 1
    CATEGORY = 2
    VOICE = 3


@dataclass
class Channel(ModelBase):
    id: str
    type: ChannelType
    name: Optional[str] = None
    parent_id: Optional[str] = None

    __converter__ = {"type": ChannelType}

    def dump(self):
        res = {"id": self.id, "type": self.type.value}
        if self.name:
            res["name"] = self.name
        if self.parent_id:
            res["parent_id"] = self.parent_id
        return res


@dataclass
class Guild(ModelBase):
    id: str
    name: Optional[str] = None
    avatar: Optional[str] = None

    def dump(self):
        res = {"id": self.id}
        if self.name:
            res["name"] = self.name
        if self.avatar:
            res["avatar"] = self.avatar
        return res


@dataclass
class User(ModelBase):
    id: str
    name: Optional[str] = None
    nick: Optional[str] = None
    avatar: Optional[str] = None
    is_bot: Optional[bool] = None

    def dump(self):
        res: dict[str, Any] = {"id": self.id}
        if self.name:
            res["name"] = self.name
        if self.nick:
            res["nick"] = self.nick
        if self.avatar:
            res["avatar"] = self.avatar
        if self.is_bot:
            res["is_bot"] = self.is_bot
        return res


@dataclass
class Member(ModelBase):
    user: Optional[User] = None
    nick: Optional[str] = None
    avatar: Optional[str] = None
    joined_at: Optional[datetime] = None

    __converter__ = {"user": User.parse, "joined_at": lambda ts: datetime.fromtimestamp(int(ts) / 1000)}

    def dump(self):
        res = {}
        if self.user:
            res["user"] = self.user.dump()
        if self.nick:
            res["nick"] = self.nick
        if self.avatar:
            res["avatar"] = self.avatar
        if self.joined_at:
            res["joined_at"] = int(self.joined_at.timestamp() * 1000)
        return res


@dataclass
class Role(ModelBase):
    id: str
    name: Optional[str] = None

    def dump(self):
        res = {"id": self.id}
        if self.name:
            res["name"] = self.name
        return res


class LoginStatus(IntEnum):
    OFFLINE = 0
    ONLINE = 1
    CONNECT = 2
    DISCONNECT = 3
    RECONNECT = 4


@dataclass
class Login(ModelBase):
    status: LoginStatus
    user: Optional[User] = None
    self_id: Optional[str] = None
    platform: Optional[str] = None
    features: list[str] = field(default_factory=list)
    proxy_urls: list[str] = field(default_factory=list)

    __converter__ = {"user": User.parse, "status": LoginStatus}

    def dump(self):
        res: dict[str, Any] = {
            "status": self.status.value,
            "features": self.features,
            "proxy_urls": self.proxy_urls,
        }
        if self.user:
            res["user"] = self.user.dump()
        if self.self_id:
            res["self_id"] = self.self_id
        if self.platform:
            res["platform"] = self.platform
        return res

    @property
    def id(self) -> Optional[str]:
        return self.self_id or (self.user.id if self.user else None)


@dataclass
class LoginPreview(ModelBase):
    user: User
    platform: str
    status: Optional[LoginStatus] = None
    features: list[str] = field(default_factory=list)
    proxy_urls: list[str] = field(default_factory=list)

    __converter__ = {"user": User.parse, "status": LoginStatus}

    def dump(self):
        res: dict[str, Any] = {
            "user": self.user.dump(),
            "platform": self.platform,
            "features": self.features,
            "proxy_urls": self.proxy_urls,
        }
        if self.status:
            res["status"] = self.status.value
        return res

    @property
    def id(self) -> str:
        return self.user.id


LoginType = Union[Login, LoginPreview]


@dataclass
class ArgvInteraction(ModelBase):
    name: str
    arguments: list
    options: Any

    def dump(self):
        return asdict(self)


@dataclass
class ButtonInteraction(ModelBase):
    id: str

    def dump(self):
        return asdict(self)


class Opcode(IntEnum):
    EVENT = 0
    PING = 1
    PONG = 2
    IDENTIFY = 3
    READY = 4


@dataclass
class Identify(ModelBase):
    token: Optional[str] = None
    sequence: Optional[int] = None


@dataclass
class Ready(ModelBase):
    logins: list[Login]


@dataclass
class MessageObject(ModelBase):
    id: str
    content: str
    channel: Optional[Channel] = None
    guild: Optional[Guild] = None
    member: Optional[Member] = None
    user: Optional[User] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_elements(
            cls,
            id: str,
            content: list[Element],
            channel: Optional[Channel] = None,
            guild: Optional[Guild] = None,
            member: Optional[Member] = None,
            user: Optional[User] = None,
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None,
    ):
        return cls(id, "".join(str(i) for i in content), channel, guild, member, user, created_at, updated_at)

    @property
    def message(self) -> list[Element]:
        return transform(parse(self.content))

    @classmethod
    def parse(cls, raw: dict):
        if "elements" in raw and "content" not in raw:
            content = [RawElement(*item.values()) for item in raw["elements"]]
            raw["content"] = "".join(str(i) for i in content)
        return super().parse(raw)

    __converter__ = {
        "channel": Channel.parse,
        "guild": Guild.parse,
        "member": Member.parse,
        "user": User.parse,
        "created_at": lambda ts: datetime.fromtimestamp(int(ts) / 1000),
        "updated_at": lambda ts: datetime.fromtimestamp(int(ts) / 1000),
    }

    def dump(self):
        res: dict[str, Any] = {"id": self.id, "content": self.content}
        if self.channel:
            res["channel"] = self.channel.dump()
        if self.guild:
            res["guild"] = self.guild.dump()
        if self.member:
            res["member"] = self.member.dump()
        if self.user:
            res["user"] = self.user.dump()
        if self.created_at:
            res["created_at"] = int(self.created_at.timestamp() * 1000)
        if self.updated_at:
            res["updated_at"] = int(self.updated_at.timestamp() * 1000)
        return res


@dataclass
class Event(ModelBase):
    id: int
    type: str
    timestamp: datetime
    platform: Optional[str] = None
    self_id: Optional[str] = None
    argv: Optional[ArgvInteraction] = None
    button: Optional[ButtonInteraction] = None
    channel: Optional[Channel] = None
    guild: Optional[Guild] = None
    login: Optional[LoginType] = None
    member: Optional[Member] = None
    message: Optional[MessageObject] = None
    operator: Optional[User] = None
    role: Optional[Role] = None
    user: Optional[User] = None

    _type: Optional[str] = None
    _data: Optional[dict] = None

    __converter__ = {
        "timestamp": lambda ts: datetime.fromtimestamp(int(ts) / 1000),
        "argv": ArgvInteraction.parse,
        "button": ButtonInteraction.parse,
        "channel": Channel.parse,
        "guild": Guild.parse,
        "login": lambda raw: (
            LoginPreview.parse(
                raw if raw["user"] else {**raw, "user": {"id": raw["self_id"]}} if "self_id" in raw else raw
            )
            if "user" in raw
            else Login.parse(raw)
        ),
        "member": Member.parse,
        "message": MessageObject.parse,
        "operator": User.parse,
        "role": Role.parse,
        "user": User.parse,
    }

    @property
    def platform_(self):
        if self.platform:
            return self.platform
        if self.login and self.login.platform:
            return self.login.platform
        raise ValueError("platform not found")

    @property
    def self_id_(self):
        if self.self_id:
            return self.self_id
        if self.login and self.login.id:
            return self.login.id
        raise ValueError("self_id not found")

    def __post_init__(self):
        _ = self.platform_
        _ = self.self_id_

    def dump(self):
        res = {
            "id": self.id,
            "type": self.type,
            "platform": self.platform_,
            "self_id": self.self_id_,
            "timestamp": int(self.timestamp.timestamp() * 1000),
        }
        if self.argv:
            res["argv"] = self.argv.dump()
        if self.button:
            res["button"] = self.button.dump()
        if self.channel:
            res["channel"] = self.channel.dump()
        if self.guild:
            res["guild"] = self.guild.dump()
        if self.login:
            res["login"] = self.login.dump()
        if self.member:
            res["member"] = self.member.dump()
        if self.message:
            res["message"] = self.message.dump()
        if self.operator:
            res["operator"] = self.operator.dump()
        if self.role:
            res["role"] = self.role.dump()
        if self.user:
            res["user"] = self.user.dump()
        if self._type:
            res["_type"] = self._type
        if self._data:
            res["_data"] = self._data
        return res


T = TypeVar("T", bound=ModelBase)


@dataclass
class PageResult(ModelBase, Generic[T]):
    data: list[T]
    next: Optional[str] = None

    @classmethod
    def parse(cls, raw: dict, parser: Optional[Callable[[dict], T]] = None) -> "PageResult[T]":
        data = [(parser or ModelBase.parse)(item) for item in raw["data"]]
        return cls(data, raw.get("next"))

    def dump(self):
        res: dict = {"data": [item.dump() for item in self.data]}
        if self.next:
            res["next"] = self.next
        return res


@dataclass
class PageDequeResult(PageResult[T]):
    prev: Optional[str] = None

    @classmethod
    def parse(cls, raw: dict, parser: Optional[Callable[[dict], T]] = None) -> "PageDequeResult[T]":
        data = [(parser or ModelBase.parse)(item) for item in raw["data"]]
        return cls(data, raw.get("next"), raw.get("prev"))

    def dump(self):
        res: dict = {"data": [item.dump() for item in self.data]}
        if self.next:
            res["next"] = self.next
        if self.prev:
            res["prev"] = self.prev
        return res


Direction: TypeAlias = Literal["before", "after", "around"]
Order: TypeAlias = Literal["asc", "desc"]


@dataclass
class Upload:
    file: Union[bytes, IO[bytes], PathLike]
    mimetype: str = "image/png"
    name: Optional[str] = None

    def __post_init__(self):
        if isinstance(self.file, PathLike):
            self.mimetype = mimetypes.guess_type(str(self.file))[0] or self.mimetype
            self.name = Path(self.file).name

    def dump(self):
        file = self.file

        if isinstance(file, PathLike):
            file = open(file, "rb")

        return {"value": file, "filename": self.name, "content_type": self.mimetype}
