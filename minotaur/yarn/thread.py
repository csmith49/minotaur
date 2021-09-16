from dataclasses import dataclass
from abc import ABC
from typing import Any

from .yarn import Value, Identifier

# Messages

@dataclass
class Message(ABC):
    timestamp : int

@dataclass
class Enter(Message):
    identifier : Identifier

@dataclass
class Exit(Message):
    identifier : Identifier

@dataclass
class Emit(Message):
    name : str
    value : Any
    context : Identifier

# monkey patch .load static method for Message

@staticmethod
def _load_message(json) -> Message:
    """Load a message from a JSON encoding."""

    # switch constructor based on the type field
    if json["type"] == "enter":
        identifier = Identifier.load(json["identifier"])
        return Enter(identifier=identifier, timestamp=json["timestamp"])

    elif json["type"] == "exit":
        identifier = Identifier.load(json["identifier"])
        return Exit(identifier=identifier, timestamp=json["timestamp"])

    elif json["type"] == "emit":
        identifier = Identifier.load(json["Identifier"])
        return Emit(name=json["name"], value=json["value"], context=identifier)

    else:
        raise ArgumentError(f"Object {json} does not represent a Message.")

setattr(Message, "load", _load_message)

# Threads

@dataclass
class Thread:
    messages : List[Message]

    def messages_in_order(self) -> Iterable[Message]:
        yield from sorted(self.messages, key=lambda m: m.timestamp)

    def to_yarn(self) -> Yarn:
        pass
