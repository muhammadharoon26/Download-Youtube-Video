# from fastapi import FastAPI, Query
# # from video_download import get_download_links
# import yt_dlp

# def get_download_links(video_url: str):
#     download_links = []
    
#     ydl_opts = {
#         'quiet': False,
#         'format': 'bestvideo+bestaudio/best',
#         'simulate': True,
#         'get_url': True,
#     }
    
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         result = ydl.extract_info(video_url, download=False)
        
#         if 'entries' in result:
#             # This indicates that the URL is a playlist
#             index = 0
#             for entry in result['entries']:
#                 index += 1
#                 download_links.append(process_video(entry, index))
#         else:
#             # Single video
#             download_links.append(process_video(result))
    
#     return download_links

# def process_video(video, index=None):
#     formats = video.get('formats', [])
#     resolutions = set()
#     video_links = {}
#     best_audio_link = None
    
#     # Process 360p separately
#     for f in formats:
#         if f.get('format_id') == '18':
#             video_links['360'] = f['url']
#             resolutions.add('360')
#             break
    
#     # Process other resolutions and find the best audio link
#     for f in formats:
#         if f.get('height') and f.get('vcodec') != 'none' and f.get('protocol') == 'https':
#             resolution = str(f['height'])
#             if resolution not in video_links and resolution != '360':
#                 video_links[resolution] = f['url']
#                 resolutions.add(resolution)
#         elif f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('protocol') == 'https':
#             if best_audio_link is None:
#                 best_audio_link = f['url']
    
#     result = {}
#     for res in sorted(resolutions, key=int):
#         if res == '360':
#             key_prefix = f"{res}" if index is None else f"{res}_{index}"
#             result[key_prefix] = video_links[res]
#         else:
#             video_key = f"{res}" if index is None else f"{res}_{index}"
#             result[video_key] = video_links[res]
    
#     if best_audio_link:
#         audio_key = "Audio" if index is None else f"Audio_{index}"
#         result[audio_key] = best_audio_link
    
#     return result


# app = FastAPI()

# @app.get("/download_links")
# async def download_links(
#     video_url: str = Query(..., description="YouTube video or playlist URL"),
#     # resolution: str = Query("360", description="Desired video resolution")
# ):
#     links = get_download_links(video_url)
#     return {"Video Links":links}


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
    thumbnail_url = ""

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(video_url, download=False)

        if 'entries' in result:
            # URL is a playlist
            for index, entry in enumerate(result['entries'], start=1):
                v_links, a_links = process_video(entry, index)
                video_links.update(v_links)
                audio_links.update(a_links)
        else:
            # Single video
            v_links, a_links = process_video(result)
            video_links.update(v_links)
            audio_links.update(a_links)

        thumbnail_url = result.get('thumbnail', "")

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
            audio_key = f"Audio_{bitrate}kbps" if index is None else f"Audio_{bitrate}kbps_{index}"
            if bitrate > 0:
                audio_links[audio_key] = f['url']

    return video_links, audio_links

@app.get("/download_links")
async def download_links(video_url: str = Query(..., description="YouTube video or playlist URL")):
    video_links, audio_links, thumbnail_url = get_download_links(video_url)
    return {"Video Links": video_links, "Audio Links": audio_links, "Thumbnail": thumbnail_url}