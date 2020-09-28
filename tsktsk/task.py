from __future__ import annotations

import dataclasses
from datetime import date
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
    done: Optional[date] = None

    @property
    def effort_points(self) -> int:
        return POINTS[self.effort.name]

    @property
    def value_points(self) -> int:
        return POINTS[self.value.name]

    def mark_done(self) -> None:
        if self.done:
            raise TaskError("task is already done")
        self.done = date.today()

    def mark_undone(self) -> None:
        if not self.done:
            raise TaskError("task is not done")
        self.done = None

    def add_dependency(self, dependency: Task):
        if self.key == dependency.key or self.key in dependency.dependencies:
            raise TaskError("circular dependencies")
        self.dependencies.add(dependency.key)

    def remove_dependency(self, dependency: Task):
        try:
            self.dependencies.remove(dependency.key)
        except KeyError:
            pass
