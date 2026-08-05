import os
from flask import Flask, render_template_string, request, send_from_directory, redirect, url_for

app = Flask(__name__)

# Directory where uploaded files will be stored
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# HTML template with standard upload and download controls
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Local File Transfer</title>
    <style>
        body { font-family: sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; }
        .card { border: 1px solid #ccc; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 8px 0; }
    </style>
</head>
<body>
    <h2>Local Network File Share</h2>
    <div class="card">
        <h3>Upload File</h3>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <button type="submit">Upload</button>
        </form>
    </div>
    <div class="card">
        <h3>Shared Files</h3>
        <ul>
            {% for filename in files %}
                <li><a href="{{ url_for('download_file', filename=filename) }}">{{ filename }}</a></li>
            {% else %}
                <li>No files shared yet.</li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template_string(HTML_TEMPLATE, files=files)

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