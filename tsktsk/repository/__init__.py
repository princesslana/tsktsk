import os
from pathlib import Path
from typing import Callable, ContextManager, Iterable

from typing_extensions import Protocol

from tsktsk.repository.file import FileRepository
from tsktsk.repository.github import GithubRepository
from tsktsk.task import Task


class Repository(Iterable[Task], Protocol):
    def add(self, cateogry: str, value: str, effort: str, message: str) -> Task:
        ...

    # this is more complicated than we'd like because of the typing of @contextlib.contextmanager
    task: Callable[..., ContextManager[Task]]


def create() -> None:
    try:
        Path(".tsktsk").touch(exist_ok=False)
    except FileExistsError:
        raise FileExistsError("Repository already exists")


def load() -> Repository:
    try:
        return GithubRepository(os.environ["TSKTSK_GITHUB_REPO"])
    except KeyError:
        return FileRepository(Path(".tsktsk"))
