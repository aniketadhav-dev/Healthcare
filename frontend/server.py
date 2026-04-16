#!/usr/bin/env python3
"""
server.py - Simple HTTP server to serve the frontend files.
Run this from the /frontend directory.
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

PORT = 3000

class HealthcareHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve HTML files cleanly."""

    def do_GET(self):
        # Map clean paths to template files
        path = self.path.split('?')[0]  # strip query string

        # Route root to login page
        if path == '/':
            self.path = '/templates/login.html'
        # Route .html requests to templates folder
        elif path.endswith('.html'):
            self.path = f'/templates{path}'
        # Static files served as-is
        
        return super().do_GET()

    def log_message(self, format, *args):
        # Clean logging
        print(f"  {self.address_string()} → {args[0]} {args[1]}")


def main():
    # Change to frontend directory
    frontend_dir = Path(__file__).parent
    os.chdir(frontend_dir)

    with socketserver.TCPServer(("", PORT), HealthcareHandler) as httpd:
        print(f"\n🌐 Frontend server running at http://localhost:{PORT}")
        print(f"   Open http://localhost:{PORT}/login.html to get started\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n⛔ Server stopped.")


if __name__ == "__main__":
    main()
