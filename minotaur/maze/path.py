from dataclasses import dataclass
from typing import Any, Tuple, Iterable

from .identifier import Identifier

# nodes

@dataclass(eq=True, frozen=True)
class Node:
    """Nodes are context-free linearized mazes."""

    identifier : Identifier
    value : Any

    # Accessors

    @property
    def symbol(self) -> str:
        """Identifier symbol."""

        return self.identifier.symbol

    @property
    def key(self) -> str:
        """Identifier key."""

        return self.identifier.key

# paths

@dataclass(eq=True, frozen=True)
class Path:
    """Paths are lists of nodes."""

    nodes : Tuple[Node]

    # construction

    @classmethod
    def empty(cls) -> "Path":
        """Construct an empty path."""

        return cls(nodes=())

    def prepend(self, node : Node) -> "Path":
        """Add a node to the beginning of the path."""

        return self.__class__(nodes=(node, *self.nodes))

    # Dunder methods for easy interfacing

    def __iter__(self) -> Iterable[Node]:
        """Iterate over all nodes in the path."""

        yield from self.nodes

    def __rlshift__(self, other : Node) -> "Path":
        """Alias for `self.prepend(other)`."""

        return self.prepend(other)