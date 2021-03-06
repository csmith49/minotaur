from ..message import Enter, Exit, Emit
from ..maze import Identifier

from ..utility.timer import current_time

from logging import Formatter, FileHandler, StreamHandler, getLogger, INFO
from functools import wraps
from typing import Optional, Any, Iterable
from sys import stdout

# Context Manager / Decorator associated with a Minotaur interface object

class MinotaurContextManager:
    """Manages a Minotaur context. Conventiently acts as a Python context manager and decorator."""

    def __init__(self, parent : "Minotaur", symbol : str, result : Optional[str] = None, kwargs : Optional[Iterable[str]] = None):
        """Construct a Minotaur context manager."""
        
        self.parent = parent
        self.symbol = symbol
        self.result = result
        self.kwargs = list(kwargs) if kwargs is not None else ()

    # Utilities for checking kwargs and results

    def emit_kwargs(self, **kwargs):
        """Emit `value` with name `key` if `key=value` is given in `**kwargs` and `key` is defined in `self.kwargs`."""
        for kwarg in self.kwargs:
            try:
                value = kwargs[kwarg]
                self.parent.emit(kwarg, value)
            except KeyError:
                pass

    def emit_result(self, value : Any):
        """Emit the value with name `self.result`, if defined."""
        if self.result is not None:
            self.parent.emit(self.result, value)

    # Context manager interface

    def __enter__(self):
        self.parent.enter(self.symbol)

    def __exit__(self, *_):
        self.parent.exit()

    # Decorator interface

    def decorate(self, callable):
        """Decorate a callable with the context manager."""

        @wraps(callable)
        def wrapper(*args, **kwargs):
            with self:
                self.emit_kwargs(**kwargs)
                result = callable(*args, **kwargs)
                self.emit_result(result)
                return result
        return wrapper

    def __call__(self, callable):
        """Alias for `self.decorate(callable)`."""
        
        return self.decorate(callable)

class Minotaur:
    """Interface for managing contexts and logging Message objects."""
    
    def __init__(self, filepath : Optional[str] = None, verbose : bool = False, root : str = "root"):
        """Construct a Minotaur object."""

        self.logger = getLogger(f"minotaur.{self}")
        self.logger.setLevel(INFO)

        self.filepath = filepath
        self.verbose = verbose
        self.root = root

        # and the formatter
        self.formatter = Formatter(fmt="%(message)s")

        # and set up handlers, if needed
        if filepath is not None:
            self.add_filepath_handler(filepath)

        if verbose:
            self.add_stdout_handler()

        # maintain a context stack for appropriately annotating emitted messages
        self.context_stack = [Identifier(self.root)]

    # Handler additions
    
    def add_filepath_handler(self, filepath : str):
        """Adds a filepath handler to the object-level logger."""

        handler = FileHandler(filepath)
        handler.setLevel(INFO)
        handler.setFormatter(self.formatter)

        self.logger.addHandler(handler)

    def add_stdout_handler(self):
        """Adds a stream handler to the object-level logger."""

        handler = StreamHandler(stream=stdout)
        handler.setLevel(INFO)
        handler.setFormatter(self.formatter)

        self.logger.addHandler(handler)

    # Special Access Functions

    @property
    def current_context(self) -> Identifier:
        """The identifier of the most-recently entered context."""

        return self.context_stack[-1]

    def pop_context(self) -> Identifier:
        """Return the identifier for the most-recently entered context."""
        
        return self.context_stack.pop()

    def push_context(self, context : Identifier):
        """Record the most-recently entered context."""

        self.context_stack.append(context)

    # Context manipulation

    def enter(self, symbol : str):
        """Enter a context with the given symbol."""

        # construct the context identifier
        identifier = Identifier(symbol)

        # emit the appropriate ENTER message
        message = Enter(
            identifier=identifier,
            context=self.current_context,
            timestamp=current_time()
        )
        self.logger.info(message)

        # add the identifier to the context stack
        self.push_context(identifier)

    def exit(self):
        """Exit the current context."""

        # get the exiting context identifier
        identifier = self.pop_context()

        # emit the appropriate EXIT message
        message = Exit(
            identifier=identifier,
            context=self.current_context,
            timestamp=current_time()
        )
        self.logger.info(message)

    # Value observations

    def emit(self, name : str, value : Any):
        """Emit a value in the current context."""

        identifier = Identifier(name)

        message = Emit(
            value=value,
            identifier=identifier,
            context=self.current_context,
            timestamp=current_time()
        )
        self.logger.info(message)

    def __setitem__(self, name : str, value : Any):
        """Alias for `self.emit(name, value)`."""

        self.emit(name, value)

    # Context manager construction
    
    def context(self, symbol : str, result : Optional[str] = None, kwargs : Optional[Iterable[str]] = None):
        return MinotaurContextManager(
            parent=self,
            symbol=symbol,
            result=result,
            kwargs=kwargs
        )

    def __call__(self, *args, **kwargs):
        return self.context(*args, **kwargs)