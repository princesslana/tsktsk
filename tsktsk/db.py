import os
import sqlite3
import threading
from typing import Any, Iterable

from pkg_resources import resource_filename
from yoyo import get_backend, read_migrations

PATH = os.environ.get("TSKTSK_DB_PATH", "data/tsktsk.sqlite")


class Database:
    def __init__(self, db_path=PATH):
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row

    def execute(self, sql: str, params: Iterable[Any] = ()) -> None:
        self.connection.execute(sql, params)

    def fetchone(self, sql: str, params: Iterable[Any] = ()) -> Any:
        return self.connection.execute(sql, params).fetchone()

    def __enter__(self) -> "Database":
        self.connection.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        self.connection.__exit__(*args, **kwargs)


namespace = threading.local()


def database() -> Database:
    db = getattr(namespace, "db", None)
    if db:
        return namespace.db
    namespace.db = Database()
    return namespace.db


def apply_migrations():
    backend = get_backend(f"sqlite:///{PATH}")
    migrations = read_migrations(resource_filename("tsktsk.resources", "migrations"))
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))
