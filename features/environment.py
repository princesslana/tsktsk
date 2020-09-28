import shutil
import tempfile
from unittest.mock import patch

from behave import fixture, use_fixture


@fixture
def date_fixture(context):
    with patch("tsktsk.eta.date") as date_mock, patch(
        "tsktsk.task.date", new=date_mock
    ):
        yield date_mock.today


def before_tag(context, tag):
    if tag == "fixtures.date":
        context.today = use_fixture(date_fixture, context)


def before_scenario(context, scenario):
    context.working_directory = tempfile.mkdtemp()


def after_scenario(context, scenario):
    shutil.rmtree(context.working_directory)
