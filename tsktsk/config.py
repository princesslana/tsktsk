import os
from enum import Enum
from typing import Dict, Iterable, List, Optional


class Env(Enum):
    GITHUB_USERNAME = "TSKTSK_GITHUB_USERNAME"
    GITHUB_TOKEN = "TSKTSK_GITHUB_TOKEN"
    GITHUB_APP_CLIENT_ID = "TSKTSK_GITHUB_CLIENT_ID"

    def get(self, default: Optional[str] = None) -> Optional[str]:
        return os.environ.get(self.value, default)


def split_tuple_list(var: str) -> Iterable[List[str]]:
    return (s.split(":") for s in os.environ.get(var, "").split(","))


def dict_from_env(var: str) -> Dict[str, str]:
    return {d[0]: d[1] for d in split_tuple_list(var)}


class Config:
    @property
    def single_github_repository(self) -> Optional[str]:
        return os.environ.get("TSKTSK_GITHUB_REPO")

    @property
    def discord_channels(self) -> Dict[str, str]:
        return dict_from_env("TSKTSK_DISCORD_CHANNELS")

    @property
    def github_repositories(self) -> Dict[str, str]:
        return dict_from_env("TSKTSK_GITHUB_REPOS")
