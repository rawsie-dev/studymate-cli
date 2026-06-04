from studymate_cli.linkcheck import extract_urls


def test_extract_urls_deduplicates():
    text = "See https://example.com and https://example.com."
    assert extract_urls(text) == ["https://example.com"]
