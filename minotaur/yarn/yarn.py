from dataclasses import dataclass
from typing import List, Optional, Any, Dict

from ..hash import hash
from ..timer import current_time

@dataclass
class Value:
    name : str
    value : Any

    # IO

    @classmethod
    def load(cls, json) -> "Value":
        """Construct a Value from a JSON encoding."""

        name = json["name"]
        value = json["value"]

        return cls(name=name, value=value)

    def dump(self):
        """Convert the instance to a JSON encoding."""

        return {
            "name" : self.name,
            "value" : self.value
        }

@dataclass
class Identifier:
    symbol : str
    key : str

    def __init__(self, symbol : str, key : Optional[str] = None):
        """Construct an identifier from a symbol and an optional key.

        If no key is provided, one will be created with `hash.hash`.
        """

        self.symbol = symbol
        if key is not None:
            self.key = key
        else:
            self.key = hash()

    # IO

    @classmethod
    def load(cls, json) -> "Identifier":
        """Construct an identifier from a JSON representation."""

        symbol, key = json["symbol"], json["key"]
        return cls(symbol=symbol, key=key)

    def dump(self):
        """Convert the instance to a JSON encoding."""

        return {
            "symbol" : self.symbol,
            "key" : self.key
        }

# Yarn

@dataclass
class Yarn:
    identifier : Identifier
    values : Dict[str, Any]
    contexts : List["Yarn"]
    enter_time : int
    exit_time : int

    # Accessing Attributes

    @property
    def duration(self) -> int:
        """Total time the context was open."""

        return self.exit_time - self.enter_time

    # IO

    @classmethod
    def load(cls, json) -> "Yarn":
        """Construct a Yarn object from a JSON encoding."""

        identifier = Identifier.load(json["identifier"])
        values = [Value.load(value) for value in json["values"]]
        contexts = [cls.load(ctx) for ctx in json["contexts"]]
        enter_time = json["enter_time"]
        exit_time = json["exit_time"]

        return cls(
            identifier=identifier,
            values=values,
            contexts=contexts,
            enter_time=enter_time,
            exit_time=exit_time
        )

    def dump(self):
        """Construct a JSON encoding for a Yarn object."""

        return {
            "identifier" : self.identifier.dump(),
            "values" : [value.dump() for value in self.values],
            "contexts" : [ctx.dump() for ctx in self.contexts],
            "enter_time" : self.enter_time,
            "exit_time" : self.exit_time
        }