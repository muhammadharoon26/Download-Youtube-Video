# from fastapi import FastAPI, Header, HTTPException, Query
# from fastapi.responses import JSONResponse
# import yt_dlp

# app = FastAPI()

# def get_download_links(video_url: str, bypass_secret: str):
#     headers = {
#         'x-vercel-protection-bypass': bypass_secret,
#         'x-vercel-set-bypass-cookie': 'true'
#     }

#     ydl_opts = {
#         'quiet': True,
#         'format': 'bestvideo+bestaudio/best',
#         'simulate': True,
#         'get_url': True,
#         'nocheckcertificate': True,
#         'http_headers': headers
#     }

#     video_links = {}
#     audio_links = {}
#     thumbnail_url = ""

#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         result = ydl.extract_info(video_url, download=False)
#         if 'entries' in result:  # Playlist
#             for index, entry in enumerate(result['entries']):
#                 v_links, a_links, thumb = process_video(entry, index)
#                 video_links.update(v_links)
#                 audio_links.update(a_links)
#                 if not thumbnail_url and thumb:
#                     thumbnail_url = thumb
#         else:  # Single video
#             v_links, a_links, thumbnail_url = process_video(result)
#             video_links.update(v_links)
#             audio_links.update(a_links)

#     return video_links, audio_links, thumbnail_url

# def process_video(video, index=None):
#     formats = video.get('formats', [])
#     video_links = {}
#     audio_links = {}

#     for f in formats:
#         if f.get('vcodec') != 'none' and f.get('acodec') == 'none' and f.get('protocol') == 'https':
#             resolution = f.get('height', 'Unknown')
#             key_prefix = f"{resolution}" if index is None else f"{resolution}_{index}"
#             if key_prefix not in video_links:
#                 video_links[key_prefix] = f['url']
#         elif f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('protocol') == 'https':
#             bitrate = round(f.get('tbr', 0))
#             audio_key = f"{bitrate}kbps" if index is None else f"{bitrate}kbps_{index}"
#             if bitrate > 0:
#                 audio_links[audio_key] = f['url']

#     thumbnail_url = video.get('thumbnail', "")

#     return video_links, audio_links, thumbnail_url

# @app.get("/download_links")
# async def download_links(
#     video_url: str = Query(..., description="YouTube video or playlist URL"),
#     bypass_secret: str = Header(None)
# ):
#     if not bypass_secret:
#         raise HTTPException(status_code=400, detail="Missing x-vercel-protection-bypass header")
    
#     video_links, audio_links, thumbnail = get_download_links(video_url, bypass_secret)
#     return {"video_links": video_links, "audio_links": audio_links, "thumbnail": thumbnail}

# @app.get("/health")
# async def health_check():
#     return JSONResponse(content={"status": "healthy"}, status_code=200)



from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import yt_dlp

app = FastAPI()


def get_download_links(video_url: str):
    ydl_opts = {
        'quiet': False,
        'format': 'bestvideo+bestaudio/best',
        'simulate': True,
        'get_url': True,
        'verbose': True
    }

    video_links = {}
    audio_links = {}
    thumbnail_url = ""

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(video_url, download=False)
        if 'entries' in result:  # Playlist
            for index, entry in enumerate(result['entries']):
                v_links, a_links, thumb = process_video(entry, index)
                video_links.update(v_links)
                audio_links.update(a_links)
                if not thumbnail_url and thumb:
                    thumbnail_url = thumb
        else:  # Single video
            v_links, a_links, thumbnail_url = process_video(result)
            video_links.update(v_links)
            audio_links.update(a_links)

    return video_links, audio_links, thumbnail_url

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
            audio_key = f"{bitrate}kbps" if index is None else f"{bitrate}kbps_{index}"
            if bitrate > 0:
                audio_links[audio_key] = f['url']

    thumbnail_url = video.get('thumbnail', "")

    return video_links, audio_links, thumbnail_url

@app.get("/download_links")
async def download_links(video_url: str = Query(..., description="YouTube video or playlist URL")):
    video_links, audio_links, thumbnail = get_download_links(video_url)
    return {"video_links": video_links, "audio_links": audio_links, "thumbnail": thumbnail}

@app.get("/health")
async def health_check():
    return JSONResponse(content={"status": "healthy"}, status_code=200)