import pytest
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).parent
sys.path.insert(0, str(TESTS_DIR.parent))
from vistopian.visitor import Visitor


@pytest.fixture
def visitor():
    return Visitor(token="")


def test_get_catalog(visitor):
    catalog = visitor.get_catalog(id=11)
    assert catalog
    assert catalog.get("author") == "梁文道"
    assert catalog.get("title") == "八分"

    assert isinstance(catalog.get("catalog"), list)


def test_get_content_show(visitor):
    content_show = visitor.get_content_show(id=11)
    assert content_show.get("author") == "梁文道"
    assert content_show.get("title") == "八分"


# def test_save_transcript(visitor):
#     visitor.save_transcript(id=11)