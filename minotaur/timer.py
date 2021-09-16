from time import perf_counter as current_time

class Timer:
    """Timing context manager that uses the highest-precision clock available (via `time.perf_counter`)."""

    def __slots__ = ("_start", "_stop")

    def __init__(self):
        """Construct (and start) a timer."""

        self._start, self._stop = None
        self.start()

    def start(self) -> 'Timer':
        """Start the timer. Returns the instance."""

        self._start = current_time()
        return self

    def stop(self) -> 'Timer':
        """Stop the timer. Returns the instance."""

        self._stop = current_time()
        return self

    @property
    def elapsed(self) -> int:
        """The time elapsed since the timer was started and either the stop time or now, whichever is earlier."""

        if self._stop is None:
            return current_time() - self._start
        else:
            return self._stop - self._start

    # Context Manager Interface

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()
