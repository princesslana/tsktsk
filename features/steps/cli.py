import re
import shlex
import subprocess


@when("I run {command}")
def run(ctx, command):
    try:
        output = subprocess.check_output(shlex.split(command), stderr=subprocess.STDOUT)
        ctx.exit_code = 0
    except subprocess.CalledProcessError as err:
        output = err.output
        ctx.exit_code = err.returncode

    ctx.output = output.decode("utf-8")


@then("its exit code should be {expected:d}")
def assert_exit_code(ctx, expected):
    assert (
        ctx.exit_code == expected
    ), f"Expected exit code {expected}, got {ctx.exit_code}. Output: {ctx.output}"


@then("its output should match {regex}")
def assert_match(ctx, regex):
    assert re.match(
        regex, ctx.output
    ), f"Expected output to match {regex}. Output: {ctx.output}"
