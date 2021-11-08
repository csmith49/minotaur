import click
from .cli import cli

from ..maze import Maze
from ..interface import load, is_value, is_context

from rich import print
from rich.tree import Tree

def walk(
    maze : Maze,
    tree : Tree,
    include_values : bool = False,
    value_styling : str = "red",
    context_styling : str = "green"
):
    """Walk a maze, appending to a tree as we do so."""

    if is_value(maze) and include_values:
        tree.add(maze.symbol, style=value_styling)

    if is_context(maze):
        tree = tree.add(maze.symbol, style=context_styling)

        for maze in maze.mazes():
            walk(
                maze,
                tree,
                include_values=include_values,
                value_styling=value_styling,
                context_styling=context_styling
            )

@cli.command()
@click.argument("filepath")
@click.option("-c", "--counts", is_flag=True, help="Annotate symbols with their number of occurrences.")
@click.option("-v", "--values", is_flag=True, help="Display value identifiers in the hierarchy.")
def symbols(filepath, counts, values):
    """Display the symbol hierarchy."""

    for maze in load(filepath=filepath):
        tree = Tree(label=filepath)
        walk(maze, tree, include_values=values)
        print(tree)
