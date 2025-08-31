import './style.css'

document.querySelector<HTMLDivElement>('#app')!.innerHTML = `
  <div id="header-container">
    <div id="hello-world">YouHub</div>
    <div id="input-container">
      <input id="user-input" type="text" placeholder="Paste a YouTube URL..." />
    </div>
  </div>
  <div id="display-area"></div>
`;

const input = document.getElementById('user-input') as HTMLInputElement;
const inputContainer = document.getElementById('input-container') as HTMLDivElement;
const headerContainer = document.getElementById('header-container') as HTMLDivElement;
const displayArea = document.getElementById('display-area') as HTMLDivElement;

function formatViews(views: string) {
  const n = parseInt(views, 10);
  if (isNaN(n)) return views;
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, '') + 'M';
  if (n >= 1_000) return (n / 1_000).toFixed(0) + 'k';
  return n.toString();
}

function formatIST(dateStr: string) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return dateStr;
  return d.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata', year: 'numeric', month: 'short', day: 'numeric' });
}

function renderVideoInfo(data: any) {
  if (data.error) {
    displayArea.innerHTML = `<div class="error">${data.error}</div>`;
    return;
  }
  displayArea.innerHTML = `
    <div class="video-info-row">
      <div class="video-info" id="video-info">
        <img class="video-thumb" src="${data.thumbnail}" alt="Thumbnail" />
        <div class="video-title">${data.title}</div>
        <div class="video-meta">
          <span>Duration: ${data.length}</span> |
          <span>Uploaded: ${formatIST(data.uploaded)}</span> |
          <span>Views: ${formatViews(data.views)}</span>
        </div>
        <div class="video-desc">${data.description}</div>
      </div>
      <div class="go-btn-col">
        <button id="go-btn" class="go-btn">
          <span>GET</span>
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 16H24M24 16L18 10M24 16L18 22" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <div class="download-btns" style="display:none;">
          <div class="video-download-row">
            <div class="dropdown-group">
              <button class="download-btn video" id="video-dropdown-btn">
                Download Video
                <svg class="dropdown-arrow" width="18" height="18" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z" fill="#fff"/></svg>
              </button>
              <div class="dropdown-menu" id="video-quality-menu" style="display:none;">
                <div class="dropdown-item" data-quality="1">High Quality</div>
                <div class="dropdown-item" data-quality="0">Low Quality</div>
              </div>
            </div>
          </div>
          <button class="download-btn audio">Download Audio</button>
        </div>
      </div>
    </div>
  `;
  const goBtn = document.getElementById('go-btn') as HTMLButtonElement;
  const downloadBtns = document.querySelector('.go-btn-col .download-btns') as HTMLDivElement;
  if (goBtn && downloadBtns) {
    goBtn.addEventListener('click', () => {
      downloadBtns.style.display = 'flex';
      goBtn.classList.add('go-btn-active');
    });
    const videoBtn = downloadBtns.querySelector('#video-dropdown-btn') as HTMLButtonElement;
    const audioBtn = downloadBtns.querySelector('.download-btn.audio') as HTMLButtonElement;
    const qualityMenu = downloadBtns.querySelector('#video-quality-menu') as HTMLDivElement;
    if (videoBtn && qualityMenu) {
      videoBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        qualityMenu.style.display = qualityMenu.style.display === 'block' ? 'none' : 'block';
      });
      document.addEventListener('click', (e) => {
        if (!videoBtn.contains(e.target as Node) && !qualityMenu.contains(e.target as Node)) {
          qualityMenu.style.display = 'none';
        }
      });
      qualityMenu.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', () => {
          const hq = (item as HTMLElement).getAttribute('data-quality');
          qualityMenu.style.display = 'none';
          if (window.lastUrl) {
            window.open(`http://localhost:5174/api/download?url=${encodeURIComponent(window.lastUrl)}&mode=video&hq=${hq}`, '_blank');
          }
        });
      });
    }
    if (audioBtn) {
      audioBtn.addEventListener('click', () => {
        if (window.lastUrl) {
          window.open(`http://localhost:5174/api/download?url=${encodeURIComponent(window.lastUrl)}&mode=audio`, '_blank');
        }
      });
    }
  }
}

if (input && displayArea && inputContainer && headerContainer) {
  input.addEventListener('keydown', async (e) => {
    if (e.key === 'Enter') {
      const url = input.value.trim();
      if (!url) return;
      window.lastUrl = url;
      displayArea.innerHTML = '<div class="loading">Loading...</div>';
      headerContainer.classList.add('move-up');
      try {
        const resp = await fetch('http://localhost:5174/api/youtube-title', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url })
        });
        const data = await resp.json();
        renderVideoInfo(data);
      } catch {
        displayArea.innerHTML = '<div class="error">Server error.</div>';
      }
      input.value = '';
    }
  });
}

declare global {
  interface Window {
    lastUrl?: string;
  }
}
