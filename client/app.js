const video = document.getElementById('webcam');
const captureBtn = document.getElementById('capture-btn');
const closeBtn = document.getElementById('close-btn');
const bottomBar = document.getElementById('bottom-bar');
const loadingOverlay = document.getElementById('loading-overlay');
const arViewport = document.getElementById('ar-viewport');
const cameraContainer = document.getElementById('camera-container');

let currentAbortController = null;
let streamInstance = null;

async function initCamera() {
  try {
    streamInstance = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: 'environment' } },
      audio: false
    });
    video.srcObject = streamInstance;
  } catch (err) {
    console.error("Camera access error:", err);
    alert("Unable to access the camera.");
  }
}

function loadScript(src) {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) return resolve();
    const script = document.createElement('script');
    script.src = src;
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
}

function showProcessingState() {
  bottomBar.classList.add('hidden');
  loadingOverlay.classList.remove('hidden');
  closeBtn.classList.remove('hidden');
}

function resetState() {
  if (currentAbortController) {
    currentAbortController.abort();
    currentAbortController = null;
  }
  
  // Reload page to reset AR.js global DOM mutations cleanly
  if (!arViewport.classList.contains('hidden')) {
    window.location.reload();
    return;
  }

  loadingOverlay.classList.add('hidden');
  closeBtn.classList.add('hidden');
  bottomBar.classList.remove('hidden');
}

window.addEventListener('DOMContentLoaded', initCamera);

captureBtn.addEventListener('click', async () => {
  showProcessingState();

  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  const base64Image = canvas.toDataURL('image/jpeg', 0.8);
  currentAbortController = new AbortController();

  try {
    const response = await fetch('/api/extract-math', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: base64Image }),
      signal: currentAbortController.signal
    });

    if (!response.ok) throw new Error("Failed to process image.");

    const data = await response.json();
    const plotUrl = `/plt/${encodeURIComponent(data.filename)}?t=${Date.now()}`;

    // Stop native video feed before launching AR mode
    if (streamInstance) {
      streamInstance.getTracks().forEach(track => track.stop());
    }

    // Load A-Frame & AR.js on demand
    await loadScript('https://aframe.io/releases/1.4.2/aframe.min.js');
    await loadScript('https://raw.githack.com/AR-js-org/AR.js/master/aframe/build/aframe-ar.js');

    // Build AR Scene dynamically
    arViewport.innerHTML = `
      <a-scene embedded arjs="sourceType: webcam; debugUIEnabled: false;" vr-mode-ui="enabled: false">
        <a-camera position="0 1.6 0"></a-camera>
        <a-entity id="graph-container" position="0 -1.2 -5" rotation="-75 0 0">
          <a-plane 
            id="matplotlib-graph" 
            width="3" 
            height="3" 
            material="src: url(${plotUrl}); transparent: true; alphaTest: 0.5;">
          </a-plane>
        </a-entity>
      </a-scene>
    `;

    cameraContainer.classList.add('hidden');
    arViewport.classList.remove('hidden');
    loadingOverlay.classList.add('hidden');

  } catch (err) {
    if (err.name === 'AbortError') {
      console.log('API request aborted.');
    } else {
      console.error("Pipeline failed:", err);
      alert("Failed to process image or render plot.");
      resetState();
    }
  }
});

closeBtn.addEventListener('click', resetState);