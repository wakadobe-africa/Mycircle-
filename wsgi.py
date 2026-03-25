"""
WSGI entry point for production servers (e.g. gunicorn, uWSGI).

Usage:
    gunicorn --bind 0.0.0.0:5000 wsgi:app
"""
from mycirclepkg import app

if __name__ == '__main__':
    app.run()
