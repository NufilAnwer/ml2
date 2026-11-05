// VisionGuard – main.js

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const submitBtn = document.getElementById('submit-btn');
const filePreview = document.getElementById('file-preview');
const previewImg = document.getElementById('preview-img');
const fileInfo = document.getElementById('file-info');
const form = document.getElementById('upload-form');

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

function handleFile(file) {
  if (!file) return;
  const allowed = ['image/jpeg', 'image/png', 'image/bmp', 'image/webp', 'image/gif', 'image/jpg'];
  if (!allowed.includes(file.type) && !file.name.match(/\.(jpg|jpeg|png|bmp|webp|gif)$/i)) {
    alert('Please select a valid image file (JPG, PNG, BMP, WEBP, GIF).');
    return;
  }
  if (file.size > 10 * 1024 * 1024) {
    alert('File is too large. Maximum allowed size is 10 MB.');
    return;
  }

  const reader = new FileReader();
  reader.onload = (e) => {
    previewImg.src = e.target.result;
    fileInfo.textContent = `${file.name}  ·  ${formatBytes(file.size)}`;
    filePreview.style.display = 'block';
    dropZone.querySelector('.drop-zone-inner').style.display = 'none';
  };
  reader.readAsDataURL(file);
  submitBtn.disabled = false;
}

// File input change
fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) handleFile(fileInput.files[0]);
});

// Click on drop zone
dropZone.addEventListener('click', (e) => {
  if (!filePreview.contains(e.target)) {
    fileInput.click();
  }
});

// Drag and drop
dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('drag-over');
});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) {
    fileInput.files = e.dataTransfer.files;
    handleFile(file);
  }
});

// Show spinner on submit
if (form) {
  form.addEventListener('submit', () => {
    const btnText = submitBtn.querySelector('.btn-text');
    const btnSpinner = submitBtn.querySelector('.btn-spinner');
    if (btnText) btnText.style.display = 'none';
    if (btnSpinner) btnSpinner.style.display = 'inline';
    submitBtn.disabled = true;
  });
}

