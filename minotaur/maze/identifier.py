from dataclasses import dataclass
from typing import Optional

from ..utility.seed import Seed

@dataclass(eq=True, unsafe_hash=True)
class Identifier:
    """Identifiers associate a symbol with a unique key."""

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
