from typing import Literal, override, cast, Any, Callable
from abc import ABC, abstractmethod
from itertools import groupby

type PathType = list[Literal["parent", "child"]]
type NumberedReprType = tuple[()] | tuple[int] | tuple[int, int]
type CoordinateType = tuple[int, int]
type ConversionFunction = Callable[[Any], Representation]

# ----------------------------------------------

class Representation(ABC):

    @abstractmethod
    def __repr__(self) -> str:
        ...

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        ...

    @abstractmethod
    def to_path(self) -> Path:
        ...

    @abstractmethod
    def to_numbered_representation(self) -> NumberedRepresentation:
        ...

    @abstractmethod
    def to_generations_to_shared_point_coordinates(self) -> GenerationsToSharedPointCoordinates:
        ...

    @abstractmethod
    def to_extended_cousin_coordinates(self) -> ExtendedCousinCoordinates:
        ...

    def to(self, repr_type: type[Representation]) -> Representation:
        if repr_type is Path:
            return self.to_path()
        elif repr_type is NumberedRepresentation:
            return self.to_numbered_representation()
        elif repr_type is GenerationsToSharedPointCoordinates:
            return self.to_generations_to_shared_point_coordinates()
        elif repr_type is ExtendedCousinCoordinates:
            return self.to_extended_cousin_coordinates()
        else:
            raise ValueError("unsupported repr_type")

    def display(self) -> None:
        print(
            f"\npath: {self.to_path()}"
            f"\nnumbered representation: {self.to_numbered_representation()}"
            f"\ngenerations to shared point coordinates: "
            f"{self.to_generations_to_shared_point_coordinates()}"
            f"\nextended cousin coordinates: {self.to_extended_cousin_coordinates()}"
        )

    def test(self) -> None:
        assert self.to_path().to(type(self)) == self
        assert self.to_numbered_representation().to(type(self)) == self
        assert self.to_generations_to_shared_point_coordinates().to(type(self)) == self
        assert self.to_extended_cousin_coordinates().to(type(self)) == self

# ----------------------------------------------

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
    def to_path(self) -> Path:
        return Path(self.path)

    @override
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

    @override
    def to_generations_to_shared_point_coordinates(self) -> GenerationsToSharedPointCoordinates:
        return self.to_numbered_representation().to_generations_to_shared_point_coordinates()

    @override
    def to_extended_cousin_coordinates(self) -> ExtendedCousinCoordinates:
        return self.to_generations_to_shared_point_coordinates().to_extended_cousin_coordinates()

# ----------------------------------------------

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
    def to_path(self) -> Path:
        path: list[str] = []
        for n in self.repr:
            if n < 0:
                path.extend(-n * ["child"])
            else:
                path.extend(n * ["parent"])
        return Path(cast(PathType, path))

    @override
    def to_numbered_representation(self) -> NumberedRepresentation:
        return NumberedRepresentation(self.repr)

    @override
    def to_generations_to_shared_point_coordinates(self) -> GenerationsToSharedPointCoordinates:
        if len(self.repr) == 0:
            return GenerationsToSharedPointCoordinates((0, 0))
        elif len(self.repr) == 1:
            x: int = self.repr[0]
            return GenerationsToSharedPointCoordinates((x, 0) if x > 0 else (0, -x))
        else:
            x, y = self.repr
            return GenerationsToSharedPointCoordinates((x, -y))

    @override
    def to_extended_cousin_coordinates(self) -> ExtendedCousinCoordinates:
        return self.to_generations_to_shared_point_coordinates().to_extended_cousin_coordinates()

# ----------------------------------------------

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
    def to_path(self) -> Path:
        return self.to_numbered_representation().to_path()

    @override
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

    @override
    def to_generations_to_shared_point_coordinates(self) -> GenerationsToSharedPointCoordinates:
        return GenerationsToSharedPointCoordinates(self.coordinates)

    @override
    def to_extended_cousin_coordinates(self) -> ExtendedCousinCoordinates:
        a, b = self.coordinates
        if a >= 0 and b >= 0:
            return ExtendedCousinCoordinates((min(a, b) - 1, a - b))
        else:
            return ExtendedCousinCoordinates((max(a, b) - 1, a - b))

# ----------------------------------------------

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
    def to_path(self) -> Path:
        return self.to_numbered_representation().to_path()

    @override
    def to_numbered_representation(self) -> NumberedRepresentation:
        return self.to_generations_to_shared_point_coordinates().to_numbered_representation()

    @override
    def to_generations_to_shared_point_coordinates(self) -> GenerationsToSharedPointCoordinates:
        n, k = self.coordinates
        if n >= -1:
            return GenerationsToSharedPointCoordinates((n + 1 + max(0, k), n + 1 + max(0, -k)))
        else:
            return GenerationsToSharedPointCoordinates((n + 1 - max(0, -k), n + 1 - max(0, k)))

    @override
    def to_extended_cousin_coordinates(self) -> ExtendedCousinCoordinates:
        return ExtendedCousinCoordinates(self.coordinates)

# ----------------------------------------------

def generate_paths(max: int) -> list[Path]:
    generated: set[tuple[str, ...]] = set()
    result: list[Path] = []
    for i in range(max + 1):
        for j in range(max + 1):
            path_1: list[str] = i * ["parent"] + j * ["child"]
            path_2: list[str] = i * ["child"] + j * ["parent"]
            if tuple(path_1) not in generated:
                result.append(Path(cast(PathType, path_1)))
                generated.add(tuple(path_1))
            if tuple(path_2) not in generated:
                result.append(Path(cast(PathType, path_2)))
                generated.add(tuple(path_2))
    return result

def generate_numbered_reprs(max: int) -> list[NumberedRepresentation]:
    result: list[NumberedRepresentation] = [NumberedRepresentation(())]
    for i in range(-max, max + 1):
        if i != 0:
            result.append(NumberedRepresentation((i,)))
    for i in range(1, max + 1):
        for j in range(1, max + 1):
            result.append(NumberedRepresentation((i, -j)))
            result.append(NumberedRepresentation((-i, j)))
    return result

def generate_gen_to_shared_point_coords(max: int) -> list[GenerationsToSharedPointCoordinates]:
    result: list[GenerationsToSharedPointCoordinates] = []
    for i in range(max + 1):
        for j in range(max + 1):
            result.append(GenerationsToSharedPointCoordinates((i, j)))
            if i != 0 and j != 0:
                result.append(GenerationsToSharedPointCoordinates((-i, -j)))
    return result

def generate_cousin_coords(max: int) -> list[ExtendedCousinCoordinates]:
    result: list[ExtendedCousinCoordinates] = []
    for n in range(-max, max + 1):
        for k in range(-max, max + 1):
            result.append(ExtendedCousinCoordinates((n, k)))
    return result

def generate_all(max: int) -> list[Representation]:
    representations: list[Representation] = []
    representations.extend(generate_paths(max))
    representations.extend(generate_numbered_reprs(max))
    representations.extend(generate_gen_to_shared_point_coords(max))
    representations.extend(generate_cousin_coords(max))
    return representations

def main(max: int) -> None:
    with open("output.txt", "w") as f:
        for test_case in generate_all(max):
            f.write(f"{type(test_case).__name__}: {test_case}\n")
            test_case.test()
    print("\nAll tests passed!")
    
# ----------------------------------------------

if __name__ == "__main__":
    main(5)