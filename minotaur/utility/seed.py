from hashids import Hashids
from random import randint
from typing import Optional

# initialize hashid conversion process
_HASHID_FACTORY = Hashids()

# seeds are human-readable random values
class Seed:
    """Human-readable random value."""

    def __init__(self, value : Optional[int] = None):
        """Construct a seed."""

        value = value if value else randint(0, 100000)
        self.value = _HASHID_FACTORY.encode(value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"Seed({self.value})"