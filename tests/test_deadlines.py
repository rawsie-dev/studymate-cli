from datetime import date, datetime

from studymate_cli.deadlines import Deadline, days_left, deadlines_to_ics
from studymate_cli.deadlines import parse_date


def test_parse_date():
    assert parse_date("2026-06-20") == date(2026, 6, 20)


def test_days_left():
    deadline = Deadline(title="Exam", due_date=date(2026, 6, 20))
    assert days_left(deadline, today=date(2026, 6, 10)) == 10


def test_deadlines_to_ics_exports_all_day_event():
    deadline = Deadline(
        title="Linear algebra exam",
        due_date=date(2026, 6, 20),
        course="Math",
        notes="Bring calculator",
    )

    result = deadlines_to_ics([deadline], dtstamp=datetime(2026, 6, 1, 12, 0, 0))

    assert "BEGIN:VCALENDAR\r\n" in result
    assert "BEGIN:VEVENT\r\n" in result
    assert "DTSTAMP:20260601T120000Z\r\n" in result
    assert "DTSTART;VALUE=DATE:20260620\r\n" in result
    assert "SUMMARY:Linear algebra exam\r\n" in result
    assert "DESCRIPTION:Course: Math\\nBring calculator\r\n" in result
    assert "CATEGORIES:Math\r\n" in result
    assert result.endswith("END:VCALENDAR\r\n")


def test_deadlines_to_ics_uses_stable_uid():
    deadline = Deadline(title="Essay", due_date=date(2026, 7, 1), course="Writing")

    first = deadlines_to_ics([deadline], dtstamp=datetime(2026, 6, 1, 12, 0, 0))
    second = deadlines_to_ics([deadline], dtstamp=datetime(2026, 6, 2, 12, 0, 0))

    first_uid = next(line for line in first.splitlines() if line.startswith("UID:"))
    second_uid = next(line for line in second.splitlines() if line.startswith("UID:"))
    assert first_uid == second_uid


def test_deadlines_to_ics_escapes_text_fields():
    deadline = Deadline(
        title="Read chapter 1, 2; and 3",
        due_date=date(2026, 8, 15),
        notes="Line one\nLine two \\ final",
    )

    result = deadlines_to_ics([deadline], dtstamp=datetime(2026, 6, 1, 12, 0, 0))

    assert "SUMMARY:Read chapter 1\\, 2\\; and 3\r\n" in result
    assert "DESCRIPTION:Line one\\nLine two \\\\ final\r\n" in result
