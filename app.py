import os
import json
import datetime
from flask import Flask, send_from_directory, request, jsonify, render_template_string, redirect

app = Flask(__name__, static_folder='.', static_url_path='')

LEADS_FILE = os.path.join(os.path.dirname(__file__), 'leads.json')

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

@app.route('/')
def home():
    """Serves the primary StackMF enterprise platform."""
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

        # Persist lead entry safely
        leads = []
        if os.path.exists(LEADS_FILE):
            try:
                with open(LEADS_FILE, 'r', encoding='utf-8') as f:
                    leads = json.load(f)
            except Exception:
                leads = []

        leads.append(lead_entry)
        with open(LEADS_FILE, 'w', encoding='utf-8') as f:
            json.dump(leads, f, indent=2)

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
