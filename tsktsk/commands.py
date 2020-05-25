import sys

import click
from pkg_resources import get_distribution

from . import repository
from .repository import RepositoryError

__version__ = get_distribution("tsktsk").version


@click.group()
@click.version_option(version=__version__, message="%(version)s")
def cli():
    pass


estimate = click.Choice(["high", "medium", "low"], case_sensitive=False)


@cli.command()
def init():
    "Initialize a new tsktsk repository."

    try:
        repository.create()
        print("tsktsk initialized.", file=sys.stderr)
    except RepositoryError:
        raise SystemExit("tsktsk already initialized.")


def task_add(category, help):
    long_help = f"""
        {help}

        Uses MESSAGE as a description of this task.

        An estimate of value gained and effort required to complete this task may
        also be added. These estimates are used to order the tasks, such that the
        tasks with the highest value:effort ratio are ordered first. If not
        specified, it defaults to medium/medium.
        """

    @cli.command(category.lower(), help=long_help)
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
    def f(*args, **kwargs):
        add(category, *args, **kwargs)

    return f


new = task_add("NEW", "Create a task to add something new.")
imp = task_add("IMP", "Create a task to improve something existing.")
fix = task_add("FIX", "Create a task to fix a bug.")
doc = task_add("DOC", "Create a task to improve documentation.")
tst = task_add("TST", "Create a task related to testing.")


def add(category, value, effort, message):
    with repository.load() as r:
        print(r.add(category, value, effort, " ".join(message)))


@cli.command()
@click.option(
    "--category",
    type=click.Choice(["NEW", "IMP", "FIX", "DOC", "TST"], case_sensitive=False),
    help="Category of this task.",
)
@click.option("--value", type=estimate, help="Value gained by completing this task.")
@click.option("--effort", type=estimate, help="Effort required to complete this task.")
@click.argument("key", nargs=1)
@click.argument("message", nargs=-1)
def edit(category, value, effort, key, message):
    "Edit an existing task. KEY specifies which task."

    with repository.load() as r:
        with r.task(key) as t:
            if category:
                t.category = category

            if value:
                t.value = value

            if effort:
                t.effort = effort

            if message:
                t.message = " ".join(message)

        print(t)


@cli.command()
def list():
    "List tasks to be done, with highest value:effort ratio first."

    with repository.load() as r:
        for task in sorted(r, key=lambda t: (-t.roi, t.key)):
            if not task.done:
                print(task)


@cli.command()
@click.argument("key", nargs=1)
def done(key):
    "Mark a task as done. KEY specifies which task."

    with repository.load() as r:
        with r.task(key) as t:
            t.mark_done()
