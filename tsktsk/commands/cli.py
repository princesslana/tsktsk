import subprocess

import click

import tsktsk.repository as repository
from tsktsk.commands.base import root, tasks
from tsktsk.task import CATEGORY


@root.command()
def init() -> None:
    "Initialize a new tsktsk repository."

    try:
        repository.create()
        click.echo("tsktsk initialized.", err=True)
    except FileExistsError:
        raise SystemExit("tsktsk already initialized.")


@root.command()
@click.argument("key", nargs=1)
def commit(key: str) -> None:
    "Commit changes using message from task. KEY specifies which task."

    with tasks().task(key) as t:
        output = subprocess.run(
            ["git", "commit", "-m", f"{CATEGORY[t.category]}: {t.message}"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        if output.stdout:
            click.echo(output.stdout, err=bool(output.returncode))
        if output.returncode:
            click.get_current_context().abort()
