import contextlib

import yaml
from tsktsk.task import Task


class FileRepository:
    def __init__(self, path):
        self.path = path

    def add(self, category, value, effort, message):
        with self.tasks() as tasks:
            key = str(len(tasks) + 1)
            task = Task(key, message, category, value, effort)
            tasks[key] = task.asdict()

        return task

    @contextlib.contextmanager
    def tasks(self):
        if not self.path.exists():
            raise FileNotFoundError("No tsktsk repository here")

        with self.path.open(mode="r") as f:
            tasks = yaml.safe_load(f) or {}

        yield tasks

        with self.path.open("w") as f:
            yaml.dump(tasks, f)

    @contextlib.contextmanager
    def task(self, key):
        with self.tasks() as tasks:
            task = Task(**tasks[key])
            yield task
            tasks[key] = task.asdict()

    def __iter__(self):
        with self.tasks() as tasks:
            all_tasks = (Task(**value) for value in tasks.values())

        return (t for t in all_tasks if not t.done)
