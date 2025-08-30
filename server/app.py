from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import re
import requests
import os
from bs4 import BeautifulSoup
import yt_dlp
import tempfile
import shutil

app = Flask(__name__)
CORS(app)

SAVE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'entries.txt'))

YOUTUBE_API_URL = "https://www.youtube.com/watch?v={video_id}"

def extract_youtube_id(url):
    match = re.search(r'(?:v=|youtu\.be/|embed/|shorts/)([\w-]{11})', url)
    return match.group(1) if match else None

@app.route('/api/youtube-title', methods=['POST'])
def youtube_title():
    data = request.get_json()
    url = data.get('url')
    video_id = extract_youtube_id(url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400
    try:
        resp = requests.get(YOUTUBE_API_URL.format(video_id=video_id))
        html = resp.text
        soup = BeautifulSoup(html, 'html.parser')
        # Title
        title_tag = soup.find('title')
        title = title_tag.text.replace(' - YouTube', '').strip() if title_tag else 'No title found'
        # Thumbnail
        thumbnail = f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
        # Description
        desc_tag = soup.find('meta', {'name': 'description'})
        description = desc_tag['content'] if desc_tag else ''
        # Duration, views, likes, upload date (from initial data)
        import json
        import re
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
        length = uploaded = views = likes = 'N/A'
        if initial_data:
            try:
                length = initial_data['videoDetails']['lengthSeconds']
                length = f"{int(length)//60}:{int(length)%60:02d}"
                views = initial_data['videoDetails']['viewCount']
                uploaded = initial_data['microformat']['playerMicroformatRenderer']['publishDate']
                # likes not available without API, set as 'N/A'
            except Exception:
                pass
        # Save entry to file
        with open(SAVE_FILE, 'a', encoding='utf-8') as f:
            f.write(f'{url} | {title}\n')
        return jsonify({
            'title': title,
            'thumbnail': thumbnail,
            'description': description,
            'length': length,
            'uploaded': uploaded,
            'views': views,
            'likes': likes
        })
    except Exception:
        return jsonify({'error': 'Failed to fetch title'}), 500

@app.route('/api/download', methods=['GET'])
def download():
    url = request.args.get('url')
    mode = request.args.get('mode', 'video')  # 'video' or 'audio'
    hq = request.args.get('hq', '1')  # '1' for HQ, '0' for low quality
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    # Use a temp directory for yt-dlp output
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
            ydl_opts['format'] = 'bestaudio/best'
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
                title = info.get('title', 'video')
                ext = 'mp3' if mode == 'audio' else 'mp4'
                if mode == 'video' and hq == '1':
                    download_name = f"{title}-HQ.{ext}"
                else:
                    download_name = f"{title}.{ext}"
                # Find the downloaded file
                downloaded_path = os.path.join(tempdir, f"{title}.{ext}")
                if not os.path.exists(downloaded_path):
                    # Try to find any file in tempdir
                    files = os.listdir(tempdir)
                    if files:
                        downloaded_path = os.path.join(tempdir, files[0])
                    else:
                        return jsonify({'error': 'Download failed, file not found.'}), 500
            return send_file(downloaded_path, as_attachment=True, download_name=download_name)
        except Exception as e:
            return jsonify({'error': f'Failed to download: {str(e)}'}), 500

@app.route('/')
def serve_index():
    static_index = os.path.join(app.root_path, 'static', 'index.html')
    if os.path.exists(static_index):
        return send_from_directory('static', 'index.html')
    return '<h1>YouHub Backend Running</h1><p>Frontend not built. Run <code>npm run build</code> and copy files to server/static.</p>'

@app.route('/<path:path>')
def serve_static(path):
    if path.startswith('api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    static_file = os.path.join(app.root_path, 'static', path)
    if os.path.exists(static_file):
        return send_from_directory('static', path)
    return '', 404

# Check ffmpeg and ffprobe availability at startup
def check_ffmpeg():
    for tool in ['ffmpeg', 'ffprobe']:
        if not shutil.which(tool):
            raise RuntimeError(f"Required tool '{tool}' not found in PATH. Please install it.")

check_ffmpeg()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5174)
