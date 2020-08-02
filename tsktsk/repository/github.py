import contextlib
import dataclasses
from typing import Any, Dict, Iterator, Optional

import requests
from tsktsk.config import GithubAuth
from tsktsk.task import (
    CATEGORY,
    CATEGORY_DEFAULT,
    EFFORT,
    EFFORT_DEFAULT,
    VALUE,
    VALUE_DEFAULT,
    Task,
)

JsonObject = Dict[str, Any]


def api(path: str) -> str:
    return f"https://api.github.com{path}"


class GithubTask(Task):
    def __init__(self, **kwargs: Any):
        self.additional_labels = kwargs.pop("additional_labels", None)

        super().__init__(**kwargs)


def task_from_json(issue: JsonObject) -> GithubTask:
    title = issue["title"]

    if ":" in title:
        prefix, message = title.split(":", maxsplit=1)

        category = next((c for c in CATEGORY if c in prefix), CATEGORY_DEFAULT)
    else:
        category = CATEGORY_DEFAULT
        message = title

    labels = sorted(label["name"] for label in issue["labels"])

    value = next((k for k, v in VALUE.items() if v in labels), VALUE_DEFAULT)
    effort = next((k for k, v in EFFORT.items() if v in labels), EFFORT_DEFAULT)

    task = GithubTask(
        key=issue["number"],
        message=message,
        category=category,
        effort=effort,
        value=value,
        additional_labels=sorted(
            l for l in labels if l not in VALUE.values() and l not in EFFORT.values()
        ),
    )
    return task


def task_to_json(task: GithubTask) -> JsonObject:
    json = {
        "state": "closed" if task.done else "open",
        "title": f"{CATEGORY[task.category]}: {task.message}",
    }

    labels = [l for l in [VALUE[task.value], EFFORT[task.effort]] if l]
    json["labels"] = sorted(labels + (task.additional_labels or []))

    return json


class GithubRepository:
    def __init__(self, repo: str, auth: Optional[GithubAuth] = None):
        self.repo = repo

        self.http = requests.Session()
        self.http.headers.update({"Accept": "application/vnd.github.v3+json"})

        if auth:
            self.http.auth = dataclasses.astuple(auth)

    def add(self, category: str, value: str, effort: str, message: str) -> Task:
        json = {"title": f"{CATEGORY[category]}: {message}"}

        labels = [l for l in [VALUE[value], EFFORT[effort]] if l]
        if labels:
            json["labels"] = labels

        result = self.http.post(api(f"/repos/{self.repo}/issues"), json=json).json()

        return Task(
            key=result["number"],
            category=category,
            message=message,
            effort=effort,
            value=value,
        )

    @contextlib.contextmanager
    def task(self, key: str) -> Iterator[Task]:
        issue = self.http.get(api(f"/repos/{self.repo}/issues/{key}")).json()

        task = task_from_json(issue)

        before = task_to_json(task)

        yield task

        after = task_to_json(task)

        changes = {
            k: after[k] for k, _ in after.items() if before.get(k, None) != after[k]
        }

        if changes:
            self.http.patch(api(f"/repos/{self.repo}/issues/{key}"), json=changes)

    def __iter__(self) -> Iterator[Task]:
        result = self.http.get(api(f"/repos/{self.repo}/issues?state=open")).json()

        issues = (issue for issue in result if not issue.get("pull_request"))

        yield from (task_from_json(issue) for issue in issues)
