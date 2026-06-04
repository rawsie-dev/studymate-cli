# StudyMate CLI

**StudyMate CLI** is not a replacement for your note editor. It is a linter and pipeline for academic text: it checks a thesis before submission and turns notes into study cards from the terminal, a script, or CI.

This project is designed for students who write coursework, reports, or theses in Markdown/LaTeX, keep the work in Git, and want a simple local-first workflow without accounts, heavy apps, or uploading private study materials.

## Features

- Generate flashcards from Markdown notes.
- Export flashcards to CSV, JSON, or Anki-compatible TSV.
- Manage deadlines in a local JSON file.
- Export deadlines to iCalendar `.ics`.
- Check links in Markdown, LaTeX, and text files.
- Lint LaTeX files for duplicate labels, missing refs, citation issues, TODOs, and common placeholders.
- Scan Obsidian vaults as plain Markdown folders.
- Schedule local spaced repetition reviews.
- Works offline for most commands.
- No required third-party runtime dependencies.

## Why this project exists

Many students already use Markdown, LaTeX, and Git for coursework, but the final quality checks are still often manual: broken links, forgotten TODOs, dangling `\ref{...}`, duplicate `\label{...}`, missing bibliography keys, and figures that are never referenced. These are the checks people do by eye on the last night before submission, and they are easy to miss.

StudyMate automates that routine. It can run locally while you work, in a Git hook before a commit, or in a GitHub Action before a pull request is merged. The goal is to make academic text checks repeatable enough that the boring mistakes simply do not ship.

StudyMate gives students one small tool for repetitive academic workflow tasks:

- preparing revision cards,
- checking thesis links before submission,
- tracking upcoming deadlines,
- catching common LaTeX mistakes.

## Not another Obsidian

Obsidian is an editor and a knowledge base: you write and read inside it. StudyMate does not try to be your writing workspace. It checks, reports on, and transforms files that already exist.

That makes it a pipeline tool, not a place to live. Comparing StudyMate to Obsidian is like comparing a text editor to a linter: they sit at different points in the workflow. StudyMate can work on top of any editor, including Obsidian, VS Code, Vim, or a plain folder of Markdown and LaTeX files.

## Why a CLI

A command-line tool fits this niche because it can run without a person clicking through a UI:

- It can run from `cron`, pre-commit hooks, CI, or GitHub Actions.
- It composes with scripts through exit codes and `--json` output.
- It does not require an account, a heavy desktop app, or editor plugins.
- It works directly on the same files already stored in the repository.

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
