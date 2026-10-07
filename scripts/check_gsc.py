import json, time, base64, urllib.request, urllib.parse
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import pkcs1_15
from Cryptodome.Hash import SHA256

KEY_FILE = r'C:\Users\Anshu\Downloads\serviceapartments-8c9df8c38105.json'
with open(KEY_FILE) as f:
    key_data = json.load(f)

header = {'alg': 'RS256', 'typ': 'JWT'}
now = int(time.time())
claims = {
    'iss': key_data['client_email'],
    'scope': 'https://www.googleapis.com/auth/webmasters.readonly',
    'aud': 'https://oauth2.googleapis.com/token',
    'exp': now + 3600,
    'iat': now
}

def b64url(data):
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

header_b64 = b64url(json.dumps(header).encode('utf-8'))
claims_b64 = b64url(json.dumps(claims).encode('utf-8'))
signing_input = f'{header_b64}.{claims_b64}'.encode('utf-8')

key = RSA.import_key(key_data['private_key'])
h = SHA256.new(signing_input)
sig = pkcs1_15.new(key).sign(h)
jwt_token = f'{header_b64}.{claims_b64}.{b64url(sig)}'

data = urllib.parse.urlencode({
    'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
    'assertion': jwt_token
}).encode('utf-8')

req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data)
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read().decode('utf-8'))['access_token']

urls_to_check = [
    'https://stackmf.com/broadcom-replacement.html',
    'https://stackmf.com/blog/which-company-can-help-with-mainframes-broadcom-tool-migration.html',
    'https://stackmf.com/blog/soc7-data-exception-cobol-packed-decimal.html'
]

for url in urls_to_check:
    inspect_req = urllib.request.Request(
        'https://searchconsole.googleapis.com/v1/urlInspection/index:inspect',
        data=json.dumps({'inspectionUrl': url, 'siteUrl': 'sc-domain:stackmf.com'}).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
    )
    try:
        with urllib.request.urlopen(inspect_req) as r:
            res = json.loads(r.read().decode('utf-8'))
            idx = res.get('inspectionResult', {}).get('indexStatusResult', {})
            verdict = idx.get('verdict')
            cov = idx.get('coverageState')
            crawl = idx.get('lastCrawlTime')
            print(f'URL: {url}')
            print(f'  Verdict: {verdict} | Coverage: {cov}')
            print(f'  LastCrawl: {crawl}\n')
    except Exception as e:
        print(f'Error inspecting {url}: {e}\n')

# Check sitemaps
sitemaps_req = urllib.request.Request(
    'https://searchconsole.googleapis.com/webmasters/v3/sites/sc-domain%3Astackmf.com/sitemaps',
    headers={'Authorization': 'Bearer ' + token}
)
try:
    with urllib.request.urlopen(sitemaps_req) as r:
        res = json.loads(r.read().decode('utf-8'))
        print('Sitemaps indexed count:')
        for sm in res.get('sitemap', []):
            contents = sm.get('contents', [{}])[0]
            print(f"{sm.get('path')} -> Submitted: {contents.get('submitted')}, Indexed: {contents.get('indexed')}")
except Exception as e:
    print(f'Error querying sitemaps: {e}')
