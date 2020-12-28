import string
from pathlib import Path
from unittest.mock import patch

import hypothesis
import hypothesis.strategies as st
from _pytest.monkeypatch import MonkeyPatch

from tsktsk.repository import FileRepository, GithubRepository
from tsktsk.repository.discovery import discover_repository


def no_db():
    return patch("tsktsk.repository.discovery.database", return_value=None)


def no_conversation():
    return patch("smalld_click.get_conversation", return_value=None)


@st.composite
def github_repo(draw):
    alphabet = string.digits + string.ascii_letters
    org = draw(st.text(alphabet=alphabet))
    name = draw(st.text(alphabet=alphabet))

    return f"{org}/{name}"


def test_defaults_to_file_repository():
    with no_db(), no_conversation():
        r = discover_repository(None, None)

        assert isinstance(r, FileRepository)
        assert r.path == Path(".tsktsk")


@hypothesis.given(github_repo=github_repo())
def test_always_uses_explicit(github_repo):
    with no_db(), no_conversation():
        r = discover_repository(None, github_repo)

        assert isinstance(r, GithubRepository)
        assert r.repo == github_repo


@hypothesis.given(github_repo=github_repo())
def test_uses_repo_configured_with_envvar(github_repo):
    with MonkeyPatch().context() as mp, no_db(), no_conversation():
        mp.setenv("TSKTSK_GITHUB_REPO", github_repo)

        r = discover_repository(None, None)

        assert isinstance(r, GithubRepository)
        assert r.repo == github_repo
