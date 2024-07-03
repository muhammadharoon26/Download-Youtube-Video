from fastapi import FastAPI, Query
import yt_dlp

def get_download_links(video_url: str):
    video_links = {}
    audio_links = {}

    ydl_opts = {
        'quiet': True,
        'format': 'bestvideo+bestaudio/best',
        'simulate': True,
        'get_url': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(video_url, download=False)

        if 'entries' in result:
            # This indicates that the URL is a playlist
            index = 0
            for entry in result['entries']:
                index += 1
                v_links, a_links = process_video(entry, index)
                video_links.update(v_links)
                audio_links.update(a_links)
        else:
            # Single video
            v_links, a_links = process_video(result)
            video_links.update(v_links)
            audio_links.update(a_links)

    return video_links, audio_links

def process_video(video, index=None):
    formats = video.get('formats', [])
    resolutions = set()
    video_links = {}
    audio_links = {}

    # Process 360p separately
    for f in formats:
        if f.get('format_id') == '18':
            video_links['360'] = f['url']
            resolutions.add('360')
            break

    # Process other resolutions and find audio links
    for f in formats:
        if f.get('height') and f.get('vcodec') != 'none' and f.get('protocol') == 'https':
            resolution = str(f['height'])
            if resolution not in video_links and resolution != '360':
                video_links[resolution] = f['url']
                resolutions.add(resolution)
        elif f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('protocol') == 'https':
            bitrate = f.get('tbr', 0)  # Get the average bitrate
            rounded_bitrate = round(bitrate)
            if rounded_bitrate > 0:
                audio_links[rounded_bitrate] = f['url']

    result_video_links = {}
    result_audio_links = {}

    for res in sorted(resolutions, key=int):
        key_prefix = f"{res}" if index is None else f"{res}_{index}"
        result_video_links[key_prefix] = video_links[res]

    for bitrate, link in audio_links.items():
        audio_key = f"Audio_{bitrate}kbps" if index is None else f"Audio_{bitrate}kbps_{index}"
        result_audio_links[audio_key] = link

    return result_video_links, result_audio_links

app = FastAPI()

@app.get("/download_links")
async def download_links(
    video_url: str = Query(..., description="YouTube video or playlist URL"),
):
    video_links, audio_links = get_download_links(video_url)
    return {"Video Links": video_links, "Audio Links": audio_links}
