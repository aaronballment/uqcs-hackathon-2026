const video = document.getElementById('webcam');
const captureBtn = document.getElementById('capture-btn');
const closeBtn = document.getElementById('close-btn');
const bottomBar = document.getElementById('bottom-bar');
const loadingOverlay = document.getElementById('loading-overlay');

let currentAbortController = null;

// Access the device rear camera
async function initCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: { ideal: 'environment' }
      },
      audio: false
    });
    video.srcObject = stream;
  } catch (err) {
    console.error("Camera access error:", err);
    alert("Unable to access the camera. Please allow camera permissions.");
  }
}

// Switch UI to loading state
function showProcessingState() {
  bottomBar.classList.add('hidden');
  loadingOverlay.classList.remove('hidden');
  closeBtn.classList.remove('hidden');
}

// Reset UI to capture state
function resetState() {
  if (currentAbortController) {
    currentAbortController.abort(); // Cancel ongoing fetch if user presses cross
    currentAbortController = null;
  }
  loadingOverlay.classList.add('hidden');
  closeBtn.classList.add('hidden');
  bottomBar.classList.remove('hidden');
}

// Initialize stream on load
window.addEventListener('DOMContentLoaded', initCamera);

// Handle capture
captureBtn.addEventListener('click', async () => {
  // 1. Show UI processing state
  showProcessingState();

  // 2. Draw current video frame to canvas
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  // 3. Export canvas to Base64
  const base64Image = canvas.toDataURL('image/jpeg', 0.8);

  // Setup abort controller so user can cancel via the cross button
  currentAbortController = new AbortController();

  // 4. Send payload to FastAPI endpoint
  try {
    const response = await fetch('/api/extract-math', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: base64Image }),
      signal: currentAbortController.signal
    });

    const data = await response.json();
    console.log("Parsed Math String:", data.latex);
    
    // Hide loading indicator after request completes
    loadingOverlay.classList.add('hidden');
    
    alert(`Extracted Equation: ${data.latex}`);
    
    // Ready for integrating your 3D model canvas/view here!
    
  } catch (err) {
    if (err.name === 'AbortError') {
      console.log('API request aborted by user.');
    } else {
      console.error("Extraction failed:", err);
      alert("Failed to process image. Please try again.");
      resetState();
    }
  }
});

// Handle cross button click (returns user back to photo mode)
closeBtn.addEventListener('click', resetState);