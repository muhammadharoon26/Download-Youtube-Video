from fastapi import FastAPI, Query
from video_download import get_download_links

app = FastAPI()

@app.get("/download_links")
async def download_links(
    video_url: str = Query(..., description="YouTube video or playlist URL"),
    # resolution: str = Query("360", description="Desired video resolution")
):
    links = get_download_links(video_url)
    return {"download_links": links}