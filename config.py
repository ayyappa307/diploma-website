import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key'
    
    # Handle DATABASE_URL or POSTGRES_URL conversion for postgres if needed
    db_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = db_url
    elif os.getenv('VERCEL'):
        # SQLite in writable /tmp directory on Vercel
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/smart_diploma.db'
    else:
        # Local SQLite development
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'smart_diploma.db')
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    if os.getenv('VERCEL'):
        UPLOAD_FOLDER = '/tmp'
    else:
        UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
        
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 MB max upload
