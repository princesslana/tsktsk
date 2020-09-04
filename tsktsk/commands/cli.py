import subprocess

import click

import tsktsk.repository as repository
from tsktsk.commands.base import fail, root, tasks


@root.command()
def init() -> None:
    "Initialize a new tsktsk repository."

    try:
        repository.create()
        click.echo("tsktsk initialized.", err=True)
    except FileExistsError:
        fail("tsktsk already initialized.")


@root.command()
@click.argument("key", nargs=1)
def commit(key: str) -> None:
    "Commit changes using message from task. KEY specifies which task."

    with tasks().task(key) as t:
        output = subprocess.run(
            ["git", "commit", "-m", f"{t.category.value}: {t.message}"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        callback = fail if output.returncode else click.echo
        callback(output.stdout)
