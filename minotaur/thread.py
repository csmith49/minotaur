from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
def Thread:
    key : str
    symbol : str
    metadata : Dict[str, Any]
    children : List['Thread']

    def json(self):
        """Convert the thread to a JSON-encodable object."""

        return {
            "key" : self.key,
            "symbol" : self.symbol,
            "metadata" : self.metadata,
            "children" : [
                child.json() for child in self.children
            ]
        }
