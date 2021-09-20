from networkx import Graph
import networkx.algorithms as algorithms
from typing import Iterable, Optional
from ..yarn import Identifier, Message, Enter, Exit, Yarn, load
from collections import defaultdict
from rich.tree import Tree

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

# loading multiple yarns

def yarns(messages : Iterable[Message]) -> Iterable[Yarn]:
    """Convert a sequence of messages into distinct Yarns."""

    graph = ContextGraph(messages)
    for component in graph.components():
        yield load(component)

# Symbol Tree Construction

def symbol_tree(title : str, yarn : Yarn) -> Tree:
    """Construct a Rich tree with the indicated title from the symbols in a Yarn."""
    
    tree = Tree(title)
    walk_symbol_tree(yarn, tree)
    return tree

def walk_symbol_tree(yarn : Yarn, tree : Tree, context_style : str = "green", value_style : str = "red"):
    """Recursively walk a Yarn to build a symbol tree."""

    tree = tree.add(yarn.symbol, style=context_style)

    # add values first
    for value in yarn.values:
        tree.add(value.name, style=value_style)
    
    # and only walk contexts that give a new symbol
    seen = set()
    for context in yarn.contexts:
        if context.symbol not in seen:
            walk_symbol_tree(context, tree, context_style=context_style, value_style=value_style)
            seen.add(context.symbol)