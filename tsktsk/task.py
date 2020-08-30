import dataclasses
import heapq
import textwrap
from datetime import datetime
from enum import Enum
from typing import Dict, Iterable, List, Optional, Set, Tuple


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


@dataclasses.dataclass
class GraphNode:
    key: str
    dependencies: List[str]
    dependents: List[str]


def max_sum_roi(tasks: Dict[str, Task], node: GraphNode):
    task = tasks[node.key]
    values_sum = sum(
        (POINTS[tasks[tk].value.name] for tk in node.dependents),
        POINTS[task.value.name],
    )
    efforts_sum = sum(
        (POINTS[tasks[tk].effort.name] for tk in node.dependents),
        POINTS[task.effort.name],
    )
    task_roi = POINTS[task.value.name] / POINTS[task.effort.name]
    return max(values_sum / efforts_sum, task_roi)


Graph = Tuple[List[str], Dict[str, GraphNode]]


def build_graph(tasks: Dict[str, Task]) -> Graph:
    nodes = {}
    roots = []
    default = lambda k: GraphNode(k, [], [])

    for key, task in tasks.items():
        if not task.dependencies:
            roots.append(key)
            nodes.setdefault(key, default(key))
        else:
            node = nodes.setdefault(key, default(key))
            node.dependencies.extend(task.dependencies)
            for dependency in task.dependencies:
                node = nodes.setdefault(dependency, default(dependency))
                node.dependents.append(key)

    return roots, nodes


def sort_by_roi(all_tasks: Iterable[Task]):
    tasks = {task.key: task for task in all_tasks}

    roots, nodes = build_graph(tasks)

    available_tasks = [(-max_sum_roi(tasks, nodes[key]), key) for key in roots]
    heapq.heapify(available_tasks)

    output = []
    while available_tasks:
        _, key = heapq.heappop(available_tasks)
        output.append(tasks[key])
        dependents = nodes[key].dependents
        for dep_key in dependents:
            dependencies = nodes[dep_key].dependencies
            dependencies.remove(key)
            if not dependencies:
                dependent = nodes[dep_key]
                heapq.heappush(
                    available_tasks, (-max_sum_roi(tasks, dependent), dependent.key)
                )

    return output
