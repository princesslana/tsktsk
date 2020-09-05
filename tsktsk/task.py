from __future__ import annotations

import dataclasses
import heapq
from datetime import date, timedelta
from enum import Enum
from itertools import repeat
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


@dataclasses.dataclass
class GraphNode:
    task: Task
    dependencies: List[GraphNode]
    dependents: List[GraphNode]


def max_sum_roi(node: GraphNode):
    task = node.task
    values_sum = sum(
        (dep.task.value_points for dep in node.dependents), task.value_points
    )
    efforts_sum = sum(
        (dep.task.effort_points for dep in node.dependents), task.effort_points
    )
    return max(values_sum / efforts_sum, task.value_points / task.effort_points)


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


def sequential_eta(repo, tasks: List[Task]) -> Iterable[Tuple[Task, Optional[date]]]:
    velocity, remaining = estimate_velocity(repo)
    if velocity == 0:
        yield from zip(tasks, repeat(None))
        return

    cur_date = date.today()
    for task in tasks:
        remaining -= task.effort_points
        while remaining < 0:
            cur_date += timedelta(days=1)
            remaining += velocity
        yield task, cur_date


def estimate_velocity(repo) -> Tuple[float, float]:
    today = date.today()
    start_date = today - timedelta(days=60)

    tasks = repo.tasks_done_between(start_date, today)
    efforts = sum(t.effort_points for t in tasks if t.done != today)
    if efforts == 0:
        return 0, 0

    earliest_date = min(t.done for t in tasks)
    velocity = efforts / (today - earliest_date).days
    used = sum(t.effort_points for t in tasks if t.done == today)

    return velocity, velocity - used
