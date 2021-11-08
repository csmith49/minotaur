from ..maze import Identifier, Maze
from typing import Generic, TypeVar, Mapping, Tuple, Iterable, Optional, Callable, Any

# Many of the constructions here are polymorphic wrt the result

T = TypeVar("T")

# Context Maps are an intermediate result in a catamorphism

class ContextMap(Generic[T]):
    """Maps a list of contexts to a list of results."""

    def __init__(self, map : Mapping[Identifier, T]):
        """Construct a context map."""

        self.map = map

    # Accessors

    def values(self, symbol : Optional[str] = None) -> Iterable[T]:
        """Yield all results in the map, optionally filtering by the provided symbol."""

        for context, result in self.map.items():
            if symbol is None or context.symbol == symbol:
                yield result

    def symbols(self) -> Iterable[str]:
        """Yield all unique symbols appearing in the map."""

        symbols = set([context.symbol for context in self.map.keys()])
        yield from symbols

    def result(self, context : Identifier) -> T:
        """Return the result associated with a specific context identifier."""

        return self.map[context]

    # Dunder methods for easier interfacing

    def __iter__(self) -> Iterable[T]:
        return self.values()

    def __getitem__(self, symbol : str) -> Iterable[T]:
        return self.values(symbol)

# Algebras are a synonym and construction tool for the functions catamorphisms evaluate

class AlgebraError(Exception):
    def __init__(self, message : str):
        self.message = message

    def __str__(self):
        return self.message

class Algebra(Generic[T]):
    def __init__(self,
        functor : Optional[Callable[[str, Mapping[str, Any], ContextMap[T]], T]] = None,
        cases : Mapping[str, Callable[[Mapping[str, Any], ContextMap[T]], T]] = {}
    ):
        """Construct an algebra from a single functor and/or a set of functors selected by the active symbol."""

        self.functor = functor
        self.cases = cases

    def evaluate(self, symbol : str, values : Mapping[str, Any], contexts : ContextMap[T]) -> T:
        """Evaluate the algebra."""

        try:
            return self.switch[symbol](values, contexts)
        except KeyError:
            if self.functor:
                return self.functor(symbol, values, contexts)
            else:
                raise AlgebraError(f"No evaluation functor suitable for symbol {symbol}.")

    def __call__(self, symbol : str, values : Mapping[str, Any], contexts : ContextMap[T]) -> T:
        """Dunder alias for `self.evaluate(...)`."""

        return self.evaluate(symbol, values, contexts)

class ProductAlgebra(Algebra[Tuple]):
    """Given algebras A_1, ..., A_k, the product algebra evaluates the functor product (A_1, ..., A_k)."""

    def __init__(self, *algebras : Algebra):
        """Construct a product algebra from a finite set of independent algebras."""

        self.algebras = algebras

    def project(self, contexts : ContextMap) -> Tuple[ContextMap]:
        """Map a context map of tuples to a tuple of context maps."""

        mappings = (dict(zip(contexts.map, values)) for values in zip(*contexts.map.values()))
        contexts = (ContextMap(mapping) for mapping in mappings)
        return tuple(contexts)

    def evaluate(self, symbol : str, values : Mapping[str, Any], contexts : ContextMap) -> Tuple:
        """Evaluate the algebra."""

        projections = zip(self.algebras, self.project(contexts))
        results = (algebra(symbol, values, contexts) for algebra, contexts in projections)
        return tuple(results)

# Catamorphisms collapse Yarn objects from the bottom-up

class Catamorphism(Generic[T]):
    """Catamorphism objects are functors from Yarns to T's."""

    def __init__(self, algebra : Algebra[T]):
        """Construct a catamorphism from an algebra."""

        self.algebra = algebra

    # Evaluation

    def evaluate(self, yarn : Maze) -> T:
        """Simple recursive evaluation of a Yarn object in the catamorphism."""

        # build value map (w/special value duration)
        values = {value.name : value.value for value in yarn.values}
        values["duration"] = yarn.duration

        # build context map <- where all the recursion happens
        context_map = {context.identifier : self.evaluate(context) for context in yarn.contexts}

        # and evaluate the current level
        return self.algebra(yarn.symbol, values, context_map)

    # Dunder methods for easier interfacing

    def __call__(self, yarn : Maze) -> T:
        """Alias for `self.evaluate(...)`."""

        return self.evaluate(yarn)