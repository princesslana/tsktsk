from argparse import ArgumentParser

from pkg_resources import get_distribution


def main():
    parser = ArgumentParser(prog="tsktsk", description="Run tsktsk")

    parser.add_argument(
        "-v", "--version", action="version", version=get_distribution("tsktsk").version
    )

    parser.parse_args()
