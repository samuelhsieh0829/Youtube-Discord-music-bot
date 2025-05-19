import yt_dlp

# ydl_opts = {
#             'quiet': True,  # Suppress yt-dlp output
#             'format': 'bestaudio/best',  # Ensure we only deal with audio or best formats
#             # 'default_search': 'ytsearch',  # Use YouTube search
#             'extract_flat': True,  # Get metadata only, no downloads
#             'noplaylist': True,  # Exclude playlists
#         }

ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio',
            'noplaylist': True,
            'youtube_include_dash_manifest': False,
            'youtube_include_hls_manifest': False,
            'extract_flat': True,
            'default_search': 'ytsearch',
        }

url = 'https://www.youtube.com/watch?v=c7E-tgmFuzw'

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    # results = ydl.extract_info(f"ytsearch{1}:{'https://www.youtube.com/watch?v=c7E-tgmFuzw'}", download=False)
    results = ydl.extract_info(url, download=False)
    # print(results["id"], results["title"], results["url"])
    print(results)
    # print(results['entries'][0]["url"])