from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path

_URL_RE = re.compile(r"https?://[^\s)\]}>\"]+")


@dataclass(frozen=True)
class LinkResult:
    url: str
    ok: bool
    status: int | None = None
    error: str | None = None


def extract_urls(text: str) -> list[str]:
    urls = []
    for match in _URL_RE.finditer(text):
        url = match.group(0).rstrip(".,;:")
        if url not in urls:
            urls.append(url)
    return urls


def check_url(url: str, timeout: float = 8.0) -> LinkResult:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "studymate-cli/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return LinkResult(url=url, ok=200 <= response.status < 400, status=response.status)
    except urllib.error.HTTPError as exc:
        if exc.code == 405:
            return _check_url_get(url, timeout)
        return LinkResult(url=url, ok=False, status=exc.code, error=str(exc))
    except Exception as exc:  # pragma: no cover - network errors vary by platform
        return LinkResult(url=url, ok=False, error=str(exc))


def _check_url_get(url: str, timeout: float) -> LinkResult:
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "studymate-cli/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return LinkResult(url=url, ok=200 <= response.status < 400, status=response.status)
    except urllib.error.HTTPError as exc:
        return LinkResult(url=url, ok=False, status=exc.code, error=str(exc))
    except Exception as exc:  # pragma: no cover
        return LinkResult(url=url, ok=False, error=str(exc))


def check_file(path: Path, timeout: float = 8.0) -> list[LinkResult]:
    text = path.read_text(encoding="utf-8")
    return [check_url(url, timeout=timeout) for url in extract_urls(text)]


def results_to_json(results: list[LinkResult]) -> str:
    return json.dumps([asdict(result) for result in results], ensure_ascii=False, indent=2)
