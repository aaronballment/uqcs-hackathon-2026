const video = document.getElementById('webcam');
const captureBtn = document.getElementById('capture-btn');
const closeBtn = document.getElementById('close-btn');
const bottomBar = document.getElementById('bottom-bar');
const loadingOverlay = document.getElementById('loading-overlay');
const domainControls = document.getElementById('domain-controls');

// Chip elements & slider references
const chipMin = document.getElementById('chip-min');
const chipMax = document.getElementById('chip-max');
const popupMin = document.getElementById('popup-min');
const popupMax = document.getElementById('popup-max');
const sliderMin = document.getElementById('slider-min');
const sliderMax = document.getElementById('slider-max');
const valMin = document.getElementById('val-min');
const valMax = document.getElementById('val-max');

let currentAbortController = null;

async function initCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: 'environment' } },
      audio: false
    });
    video.srcObject = stream;

    video.onloadedmetadata = () => {
      video.play().catch(err => console.error("Playback failed:", err));
    };
  } catch (err) {
    console.error("Camera access error:", err);
    alert("Unable to access the camera. Please allow camera permissions.");
  }
}
// Toggle Popups on Chip Click (using closest to handle inner text clicks)
chipMin.addEventListener('click', (e) => {
  e.stopPropagation();
  const isHidden = popupMin.classList.contains('hidden');
  popupMax.classList.add('hidden');
  
  if (isHidden) {
    popupMin.classList.remove('hidden');
  } else {
    popupMin.classList.add('hidden');
  }
});

chipMax.addEventListener('click', (e) => {
  e.stopPropagation();
  const isHidden = popupMax.classList.contains('hidden');
  popupMin.classList.add('hidden');

  if (isHidden) {
    popupMax.classList.remove('hidden');
  } else {
    popupMax.classList.add('hidden');
  }
});

// Prevent closing when clicking inside the slider popups
popupMin.addEventListener('click', (e) => e.stopPropagation());
popupMax.addEventListener('click', (e) => e.stopPropagation());

// Real-time value display updates
sliderMin.addEventListener('input', (e) => {
  valMin.textContent = e.target.value;
});

sliderMax.addEventListener('input', (e) => {
  valMax.textContent = e.target.value;
});

// Close popups when clicking anywhere outside
document.addEventListener('click', () => {
  popupMin.classList.add('hidden');
  popupMax.classList.add('hidden');
});

function showProcessingState() {
  popupMin.classList.add('hidden');
  popupMax.classList.add('hidden');
  bottomBar.classList.add('hidden');
  domainControls.classList.add('hidden');
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
  domainControls.classList.remove('hidden');
  bottomBar.classList.remove('hidden');
}

window.addEventListener('DOMContentLoaded', initCamera);

captureBtn.addEventListener('click', async () => {
  const minVal = parseFloat(sliderMin.value);
  const maxVal = parseFloat(sliderMax.value);

  if (isNaN(minVal) || isNaN(maxVal) || minVal >= maxVal) {
    alert("Please enter a valid range where Min X is strictly less than Max X.");
    return;
  }

  showProcessingState();

  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth || 1280;
  canvas.height = video.videoHeight || 720;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  const base64Image = canvas.toDataURL('image/jpeg', 0.8);
  currentAbortController = new AbortController();

  try {
    const response = await fetch('/api/extract-math', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        image: base64Image,
        x_min: minVal,
        x_max: maxVal
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