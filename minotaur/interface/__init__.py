from .minotaur import Minotaur
from ..yarn import Message

from typing import Iterable
from json import loads

# IO Utility

def messages(filepath : str) -> Iterable[Message]:
    """Load a sequence of messages from the indicated filepath."""

    with open(filepath, "r") as f:
        for line in f.readlines():
            contents = loads(line)
            yield Message.load(contents)