from smalld import SmallD
from smalld_click import SmallDCliRunner

from tsktsk.commands import root


def cli():
    import tsktsk.commands.cli

    root()


def bot():
    smalld = SmallD()

    with SmallDCliRunner(smalld, root, prefix=""):
        smalld.run()
