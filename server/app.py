from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from utils.yt_utils import get_youtube_title, handle_download, check_ffmpeg

app = Flask(__name__)
CORS(app)

SAVE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'entries.txt'))

@app.route('/api/youtube-title', methods=['POST'])
def youtube_title():
    return get_youtube_title(request.get_json(), SAVE_FILE)

@app.route('/api/download', methods=['GET'])
def download():
    return handle_download(request)

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

check_ffmpeg()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5174)
