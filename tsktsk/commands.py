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


def task_add(f):
    f = cli.command()(f)
    f = click.argument("message", nargs=-1)(f)
    return f


@task_add
def new(message):
    add("NEW", message)


@task_add
def imp(message):
    add("IMP", message)


@task_add
def fix(message):
    add("FIX", message)


@task_add
def doc(message):
    add("DOC", message)


@task_add
def tst(message):
    add("TST", message)


def add(category, message):
    with repository.load() as r:
        print(r.add(category, " ".join(message)))


@cli.command()
def top():
    with repository.load() as r:
        print(r.top())


@cli.command()
def list():
    with repository.load() as r:
        for task in r:
            if not task.done:
                print(task)


@cli.command()
@click.argument("key", nargs=-1)
def done(key):
    with repository.load() as r:
        for k in key:
            with r.task(k) as t:
                t.mark_done()
