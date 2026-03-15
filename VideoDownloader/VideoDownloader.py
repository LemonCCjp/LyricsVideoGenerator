import yt_dlp

async def download_video(video_url):
    options = {
        'format': 'bestaudio/best',
        'outtmpl': 'output/downloaded_videos/downloaded.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(video_url, download=True)
            title = info.get("title")

        return title, "output/downloaded_videos/downloaded.mp3"

    except Exception:
        return None, None