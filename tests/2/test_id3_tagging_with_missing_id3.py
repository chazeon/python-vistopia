import sys
from pathlib import Path
import shutil
import mutagen

TESTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TESTS_DIR.parent))
sys.path.insert(0, str(TESTS_DIR.parent / "vistopia"))
from vistopia.visitor import Visitor

CURR_TEST_DIR = Path(__file__).parent


# The missing_id3 file is created using the following command:
# ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 0.01 -q:a 9 -acodec libmp3lame regular.mp3
# ffmpeg -i regular.mp3 -map 0:a -codec:a copy -write_id3v1 0 -id3v2_version 0 id3_removed.mp3


def test_id3_tagging_with_missing_id3(tmpdir):

    test_mp3 = tmpdir / "id3_removed.mp3"

    shutil.copyfile(
        CURR_TEST_DIR / "data" / "id3_removed.mp3",
        test_mp3
    )

    Visitor.retag(
        test_mp3,
        article_info={
            "title": "测试标题",
            "sort_number": "7",
            "content_url": "http://example.com",
        },
        series_info={
            "title": "测试系列",
            "author": "测试作者",
        },
        catalog_info={}
    )

    from mutagen.easyid3 import EasyID3
    tag = EasyID3(test_mp3)

    assert tag["title"] == ["测试标题"]
    assert tag["album"] == ["测试系列"]
    assert tag["artist"] == ["测试作者"]

