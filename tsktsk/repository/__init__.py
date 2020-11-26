from datetime import date
from pathlib import Path
from typing import Callable, ContextManager, Iterable, List, Set

from typing_extensions import Protocol

from tsktsk.repository.file import FileRepository  # noqa
from tsktsk.repository.github import GithubRepository  # noqa
from tsktsk.task import Category, Effort, Task, Value


class Repository(Iterable[Task], Protocol):
    def add(
        self,
        cateogry: Category,
        value: Value,
        effort: Effort,
        message: str,
        dependencies: Set[str],
    ) -> Task:
        ...

    # this is more complicated than we'd like because of the typing of @contextlib.contextmanager
    task: Callable[..., ContextManager[Task]]

    def tasks_done_between(self, start: date, end: date) -> List[Task]:
        ...


def create() -> None:
    try:
        Path(".tsktsk").touch(exist_ok=False)
    except FileExistsError:
        raise FileExistsError("Repository already exists")
