from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pytubefix import YouTube, Playlist
from pytubefix.exceptions import RegexMatchError, VideoUnavailable

app = FastAPI()

def get_download_links(video_url: str):
    video_links = {}
    audio_links = {}
    thumbnail_url = ""

    try:
        if "playlist" in video_url:
            playlist = Playlist(video_url)
            for index, video in enumerate(playlist.videos):
                v_links, a_links, thumb = process_video(video, index)
                video_links.update(v_links)
                audio_links.update(a_links)
                if not thumbnail_url and thumb:
                    thumbnail_url = thumb
        else:
            video = YouTube(video_url)
            v_links, a_links, thumbnail_url = process_video(video)
            video_links.update(v_links)
            audio_links.update(a_links)
    except (RegexMatchError, VideoUnavailable) as e:
        print(f"Error processing video: {str(e)}")
        return {}, {}, ""

    return video_links, audio_links, thumbnail_url

def process_video(video, index=None):
    video_links = {}
    audio_links = {}

    # Handle 360p separately
    stream_360p = video.streams.filter(progressive=True, resolution="360p").first()
    if stream_360p:
        key_prefix = '360' if index is None else f'360_{index}'
        video_links[key_prefix] = stream_360p.url

    # Handle other video streams
    for stream in video.streams.filter(adaptive=True, only_video=True):
        resolution = stream.resolution
        if resolution:
            key_prefix = resolution if index is None else f"{resolution}_{index}"
            if key_prefix not in video_links and resolution != "360p":
                video_links[key_prefix] = stream.url

    # Handle audio streams
    for stream in video.streams.filter(only_audio=True):
        if stream.abr:
            try:
                bitrate = int(stream.abr.rstrip('kbps'))
                audio_key = f"{bitrate}kbps" if index is None else f"{bitrate}kbps_{index}"
                if bitrate > 0:
                    audio_links[audio_key] = stream.url
            except ValueError:
                print(f"Unable to parse bitrate: {stream.abr}")

    thumbnail_url = video.thumbnail_url

    return video_links, audio_links, thumbnail_url

@app.get("/download_links")
async def download_links(video_url: str = Query(..., description="YouTube video or playlist URL")):
    video_links, audio_links, thumbnail = get_download_links(video_url)
    return {"video_links": video_links, "audio_links": audio_links, "thumbnail": thumbnail}

@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "healthy"}, status_code=200)