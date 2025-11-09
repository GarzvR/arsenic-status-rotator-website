# File: api/check_license.py
from http.server import BaseHTTPRequestHandler
import json
from vercel_kv import kv

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        self.do_OPTIONS()
        query = self.path.split('?', 1)[1] if '?' in self.path else ''
        params = dict(p.split('=') for p in query.split('&'))
        license_key = params.get('key')
        hwid = params.get('hwid')

        if not license_key or not hwid:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": "Missing key or hwid"}).encode())
            return

        stored_hwid = kv.get(license_key)
        if stored_hwid is None:
            response = {"status": "invalid"}
        elif stored_hwid == "":
            kv.set(license_key, hwid)
            response = {"status": "valid"}
        elif stored_hwid == hwid:
            response = {"status": "valid"}
        else:
            response = {"status": "used"}

        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())