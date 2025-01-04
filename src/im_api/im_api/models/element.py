from base64 import b64encode
from dataclasses import InitVar, dataclass, field, fields
from io import BytesIO
from pathlib import Path
from typing import Any, ClassVar, Optional, TypeVar, Union, get_args
from typing_extensions import override

TE = TypeVar("TE", bound="Element")

@dataclass(repr=False)
class Element:
    """Base class for all Satori message elements."""
    
    _attrs: dict[str, Any] = field(init=False, default_factory=dict)
    _children: list["Element"] = field(init=False, default_factory=list)
    
    __names__: ClassVar[tuple[str, ...]]
    
    @property
    def children(self) -> list["Element"]:
        """Get the child elements."""
        return self._children

    @property
    def type(self) -> str:
        """Get the element type."""
        return self.__class__.__name__.lower()
    
    @classmethod
    def unpack(cls, attrs: dict[str, Any]):
        """Create an element from attributes."""
        obj = cls(**{k: v for k, v in attrs.items() if k in cls.__names__})  # type: ignore
        obj._attrs.update({k: v for k, v in attrs.items() if k not in cls.__names__})
        return obj

    def __post_init__(self):
        """Post initialization processing."""
        for f in fields(self):
            if f.name in ("_attrs", "_children"):
                continue
            _type = get_args(f.type)[0] if hasattr(f.type, "__origin__") else f.type
            if _type is not str and isinstance(attr := getattr(self, f.name), str):
                if _type is bool:
                    if attr.lower() not in ("true", "false"):
                        raise TypeError(f.name, attr)
                    setattr(self, f.name, attr.lower() == "true")
                else:
                    setattr(self, f.name, _type(attr))  # type: ignore
            self._attrs[f.name] = getattr(self, f.name)
        self._attrs = {k: v for k, v in self._attrs.items() if v is not None}

    def to_dict(self) -> dict:
        """Convert element to Satori protocol format."""
        result = {"type": self.type}
        if self._attrs:
            result["attrs"] = self._attrs
        if self._children:
            result["children"] = [child.to_dict() for child in self._children]
        return result

    def __str__(self) -> str:
        return str(self.to_dict())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._attrs!r}, children={len(self._children)})"

    def __call__(self, *content: Union[str, "Element"]):
        """Add child elements."""
        self._children.extend(Text(i) if isinstance(i, str) else i for i in content)
        self.__post_call__()
        return self

    def __post_call__(self):
        """Post call processing."""
        pass

    def __getitem__(self, key: str) -> Any:
        return self._attrs[key]

    @classmethod
    def from_dict(cls, data: dict) -> "Element":
        """Create element from Satori protocol format."""
        if "type" not in data:
            raise ValueError("Missing type in Satori data")
        
        element_type = data["type"]
        attrs = data.get("attrs", {})
        children = []
        
        for child in data.get("children", []):
            children.append(cls.from_dict(child))
            
        element_cls = ELEMENT_TYPES.get(element_type)
        if not element_cls:
            raise ValueError(f"Unknown element type: {element_type}")
            
        element = element_cls(**attrs)
        element._children = children
        return element

@dataclass(repr=False)
class Text(Element):
    """文本元素"""
    text: str
    __names__ = ("text",)

@dataclass(repr=False)
class At(Element):
    """提及用户元素"""
    id: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None
    type: Optional[str] = None
    __names__ = ("id", "name", "role", "type")

    @staticmethod
    def role_(role: str, name: Optional[str] = None) -> "At":
        return At(role=role, name=name)

    @staticmethod
    def all(here: bool = False) -> "At":
        return At(type="here" if here else "all")

@dataclass(repr=False)
class Channel(Element):
    """频道元素"""
    id: str
    name: Optional[str] = None
    parent_id: Optional[str] = None
    type: Optional[str] = None
    __names__ = ("id", "name", "parent_id", "type")

@dataclass(repr=False)
class Resource(Element):
    """资源元素基类"""
    src: str
    title: Optional[str] = None
    cache: Optional[bool] = None
    timeout: Optional[int] = None
    __names__ = ("src", "title", "cache", "timeout")

    @classmethod
    def of(
        cls,
        url: Optional[str] = None,
        path: Optional[Union[str, Path]] = None,
        raw: Optional[Union[bytes, BytesIO]] = None,
        mime: Optional[str] = None,
        name: Optional[str] = None,
        extra: Optional[dict[str, Any]] = None,
        cache: Optional[bool] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ):
        data: dict[str, Any] = {"extra": extra or kwargs}
        if url is not None:
            data |= {"src": url}
        elif path:
            data |= {"src": Path(path).as_uri()}
        elif raw and mime:
            bd = raw.getvalue() if isinstance(raw, BytesIO) else raw
            data |= {"src": f"data:{mime};base64,{b64encode(bd).decode('utf-8')}"}
        else:
            raise ValueError(f"{cls} need at least one of url, path and raw")
        if name is not None:
            data["title"] = name
        if cache is not None:
            data["cache"] = cache
        if timeout is not None:
            data["timeout"] = timeout
        return cls(**data)

@dataclass(repr=False)
class Image(Resource):
    """图片元素"""
    width: Optional[int] = None
    height: Optional[int] = None
    __names__ = ("src", "title", "width", "height", "cache", "timeout")

@dataclass(repr=False)
class Audio(Resource):
    """音频元素"""
    duration: Optional[int] = None
    __names__ = ("src", "title", "duration", "cache", "timeout")

@dataclass(repr=False)
class Video(Resource):
    """视频元素"""
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    __names__ = ("src", "title", "width", "height", "duration", "cache", "timeout")

@dataclass(repr=False)
class File(Resource):
    """文件元素"""
    __names__ = ("src", "title", "cache", "timeout")

@dataclass(repr=False)
class Message(Element):
    """消息元素"""
    id: Optional[str] = None
    content: Optional[str] = None
    channel: Optional[Channel] = None
    guild: Optional[str] = None
    member: Optional[dict] = None
    user: Optional[dict] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    __names__ = ("id", "content", "channel", "guild", "member", "user", "created_at", "updated_at")

@dataclass(repr=False)
class Quote(Message):
    """引用消息元素"""
    pass

@dataclass(repr=False)
class Button(Element):
    """按钮元素"""
    type: str
    id: Optional[str] = None
    href: Optional[str] = None
    text: Optional[str] = None
    theme: Optional[str] = None
    __names__ = ("type", "id", "href", "text", "theme")

    @classmethod
    def action(cls, button_id: str, theme: Optional[str] = None):
        return cls(type="action", id=button_id, theme=theme)

    @classmethod
    def link(cls, url: str, theme: Optional[str] = None):
        return cls(type="link", href=url, theme=theme)

    @classmethod
    def input(cls, text: str, theme: Optional[str] = None):
        return cls(type="input", text=text, theme=theme)

# 注册所有元素类型
ELEMENT_TYPES = {
    "text": Text,
    "at": At,
    "channel": Channel,
    "img": Image,
    "audio": Audio,
    "video": Video,
    "file": File,
    "message": Message,
    "quote": Quote,
    "button": Button,
}
# 导出所有元素类型
__all__ = [
    "Element",
    "Text",
    "At",
    "Channel",
    "Resource",
    "Image",
    "Audio",
    "Video",
    "File",
    "Message",
    "Quote",
    "Button",
    "ELEMENT_TYPES",
]

