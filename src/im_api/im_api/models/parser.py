from dataclasses import dataclass
from typing import Any, Optional, Union

@dataclass
class Event:
    """Base class for Satori events."""
    type: str
    platform: str
    self_id: str
    timestamp: int
    data: dict[str, Any]

    def to_dict(self) -> dict:
        """Convert event to Satori protocol format."""
        return {
            "type": self.type,
            "platform": self.platform,
            "self_id": self.self_id,
            "timestamp": self.timestamp,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        """Create event from Satori protocol format."""
        return cls(
            type=data["type"],
            platform=data["platform"],
            self_id=data["self_id"],
            timestamp=data["timestamp"],
            data=data.get("data", {}),
        )

@dataclass
class Message:
    """Message class for Satori protocol."""
    id: str
    content: str
    channel: Optional[dict] = None
    guild: Optional[dict] = None
    member: Optional[dict] = None
    user: Optional[dict] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert message to Satori protocol format."""
        result = {
            "id": self.id,
            "content": self.content,
        }
        if self.channel:
            result["channel"] = self.channel
        if self.guild:
            result["guild"] = self.guild
        if self.member:
            result["member"] = self.member
        if self.user:
            result["user"] = self.user
        if self.created_at:
            result["created_at"] = self.created_at
        if self.updated_at:
            result["updated_at"] = self.updated_at
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """Create message from Satori protocol format."""
        return cls(
            id=data["id"],
            content=data["content"],
            channel=data.get("channel"),
            guild=data.get("guild"),
            member=data.get("member"),
            user=data.get("user"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

def parse_event(data: dict) -> Event:
    """Parse Satori protocol event."""
    return Event.from_dict(data)

def parse_message(data: dict) -> Message:
    """Parse Satori protocol message."""
    return Message.from_dict(data)

__all__ = ["Event", "Message", "parse_event", "parse_message"]
