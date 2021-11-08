from networkx import Graph
import networkx.algorithms as algorithms
from typing import Iterable
from collections import defaultdict

from ..maze import Identifier
from .message import Message, Enter, Exit

# CONTEXT GRAPH

class ContextGraph:
    """Graph storing relationships between contexts.
    
    Used as a Union-Find style data-structure. Nodes are contexts, and edges indicate a sub-context relation."""
    
    def __init__(self, messages : Iterable[Message]):
        """Construct a context graph."""

        self.graph = Graph()
        self.context_map = defaultdict(lambda: set())

        for message in messages:
            if isinstance(message, (Enter, Exit)):
                self.graph.add_edge(message.identifier, message.context)
            
            self.context_map[message.context].add(message)

    def messages(self, *contexts : Identifier) -> Iterable[Message]:
        """Return all messages from the indicated contexts."""

        for context in contexts:
            yield from self.context_map[context]

    def components(self) -> Iterable[Iterable[Message]]:
        """Iterate over all connected components in the context graph."""

        for component in algorithms.components.connected_components(self.graph):
            yield self.messages(*component)