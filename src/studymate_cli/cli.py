from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from .deadlines import add_deadline, days_left, default_deadline_store, load_deadlines, save_deadlines
from .flashcards import export_cards, parse_flashcards
from .latex import lint_latex_file
from .linkcheck import check_file, results_to_json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="studymate", description="Student-focused CLI toolkit.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    flashcards = subparsers.add_parser("flashcards", help="Generate flashcards from Markdown notes.")
    flashcards.add_argument("input", type=Path)
    flashcards.add_argument("--output", "-o", type=Path, required=True)
    flashcards.add_argument("--format", "-f", choices=["csv", "json"], default="csv")

    deadlines = subparsers.add_parser("deadlines", help="Manage coursework deadlines.")
    deadline_sub = deadlines.add_subparsers(dest="deadline_command", required=True)

    add = deadline_sub.add_parser("add", help="Add a deadline.")
    add.add_argument("title")
    add.add_argument("--date", required=True, help="Due date in YYYY-MM-DD format.")
    add.add_argument("--course")
    add.add_argument("--notes")
    add.add_argument("--store", type=Path, default=default_deadline_store())

    list_cmd = deadline_sub.add_parser("list", help="List deadlines.")
    list_cmd.add_argument("--store", type=Path, default=default_deadline_store())

    export_cmd = deadline_sub.add_parser("export", help="Export deadlines to JSON.")
    export_cmd.add_argument("--store", type=Path, default=default_deadline_store())
    export_cmd.add_argument("--output", "-o", type=Path, required=True)

    linkcheck = subparsers.add_parser("linkcheck", help="Check links in a text, Markdown, or LaTeX file.")
    linkcheck.add_argument("input", type=Path)
    linkcheck.add_argument("--timeout", type=float, default=8.0)
    linkcheck.add_argument("--json", action="store_true")

    latex = subparsers.add_parser("latex-lint", help="Lint a LaTeX file for common thesis/report issues.")
    latex.add_argument("input", type=Path)

    args = parser.parse_args(argv)

    if args.command == "flashcards":
        cards = parse_flashcards(args.input.read_text(encoding="utf-8"))
        export_cards(cards, args.output, args.format)
        print(f"Exported {len(cards)} flashcards to {args.output}")
        return 0

    if args.command == "deadlines":
        if args.deadline_command == "add":
            deadline = add_deadline(args.store, args.title, args.date, args.course, args.notes)
            print(f"Added deadline: {deadline.title} ({deadline.due_date.isoformat()})")
            return 0

        if args.deadline_command == "list":
            deadlines_data = load_deadlines(args.store)
            if not deadlines_data:
                print("No deadlines found.")
                return 0
            for deadline in deadlines_data:
                course = f" [{deadline.course}]" if deadline.course else ""
                left = days_left(deadline)
                print(f"{deadline.due_date.isoformat()} ({left:+d} days){course} - {deadline.title}")
            return 0

        if args.deadline_command == "export":
            deadlines_data = load_deadlines(args.store)
            save_deadlines(args.output, deadlines_data)
            print(f"Exported {len(deadlines_data)} deadlines to {args.output}")
            return 0

    if args.command == "linkcheck":
        results = check_file(args.input, timeout=args.timeout)
        if args.json:
            print(results_to_json(results))
            return 0 if all(result.ok for result in results) else 1

        if not results:
            print("No links found.")
            return 0

        width = shutil.get_terminal_size((100, 20)).columns
        for result in results:
            status = result.status if result.status is not None else "ERR"
            marker = "OK" if result.ok else "FAIL"
            print(f"{marker:4} {status!s:>4} {result.url}"[:width])
            if result.error and not result.ok:
                print(f"     {result.error}"[:width])
        return 0 if all(result.ok for result in results) else 1

    if args.command == "latex-lint":
        issues = lint_latex_file(args.input)
        if not issues:
            print("No LaTeX issues found.")
            return 0
        for issue in issues:
            print(f"{issue.severity.upper():7} line {issue.line}: {issue.message}")
        return 1 if any(issue.severity == "error" for issue in issues) else 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
