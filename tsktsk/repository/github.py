import contextlib
import os

import requests
from tsktsk.task import CATEGORY, CATEGORY_DEFAULT, Task


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

    return Task(key=issue["number"], message=message, category=category)


def task_to_json(task):
    return {
        "state": "closed" if task.done else "open",
        "title": f"{CATEGORY[task.category]}: {task.message}",
    }


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
        result = self.http.post(
            api(f"/repos/{self.repo}/issues"),
            json={"title": f"{CATEGORY[category]}: {message}"},
        ).json()

        return Task(key=result["number"], category=category, message=message)

    @contextlib.contextmanager
    def task(self, key):
        issue = self.http.get(api(f"/repos/{self.repo}/issues/{key}")).json()

        task = task_from_json(issue)

        before = task_to_json(task)

        yield task

        after = task_to_json(task)

        changes = {k: after[k] for k, _ in set(after.items()) - set(before.items())}

        if changes:
            self.http.patch(api(f"/repos/{self.repo}/issues/{key}"), json=changes)

    def __iter__(self):
        result = self.http.get(api(f"/repos/{self.repo}/issues?state=open")).json()

        issues = (issue for issue in result if not issue.get("pull_request"))

        yield from (task_from_json(issue) for issue in issues)
