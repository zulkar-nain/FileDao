import io
import os

import qrcode
from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    render_template_string,
    request,
    send_file,
    send_from_directory,
    url_for,
)

from .file_service import get_uploaded_files
from .sockets import broadcast_file_update
from .config import Config

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    cfg = current_app.config
    return render_template(
        'index.html',
        files=get_uploaded_files(),
        enforce_upload_limit=cfg.get('ENFORCE_UPLOAD_LIMIT', Config.ENFORCE_UPLOAD_LIMIT),
        upload_limit_bytes=cfg.get('UPLOAD_LIMIT_BYTES', Config.UPLOAD_LIMIT_BYTES),
    )


@main_bp.route('/file-list')
def file_list():
    return render_template_string(
        '''
        {% for file in files %}
            <li class="file-row">
                <div class="file-main">
                    {% if file.is_image %}
                        <img class="thumb" src="{{ file.preview_url }}" alt="{{ file.name }}">
                    {% else %}
                        <div class="file-icon">📄</div>
                    {% endif %}
                    <div class="file-details">
                        <a class="file-name" href="{{ url_for('main.download_file', filename=file.name) }}">{{ file.name }}</a>
                        <span class="file-subtitle">{{ file.size }} KB • {{ file.modified }}</span>
                    </div>
                </div>
                <div class="file-actions">
                    <a class="small-button primary" href="{{ url_for('main.download_file', filename=file.name) }}">Download</a>
                    <form action="{{ url_for('main.delete_file', filename=file.name) }}" method="post" style="margin:0;">
                        <button type="submit" class="small-button">Delete</button>
                    </form>
                </div>
            </li>
        {% else %}
            <li class="empty">No files have been shared yet.</li>
        {% endfor %}
    ''',
        files=get_uploaded_files(),
    )


@main_bp.route('/qr.png')
def qr_code():
    target_url = url_for('main.index', _external=True)
    qr = qrcode.QRCode(
        version=4,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4,
    )
    qr.add_data(target_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return send_file(buffer, mimetype='image/png')


@main_bp.route('/view/<path:filename>')
def view_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@main_bp.route('/delete/<path:filename>', methods=['POST'])
def delete_file(filename):
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(path):
        os.remove(path)
    broadcast_file_update()
    return redirect(url_for('main.index'))


@main_bp.route('/clear', methods=['POST'])
def clear_all():
    for filename in os.listdir(current_app.config['UPLOAD_FOLDER']):
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if not os.path.isfile(path):
            continue
        try:
            os.remove(path)
        except PermissionError:
            continue
    broadcast_file_update()
    return redirect(url_for('main.index'))


@main_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename:
        enforce = current_app.config.get('ENFORCE_UPLOAD_LIMIT', Config.ENFORCE_UPLOAD_LIMIT)
        limit = current_app.config.get('UPLOAD_LIMIT_BYTES', Config.UPLOAD_LIMIT_BYTES)

        # Try to determine file size using available attributes, fallback to stream seek
        size = None
        if hasattr(file, 'content_length') and file.content_length:
            size = file.content_length
        elif request.content_length:
            size = request.content_length
        else:
            try:
                file.stream.seek(0, os.SEEK_END)
                size = file.stream.tell()
                file.stream.seek(0)
            except Exception:
                size = None

        if enforce and size is not None and size > limit:
            # Return to index with a helpful message
            human_mb = round(limit / (1024 * 1024))
            return render_template(
                'index.html',
                files=get_uploaded_files(),
                upload_error=f'File too large — maximum allowed is {human_mb} MB.',
                enforce_upload_limit=enforce,
                upload_limit_bytes=limit,
            )

        # Save file normally
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename))
        broadcast_file_update()

    return redirect(url_for('main.index'))


@main_bp.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

