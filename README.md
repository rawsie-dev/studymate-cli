# StudyMate CLI

**StudyMate CLI** is a lightweight open-source command-line toolkit for students. It helps turn Markdown notes into flashcards, manage coursework deadlines, check thesis/report links, and lint LaTeX documents for common academic writing mistakes.

This project is designed for students who keep their notes and assignments in plain text and want a simple local-first workflow without creating accounts or uploading private study materials.

## Features

- Generate flashcards from Markdown notes.
- Export flashcards to CSV or JSON.
- Manage deadlines in a local JSON file.
- Check links in Markdown, LaTeX, and text files.
- Lint LaTeX files for duplicate labels, missing refs, TODOs, and common placeholders.
- Works offline for most commands.
- No required third-party runtime dependencies.

## Why this project exists

Many students already use Markdown, LaTeX, and Git for coursework, but the tooling is often fragmented. StudyMate CLI gives students one small tool for repetitive academic workflow tasks:

- preparing revision cards,
- checking thesis links before submission,
- tracking upcoming deadlines,
- catching common LaTeX mistakes.

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/studymate-cli.git
cd studymate-cli
python -m pip install -e .
```

## Usage

### Generate flashcards from Markdown

StudyMate recognizes these formats:

```markdown
- Q: What is photosynthesis?
- A: The process plants use to convert light energy into chemical energy.

Q: What is Big-O notation?
A: A way to describe algorithmic complexity.
```

Run:

```bash
studymate flashcards examples/notes.md --output flashcards.csv --format csv
studymate flashcards examples/notes.md --output flashcards.json --format json
studymate flashcards examples/notes.md --output flashcards.tsv --format anki
```

### Manage deadlines

```bash
studymate deadlines add "Linear algebra exam" --date 2026-06-20 --course "Math"
studymate deadlines list
studymate deadlines export --output deadlines.json
studymate deadlines export --format ics --output deadlines.ics
```

### Check links

```bash
studymate linkcheck thesis.md
studymate linkcheck thesis.tex --json
```

### Scan an Obsidian vault

```bash
studymate obsidian scan ~/NotesVault
studymate obsidian scan ~/NotesVault --json
```

### Schedule spaced repetition reviews

```bash
studymate srs add "What is active recall?"
studymate srs due
studymate srs review ITEM_ID --rating good
```

### Lint LaTeX

```bash
studymate latex-lint thesis.tex
```

## Development

```bash
python -m pip install -e ".[dev]"
pytest
```

## Project status

This is an early student-focused open-source project. Contributions, bug reports, feature ideas, and documentation improvements are welcome.

Good first issues:

- Add Anki `.apkg` export.
- Add spaced repetition scheduling.
- Add Notion/Obsidian import helpers.
- Add calendar `.ics` export for deadlines.
- Improve LaTeX lint rules.

## License

MIT License.
