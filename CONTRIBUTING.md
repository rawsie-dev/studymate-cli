# Contributing to StudyMate CLI

Thanks for considering a contribution.

## Ways to help

- Report bugs.
- Improve documentation.
- Add examples for student workflows.
- Add tests.
- Suggest new commands.
- Improve Markdown or LaTeX parsing.

## Local setup

```bash
git clone https://github.com/YOUR_USERNAME/studymate-cli.git
cd studymate-cli
python -m pip install -e ".[dev]"
pytest
```

## Pull request checklist

Before opening a PR:

- Add or update tests if behavior changes.
- Update README examples if user-facing behavior changes.
- Keep the CLI output readable.
- Prefer standard-library solutions where practical.

## Code style

This project favors small, readable Python modules and a local-first privacy model. Student notes, deadlines, and thesis files should never be uploaded by default.
