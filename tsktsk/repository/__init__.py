import os
from pathlib import Path

from tsktsk.repository.file import FileRepository
from tsktsk.repository.github import GithubRepository


def create():
    try:
        Path(".tsktsk").touch(exist_ok=False)
    except FileExistsError:
        raise FileExistsError("Repository already exists")


def load():
    try:
        return GithubRepository(os.environ["TSKTSK_GITHUB_REPO"])
    except KeyError:
        return FileRepository(Path(".tsktsk"))
