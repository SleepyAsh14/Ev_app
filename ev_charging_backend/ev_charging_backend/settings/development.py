from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# Keep your current SQLite database for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}