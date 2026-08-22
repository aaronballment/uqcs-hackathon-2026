const video = document.getElementById('webcam');
const captureBtn = document.getElementById('capture-btn');
const closeBtn = document.getElementById('close-btn');
const bottomBar = document.getElementById('bottom-bar');
const loadingOverlay = document.getElementById('loading-overlay');
const domainOverlay = document.getElementById('domain-overlay');
const setDomainBtn = document.getElementById('set-domain-btn');
const xMinInput = document.getElementById('x-min');
const xMaxInput = document.getElementById('x-max');

let currentAbortController = null;
let domainMin = -10;
let domainMax = 10;

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

// Confirm domain selection overlay and unveil camera shutter
setDomainBtn.addEventListener('click', () => {
  const minVal = parseFloat(xMinInput.value);
  const maxVal = parseFloat(xMaxInput.value);

  if (isNaN(minVal) || isNaN(maxVal) || minVal >= maxVal) {
    alert("Please enter a valid range where Min X is strictly less than Max X.");
    return;
  }

  domainMin = minVal;
  domainMax = maxVal;

  domainOverlay.classList.add('hidden');
  bottomBar.classList.remove('hidden');
});

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
    // 3. Post base64 payload and domain parameters to backend
    const response = await fetch('/api/extract-math', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        image: base64Image,
        x_min: domainMin,
        x_max: domainMax
      }),
      signal: currentAbortController.signal
    });

    if (!response.ok) throw new Error("Failed to process image.");

    const data = await response.json();
    if (data.error) {
      alert(data.error);
      resetState();
    } else {
      window.location.href = `/AR.html?filename=${encodeURIComponent(data.filename)}`;
    }
    
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