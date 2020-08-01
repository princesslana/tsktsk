import os
from pathlib import Path
from typing import Any, Callable, Optional

import click

import smalld_click
import tsktsk
from dotenv import load_dotenv
from tsktsk.config import Config, GithubAuth
from tsktsk.repository import FileRepository, GithubRepository, Repository


def find_github_auth(config: Config) -> Optional[GithubAuth]:
    conversation = smalld_click.get_conversation()
    if conversation:
        user = next(
            (
                name
                for name, user_id in config.discord_users.items()
                if user_id == conversation.user_id
            ),
            None,
        )
        return config.github_users.get(user)
    else:
        return config.single_github_auth


def find_github_repository(config: Config) -> Optional[str]:
    conversation = smalld_click.get_conversation()
    if conversation:
        channel = next(
            (
                name
                for name, channel_id in config.discord_channels.items()
                if channel_id == conversation.channel_id
            ),
            None,
        )
        return config.github_repositories.get(channel, config.single_github_repository)
    else:
        return config.single_github_repository


@click.group("tsktsk")
@click.version_option(version=tsktsk.__version__, message="%(version)s")
@click.option("--github", default=None, help="Manage issues in a github repository.")
def root(github: Optional[str]) -> None:
    load_dotenv(Path(".env"))

    if github:
        os.environ["TSKTSK_GITHUB_REPO"] = github

    config = Config()

    tasks = FileRepository(Path(".tsktsk"))

    github_repository = find_github_repository(config)
    if github_repository:
        tasks = GithubRepository(github_repository, find_github_auth(config))

    click.get_current_context().obj = tasks


def tasks() -> Repository:
    return click.get_current_context().obj


estimate = click.Choice(["high", "medium", "low"], case_sensitive=False)


def task_add(category: str, help: str) -> Callable[..., None]:
    long_help = f"""
        {help}

        Uses MESSAGE as a description of this task.

        An estimate of value gained and effort required to complete this task may
        also be added. These estimates are used to order the tasks, such that the
        tasks with the highest value:effort ratio are ordered first. If not
        specified, it defaults to medium/medium.
        """

    @root.command(category.lower(), help=long_help)
    @click.option(
        "--value",
        type=estimate,
        default="medium",
        help="Value gained by completing this task.",
    )
    @click.option(
        "--effort",
        type=estimate,
        default="medium",
        help="Effort required to complete this task.",
    )
    @click.argument("message", nargs=-1, required=True)
    def f(*args: Any, **kwargs: Any) -> None:
        add(category, *args, **kwargs)

    return f


new = task_add("NEW", "Create a task to add something new.")
imp = task_add("IMP", "Create a task to improve something existing.")
fix = task_add("FIX", "Create a task to fix a bug.")
doc = task_add("DOC", "Create a task to improve documentation.")
tst = task_add("TST", "Create a task related to testing.")


def add(category: str, value: str, effort: str, message: str) -> None:
    click.echo(tasks().add(category, value, effort, " ".join(message)))


@root.command()
@click.option(
    "--category",
    type=click.Choice(["NEW", "IMP", "FIX", "DOC", "TST"], case_sensitive=False),
    help="Category of this task.",
)
@click.option("--value", type=estimate, help="Value gained by completing this task.")
@click.option("--effort", type=estimate, help="Effort required to complete this task.")
@click.argument("key", nargs=1)
@click.argument("message", nargs=-1)
def edit(
    category: Optional[str],
    value: Optional[str],
    effort: Optional[str],
    key: Optional[str],
    message: Optional[str],
) -> None:
    "Edit an existing task. KEY specifies which task."

    with tasks().task(key) as t:
        if category:
            t.category = category

        if value:
            t.value = value

        if effort:
            t.effort = effort

        if message:
            t.message = " ".join(message)

    click.echo(t)


@root.command()
def list() -> None:
    "List tasks to be done, with highest value:effort ratio first."

    for task in sorted(tasks(), key=lambda t: (-t.roi, t.key)):
        click.echo(task)


@root.command()
@click.argument("key", nargs=1)
def done(key: str) -> None:
    "Mark a task as done. KEY specifies which task."

    with tasks().task(key) as t:
        t.mark_done()

    click.echo("Marked as done:", err=True)
    click.echo(t, err=True)
