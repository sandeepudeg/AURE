#!/usr/bin/env python3
"""
Elastic Beanstalk entry point for Streamlit application
This file is required by Elastic Beanstalk but Streamlit runs via Procfile
"""

# This file exists to satisfy Elastic Beanstalk's requirement for a WSGI application
# The actual Streamlit app runs via the Procfile command

def application(environ, start_response):
    """Dummy WSGI application - Streamlit runs separately via Procfile"""
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [b'Streamlit is running on port 8501']

if __name__ == '__main__':
    # For local testing
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()
