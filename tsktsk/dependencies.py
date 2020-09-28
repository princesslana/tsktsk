from __future__ import annotations

import dataclasses
import heapq
from typing import Dict, List

from tsktsk.repository import Repository
from tsktsk.task import Task


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


def sort_tasks_by_roi(repo: Repository):
    roots = build_graph({task.key: task for task in repo})

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
