from datetime import date, timedelta
from itertools import repeat
from typing import Iterable, List, Optional, Tuple

from tsktsk.repository import Repository
from tsktsk.task import Task


def sequential_eta(
    repo: Repository, tasks: List[Task]
) -> Iterable[Tuple[Task, Optional[date]]]:
    velocity, remaining = estimate_velocity(repo)
    if velocity == 0:
        yield from zip(tasks, repeat(None))
        return

    cur_date = date.today()
    for task in tasks:
        remaining -= task.effort_points
        while remaining < 0:
            cur_date += timedelta(days=1)
            remaining += velocity
        yield task, cur_date


def estimate_velocity(repo: Repository) -> Tuple[float, float]:
    today = date.today()
    start_date = today - timedelta(days=60)

    tasks = repo.tasks_done_between(start_date, today)
    efforts = sum(t.effort_points for t in tasks if t.done != today)
    if efforts == 0:
        return 0, 0

    earliest_date = min(t.done for t in tasks)
    velocity = efforts / (today - earliest_date).days
    used = sum(t.effort_points for t in tasks if t.done == today)

    return velocity, velocity - used
