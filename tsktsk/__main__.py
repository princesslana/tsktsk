from .commands import cli


def main():
    cli()


def bot():
    from smalld import SmallD
    from smalld_click import SmallDCliRunner

    smalld = SmallD()

    with SmallDCliRunner(smalld, cli, prefix="++"):
        smalld.run()
