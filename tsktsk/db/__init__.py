import contextlib
import os
import sqlite3
import threading
from typing import Any, Iterable, Iterator, Optional

from pkg_resources import resource_filename
from yoyo import get_backend, read_migrations

from tsktsk.config import Env


def get_path():
    return Env.DB_PATH.get(default="data/tsktsk.sqlite")


@contextlib.contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    with contextlib.closing(sqlite3.connect(get_path())) as conn:
        conn.row_factory = sqlite3.Row
        with conn:
            yield conn


def apply_migrations(path: Optional[str] = None):
    backend = get_backend(f"sqlite:///{path or get_path()}")
    migrations = read_migrations(resource_filename("tsktsk.resources", "migrations"))
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))
