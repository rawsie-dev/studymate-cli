import json

from studymate_cli.obsidian import notes_to_json, scan_vault


def test_scan_vault_extracts_notes_metadata(tmp_path):
    vault = tmp_path / "vault"
    nested = vault / "Courses" / "Math"
    nested.mkdir(parents=True)
    note = nested / "Linear Algebra.md"
    note.write_text(
        """---
title: Matrices
tags: [math, linear-algebra]
---
# Matrix notes
Connects to [[Determinants|det notes]] and [[Eigenvalues#Basics]].
Review #exam/prep soon.
""",
        encoding="utf-8",
    )

    notes = scan_vault(vault)

    assert len(notes) == 1
    assert notes[0].path == "Courses/Math/Linear Algebra.md"
    assert notes[0].title == "Matrices"
    assert notes[0].tags == ["exam/prep", "linear-algebra", "math"]
    assert notes[0].links == ["Determinants", "Eigenvalues"]
    assert notes[0].frontmatter["title"] == "Matrices"


def test_scan_vault_ignores_obsidian_config(tmp_path):
    vault = tmp_path / "vault"
    (vault / ".obsidian").mkdir(parents=True)
    (vault / ".obsidian" / "config.md").write_text("# internal", encoding="utf-8")
    (vault / "Study.md").write_text("Body #tag", encoding="utf-8")

    notes = scan_vault(vault)

    assert [note.path for note in notes] == ["Study.md"]


def test_notes_to_json(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "Study.md").write_text("Body #tag", encoding="utf-8")

    payload = json.loads(notes_to_json(scan_vault(vault)))

    assert payload == [
        {
            "path": "Study.md",
            "title": "Study",
            "tags": ["tag"],
            "links": [],
            "frontmatter": {},
        }
    ]
