from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UrlRequest(BaseModel):
    url: str

def extract_youtube_id(url: str):
    match = re.search(r'(?:v=|youtu\.be/|embed/|shorts/)([\w-]{11})', url)
    return match.group(1) if match else None

@app.post("/api/youtube-title")
async def youtube_title(req: UrlRequest):
    video_id = extract_youtube_id(req.url)
    if not video_id:
        return {"error": "Invalid YouTube URL"}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"https://www.youtube.com/watch?v={video_id}")
            html = resp.text
            match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
            title = match.group(1) if match else 'No title found'
            title = title.replace(' - YouTube', '').strip()
            return {"title": title}
    except Exception:
        return {"error": "Failed to fetch title"}
