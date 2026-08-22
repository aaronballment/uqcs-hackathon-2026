const video = document.getElementById('webcam');
const captureBtn = document.getElementById('capture-btn');

// Access the device rear camera
async function initCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: { ideal: 'environment' } // Prefers rear camera on mobile devices
      },
      audio: false
    });
    video.srcObject = stream;
  } catch (err) {
    console.error("Camera access error:", err);
    alert("Unable to access the camera. Please allow camera permissions.");
  }
}

// Initialize stream on load
window.addEventListener('DOMContentLoaded', initCamera);

// Click event handler for capture button
captureBtn.addEventListener('click', () => {
  // Photo capture / API payload hook goes here
  console.log('Capture button pressed');
});