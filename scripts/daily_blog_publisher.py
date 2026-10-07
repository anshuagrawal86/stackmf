#!/usr/bin/env python3
"""
daily_blog_publisher.py - StackMF Autonomous Daily Mainframe Knowledge Base Publisher
Runs automatically without manual triggers (e.g. via scheduled GitHub Actions).
100% Free Tier Compliant.
Honors kill switch in blog-config.json: stops immediately when 'active' is false.
"""

import os
import sys
import json
import datetime
import urllib.request
import urllib.parse
from generate_blogs import generate_article_page, generate_blog_index, update_sitemap, update_llms
from blogs_data import ARTICLES
from blogs_data_additional import ADDITIONAL_ARTICLES
from blogs_data_queue import QUEUED_ARTICLES

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_FILE = os.path.join(BASE_DIR, "blog-config.json")
POSTS_FILE = os.path.join(BASE_DIR, "blog", "posts.json")
BLOG_DIR = os.path.join(BASE_DIR, "blog")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"active": True}
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_posts():
    if not os.path.exists(POSTS_FILE):
        return []
    with open(POSTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_ai_draft_free_tier(topic_info, api_key):
    """
    Optional dynamic blog generator using Google Gemini Free Tier API.
    100% Free with 15 RPM / 1500 RPD from Google AI Studio.
    """
    prompt = f"""You are an elite Principal Mainframe Architect at StackMF Technologies LLP.
Write a deep-dive technical article for mainframe developers on:
Topic: {topic_info.get('title')}
Category: {topic_info.get('category')}
Target Technologies: {', '.join(topic_info.get('tech', ['COBOL', 'DB2', 'z/OS']))}

Format the response strictly as valid JSON with these keys:
"slug": "{topic_info.get('slug')}",
"title": "{topic_info.get('title')}",
"category": "{topic_info.get('category')}",
"tags": ["tag1", "tag2", ...],
"reading_time": "9 min read",
"tldr": "A 2-3 sentence executive summary of the problem and concrete resolution",
"problem": "Detailed developer incident with exact error codes/logs in markdown",
"root_cause": "Deep architectural explanation of memory/subsystem mechanics in markdown",
"solution": "Step-by-step production resolution with authentic code snippets (COBOL/JCL/SQL/REXX/etc.) in markdown",
"prevention": ["Bullet 1", "Bullet 2", "Bullet 3", "Bullet 4"],
"references": [
  {{"title": "IBM Manual Title", "url": "https://www.ibm.com/docs/..."}},
  {{"title": "StackMF Guide", "url": "https://stackmf.com/#mainframe-modernization"}}
]
Do not wrap JSON in markdown blocks. Return only pure JSON."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        res_data = json.loads(resp.read().decode('utf-8'))
        text_content = res_data['candidates'][0]['content']['parts'][0]['text']
        article_data = json.loads(text_content.strip())
        return article_data

def get_all_known_articles():
    """Returns combined deduplicated list of all base and queued articles."""
    seen = set()
    combined = []
    for a in ARTICLES + ADDITIONAL_ARTICLES + QUEUED_ARTICLES:
        if a['slug'] not in seen:
            seen.add(a['slug'])
            combined.append(a)
    return combined

def publish_single_article(target_topic, target_date):
    """Generates, writes, and updates all indexes for a single article."""
    print(f"Preparing blog post for {target_date}: {target_topic['title']} ({target_topic['slug']})")

    api_key = os.environ.get("GEMINI_API_KEY")
    article_obj = None

    if api_key and api_key.strip():
        try:
            print("Invoking Gemini Free Tier API for dynamic synthesis...")
            article_obj = generate_ai_draft_free_tier(target_topic, api_key.strip())
            article_obj['date'] = target_date
        except Exception as e:
            print(f"Notice: Gemini API call failed ({e}). Falling back to precision template.")

    if not article_obj:
        # Match from QUEUED_ARTICLES or EXPANDED_TOPICS
        match = next((t for t in QUEUED_ARTICLES if t['slug'] == target_topic['slug']), None)
        if match:
            article_obj = dict(match)
            article_obj['date'] = target_date
        else:
            print(f"No template available for {target_topic['slug']}. Skipping.")
            return None

    # Load all known articles for internal link graph and related recommendations
    all_known = get_all_known_articles()
    
    # Write article HTML
    article_html = generate_article_page(article_obj, all_known)
    article_path = os.path.join(BLOG_DIR, f"{article_obj['slug']}.html")
    with open(article_path, 'w', encoding='utf-8') as f:
        f.write(article_html)
    print(f"Published: blog/{article_obj['slug']}.html")

    # Update posts list in posts.json
    existing_posts = load_posts()
    # Remove old entry with same slug if any
    existing_posts = [p for p in existing_posts if p['slug'] != article_obj['slug']]
    new_meta = {
        "slug": article_obj['slug'],
        "title": article_obj['title'],
        "date": article_obj['date'],
        "category": article_obj['category'],
        "tags": article_obj['tags'],
        "reading_time": article_obj['reading_time'],
        "tldr": article_obj['tldr']
    }
    updated_posts = [new_meta] + existing_posts
    with open(POSTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(updated_posts, f, indent=2)

    return article_obj

def rebuild_site_assets():
    """Rebuilds blog/index.html, sitemap.xml, and llms.txt containing all published posts."""
    posts_meta = load_posts()
    all_known_map = {a['slug']: a for a in get_all_known_articles()}
    
    full_articles_list = []
    for p in posts_meta:
        if p['slug'] in all_known_map:
            art = dict(all_known_map[p['slug']])
            art['date'] = p['date']
            full_articles_list.append(art)
        else:
            full_articles_list.append(p)

    # Rebuild blog/index.html
    index_html = generate_blog_index(full_articles_list)
    with open(os.path.join(BLOG_DIR, "index.html"), 'w', encoding='utf-8') as f:
        f.write(index_html)
    print("Rebuilt: blog/index.html")

    # Update sitemap & llms
    update_sitemap(full_articles_list)
    update_llms(full_articles_list)

def publish_daily_blog():
    config = load_config()

    # 1. KILL SWITCH CHECK
    if not config.get("active", True):
        print("KILL SWITCH ACTIVE: Daily blog publishing is disabled in blog-config.json. Exiting cleanly.")
        sys.exit(0)

    today_str = datetime.date.today().isoformat()
    existing_posts = load_posts()
    existing_slugs = set(p['slug'] for p in existing_posts)

    # 2. Select next topic from queue
    target_topic = None
    upcoming_queue = config.get("upcoming_queue", [])

    for item in upcoming_queue:
        if item['slug'] not in existing_slugs:
            target_topic = item
            break

    if not target_topic:
        for item in QUEUED_ARTICLES:
            if item['slug'] not in existing_slugs:
                target_topic = item
                break

    if not target_topic:
        print("All queue topics already published! Add new topics to blog-config.json upcoming_queue.")
        sys.exit(0)

    article_obj = publish_single_article(target_topic, today_str)
    if not article_obj:
        sys.exit(1)

    rebuild_site_assets()

    # Automated Search Engine Indexing Push
    article_url = f"https://www.stackmf.com/blog/{article_obj['slug']}.html"
    push_urls_to_search_engines([
        article_url,
        "https://www.stackmf.com/blog/",
        "https://www.stackmf.com/"
    ])

    print(f"SUCCESS: Daily blog '{article_obj['title']}' published and queued for search indexing for {today_str}!")

def push_urls_to_search_engines(urls):
    """
    Submits newly generated URLs to IndexNow (Bing/Copilot/Perplexity) and
    Google Indexing API (if GCP credentials exist in env or local key path).
    100% Free Tier compliant.
    """
    print(f"\n[SEO Automation] Pushing {len(urls)} URLs to search engine indexing APIs...")

    # 1. IndexNow (Bing, Microsoft Copilot, Perplexity, Naver, Seznam) - Instant & Key-based
    try:
        indexnow_payload = {
            'host': 'www.stackmf.com',
            'key': 'stackmf2026geoindexkey',
            'keyLocation': 'https://www.stackmf.com/stackmf2026geoindexkey.txt',
            'urlList': urls
        }
        req_in = urllib.request.Request(
            'https://api.indexnow.org/indexnow',
            data=json.dumps(indexnow_payload).encode('utf-8'),
            headers={'Content-Type': 'application/json; charset=utf-8'}
        )
        with urllib.request.urlopen(req_in, timeout=15) as resp:
            print(f"[IndexNow] Successfully pushed {len(urls)} URLs (HTTP {resp.status})")
    except Exception as e:
        print(f"[IndexNow] Notice: {e}")

    # 2. Google Indexing API (Direct push to Googlebot crawl queue)
    sa_info = None
    gcp_sa_key = os.environ.get("GCP_SA_KEY")
    local_key_path = r"C:\Users\Anshu\Downloads\serviceapartments-8c9df8c38105.json"

    if gcp_sa_key and gcp_sa_key.strip():
        try:
            sa_info = json.loads(gcp_sa_key.strip())
        except Exception:
            if os.path.exists(gcp_sa_key.strip()):
                with open(gcp_sa_key.strip(), 'r', encoding='utf-8') as f:
                    sa_info = json.load(f)
    elif os.path.exists(local_key_path):
        try:
            with open(local_key_path, 'r', encoding='utf-8') as f:
                sa_info = json.load(f)
        except Exception:
            pass

    if sa_info and 'private_key' in sa_info:
        try:
            import time
            import base64
            try:
                from Cryptodome.PublicKey import RSA
                from Cryptodome.Signature import pkcs1_15
                from Cryptodome.Hash import SHA256
            except ImportError:
                from Crypto.PublicKey import RSA
                from Crypto.Signature import pkcs1_15
                from Crypto.Hash import SHA256

            now = int(time.time())
            header = {'alg': 'RS256', 'typ': 'JWT'}
            payload = {
                'iss': sa_info['client_email'],
                'scope': 'https://www.googleapis.com/auth/indexing',
                'aud': 'https://oauth2.googleapis.com/token',
                'exp': now + 3600,
                'iat': now
            }

            def b64url(data):
                return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

            segments = [
                b64url(json.dumps(header).encode('utf-8')),
                b64url(json.dumps(payload).encode('utf-8'))
            ]
            signing_input = '.'.join(segments).encode('utf-8')
            key = RSA.import_key(sa_info['private_key'])
            h = SHA256.new(signing_input)
            signature = pkcs1_15.new(key).sign(h)
            jwt_token = f"{signing_input.decode('utf-8')}.{b64url(signature)}"

            token_data = urllib.parse.urlencode({
                'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                'assertion': jwt_token
            }).encode('utf-8')

            token_req = urllib.request.Request('https://oauth2.googleapis.com/token', data=token_data)
            with urllib.request.urlopen(token_req, timeout=10) as token_resp:
                access_token = json.loads(token_resp.read().decode('utf-8'))['access_token']

            for url in urls:
                try:
                    notify_payload = json.dumps({'url': url, 'type': 'URL_UPDATED'}).encode('utf-8')
                    notify_req = urllib.request.Request(
                        'https://indexing.googleapis.com/v3/urlNotifications:publish',
                        data=notify_payload,
                        headers={
                            'Authorization': f'Bearer {access_token}',
                            'Content-Type': 'application/json'
                        }
                    )
                    with urllib.request.urlopen(notify_req, timeout=10) as notify_resp:
                        print(f"[Google Indexing API] Notified Googlebot for {url} (HTTP {notify_resp.status})")
                except Exception as ex:
                    print(f"[Google Indexing API] Notice for {url}: {ex}")
        except Exception as e:
            print(f"[Google Indexing API] Auth Notice: {e}")

if __name__ == '__main__':
    publish_daily_blog()
