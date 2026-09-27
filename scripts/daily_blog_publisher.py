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

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_FILE = os.path.join(BASE_DIR, "blog-config.json")
POSTS_FILE = os.path.join(BASE_DIR, "blog", "posts.json")
BLOG_DIR = os.path.join(BASE_DIR, "blog")

# Rich curated repository of daily mainframe deep-dive templates
EXPANDED_TOPICS = [
    {
        "slug": "cics-storage-violation-aica-runaway-task",
        "title": "Diagnosing CICS AICA (Runaway Task) and Storage Violations (Subpool Overwrites)",
        "category": "ABENDS & Diagnostics",
        "tags": ["CICS", "AICA", "Storage Violation", "Runaway Task", "Subpool", "Dump Analysis"],
        "reading_time": "10 min read",
        "tldr": "CICS ABEND AICA halts transactions that loop without yielding CPU control to CICS task dispatcher, while storage violations corrupt transaction work areas. Discover how to inspect the CICS System Dump, identify runaway loops, and configure storage protection keys.",
        "problem": """High-priority CICS transactions suddenly terminate with:
```text
DFHPC2034 10:14:22 CICS01 TASK 04921 TRANSACTION TXOR ABENDED AICA.
          TIME LIMIT EXCEEDED WITHOUT RETURNING CONTROL TO CICS.
```
In other instances, the entire CICS region writes message `DFHSR0601 A storage violation has occurred in module DFHXMDS`, forcing emergency region cycling during peak trading hours.""",
        "root_cause": """CICS uses cooperative multitasking:
1. **AICA (Runaway Task)**: If an application COBOL program enters an infinite `PERFORM` loop or scans large tables without issuing a CICS command (such as `EXEC CICS DELAY`, `EXEC CICS RECEIVE`, or `EXEC CICS SUSPEND`), the CICS dispatcher timer expires (defined by `RUNAWAY` interval in the SIT or transaction definition, typically 5000ms), and CICS purges the task.
2. **Storage Violation**: An application program writes beyond the boundary of its allocated `DFHCOMMAREA`, CICS `CONTAINER`, or `GETMAIN` storage, overwriting the Storage Accounting Area (SAA) check-bytes of an adjacent task's memory.""",
        "solution": """### 1. Locate the Infinite Loop in CICS Dump
Check the offset where the task was interrupted:
```text
PSW AT TIME OF INTERRUPT: 078D1000 84C2145A
TASK CPU TIME USED: 5.002 SECONDS (EXCEEDED RUNAWAY 5000MS)
```
Map the offset `84C2145A` to the compiler listing. Typically, an un-incremented counter in an `UNTIL` loop is the culprit:
```cobol
      * BUGGY CODE
       PERFORM UNTIL WS-RECORD-FOUND = 'Y'
           READ RECORD ...
      * Missing condition advance or exit trigger!
       END-PERFORM.
```

### 2. Yield CPU Control in Long-Running Transactions
If a transaction must process a large array in memory, issue periodic yields:
```cobol
       ADD 1 TO WS-CHUNK-COUNT
       IF WS-CHUNK-COUNT > 500
           EXEC CICS SUSPEND END-EXEC
           MOVE 0 TO WS-CHUNK-COUNT
       END-IF.
```

### 3. Activate CICS Storage Protection & Transaction Isolation
In the CICS System Initialization Table (SIT):
- Set `STGPROT=YES`
- Set `TRANISO=YES`
This prevents an errant User-Key transaction from corrupting other concurrent tasks or CICS system subpools!""",
        "prevention": [
            "Set appropriate `RUNAWAY` transaction limits in CSD definitions (e.g., 2000-5000ms).",
            "Enable CICS Storage Protection (`STGPROT=YES`) across all production regions.",
            "Verify subscript boundaries on all `MOVE` statements to avoid SAA header corruption.",
            "Include `EXEC CICS SUSPEND` in CPU-bound batch-in-online algorithms."
        ],
        "references": [
            {"title": "IBM CICS TS: Dealing with Runaway Tasks (AICA)", "url": "https://www.ibm.com/docs/en/cics-ts/latest?topic=dumps-investigating-aica-abend"},
            {"title": "IBM CICS TS: Storage Violations and Recovery", "url": "https://www.ibm.com/docs/en/cics-ts/latest?topic=dumps-investigating-storage-violations"},
            {"title": "StackMF 24/7 Managed Application Maintenance (AMS)", "url": "https://stackmf.com/#maintenance-ams"}
        ]
    },
    {
        "slug": "db2-rebind-stability-package-plan-switching",
        "title": "Mastering DB2 Package Plan Stability: Avoiding Access Path Regressions During REBIND",
        "date": "2026-09-27",
        "category": "DB2 SQL & Performance",
        "tags": ["DB2", "Plan Stability", "REBIND", "Access Paths", "APREUSE", "PLANMGMT"],
        "reading_time": "9 min read",
        "tldr": "Rebinding DB2 packages after software maintenance or schema changes can cause access path regressions, resulting in sudden 10x query slowdowns. Master DB2 Plan Management (PLANMGMT), APREUSE, and catalog switching to safeguard production workloads.",
        "problem": """Following a quarterly DB2 maintenance migration or catalog RUNSTATS update, an automated mass `REBIND` job runs. The next morning, high-throughput OLTP transactions stall:
```text
DSNA672I SQL QUERY RUNTIME JUMPED FROM 12MS TO 4800MS
PLAN_TABLE SHOWS ACCESS PATH SWITCHED FROM MATCHING INDEX SCAN TO TABLESPACE SCAN
```
Database administrators face severe business escalation while attempting to pinpoint which packages regressed.""",
        "root_cause": """During `REBIND PACKAGE`, DB2 re-evaluates all access paths based on current catalog statistics and optimizer algorithms. If statistics changed slightly or a different index path is estimated marginally cheaper, the optimizer selects a new path. In complex multi-table joins, the new estimate may result in disastrous access path regression.""",
        "solution": """### 1. Bind with PLANMGMT(EXTENDED)
Configure DB2 Plan Management to retain current, previous, and original package copies:
```text
REBIND PACKAGE(DSN8D13A.CUST01) -
       PLANMGMT(EXTENDED) -
       APREUSE(WARN)
```
- `PLANMGMT(EXTENDED)` stores the historical access path in `SYSIBM.SYSPACKCOPY`.
- `APREUSE(WARN)` attempts to reuse existing access paths and warns if a query path must deviate.

### 2. Instant Access Path Fallback via SWITCH
If a newly bound package exhibits poor response times, instantly revert without recompiling or re-analyzing:
```text
REBIND PACKAGE(DSN8D13A.CUST01) -
       SWITCH(PREVIOUS)
```
Within 2 seconds, DB2 switches back to the previous proven access path in the catalog, restoring production immediately!

### 3. Verify Package Copies in Catalog
Query package stability history:
```sql
SELECT BIND_TIME, PLANMGMT, APREUSE_SUCCESS
FROM SYSIBM.SYSPACKAGE
WHERE NAME = 'CUST01';

SELECT COPYID, BIND_TIME
FROM SYSIBM.SYSPACKCOPY
WHERE NAME = 'CUST01';
```""",
        "prevention": [
            "Always rebind critical production packages with `PLANMGMT(EXTENDED)`.",
            "Use `APREUSE(ERROR)` or `APREUSE(WARN)` to detect unexpected access path deviations before cutover.",
            "Test rebinds in a cloned pre-production subsystem before executing across production.",
            "Use DB2 Query Capture and Comparison utilities to validate elapsed-time impact."
        ],
        "references": [
            {"title": "IBM Db2 13 for z/OS Managing Performance: Access Path Stability", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=performance-access-path-stability"},
            {"title": "IBM Db2 13 for z/OS REBIND PACKAGE Command", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=commands-rebind-package-db2"},
            {"title": "StackMF Enterprise Mainframe Modernization Services", "url": "https://stackmf.com/#mainframe-modernization"}
        ]
    },
    {
        "slug": "cobol-null-indicators-db2-host-variables",
        "title": "Handling DB2 SQLCODE -305: Null Indicator Variables in COBOL Working-Storage",
        "date": "2026-09-27",
        "category": "DB2 SQL & Performance",
        "tags": ["DB2", "COBOL", "SQLCODE -305", "Null Indicator", "Host Variables"],
        "reading_time": "8 min read",
        "tldr": "DB2 SQLCODE -305 is raised when a query attempts to retrieve a NULL column value into a COBOL host variable without specifying an accompanying Null Indicator variable. Learn proper indicator syntax and default coalescing.",
        "problem": """A COBOL DB2 batch program runs smoothly in testing but fails in production when processing a newly created customer record:
```text
DSNT408I SQLCODE = -305, ERROR:  THE NULL VALUE CANNOT BE ASSIGNED TO A HOST
         VARIABLE IN POSITION 4 BECAUSE NO INDICATOR VARIABLE IS SPECIFIED.
DSNT418I SQLSTATE = 22002 SQLSTATE RETURN CODE
CEE3250C The system or user abend U4038 was issued.
```
The job halts, rolling back earlier batch changes.""",
        "root_cause": """Relational databases support `NULL` (the absence of any value), whereas COBOL has no intrinsic concept of null memory—every memory location contains bits (spaces, zeroes, etc.).
When DB2 encounters a `NULL` column during a `FETCH` or `SELECT INTO`:
- If the SQL statement provides a companion **Indicator Variable** (`:VAR :IND`), DB2 sets the indicator to `-1` (Null) and leaves the host variable undisturbed.
- If no indicator variable was supplied on a nullable column, DB2 raises SQLCODE -305 to prevent undefined data corruption.""",
        "solution": """### 1. Declare Indicator Variables in Working-Storage
Define null indicators as 2-byte binary signed integers (`PIC S9(4) COMP`):
```cobol
       01  WS-CUSTOMER-DATA.
           05  WS-CUST-ID               PIC X(10).
           05  WS-PHONE-NUMBER          PIC X(15).
           05  WS-PHONE-IND             PIC S9(4) COMP.
           05  WS-CREDIT-SCORE          PIC S9(4) COMP.
           05  WS-CREDIT-IND            PIC S9(4) COMP.
```

### 2. Include Indicators in SELECT Statements
Attach the indicator variable immediately after the host variable:
```cobol
       EXEC SQL
           SELECT CUST_ID, PHONE_NUMBER, CREDIT_SCORE
           INTO :WS-CUST-ID,
                :WS-PHONE-NUMBER :WS-PHONE-IND,
                :WS-CREDIT-SCORE :WS-CREDIT-IND
           FROM CUSTOMER_TABLE
           WHERE CUST_ID = :WS-CUST-ID
       END-EXEC.
```

### 3. Evaluate Indicator Values in COBOL Logic
Check indicator status before using column data:
```cobol
       IF WS-PHONE-IND < 0
      * Column is NULL in DB2
           MOVE 'NO PHONE ON FILE' TO WS-DISPLAY-PHONE
       ELSE
           MOVE WS-PHONE-NUMBER    TO WS-DISPLAY-PHONE
       END-IF.
```

### 4. Alternative: SQL COALESCE Function
Avoid host indicator variables by handling nulls directly in SQL:
```sql
SELECT CUST_ID,
       COALESCE(PHONE_NUMBER, 'UNLISTED'),
       COALESCE(CREDIT_SCORE, 0)
INTO :WS-CUST-ID, :WS-PHONE-NUMBER, :WS-CREDIT-SCORE
FROM CUSTOMER_TABLE ...
```""",
        "prevention": [
            "Check the DB2 DCLGEN output: any column defined with `NULL` requires an indicator variable in COBOL.",
            "Use `COALESCE` or `IFNULL` in SQL when sensible default values exist.",
            "Verify all external fields during unit tests using test cases with empty/null columns.",
            "Include `-305` error handling in enterprise exception handlers."
        ],
        "references": [
            {"title": "IBM Db2 13 for z/OS Codes: SQLCODE -305", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=codes-305"},
            {"title": "IBM Enterprise COBOL for z/OS: Using DB2 Indicator Variables", "url": "https://www.ibm.com/docs/en/cobol-zos/latest?topic=sql-indicator-variables"},
            {"title": "StackMF Mainframe Core Application Engineering Pods", "url": "https://stackmf.com/#mainframe-developers"}
        ]
    }
]

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

def publish_daily_blog():
    config = load_config()

    # 1. KILL SWITCH CHECK
    if not config.get("active", True):
        print("KILL SWITCH ACTIVE: Daily blog publishing is disabled in blog-config.json. Exiting cleanly.")
        sys.exit(0)

    today_str = datetime.date.today().isoformat()
    existing_posts = load_posts()
    existing_slugs = set(p['slug'] for p in existing_posts)

    # 2. Select next topic
    target_topic = None
    upcoming_queue = config.get("upcoming_queue", [])

    for item in upcoming_queue:
        if item['slug'] not in existing_slugs:
            target_topic = item
            break

    if not target_topic:
        for item in EXPANDED_TOPICS:
            if item['slug'] not in existing_slugs:
                target_topic = item
                break

    if not target_topic:
        print("All queue topics already published! Add new topics to blog-config.json upcoming_queue.")
        sys.exit(0)

    print(f"Preparing daily blog post for {today_str}: {target_topic['title']} ({target_topic['slug']})")

    # 3. Generate article (Gemini Free Tier if key is available, else curated deep template)
    api_key = os.environ.get("GEMINI_API_KEY")
    article_obj = None

    if api_key and api_key.strip():
        try:
            print("Invoking Gemini Free Tier API for dynamic synthesis...")
            article_obj = generate_ai_draft_free_tier(target_topic, api_key.strip())
            article_obj['date'] = today_str
        except Exception as e:
            print(f"Notice: Gemini API call failed ({e}). Falling back to precision template.")

    if not article_obj:
        # Check if topic has full definition in EXPANDED_TOPICS
        match = next((t for t in EXPANDED_TOPICS if t['slug'] == target_topic['slug']), None)
        if match:
            article_obj = dict(match)
            article_obj['date'] = today_str
        else:
            print(f"No template available for {target_topic['slug']}. Skipping.")
            sys.exit(0)

    # 4. Write article HTML
    article_html = generate_article_page(article_obj)
    article_path = os.path.join(BLOG_DIR, f"{article_obj['slug']}.html")
    with open(article_path, 'w', encoding='utf-8') as f:
        f.write(article_html)
    print(f"Published: blog/{article_obj['slug']}.html")

    # 5. Update posts list
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

    # 6. Rebuild blog/index.html
    from blogs_data import ARTICLES
    from blogs_data_additional import ADDITIONAL_ARTICLES
    all_articles = [article_obj] + ARTICLES + ADDITIONAL_ARTICLES
    index_html = generate_blog_index(all_articles)
    with open(os.path.join(BLOG_DIR, "index.html"), 'w', encoding='utf-8') as f:
        f.write(index_html)
    print("Rebuilt: blog/index.html")

    # 7. Update sitemap & llms
    update_sitemap([article_obj])
    update_llms([article_obj])

    print(f"SUCCESS: Daily blog '{article_obj['title']}' published successfully for {today_str}!")

if __name__ == '__main__':
    publish_daily_blog()
