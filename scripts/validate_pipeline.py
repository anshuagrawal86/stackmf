import json
import re
import sys
import os

required_files = ['index.html', 'robots.txt', 'sitemap.xml', 'llms.txt', 'llms-full.txt']
missing = [f for f in required_files if not os.path.exists(f)]
if missing:
    print(f"ERROR: Missing critical files: {missing}")
    sys.exit(1)

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

schemas = re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.DOTALL)
if not schemas:
    print("ERROR: No JSON-LD schema found in index.html")
    sys.exit(1)

for idx, s in enumerate(schemas):
    try:
        data = json.loads(s.strip())
        print(f"JSON-LD block {idx+1} valid. Context: {data.get('@context')}")
    except Exception as e:
        print(f"ERROR: Invalid JSON-LD in block {idx+1}: {e}")
        sys.exit(1)

required_anchors = [
    'broadcom-replacement',
    'mainframe-developers',
    'mainframe-modernization',
    'fullstack-bridge',
    'maintenance-ams',
    'tco-calculator',
    'system-flow',
    'contact'
]
for anchor in required_anchors:
    if f'id="{anchor}"' not in content:
        print(f"ERROR: Missing section anchor #{anchor} in index.html")
        sys.exit(1)

print("ALL CI VALIDATION CHECKS PASSED PERFECTLY!")
