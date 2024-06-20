import concurrent.futures
import requests
import subprocess
import time
import os
from urllib.parse import urljoin
from urllib.request import urlretrieve, urlcleanup
from logging import getLogger
from functools import lru_cache
from typing import Optional
from pathvalidate import sanitize_filename


logger = getLogger(__name__)


class Visitor:
    def __init__(self, token: Optional[str]):
        self.token = token

    def get_api_response(self, uri: str, params: Optional[dict] = None):

        url = urljoin("https://api.vistopia.com.cn/api/v1/", uri)

        if params is None:
            params = {}

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
            response = self.get_api_response("user/subscriptions-list")
            data.extend(response["data"])
            break
        return data

    @lru_cache()
    def search(self, keyword: str) -> list:
        response = self.get_api_response("search/web", {'keyword': keyword})
        return response["data"]

    @lru_cache()
    def get_content_show(self, id: int):
        response = self.get_api_response(f"content/content-show/{id}")
        return response

    def save_show(self, id: int,
                  no_tag: bool = False, no_cover: bool = False,
                  episodes: Optional[set] = None):

        from pathlib import Path

        catalog = self.get_catalog(id)
        series = self.get_content_show(id)

        show_dir = Path(catalog["title"])
        show_dir.mkdir(exist_ok=True)

        idx = 1
        for part in catalog["catalog"]:
            for article in part["part"]:

                if episodes and \
                        int(article["sort_number"]) not in episodes:
                    continue

                tracknumber = self.generate_tracknumber(
                    idx,
                    catalog["catalog"])
                idx += 1

                media_url = article.get("media_key_full_url")
                if not media_url:
                    media_files = article.get("media_files")
                    if media_files and "media_key_full_url" in media_files[0]:
                        media_url = media_files[0]["media_key_full_url"]
                    else:
                        raise ValueError(f"Media URL not found for article: \
                                {article['title']}")

                logger.debug(f"media_url {media_url}")
                is_video = media_url.endswith('.m3u8') or \
                    media_url.endswith('.mp4')
                extension = '.mp4' if is_video else '.mp3'
                filename = sanitize_filename(article["title"]) + extension
                fname = show_dir / filename

                if prefix_index:
                    filename_with_index = "{}_{}".format(tracknumber, filename)
                    fname = show_dir / filename_with_index
                logger.debug(f"fname {fname}")

                if is_video:
                    if not fname.exists():
                        command = [
                            'ffmpeg',
                            '-i', media_url,
                            '-c', 'copy',
                            str(fname)
                        ]
                        try:
                            with open(os.devnull, 'w') as devnull:
                                subprocess.run(command, stdout=devnull,
                                               stderr=devnull, check=True)
                            print(f"Video saved successfully to {fname}")
                        except Exception as e:
                            print(f"Failed to process with ffmpeg: {str(e)}")

                else:
                    if not fname.exists():
                        urlretrieve(media_url, fname)
                        if not no_tag:
                            self.retag(str(fname), article,
                                       catalog, series, tracknumber)
                        if not no_cover:
                            self.retag_cover(str(fname), article,
                                             catalog, series)

    def save_transcript(self, id: int, episodes: Optional[set] = None):

        from pathlib import Path

        catalog = self.get_catalog(id)

        show_dir = Path(catalog["title"])
        show_dir.mkdir(exist_ok=True)

        for part in catalog["catalog"]:
            for article in part["part"]:

                if episodes and \
                        int(article["sort_number"]) not in episodes:
                    continue

                fname = show_dir / "{}.html".format(
                    sanitize_filename(article["title"])
                )
                if not fname.exists():
                    urlretrieve(article["content_url"], fname)

                    with open(fname) as f:
                        content = f.read()

                    content = content.replace(
                        "/assets/article/course.css",
                        "https://api.vistopia.com.cn/assets/article/course.css"
                    )

                    with open(fname, "w") as f:
                        f.write(content)

    def download_with_single_file(self, article,
                                  catalog,
                                  show_dir,
                                  single_file_exec_path,
                                  cookie_file_path,
                                  prefix_index,
                                  episodes,
                                  idx):
        if episodes and int(article["sort_number"]) not in episodes:
            return

        tracknumber = self.generate_tracknumber(
            idx,
            catalog["catalog"])

        fname = show_dir / "{}.html".format(
            sanitize_filename(article["title"])
        )
        if prefix_index:
            fname = show_dir / "{}_{}.html".format(
                tracknumber,
                sanitize_filename(article["title"])
            )
        if not fname.exists():
            command = [
                single_file_exec_path,
                "https://www.vistopia.com.cn/article/"
                + article["article_id"],
                str(fname),
                "--browser-cookies-file=" + cookie_file_path
            ]

            attempts = 0
            max_retries = 3
            timeout_seconds = 60
            retry_delay_seconds = 10

            while attempts < max_retries:
                try:
                    subprocess.run(command, check=True,
                                   timeout=timeout_seconds)
                    print(f"Successfully fetched and saved to {fname}")
                    break
                except subprocess.TimeoutExpired:
                    attempts += 1
                    print(
                        f"Timeout expired for {article['title']}. \
                        Retrying {attempts}/{max_retries}...")
                    time.sleep(retry_delay_seconds)
                except subprocess.CalledProcessError as e:
                    print(f"Failed to fetch page using single-file: {e}")
                    break

            if attempts == max_retries:
                print(
                    "Reached maximum retry attempts. \
                    Please check the network or the URL.")

    def save_transcript_with_single_file(self, id: int,
                                         episodes: Optional[set] = None,
                                         single_file_exec_path: str = "",
                                         cookie_file_path: str = ""):
        from pathlib import Path

        logger.debug(f"save_transcript_with_single_file id {id}")

        catalog = self.get_catalog(id)
        show_dir = Path(catalog["title"])
        show_dir.mkdir(exist_ok=True)

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            idx = 1
            for part in catalog["catalog"]:
                for article in part["part"]:
                    futures.append(executor.submit(
                        self.download_with_single_file,
                        article, catalog, show_dir, single_file_exec_path,
                        cookie_file_path, prefix_index, episodes, idx
                    ))
                    idx += 1

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as exc:
                    print(f"Generated an exception: {exc}")

    @staticmethod
    def retag(
        fname: str,
        article_info: dict,
        catalog_info: dict,
        series_info: dict,
        tracknumber: str,
    ):

        from mutagen.easyid3 import EasyID3
        from mutagen.id3 import ID3NoHeaderError

        try:
            track = EasyID3(fname)
        except ID3NoHeaderError:
            # No ID3 tag found, creating a new ID3 tag
            # See: https://github.com/quodlibet/mutagen/issues/327
            track = EasyID3()

        track['title'] = article_info['title']
        track['album'] = series_info['title']
        track['artist'] = series_info['author']
        track['tracknumber'] = tracknumber
        track['website'] = article_info['content_url']

        try:
            track.save(fname)
        except Exception as e:
            print(f"Error saving ID3 tags: {e}")

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
        track["APIC"] = APIC(encoding=3, mime="image/jpeg",
                             type=3, desc="Cover", data=cover)
        track.save()

    @staticmethod
    def generate_tracknumber(idx: int, catalog: dict) -> str:
        # Calculate the total number of episodes in the show
        total_files = sum(len(part['part']) for part in catalog)
        # Determine the minimum length needed
        # for the identifier based on total files
        min_length = len(str(total_files))
        # Generate a formatted identifier, ensuring it has at least min_length
        # digits, padding with zeros if necessary
        formatted_id = f"{idx:0{min_length}d}"
        return formatted_id
