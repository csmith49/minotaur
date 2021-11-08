from dataclasses import dataclass
from typing import List, Optional, Iterable, Generic, TypeVar
from collections.abc import Container
from itertools import chain

from .identifier import Identifier
from .path import Node, Path

# maze

T = TypeVar("T")

@dataclass
class Maze(Generic[T]):
    """Mazes recursively track the relationship between identifiers and polymorphic values."""

    identifier : Identifier
    value : T
    branches : List["Maze"]

    # Useful Accesssors

    @property
    def symbol(self) -> str:
        """Identifier symbol."""

        return self.identifier.symbol

    @property
    def key(self) -> str:
        """Identifier key."""

        return self.identifier.key

    @property
    def is_deadend(self) -> bool:
        """Returns `True` if the Maze has no paths."""
        
        return self.branches == []

    # Recursing Utilities

    def choices(self) -> Iterable[str]:
        """Yields all unique symbols identifying branches in the Maze."""

        yield from set([maze.symbol for maze in self.paths])

    def mazes(self, symbols : Optional[Container[str]] = None) -> Iterable["Maze"]:
        """Iterates over all mazes reachable via a path, optionally filtering out those that do not contain a provided symbol."""

        for maze in self.branches:
            if symbols is None or maze.symbol in symbols:
                yield maze

    def deadends(self, symbols : Optional[Container[str]] = None) -> Iterable["Maze"]:
        """Iterates over all dead-end mazes, optionally filtering out those that do not contain a provided symbol."""

        for maze in self.mazes(symbols=symbols):
            if maze.is_deadend:
                yield maze
            

    # Path-based manipulation

    @property
    def paths(self) -> Iterable[Path]:
        """Iterate over all complete paths in the maze."""

        node = Node(identifier=self.identifier, value=self.value)

        if self.is_deadend:
            yield node << Path.empty()

        else:
            subpaths = (maze.paths for maze in self.mazes())
            for subpath in chain.from_iterable(subpaths):
                yield node << subpath

    # IO

    @classmethod
    def load(cls, json, value_loader = None) -> "Maze":
        """Load a Maze object from a JSON encoding."""

        assert json["type"] == "maze"
        identifier = Identifier.load(json["identifier"])
        value = value_loader(json["value"]) if value_loader else json["value"]
        mazes = [cls.load(maze, value_loader=value_loader) for maze in json["mazes"]]
        return cls(identifier=identifier, value=value, branches=mazes)

    def dump(self, value_dumper = None):
        """Convert a Maze object to a JSON encoding."""

        return {
            "type" : "maze",
            "identifier" : self.identifier.dump(),
            "value" : value_dumper(self.value) if value_dumper else self.value,
            "mazes" : [maze.dump(value_dumper=value_dumper) for maze in self.mazes()]
        }
