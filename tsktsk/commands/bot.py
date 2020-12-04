import click
import smalld_click

from tsktsk.auth import GithubAuth, GithubAuthState
from tsktsk.commands.base import github_auth_handler, root


@root.command()
def auth() -> None:
    auth_handler = github_auth_handler()
    context = click.get_current_context()

    def on_completed(auth: GithubAuth, state: GithubAuthState):
        with context, smalld_click.get_conversation():
            if state == GithubAuthState.ACCEPTED:
                click.echo("You have been registered successfully")
            elif state == GithubAuthState.DENIED:
                click.echo("Registration cancelled")
            elif state == GithubAuthState.EXPIRED:
                click.echo("Your verification code has expired")
            else:
                click.echo("An error has occurred. Please try again later")
        context.close()

    auth_data = auth_handler.authenticate(on_completed)
    smalld_click.get_conversation().ensure_safe()
    click.echo(
        f"Your verification code is {auth_data.user_code} valid for"
        f" {auth_data.expires_in // 60} minutes. Visit {auth_data.verification_uri}"
        f" to complete the authentication process."
    )
    context.scope(cleanup=False)
