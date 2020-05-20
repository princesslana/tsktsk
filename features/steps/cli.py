import re
import shlex
import subprocess
from pathlib import Path

@given("I have run {command}")
@when("I run {command}")
def run(ctx, command):
    try:
        output = subprocess.check_output(
            shlex.split(command),
            cwd=ctx.working_directory,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
        )
        ctx.exit_code = 0
    except subprocess.CalledProcessError as err:
        output = err.output
        ctx.exit_code = err.returncode

    ctx.output = output


@then("its exit code should be {expected:d}")
def assert_exit_code(ctx, expected):
    assert (
        ctx.exit_code == expected
    ), f"Expected exit code {expected}, got {ctx.exit_code}. Output: {ctx.output}"


@then("its output should match {regex}")
def assert_output_matches(ctx, regex):
    assert re.match(
        regex, ctx.output
    ), f"Expected output to match '{regex}', got '{ctx.output}'"


@then("its output should be")
def assert_output_is(ctx):
    assert ctx.output == ctx.text, f"Expected output to be '{ctx.text}', got '{ctx.output}'"


@then("the file {file_name} should exist")
def assert_file_exists(ctx, file_name):
    path = Path(ctx.working_directory, file_name)
    assert path.exists(), f"Expected {file_name} to exist. It does not"
    assert path.is_file(), f"Expected {file_name} to be a file. It is not"
