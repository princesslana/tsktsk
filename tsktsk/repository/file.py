import contextlib
import dataclasses
from pathlib import Path
from typing import Any, Dict, Iterator

import yaml
from tsktsk.task import Task

YamlDict = Dict[str, Any]


class FileRepository:
    def __init__(self, path: Path):
        self.path = path

    def add(self, category: str, value: str, effort: str, message: str) -> Task:
        with self.tasks() as tasks:
            key = str(len(tasks) + 1)
            task = Task(key, message, category, value, effort)
            tasks[key] = dataclasses.asdict(task)

        return task

    @contextlib.contextmanager
    def tasks(self) -> Iterator[YamlDict]:
        if not self.path.exists():
            raise FileNotFoundError("No tsktsk repository here")

        with self.path.open(mode="r") as f:
            tasks = yaml.safe_load(f) or {}

        yield tasks

        with self.path.open("w") as f:
            yaml.dump(tasks, f)

    @contextlib.contextmanager
    def task(self, key: str) -> Iterator[Task]:
        with self.tasks() as tasks:
            task = Task(**tasks[key])
            yield task
            tasks[key] = dataclasses.asdict(task)

    def __iter__(self) -> Iterator[Task]:
        with self.tasks() as tasks:
            all_tasks = (Task(**value) for value in tasks.values())

        return (t for t in all_tasks if not t.done)
