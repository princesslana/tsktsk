import os
import textwrap
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Iterable, NoReturn, Optional, Set, Type, TypeVar

import click

import smalld_click
import tsktsk
from dotenv import load_dotenv
from tsktsk.config import Config, GithubAuth
from tsktsk.repository import FileRepository, GithubRepository, Repository
from tsktsk.task import (
    Category,
    Effort,
    Task,
    TaskError,
    Value,
    sequential_eta,
    sort_tasks_by_roi,
)


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


def fail(message: str) -> NoReturn:
    click.echo(message, err=True)
    click.get_current_context().exit(1)


F = TypeVar("F", bound=Callable[..., Any])


def enum_option(
    enum_type: Type[Enum], *param_decls: str, default: Optional[Enum] = None, **kwargs
) -> Callable[[F], F]:
    def callback(ctx, param, value):
        return enum_type.__members__[value.upper()] if isinstance(value, str) else value

    if default:
        kwargs["default"] = default.name

    return click.option(
        *param_decls,
        type=click.Choice([e.name.lower() for e in enum_type], case_sensitive=False),
        callback=callback,
        **kwargs,
    )


def task_add(category: Category, help: str) -> Callable[..., None]:
    long_help = f"""
        {help}

        Uses MESSAGE as a description of this task.

        An estimate of value gained and effort required to complete this task may
        also be added. These estimates are used to order the tasks, such that the
        tasks with the highest value:effort ratio are ordered first. If not
        specified, it defaults to medium/medium.
        """

    @root.command(category.name.lower(), help=long_help)
    @enum_option(
        Value,
        "--value",
        default=Value.DEFAULT,
        help="Value gained by completing this task.",
    )
    @enum_option(
        Effort,
        "--effort",
        default=Effort.DEFAULT,
        help="Effort required to complete this task.",
    )
    @click.option("--dep", multiple=True, help="Add dependency for this task.")
    @click.argument("message", nargs=-1, required=True)
    def f(*args: Any, **kwargs: Any) -> None:
        add(category, *args, **kwargs)

    return f


new = task_add(Category.NEW, "Create a task to add something new.")
imp = task_add(Category.IMP, "Create a task to improve something existing.")
fix = task_add(Category.FIX, "Create a task to fix a bug.")
doc = task_add(Category.DOC, "Create a task to improve documentation.")
tst = task_add(Category.TST, "Create a task related to testing.")


def describe_task(task, completion_date: Optional[date] = None):
    # 50 chars is the recommended length of a git commit
    msg = textwrap.shorten(task.message, width=50)

    eta_txt = f"⏰ {completion_date.strftime('%d-%m')}" if completion_date else ""

    # This should be under 80 chars wide, currently 78
    # key:6, space, category:6, space, message:50, space, value:2, space, effort:2, space, date:7
    header = (
        f"{task.key:>6} "
        f"{task.category.value}: "
        f"{msg:50} {task.value.value:2} {task.effort.value:2} {eta_txt}".rstrip()
    )

    deps = ""
    if task.dependencies:
        deps = ", ".join(sorted(task.dependencies, key=int))
        # Aligned to the start of the category name and wrapped to 80 chars wide
        first, *rest = textwrap.wrap(deps, width=80 - 13)
        first = f"\n{'🔗':>11} {first}"
        second = textwrap.indent("\n".join(rest), " " * 13)
        deps = "\n".join((first, second)).rstrip()

    return "".join([header, deps])


def add(
    category: Category, value: Value, effort: Effort, dep: Iterable[str], message: str
) -> None:
    try:
        task = tasks().add(category, value, effort, " ".join(message), set(dep))
    except ValueError as e:
        fail(f"Nonexistent task(s): {', '.join(e.args)}")
    click.echo(describe_task(task))


@root.command()
@enum_option(Category, "--category", help="Category of this task.")
@enum_option(Value, "--value", help="Value gained by completing this task.")
@enum_option(Effort, "--effort", help="Effort required to complete this task.")
@click.option("--dep", multiple=True, help="Add dependency to this task.")
@click.option("--rm-dep", multiple=True, help="Remove dependency from this task.")
@click.argument("key", nargs=1)
@click.argument("message", nargs=-1)
def edit(
    category: Optional[Category],
    value: Optional[Value],
    effort: Optional[Effort],
    dep: Iterable[str],
    rm_dep: Iterable[str],
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

        if dep or rm_dep:
            edit_dependencies(t, add=set(dep), remove=set(rm_dep))

    click.echo(describe_task(t))


def edit_dependencies(task: Task, add: Set[str], remove: Set[str]):
    if not add.isdisjoint(remove):
        fail("Dependency cannot be added and removed simultaneously")

    for dependency in tasks():
        if dependency.key in add:
            try:
                task.add_dependency(dependency)
            except TaskError:
                fail("Circular dependencies are not allowed")
            add.remove(dependency.key)
        elif dependency.key in remove:
            task.remove_dependency(dependency)
            remove.remove(dependency.key)

    if add or remove:
        fail(f"Nonexistent task(s): {', '.join(add | remove)}")


@root.command()
def list() -> None:
    "List tasks to be done, with highest value:effort ratio first."

    repo = tasks()
    sorted_tasks = sort_tasks_by_roi(repo)

    if not sorted_tasks:
        click.echo("No tasks", err=True)
        return

    for task, eta in sequential_eta(repo, sorted_tasks):
        click.echo(describe_task(task, eta))


@root.command()
@click.argument("key", nargs=1)
def done(key: str) -> None:
    "Mark a task as done. KEY specifies which task."

    try:
        with tasks().task(key) as t:
            t.mark_done()
    except TaskError:
        fail("Task is already done")

    click.echo("Marked as done:", err=True)
    click.echo(describe_task(t))


@root.command()
@click.argument("key", nargs=1)
def undone(key: str) -> None:
    "Mark a task as undone. KEY specifies which task."

    try:
        with tasks().task(key) as t:
            t.mark_undone()
    except TaskError:
        fail("Task is not done")

    click.echo("Marked as undone:", err=True)
    click.echo(describe_task(t))
