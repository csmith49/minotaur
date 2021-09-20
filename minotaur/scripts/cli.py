import click
from rich import print
from rich.tree import Tree

from ..interface.inspector import yarns, symbol_tree
from ..interface import messages

@click.command()
@click.argument("filepath")
def cli(filepath):
    for yarn in yarns(messages(filepath)):
        tree = symbol_tree(filepath, yarn)
        print(tree)
