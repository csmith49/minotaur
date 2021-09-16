from functools import wraps

class Instrumenter:
    """Interface for constructing linearized threads via a program's call-stack."""

    def __init__(self):
        """Construct an instrumenter."""

        self._logger = None
        self._context_stack = []

    def __enter__(self, *args, **kwargs):
        self.enter_context(*args, **kwargs)
        return self

    def __exit__(self, *_):
        self.exit_context()

    def wrap(self, *args, **kwargs):
        """Wrap a function execution with an instrumentation context."""
        def decorator(callable):
            @wraps(callable)
            def wrapped(*args, **kwargs):
                with self(*args):
                    result = callable(*args, **kwargs)
                return result
            return wrapped
        return decorator


