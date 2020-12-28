import dataclasses
import time
from enum import Enum, auto
from queue import PriorityQueue
from threading import Event, Thread
from typing import Callable, Optional

import requests
import smalld_click

from tsktsk.config import Env
from tsktsk.db import Database


@dataclasses.dataclass
class GithubAuth:
    username: str
    token: str


def auth_from_env() -> Optional[GithubAuth]:
    username = Env.GITHUB_USERNAME.get()
    token = Env.GITHUB_TOKEN.get()

    if username and not token:
        raise ValueError("Github username provided, but no token")

    if token and not username:
        raise ValueError("Github token provided, but no username")

    if not username and not token:
        return None

    return GithubAuth(username, token)


class GithubAuthState(Enum):
    ACCEPTED = auto()
    EXPIRED = auto()
    DENIED = auto()
    ERROR = auto()


AuthCallback = Callable[[Optional[GithubAuth], GithubAuthState], None]


@dataclasses.dataclass
class DeviceAuthData:
    device_code: str
    user_code: str
    verification_uri: str
    started_at: float
    expires_in: int
    interval: int
    on_completed: AuthCallback


class GithubAuthHandler:
    def __init__(self, client_id, scope):
        self.client_id = client_id
        self.scope = scope
        self.http = requests.Session()
        self.http.headers["Accept"] = "application/json"
        self.pending_auth = PriorityQueue()
        self.auth_requested = Event()
        Thread(target=self.periodic_poll, daemon=True).start()

    def authenticate(self, on_completed: AuthCallback) -> DeviceAuthData:
        info = self.http.post(
            "https://github.com/login/device/code",
            {"client_id": self.client_id, "scope": self.scope},
        ).json()
        auth_data = DeviceAuthData(
            **info,
            started_at=time.time(),
            on_completed=on_completed,
        )
        next_poll = auth_data.started_at + auth_data.interval
        self.pending_auth.put((next_poll, auth_data))
        self.auth_requested.set()
        return auth_data

    def periodic_poll(self):
        while True:
            next_poll, auth_data = self.pending_auth.get()
            self.auth_requested.clear()

            now = time.time()
            if next_poll > now:
                self.auth_requested.wait(next_poll - now)
                self.pending_auth.put((next_poll, auth_data))
            else:
                self.poll_auth_state(auth_data)

    def poll_auth_state(self, auth_data: DeviceAuthData):
        data = self.http.post(
            "https://github.com/login/oauth/access_token",
            {
                "client_id": self.client_id,
                "device_code": auth_data.device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            },
        ).json()

        # We can't rely on the response status because Github does not return
        # 400 Bad Request as the standard requires for every error case.
        if "error" in data:
            self.handle_error(data["error"], auth_data)
        else:
            auth_data.on_completed(
                GithubAuth(username="token", token=data["access_token"]),
                GithubAuthState.ACCEPTED,
            )

    def handle_error(self, error: str, auth_data: DeviceAuthData):
        if error == "slow_down":
            auth_data.interval += 5

        if error == "authorization_pending" or error == "slow_down":
            next_poll = time.time() + auth_data.interval
            if next_poll <= auth_data.started_at + auth_data.expires_in:
                self.pending_auth.put((next_poll, auth_data))
            else:
                auth_data.on_completed(None, GithubAuthState.EXPIRED)
        elif error == "access_denied":
            auth_data.on_completed(None, GithubAuthState.DENIED)
        elif error == "expired_token":
            auth_data.on_completed(None, GithubAuthState.EXPIRED)
        else:
            auth_data.on_completed(None, GithubAuthState.ERROR)


class GithubAuthDao:
    def __init__(self, db: Database):
        self.db = db

    def add_or_update(self, discord_id: str, auth: GithubAuth):
        self.db.execute(
            "INSERT OR REPLACE INTO github_auth(discord_id, username, token) VALUES (?, ?, ?)",
            (discord_id, auth.username, auth.token),
        )

    def find(self, discord_id: str):
        row = self.db.fetchone(
            "SELECT username, token FROM github_auth WHERE discord_id = ?",
            (discord_id,),
        )
        return GithubAuth(row[0], row[1]) if row is not None else None


def find_github_auth(dao: GithubAuthDao) -> Optional[GithubAuth]:
    conversation = smalld_click.get_conversation()
    return dao.find(conversation.user_id) if conversation else auth_from_env()
