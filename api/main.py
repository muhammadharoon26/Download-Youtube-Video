from fastapi import FastAPI, Query
import yt_dlp

app = FastAPI()

def get_download_links(video_url: str):
    ydl_opts = {
        'quiet': True,
        'format': 'bestvideo+bestaudio/best',
        'simulate': True,
        'get_url': True,
    }

    video_links = {}
    audio_links = {}
    thumbnails = {}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(video_url, download=False)

        if 'entries' in result:
            # URL is a playlist
            for index, entry in enumerate(result['entries'], start=1):
                v_links, a_links, thumbnail_url = process_video(entry, index)
                video_links.update(v_links)
                audio_links.update(a_links)
                thumbnails[f"Thumbnail_Video {index}"] = thumbnail_url
        else:
            # Single video
            v_links, a_links, thumbnail_url = process_video(result)
            video_links.update(v_links)
            audio_links.update(a_links)
            thumbnails["Thumbnail"] = thumbnail_url

    return video_links, audio_links, thumbnails

def process_video(video, index=None):
    formats = video.get('formats', [])
    video_links = {}
    audio_links = {}

    # Handle 360p separately
    for f in formats:
        if f.get('format_id') == '18':
            key_prefix = '360' if index is None else f'360_{index}'
            video_links[key_prefix] = f['url']
            break

    for f in formats:
        if f.get('vcodec') != 'none' and f.get('acodec') == 'none' and f.get('protocol') == 'https':
            resolution = f.get('height', 'Unknown')
            key_prefix = f"{resolution}" if index is None else f"{resolution}_{index}"
            if key_prefix not in video_links and resolution != 360:
                video_links[key_prefix] = f['url']
        elif f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('protocol') == 'https':
            bitrate = round(f.get('tbr', 0))
            audio_key = f"Audio_{bitrate}kbps" if index is None else f"Audio_{bitrate}kbps_{index}"
            if bitrate > 0:
                audio_links[audio_key] = f['url']

    thumbnail_url = video.get('thumbnail', "")

    return video_links, audio_links, thumbnail_url

@app.get("/download_links")
async def download_links(video_url: str = Query(..., description="YouTube video or playlist URL")):
    video_links, audio_links, thumbnails = get_download_links(video_url)
    return {"Video Links": video_links, "Audio Links": audio_links, "Thumbnails": thumbnails}