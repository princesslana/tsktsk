from pathlib import Path
from typing import Optional

import smalld_click

from tsktsk.config import Config, Env
from tsktsk.repository import FileRepository, GithubRepository, Repository
from tsktsk.repository.auth import find_github_auth


def discover_repository(config: Config, explicit_github: Optional[str]) -> Repository:
    """
    Determine which repository we should fetch tasks from.
    This method should never throw an exception, as some commands do
    not require a repository.

    Discovery priority is:
    1. Use explicitly passed repository
    2. If Discord, use repository configured for that channel
    3. Use repository configured via env vars
    4. Use default file repository
    """

    github_repository = explicit_github

    if not github_repository:
        github_repository = github_from_channel(config)

    if not github_repository:
        github_repository = Env.GITHUB_SINGLE_REPO.get()

    if github_repository:
        return GithubRepository(github_repository, find_github_auth())
    else:
        return FileRepository(Path(".tsktsk"))


def github_from_channel(config: Config) -> Optional[str]:
    conversation = smalld_click.get_conversation()

    if not conversation:
        return None

    channel = next(
        (
            name
            for name, channel_id in config.discord_channels.items()
            if channel_id == conversation.channel_id
        ),
        None,
    )
    return config.github_repositories.get(channel)
