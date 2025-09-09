import re
import json
import requests
import os
from bs4 import BeautifulSoup
import yt_dlp
import tempfile
import shutil
from flask import jsonify, send_file


# Check ffmpeg and ffprobe availability at startup
def check_ffmpeg():
    for tool in ['ffmpeg', 'ffprobe']:
        if not shutil.which(tool):
            raise RuntimeError(f"Required tool '{tool}' not found in PATH. Please install it.")

YOUTUBE_API_URL = "https://www.youtube.com/watch?v={video_id}"

# Extract YouTube video ID from URL
def extract_youtube_id(url):
    match = re.search(r'(?:v=|youtu\.be/|embed/|shorts/)([\w-]{11})', url)
    return match.group(1) if match else None

# Get YouTube video title and metadata
def get_youtube_title(data, SAVE_FILE):
    url = data.get('url')
    video_id = extract_youtube_id(url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400
    try:
        resp = requests.get(YOUTUBE_API_URL.format(video_id=video_id))
        html = resp.text
        soup = BeautifulSoup(html, 'html.parser')
        title_tag = soup.find('title')
        title = title_tag.text.replace(' - YouTube', '').strip() if title_tag else 'No title found'
        thumbnail = f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
        desc_tag = soup.find('meta', {'name': 'description'})
        description = desc_tag['content'] if desc_tag else ''
        initial_data = None
        for script in soup.find_all('script'):
            if script.string and 'var ytInitialPlayerResponse' in script.string:
                m = re.search(r'ytInitialPlayerResponse\s*=\s*(\{.*?\});', script.string, re.DOTALL)
                if m:
                    try:
                        initial_data = json.loads(m.group(1))
                    except Exception:
                        pass
                break
        length = uploaded = views = 'N/A'
        if initial_data:
            try:
                length = initial_data['videoDetails']['lengthSeconds']
                length = f"{int(length)//60}:{int(length)%60:02d}"
                views = initial_data['videoDetails']['viewCount']
                uploaded = initial_data['microformat']['playerMicroformatRenderer']['publishDate']
                category = initial_data['microformat']['playerMicroformatRenderer']['category']
                likecount = initial_data['microformat']['playerMicroformatRenderer']['likeCount']
                print(f"Video Category: {category}, Likes: {likecount}")
            except Exception:
                pass
        with open(SAVE_FILE, 'a', encoding='utf-8') as f:
            f.write(f'{url} | {title}\n')
        return jsonify({
            'title': title,
            'thumbnail': thumbnail,
            'description': description,
            'length': length,
            'uploaded': uploaded,
            'views': views
        })
    except Exception:
        return jsonify({'error': 'Failed to fetch title'}), 500

# Handle video/audio download
def handle_download(request):
    url = request.args.get('url')
    mode = request.args.get('mode', 'video')
    hq = request.args.get('hq', '1')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    with tempfile.TemporaryDirectory() as tempdir:
        if mode == 'video':
            ext = 'mp4'
        else:
            ext = 'mp3'
        outtmpl = os.path.join(tempdir, '%(title)s.%(ext)s')
        ydl_opts = {
            'outtmpl': outtmpl,
            'quiet': True,
        }
        if mode == 'audio':
            if hq == '1':
                ydl_opts['format'] = 'bestaudio/best'
            else:
                ydl_opts['format'] = 'bestaudio[abr<=192]/bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
        else:
            if hq == '1':
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
                ydl_opts['merge_output_format'] = 'mp4'
            else:
                ydl_opts['format'] = '18/22/134/135/136/137/160/140'
                ydl_opts['merge_output_format'] = 'mp4'
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                print(f"Video Category: {get_video_category(info)}")
                title = info.get('title', 'video')
                ext = 'mp3' if mode == 'audio' else 'mp4'
                if mode == 'video' and hq == '1':
                    download_name = f"{title}-HQ.{ext}"
                else:
                    download_name = f"{title}.{ext}"
                downloaded_path = os.path.join(tempdir, f"{title}.{ext}")
                if not os.path.exists(downloaded_path):
                    files = os.listdir(tempdir)
                    if files:
                        downloaded_path = os.path.join(tempdir, files[0])
                    else:
                        return jsonify({'error': 'Download failed, file not found.'}), 500
            return send_file(downloaded_path, as_attachment=True, download_name=download_name)
        except Exception as e:
            return jsonify({'error': f'Failed to download: {str(e)}'}), 500

# Get the video category from the metadata
def get_video_category(info):
    try:
        return info.get('categories', ['Unknown'])[0]
    except Exception:
        return 'Unknown'