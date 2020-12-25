import string

import hypothesis
import hypothesis.strategies as st

from tsktsk.repository.github import task_from_json
from tsktsk.task import Category, Effort, Value


@hypothesis.given(
    key=st.integers(min_value=1),
    category=st.sampled_from(Category),
    message=st.text(alphabet=string.printable, min_size=1),
)
def test_simple_task_from_json(key, category, message):
    issue = {
        "number": key,
        "title": f"{category.value}: {message}",
        "labels": [],
        "closed_at": None,
        "body": "",
    }

    task = task_from_json(issue)

    assert task.key == str(key)
    assert task.message == message.strip()
    assert task.category == category
    assert task.value == Value.MEDIUM
    assert task.effort == Effort.MEDIUM
    assert len(task.dependencies) == 0
    assert not task.done


@hypothesis.given(
    number=st.integers(min_value=1),
    title=st.text(alphabet=string.printable, min_size=1),
    labels=st.lists(st.text(alphabet=string.printable)),
    body=st.text(alphabet=string.printable),
)
def test_random_non_tsktsk_task_from_json(number, title, labels, body):
    issue = {
        "number": number,
        "title": title,
        "labels": [{"name": l} for l in labels],
        "closed_at": None,
        "body": body,
    }

    task = task_from_json(issue)

    assert task.key == str(number)
    assert task.message == title.strip()
    assert task.category == Category.NEW
    assert task.value == Value.MEDIUM
    assert task.effort == Effort.MEDIUM
    assert len(task.dependencies) == 0
    assert not task.done
