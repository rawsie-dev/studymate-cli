from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

_TAG_RE = re.compile(r"(?<!\w)#([A-Za-z0-9_/-]+)")
_WIKI_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


@dataclass(frozen=True)
class ObsidianNote:
    path: str
    title: str
    tags: list[str]
    links: list[str]
    frontmatter: dict[str, str]


def _parse_frontmatter(markdown: str) -> tuple[dict[str, str], str]:
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, markdown

    frontmatter: dict[str, str] = {}
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            body = "\n".join(lines[index + 1 :])
            return frontmatter, body
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key:
            frontmatter[key] = value.strip().strip("\"'")

    return {}, markdown


def _extract_tags(markdown: str, frontmatter: dict[str, str]) -> list[str]:
    tags = set(_TAG_RE.findall(markdown))
    frontmatter_tags = frontmatter.get("tags")
    if frontmatter_tags:
        raw_tags = frontmatter_tags.strip()
        if raw_tags.startswith("[") and raw_tags.endswith("]"):
            raw_tags = raw_tags[1:-1]
        for tag in raw_tags.split(","):
            cleaned = tag.strip().strip("\"'").lstrip("#")
            if cleaned:
                tags.add(cleaned)
    return sorted(tags)


def _extract_links(markdown: str) -> list[str]:
    links = set()
    for raw_link in _WIKI_LINK_RE.findall(markdown):
        link = raw_link.split("|", 1)[0].split("#", 1)[0].strip()
        if link:
            links.add(link)
    return sorted(links)


def parse_obsidian_note(path: Path, vault_path: Path) -> ObsidianNote:
    markdown = path.read_text(encoding="utf-8")
    frontmatter, body = _parse_frontmatter(markdown)
    relative_path = path.relative_to(vault_path).as_posix()
    return ObsidianNote(
        path=relative_path,
        title=frontmatter.get("title") or path.stem,
        tags=_extract_tags(body, frontmatter),
        links=_extract_links(body),
        frontmatter=frontmatter,
    )


def scan_vault(vault_path: Path) -> list[ObsidianNote]:
    if not vault_path.exists():
        raise FileNotFoundError(f"Vault path does not exist: {vault_path}")
    if not vault_path.is_dir():
        raise NotADirectoryError(f"Vault path is not a directory: {vault_path}")

    notes = [
        parse_obsidian_note(path, vault_path)
        for path in sorted(vault_path.rglob("*.md"))
        if ".obsidian" not in path.relative_to(vault_path).parts
    ]
    return notes


def notes_to_json(notes: list[ObsidianNote]) -> str:
    return json.dumps([asdict(note) for note in notes], ensure_ascii=False, indent=2)
