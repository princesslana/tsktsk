from typing import Optional

import click
import smalld_click

import tsktsk.db.auth as auth_dao
from tsktsk.commands.base import root
from tsktsk.config import Env
from tsktsk.db.auth import GithubAuth
from tsktsk.repository.auth import GithubAuthHandler, GithubAuthState

AUTH_HANDLER = GithubAuthHandler(Env.GITHUB_APP_CLIENT_ID.get(), "public_repo")


def auth_callback(context):
    def on_complete(auth: Optional[GithubAuth], state: GithubAuthState) -> None:
        with context.scope(), smalld_click.get_conversation() as conversation:
            if state == GithubAuthState.ACCEPTED:
                auth_dao.add_or_update(conversation.user_id, auth)
                click.echo("You have been registered successfully")
            elif state == GithubAuthState.DENIED:
                click.echo("Registration cancelled")
            elif state == GithubAuthState.EXPIRED:
                click.echo("Your verification code has expired")
            else:
                click.echo("An error has occurred. Please try again later")
        context.close()

    return on_complete


@root.command()
def auth() -> None:
    context = click.get_current_context()

    smalld_click.get_conversation().ensure_safe()
    auth_data = AUTH_HANDLER.authenticate(auth_callback(context))
    click.echo(
        f"Your verification code is {auth_data.user_code} valid for"
        f" {auth_data.expires_in // 60} minutes. Visit {auth_data.verification_uri}"
        f" to complete the authentication process."
    )
