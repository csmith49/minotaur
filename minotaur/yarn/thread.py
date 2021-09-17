from dataclasses import dataclass
from abc import ABC, abstractmethod, abstractclassmethod
from typing import Any, List, Iterable
from json import dumps

from .yarn import Value, Identifier, Yarn

# Messages

@dataclass
class Message(ABC):
    timestamp : int
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
            "context" : self.identifier.dump(),
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

# Threads

class Thread:
    """A linearized Yarn."""

    def __init__(self, messages : List[Message]):
        """Construct a Thread from a list of messagse."""

        self._messages = messages

    # Access

    @property
    def messages(self) -> Iterable[Message]:
        """Yield messages in timestamp-order."""

        yield from sorted(self.messages, key=lambda m: m.timestamp)

    # IO

    def dump(self):
        """Encode a Thread as a list of JSON objects."""

        lines = []
        for message in self.messages_in_order():
            lines.append(message.dump())

        return lines

    @classmethod
    def load(cls, jsonl) -> "Thread":
        """Load a Thread from a list of JSON objects."""

        messages = [Message.load(json) for json in jsonl]
        return cls(messages=messages)

    # Conversion

    def yarn(self) -> Yarn:
        """Convert a Thread object to a Yarn object.
        
        Based on the classic Shunting-Yard algorithim. Runs in O(m) time."""

        stack = []

        for message in self.messages:
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