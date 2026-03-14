import yt_dlp

async def download_video_as_mp4(video_url):
    options = {
        'format': 'bestaudio[ext=m4a]/best[ext=mp3]',
        'outtmpl': 'downloaded_videos/downloaded.mp3', # 出力ファイル名のテンプレート
    }
    with yt_dlp.YoutubeDL(options) as ydl:
        video_details = ydl.extract_info(video_url)
        title = video_details['title']
        ydl.download([video_url])

    return title, fr"downloaded_videos\downloaded.mp3"