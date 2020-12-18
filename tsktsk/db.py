import contextlib
import sqlite3
from typing import Any, Iterable, Iterator


class Database:
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row

    def execute(self, sql: str, params: Iterable[Any] = ()) -> None:
        self.connection.execute(sql, params)

    def fetchone(self, sql: str, params: Iterable[Any] = ()) -> Any:
        return self.connection.execute(sql, params).fetchone()

    @contextlib.contextmanager
    def transaction(self) -> Iterator:
        with self.connection:
            yield

    def close(self):
        self.connection.close()
