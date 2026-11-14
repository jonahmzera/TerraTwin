"""End-to-end checks: every page of the app runs on the pipeline outputs."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from config.settings import PROCESSED_DIR

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["app.py", *sorted(str(p.relative_to(ROOT)) for p in (ROOT / "pages").glob("*.py"))]


@pytest.mark.skipif(not (PROCESSED_DIR / "earth_sites.csv").exists(), reason="pipeline outputs not generated")
@pytest.mark.parametrize("page", PAGES)
def test_page_runs_without_errors(page):
    at = AppTest.from_file(str(ROOT / page), default_timeout=180).run()
    assert not at.exception, [e.value for e in at.exception]
