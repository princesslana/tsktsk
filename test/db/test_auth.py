import string
import tempfile

import hypothesis
import hypothesis.strategies as st
from _pytest.monkeypatch import MonkeyPatch

import tsktsk.db.auth as auth_dao
from tsktsk.db import apply_migrations
from tsktsk.db.auth import GithubAuth

tmp_db = tempfile.NamedTemporaryFile()

apply_migrations(path=tmp_db.name)


@hypothesis.given(
    discord_id=st.text(alphabet=string.digits, min_size=1),
    username=st.text(alphabet=string.digits + string.ascii_letters, min_size=1),
    token=st.text(alphabet=string.digits + string.ascii_letters, min_size=1),
)
def test_add(discord_id, username, token):
    auth = GithubAuth(username, token)

    with MonkeyPatch().context() as mp:
        mp.setenv("TSKTSK_DB_PATH", tmp_db.name)

        auth_dao.add_or_update(discord_id, auth)

        assert auth_dao.find(discord_id) == auth


@hypothesis.given(
    username=st.text(alphabet=string.digits + string.ascii_letters, min_size=1),
    token=st.text(alphabet=string.digits + string.ascii_letters, min_size=1),
)
def test_update(username, token):
    discord_id = "123"
    auth = GithubAuth(username, token)

    with MonkeyPatch().context() as mp:
        mp.setenv("TSKTSK_DB_PATH", tmp_db.name)

        auth_dao.add_or_update(discord_id, auth)

        assert auth_dao.find(discord_id) == auth


@hypothesis.given(
    discord_id=st.text(alphabet=string.digits, min_size=1),
    username=st.text(alphabet=string.digits + string.ascii_letters, min_size=1),
    token=st.text(alphabet=string.digits + string.ascii_letters, min_size=1),
)
def test_delete(discord_id, username, token):
    auth = GithubAuth(username, token)

    with MonkeyPatch().context() as mp:
        mp.setenv("TSKTSK_DB_PATH", tmp_db.name)

        auth_dao.add_or_update(discord_id, auth)
        assert auth_dao.find(discord_id) == auth

        auth_dao.delete(discord_id)
        assert auth_dao.find(discord_id) is None
