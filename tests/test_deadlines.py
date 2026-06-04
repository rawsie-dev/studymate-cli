from datetime import date

from studymate_cli.deadlines import Deadline, days_left, parse_date


def test_parse_date():
    assert parse_date("2026-06-20") == date(2026, 6, 20)


def test_days_left():
    deadline = Deadline(title="Exam", due_date=date(2026, 6, 20))
    assert days_left(deadline, today=date(2026, 6, 10)) == 10
