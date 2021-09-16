from dataclasses import dataclass
from typing import List, Dict, Any

from ..hash import hash
from ..timer import current_time

@dataclass
class Value:
    name : str
    value : Any

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
