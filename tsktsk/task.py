import textwrap
from datetime import datetime
from typing import Any, Dict, Optional

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
        key: str,
        message: str,
        category: str = CATEGORY_DEFAULT,
        value: str = VALUE_DEFAULT,
        effort: str = EFFORT_DEFAULT,
        done: Optional[str] = None,
    ):
        self.key = key
        self.message = message
        self.category = category
        self.value = value
        self.effort = effort
        self.done = done

    def asdict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "message": self.message,
            "category": self.category,
            "value": self.value,
            "effort": self.effort,
            "done": self.done,
        }

    @property
    def roi(self) -> float:
        return POINTS[self.value] / POINTS[self.effort]

    def mark_done(self) -> None:
        self.done = datetime.now().strftime("%Y%m%d")

    def __repr__(self) -> str:
        return "Task(" + ",".join(f"{k}={v!r}" for k, v in self.asdict().items()) + ")"

    def __str__(self) -> str:
        # 50 chars is the recommended length of a git commit summary
        msg = textwrap.shorten(self.message, width=50)

        # This should be under 80 chars wide, currently 70
        # key:6, space, category:6, space, message:50, space, value:2, space effort 2
        return (
            f"{self.key:>6} "
            f"{CATEGORY[self.category]}: "
            f"{msg:50} {VALUE[self.value]:2} {EFFORT[self.effort]:2}".rstrip()
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False
