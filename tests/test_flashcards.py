from studymate_cli.flashcards import parse_flashcards


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
