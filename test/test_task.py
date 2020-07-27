import string
import textwrap

import hypothesis
import hypothesis.strategies as st
from tsktsk.task import Task


def printable():
    return st.text(alphabet=string.printable, min_size=1)


@st.composite
def task(draw):
    key = draw(
        st.text(
            alphabet=string.digits + string.ascii_letters + string.punctuation,
            min_size=1,
            max_size=6,
        )
    )
    message = draw(st.text(alphabet=string.printable, min_size=1))

    return Task(key=key, message=message)


@hypothesis.given(task=task())
def test_repr_inverts_eval(task):
    assert eval(repr(task)) == task


@hypothesis.given(task=task())
def test_str_contains_task_info(task):
    output = str(task)
    assert task.key in output
    assert textwrap.shorten(task.message, width=50) in output
    assert len(output) < 80
