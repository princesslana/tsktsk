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


@cli.command()
def init():
    try:
        repository.create()
        print("Tsktsk initialized.", file=sys.stderr)
    except RepositoryError:
        raise SystemExit("Tsktsk already initialized.")


def task_add(category):
    @cli.command(category.lower())
    @click.option(
        "--value",
        type=click.Choice(["high", "medium", "low"], case_sensitive=False),
        default="medium",
    )
    @click.option(
        "--effort",
        type=click.Choice(["high", "medium", "low"], case_sensitive=False),
        default="medium",
    )
    @click.argument("message", nargs=-1)
    def f(*args, **kwargs):
        add(category, *args, **kwargs)

    return f


new = task_add("NEW")
imp = task_add("IMP")
fix = task_add("FIX")
doc = task_add("DOC")
tst = task_add("TST")


def add(category, value, effort, message):
    with repository.load() as r:
        print(r.add(category, value, effort, " ".join(message)))


@cli.command()
@click.option(
    "--category",
    type=click.Choice(["NEW", "IMP", "FIX", "DOC", "TST"], case_sensitive=False),
)
@click.option(
    "--value", type=click.Choice(["high", "medium", "low"], case_sensitive=False)
)
@click.option(
    "--effort", type=click.Choice(["high", "medium", "low"], case_sensitive=False)
)
@click.argument("key", nargs=1)
@click.argument("message", nargs=-1)
def edit(category, value, effort, key, message):
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
def top():
    with repository.load() as r:
        print(r.top())


@cli.command()
def list():
    with repository.load() as r:
        for task in sorted(r, key=lambda t: (-t.roi, t.key)):
            if not task.done:
                print(task)


@cli.command()
@click.argument("key", nargs=-1)
def done(key):
    with repository.load() as r:
        for k in key:
            with r.task(k) as t:
                t.mark_done()
