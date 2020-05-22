import contextlib
import textwrap
from datetime import datetime
from pathlib import Path

import yaml


def create():
    try:
        Path(".tsktsk").touch(exist_ok=False)

    except FileExistsError:
        raise RepositoryError("Repository already exists")


@contextlib.contextmanager
def load():
    path = Path(".tsktsk")

    assert path.exists()

    with path.open(mode="r") as f:
        tasks = yaml.safe_load(f) or {}

    repository = TaskRepository(tasks)

    yield repository

    with path.open("w") as f:
        yaml.dump(repository.tasks, f)


CATEGORY = {
    "NEW": "📦 NEW",
    "IMP": "👌 IMP",
    "FIX": "🐛 FIX",
    "DOC": "📖 DOC",
    "TST": "✅ TST",
}


class Task:
    def __init__(self, key, message, category="NEW", done=None):
        self.key = key
        self.message = message
        self.category = category
        self.done = done

    def asdict(self):
        return {
            "key": self.key,
            "message": self.message,
            "category": self.category,
            "done": self.done,
        }

    def mark_done(self):
        self.done = datetime.now().strftime("%Y%m%d")

    def __repr__(self):
        return f"Task({self.key}, {self.message})"

    def __str__(self):
        msg = textwrap.shorten(self.message, width=50)
        return f"{self.key:>6} {CATEGORY[self.category]}: {msg}"


class TaskRepository:
    def __init__(self, tasks):
        self.tasks = tasks

    def add(self, category, message):
        key = str(len(self.tasks) + 1)
        task = Task(key, message, category)
        self.tasks[key] = task.asdict()
        return task

    def top(self):
        return next(iter(self))

    @contextlib.contextmanager
    def task(self, key):
        task = Task(**self.tasks[key])
        yield task
        self.tasks[key] = task.asdict()

    def __iter__(self):
        return (Task(**value) for value in self.tasks.values())


class RepositoryError(Exception):
    pass
