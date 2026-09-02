from datetime import date
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
TODAY = date(2026, 9, 1)


@pytest.fixture
def worklist_path():
    return FIXTURES / "worklist_fixture.csv"


@pytest.fixture
def recon_path():
    return FIXTURES / "RECON_sample.md"


@pytest.fixture
def prev_now_path():
    return FIXTURES / "PCOS_NOW_prev.md"


@pytest.fixture
def today():
    return TODAY
