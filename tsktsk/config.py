import dataclasses
import os
from typing import Dict, Iterable, Optional, Tuple


@dataclasses.dataclass
class GithubAuth:
    username: str
    token: str


def split_tuple_list(var: str) -> Iterable[Tuple[str]]:
    return (tuple(s.split(":")) for s in os.environ.get(var, "").split(","))


def dict_from_env(var: str) -> Dict[str, str]:
    return {d[0]: d[1] for d in split_tuple_list(var)}


class Config:
    @property
    def single_github_repository(self) -> Optional[str]:
        return os.environ.get("TSKTSK_GITHUB_REPO")

    @property
    def single_github_auth(self) -> Optional[GithubAuth]:
        username = os.environ.get("TSKTSK_GITHUB_USERNAME")
        token = os.environ.get("TSKTSK_GITHUB_TOKEN")

        if username and not token:
            raise ValueError("Github username provided, but no token")

        if token and not username:
            raise ValueError("Github token provided, but no username")

        if not username and not token:
            return None

        return GithubAuth(username, token)

    @property
    def discord_users(self) -> Dict[str, str]:
        return dict_from_env("TSKTSK_DISCORD_USERS")

    @property
    def discord_channels(self) -> Dict[str, str]:
        return dict_from_env("TSKTSK_DISCORD_CHANNELS")

    @property
    def github_users(self) -> Dict[str, GithubAuth]:
        return {
            u[0]: GithubAuth(*u[1:]) for u in split_tuple_list("TSKTSK_GITHUB_USERS")
        }

    @property
    def github_repositories(self) -> Dict[str, str]:
        return dict_from_env("TSKTSK_GITHUB_REPOS")
