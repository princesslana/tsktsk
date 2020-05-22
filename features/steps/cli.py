import re
import shlex
import subprocess
from pathlib import Path


@given("I have run {command}")
@when("I run {command}")
def run(ctx, command):
        result = subprocess.run(
            shlex.split(command),
            cwd=ctx.working_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8"
        )

        ctx.exit_code = result.returncode

        ctx.output = {
            "stdout": result.stdout,
            "stderr": result.stderr
        }

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
    assert not ctx.output[stream], f"Expected {stream} to be empty, got '{ctx.output[stream]}'"

@then("its {stream} should be")
def assert_output_is(ctx, stream):
    assert (
        ctx.output[stream] == ctx.text
    ), f"Expected {stream} to be '{ctx.text}', got '{ctx.output[stream]}'"


@then("the file {file_name} should exist")
def assert_file_exists(ctx, file_name):
    path = Path(ctx.working_directory, file_name)
    assert path.exists(), f"Expected {file_name} to exist. It does not"
    assert path.is_file(), f"Expected {file_name} to be a file. It is not"
