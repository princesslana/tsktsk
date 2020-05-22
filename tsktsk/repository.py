import contextlib
import yaml

from pathlib import Path


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

class Task:
    def __init__(self, key, message):
        self.key = key
        self.message = message

    def asdict(self):
        return {
            "key" : self.key,
            "message" : self.message
        }

    def __repr__(self):
        return f"Task({self.key}, {self.message})"

    def __str__(self):
        return f"{self.key:>6} {self.message}"

class TaskRepository:
    def __init__(self, tasks):
        self.tasks = tasks

    def add(self, message):
        key = str(len(self.tasks) + 1)
        task = Task(key, message)
        self.tasks[key] = task.asdict()
        return task

    def top(self):
        return next(iter(self))

    def __iter__(self):
        return (Task(**value) for value in self.tasks.values())



class RepositoryError(Exception):
    pass

