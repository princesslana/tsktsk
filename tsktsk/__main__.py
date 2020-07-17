from smalld import SmallD
from smalld_click import SmallDCliRunner

from .commands import tsktsk


def cli():
    tsktsk()


def bot():
    smalld = SmallD()

    with SmallDCliRunner(smalld, tsktsk, prefix="++"):
        smalld.run()
