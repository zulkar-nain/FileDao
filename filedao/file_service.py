import os
from datetime import datetime

from flask import current_app, url_for

from .config import IMAGE_EXTENSIONS


def get_uploaded_files():
    files = []
    upload_folder = current_app.config['UPLOAD_FOLDER']
    for filename in sorted(os.listdir(upload_folder)):
        path = os.path.join(upload_folder, filename)
        if not os.path.isfile(path):
            continue

        stat = os.stat(path)
        size_kb = max(1, round(stat.st_size / 1024))
        ext = os.path.splitext(filename)[1].lower()
        files.append({
            'name': filename,
            'size': size_kb,
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%b %d'),
            'is_image': ext in IMAGE_EXTENSIONS,
            'preview_url': url_for('main.view_file', filename=filename) if ext in IMAGE_EXTENSIONS else None,
        })
    return files
