from dataclasses import dataclass
from abc import ABC, abstractmethod, abstractclassmethod
from typing import Any
from json import dumps

from ..maze import Identifier

# Messages

@dataclass(eq=True, frozen=True)
class Message(ABC):
    """Base class for linearization of mazes."""

    identifier : Identifier
    context : Identifier
    timestamp : float

    # IO

    @abstractmethod
    def dump(self):
        """Convert a message to a JSON encoding."""

        raise NotImplementedError(f"Object {self} has no `dump` method.")

    @abstractclassmethod
    def load(cls, json):
        """Load a message from a JSON encoding."""

        raise NotImplementedError(f"Class {cls} has no `load` method.")

    def dump_stub(self):
        """Construct a dump stub for JSON encoding.
        
        To be used in sub-class instantiations of `dump`."""

        return {
            "identifier" : self.identifier.dump(),
            "context" : self.context.dump(),
            "timestamp" : self.timestamp
        }

    @classmethod
    def load_stub(cls, json):
        """Partially parse the JSON encoding for the message.
        
        To be used in sub-class instantiations of `load`."""

        return {
            "identifier" : Identifier.load(json["identifier"]),
            "context" : Identifier.load(json["context"]),
            "timestamp" : json["timestamp"]
        }

    # magic methods

    def __str__(self):
        return dumps(self.dump())

    def __lt__(self, other):
        """Uses timestamp-order."""

        return self.timestamp <= other.timestamp

@dataclass(eq=True, frozen=True)
class Enter(Message):
    """Denotes a context has been entered."""

    def dump(self):
        """Convert an Enter message to a JSON encoding."""

        result = self.dump_stub()
        result["type"] = "enter"
        return result

    @classmethod
    def load(cls, json) -> "Enter":
        """Load an Enter message from a JSON encoding."""

        assert json["type"] == "enter"
        kwargs = cls.load_stub(json)
        return cls(**kwargs)

@dataclass(eq=True, frozen=True)
class Exit(Message):
    """Denotes a context has been exited."""

    def dump(self):
        """Convert an Exit message to a JSON encoding."""

        result = self.dump_stub()
        result["type"] = "exit"
        return result

    @classmethod
    def load(cls, json) -> "Exit":
        """Load an Exit message from a JSON encoding."""

        assert json["type"] == "exit"
        kwargs = cls.load_stub(json)
        return cls(**kwargs)

@dataclass(eq=True, frozen=True)
class Emit(Message):
    """Denotes a value has been emitted."""

    value : Any

    def dump(self):
        """Convert an Emit message to a JSON encoding."""

        result = self.dump_stub()
        result["type"] = "emit"
        result["value"] = self.value
        return result

    @classmethod
    def load(cls, json) -> "Emit":
        """Load an Emit message from a JSON encoding."""

        assert json["type"] == "emit"
        kwargs = cls.load_stub(json)
        value = json["value"]
        return cls(value=value, **kwargs)

# monkey patch .load static method for Message

@staticmethod
def _load_message(json) -> Message:
    """Load a message from a JSON encoding."""

    # switch constructor based on the type field
    if json["type"] == "enter":
        return Enter.load(json)
    elif json["type"] == "exit":
        return Exit.load(json)
    elif json["type"] == "emit":
        return Emit.load(json)
    else:
        raise TypeError(f"Object {json} does not represent a Message.")

setattr(Message, "load", _load_message)
