from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
_REF_RE = re.compile(r"\\(?:ref|autoref|eqref)\{([^}]+)\}")
_CITE_RE = re.compile(
    r"\\(?:cite\w*|parencite|textcite|autocite|footcite)\*?(?:\[[^\]]*\]){0,2}\{([^}]+)\}"
)
_BIBITEM_RE = re.compile(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}")
_BIB_ENTRY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)", re.IGNORECASE)
_BIB_RESOURCE_RE = re.compile(r"\\(?:bibliography|addbibresource)\{([^}]+)\}")
_TODO_RE = re.compile(r"\b(TODO|FIXME|TBD)\b", re.IGNORECASE)
_PLACEHOLDER_RE = re.compile(r"\b(lorem ipsum|insert citation|add source|citation needed)\b", re.IGNORECASE)


@dataclass(frozen=True)
class LatexIssue:
    line: int
    severity: str
    message: str


def _split_citation_keys(value: str) -> list[str]:
    return [key.strip() for key in value.split(",") if key.strip()]


def _collect_bibliography_keys(texts: list[str]) -> tuple[dict[str, int], list[LatexIssue]]:
    keys: dict[str, int] = {}
    issues: list[LatexIssue] = []

    for text in texts:
        for line_no, line in enumerate(text.splitlines(), start=1):
            line_keys = _BIBITEM_RE.findall(line)
            line_keys.extend(_BIB_ENTRY_RE.findall(line))
            for key in line_keys:
                if key in keys:
                    issues.append(
                        LatexIssue(
                            line=line_no,
                            severity="error",
                            message=f"Duplicate bibliography key '{key}' first defined on line {keys[key]}.",
                        )
                    )
                else:
                    keys[key] = line_no

    return keys, issues


def _bibliography_paths(text: str, base_path: Path) -> list[Path]:
    paths: list[Path] = []
    for match in _BIB_RESOURCE_RE.findall(text):
        for raw_name in match.split(","):
            name = raw_name.strip()
            if not name:
                continue
            path = base_path / name
            if path.suffix != ".bib":
                path = path.with_suffix(".bib")
            paths.append(path)
    return paths


def lint_latex(text: str, bibliography_texts: list[str] | None = None) -> list[LatexIssue]:
    issues: list[LatexIssue] = []
    labels: dict[str, int] = {}
    refs: list[tuple[str, int]] = []
    citations: list[tuple[str, int]] = []
    bibliography_keys, bibliography_issues = _collect_bibliography_keys(bibliography_texts or [text])
    issues.extend(bibliography_issues)

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

        for cite_group in _CITE_RE.findall(line):
            for key in _split_citation_keys(cite_group):
                citations.append((key, line_no))

        if _TODO_RE.search(line):
            issues.append(LatexIssue(line=line_no, severity="warning", message="TODO/FIXME/TBD left in document."))

        if _PLACEHOLDER_RE.search(line):
            issues.append(LatexIssue(line=line_no, severity="warning", message="Placeholder text appears to remain."))

    for ref, line_no in refs:
        if ref not in labels:
            issues.append(LatexIssue(line=line_no, severity="error", message=f"Reference '{ref}' has no matching label."))

    cited_keys = {key for key, _line_no in citations}
    if bibliography_keys:
        for key, line_no in citations:
            if key not in bibliography_keys:
                issues.append(
                    LatexIssue(
                        line=line_no,
                        severity="error",
                        message=f"Citation '{key}' has no matching bibliography entry.",
                    )
                )

        for key, line_no in bibliography_keys.items():
            if key not in cited_keys:
                issues.append(
                    LatexIssue(
                        line=line_no,
                        severity="warning",
                        message=f"Bibliography entry '{key}' is not cited.",
                    )
                )

    return issues


def lint_latex_file(path: Path) -> list[LatexIssue]:
    text = path.read_text(encoding="utf-8")
    bibliography_texts: list[str] = []
    issues: list[LatexIssue] = []

    for bibliography_path in _bibliography_paths(text, path.parent):
        if bibliography_path.exists():
            bibliography_texts.append(bibliography_path.read_text(encoding="utf-8"))
        else:
            issues.append(
                LatexIssue(
                    line=1,
                    severity="warning",
                    message=f"Bibliography file '{bibliography_path}' was not found.",
                )
            )

    issues.extend(lint_latex(text, bibliography_texts or None))
    return issues
