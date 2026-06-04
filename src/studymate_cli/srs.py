from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from uuid import uuid4

RATINGS = ("again", "hard", "good", "easy")


@dataclass(frozen=True)
class ReviewItem:
    id: str
    prompt: str
    due_date: date
    interval_days: int = 0
    ease_factor: float = 2.5
    repetitions: int = 0
    lapses: int = 0


def default_srs_store() -> Path:
    return Path.home() / ".studymate" / "srs.json"


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def load_review_items(path: Path) -> list[ReviewItem]:
    if not path.exists():
        return []

    data = json.loads(path.read_text(encoding="utf-8"))
    return sorted(
        [
            ReviewItem(
                id=item["id"],
                prompt=item["prompt"],
                due_date=_parse_date(item["due_date"]),
                interval_days=item.get("interval_days", 0),
                ease_factor=item.get("ease_factor", 2.5),
                repetitions=item.get("repetitions", 0),
                lapses=item.get("lapses", 0),
            )
            for item in data
        ],
        key=lambda item: (item.due_date, item.prompt),
    )


def save_review_items(path: Path, items: list[ReviewItem]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = []
    for item in sorted(items, key=lambda value: (value.due_date, value.prompt)):
        data = asdict(item)
        data["due_date"] = item.due_date.isoformat()
        payload.append(data)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def add_review_item(path: Path, prompt: str, today: date | None = None) -> ReviewItem:
    today = today or date.today()
    item = ReviewItem(id=uuid4().hex[:12], prompt=prompt, due_date=today)
    items = load_review_items(path)
    items.append(item)
    save_review_items(path, items)
    return item


def due_review_items(items: list[ReviewItem], today: date | None = None) -> list[ReviewItem]:
    today = today or date.today()
    return [item for item in sorted(items, key=lambda value: (value.due_date, value.prompt)) if item.due_date <= today]


def schedule_review(item: ReviewItem, rating: str, today: date | None = None) -> ReviewItem:
    if rating not in RATINGS:
        raise ValueError(f"Rating must be one of: {', '.join(RATINGS)}")

    today = today or date.today()
    ease_factor = item.ease_factor
    repetitions = item.repetitions
    interval_days = item.interval_days
    lapses = item.lapses

    if rating == "again":
        ease_factor = max(1.3, ease_factor - 0.2)
        repetitions = 0
        interval_days = 1
        lapses += 1
    elif rating == "hard":
        ease_factor = max(1.3, ease_factor - 0.15)
        repetitions += 1
        interval_days = max(1, round(max(1, interval_days) * 1.2))
    elif rating == "good":
        repetitions += 1
        if item.repetitions == 0:
            interval_days = 1
        elif item.repetitions == 1:
            interval_days = 3
        else:
            interval_days = max(1, round(interval_days * ease_factor))
    else:
        ease_factor += 0.15
        repetitions += 1
        if item.repetitions == 0:
            interval_days = 4
        else:
            interval_days = max(1, round(interval_days * ease_factor * 1.3))

    return ReviewItem(
        id=item.id,
        prompt=item.prompt,
        due_date=today + timedelta(days=interval_days),
        interval_days=interval_days,
        ease_factor=round(ease_factor, 2),
        repetitions=repetitions,
        lapses=lapses,
    )


def review_item(path: Path, item_id: str, rating: str, today: date | None = None) -> ReviewItem:
    items = load_review_items(path)
    updated_items = []
    reviewed_item: ReviewItem | None = None

    for item in items:
        if item.id == item_id:
            reviewed_item = schedule_review(item, rating, today=today)
            updated_items.append(reviewed_item)
        else:
            updated_items.append(item)

    if reviewed_item is None:
        raise KeyError(f"Review item not found: {item_id}")

    save_review_items(path, updated_items)
    return reviewed_item
