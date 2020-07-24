from setuptools import find_packages, setup


def install_requires():
    with open("requirements.txt") as f:
        return [r.strip() for r in f.readlines()]


setup(
    name="tsktsk",
    packages=find_packages(),
    use_scm_version=True,
    install_requires=install_requires(),
    setup_requires=["setuptools-scm==3.3.3"],
    entry_points={
        "console_scripts": [
            "tsktsk=tsktsk.__main__:cli",
            "tsktsk-bot=tsktsk.__main__:bot",
        ]
    },
)
