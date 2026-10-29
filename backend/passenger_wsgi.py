"""
LensVault cPanel Passenger WSGI Entrypoint.
Used by cPanel "Setup Python App" / Phusion Passenger.
"""
import os
import sys

# Add project root and backend virtualenv paths
cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, cwd)

# Set environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as exc:
    import traceback
    error_traceback = traceback.format_exc()
    def application(environ, start_response):
        start_response('500 Internal Server Error', [('Content-Type', 'text/plain; charset=utf-8')])
        output = (
            "==================================================\n"
            " LensVault Backend Startup Exception\n"
            "==================================================\n\n"
            f"{error_traceback}\n\n"
            "Troubleshooting Tips:\n"
            "1. Run 'pip install -r requirements.txt' in the cPanel virtual environment.\n"
            "2. Ensure '/home/texastravels/lensvault/backend/.env' exists with valid credentials.\n"
            "3. Run 'python manage.py migrate' to initialize database tables.\n"
        )
        return [output.encode('utf-8')]
