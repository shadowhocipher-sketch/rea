import sys
from pathlib import Path

import pytest

RENDER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RENDER_DIR))
sys.path.insert(0, str(RENDER_DIR / "examples"))


@pytest.fixture(scope="session")
def test_model(tmp_path_factory):
    import make_test_model

    return make_test_model.main(str(tmp_path_factory.mktemp("model")))
