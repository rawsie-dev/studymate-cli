from studymate_cli.flashcards import Flashcard, export_cards, parse_flashcards


def test_parse_bullet_flashcards():
    text = """
- Q: What is a derivative?
- A: A rate of change.
"""
    cards = parse_flashcards(text)
    assert len(cards) == 1
    assert cards[0].question == "What is a derivative?"
    assert cards[0].answer == "A rate of change."


def test_parse_plain_flashcards():
    text = """
Q: What is active recall?
A: Retrieving information from memory.
"""
    cards = parse_flashcards(text)
    assert len(cards) == 1
    assert cards[0].source_line == 2


def test_export_anki_tsv(tmp_path):
    output = tmp_path / "cards.tsv"
    cards = [Flashcard(question="What is active recall?", answer="Retrieving information.")]

    export_cards(cards, output, "anki")

    assert output.read_text(encoding="utf-8") == (
        "#separator:tab\n"
        "#html:false\n"
        "#notetype:Basic\n"
        "#deck:StudyMate\n"
        "#tags:studymate\n"
        "What is active recall?\tRetrieving information.\n"
    )


def test_export_anki_normalizes_multiline_fields(tmp_path):
    output = tmp_path / "cards.tsv"
    cards = [Flashcard(question="What\nis\tspaced repetition?", answer="Review  over\n time.")]

    export_cards(cards, output, "anki")

    assert "What is spaced repetition?\tReview over time.\n" in output.read_text(encoding="utf-8")
