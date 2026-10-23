from typing import Literal, override, cast, Any, Callable, Self
from abc import ABC, abstractmethod
from collections.abc import Sequence
from collections import deque
from itertools import groupby

type PathType = list[Literal["parent", "child"]]
type NumberedReprType = tuple[()] | tuple[int] | tuple[int, int]
type CoordinateType = tuple[int, int]
type ConversionFunction = Callable[[Any], Representation]

CONVERSIONS: dict[
    type[Representation],
    Callable[[], dict[type[Representation], ConversionFunction]]
] = {}

# ----------------------------------------------

def register_conversions[T: Representation](
    conversions: Callable[[], dict[type[Representation], ConversionFunction]]
) -> Callable[[type[T]], type[T]]:
    def decorator(repr_type: type[T]) -> type[T]:
        CONVERSIONS[repr_type] = conversions
        return repr_type
    return decorator

# ----------------------------------------------

class Representation(ABC):

    @abstractmethod
    def __repr__(self) -> str:
        ...

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        ...

    @classmethod
    @abstractmethod
    def generate(cls, max: int) -> Sequence[Self]:
        ...

    def find_path(self, destination: type[Representation]) -> list[type[Representation]]:
        frontier: deque[list[type[Representation]]] = deque([[type(self)]])
        visited: set[type[Representation]] = {type(self)}
        while len(frontier) > 0:
            curr_path: list[type[Representation]] = frontier.popleft()
            curr_type: type[Representation] = curr_path[-1]
            if curr_type is destination:
                return curr_path[1:]
            for neighbour_type in CONVERSIONS[curr_type]():
                if neighbour_type not in visited:
                    visited.add(neighbour_type)
                    frontier.append(curr_path + [neighbour_type])
        raise ValueError(f"no path connects {type(self).__name__} to {destination.__name__}")

    def to[T: Representation](self, repr_type: type[T]) -> T:
        curr: Representation = self
        for neighbour_type in self.find_path(repr_type):
            conversion_func: ConversionFunction = CONVERSIONS[type(curr)]()[neighbour_type]
            curr = conversion_func(curr)
        return cast(T, curr)

    def display(self) -> None:
        print()
        for repr_type in CONVERSIONS:
            print(f"{repr_type.__name__}: {self.to(repr_type)}")

    def test(self) -> None:
        for repr_type in CONVERSIONS:
            assert self.to(repr_type).to(type(self)) == self

    @staticmethod
    def generate_all(max: int) -> list[Representation]:
        representations: list[Representation] = []
        for repr_type in CONVERSIONS:
            representations.extend(repr_type.generate(max))
        return representations

# ----------------------------------------------

@register_conversions(lambda: {
    NumberedRepresentation:
        Path.to_numbered_representation
})
class Path(Representation):

    def __init__(self, path: PathType) -> None:
        self.path: PathType = path.copy()

    @override
    def __repr__(self) -> str:
        return str(self.path).replace("'", "")

    @override
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Path):
            return False
        return self.path == other.path

    @override
    @classmethod
    def generate(cls, max: int) -> Sequence[Self]:
        generated: set[tuple[str, ...]] = set()
        result: list[Self] = []
        for i in range(max + 1):
            for j in range(max + 1):
                path_1: list[str] = i * ["parent"] + j * ["child"]
                path_2: list[str] = i * ["child"] + j * ["parent"]
                if tuple(path_1) not in generated:
                    result.append(cls(cast(PathType, path_1)))
                    generated.add(tuple(path_1))
                if tuple(path_2) not in generated:
                    result.append(cls(cast(PathType, path_2)))
                    generated.add(tuple(path_2))
        return result

    def to_numbered_representation(self) -> NumberedRepresentation:
        repr: list[int] = []
        for edge_type, group in groupby(self.path):
            if edge_type == "parent":
                repr.append(len(list(group)))
            else:
                repr.append(-len(list(group)))
        repr_t: tuple[int, ...] = tuple(repr)
        assert len(repr_t) <= 2
        return NumberedRepresentation(repr_t)

# ----------------------------------------------

