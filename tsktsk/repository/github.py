import requests
from tsktsk.task import CATEGORY, CATEGORY_DEFAULT, Task


class GithubRepository:
    def __init__(self, repo):
        self.repo = repo

    def __iter__(self):
        result = requests.get(
            f"https://api.github.com/repos/{self.repo}/issues?state=open",
            headers={"Accept": "application/vnd.github.v3+json"},
        ).json()

        issues = (issue for issue in result if not issue.get("pull_request"))

        for issue in issues:
            title = issue["title"]

            if ":" in title:
                prefix, message = title.split(":", maxsplit=1)

                category = next((c for c in CATEGORY if c in prefix), CATEGORY_DEFAULT)
            else:
                category = CATEGORY_DEFAULT
                message = title

            yield Task(key=issue["number"], message=message, category=category)
