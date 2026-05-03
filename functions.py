from flask import Flask
import serverless_wsgi
from mycirclepkg import app # Import your actual Flask app

def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)
