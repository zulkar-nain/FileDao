import os

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg'}
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')


class Config:
    UPLOAD_FOLDER = UPLOAD_FOLDER
    IMAGE_EXTENSIONS = IMAGE_EXTENSIONS
    # Secret key used for signed share tokens. Override with environment variable in production.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

    # Share token settings
    SHARE_TOKEN_EXPIRY = int(os.environ.get('SHARE_TOKEN_EXPIRY', 86400))  # seconds, default 1 day
    SHARE_TOKEN_SALT = os.environ.get('SHARE_TOKEN_SALT', 'file-share')
