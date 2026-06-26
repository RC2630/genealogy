from typing import Final
import re

INPUT_FILE: Final[str] = "files/input.md"
PEOPLE: dict[str, Person] = {}

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
        
    def __repr__(self) -> str:
        return remove_leading_whitespaces(
            f"""{self.name} ({self.gender})
            - parents: {display_people_list(self.parents)}
            - siblings: {display_people_list(self.siblings)}
            - spouse: {self.spouse.name if self.spouse is not None else '(N/A)'}
            - children: {display_people_list(self.children)}"""
        )

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
        return "(N/A)"
    return ", ".join(person.name for person in people)

def display_all() -> None:
    for person in PEOPLE.values():
        print(f"\n{person}")

# ----------------------------------------------------------

if __name__ == "__main__":
    parse_input_file()
    display_all()