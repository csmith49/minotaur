from .timer import current_time
from hashids import Hashids
from typing import Union, Optional

# module-level hashid factory, not to be exposed
_FACTORY = Hashids()

def hash(seed : Optional[Union[int, str]] = None) -> str:
    """Construct a hash.

    If provided, uses the optional seed. Otherwise, uses the current time.
    """
    
    if seed:
        return _FACTORY.encode(seed)
    else:
        return _FACTORY.encode(current_time())
