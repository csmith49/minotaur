import click
from .cli import cli

from ..maze import Maze
from ..interface import load, is_context, is_value

from json import dumps
from sys import stdout
from typing import Iterable, Callable, Tuple, TypeVar
from itertools import chain, filterfalse, tee

T = TypeVar("T")

def partition(iterable : Iterable[T], predicate : Callable[[T], bool]) -> Tuple[Iterable[T], Iterable[T]]:
    """Partition an iterable by a predicate."""

    iter1, iter2 = tee(iterable)
    return filterfalse(predicate, iter1), filter(predicate, iter2)

def entries(maze : Maze) -> Iterable:
    """Convert a maze to a sequence of rows in a JSONL-encoded table."""

    if is_context(maze):
        values, contexts = partition(maze.mazes(), is_context)
        
        # pre-populate the entry with the values
        entry = {value.symbol : value.value for value in values}
        # tag the maze symbol with the key
        entry[f"{maze.symbol}:key"] = maze.key
        # and add the duration
        entry[f"{maze.symbol}:duration"] = maze.value.duration

        # now, merge with all the sub-contexts (if they exist!)
        contexts = list(contexts)

        if contexts:
            context_entries = (entries(context) for context in contexts)
            for context_entry in chain.from_iterable(context_entries):
                yield {**entry, **context_entry}
        else:
            yield entry

def dump(maze : Maze, fp):
    """Dump the paths of a maze to the provided file pointer."""

    for entry in entries(maze):
        fp.write(f"{dumps(entry)}\n")

@cli.command()
@click.argument("filepath")
@click.option("-o", "--output", type=str, help="Output file to which rows will be appended.")
def jsonl(filepath, output):
    """Convert a message log into a JSONL-encoded table."""

    mazes = load(filepath=filepath)

    if output:
        with open(output, "a") as f:
            for maze in mazes:
                dump(maze, f)
    
    else:
        for maze in mazes:
            dump(maze, stdout)
