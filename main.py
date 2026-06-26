from typing import Final
import re
from sys import argv
from collections import deque
from helpers.ansi_codes import green, blue, red

INPUT_FILE: Final[str] = "files/input.md"
PEOPLE: dict[str, Person] = {}

GENDERED_TERMS: dict[tuple[str, str], str] = {
    ("parent", "M"): "father", ("parent", "F"): "mother",
    ("child", "M"): "son", ("child", "F"): "daughter",
    ("sibling", "M"): "brother", ("sibling", "F"): "sister",
    ("spouse", "M"): "husband", ("spouse", "F"): "wife"
}

NUMBERED_REPRESENTATIONS: dict[str, list[int]] = {
    "parent": [1], "child": [-1], "sibling": [1, -1], "spouse": [-1, 1]
}

type Path = list[tuple[str, str]]

# ----------------------------------------------------------

class Person:

    def __init__(self, name: str, gender: str) -> None:
        self.name: str = name
        self.gender: str = gender
        self.siblings: list[Person] = []
        self.parents: list[Person] = []
        self.children: list[Person] = []
        self.spouse: Person | None = None

    def add_relative(self, type: str, name: str) -> None:
        if type == "child":
            self.children.append(PEOPLE[name])
            PEOPLE[name].parents.append(self)
        elif type == "sibling":
            self.siblings.append(PEOPLE[name])
            PEOPLE[name].siblings.append(self)
        elif type == "parent":
            self.parents.append(PEOPLE[name])
            PEOPLE[name].children.append(self)
        elif type == "spouse":
            if self.spouse is not None or PEOPLE[name].spouse is not None:
                raise ValueError("at least 1 member of this couple already has a spouse")
            self.spouse = PEOPLE[name]
            PEOPLE[name].spouse = self
        else:
            raise ValueError("invalid relative type")
        
    def get_gen(self) -> int:
        path: Path | None = self.find(list(PEOPLE.items())[0][1])
        assert path is not None
        return generational_difference(path)
        
    def __repr__(self) -> str:
        return remove_leading_whitespaces(
            f"""{green(self.name)} ({blue(self.gender)}, gen {blue(str(self.get_gen()))})
            - {blue('parents:')} {display_people_list(self.parents)}
            - {blue('siblings:')} {display_people_list(self.siblings)}
            - {blue('spouse:')} {green(self.spouse.name) if self.spouse else red('(N/A)')}
            - {blue('children:')} {display_people_list(self.children)}"""
        )
    
    def find(self, other: Person) -> Path | None:
        frontier: deque[tuple[Person, Path]] = deque([(self, [])])
        already_appended: set[str] = {self.name}
        while len(frontier) > 0:
            curr_person, curr_path = frontier.popleft()
            if curr_person.name == other.name:
                return curr_path
            if (spouse := curr_person.spouse) is not None:
                if spouse.name not in already_appended:
                    frontier.append((spouse, curr_path + [("spouse", spouse.name)]))
                    already_appended.add(spouse.name)
            for child in curr_person.children:
                if child.name not in already_appended:
                    frontier.append((child, curr_path + [("child", child.name)]))
                    already_appended.add(child.name)
            for parent in curr_person.parents:
                if parent.name not in already_appended:
                    frontier.append((parent, curr_path + [("parent", parent.name)]))
                    already_appended.add(parent.name)
            for sibling in curr_person.siblings:
                if sibling.name not in already_appended:
                    frontier.append((sibling, curr_path + [("sibling", sibling.name)]))
                    already_appended.add(sibling.name)
        return None

# ----------------------------------------------------------

def parse_input_file() -> None:
    
    with open(INPUT_FILE, "r", encoding = "utf-8") as f:
        lines: list[str] = f.read().split("\n")

    current_person: Person | None = None
    for line in lines:
        if line == "":
            current_person = None
        elif not line.startswith("- "):
            if m := re.match(r"(.+) \((.)\)", line):
                p = Person(name = m.group(1), gender = m.group(2))
                PEOPLE[m.group(1)] = p
                current_person = p
            else:
                raise ValueError("new person entry: format error")
        else:
            if m := re.match(r"- (.+): (.+)", line):
                assert current_person is not None
                current_person.add_relative(type = m.group(1), name = m.group(2))
            else:
                raise ValueError("relative entry: format error")

