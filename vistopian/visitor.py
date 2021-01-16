import requests
from urllib.parse import urljoin
from urllib.request import urlretrieve, urlcleanup
from logging import getLogger
from functools import lru_cache


logger = getLogger(__name__)


class Visitor:
    def __init__(self, token: str):
        self.token = token

    def get_api_response(self, uri: str, params: dict = None):

        url = urljoin("https://api.vistopia.com.cn/api/v1/", uri)

        if params == None: params = {}
        params.update({"api_token": self.token})

        logger.debug(f"Visiting {url}")

        response = requests.get(url, params=params).json()
        assert response["status"] == "success"
        assert "data" in response.keys()

        return response["data"]


    @lru_cache()
    def get_catalog(self, id: int):
        response = self.get_api_response(f"content/catalog/{id}")
        return response

    @lru_cache()
    def get_user_subscriptions_list(self):
        data = []
        while True:
            response = self.get_api_response(f"user/subscriptions-list")
            data.extend(response["data"])
            break
        return data

    @lru_cache()
    def get_content_show(self, id: int):
        response = self.get_api_response(f"content/content-show/{id}")
        return response

    def save_show(self, id: int, no_tag: bool = False, no_cover: bool = False):

        from pathlib import Path

        catalog = self.get_catalog(id)
        series = self.get_content_show(id)

        show_dir = Path(catalog["title"])
        show_dir.mkdir(exist_ok=True)

        for part in catalog["catalog"]:
            for article in part["part"]:
                fname = show_dir / "{}.mp3".format(article["title"])
                if not fname.exists():
                    urlretrieve(article["media_key_full_url"], fname)

                if not no_tag:
                    self.retag(str(fname), article, catalog, series)
    
                if not no_cover:
                    self.retag_cover(str(fname), article, catalog, series)
 

    @staticmethod
    def retag(fname, article_info, catalog_info, series_info):

        from mutagen.easyid3 import EasyID3

        track = EasyID3(fname)
        track["title"] = article_info["title"]
        track["album"]= series_info["title"]
        track["artist"] = series_info["author"]
        track["tracknumber"] = article_info["sort_number"]
        #track["tracksort"] = article_info["sort_number"]
        track["website"] = article_info["content_url"]
        track.save()


    @staticmethod
    def retag_cover(fname, article_info, catalog_info, series_info):

        from mutagen.id3 import ID3, APIC

        @lru_cache()
        def _get_cover(url: str) -> bytes:
            cover_fname, _ = urlretrieve(url)
            with open(cover_fname, "rb") as fp:
                cover = fp.read()
            urlcleanup()
            return cover

        cover = _get_cover(catalog_info["background_img"])

        track = ID3(fname)
        track["APIC"] = APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=cover)
        track.save()
