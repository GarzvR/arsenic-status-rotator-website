# File: api/add_license.py
from http.server import BaseHTTPRequestHandler
import json
from vercel_kv import kv

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        self.do_OPTIONS()
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        body = json.loads(post_data.decode('utf-8'))
        key = body.get('key')

        if not key:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Key is required"}).encode())
            return

        if kv.get(key) is not None:
            self.send_response(409)
            self.end_headers()
            self.wfile.write(json.dumps({"message": "License already exists"}).encode())
            return

        kv.set(key, "")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({"message": f"License '{key}' added successfully."}).encode())