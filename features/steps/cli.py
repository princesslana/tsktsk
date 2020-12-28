import difflib
import io
import os
import re
import shlex
import subprocess
import sys
import tempfile
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path

# Set before import to avoid local .env interfering with tests
os.environ["TSKTSK_IGNORE_DOTENV"] = "true"
from tsktsk.__main__ import cli


@contextmanager
def change_execution_env(new_cwd, new_argv):
    old_cwd = os.getcwd()
    old_argv = sys.argv

    try:
        os.chdir(new_cwd)
        sys.argv = new_argv
        yield
    finally:
        os.chdir(old_cwd)
        sys.argv = old_argv


@given("I have run tsktsk {args}")
@when("I run tsktsk {args}")
def run(ctx, args):
    command = ["tsktsk"] + shlex.split(args)
    stdout = redirect_stdout(io.StringIO())
    stderr = redirect_stderr(io.StringIO())
    exec_env = change_execution_env(ctx.working_directory, command)

    with stdout as out, stderr as err, exec_env:
        try:
            cli()
        except SystemExit as e:
            ctx.exit_code = e.code

    ctx.output = {"stdout": out.getvalue(), "stderr": err.getvalue()}


@given("I have run {command}")
@when("I run {command}")
def run(ctx, command):
    result = subprocess.run(
        shlex.split(command),
        cwd=ctx.working_directory,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )

    ctx.exit_code = result.returncode

    ctx.output = {"stdout": result.stdout, "stderr": result.stderr}


@given("today is {today:ti}")
@when("today is {today:ti}")
def change_date(ctx, today):
    ctx.today.return_value = today.date()


@given("I have a git repository")
def create_repository(ctx):
    ctx.execute_steps(
        """
        Given I have run git init
          And I have run git config user.email "user@email.com"
          And I have run git config user.name "User Name"
        """
    )


@given("I have added a file to staging")
def add_file_to_staging(ctx):
    temp_file = tempfile.NamedTemporaryFile(dir=ctx.working_directory)
    ctx.execute_steps(f"Given I have run git add {temp_file.name}")


@then("its exit code should be {expected:d}")
def assert_exit_code(ctx, expected):
    assert (
        ctx.exit_code == expected
    ), f"Expected exit code {expected}, got {ctx.exit_code}. stdout was '{ctx.output['stdout']}', stderr was '{ctx.output['stderr']}'"


@then("its {stream} should match {regex}")
def assert_output_matches(ctx, stream, regex):
    assert re.match(
        regex, ctx.output[stream]
    ), f"Expected {stream} to match '{regex}', got '{ctx.output[stream]}'"


@then("its {stream} should be empty")
def assert_output_is_empty(ctx, stream):
    assert not ctx.output[
        stream
    ], f"Expected {stream} to be empty, got '{ctx.output[stream]}'"


@then("its {stream} should be")
def assert_output_is(ctx, stream):
    assert (
        ctx.output[stream] == ctx.text
    ), f"Expected {stream} and actual differ. \n{get_diff(ctx.output[stream], ctx.text)}"


@then("the file {file_name} should exist")
def assert_file_exists(ctx, file_name):
    path = Path(ctx.working_directory, file_name)
    assert path.exists(), f"Expected {file_name} to exist. It does not"
    assert path.is_file(), f"Expected {file_name} to be a file. It is not"


def get_diff(lhs, rhs):
    lhs_lines = lhs.splitlines(keepends=True)
    rhs_lines = rhs.splitlines(keepends=True)
    diff = difflib.unified_diff(lhs_lines, rhs_lines)
    return "".join(diff)
