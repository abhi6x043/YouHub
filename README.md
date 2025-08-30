# YouHub

A modern webapp to fetch YouTube video info and download video/audio, built with Vite + TypeScript (frontend) and Flask + yt-dlp (backend).

---

## Features
- Bold, animated "YouHub" UI
- Enter a YouTube URL to fetch video info (title, thumbnail, description, duration, upload date, views)
- Animated, aesthetic, and interactive frontend
- Download video (HQ/Low) or audio (MP3) with correct file naming
- All downloads use yt-dlp and ffmpeg for best quality
- Each URL/title is logged to `entries.txt` on the backend

---

## Prerequisites
- **Node.js** (v18+ recommended)
- **npm** (comes with Node)
- **Python 3.8+**
- **pip** (Python package manager)
- **ffmpeg** and **ffprobe** (system binaries, required for audio/video processing)

### Install ffmpeg/ffprobe (Linux)
```sh
sudo apt-get update
sudo apt-get install ffmpeg
```

---

## Frontend Setup (Vite + TypeScript)

1. **Install dependencies:**
   ```sh
   cd /home/abhi/webapp-abhi
   npm install
   ```
2. **Run the frontend dev server:**
   ```sh
   npm run dev
   ```
   The app will be available at `http://localhost:5173` (default Vite port).

3. **Build for production:**
   ```sh
   npm run build
   ```
   Output will be in the `dist/` folder.

---

## Backend Setup (Flask + yt-dlp)

1. **Create a Python virtual environment (recommended):**
   ```sh
   cd /home/abhi/webapp-abhi/server
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **Install Python dependencies:**
   ```sh
   pip install flask flask-cors yt-dlp beautifulsoup4 requests
   ```
3. **Run the backend server:**
   ```sh
   python app.py
   ```
   The backend will run on `http://localhost:5174` by default.

4. **Ensure ffmpeg/ffprobe are in your PATH:**
   - Run `which ffmpeg` and `which ffprobe` to verify.
   - The backend will refuse to start if these are missing.

---

## Docker Setup (All-in-one Container)

You can run both the frontend and backend in a single Docker container using the provided `Dockerfile`.

### 1. Build the Docker image
```sh
docker build -t youhub .
```

### 2. Run the container
```sh
docker run -p 8080:5174 youhub
```
- The app will be available at [http://localhost:8080](http://localhost:8080)
- Flask serves both the API and the built frontend from the same container.

### 3. Development tips
- If you change frontend or backend code, rebuild the image to see changes.
- For local development, you can still run frontend and backend separately as described above.

---

## Usage
- Open the frontend in your browser.
- Enter a YouTube URL, view info, and use the download buttons.
- All downloads are handled by the backend and streamed to the browser.
- Each download is logged in `server/entries.txt`.

---

## Troubleshooting
- **0B/empty downloads:**
  - Ensure ffmpeg/ffprobe are installed and in PATH.
  - Check backend logs for errors.
- **CORS issues:**
  - The backend uses Flask-CORS; ensure both servers are running.
- **Port conflicts:**
  - Change the port in `app.py` or Vite config if needed.

---

## Contributing & Development
- All frontend code is in `src/`.
- All backend code is in `server/app.py`.
- For new features, update both frontend and backend as needed.
- PRs and issues welcome!

---

## License
MIT
