from datetime import date

import pytest

from studymate_cli.srs import (
    ReviewItem,
    add_review_item,
    due_review_items,
    load_review_items,
    review_item,
    save_review_items,
    schedule_review,
)


def test_add_review_item_is_due_today(tmp_path):
    store = tmp_path / "srs.json"

    item = add_review_item(store, "What is active recall?", today=date(2026, 6, 1))

    assert item.due_date == date(2026, 6, 1)
    assert due_review_items(load_review_items(store), today=date(2026, 6, 1)) == [item]


def test_schedule_good_review_advances_interval():
    item = ReviewItem(id="abc", prompt="Define entropy", due_date=date(2026, 6, 1))

    first = schedule_review(item, "good", today=date(2026, 6, 1))
    second = schedule_review(first, "good", today=date(2026, 6, 2))

    assert first.interval_days == 1
    assert first.due_date == date(2026, 6, 2)
    assert second.interval_days == 3
    assert second.due_date == date(2026, 6, 5)
    assert second.repetitions == 2


def test_schedule_again_records_lapse():
    item = ReviewItem(
        id="abc",
        prompt="Define entropy",
        due_date=date(2026, 6, 1),
        interval_days=10,
        repetitions=3,
    )

    updated = schedule_review(item, "again", today=date(2026, 6, 1))

    assert updated.interval_days == 1
    assert updated.due_date == date(2026, 6, 2)
    assert updated.repetitions == 0
    assert updated.lapses == 1
    assert updated.ease_factor == 2.3


def test_review_item_persists_updated_schedule(tmp_path):
    store = tmp_path / "srs.json"
    item = ReviewItem(id="abc", prompt="Define entropy", due_date=date(2026, 6, 1))
    save_review_items(store, [item])

    updated = review_item(store, "abc", "easy", today=date(2026, 6, 1))

    assert updated.due_date == date(2026, 6, 5)
    assert load_review_items(store)[0] == updated


def test_review_item_rejects_unknown_id(tmp_path):
    store = tmp_path / "srs.json"
    save_review_items(store, [])

    with pytest.raises(KeyError):
        review_item(store, "missing", "good", today=date(2026, 6, 1))
