from ..maze import Maze
from ..message import Message, Enter, Exit, Emit, ContextGraph

from typing import Iterable, List, Union, Any
from json import loads
from dataclasses import dataclass

# Utility Algorithms

@dataclass(eq=True, frozen=True)
class Timestamp:
    start : float
    stop : float

    @property
    def duration(self):
        return self.stop - self.start

def tangle(messages : List[Message]) -> Maze[Union[Timestamp, Any]]:
    """Load a Maze object from a list of messages.
    
    Based on the classic Shunting-Yard algorithm. Runs in O(m) time."""

    stack = []

    for message in sorted(messages):
        # case 1: emits are converted to value-wrapping mazes and pushed onto the stack
        if isinstance(message, Emit):
            maze = Maze(identifier=message.identifier, value=message.value, branches=[])
            stack.append(maze)

        # case 2: enters are pushed onto the stack as-is
        if isinstance(message, Enter):
            stack.append(message)

        # case 3: exits process all mazes on the stack until the matching enter
        if isinstance(message, Exit):
            mazes = []

            # search for the matching enter
            while stack:
                obj = stack.pop()

                # store mazes
                if isinstance(obj, Maze):
                    mazes.append(obj)
                
                # and check enters
                if isinstance(obj, Enter) and obj.identifier == message.identifier:

                    # build the timestamp-wrapping maze and push back to stack
                    timestamp = Timestamp(start=obj.timestamp, stop=message.timestamp)
                    maze = Maze(identifier=message.identifier, value=timestamp, branches=mazes)
                    stack.append(maze)

                    # and make sure we exit the loop
                    break
            
            # if we don't exit...
            else:
                raise Exception(f"No matching enter for identifier {message.identifier}...")

    # if all went well, there's exactly one maze on the stack
    assert len(stack) == 1
    return stack[0]

# Utilities associated with the tangling operation above

def is_value(maze : Maze) -> bool:
    """True iff the maze has no paths and doesn't contain a timestamp."""

    return (not isinstance(maze.value, Timestamp)) and maze.is_deadend

def is_context(maze : Maze) -> bool:
    """True iff the maze contains a timestamp."""

    return isinstance(maze.value, Timestamp)

# IO Utility

def load_messages(filepath : str) -> Iterable[Message]:
    """Load a sequence of messages from the indicated filepath."""

    with open(filepath, "r") as f:
        for line in f.readlines():
            contents = loads(line)
            yield Message.load(contents)

def mazes_from_messages(messages : Iterable[Message]) -> Iterable[Maze]:
    """Convert a sequence of messages to a sequence of Mazes."""

    graph = ContextGraph(messages)
    for component in graph.components():
        yield tangle(component)

def load(filepath : str) -> Iterable[Maze]:
    """Load a sequence of Mazes from a message file."""

    yield from mazes_from_messages(load_messages(filepath))