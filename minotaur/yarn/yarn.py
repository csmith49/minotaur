from dataclasses import dataclass
from typing import List, Optional, Any, Dict

from ..utility.seed import Seed

@dataclass(eq=True, frozen=True)
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

@dataclass(eq=True, unsafe_hash=True)
class Identifier:
    symbol : str
    key : str

    def __init__(self, symbol : str, key : Optional[str] = None):
        """Construct an identifier from a symbol.

        Identifiers are further disambiguated with a key, constructed using `utility.Seed`.
        """

        self.symbol = symbol

        if key is not None:
            self.key = key
        else:
            self.key = Seed().value

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
    enter_time : float
    exit_time : float

    # Accessing Attributes

    @property
    def duration(self) -> float:
        """Total time the context was open."""

        return self.exit_time - self.enter_time

    @property
    def symbol(self) -> str:
        """Identifier symbol."""

        return self.identifier.symbol

    @property
    def key(self) -> str:
        """Identifier key."""

        return self.identifier.key

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