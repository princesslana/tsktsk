import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from smalld import SmallD
from smalld_click import SmallDCliRunner

from tsktsk.commands import root
from tsktsk.db import apply_migrations

if not os.environ.get("TSKTSK_IGNORE_DOTENV"):
    load_dotenv(Path(".env"))


def cli():
    import tsktsk.commands.cli  # noqa

    root()


def bot():
    import tsktsk.commands.bot  # noqa

    logging.basicConfig(level=logging.INFO)

    name = os.environ.get("TSKTSK_NAME", "tsktsk")

    apply_migrations()

    smalld = SmallD()

    create_message = lambda msg: {"content": f"```\n{msg}\n```"}

    with SmallDCliRunner(
        smalld, root, prefix="", name=name, create_message=create_message
    ):
        smalld.run()
