from studymate_cli.latex import lint_latex


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
