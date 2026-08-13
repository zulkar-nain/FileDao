import os

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg'}
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')


class Config:
    UPLOAD_FOLDER = UPLOAD_FOLDER
    IMAGE_EXTENSIONS = IMAGE_EXTENSIONS
    # Enable or disable server-side enforcement of upload size limit
    ENFORCE_UPLOAD_LIMIT = True
    # Default upload limit (100 MB)
    UPLOAD_LIMIT_BYTES = 100 * 1024 * 1024
