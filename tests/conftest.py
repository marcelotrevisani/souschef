from pathlib import Path

import pytest


@pytest.fixture
def path_data() -> Path:
    return Path(__file__).parent / "data"
