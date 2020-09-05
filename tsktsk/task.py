from __future__ import annotations

import dataclasses
import heapq
import textwrap
from datetime import date
from enum import Enum
from typing import Dict, Iterable, List, Optional, Set


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


@dataclasses.dataclass
class GraphNode:
    task: Task
    dependencies: List[GraphNode]
    dependents: List[GraphNode]


def max_sum_roi(node: GraphNode):
    task = node.task
    values_sum = sum(
        (POINTS[dep.task.value.name] for dep in node.dependents),
        POINTS[task.value.name],
    )
    efforts_sum = sum(
        (POINTS[dep.task.effort.name] for dep in node.dependents),
        POINTS[task.effort.name],
    )
    task_roi = POINTS[task.value.name] / POINTS[task.effort.name]
    return max(values_sum / efforts_sum, task_roi)


def build_graph(tasks: Dict[str, Task]) -> List[GraphNode]:
    nodes = {}
    roots = []

    def get_node(task):
        node = nodes.get(task.key)
        if not node:
            node = nodes[task.key] = GraphNode(task, [], [])
        return node

    for node in map(get_node, tasks.values()):
        for dep in node.task.dependencies:
            try:
                dependency_node = get_node(tasks[dep])
            except KeyError:
                continue
            node.dependencies.append(dependency_node)
            dependency_node.dependents.append(node)

        if not node.dependencies:
            roots.append(node)

    return roots


def sort_tasks_by_roi(all_tasks: Iterable[Task]):
    roots = build_graph({task.key: task for task in all_tasks})

    sort_key = lambda node: (-max_sum_roi(node), node.task.key)
    available_nodes = [(sort_key(node), node) for node in roots]
    heapq.heapify(available_nodes)

    output = []
    while available_nodes:
        _, node = heapq.heappop(available_nodes)
        output.append(node.task)
        for dependent_node in node.dependents:
            dependent_node.dependencies.remove(node)
            if not dependent_node.dependencies:
                heapq.heappush(
                    available_nodes, (sort_key(dependent_node), dependent_node)
                )

    return output
