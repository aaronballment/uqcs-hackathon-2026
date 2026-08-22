const video = document.getElementById('webcam');
const captureBtn = document.getElementById('capture-btn');
const closeBtn = document.getElementById('close-btn');
const bottomBar = document.getElementById('bottom-bar');
const loadingOverlay = document.getElementById('loading-overlay');

let currentAbortController = null;

// Initialize native webcam
async function initCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: 'environment' } },
      audio: false
    });
    video.srcObject = stream;
  } catch (err) {
    console.error("Camera access error:", err);
    alert("Unable to access the camera. Please allow camera permissions.");
  }
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
  loadingOverlay.classList.add('hidden');
  closeBtn.classList.add('hidden');
  bottomBar.classList.remove('hidden');
}

window.addEventListener('DOMContentLoaded', initCamera);

captureBtn.addEventListener('click', async () => {
  showProcessingState();

  // 1. Capture frame to canvas
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  // 2. Export base64 image
  const base64Image = canvas.toDataURL('image/jpeg', 0.8);
  currentAbortController = new AbortController();

  try {
    // 3. Post base64 payload to backend
    const response = await fetch('/api/extract-math', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: base64Image }),
      signal: currentAbortController.signal
    });

    if (!response.ok) throw new Error("Failed to process image.");

    const data = await response.json();
    console.log("Extraction complete:", data);

    // 4. Redirect to AR.html with the target image filename in query params
    window.location.href = `/AR.html?filename=${encodeURIComponent(data.filename)}`;
    
  } catch (err) {
    if (err.name === 'AbortError') {
      console.log('API request aborted.');
    } else {
      console.error("Pipeline error:", err);
      alert("Failed to process image or generate plot.");
      resetState();
    }
  }
});

closeBtn.addEventListener('click', resetState);