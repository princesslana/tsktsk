import contextlib
import dataclasses
from datetime import datetime
from typing import Any, Dict, Iterator, Optional

import requests
from tsktsk.config import GithubAuth
from tsktsk.task import Category, Effort, Task, Value

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

        category = next((c for c in Category if c.name in prefix), Category.DEFAULT)
    else:
        category = Category.DEFAULT
        message = title

    labels = sorted(label["name"] for label in issue["labels"])

    value = next((v for v in Value if v.value in labels), Value.DEFAULT)
    effort = next((e for e in Effort if e.value in labels), Effort.DEFAULT)
    additional_labels = sorted(
        l
        for l in labels
        if l not in (v.value for v in Value) and l not in (e.value for e in Effort)
    )

    closed_at = issue["closed_at"]
    done = (
        datetime.strptime(closed_at, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y%m%d")
        if closed_at
        else None
    )

    return GithubTask(
        key=issue["number"],
        message=message,
        category=category,
        effort=effort,
        value=value,
        additional_labels=additional_labels,
        done=done,
    )


def task_to_json(task: GithubTask) -> JsonObject:
    json = {
        "state": "closed" if task.done else "open",
        "title": f"{task.category.value}: {task.message}",
    }

    labels = [l.value for l in (task.value, task.effort) if l.value]
    json["labels"] = sorted(labels + (task.additional_labels or []))

    return json


class GithubRepository:
    def __init__(self, repo: str, auth: Optional[GithubAuth] = None):
        self.repo = repo

        self.http = requests.Session()
        self.http.headers.update({"Accept": "application/vnd.github.v3+json"})

        if auth:
            self.http.auth = dataclasses.astuple(auth)

    def add(
        self, category: Category, value: Value, effort: Effort, message: str
    ) -> Task:
        json = {"title": f"{category.value}: {message}"}

        labels = [l.value for l in (value, effort) if l.value]
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
