import yt_dlp
import subprocess
import json

# ydl_opts = {
#             'quiet': True,  # Suppress yt-dlp output
#             'format': 'bestaudio/best',  # Ensure we only deal with audio or best formats
#             # 'default_search': 'ytsearch',  # Use YouTube search
#             'extract_flat': True,  # Get metadata only, no downloads
#             'noplaylist': True,  # Exclude playlists
#         }

# ydl_opts = {
#             'format': 'bestaudio[ext=m4a]/bestaudio',
#             'noplaylist': True,
#             'youtube_include_dash_manifest': False,
#             'youtube_include_hls_manifest': False,
#             'extract_flat': True,
#             'default_search': 'ytsearch',
#         }

# url = 'https://www.youtube.com/watch?v=c7E-tgmFuzw'
# url = "https://www.youtube.com/watch?v=34MrZbciINA"

# with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#     # results = ydl.extract_info(f"ytsearch{1}:{'https://www.youtube.com/watch?v=c7E-tgmFuzw'}", download=False)
#     results = ydl.extract_info(url, download=False)
#     print(results["id"], results["title"], results["url"])
#     # print(results)
#     ffmpeg_options = (
#              f"ffmpeg -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 "
#              f"-i {results['url']} -acodec libopus -f opus -ar 48000 -ac 2 pipe:1"
#          )
#     process = subprocess.Popen(ffmpeg_options.split(), stdout=subprocess.PIPE)
#     # print(results['entries'][0]["url"])

ydl_opts = {
            'quiet': True,  # Suppress yt-dlp output
            'format': 'bestaudio/best',  # Ensure we only deal with audio or best formats
            # 'default_search': 'ytsearch',  # Use YouTube search
            'extract_flat': True,  # Get metadata only, no downloads
            'noplaylist': False,
        }

url = "https://www.youtube.com/playlist?list=PLa_YLjXHBtSpbSc4druh0HrC0AxOjOoCj"

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    results = ydl.extract_info(url, download=False)
    print(results["title"], results["entries"])
    # print(json.dumps(results, indent=4))


# ydl_opts = {
#             'format': 'bestaudio[ext=m4a]/bestaudio',
#             'noplaylist': False,
#             'youtube_include_dash_manifest': False,
#             'youtube_include_hls_manifest': False,
#             'extract_flat': True,
#             'default_search': 'ytsearch',
#         }