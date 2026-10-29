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

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
