import express from 'express';
import cors from 'cors';
import fetch from 'node-fetch';

const app = express();
const PORT = 5174;

app.use(cors());
app.use(express.json());

// Helper to extract YouTube video ID from URL
function extractYouTubeId(url: string): string | null {
  const match = url.match(/(?:v=|youtu\.be\/|embed\/|shorts\/)([\w-]{11})/);
  return match ? match[1] : null;
}

app.post('/api/youtube-title', async (req, res) => {
  const { url } = req.body;
  if (!url) return res.status(400).json({ error: 'No URL provided' });
  const videoId = extractYouTubeId(url);
  if (!videoId) return res.status(400).json({ error: 'Invalid YouTube URL' });

  try {
    // Fetch the YouTube page and extract the title
    const resp = await fetch(`https://www.youtube.com/watch?v=${videoId}`);
    const html = await resp.text();
    const match = html.match(/<title>(.*?)<\/title>/i);
    let title = match ? match[1] : 'No title found';
    title = title.replace(' - YouTube', '').trim();
    res.json({ title });
  } catch (e) {
    res.status(500).json({ error: 'Failed to fetch title' });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
