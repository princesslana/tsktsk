from argparse import ArgumentParser

from pkg_resources import get_distribution

from .commands import init


def main():
    parser = ArgumentParser(prog="tsktsk", description="Run tsktsk")

    parser.add_argument(
        "-v", "--version", action="version", version=get_distribution("tsktsk").version
    )

    commands = parser.add_subparsers(title="commands")

    init_parser = commands.add_parser("init")
    init_parser.set_defaults(command_f=init)

    args = parser.parse_args()
    args.command_f()
