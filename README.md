# FileDao — Local File Transfer

Small, minimal Flask app to share files across devices on your local network.

## Features
- Upload and download files from a simple web UI
- Image thumbnail previews
- QR code to open the page on another device
- Instant cross-device updates with Socket.IO push events instead of polling

## Requirements
- Python 3.8+
- (Recommended) use a virtual environment
- Python packages: `Flask`, `Flask-SocketIO`, `eventlet`, `qrcode[pil]`, `Pillow`

Install dependencies:

```bash
# with pip
pip install Flask Flask-SocketIO eventlet qrcode[pil] Pillow

# or if you prefer a requirements file
# echo "Flask\nFlask-SocketIO\neventlet\nqrcode[pil]\nPillow" > requirements.txt
# pip install -r requirements.txt
```

## Run (development)
Windows PowerShell:

```powershell
# activate virtualenv (if present)
.\.venv\Scripts\Activate.ps1
# run the app
python app.py
```

Linux / macOS:

```bash
source .venv/bin/activate
python app.py
```

The server runs on port `5000` by default. From another device on the same network open the IP shown in the console (e.g. `http://192.168.1.118:5000`) or scan the QR code shown in the UI.

## Uploads
- Uploaded files are saved to the `uploads/` directory (created automatically).
- The UI listens for Socket.IO events and updates immediately when files are added, removed, or cleared on any connected device.

## Notes & Troubleshooting
- This uses Flask's development server — do not use it as-is for production.
- If your editor shows red underlines but `python -m py_compile app.py` runs fine, ensure VS Code is using the project virtualenv interpreter and that `Pillow` and `qrcode` are installed in that environment.

## Next steps (optional)
- Add authentication or expiry for shared files.

---
Created by the project workspace scripts.
