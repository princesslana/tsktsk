from pathlib import Path


def init():
    try:
        Path(".tsktsk").touch(exist_ok=False)
        print("Tsktsk initialized.")
    except FileExistsError:
        raise SystemExit("Tsktsk already initialized.")
