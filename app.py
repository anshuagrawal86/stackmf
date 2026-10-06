
import os
import json
import datetime
from flask import Flask, send_from_directory, request, jsonify, render_template_string, redirect
try:
    from google.cloud import storage
    storage_client = storage.Client()
    # Use the project ID from the environment or fallback
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT', 'serviceapartments')
    bucket_name = f"{project_id}-stackmf-data"
    bucket = storage_client.bucket(bucket_name)
except Exception as e:
    bucket = None
    print(f"GCS Init Error: {e}")

def load_json(filename):
    if bucket:
        try:
            blob = bucket.blob(filename)
            if blob.exists():
                return json.loads(blob.download_as_text())
        except Exception as e:
            print(f"GCS Load Error: {e}")
    # Local fallback
    local_path = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(local_path):
        with open(local_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_json(filename, data):
    if bucket:
        try:
            blob = bucket.blob(filename)
            blob.upload_from_string(json.dumps(data, indent=2), content_type='application/json')
            return
        except Exception as e:
            print(f"GCS Save Error: {e}")
    # Local fallback
    local_path = os.path.join(os.path.dirname(__file__), filename)
    with open(local_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

LEADS_FILE = 'leads.json'
HITS_FILE = 'hits.json'

app = Flask(__name__, static_folder='.', static_url_path='')

@app.before_request
def enforce_canonical_domain():
    """Consolidates domain authority by 301 redirecting www.stackmf.com to https://stackmf.com."""
    host = request.headers.get('Host', request.host).lower()
    if host.startswith('www.'):
        if request.path.startswith('/google') and request.path.endswith('.html'):
            return None
        clean_path = request.path
        if request.query_string:
            clean_path += '?' + request.query_string.decode('utf-8')
        return redirect(f"https://stackmf.com{clean_path}", code=301)

import threading
import urllib.request
import datetime

EU_COUNTRIES = {'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'}

def get_country_and_increment(ip, headers):
    try:
        user_agent = headers.get('User-Agent', '').lower()
        bot_keywords = ['bot', 'crawl', 'spider', 'slurp', 'yandex', 'headless', 'lighthouse', 'google', 'bing', 'ahrefs', 'semrush', 'python-requests', 'curl', 'wget']
        if any(keyword in user_agent for keyword in bot_keywords):
            return  # Skip counting this bot hit
            
        country = headers.get('CF-IPCountry') or headers.get('X-Country-Code') or headers.get('X-Appengine-Country') or headers.get('CloudFront-Viewer-Country')
        
        if not country and ip:
            ip = ip.split(',')[0].strip()
            try:
                url = f"http://ip-api.com/json/{ip}?fields=countryCode"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=3) as response:
                    data = json.loads(response.read().decode())
                    if data.get('countryCode'):
                        country = data['countryCode']
            except Exception:
                pass
                
        country = country or 'Unknown'
        country = country.upper()
        if country in EU_COUNTRIES:
            country = 'EU'
            
        now = datetime.datetime.utcnow()
        month_key = now.strftime("%Y-%m")
        
        hits = load_json(HITS_FILE) or {"total_hits": 0, "months": {}}
                
        if "months" not in hits:
            hits["months"] = {}
        if month_key not in hits["months"]:
            hits["months"][month_key] = {"total": 0, "countries": {}}
            
        hits["total_hits"] = hits.get("total_hits", 0) + 1
        hits["months"][month_key]["total"] += 1
        hits["months"][month_key]["countries"][country] = hits["months"][month_key]["countries"].get(country, 0) + 1
        
        save_json(HITS_FILE, hits)
            
    except Exception:
        pass

def increment_hit():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    headers_dict = dict(request.headers)
    # Run in background thread to avoid slowing down page load
    threading.Thread(target=get_country_and_increment, args=(ip, headers_dict)).start()

@app.route('/')
def home():
    """Serves the primary StackMF enterprise platform."""
    increment_hit()
    return send_from_directory('.', 'index.html')

@app.route('/robots.txt')
def robots():
    """Serves robots.txt with bot & GEO permissions."""
    return send_from_directory('.', 'robots.txt', mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap():
    """Serves search engine sitemap."""
    return send_from_directory('.', 'sitemap.xml', mimetype='application/xml')

@app.route('/legal')
@app.route('/legal.html')
def legal():
    """Serves statutory legal, IP compliance, and nominative fair use documentation."""
    return send_from_directory('.', 'legal.html')

@app.route('/broadcom-replacement')
@app.route('/broadcom-replacement.html')
def broadcom_replacement():
    """Serves the dedicated Broadcom Mainframe Tool Migration & Replacement landing page."""
    return send_from_directory('.', 'broadcom-replacement.html')

@app.route('/google<token>.html')
def serve_google_verification(token):
    """Serves Google Search Console HTML verification file."""
    return send_from_directory('.', f'google{token}.html', mimetype='text/html; charset=utf-8')

@app.route('/<filename>.txt')
def serve_txt(filename):
    """Serves root text files like llms.txt, robots.txt, IndexNow verification keys."""
    return send_from_directory('.', f'{filename}.txt', mimetype='text/plain; charset=utf-8')

@app.route('/blog')
@app.route('/blog/')
def blog_index():
    """Serves the Mainframe Engineering Knowledge Base Index."""
    return send_from_directory('blog', 'index.html')

@app.route('/blog/resolving-abend-s0c7-data-exception-cobol.html')
@app.route('/blog/resolving-abend-s0c7-data-exception-cobol')
def legacy_soc7_redirect():
    """301 Permanent Redirect to canonical S0C7 runbook."""
    return redirect('/blog/soc7-data-exception-cobol-packed-decimal.html', code=301)

@app.route('/blog/<path:slug>')
def blog_post(slug):
    """Serves individual blog articles, supporting clean URLs without .html extension."""
    if not slug.endswith('.html'):
        candidate = f"{slug}.html"
        if os.path.exists(os.path.join(os.path.dirname(__file__), 'blog', candidate)):
            return send_from_directory('blog', candidate)
    return send_from_directory('blog', slug)

@app.route('/healthz')
def healthz():
    """Google Cloud Run healthcheck endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "stackmf",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }), 200

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    """Handles enterprise consultation bookings and lead captures."""
    try:
        data = request.get_json(silent=True) or request.form.to_dict()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        company = data.get('company', '').strip()
        service = data.get('service', 'General Inquiry').strip()
        message = data.get('message', '').strip()

        if not name or not email:
            return jsonify({"success": False, "error": "Name and email are required"}), 400

        lead_entry = {
            "name": name,
            "email": email,
            "company": company,
            "service": service,
            "message": message,
            "created_at": datetime.datetime.utcnow().isoformat() + "Z",
            "ip_address": request.headers.get('X-Forwarded-For', request.remote_addr)
        }

        # Persist lead entry safely using GCS/Local
        leads = load_json(LEADS_FILE) or []
        leads.append(lead_entry)
        save_json(LEADS_FILE, leads)

        return jsonify({
            "success": True,
            "message": "Consultation request recorded. A principal architect will respond within 4 hours."
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/broadcom-savings', methods=['POST'])
def calculate_savings():
    """Programmatic API for calculating Broadcom license replacement savings."""
    try:
        payload = request.get_json(silent=True) or {}
        annual_spend = float(payload.get('annualSpend', 850000))
        tools = payload.get('tools', ['ca7', 'endevor', 'filemaster'])

        weight_map = {
            'ca7': 0.22,
            'endevor': 0.18,
            'filemaster': 0.08,
            'sysview': 0.12,
            'datacom': 0.15,
            'netmaster': 0.08
        }

        tool_weights = sum(weight_map.get(t.lower(), 0.0) for t in tools)
        savings_fraction = min(0.70, max(0.25, tool_weights * 0.95))
        annual_savings = round(annual_spend * savings_fraction)
        three_year_savings = annual_savings * 3

        return jsonify({
            "annualSpend": annual_spend,
            "selectedTools": tools,
            "savingsPercentage": round(savings_fraction * 100),
            "estimatedAnnualSavings": annual_savings,
            "estimatedThreeYearSavings": three_year_savings,
            "paybackMonths": "4 - 7 Months"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

@app.route('/api/stats_hidden_1234')
def view_stats():
    """Hidden endpoint to view organic hits."""
    hits = {"organic_hits": 0}
    if os.path.exists(HITS_FILE):
        try:
            with open(HITS_FILE, 'r', encoding='utf-8') as f:
                hits = json.load(f)
        except Exception:
            pass
    return jsonify(hits)
