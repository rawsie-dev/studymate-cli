from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
_REF_RE = re.compile(r"\\(?:ref|autoref|eqref)\{([^}]+)\}")
_TODO_RE = re.compile(r"\b(TODO|FIXME|TBD)\b", re.IGNORECASE)
_PLACEHOLDER_RE = re.compile(r"\b(lorem ipsum|insert citation|add source|citation needed)\b", re.IGNORECASE)


@dataclass(frozen=True)
class LatexIssue:
    line: int
    severity: str
    message: str


def lint_latex(text: str) -> list[LatexIssue]:
    issues: list[LatexIssue] = []
    labels: dict[str, int] = {}
    refs: list[tuple[str, int]] = []

    for line_no, line in enumerate(text.splitlines(), start=1):
        for label in _LABEL_RE.findall(line):
            if label in labels:
                issues.append(
                    LatexIssue(
                        line=line_no,
                        severity="error",
                        message=f"Duplicate label '{label}' first defined on line {labels[label]}.",
                    )
                )
            else:
                labels[label] = line_no

        for ref in _REF_RE.findall(line):
            refs.append((ref, line_no))

        if _TODO_RE.search(line):
            issues.append(LatexIssue(line=line_no, severity="warning", message="TODO/FIXME/TBD left in document."))

        if _PLACEHOLDER_RE.search(line):
            issues.append(LatexIssue(line=line_no, severity="warning", message="Placeholder text appears to remain."))

    for ref, line_no in refs:
        if ref not in labels:
            issues.append(LatexIssue(line=line_no, severity="error", message=f"Reference '{ref}' has no matching label."))

    return issues


def lint_latex_file(path: Path) -> list[LatexIssue]:
    return lint_latex(path.read_text(encoding="utf-8"))
