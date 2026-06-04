import json
from unittest.mock import patch
from studymate_cli.linkcheck import extract_urls, results_to_json, check_file, LinkResult


def test_extract_urls_deduplicates():
    text = "See https://example.com and https://example.com."
    assert extract_urls(text) == ["https://example.com"]

def test_results_to_json(tmp_path):
    note_file = tmp_path / "notes.md"
    note_file.write_text(
        "Check out https://example.com and https://example.com/this-does-not-exist and https://example.com/this-does-not-exist", 
        encoding="utf-8"
    )

    def temp_check_url(url, timeout=8.0):
        if "this-does-not-exist" in url:
            return LinkResult(url=url, ok=False, status=404, error="HTTP Error 404: Not Found")
        return LinkResult(url=url, ok=True, status=200)
    
    with patch("studymate_cli.linkcheck.check_url", side_effect=temp_check_url):
        payload = json.loads(results_to_json(check_file(note_file)))
    
    assert payload == [
        {
            "url": "https://example.com",
            "ok": True,
            "status": 200,
            "error": None
        },
        {
            "url": "https://example.com/this-does-not-exist",
            "ok": False,
            "status": 404,
            "error": "HTTP Error 404: Not Found"
        }
    ]