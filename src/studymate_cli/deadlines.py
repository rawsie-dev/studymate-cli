from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path


@dataclass(frozen=True)
class Deadline:
    title: str
    due_date: date
    course: str | None = None
    notes: str | None = None


def default_deadline_store() -> Path:
    return Path.home() / ".studymate" / "deadlines.json"


def parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("Date must be in YYYY-MM-DD format.") from exc


def load_deadlines(path: Path) -> list[Deadline]:
    if not path.exists():
        return []

    data = json.loads(path.read_text(encoding="utf-8"))
    deadlines: list[Deadline] = []
    for item in data:
        deadlines.append(
            Deadline(
                title=item["title"],
                due_date=parse_date(item["due_date"]),
                course=item.get("course"),
                notes=item.get("notes"),
            )
        )
    return sorted(deadlines, key=lambda item: item.due_date)


def save_deadlines(path: Path, deadlines: list[Deadline]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = []
    for deadline in sorted(deadlines, key=lambda item: item.due_date):
        item = asdict(deadline)
        item["due_date"] = deadline.due_date.isoformat()
        payload.append(item)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def add_deadline(
    path: Path,
    title: str,
    due_date: str,
    course: str | None = None,
    notes: str | None = None,
) -> Deadline:
    deadline = Deadline(title=title, due_date=parse_date(due_date), course=course, notes=notes)
    deadlines = load_deadlines(path)
    deadlines.append(deadline)
    save_deadlines(path, deadlines)
    return deadline


def days_left(deadline: Deadline, today: date | None = None) -> int:
    today = today or date.today()
    return (deadline.due_date - today).days
