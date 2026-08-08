const themeToggle = document.getElementById('themeToggle');
const root = document.documentElement;
const savedTheme = localStorage.getItem('file-share-theme');

if (savedTheme === 'dark') {
    root.classList.add('dark');
    themeToggle.textContent = '☀️';
}

themeToggle.addEventListener('click', () => {
    root.classList.toggle('dark');
    const isDark = root.classList.contains('dark');
    themeToggle.textContent = isDark ? '☀️' : '🌙';
    localStorage.setItem('file-share-theme', isDark ? 'dark' : 'light');
});

const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const dropzoneTitle = document.getElementById('dropzoneTitle');
const dropzoneSubtitle = document.getElementById('dropzoneSubtitle');

const updateDropzoneText = (fileName) => {
    if (fileName) {
        dropzoneTitle.textContent = fileName;
        dropzoneSubtitle.textContent = 'Ready to upload';
    } else {
        dropzoneTitle.textContent = 'Drop your file here';
        dropzoneSubtitle.textContent = 'or click to browse';
    }
};

['dragenter', 'dragover'].forEach((eventName) => {
    dropzone.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropzone.classList.add('drag-over');
    });
});

['dragleave', 'drop'].forEach((eventName) => {
    dropzone.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropzone.classList.remove('drag-over');
    });
});

dropzone.addEventListener('drop', (event) => {
    const droppedFile = event.dataTransfer?.files?.[0];
    if (droppedFile) {
        fileInput.files = event.dataTransfer.files;
        updateDropzoneText(droppedFile.name);
    }
});

fileInput.addEventListener('change', () => {
    const selectedFile = fileInput.files?.[0];
    updateDropzoneText(selectedFile ? selectedFile.name : '');
});

async function refreshFileList() {
    try {
        const response = await fetch('/file-list');
        if (!response.ok) return;
        const html = await response.text();
        document.getElementById('fileList').innerHTML = html;
    } catch (error) {
        console.warn('File refresh failed:', error);
    }
}

const socket = io({ transports: ['websocket', 'polling'] });
socket.on('file_list_updated', () => {
    refreshFileList();
});

document.addEventListener('visibilitychange', () => {
    if (!document.hidden) refreshFileList();
});
