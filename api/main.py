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

def get_download_links(video_url: str):
    download_links = []
    
    ydl_opts = {
        'quiet': True,
        'format': 'bestvideo+bestaudio/best',
        'simulate': True,
        'get_url': True,
        'nocache': True  # Disable caching
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(video_url, download=False)
        
        if 'entries' in result:
            # This indicates that the URL is a playlist
            index = 0
            for entry in result['entries']:
                index += 1
                download_links.append(process_video(entry, index))
        else:
            # Single video
            download_links.append(process_video(result))
    
    return download_links

def process_video(video, index=None):
    formats = video.get('formats', [])
    resolutions = set()
    video_links = {}
    best_audio_link = None
    
    # Process 360p separately
    for f in formats:
        if f.get('format_id') == '18':
            video_links['360'] = f['url']
            resolutions.add('360')
            break
    
    # Process other resolutions and find the best audio link
    for f in formats:
        if f.get('height') and f.get('vcodec') != 'none' and f.get('protocol') == 'https':
            resolution = str(f['height'])
            if resolution not in video_links and resolution != '360':
                video_links[resolution] = f['url']
                resolutions.add(resolution)
        elif f.get('acodec') != 'none' and f.get('vcodec') == 'none' and f.get('protocol') == 'https':
            if best_audio_link is None:
                best_audio_link = f['url']
    
    result = {}
    for res in sorted(resolutions, key=int):
        if res == '360':
            key_prefix = f"{res}" if index is None else f"{res}_{index}"
            result[key_prefix] = video_links[res]
        else:
            video_key = f"{res}" if index is None else f"{res}_{index}"
            result[video_key] = video_links[res]
    
    if best_audio_link:
        audio_key = "Audio" if index is None else f"Audio_{index}"
        result[audio_key] = best_audio_link
    
    return result


app = FastAPI()

@app.get("/download_links")
async def download_links(
    video_url: str = Query(..., description="YouTube video or playlist URL"),
):
    links = get_download_links(video_url)
    return {"Video Links": links}
