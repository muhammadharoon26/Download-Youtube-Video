from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import yt_dlp

app = FastAPI()

def get_download_links(video_url: str):
    ydl_opts = {
        'quiet': True,
        'format': 'bestvideo+bestaudio/best',
        'simulate': True,
        'get_url': True,
        'verbose': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'nocheckcertificate': True
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










# import yt_dlp
# from fastapi import FastAPI, Query, HTTPException
# from fastapi.responses import JSONResponse

# app = FastAPI()

# def extract_video_info(url: str):
#     ydl_opts = {}
    
#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(url, download=False)
            
#             video_info = {
#                 "id": info.get("id", ""),
#                 "title": info.get("title", ""),
#                 "lengthSeconds": str(info.get("duration", "")),
#                 "channelTitle": info.get("channel", ""),
#                 "channelId": info.get("channel_id", ""),
#                 "description": info.get("description", ""),
#                 "allowRatings": info.get("allow_ratings", None),
#                 "viewCount": str(info.get("view_count", "")),
#                 "isPrivate": info.get("is_private", None),
#                 "isUnpluggedCorpus": info.get("is_unplugged_corpus", None),
#                 "isLiveContent": info.get("is_live", None),
#                 "isCrawlable": info.get("crawlable", None),
#                 "isFamilySafe": info.get("age_limit", 0) == 0,
#                 "availableCountries": info.get("availability", []),
#                 "isUnlisted": info.get("visibility", "") == "unlisted",
#                 "category": info.get("categories", [""])[0] if info.get("categories") else "",
#                 "publishDate": info.get("publish_date", ""),
#                 "publishedAt": info.get("upload_date", ""),
#                 "uploadDate": info.get("upload_date", "")
#             }
            
#             return video_info
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# def get_subs_structure(url):
#     sub_options = {
#     'skip_download': True,
#     'writesubtitles': True,
#     'writeautomaticsub': True,
#     'quiet': True,
#     'outtmpl': '%(title)s.%(ext)s',
#     }
#     subs = {}
#     auto_subs = {}
#     allowed_formats = {'vtt', 'json3', 'srv1', 'srv2', 'srv3', 'ttml'}

#     with yt_dlp.YoutubeDL(sub_options) as ydl:
#         info_dict = ydl.extract_info(url, download=False)

#     # Process regular subtitles
#     subtitles = info_dict.get('subtitles')
#     if subtitles:
#         for lang, subs_list in subtitles.items():
#             subs[lang] = {fmt: None for fmt in allowed_formats}
#             for sub in subs_list:
#                 sub_ext = sub.get('ext')
#                 sub_url = sub.get('url')
#                 if sub_ext in allowed_formats and sub_url:
#                     subs[lang][sub_ext] = sub_url

#     # Process auto-generated subtitles
#     auto_subtitles = info_dict.get('automatic_captions')
#     if auto_subtitles:
#         for lang, subs_list in auto_subtitles.items():
#             auto_subs[lang] = {fmt: None for fmt in allowed_formats}
#             for sub in subs_list:
#                 sub_ext = sub.get('ext')
#                 sub_url = sub.get('url')
#                 if sub_ext in allowed_formats and sub_url:
#                     auto_subs[lang][sub_ext] = sub_url

#     return subs, auto_subs

# def get_download_links(video_url: str):
#     ydl_opts = {
#         'quiet': True,
#         'format': 'bestvideo+bestaudio/best',
#         'simulate': True,
#         'get_url': True,
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

#     subs, auto_subs = get_subs_structure(video_url)
#     return video_links, audio_links, subs, auto_subs, thumbnail_url

# def process_video(video, index=None):
#     formats = video.get('formats', [])
#     video_links = {}
#     audio_links = {}

#     # Handle 360p separately
#     for f in formats:
#         if f.get('format_id') == '18':
#             key_prefix = '360' if index is None else f'360_{index}'
#             video_links[key_prefix] = f['url']
#             break

#     for f in formats:
#         if f.get('vcodec') != 'none' and f.get('acodec') == 'none' and f.get('protocol') == 'https':
#             resolution = f.get('height', 'Unknown')
#             key_prefix = f"{resolution}" if index is None else f"{resolution}_{index}"
#             if key_prefix not in video_links and resolution != 360:
#                 video_links[key_prefix] = f['url']
#         elif f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('protocol') == 'https':
#             bitrate = round(f.get('tbr', 0))
#             audio_key = f"{bitrate}kbps" if index is None else f"{bitrate}kbps_{index}"
#             if bitrate > 0:
#                 audio_links[audio_key] = f['url']

#     thumbnail_url = video.get('thumbnail', "")

#     return video_links, audio_links, thumbnail_url

# @app.get("/download_links")
# async def download_links(video_url: str = Query(..., description="YouTube video or playlist URL")):
#     video_links, audio_links, subs, auto_subs, thumbnail = get_download_links(video_url)
#     return {"video_links": video_links, "audio_links": audio_links, "subs": subs, "auto_subs": auto_subs, "thumbnail": thumbnail}

# @app.get("/extract_video_info")
# def get_video_info(url: str = Query(..., description="The YouTube video URL")):
#     video_info = extract_video_info(url)
#     return video_info

# @app.get("/health")
# async def health_check():
#     return JSONResponse(content={"status": "healthy"}, status_code=200)