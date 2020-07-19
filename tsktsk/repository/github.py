import contextlib
import os

import requests
from tsktsk.task import (
    CATEGORY,
    CATEGORY_DEFAULT,
    EFFORT,
    EFFORT_DEFAULT,
    VALUE,
    VALUE_DEFAULT,
    Task,
)


def api(path):
    return f"https://api.github.com{path}"


def task_from_json(issue):
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

    task = Task(
        key=issue["number"],
        message=message,
        category=category,
        effort=effort,
        value=value,
    )
    task.additional_labels = sorted(
        l for l in labels if l not in VALUE.values() and l not in EFFORT.values()
    )
    return task


def task_to_json(task):
    json = {
        "state": "closed" if task.done else "open",
        "title": f"{CATEGORY[task.category]}: {task.message}",
    }

    labels = [l for l in [VALUE[task.value], EFFORT[task.effort]] if l]
    if labels:
        json["labels"] = sorted(labels + (task.additional_labels or []))

    return json


class GithubRepository:
    def __init__(self, repo):
        self.repo = repo

        self.http = requests.Session()
        self.http.headers.update({"Accept": "application/vnd.github.v3+json"})

        auth = (
            os.environ.get("TSKTSK_GITHUB_USERNAME"),
            os.environ.get("TSKTSK_GITHUB_TOKEN"),
        )
        if auth != (None, None):
            self.http.auth = auth

    def add(self, category, value, effort, message):
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
    def task(self, key):
        issue = self.http.get(api(f"/repos/{self.repo}/issues/{key}")).json()

        task = task_from_json(issue)

        before = task_to_json(task)

        yield task

        after = task_to_json(task)

        changes = {
            k: after[k] for k, _ in after.items() if not before.get(k, None) == after[k]
        }

        print(changes)

        if changes:
            self.http.patch(api(f"/repos/{self.repo}/issues/{key}"), json=changes)

    def __iter__(self):
        result = self.http.get(api(f"/repos/{self.repo}/issues?state=open")).json()

        issues = (issue for issue in result if not issue.get("pull_request"))

        yield from (task_from_json(issue) for issue in issues)
