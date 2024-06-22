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

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "success" or "data" not in data:
                logger.error(f"Resource may not exist: {url}")
                return None

            return data["data"]

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None

        except ValueError as e:
            logger.error(f"Failed to decode JSON response: {e}")
            return None

    @lru_cache()
    def get_catalog(self, id: int):
        response = self.get_api_response(f"content/catalog/{id}")
        return response

    @lru_cache()
    def get_user_subscriptions_list(self):
        data = []
        while True:
            response = self.get_api_response("user/subscriptions-list")
            if response and 'data' in response:
                data.extend(response["data"])
                break
        return data

    @lru_cache()
    def search(self, keyword: str) -> list:
        data = []
        response = self.get_api_response("search/web", {'keyword': keyword})
        if response and 'data' in response:
            data.extend(response["data"])
        return data

    @lru_cache()
    def get_content_show(self, id: int):
        response = self.get_api_response(f"content/content-show/{id}")
        return response

    def save_show(self, id: int,
                  no_tag: bool = False, no_cover: bool = False,
                  episodes: Optional[set] = None):

        from pathlib import Path

        catalog = self.get_catalog(id)
        if catalog is None:
            logger.error(f"Failed to retrieve catalog for id {id}")
            return

        series = self.get_content_show(id)
        if series is None:
            logger.error(f"Failed to retrieve series information for id {id}")
            return

        show_dir = Path(catalog["title"])
        show_dir.mkdir(exist_ok=True)

        human_idx = 1
        for part in catalog["catalog"]:
            for article in part["part"]:
                if episodes and int(article["sort_number"]) not in episodes:
                    continue
                track_number = self.generate_tracknumber(
                    human_idx,
                    catalog["catalog"])
                self.process_media(article, catalog, series, show_dir,
                                   track_number, no_tag, no_cover)
                human_idx += 1

    def process_media(self, article, catalog, series, show_dir,
                      track_number, no_tag, no_cover):
        media_url = self.get_media_url(article)
        if media_url:
            is_video = media_url.endswith('.m3u8') or media_url.endswith('.mp4')
            extension = '.mp4' if is_video else '.mp3'
            filename = sanitize_filename(article["title"]) + extension
            filename = f"{track_number}_{filename}" if track_number else filename
            fname = show_dir / filename

            if is_video:
                self.process_video(media_url, fname)
            else:
                self.process_audio(media_url, fname, article, catalog,
                                   series, track_number, no_tag, no_cover)

    def get_media_url(self, article):
        media_url = article.get("media_key_full_url")
        if not media_url and "media_files" in article:
            media_url = article["media_files"][0].get("media_key_full_url", "")
        return media_url

    def process_video(self, media_url, fname):
        from shutil import which

        if which('ffmpeg') is None:
            print(f"Please install ffmpeg to fetch video: {fname}")
            return

        if not fname.exists():
            command = ['ffmpeg', '-i', media_url, '-c', 'copy', str(fname)]
            try:
                with open(os.devnull, 'w') as devnull:
                    subprocess.run(command, stdout=devnull,
                                   stderr=devnull, check=True)
                print(f"Successfully fetched and saved to {fname}")
            except Exception as e:
                logger.error(f"Failed to fetch video: {str(e)}")

    def process_audio(self, media_url, fname, article, catalog, series,
                      track_number, no_tag, no_cover):
        if not fname.exists():
            try:
                urlretrieve(media_url, fname)
                if not no_tag:
                    self.retag(str(fname), article,
                               catalog, series, track_number)
                if not no_cover:
                    self.retag_cover(str(fname), article,
                                     catalog, series)
                print(f"Successfully fetched and saved to {fname}")
            except Exception as e:
                logger.error(f"Failed to fetch audio: {str(e)}")

    def save_transcript(self, id: int, episodes: Optional[set] = None):

        from pathlib import Path

        catalog = self.get_catalog(id)
        if catalog is None:
            logger.error(f"Failed to retrieve catalog for id {id}")
            return

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
                                  episodes,
                                  human_idx):
        if episodes and int(article["sort_number"]) not in episodes:
            return

        track_number = self.generate_tracknumber(
            human_idx,
            catalog["catalog"])

        fname = show_dir / "{}.html".format(
            sanitize_filename(article["title"])
        )
        fname = show_dir / "{}_{}.html".format(
            track_number,
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
        if catalog is None:
            logger.error(f"Failed to retrieve catalog for id {id}")
            return

        show_dir = Path(catalog["title"])
        show_dir.mkdir(exist_ok=True)

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            human_idx = 1
            for part in catalog["catalog"]:
                for article in part["part"]:
                    futures.append(executor.submit(
                        self.download_with_single_file,
                        article, catalog, show_dir, single_file_exec_path,
                        cookie_file_path, episodes, human_idx
                    ))
                    human_idx += 1

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
