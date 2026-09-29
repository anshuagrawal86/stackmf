import os
import json
import time
import base64
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import pkcs1_15
from Cryptodome.Hash import SHA256

KEY_FILE = r"C:\Users\Anshu\Downloads\serviceapartments-8c9df8c38105.json"
SITEMAP_FILE = r"c:\Users\Anshu\source\stackmf\sitemap.xml"
INDEXNOW_KEY = "stackmf2026geoindexkey"
HOST = "stackmf.com"

def get_sitemap_urls():
    tree = ET.parse(SITEMAP_FILE)
    root = tree.getroot()
    urls = []
    ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    for url in root.findall('ns:url', ns):
        loc = url.find('ns:loc', ns)
        if loc is not None and loc.text:
            urls.append(loc.text.strip())
    return urls

def submit_indexnow(urls):
    print(f"\n[IndexNow] Submitting {len(urls)} URLs to IndexNow (Bing/Copilot/Perplexity)...")
    payload = {
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"https://{HOST}/{INDEXNOW_KEY}.txt",
        "urlList": urls
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        "https://api.indexnow.org/indexnow",
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"[IndexNow] Status: {resp.status} {resp.reason}")
    except urllib.error.HTTPError as e:
        print(f"[IndexNow] HTTP Error: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"[IndexNow] Error: {e}")

def get_google_access_token():
    if not os.path.exists(KEY_FILE):
        print(f"Key file not found at {KEY_FILE}")
        return None
    try:
        with open(KEY_FILE, "r") as f:
            key_data = json.load(f)

        header = {'alg': 'RS256', 'typ': 'JWT'}
        now = int(time.time())
        claims = {
            'iss': key_data['client_email'],
            'scope': 'https://www.googleapis.com/auth/indexing https://www.googleapis.com/auth/webmasters.readonly',
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
        with urllib.request.urlopen(req, timeout=10) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            return res.get('access_token')
    except Exception as e:
        print(f"Error obtaining Google OAuth token: {e}")
        return None

def submit_google_indexing(priority_urls):
    print(f"\n[Google Indexing API] Submitting priority URLs...")
    token = get_google_access_token()
    if not token:
        print("[Google Indexing API] Failed to obtain token.")
        return

    endpoint = "https://indexing.googleapis.com/v3/urlNotifications:publish"

    for url in priority_urls:
        payload = json.dumps({"url": url, "type": "URL_UPDATED"}).encode('utf-8')
        req = urllib.request.Request(
            endpoint,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                res_data = json.loads(resp.read().decode('utf-8'))
                metadata = res_data.get('urlNotificationMetadata', {})
                print(f"[Google Indexing] SUCCESS 200: {url} (Notify Time: {metadata.get('latestUpdate', {}).get('notifyTime')})")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8')
            print(f"[Google Indexing] HTTP Error {e.code} for {url}: {err_body}")
        except Exception as e:
            print(f"[Google Indexing] Error for {url}: {e}")

if __name__ == "__main__":
    all_urls = get_sitemap_urls()
    print(f"Discovered {len(all_urls)} URLs from sitemap.xml")
    submit_indexnow(all_urls)

    priority_urls = [
        "https://stackmf.com/broadcom-replacement.html",
        "https://stackmf.com/blog/which-company-can-help-with-mainframes-broadcom-tool-migration.html",
        "https://stackmf.com/",
        "https://stackmf.com/blog/",
        "https://stackmf.com/blog/soc7-data-exception-cobol-packed-decimal.html",
        "https://stackmf.com/blog/replacing-broadcom-endevor-with-git-zowe.html",
        "https://stackmf.com/blog/automating-ca7-migration-to-stonebranch-controlm.html",
        "https://stackmf.com/blog/migrating-broadcom-file-master-to-zowe-data-sets.html"
    ]
    submit_google_indexing(priority_urls)
