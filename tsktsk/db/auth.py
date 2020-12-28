import dataclasses
from typing import Optional

from tsktsk.db import connection


@dataclasses.dataclass
class GithubAuth:
    username: str
    token: str


def add_or_update(discord_id: str, auth: GithubAuth):
    with connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO github_auth(discord_id, username, token) VALUES (?, ?, ?)",
            (discord_id, auth.username, auth.token),
        )


def find(discord_id: str) -> Optional[GithubAuth]:
    with connection() as conn:
        row = conn.execute(
            "SELECT username, token FROM github_auth WHERE discord_id = ?",
            (discord_id,),
        ).fetchone()
        return GithubAuth(row[0], row[1]) if row is not None else None
