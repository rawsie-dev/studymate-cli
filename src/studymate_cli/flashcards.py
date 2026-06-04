from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Flashcard:
    question: str
    answer: str
    source_line: int | None = None


_Q_RE = re.compile(r"^\s*(?:[-*]\s*)?Q(?:uestion)?\s*:\s*(.+?)\s*$", re.IGNORECASE)
_A_RE = re.compile(r"^\s*(?:[-*]\s*)?A(?:nswer)?\s*:\s*(.+?)\s*$", re.IGNORECASE)


def _normalize_anki_field(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_flashcards(markdown: str) -> list[Flashcard]:
    """Extract simple Q/A flashcards from Markdown text."""
    cards: list[Flashcard] = []
    pending_question: tuple[str, int] | None = None

    for line_no, line in enumerate(markdown.splitlines(), start=1):
        q_match = _Q_RE.match(line)
        if q_match:
            pending_question = (q_match.group(1).strip(), line_no)
            continue

        a_match = _A_RE.match(line)
        if a_match and pending_question:
            question, question_line = pending_question
            answer = a_match.group(1).strip()
            if question and answer:
                cards.append(Flashcard(question=question, answer=answer, source_line=question_line))
            pending_question = None

    return cards


def export_cards(cards: list[Flashcard], output: Path, fmt: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "json":
        output.write_text(
            json.dumps([asdict(card) for card in cards], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return

    if fmt == "anki":
        with output.open("w", encoding="utf-8", newline="") as handle:
            handle.write("#separator:tab\n")
            handle.write("#html:false\n")
            handle.write("#notetype:Basic\n")
            handle.write("#deck:StudyMate\n")
            handle.write("#tags:studymate\n")
            writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
            for card in cards:
                writer.writerow(
                    [
                        _normalize_anki_field(card.question),
                        _normalize_anki_field(card.answer),
                    ]
                )
        return

    if fmt == "csv":
        with output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["question", "answer", "source_line"])
            writer.writeheader()
            for card in cards:
                writer.writerow(asdict(card))
        return

    raise ValueError(f"Unsupported flashcard format: {fmt}")