@register_conversions(lambda: {
    Path:
        NumberedRepresentation.to_path,
    GenerationsToSharedPointCoordinates:
        NumberedRepresentation.to_generations_to_shared_point_coordinates
})
class NumberedRepresentation(Representation):

    def __init__(self, repr: NumberedReprType) -> None:
        self.repr: NumberedReprType = repr

    @override
    def __repr__(self) -> str:
        return str(self.repr).replace(",)", ")")

    @override
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, NumberedRepresentation):
            return False
        return self.repr == other.repr

    @override
    @classmethod
    def generate(cls, max: int) -> Sequence[Self]:
        result: list[Self] = [cls(())]
        for i in range(-max, max + 1):
            if i != 0:
                result.append(cls((i,)))
        for i in range(1, max + 1):
            for j in range(1, max + 1):
                result.append(cls((i, -j)))
                result.append(cls((-i, j)))
        return result

    def to_path(self) -> Path:
        path: list[str] = []
        for n in self.repr:
            if n < 0:
                path.extend(-n * ["child"])
            else:
                path.extend(n * ["parent"])
        return Path(cast(PathType, path))

    def to_generations_to_shared_point_coordinates(self) -> GenerationsToSharedPointCoordinates:
        if len(self.repr) == 0:
            return GenerationsToSharedPointCoordinates((0, 0))
        elif len(self.repr) == 1:
            x: int = self.repr[0]
            return GenerationsToSharedPointCoordinates((x, 0) if x > 0 else (0, -x))
        else:
            x, y = self.repr
            return GenerationsToSharedPointCoordinates((x, -y))

# ----------------------------------------------

@register_conversions(lambda: {
    NumberedRepresentation:
        GenerationsToSharedPointCoordinates.to_numbered_representation,
    ExtendedCousinCoordinates:
        GenerationsToSharedPointCoordinates.to_extended_cousin_coordinates
})
class GenerationsToSharedPointCoordinates(Representation):

    def __init__(self, coordinates: CoordinateType) -> None:
        self.coordinates: CoordinateType = coordinates

    @override
    def __repr__(self) -> str:
        return str(self.coordinates)

    @override
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, GenerationsToSharedPointCoordinates):
            return False
        return self.coordinates == other.coordinates

    @override
    @classmethod
    def generate(cls, max: int) -> Sequence[Self]:
        result: list[Self] = []
        for i in range(max + 1):
            for j in range(max + 1):
                result.append(cls((i, j)))
                if i != 0 and j != 0:
                    result.append(cls((-i, -j)))
        return result

    def to_numbered_representation(self) -> NumberedRepresentation:
        a, b = self.coordinates
        if (a, b) == (0, 0):
            return NumberedRepresentation(())
        elif b == 0:
            return NumberedRepresentation((a,))
        elif a == 0:
            return NumberedRepresentation((-b,))
        else:
            return NumberedRepresentation((a, -b))

    def to_extended_cousin_coordinates(self) -> ExtendedCousinCoordinates:
        a, b = self.coordinates
        if a >= 0 and b >= 0:
            return ExtendedCousinCoordinates((min(a, b) - 1, a - b))
        else:
            return ExtendedCousinCoordinates((max(a, b) - 1, a - b))

# ----------------------------------------------

@register_conversions(lambda: {
    GenerationsToSharedPointCoordinates:
        ExtendedCousinCoordinates.to_generations_to_shared_point_coordinates
})
class ExtendedCousinCoordinates(Representation):

    def __init__(self, coordinates: CoordinateType) -> None:
        self.coordinates: CoordinateType = coordinates

    @override
    def __repr__(self) -> str:
        return str(self.coordinates)

    @override
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ExtendedCousinCoordinates):
            return False
        return self.coordinates == other.coordinates

    @override
    @classmethod
    def generate(cls, max: int) -> Sequence[Self]:
        result: list[Self] = []
        for n in range(-max, max + 1):
            for k in range(-max, max + 1):
                result.append(cls((n, k)))
        return result

    def to_generations_to_shared_point_coordinates(self) -> GenerationsToSharedPointCoordinates:
        n, k = self.coordinates
        if n >= -1:
            return GenerationsToSharedPointCoordinates((n + 1 + max(0, k), n + 1 + max(0, -k)))
        else:
            return GenerationsToSharedPointCoordinates((n + 1 - max(0, -k), n + 1 - max(0, k)))

# ----------------------------------------------

def main(max: int) -> None:
    with open("output.txt", "w") as f:
        for test_case in Representation.generate_all(max):
            f.write(f"{type(test_case).__name__}: {test_case}\n")
            test_case.test()
    print("\nAll tests passed!")
    
# ----------------------------------------------

if __name__ == "__main__":
    main(5)