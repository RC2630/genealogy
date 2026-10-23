from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

import main as g
from four_family_repr import *
from contextlib import redirect_stdout

g.PEOPLE = {"X": g.Person("X", "M"), "Y": g.Person("Y", "F")}

# ----------------------------------------------

def construct_path_element(
    edge_type: Literal["parent", "child"], parent_gender: Literal["M", "F"],
    child_gender: Literal["M", "F"]
) -> tuple[Literal["parent", "child"], Literal["X", "Y"]]:
    if edge_type == "parent":
        return (edge_type, "X" if parent_gender == "M" else "Y")
    else:
        return (edge_type, "X" if child_gender == "M" else "Y")

def common_name(
    repr: Representation, parent_gender: Literal["M", "F"], child_gender: Literal["M", "F"]
) -> str:
    return g.decompose_and_naturalize([
        construct_path_element(edge_type, parent_gender, child_gender)
        for edge_type in repr.to(Path).path
    ], g.AnyPart).replace("half-", "")

def get_names_to_print(repr: Representation) -> str:
    common_names: list[str] = [
        common_name(repr, "M", "M"), common_name(repr, "M", "F"),
        common_name(repr, "F", "M"), common_name(repr, "F", "F")
    ]
    return ", ".join(dict.fromkeys(common_names))

def main(max: int) -> None:
    with open("output.txt", "w") as f:
        for repr in Representation.generate_all(max):
            f.write(f"{type(repr).__name__}: {repr} -> {get_names_to_print(repr)}\n")
    with open("dense_cousin_coords.txt", "w") as f:
        with redirect_stdout(f):
            for coord in ExtendedCousinCoordinates.generate(max):
                coord.display()
                print(f"common name: {get_names_to_print(coord)}")

# ----------------------------------------------

if __name__ == "__main__":
    main(5)