from dataclasses import dataclass
from abc import ABC, abstractmethod, abstractclassmethod
from typing import Any, List, Iterable
from json import dumps

from .yarn import Value, Identifier, Yarn

# Messages

@dataclass
class Message(ABC):
    timestamp : float
    context : Identifier

    # IO

    @abstractmethod
    def dump(self):
        """Convert a message to a JSON encoding."""

        raise NotImplementedError(f"Object {self} has no `dump` method.")

    @abstractclassmethod
    def load(cls, json):
        """Load a message from a JSON encoding."""

        raise NotImplementedError(f"Class {cls} has no `load` method.")

    # magic methods

    def __str__(self):
        return dumps(self.dump())

@dataclass
class Enter(Message):
    identifier : Identifier

    def dump(self):
        """Convert an Enter message to a JSON encoding."""

        return {
            "type" : "enter",
            "identifier" : self.identifier.dump(),
            "context" : self.context.dump(),
            "timestamp" : self.timestamp
        }

    @classmethod
    def load(cls, json) -> "Enter":
        """Load an Enter message from a JSON encoding."""

        assert json["type"] == "enter"
        identifier = Identifier.load(json["identifier"])
        context = Identifier.load(json["context"])
        timestamp = json["timestamp"]

        return cls(identifier=identifier, context=context, timestamp=timestamp)

@dataclass
class Exit(Message):
    identifier : Identifier

    def dump(self):
        """Convert an Exit message to a JSON encoding."""

        return {
            "type" : "exit",
            "identifier" : self.identifier.dump(),
            "context" : self.context.dump(),
            "timestamp" : self.timestamp
        }

    @classmethod
    def load(cls, json) -> "Exit":
        """Load an Exit message from a JSON encoding."""

        assert json["type"] == "exit"
        identifier = Identifier.load(json["identifier"])
        context = Identifier.load(json["context"])
        timestamp = json["timestamp"]

        return cls(identifier=identifier, context=context, timestamp=timestamp)

@dataclass
class Emit(Message):
    name : str
    value : Any
    context : Identifier

    def dump(self):
        """Convert an Emit message to a JSON encoding."""

        return {
            "type" : "emit",
            "name" : self.name,
            "value" : self.value,
            "context" : self.context.dump(),
            "timestamp" : self.timestamp
        }

    @classmethod
    def load(cls, json) -> "Emit":
        """Load an Emit message from a JSON encoding."""

        context = Identifier.load(json["context"])
        name, value = json["name"], json["value"]
        timestamp = json["timestamp"]

        return cls(name=name, value=value, context=context, timestamp=timestamp)

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

# Sequences of Messages

def timestamp_order(messages : List[Message]) -> Iterable[Message]:
    """Yield messages in increasing timestamp-order (so earlier messages are yielded first)."""

    yield from sorted(messages, key=lambda message: message.timestamp)

def load(messages : List[Message]) -> Yarn:
    """Load a Yarn object from a list of messages.
    
    Based on the classic Shunting-Yard algorithm. Runs in O(m) time."""

    stack = []

    for message in timestamp_order(messages):
        # case 1: emits and enters get pushed onto the stack
        if isinstance(message, (Emit, Enter)):
            stack.append(message)

        # case 2: exits process all values until the matching enter
        if isinstance(message, Exit):
            values, contexts = [], []
            
            # search for the matching enter
            while stack:
                obj = stack.pop()

                # push the object into the right list
                if isinstance(obj, Emit):
                    value = Value(name=obj.name, value=obj.value)
                    values.append(value)

                if isinstance(obj, Yarn):
                    contexts.append(obj)

                if isinstance(obj, Enter) and obj.identifier == message.identifier:
                    exit_time = obj.timestamp
                    break
            
            # if we don't find the matching enter, contexts are unmatched
            else:
                raise Exception()

            # build the new yarn object
            yarn = Yarn(
                identifier=message.identifier,
                values=values,
                contexts=contexts,
                enter_time=message.timestamp,
                exit_time=exit_time
            )

            # and add it back to the stack
            stack.append(yarn)

    # if all went well, the only object remaining on the stack is a yarn object we can return
    return stack[0]