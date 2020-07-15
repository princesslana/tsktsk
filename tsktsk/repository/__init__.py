from pathlib import Path

from tsktsk.repository.file import FileRepository


def create():
    try:
        Path(".tsktsk").touch(exist_ok=False)

    except FileExistsError:
        raise RepositoryError("Repository already exists")


def load():
    return FileRepository(Path(".tsktsk"))


class RepositoryError(Exception):
    pass
