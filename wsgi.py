"""WSGI import target; PythonAnywhere configures environment before importing this."""

from app import create_app

application = create_app()
