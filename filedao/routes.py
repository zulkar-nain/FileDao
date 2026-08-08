import io
import os

import qrcode
import qrcode.image.svg
import itsdangerous
from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    render_template_string,
    request,
    send_from_directory,
    url_for,
    Response,
)

from .file_service import get_uploaded_files
from .sockets import broadcast_file_update

main_bp = Blueprint('main', __name__)


def _get_serializer():
    return itsdangerous.URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


@main_bp.route('/')
def index():
    return render_template('index.html', files=get_uploaded_files())


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
    qr = qrcode.QRCode(version=4, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=4, border=2)
    qr.add_data(target_url)
    qr.make(fit=True)
    img = qr.make_image(image_factory=qrcode.image.svg.SvgImage)
    buf = io.BytesIO()
    img.save(buf)
    svg = buf.getvalue().decode('utf-8')
    return Response(svg, mimetype='image/svg+xml')


@main_bp.route('/share/<path:filename>')
def share_file(filename):
    # create a time-limited signed token for the filename and present a shareable link + QR
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.isfile(path):
        return "Not found", 404

    s = _get_serializer()
    token = s.dumps({'filename': filename}, salt=current_app.config.get('SHARE_TOKEN_SALT'))
    link = url_for('main.shared_download', token=token, _external=True)

    qr = qrcode.QRCode(version=4, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=4, border=2)
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(image_factory=qrcode.image.svg.SvgImage)
    buf = io.BytesIO()
    img.save(buf)
    svg = buf.getvalue().decode('utf-8')

    return render_template_string(
        '''
        <html><body style="font-family: system-ui, Arial; padding:24px;">
        <h2>Share link for {{ filename }}</h2>
        <p><a href="{{ link }}">{{ link }}</a></p>
        <div style="margin-top:18px;">{{ svg|safe }}</div>
        <p style="margin-top:18px;"><a href="{{ url_for('main.index') }}">Back</a></p>
        </body></html>
        ''',
        filename=filename,
        link=link,
        svg=svg,
    )


@main_bp.route('/s/<token>')
def shared_download(token):
    s = _get_serializer()
    try:
        data = s.loads(token, salt=current_app.config.get('SHARE_TOKEN_SALT'), max_age=current_app.config.get('SHARE_TOKEN_EXPIRY'))
    except itsdangerous.SignatureExpired:
        return "Link expired", 410
    except Exception:
        return "Invalid link", 400

    filename = data.get('filename')
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.isfile(path):
        return "Not found", 404

    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


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
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename))
        broadcast_file_update()

    return redirect(url_for('main.index'))


@main_bp.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
