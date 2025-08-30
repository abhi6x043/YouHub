# Multi-stage build for YouHub (Vite + Flask + yt-dlp + ffmpeg)

# --- Frontend build stage ---
FROM node:18 AS frontend-build
WORKDIR /app
COPY package.json package-lock.json ./
COPY tsconfig.json ./
RUN npm install
COPY ./src ./src
COPY ./index.html ./
RUN npm run build

# --- Backend build stage ---
FROM python:3.10-slim
WORKDIR /app

# Install ffmpeg and system dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY server ./server

# Copy built frontend to backend static folder
COPY --from=frontend-build /app/dist ./server/static

# Install Python dependencies
RUN pip install --no-cache-dir flask flask-cors yt-dlp beautifulsoup4 requests

# Expose backend port
EXPOSE 5174

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_PORT=5174
ENV FLASK_ENV=production

WORKDIR /app/server

# Start Flask backend
CMD ["python", "app.py"]
