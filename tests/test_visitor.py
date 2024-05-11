import pytest
import sys
from pathlib import Path
import os
import itertools

TESTS_DIR = Path(__file__).parent
sys.path.insert(0, str(TESTS_DIR.parent))
from vistopia.visitor import Visitor


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

def test_save_show(visitor, tmpdir):

    cwd = os.getcwd()
    os.chdir(tmpdir)
    visitor.save_show(id=11, episodes={1})
    os.chdir(cwd)

    expected_file = (
        Path(tmpdir) /
        "八分" /
        "【推荐语】窦文涛：我保证《八分》会给咱们“十分”的收获.mp3"
    )

    assert expected_file.exists()
    assert os.path.getsize(expected_file) > 0



def test_save_transcript(visitor, tmpdir):

    cwd = os.getcwd()
    os.chdir(tmpdir)
    visitor.save_transcript(id=11, episodes={1})
    os.chdir(cwd)

    expected_file = (
        Path(tmpdir) /
        "八分" /
        "【推荐语】窦文涛：我保证《八分》会给咱们“十分”的收获.html"
    )

    assert expected_file.exists()
    assert os.path.getsize(expected_file) > 0

    with open(expected_file, "r", encoding="utf8") as fp:
        line = fp.readline()
        assert line.strip() == "<!DOCTYPE html>"


@pytest.mark.parametrize("keyword, expected", [
    ("八分", (11, "梁文道", "八分", "知识只求八分饱", "content")),
    ("李如一", (19, "李如一", "20世纪十大唱片里程碑", "作为乐器的录音室", "content")),
])
def test_search(visitor: Visitor, keyword: str, expected: tuple):

    data = visitor.search(keyword)
    assert isinstance(data, list)
    for k in ("id", "author", "title", "share_desc", "data_type"):
        assert all([k in item.keys() for item in data])
    assert any([
        (
            int(item["id"]),
            item["author"],
            item["title"],
            item["share_desc"],
            item["data_type"],
        ) == expected for item in data
    ])