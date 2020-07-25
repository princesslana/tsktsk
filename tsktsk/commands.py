import os
from pathlib import Path
from typing import Any, Callable, Optional

import click
from dotenv import load_dotenv
from pkg_resources import get_distribution

from tsktsk import repository
from tsktsk.repository import Repository

__version__ = get_distribution("tsktsk").version


@click.group()
@click.version_option(version=__version__, message="%(version)s")
@click.option("--github", default=None, help="Manage issues in a github repository.")
def tsktsk(github: Optional[str]) -> None:
    load_dotenv(Path(".env"))

    if github:
        os.environ["TSKTSK_GITHUB_REPO"] = github

    click.get_current_context().obj = repository.load()


def tasks() -> Repository:
    return click.get_current_context().obj


estimate = click.Choice(["high", "medium", "low"], case_sensitive=False)


@tsktsk.command()
def init() -> None:
    "Initialize a new tsktsk repository."

    try:
        repository.create()
        click.echo("tsktsk initialized.", err=True)
    except FileExistsError:
        raise SystemExit("tsktsk already initialized.")


def task_add(category: str, help: str) -> Callable[..., None]:
    long_help = f"""
        {help}

        Uses MESSAGE as a description of this task.

        An estimate of value gained and effort required to complete this task may
        also be added. These estimates are used to order the tasks, such that the
        tasks with the highest value:effort ratio are ordered first. If not
        specified, it defaults to medium/medium.
        """

    @tsktsk.command(category.lower(), help=long_help)
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


@tsktsk.command()
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

    r = repository.load()

    with r.task(key) as t:
        if category:
            t.category = category

        if value:
            t.value = value

        if effort:
            t.effort = effort

        if message:
            t.message = " ".join(message)

    click.echo(t)


@tsktsk.command()
def list() -> None:
    "List tasks to be done, with highest value:effort ratio first."

    r = repository.load()

    for task in sorted(r, key=lambda t: (-t.roi, t.key)):
        click.echo(task)


@tsktsk.command()
@click.argument("key", nargs=1)
def done(key: str) -> None:
    "Mark a task as done. KEY specifies which task."

    r = repository.load()

    with r.task(key) as t:
        t.mark_done()

    click.echo("Marked as done:", err=True)
    click.echo(t, err=True)
