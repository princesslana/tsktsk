import textwrap
from datetime import datetime

CATEGORY_DEFAULT = "NEW"
VALUE_DEFAULT = "medium"
EFFORT_DEFAULT = "medium"

CATEGORY = {
    "NEW": "📦 NEW",
    "IMP": "👌 IMP",
    "FIX": "🐛 FIX",
    "DOC": "📖 DOC",
    "TST": "✅ TST",
}

VALUE = {"high": "V⬆", "medium": "", "low": "V⬇"}
EFFORT = {"high": "E⬆", "medium": "", "low": "E⬇"}
POINTS = {"high": 8, "medium": 5, "low": 3}


class Task:
    def __init__(
        self,
        key,
        message,
        category=CATEGORY_DEFAULT,
        value=VALUE_DEFAULT,
        effort=EFFORT_DEFAULT,
        done=None,
    ):
        self.key = key
        self.message = message
        self.category = category
        self.value = value
        self.effort = effort
        self.done = done

    def asdict(self):
        return {
            "key": self.key,
            "message": self.message,
            "category": self.category,
            "value": self.value,
            "effort": self.effort,
            "done": self.done,
        }

    @property
    def roi(self):
        return POINTS[self.value] / POINTS[self.effort]

    def mark_done(self):
        self.done = datetime.now().strftime("%Y%m%d")

    def __repr__(self):
        return "Task(" + "".join(f"{k}={v}" for k, v in self.asdict().items()) + ")"

    def __str__(self):
        # 50 chars is the recommended length of a git commit summary
        msg = textwrap.shorten(self.message, width=50)

        # This should be under 80 chars wide, currently 70
        # key:6, space, category:6, space, message:50, space, value:2, space effort 2
        return (
            f"{self.key:>6} "
            f"{CATEGORY[self.category]}: "
            f"{msg:50} {VALUE[self.value]:2} {EFFORT[self.effort]:2}".rstrip()
        )
