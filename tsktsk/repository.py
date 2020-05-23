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

VALUE = {"high": "V⬆", "medium": "", "low": "V⬇"}
EFFORT = {"high": "E⬆", "medium": "", "low": "E⬇"}
POINTS = {"high": 8, "medium": 5, "low": 3}


class Task:
    def __init__(
        self, key, message, category="NEW", value="medium", effort="medium", done=None
    ):
        self.key = key
        self.message = message
        self.category = category
        self.value = value
        self.effort = effort
        self.done = done

    def asdict(self):
        return {
            "key": self.key,
            "message": self.message,
            "category": self.category,
            "effort": self.effort,
            "value": self.value,
            "done": self.done,
        }

    @property
    def roi(self):
        return POINTS[self.value] / POINTS[self.effort]

    def mark_done(self):
        self.done = datetime.now().strftime("%Y%m%d")

    def __repr__(self):
        return f"Task({self.key}, {self.message}, {self.category}, {self.value}, {self.effort}, {self.done})"

    def __str__(self):
        # 50 chars is the recommended length of a git commit summary
        msg = textwrap.shorten(self.message, width=50)

        # This should be under 80 chars wide, currently 70
        # key:6, space, category:6, space, message:50, space, value:2, space effort 2
        return f"{self.key:>6} {CATEGORY[self.category]}: {msg:50} {VALUE[self.value]:2} {EFFORT[self.effort]:2}".rstrip()


class TaskRepository:
    def __init__(self, tasks):
        self.tasks = tasks

    def add(self, category, value, effort, message):
        key = str(len(self.tasks) + 1)
        task = Task(key, message, category, value, effort)
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
