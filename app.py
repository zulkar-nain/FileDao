import io
import os
from datetime import datetime

import qrcode
from flask import Flask, render_template_string, request, send_from_directory, send_file, redirect, url_for

app = Flask(__name__)

# Directory where uploaded files will be stored
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg'}

# HTML template with a minimal, modern interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Local File Transfer</title>
    <style>
        :root {
            color-scheme: light;
            --bg: #f4f7fb;
            --panel: rgba(255, 255, 255, 0.92);
            --text: #0f172a;
            --muted: #64748b;
            --border: #e2e8f0;
            --accent: #2563eb;
            --accent-2: #4f46e5;
            --surface: #ffffff;
            --surface-2: #f8fafc;
        }

        :root.dark {
            color-scheme: dark;
            --bg: #020617;
            --panel: rgba(15, 23, 42, 0.92);
            --text: #f8fafc;
            --muted: #94a3b8;
            --border: #334155;
            --accent: #60a5fa;
            --accent-2: #8b5cf6;
            --surface: #111827;
            --surface-2: #0f172a;
        }

        * { box-sizing: border-box; }
        html, body {
            min-height: 100%;
        }
        body {
            margin: 0;
            min-height: 100vh;
            font-family: Inter, "Segoe UI", Roboto, sans-serif;
            color: var(--text);
            display: grid;
            place-items: center;
            padding: 24px;
            position: relative;
            background: var(--bg);
            transition: background 0.2s ease, color 0.2s ease;
        }

        body::before {
            content: "";
            position: fixed;
            inset: 0;
            z-index: -1;
            background: radial-gradient(circle at top left, rgba(59, 130, 246, 0.18), transparent 20%), radial-gradient(circle at bottom right, rgba(37, 99, 235, 0.12), transparent 16%);
            pointer-events: none;
            opacity: 1;
            transition: background 0.2s ease;
        }

        :root.dark body::before {
            background: radial-gradient(circle at top left, rgba(96, 165, 250, 0.18), transparent 22%), radial-gradient(circle at bottom right, rgba(147, 197, 253, 0.12), transparent 18%);
        }

        .shell {
            position: relative;
            z-index: 1;
            width: min(820px, 100%);
            padding: 28px;
            border-radius: 24px;
            background: var(--panel);
            border: 1px solid rgba(255, 255, 255, 0.45);
            box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
            backdrop-filter: blur(16px);
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
        }

        .title {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 700;
        }

        .header-actions {
            display: flex;
            gap: 8px;
        }

        .ghost {
            padding: 8px 12px;
            border-radius: 999px;
            font-size: 0.9rem;
            font-weight: 600;
            border: 1px solid var(--border);
            background: var(--surface-2);
            color: var(--text);
            cursor: pointer;
        }

        .action-pill {
            padding: 8px 12px;
            border-radius: 999px;
            font-size: 0.9rem;
            font-weight: 600;
            border: 1px solid var(--border);
            background: rgba(37, 99, 235, 0.1);
            color: var(--accent);
        }

        .clear-button {
            margin-left: auto;
            border-radius: 999px;
            padding: 10px 16px;
            border: 1px solid var(--border);
            background: var(--surface-2);
            color: var(--text);
            font-weight: 600;
            cursor: pointer;
        }

        .clear-button:hover,
        .ghost:hover,
        .small-button:hover {
            transform: translateY(-1px);
        }

        .small-button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            min-width: 96px;
            border-radius: 999px;
            padding: 8px 12px;
            border: 1px solid var(--border);
            background: var(--surface-2);
            color: var(--text);
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
        }

        .small-button.primary {
            background: linear-gradient(135deg, var(--accent), var(--accent-2));
            color: white;
            border-color: transparent;
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.18);
        }

        .file-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            justify-content: flex-end;
        }

        .qr-card {
            display: grid;
            grid-template-columns: auto 1fr;
            align-items: center;
            gap: 18px;
            padding: 20px;
            width: min(100%, 420px);
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.12), rgba(129, 140, 248, 0.12));
            border: 1px solid var(--border);
            border-radius: 24px;
            box-shadow: 0 18px 40px rgba(15, 23, 42, 0.06);
        }

        .qr-frame {
            width: 260px;
            height: 260px;
            border-radius: 26px;
            padding: 16px;
            background: white;
            box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.06);
        }

        .qr-frame img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 20px;
        }

        .card {
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 18px;
            background: var(--surface);
            margin-bottom: 16px;
        }

        .card h3 {
            margin: 0 0 10px;
            font-size: 1rem;
        }

        .subtle {
            color: var(--muted);
            font-size: 0.95rem;
            margin: 0 0 14px;
        }

        .hero-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
            margin-bottom: 14px;
        }


        .qr-title {
            font-weight: 700;
            font-size: 0.95rem;
        }

        .qr-subtitle {
            color: var(--muted);
            font-size: 0.83rem;
        }

        form {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
        }

        .dropzone {
            flex: 1;
            min-width: 260px;
            border: 1.5px dashed var(--border);
            border-radius: 16px;
            padding: 16px;
            background: linear-gradient(135deg, var(--surface-2), rgba(37, 99, 235, 0.06));
            cursor: pointer;
            transition: border-color 0.2s ease, transform 0.2s ease, background 0.2s ease;
        }

        .dropzone.drag-over {
            border-color: var(--accent);
            transform: translateY(-1px);
            background: rgba(37, 99, 235, 0.12);
        }

        .dropzone input[type="file"] {
            display: none;
        }

        .dropzone-content {
            display: flex;
            gap: 12px;
            align-items: center;
        }

        .dropzone-icon {
            display: grid;
            place-items: center;
            width: 42px;
            height: 42px;
            border-radius: 12px;
            background: rgba(37, 99, 235, 0.12);
            color: var(--accent);
            font-size: 1.1rem;
        }

        .dropzone-title {
            font-weight: 700;
            display: block;
            margin-bottom: 4px;
        }

        .dropzone-subtitle {
            margin: 0;
            color: var(--muted);
            font-size: 0.9rem;
        }

        button {
            border: none;
            border-radius: 999px;
            padding: 10px 16px;
            background: linear-gradient(135deg, var(--accent), var(--accent-2));
            color: white;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.18);
        }

        button:hover {
            transform: translateY(-1px);
        }

        ul {
            list-style: none;
            padding: 0;
            margin: 0;
            display: grid;
            gap: 10px;
        }

        li.file-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            padding: 12px 14px;
            border-radius: 12px;
            background: var(--surface-2);
            border: 1px solid var(--border);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        li.file-row:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
        }

        .file-main {
            display: flex;
            align-items: center;
            gap: 10px;
            min-width: 0;
        }

        .thumb {
            width: 44px;
            height: 44px;
            object-fit: cover;
            border-radius: 12px;
            border: 1px solid var(--border);
            background: var(--surface);
        }

        .file-icon {
            display: grid;
            place-items: center;
            width: 44px;
            height: 44px;
            border-radius: 12px;
            background: rgba(37, 99, 235, 0.12);
            color: var(--accent);
            font-size: 1rem;
        }

        .file-details {
            display: flex;
            flex-direction: column;
            min-width: 0;
        }

        .file-name {
            font-weight: 600;
            color: var(--text);
            text-decoration: none;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .file-subtitle {
            font-size: 0.82rem;
            color: var(--muted);
            margin-top: 2px;
        }

        .download-pill {
            padding: 7px 10px;
            border-radius: 999px;
            background: rgba(37, 99, 235, 0.1);
            color: var(--accent);
            font-size: 0.82rem;
            font-weight: 600;
            text-decoration: none;
            white-space: nowrap;
        }

        .empty {
            text-align: center;
            color: var(--muted);
            padding: 12px 0;
        }

        @media (max-width: 860px) {
            .shell {
                width: calc(100% - 32px);
                padding: 22px;
            }
            .hero-row {
                flex-direction: column;
                align-items: stretch;
            }
            .hero-row > .card,
            .hero-row > .qr-card {
                width: 100%;
            }
            .qr-card {
                grid-template-columns: 1fr;
                justify-items: center;
                text-align: center;
            }
            .qr-frame {
                width: 220px;
                height: 220px;
                justify-self: center;
            }
        }

        @media (max-width: 640px) {
            body {
                padding: 16px;
            }
            .hero-row {
                gap: 18px;
            }
            .qr-frame {
                width: 180px;
                height: 180px;
            }
            .file-row {
                flex-direction: column;
                align-items: stretch;
            }
            .file-actions {
                justify-content: stretch;
                width: 100%;
            }
            .file-actions .small-button,
            .download-pill {
                width: 100%;
                flex: 1;
            }
            .clear-button {
                width: 100%;
                margin-left: 0;
            }
        }

        @media (max-width: 480px) {
            .shell {
                padding: 18px;
            }
            .qr-frame {
                width: 160px;
                height: 160px;
            }
            .dropzone {
                min-width: auto;
            }
            .file-name {
                white-space: normal;
            }
            .file-actions {
                flex-direction: column;
            }
            .file-actions .small-button,
            .download-pill {
                width: 100%;
            }
        }
    </style>
</head>
<body>

    <div class="shell">
        <div class="header">
            <div>
                <h2 class="title">Local File Share</h2>
                <p class="subtle">Upload and download files in a polished, distraction-free space.</p>
            </div>
            <div class="header-actions">
                <button type="button" class="ghost" id="themeToggle" aria-label="Toggle color theme">🌙</button>
            </div>
        </div>

        <div class="hero-row">
            <div class="card" style="margin-bottom: 0; flex: 1; min-width: 240px;">
                <h3>Upload a file</h3>
                <p class="subtle">Drag a file into the drop area or click to browse from your device.</p>
                <form id="uploadForm" action="/upload" method="post" enctype="multipart/form-data">
                    <label class="dropzone" id="dropzone" for="fileInput">
                        <input type="file" id="fileInput" name="file" required>
                        <div class="dropzone-content">
                            <div class="dropzone-icon">⬆</div>
                            <div>
                                <span class="dropzone-title" id="dropzoneTitle">Drop your file here</span>
                                <p class="dropzone-subtitle" id="dropzoneSubtitle">or click to browse</p>
                            </div>
                        </div>
                    </label>
                    <button type="submit">Upload</button>
                </form>
            </div>
            <div class="qr-card">
                <div class="qr-frame">
                    <img src="{{ url_for('qr_code') }}" alt="QR code to open this page">
                </div>
                <div>
                    <div class="qr-title">Scan to open</div>
                    <div class="qr-subtitle">Quickly access this page from another device.</div>
                </div>
            </div>
        </div>

        <div class="card">
            <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap; margin-bottom:14px;">
                <h3 style="margin:0;">Shared files</h3>
                <form action="{{ url_for('clear_all') }}" method="post" style="margin-left:auto;">
                    <button type="submit" class="clear-button">Delete all files</button>
                </form>
            </div>
            <ul>
                {% for file in files %}
                    <li class="file-row">
                        <div class="file-main">
                            {% if file.is_image %}
                                <img class="thumb" src="{{ file.preview_url }}" alt="{{ file.name }}">
                            {% else %}
                                <div class="file-icon">📄</div>
                            {% endif %}
                            <div class="file-details">
                                <a class="file-name" href="{{ url_for('download_file', filename=file.name) }}">{{ file.name }}</a>
                                <span class="file-subtitle">{{ file.size }} KB • {{ file.modified }}</span>
                            </div>
                        </div>
                        <div class="file-actions">
                            <a class="small-button primary" href="{{ url_for('download_file', filename=file.name) }}">Download</a>
                            <form action="{{ url_for('delete_file', filename=file.name) }}" method="post" style="margin:0;">
                                <button type="submit" class="small-button">Delete</button>
                            </form>
                        </div>
                    </li>
                {% else %}
                    <li class="empty">No files have been shared yet.</li>
                {% endfor %}
            </ul>
        </div>
    </div>

    <script>
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
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    files = []
    for filename in sorted(os.listdir(app.config['UPLOAD_FOLDER'])):
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        stat = os.stat(path)
        size_kb = max(1, round(stat.st_size / 1024))
        ext = os.path.splitext(filename)[1].lower()
        files.append({
            'name': filename,
            'size': size_kb,
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%b %d'),
            'is_image': ext in IMAGE_EXTENSIONS,
            'preview_url': url_for('view_file', filename=filename) if ext in IMAGE_EXTENSIONS else None
        })
    return render_template_string(HTML_TEMPLATE, files=files)

@app.route('/qr.png')
def qr_code():
    target_url = url_for('index', _external=True)
    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4,
    )
    qr.add_data(target_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return send_file(buffer, mimetype='image/png')

@app.route('/view/<path:filename>')
def view_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete/<path:filename>', methods=['POST'])
def delete_file(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(path):
        os.remove(path)
    return redirect(url_for('index'))

@app.route('/clear', methods=['POST'])
def clear_all():
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(path):
            os.remove(path)
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        
    return redirect(url_for('index'))

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    # host='0.0.0.0' exposes the server to the local network
    app.run(host='0.0.0.0', port=5000, debug=True)