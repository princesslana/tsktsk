import logging

from pkg_resources import resource_filename
from smalld import SmallD
from smalld_click import SmallDCliRunner
from yoyo import get_backend, read_migrations

from tsktsk.commands import root


def cli():
    import tsktsk.commands.cli  # noqa

    root()


def bot():
    import tsktsk.commands.bot  # noqa

    logging.basicConfig(level=logging.INFO)

    backend = get_backend("sqlite:///.tsktsk.db")
    migrations = read_migrations(resource_filename("tsktsk.resources", "migrations"))
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))

    smalld = SmallD()

    create_message = lambda msg: {"content": f"```\n{msg}\n```"}

    with SmallDCliRunner(smalld, root, create_message=create_message):
        smalld.run()
