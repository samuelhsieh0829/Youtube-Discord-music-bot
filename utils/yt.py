import os
import subprocess
import re

from pytube import YouTube
from youtube_api import YouTubeDataAPI
from dotenv import load_dotenv
import yt_dlp

from utils.video import Video
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2
from utils.logger import setup_logger

load_dotenv()

log = setup_logger(__name__)

yt_api_key = os.getenv("YT_TOKEN")

YOUTUBE_URL_RE = re.compile(
    r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w\-]{11})"
)

class YT:
    YT_BASE_URL = "https://www.youtube.com/watch?v="

    def __init__(self):
        if not yt_api_key:
            log.error("No YT API key found.")
        self.yt = YouTubeDataAPI(yt_api_key)

    # def search(self, query:str, max_results=10) -> list[Video]:
    #     if self.yt is None:
    #         log.error("No YT API key found. Cannot search.")
    #         return []
    #     try:
    #         resp = self.yt.search(q=query, max_results=max_results)
    #     except Exception:
    #         log.exception("Error during YT API search")
    #         return [Video(video_id=query, video_title=query)]
    #     videos = []
    #     for video in resp:
    #         videos.append(Video(**video))
    #     return videos

    def search(self, query: str, max_results: int = 10) -> list[Video]:
        if query == "":
            return []
        # yt-dlp options for searching
        ydl_opts = {
            'quiet': True,  # Suppress yt-dlp output
            'format': 'bestaudio/best',  # Ensure we only deal with audio or best formats
            # 'default_search': 'ytsearch',  # Use YouTube search
            'extract_flat': True,  # Get metadata only, no downloads
            'noplaylist': True,  # Exclude playlists
        }

        is_url = YOUTUBE_URL_RE.match(query)

        if not is_url:
            # If the query is not a URL, we can use yt-dlp to search
            # Use yt-dlp to search for the video
            ydl_opts['default_search'] = 'ytsearch'

        try:
                # Perform the search using yt-dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if not is_url:
                    results = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
                    # Convert results into Video objects
                    return [
                        Video(video_id=entry['id'], video_title=entry['title'], url=entry['url'])
                        for entry in results['entries']
                    ]
                else:
                    results = ydl.extract_info(query, download=False)
                    return [
                        Video(video_id=results['id'], video_title=results['title'], url=YT.YT_BASE_URL + results['id'])
                    ]
        
        except Exception:
            log.exception(f"Error during yt-dlp search for query {query}:")
            # Fallback: Assume the query is a video ID
            return [Video(video_id=query, video_title=query)]


    
    def stream(self, video_id:str):
        url = YT.YT_BASE_URL + video_id
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "noplaylist": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            stream_url = info["url"]  # Direct audio stream URL
            # return stream_url

        ffmpeg_options = (
            f"ffmpeg -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 "
            f"-i {stream_url} -acodec libopus -f opus -ar 48000 -ac 2 pipe:1"
        )
        process = subprocess.Popen(ffmpeg_options.split(), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        return process

    @staticmethod    
    def download(target_url:str, filename:str=None) -> list[bool, str]:
        if not target_url.startswith(YT.YT_BASE_URL):
            url = YT.YT_BASE_URL + target_url
        else:
            url = target_url
        
        try:
            ydl_opts = {
                            "format": "bestaudio/best",
                            "outtmpl": f"music\\{filename}",
                            "postprocessors": [
                                {
                                    "key": "FFmpegExtractAudio",
                                    "preferredcodec": "mp3",
                                    "preferredquality": "192",
                                }
                            ],
                        }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
            return [True, filename]
        except Exception as e:
            return [False, e]
        
    @staticmethod    
    def list_music():
        return os.listdir(".\\music")
    
    @staticmethod
    def get_music_title(filename:str):
        audio = MP3(f"music\\{filename}", ID3=ID3)
        title_tag = audio.tags.get("TIT2").text[0]
        return title_tag if title_tag else filename

if __name__ == __file__:
    pass