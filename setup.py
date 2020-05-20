from setuptools import find_packages, setup

fmt_deps = ["autoflake==1.3.1", "isort==4.3.21", "black==19.3b0"]
setup_deps = ["setuptools-scm==3.3.3"]
test_deps = ["pytest==5.2.1", "pytest-cov==2.8.1", "behave==1.2.6"]
extras = {"fmt": fmt_deps, "test": test_deps}


def install_requires():
    with open("requirements.txt") as f:
        return [r.strip() for r in f.readlines()]


setup(
    name="tsktsk",
    packages=find_packages(),
    use_scm_version=True,
    install_requires=install_requires(),
    tests_require=test_deps,
    extras_require=extras,
    setup_requires=setup_deps,
    entry_points={"console_scripts": ["tsktsk=tsktsk.__main__:main"]},
)
