import logging

from smalld import SmallD
from smalld_click import SmallDCliRunner
from tsktsk.commands import root


def cli():
    import tsktsk.commands.cli  # noqa

    root()


def bot():
    logging.basicConfig(level=logging.INFO)

    smalld = SmallD()

    create_message = lambda msg: {"content": f"```\n{msg}\n```"}

    with SmallDCliRunner(smalld, root, create_message=create_message):
        smalld.run()
