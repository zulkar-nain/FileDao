import os

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg'}
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')


class Config:
    UPLOAD_FOLDER = UPLOAD_FOLDER
    IMAGE_EXTENSIONS = IMAGE_EXTENSIONS