# ----------------------------------------------------------

def remove_leading_whitespaces(s: str) -> str:
    return "\n".join([line.lstrip() for line in s.split("\n")])

def display_people_list(people: list[Person]) -> str:
    if len(people) == 0:
        return red("(N/A)")
    return ", ".join(green(person.name) for person in people)

def reverse_path(path: Path, start: str) -> Path:
    reverse_mapping: dict[str, str] = {"child": "parent", "parent": "child"}
    relationships: list[str] = [reverse_mapping.get(rel, rel) for rel, name in reversed(path)]
    names: list[str] = [name for rel, name in reversed(path)][1:] + [start]
    return list(zip(relationships, names))

def display_all() -> None:
    for person in PEOPLE.values():
        print(f"\n{person}")

def find_chain() -> None:
    name_1: str = input("\nEnter name of person 1: ")
    name_2: str = input("Enter name of person 2: ")
    person_1: Person = PEOPLE[name_1]
    person_2: Person = PEOPLE[name_2]
    chain: Path | None = person_1.find(person_2)
    if chain is None:
        print("\nThere is no chain of relationships connecting these two people.")
        return
    print(f"\nChain of relationships from {green(name_1)} to {green(name_2)}:")
    display_full_chain_info(chain)
    print(f"\nChain of relationships from {green(name_2)} to {green(name_1)}:")
    display_full_chain_info(reverse_path(chain, name_1))

def get_gendered(rel: str, name: str) -> str:
    return GENDERED_TERMS[(rel, PEOPLE[name].gender)]
            
# ----------------------------------------------------------

def ungendered_with_names(chain: Path) -> str:
    return " -> ".join(f"{red(rel)} ({green(name)})" for rel, name in chain)

def ungendered_without_names(chain: Path) -> str:
    return " -> ".join(red(rel) for rel, name in chain)

def gendered_with_names(chain: Path) -> str:
    return " -> ".join(f"{red(get_gendered(rel, name))} ({green(name)})" for rel, name in chain)

def gendered_without_names(chain: Path) -> str:
    return " -> ".join(red(get_gendered(rel, name)) for rel, name in chain)

def numbered_representation(chain: Path) -> list[int]:
    numbered_repr: list[int] = []
    for rel, name in chain:
        curr_repr: list[int] = NUMBERED_REPRESENTATIONS[rel]
        if len(numbered_repr) == 0 or numbered_repr[-1] * curr_repr[0] < 0:
            numbered_repr += curr_repr
        else:
            numbered_repr[-1] += curr_repr[0]
            numbered_repr += curr_repr[1:]
    return numbered_repr

def common_name(chain: Path) -> str:
    return red("(TO BE IMPLEMENTED)")

def generational_difference(chain: Path) -> int:
    return sum(numbered_representation(chain))

def distance(chain: Path) -> int:
    return len(chain)

def display_full_chain_info(chain: Path) -> None:
    print(remove_leading_whitespaces(
        f"""{blue('Ungendered chain with names:')} {ungendered_with_names(chain)}
        {blue('Ungendered chain without names:')} {ungendered_without_names(chain)}
        {blue('Gendered chain with names:')} {gendered_with_names(chain)}
        {blue('Gendered chain without names:')} {gendered_without_names(chain)}
        {blue('Numbered representation:')} {numbered_representation(chain)}
        {blue('Common name:')} {common_name(chain)}
        {blue('Generational difference:')} {generational_difference(chain)}
        {blue('Distance:')} {distance(chain)}"""
    ))

# ----------------------------------------------------------

def run_program() -> None:

    if len(argv) == 1:
        print("\nUSAGE: `python main.py <OPTION>`\n"
              "\nOPTIONS:"
              "\nd: display all people and their immediate relationships"
              "\nf: find the chain of relationships between two people")
        return

    parse_input_file()
    option: str = argv[1]

    if option == "d":
        display_all()
    elif option == "f":
        find_chain()
    else:
        raise ValueError("invalid option")

# ----------------------------------------------------------

if __name__ == "__main__":
    run_program()