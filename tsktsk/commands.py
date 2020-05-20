from pathlib import Path

import click
from pkg_resources import get_distribution

__version__ = get_distribution("tsktsk").version


@click.group()
@click.version_option(version=__version__, message="%(version)s")
def cli():
    pass


@cli.command()
def init():
    try:
        Path(".tsktsk").touch(exist_ok=False)
        print("Tsktsk initialized.")
    except FileExistsError:
        raise SystemExit("Tsktsk already initialized.")
