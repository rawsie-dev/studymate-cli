import json
from studymate_cli.latex import lint_latex, lint_latex_file, issues_to_json


def test_lint_latex_duplicate_and_missing_ref():
    text = r"""
\label{sec:intro}
\label{sec:intro}
See \ref{sec:missing}.
TODO: rewrite
"""
    issues = lint_latex(text)
    messages = [issue.message for issue in issues]
    assert any("Duplicate label" in message for message in messages)
    assert any("no matching label" in message for message in messages)
    assert any("TODO" in message for message in messages)


def test_lint_latex_missing_citation_key():
    text = r"""
Prior work shows this effect \citep{smith2024,missing2025}.
"""
    bibliography = """
@article{smith2024,
  title = {A Useful Paper}
}
"""

    issues = lint_latex(text, bibliography_texts=[bibliography])
    messages = [issue.message for issue in issues]

    assert any("Citation 'missing2025' has no matching bibliography entry" in message for message in messages)
    assert not any("Citation 'smith2024'" in message for message in messages)


def test_lint_latex_duplicate_and_unused_bibliography_keys():
    text = r"""
See \citet{smith2024}.
"""
    bibliography = """
@article{smith2024,
  title = {A Useful Paper}
}
@book{unused2025,
  title = {Unused}
}
@misc{smith2024,
  title = {Duplicate}
}
"""

    issues = lint_latex(text, bibliography_texts=[bibliography])
    messages = [issue.message for issue in issues]

    assert any("Duplicate bibliography key 'smith2024'" in message for message in messages)
    assert any("Bibliography entry 'unused2025' is not cited" in message for message in messages)


def test_lint_latex_file_reads_bibliography_resource(tmp_path):
    tex = tmp_path / "paper.tex"
    bib = tmp_path / "refs.bib"
    tex.write_text(
        r"""
\section{Intro}
See \parencite{known2026,unknown2026}.
\addbibresource{refs.bib}
""",
        encoding="utf-8",
    )
    bib.write_text(
        """
@article{known2026,
  title = {Known}
}
""",
        encoding="utf-8",
    )

    issues = lint_latex_file(tex)
    messages = [issue.message for issue in issues]

    assert any("Citation 'unknown2026' has no matching bibliography entry" in message for message in messages)
    assert not any("Citation 'known2026'" in message for message in messages)

def test_lint_latex_issues_to_json(tmp_path):
    thesis = tmp_path / "thesis.tex"
    
    thesis.write_text(
        "\\label{intro}\n"
        "\\label{intro}\n"
        "TODO: finish this section\n",
        encoding="utf-8"
    )

    payload = json.loads(issues_to_json(lint_latex_file(thesis)))

    assert payload == {
        "findings": [
            {
                "line": 2,
                "severity": "error",
                "message": "Duplicate label 'intro' first defined on line 1."
            },
            {
                "line": 3,
                "severity": "warning",
                "message": "TODO/FIXME/TBD left in document."
            }
        ],
        "summary": {
            "total_issues": 2,
            "errors": 1,
            "warnings": 1,
            "status": "failed"
        }
    }