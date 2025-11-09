# File: server.py
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)
DB_FILE = 'licenses.json'

# Simple HTML for web page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Arsenic License Manager</title>
    <style>body { font-family: sans-serif; background: #222; color: #eee; } .container { max-width: 800px; margin: auto; padding: 20px; } input, button { padding: 10px; margin: 5px; } .license { background: #333; padding: 10px; margin-top: 10px; border-radius: 5px; }</style>
</head>
<body>
    <div class="container">
        <h1>Arsenic License Manager</h1>
        <h2>Add New License</h2>
        <input type="text" id="newLicenseKey" placeholder="Enter new license key">
        <button onclick="addLicense()">Add License</button>
        <div id="status"></div>
        <h2>Current Licenses</h2>
        <div id="licenseList">{{ license_list|safe }}</div>
    </div>
    <script>
        function addLicense() {
            const key = document.getElementById('newLicenseKey').value;
            if (!key) { alert('Please enter a key'); return; }
            // The path is now just /license
            fetch('/license', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({key: key}) })
            .then(res => res.json()).then(data => { document.getElementById('status').innerText = data.message; setTimeout(() => location.reload(), 1500); });
        }
    </script>
</body>
</html>
"""

def load_db():
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    db = load_db()
    license_list_html = ""
    for key, hwid in db.items():
        license_list_html += f'<div class="license"><strong>Key:</strong> {key}<br><strong>HWID:</strong> {hwid if hwid else "Not Used"}</div>'
    return render_template_string(HTML_TEMPLATE, license_list=license_list_html)

# This single route handles both checking (GET) and adding (POST) licenses
@app.route('/license', methods=['GET', 'POST'])
def license_handler():
    # --- Handle POST request to add a license ---
    if request.method == 'POST':
        data = request.get_json()
        key = data.get('key')
        if not key:
            return jsonify({"message": "Key is required"}), 400
        
        db = load_db()
        if key in db:
            return jsonify({"message": "License already exists"}), 409
        
        db[key] = None
        save_db(db)
        return jsonify({"message": f"License '{key}' added successfully."})

    # --- Handle GET request to check a license ---
    if request.method == 'GET':
        license_key = request.args.get('key')
        hwid = request.args.get('hwid')
        if not license_key or not hwid:
            return jsonify({"status": "error", "message": "Missing key or hwid"}), 400

        db = load_db()
        if license_key not in db:
            return jsonify({"status": "invalid"})
        
        stored_hwid = db[license_key]
        if stored_hwid is None:
            db[license_key] = hwid
            save_db(db)
            return jsonify({"status": "valid"})
        elif stored_hwid == hwid:
            return jsonify({"status": "valid"})
        else:
            return jsonify({"status": "used"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)