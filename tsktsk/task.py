import dataclasses
import textwrap
from datetime import datetime
from enum import Enum
from typing import Optional, Set


class Category(Enum):
    NEW = "📦 NEW"
    IMP = "👌 IMP"
    FIX = "🐛 FIX"
    DOC = "📖 DOC"
    TST = "✅ TST"

    DEFAULT = NEW


class Value(Enum):
    HIGH = "V⬆"
    MEDIUM = ""
    LOW = "V⬇"

    DEFAULT = MEDIUM


class Effort(Enum):
    HIGH = "E⬆"
    MEDIUM = ""
    LOW = "E⬇"

    DEFAULT = MEDIUM


POINTS = {"HIGH": 8, "MEDIUM": 5, "LOW": 3}


class TaskError(Exception):
    pass


@dataclasses.dataclass
class Task:
    key: str
    message: str
    category: Category = Category.DEFAULT
    value: Value = Value.DEFAULT
    effort: Effort = Effort.DEFAULT
    dependencies: Set[str] = dataclasses.field(default_factory=set)
    done: Optional[str] = None

    @property
    def roi(self) -> float:
        return POINTS[self.value.name] / POINTS[self.effort.name]

    def mark_done(self) -> None:
        if self.done:
            raise TaskError("task is already done")
        self.done = datetime.now().strftime("%Y%m%d")

    def mark_undone(self) -> None:
        if not self.done:
            raise TaskError("task is not done")
        self.done = None

    def add_dependency(self, dependency: "Task"):
        if dependency.key == self.key:
            raise TaskError("task cannot be dependent on itself")
        self.dependencies.add(dependency.key)

    def remove_dependency(self, dependency: "Task"):
        try:
            self.dependencies.remove(dependency.key)
        except KeyError:
            pass

    def __str__(self) -> str:
        # 50 chars is the recommended length of a git commit summary
        msg = textwrap.shorten(self.message, width=50)

        # This should be under 80 chars wide, currently 70
        # key:6, space, category:6, space, message:50, space, value:2, space effort 2
        header = (
            f"{self.key:>6} "
            f"{self.category.value}: "
            f"{msg:50} {self.value.value:2} {self.effort.value:2}".rstrip()
        )

        deps = ""
        if self.dependencies:
            deps = ", ".join(sorted(self.dependencies, key=int))
            # Aligned to the start of the category name and wrapped to 80 chars wide
            first, *rest = textwrap.wrap(deps, width=80 - 13)
            first = f"\n{'🔗 ':>12}{first}"
            second = textwrap.indent("\n".join(rest), " " * 13)
            deps = "\n".join((first, second)).rstrip()

        return "".join([header, deps])
