import http.server
import socketserver
import os

PORT = 8000

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    
    def guess_type(self, path):
        # Ensure .exe files are served with correct MIME type
        if path.endswith('.exe'):
            return 'application/octet-stream'
        return super().guess_type(path)

Handler = MyHttpRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server")
    httpd.serve_forever() 