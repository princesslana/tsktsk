from pathlib import Path


def init():
    Path(".tsktsk").touch()

    print("Initialized tsktsk.")
