import os
import re
import json
import datetime
from blogs_data import ARTICLES
from blogs_data_additional import ADDITIONAL_ARTICLES

SITE_URL = "https://stackmf.com"
BLOG_DIR = os.path.join(os.path.dirname(__file__), "..", "blog")
SITEMAP_FILE = os.path.join(os.path.dirname(__file__), "..", "sitemap.xml")
LLMS_FILE = os.path.join(os.path.dirname(__file__), "..", "llms.txt")
LLMS_FULL_FILE = os.path.join(os.path.dirname(__file__), "..", "llms-full.txt")

os.makedirs(BLOG_DIR, exist_ok=True)

def markdown_to_html(md_text):
    """Converts a subset of markdown (code blocks, inline code, headings, lists, bold, links) to HTML."""
    code_blocks = []
    def save_code_block(match):
        lang = match.group(1) or 'text'
        code = match.group(2)
        code = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        idx = len(code_blocks)
        html = f'''<div class="my-6 rounded-xl overflow-hidden border border-white/10 bg-[#070b14] shadow-2xl">
          <div class="flex items-center justify-between px-4 py-2.5 bg-slate-900/90 border-b border-white/10 font-mono text-xs text-slate-400">
            <span class="flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full bg-rose-500/70"></span>
              <span class="w-2.5 h-2.5 rounded-full bg-amber-500/70"></span>
              <span class="w-2.5 h-2.5 rounded-full bg-neon-emerald/70"></span>
              <span class="ml-2 uppercase tracking-wider text-slate-300 font-semibold">{lang}</span>
            </span>
            <button onclick="navigator.clipboard.writeText(this.closest('.my-6').querySelector('code').innerText); this.innerText='Copied!'; setTimeout(()=>this.innerText='Copy', 2000)" class="text-xs text-slate-400 hover:text-white px-2 py-0.5 rounded bg-slate-800 border border-slate-700 transition">Copy</button>
          </div>
          <pre class="p-4 text-xs sm:text-sm font-mono text-emerald-400 overflow-x-auto leading-relaxed"><code>{code.strip()}</code></pre>
        </div>'''
        code_blocks.append(html)
        return f"<!--CODE_BLOCK_{idx}-->"

    content = re.sub(r'```([a-zA-Z0-9_\-]*)\n(.*?)```', save_code_block, md_text, flags=re.DOTALL)

    lines = content.split('\n')
    output_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                output_lines.append('</ul>')
                in_list = False
            continue

        if stripped.startswith('### '):
            if in_list: output_lines.append('</ul>'); in_list = False
            h_text = stripped[4:]
            output_lines.append(f'<h3 class="text-xl sm:text-2xl font-bold text-white mt-8 mb-4 flex items-center gap-2.5"><span class="text-neon-cyan">#</span> {h_text}</h3>')
            continue
        elif stripped.startswith('## '):
            if in_list: output_lines.append('</ul>'); in_list = False
            h_text = stripped[3:]
            output_lines.append(f'<h2 class="text-2xl sm:text-3xl font-extrabold text-white mt-12 mb-5 pb-2 border-b border-white/10 flex items-center gap-3"><span class="text-neon-emerald">#</span> {h_text}</h2>')
            continue

        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                output_lines.append('<ul class="space-y-3 my-4 list-none pl-0">')
                in_list = True
            item_text = stripped[2:]
            output_lines.append(f'<li class="flex items-start gap-3 text-slate-300 leading-relaxed"><i class="fa-solid fa-check text-neon-emerald text-xs mt-1.5 shrink-0"></i> <span>{item_text}</span></li>')
            continue
        elif in_list and not (stripped.startswith('- ') or stripped.startswith('* ')):
            output_lines.append('</ul>')
            in_list = False

        if not stripped.startswith('<!--CODE_BLOCK_'):
            output_lines.append(f'<p class="text-slate-300 leading-relaxed my-4 text-base sm:text-lg font-light">{stripped}</p>')
        else:
            output_lines.append(stripped)

    if in_list:
        output_lines.append('</ul>')

    html_out = '\n'.join(output_lines)
    html_out = re.sub(r'\*\*(.*?)\*\*', r'<strong class="text-white font-semibold">\1</strong>', html_out)
    html_out = re.sub(r'`([^`]+)`', r'<code class="font-mono text-neon-cyan bg-slate-900/90 px-1.5 py-0.5 rounded border border-white/10 text-xs sm:text-sm">\1</code>', html_out)
    html_out = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener noreferrer" class="text-neon-cyan hover:underline font-medium">\1 <i class="fa-solid fa-arrow-up-right-from-square text-[10px] ml-0.5"></i></a>', html_out)

    for idx, block in enumerate(code_blocks):
        html_out = html_out.replace(f'<!--CODE_BLOCK_{idx}-->', block)

def optimize_seo_title(article):
    """
    Produces front-loaded, exact-match SEO title tags (< 60 chars)
    that prioritize high-volume developer search queries (S0C7, S0C4, SQLCODE, etc.).
    """
    clean = article['title'].strip()
    slug = article['slug'].lower()
    
    if "soc7" in slug or "s0c7" in clean.lower():
        return "S0C7 / SOC7 ABEND Fix: COBOL Data Exception (COMP-3) | StackMF"
    if "soc4" in slug or "s0c4" in clean.lower():
        return "S0C4 / SOC4 ABEND Fix: Protection Exception & Linkage Pointers | StackMF"
    if "soc1" in slug or "s0c1" in clean.lower():
        return "S0C1 / SOC1 ABEND Fix: Operation Exception & Unresolved Calls | StackMF"
    if "sb37" in slug or "b37" in clean.lower() or "d37" in clean.lower():
        return "Sx37 Out-of-Space ABEND Fix: B37, D37, E37 Resolution | StackMF"
    if "asra" in slug:
        return "CICS ASRA ABEND Fix: Program Check & Memory Overwrite | StackMF"
    if "aica" in slug:
        return "CICS AICA ABEND Fix: Runaway Task & Storage Violations | StackMF"
    if "911" in slug or "904" in slug:
        return "DB2 SQLCODE -911 & -904 Fix: Deadlocks & Timeouts | StackMF"
    if "status-92" in slug:
        return "VSAM File Status 92 & 93 Fix: Dynamic Allocation Conflicts | StackMF"
    if "status-35" in slug:
        return "VSAM File Status 35 Fix: File Not Found & JCL DD Miss | StackMF"
    if "ca7" in slug or "ca-7" in slug:
        return "CA-7 Migration Guide: Modernizing to Stonebranch & Control-M | StackMF"
    if "endevor" in slug:
        return "Broadcom Endevor to Git Migration: Modern DevOps Guide | StackMF"

    for prefix in ["Resolving ABEND ", "Resolving ", "Diagnosing ", "Mastering ", "Demystifying ", "Comprehensive Guide to ", "Complete Guide: "]:
        if clean.startswith(prefix):
            clean = clean[len(prefix):]
            break

    brand = " | StackMF"
    max_len = 60 - len(brand)
    if len(clean) > max_len:
        clean = clean[:max_len].rsplit(' ', 1)[0]

    return f"{clean}{brand}"

def get_article_keywords(article):
    """Generates rich exact-match keyword variations and technical synonyms for search engines."""
    kw = list(article.get('tags', []))
    slug = article['slug'].lower()
    title_lower = article['title'].lower()

    if "soc7" in slug or "s0c7" in title_lower:
        kw.extend(["S0C7", "SOC7", "0C7", "abend s0c7", "abend 0c7", "data exception", "CEE3207S", "COMP-3", "packed decimal", "NUMVAL"])
    elif "soc4" in slug or "s0c4" in title_lower:
        kw.extend(["S0C4", "SOC4", "0C4", "abend s0c4", "protection exception", "linkage section", "addressing exception", "BASSM"])
    elif "soc1" in slug or "s0c1" in title_lower:
        kw.extend(["S0C1", "SOC1", "0C1", "operation exception", "unresolved call", "missing module"])
    elif "911" in slug or "904" in slug:
        kw.extend(["SQLCODE -911", "SQLCODE -904", "DB2 deadlock", "resource unavailable", "00C90088", "DSNT408I"])
    elif "vsam" in slug:
        kw.extend(["VSAM", "file status 92", "file status 93", "file status 35", "IDC3009I", "dynamic allocation", "VERIFY"])
    elif "ca7" in slug or "ca-7" in slug:
        kw.extend(["CA-7", "CA 7", "Stonebranch", "Control-M", "SASSSB01", "workload automation"])
    elif "endevor" in slug:
        kw.extend(["Endevor", "CA Endevor", "Git", "Zowe", "IBM DBB", "BC1PFP00", "SCM migration"])

    kw.extend(["IBM z/OS", "mainframe modernization", "production troubleshooting", "stackmf"])
    return list(dict.fromkeys(kw))

def build_schema_graph(article, article_url, related_articles):
    """Builds a rich, multi-entity linked Schema.org @graph including TechArticle, HowTo, FAQPage, and BreadcrumbList."""
    # Build FAQs
    q1 = f"What is the root cause of {article['title']}?"
    a1 = article['root_cause'].splitlines()[0].replace('`', '').replace('*', '').strip()
    if not a1.endswith('.'): a1 += '.'

    q2 = f"How do you resolve {article['title']} in production?"
    a2 = article['tldr']

    q3 = f"How can teams prevent {article['title']} in enterprise pipelines?"
    a3 = article['prevention'][0] if article.get('prevention') else "Incorporate automated compilation flags and regression test suites."

    faq_entities = [
        {
            "@type": "Question",
            "name": q1,
            "acceptedAnswer": {"@type": "Answer", "text": a1}
        },
        {
            "@type": "Question",
            "name": q2,
            "acceptedAnswer": {"@type": "Answer", "text": a2}
        },
        {
            "@type": "Question",
            "name": q3,
            "acceptedAnswer": {"@type": "Answer", "text": a3}
        }
    ]

    graph = [
        {
            "@type": "TechArticle",
            "@id": f"{article_url}#article",
            "isPartOf": {
                "@type": "WebPage",
                "@id": article_url
            },
            "headline": f"{article['title']} Fix",
            "description": article['tldr'],
            "url": article_url,
            "datePublished": f"{article['date']}T08:00:00+00:00",
            "dateModified": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "inLanguage": "en-US",
            "mainEntityOfPage": article_url,
            "author": {
                "@type": "Person",
                "name": "Anshu",
                "jobTitle": "Chief Technology Architect & Mainframe Systems SME",
                "url": "https://stackmf.com",
                "sameAs": "https://www.linkedin.com/company/stackmf"
            },
            "publisher": {
                "@type": "Organization",
                "@id": "https://stackmf.com/#organization",
                "name": "StackMF Technologies LLP",
                "url": "https://stackmf.com",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://assets.zyrosite.com/cdn-cgi/image/format=auto,w=192,h=192,fit=crop,f=png/ALpXb5J8LKfeaWNX/logo-YZ9nXvEj8KiMb60r.png"
                }
            },
            "keywords": get_article_keywords(article),
            "about": [{"@type": "Thing", "name": t} for t in article['tags']]
        },
        {
            "@type": "HowTo",
            "@id": f"{article_url}#howto",
            "name": f"How to Resolve {article['title']}",
            "description": article['tldr'],
            "totalTime": "PT15M",
            "tool": [
                {"@type": "HowToTool", "name": "SDSF Spool / JES2 System Log"},
                {"@type": "HowToTool", "name": "Language Environment CEEDUMP"},
                {"@type": "HowToTool", "name": "IBM Enterprise COBOL / DB2 Subsystem"}
            ],
            "step": [
                {
                    "@type": "HowToStep",
                    "position": 1,
                    "name": "Analyze the Spool and Traceback Logs",
                    "text": "Locate the failing statement, completion code, or SQLCODE in SDSF or CEEDUMP."
                },
                {
                    "@type": "HowToStep",
                    "position": 2,
                    "name": "Identify the Corrupt Variable or Contention Lock",
                    "text": "Inspect the hexadecimal storage, host variables, or resource locks involved in the failure."
                },
                {
                    "@type": "HowToStep",
                    "position": 3,
                    "name": "Apply the Verified Defensive Code or JCL Patch",
                    "text": "Implement the recommended syntax, compiler options, or parameter adjustment."
                },
                {
                    "@type": "HowToStep",
                    "position": 4,
                    "name": "Validate Execution in Test Subsystem",
                    "text": "Run batch cycle or transaction test to confirm clean execution with RC=0000."
                }
            ]
        },
        {
            "@type": "FAQPage",
            "@id": f"{article_url}#faq",
            "mainEntity": faq_entities
        },
        {
            "@type": "BreadcrumbList",
            "@id": f"{article_url}#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://stackmf.com/"},
                {"@type": "ListItem", "position": 2, "name": "Mainframe Knowledge Base", "item": "https://stackmf.com/blog/"},
                {"@type": "ListItem", "position": 3, "name": article['category'], "item": "https://stackmf.com/blog/"},
                {"@type": "ListItem", "position": 4, "name": article['title'], "item": article_url}
            ]
        }
    ]

    return json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2)

def generate_article_page(article, all_articles):
    """Generates the full standalone HTML page for an article with max SEO/GEO/AEO impact."""
    problem_html = markdown_to_html(article['problem'])
    root_cause_html = markdown_to_html(article['root_cause'])
    solution_html = markdown_to_html(article['solution'])

    prevention_items = "".join([
        f'<li class="flex items-start gap-3 text-slate-200 text-sm sm:text-base"><i class="fa-solid fa-shield-halved text-neon-cyan mt-1 shrink-0"></i><span>{item}</span></li>'
        for item in article['prevention']
    ])

    ref_items = "".join([
        f'''<li class="flex items-center justify-between p-3.5 rounded-xl bg-slate-900/60 border border-white/10 hover:border-neon-cyan/40 transition group">
              <div class="flex items-center gap-3">
                <i class="fa-solid fa-book-bookmark text-neon-cyan group-hover:scale-110 transition-transform"></i>
                <span class="text-sm font-medium text-slate-200 group-hover:text-white">{ref["title"]}</span>
              </div>
              <a href="{ref["url"]}" target="_blank" rel="noopener noreferrer" class="text-xs font-mono text-neon-cyan hover:text-white flex items-center gap-1.5 px-3 py-1 rounded-lg bg-white/5 border border-white/10 hover:bg-neon-cyan hover:text-black transition">
                <span>Docs</span>
                <i class="fa-solid fa-arrow-up-right-from-square text-[10px]"></i>
              </a>
            </li>'''
        for ref in article['references']
    ])

    tags_html = "".join([
        f'<span class="px-2.5 py-1 rounded-lg text-xs font-mono bg-white/5 text-slate-300 border border-white/10">{tag}</span>'
        for tag in article['tags']
    ])

    # Dynamic Related Articles (Pick 3 related articles)
    related = [a for a in all_articles if a['slug'] != article['slug']]
    # Prefer same category first
    same_cat = [a for a in related if a['category'] == article['category']]
    diff_cat = [a for a in related if a['category'] != article['category']]
    selected_related = (same_cat + diff_cat)[:3]

    related_cards_html = ""
    for r in selected_related:
        related_cards_html += f'''
        <a href="/blog/{r["slug"]}.html" class="p-5 rounded-2xl bg-slate-900/60 border border-white/10 hover:border-neon-cyan/50 hover:bg-slate-900/90 transition-all flex flex-col justify-between group">
          <div>
            <div class="flex items-center justify-between text-xs font-mono mb-2">
              <span class="text-neon-cyan">{r["category"]}</span>
              <span class="text-slate-400">{r["reading_time"]}</span>
            </div>
            <h4 class="text-sm font-bold text-white group-hover:text-neon-cyan transition-colors line-clamp-2 mb-2">
              {r["title"]}
            </h4>
          </div>
          <div class="text-xs font-mono text-neon-emerald flex items-center gap-1 mt-4 pt-3 border-t border-white/5">
            <span>Read Diagnostic Fix</span> &rarr;
          </div>
        </a>
        '''

    # FAQs for page display
    faq_q1 = f"What is the root cause of {article['title']}?"
    faq_a1 = article['root_cause'].splitlines()[0].replace('`', '').replace('*', '').strip()
    if not faq_a1.endswith('.'): faq_a1 += '.'

    faq_q2 = f"How do you resolve {article['title']} in production?"
    faq_a2 = article['tldr']

    faq_q3 = f"How can teams prevent {article['title']} in enterprise pipelines?"
    faq_a3 = article['prevention'][0] if article.get('prevention') else "Incorporate automated compilation flags and regression test suites."

    article_url = f"{SITE_URL}/blog/{article['slug']}.html"
    schema_json = build_schema_graph(article, article_url, selected_related)

    # High-ranking exact-match SEO Title & Keywords
    seo_title = optimize_seo_title(article)
    article_keywords = ", ".join(get_article_keywords(article))

    display_h1 = article['title']
    slug_lower = article['slug'].lower()
    if "soc7" in slug_lower or "s0c7" in slug_lower:
        display_h1 = "S0C7 / SOC7 ABEND: Resolving Data Exception in COBOL Packed-Decimal (COMP-3)"
    elif "soc4" in slug_lower or "s0c4" in slug_lower:
        display_h1 = "S0C4 / SOC4 ABEND: Resolving Protection Exception & Linkage Pointers"
    elif "soc1" in slug_lower or "s0c1" in slug_lower:
        display_h1 = "S0C1 / SOC1 ABEND: Resolving Operation Exception & Missing Modules"
    elif "sb37" in slug_lower or "b37" in slug_lower:
        display_h1 = "Sx37 (B37 / D37 / E37) ABEND: Resolving Disk Dataset Out-of-Space Errors"

    return f'''<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  
  <title>{seo_title}</title>
  <meta name="title" content="{seo_title}">
  <meta name="description" content="{article['tldr']}">
  <meta name="keywords" content="{article_keywords}">
  <meta name="author" content="Anshu - StackMF Technologies">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <link rel="canonical" href="{article_url}">

  <!-- Open Graph -->
  <meta property="og:type" content="article">
  <meta property="og:url" content="{article_url}">
  <meta property="og:title" content="{seo_title}">
  <meta property="og:description" content="{article['tldr']}">
  <meta property="og:site_name" content="StackMF Technologies LLP">
  <meta property="article:published_time" content="{article['date']}T08:00:00+00:00">
  <meta property="article:section" content="{article['category']}">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{seo_title}">
  <meta name="twitter:description" content="{article['tldr']}">

  <link rel="icon" type="image/png" sizes="32x32" href="https://assets.zyrosite.com/cdn-cgi/image/format=auto,w=32,h=32,fit=crop,f=png/ALpXb5J8LKfeaWNX/logo-YZ9nXvEj8KiMb60r.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          colors: {{
            neon: {{
              emerald: '#00F5A0',
              cyan: '#00F0FF',
              violet: '#8B5CF6',
              amber: '#FBBF24',
              rose: '#F43F5E'
            }},
            cyber: {{
              darker: '#030712',
              dark: '#070a0f',
              surface: '#0d131d',
              card: '#111827',
              border: 'rgba(255, 255, 255, 0.08)'
            }}
          }},
          fontFamily: {{
            sans: ['Inter', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace']
          }}
        }}
      }}
    }}
  </script>

  <style>
    body {{ background-color: #030712; color: #f1f5f9; font-family: 'Inter', sans-serif; }}
    .cyber-grid {{
      background-size: 48px 48px;
      background-image: 
        linear-gradient(to right, rgba(255, 255, 255, 0.035) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(255, 255, 255, 0.035) 1px, transparent 1px);
      mask-image: radial-gradient(ellipse 70% 60% at 50% 25%, #000 40%, transparent 100%);
      -webkit-mask-image: radial-gradient(ellipse 70% 60% at 50% 25%, #000 40%, transparent 100%);
    }}
  </style>

  <script type="application/ld+json">
{schema_json}
  </script>
</head>
<body class="min-h-screen relative antialiased selection:bg-neon-cyan selection:text-black">

  <div class="fixed inset-0 cyber-grid pointer-events-none z-0"></div>

  <!-- Header -->
  <header class="sticky top-0 z-50 bg-[#030712]/90 backdrop-blur-xl border-b border-white/10">
    <div class="h-[2px] w-full bg-gradient-to-r from-neon-emerald via-neon-cyan to-neon-violet"></div>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
      <a href="/" class="flex items-center gap-3.5 group">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-neon-emerald via-neon-cyan to-neon-violet p-[2px]">
          <div class="w-full h-full bg-[#030712] rounded-[10px] flex items-center justify-center">
            <span class="font-mono font-black text-transparent bg-clip-text bg-gradient-to-r from-neon-emerald to-neon-cyan text-lg">S/MF</span>
          </div>
        </div>
        <div>
          <span class="font-extrabold text-xl tracking-tight text-white block leading-none">Stack<span class="text-transparent bg-clip-text bg-gradient-to-r from-neon-emerald to-neon-cyan">MF</span></span>
          <span class="text-[9px] font-mono uppercase tracking-widest text-slate-400 block mt-1">Knowledge Base &bull; z/OS</span>
        </div>
      </a>

      <nav class="hidden md:flex items-center gap-6 text-sm font-medium text-slate-300">
        <a href="/blog/" class="text-neon-cyan hover:text-white transition-colors flex items-center gap-1.5 font-bold">
          <i class="fa-solid fa-book-open text-xs"></i> All Blogs
        </a>
        <a href="/#mainframe-developers" class="hover:text-neon-emerald transition-colors">Hire Developers</a>
        <a href="/#broadcom-replacement" class="hover:text-neon-amber transition-colors">Broadcom Replacement</a>
        <a href="/#mainframe-modernization" class="hover:text-neon-cyan transition-colors">Modernization</a>
        <a href="/#contact" class="px-4 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-neon-emerald to-neon-cyan text-black hover:scale-105 transition-all">Book Architect</a>
      </nav>
    </div>
  </header>

  <!-- Main Content Container -->
  <main class="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-10 pb-24">

    <!-- Breadcrumb -->
    <nav class="flex items-center gap-2 text-xs font-mono text-slate-400 mb-6 flex-wrap">
      <a href="/" class="hover:text-white transition">Home</a>
      <span>/</span>
      <a href="/blog/" class="hover:text-white transition">Knowledge Base</a>
      <span>/</span>
      <span class="text-neon-cyan">{article['category']}</span>
    </nav>

    <!-- Header Badges -->
    <div class="flex items-center gap-3 flex-wrap mb-4">
      <span class="px-3 py-1 rounded-full text-xs font-mono font-bold bg-neon-cyan/10 text-neon-cyan border border-neon-cyan/30">
        {article['category']}
      </span>
      <span class="text-xs font-mono text-slate-400 flex items-center gap-1.5">
        <i class="fa-regular fa-clock"></i> {article['reading_time']}
      </span>
      <span class="text-xs font-mono text-slate-400 flex items-center gap-1.5">
        <i class="fa-regular fa-calendar"></i> {article['date']}
      </span>
    </div>

    <!-- Title -->
    <h1 class="text-3xl sm:text-4xl lg:text-5xl font-black text-white tracking-tight leading-tight mb-6">
      {display_h1}
    </h1>

    <!-- Author & Trust Pod -->
    <div class="flex items-center justify-between p-4 rounded-xl bg-slate-900/60 border border-white/10 mb-8 flex-wrap gap-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-neon-emerald to-neon-cyan p-[2px]">
          <div class="w-full h-full bg-[#030712] rounded-full flex items-center justify-center font-mono font-bold text-white text-xs">
            A
          </div>
        </div>
        <div>
          <div class="text-sm font-bold text-white">Reviewed by Anshu</div>
          <div class="text-xs font-mono text-slate-400">Chief Technology Architect & Mainframe Systems SME</div>
        </div>
      </div>
      <span class="inline-flex items-center gap-1.5 text-xs font-mono text-neon-emerald bg-neon-emerald/10 px-3 py-1 rounded-full border border-neon-emerald/30 font-semibold">
        <i class="fa-solid fa-circle-check"></i> Verified Production Runbook
      </span>
    </div>

    <!-- Google AI Overview & Featured Snippet Quick Answer Box -->
    <div class="p-6 sm:p-7 rounded-2xl bg-gradient-to-r from-emerald-950/40 via-slate-900 to-cyan-950/40 border-2 border-neon-emerald/40 shadow-[0_0_35px_rgba(0,245,160,0.18)] mb-10 relative overflow-hidden">
      <div class="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-neon-emerald font-bold mb-2.5">
        <span class="flex h-2.5 w-2.5 relative">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-neon-emerald opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-neon-emerald"></span>
        </span>
        <span>45-Word Production Resolution (Featured Snippet)</span>
      </div>
      <p class="text-white text-base sm:text-lg leading-relaxed font-medium">
        {article['tldr']}
      </p>
    </div>

    <!-- Section 1: The Production Incident / Problem -->
    <section class="mb-12">
      <h2 class="text-2xl sm:text-3xl font-extrabold text-white mb-4 flex items-center gap-3">
        <span class="w-8 h-8 rounded-lg bg-rose-500/20 text-rose-400 flex items-center justify-center text-sm border border-rose-500/30">1</span>
        Incident Symptoms: What Triggers {article['title']}?
      </h2>
      <div class="prose prose-invert max-w-none text-slate-300">
        {problem_html}
      </div>
    </section>

    <!-- Section 2: Root Cause Mechanics -->
    <section class="mb-12">
      <h2 class="text-2xl sm:text-3xl font-extrabold text-white mb-4 flex items-center gap-3">
        <span class="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center text-sm border border-amber-500/30">2</span>
        Technical Root Cause & Architecture Mechanics
      </h2>
      <div class="prose prose-invert max-w-none text-slate-300">
        {root_cause_html}
      </div>
    </section>

    <!-- Section 3: Step-by-Step Resolution -->
    <section class="mb-12">
      <h2 class="text-2xl sm:text-3xl font-extrabold text-white mb-4 flex items-center gap-3">
        <span class="w-8 h-8 rounded-lg bg-neon-emerald/20 text-neon-emerald flex items-center justify-center text-sm border border-neon-emerald/30">3</span>
        Step-by-Step Diagnostic & Code Resolution
      </h2>
      <div class="prose prose-invert max-w-none text-slate-300">
        {solution_html}
      </div>
    </section>

    <!-- Section 4: Diagnostic Reference Matrix Table -->
    <section class="mb-12 overflow-x-auto">
      <h3 class="text-xl font-bold text-white mb-4 flex items-center gap-2.5">
        <i class="fa-solid fa-table-list text-neon-cyan"></i>
        Diagnostic Reference Matrix
      </h3>
      <table class="w-full text-left text-xs font-mono border border-white/10 rounded-xl overflow-hidden bg-slate-900/60">
        <thead class="bg-black/50 text-slate-300 uppercase border-b border-white/10">
          <tr>
            <th class="p-3">Attribute</th>
            <th class="p-3">Diagnostic Specification</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/5 text-slate-300">
          <tr>
            <td class="p-3 font-bold text-neon-cyan">Target Subsystem</td>
            <td class="p-3">IBM z/OS 2.4 - 3.1 &bull; {article['category']}</td>
          </tr>
          <tr>
            <td class="p-3 font-bold text-neon-emerald">Error Signature</td>
            <td class="p-3">{", ".join(article["tags"][:3])}</td>
          </tr>
          <tr>
            <td class="p-3 font-bold text-neon-amber">Resolution SLA</td>
            <td class="p-3">&lt; 15 Minutes via Verified StackMF Runbook</td>
          </tr>
          <tr>
            <td class="p-3 font-bold text-neon-violet">Technical Reviewer</td>
            <td class="p-3">Anshu, Chief Technology Architect &bull; StackMF Architecture Pod</td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- Section 5: Architectural Prevention & Tuning -->
    <section class="mb-12 p-6 rounded-2xl bg-slate-900/50 border border-white/10">
      <h3 class="text-xl font-bold text-white mb-4 flex items-center gap-2.5">
        <i class="fa-solid fa-list-check text-neon-cyan"></i>
        Architectural Prevention & Performance Tuning Checklist
      </h3>
      <ul class="space-y-3">
        {prevention_items}
      </ul>
    </section>

    <!-- Section 6: Frequently Asked Questions (FAQ) -->
    <section class="mb-12">
      <h2 class="text-2xl sm:text-3xl font-extrabold text-white mb-6 flex items-center gap-3">
        <span class="w-8 h-8 rounded-lg bg-cyan-500/20 text-neon-cyan flex items-center justify-center text-sm border border-cyan-500/30">?</span>
        Frequently Asked Questions
      </h2>
      <div class="space-y-4">
        <details class="p-5 rounded-2xl bg-slate-900/60 border border-white/10 group cursor-pointer" open>
          <summary class="font-bold text-white text-base flex items-center justify-between list-none">
            <span>{faq_q1}</span>
            <span class="text-neon-cyan font-mono group-open:rotate-180 transition-transform">&darr;</span>
          </summary>
          <div class="text-sm text-slate-300 mt-3 pt-3 border-t border-white/10 leading-relaxed font-light">
            {faq_a1}
          </div>
        </details>

        <details class="p-5 rounded-2xl bg-slate-900/60 border border-white/10 group cursor-pointer">
          <summary class="font-bold text-white text-base flex items-center justify-between list-none">
            <span>{faq_q2}</span>
            <span class="text-neon-cyan font-mono group-open:rotate-180 transition-transform">&darr;</span>
          </summary>
          <div class="text-sm text-slate-300 mt-3 pt-3 border-t border-white/10 leading-relaxed font-light">
            {faq_a2}
          </div>
        </details>

        <details class="p-5 rounded-2xl bg-slate-900/60 border border-white/10 group cursor-pointer">
          <summary class="font-bold text-white text-base flex items-center justify-between list-none">
            <span>{faq_q3}</span>
            <span class="text-neon-cyan font-mono group-open:rotate-180 transition-transform">&darr;</span>
          </summary>
          <div class="text-sm text-slate-300 mt-3 pt-3 border-t border-white/10 leading-relaxed font-light">
            {faq_a3}
          </div>
        </details>
      </div>
    </section>

    <!-- Section 7: Recommended Technical Runbooks (Topic Cluster Cross-linking) -->
    <section class="mb-14">
      <h3 class="text-xl font-bold text-white mb-4 flex items-center gap-2.5">
        <i class="fa-solid fa-diagram-project text-neon-emerald"></i>
        Recommended Technical Runbooks
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        {related_cards_html}
      </div>
    </section>

    <!-- Section 8: Authoritative Reference Links -->
    <section class="mb-14">
      <h3 class="text-xl font-bold text-white mb-4 flex items-center gap-2.5">
        <i class="fa-solid fa-graduation-cap text-neon-violet"></i>
        Authoritative Reference Documentation
      </h3>
      <p class="text-sm text-slate-400 mb-4">
        Official IBM manuals, Redbooks, and vendor technical advisories:
      </p>
      <ul class="space-y-3">
        {ref_items}
      </ul>
    </section>

    <!-- Tags -->
    <div class="pt-6 border-t border-white/10 flex items-center gap-2 flex-wrap mb-12">
      <span class="text-xs font-mono text-slate-400 mr-2"><i class="fa-solid fa-tags"></i> Related Topics:</span>
      {tags_html}
    </div>

    <!-- Section 9: Diagnostic Notice & Nominative Fair Use Disclaimer -->
    <div class="my-10 p-5 rounded-2xl bg-[#060a14] border border-white/10 text-xs font-mono text-slate-400 space-y-2">
      <div class="text-slate-300 font-bold flex items-center gap-2">
        <i class="fa-solid fa-scale-balanced text-neon-cyan"></i>
        <span>Diagnostic Runbook Notice &amp; Nominative Fair Use Disclaimer</span>
      </div>
      <p class="leading-relaxed">
        This diagnostic runbook is published by StackMF Technologies LLP for educational and architectural reference only. All code snippets, JCL, and procedures are provided <strong>"AS IS"</strong> without warranty of any kind. Always test changes thoroughly in non-production sysplex environments prior to production rollout.
      </p>
      <p class="leading-relaxed text-[11px] text-slate-500">
        IBM, z/OS, CICS, Db2, IMS, RACF, and IDz are registered trademarks of International Business Machines Corporation. Broadcom, CA-7, and Endevor are trademarks of Broadcom Inc. All other trademarks belong to their respective owners and are referenced under the Nominative Fair Use Doctrine (US Lanham Act 15 U.S.C. § 1125 / Section 30 of the Indian Trade Marks Act, 1999) solely for technology compatibility and diagnostic identification. StackMF Technologies LLP is an independent consulting entity not affiliated with or endorsed by these vendors. <a href="/legal.html" class="text-neon-cyan hover:underline font-semibold">View Full Legal &amp; IP Policy &rarr;</a>
      </p>
    </div>

    <!-- Bottom Advisory Banner CTA -->
    <div class="p-8 rounded-2xl bg-gradient-to-r from-emerald-950/60 via-slate-900 to-cyan-950/60 border border-neon-emerald/30 shadow-2xl relative overflow-hidden">
      <div class="relative z-10">
        <span class="px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-neon-emerald/20 text-neon-emerald border border-neon-emerald/40 uppercase tracking-widest">
          Enterprise Advisory
        </span>
        <h3 class="text-2xl sm:text-3xl font-bold text-white mt-3 mb-2">
          Struggling with Critical Mainframe Incidents or Vendor Renewal Pressure?
        </h3>
        <p class="text-slate-300 text-sm sm:text-base leading-relaxed mb-6 max-w-2xl">
          StackMF deploys certified Senior Mainframe Engineers fluent in both z/OS legacy internals (COBOL, DB2, CICS, VSAM, CA-7, Endevor) and modern cloud stacks (React, Kafka, AWS, Git). Onboard dedicated pods in 48 hours or cut Broadcom licensing by 60%.
        </p>
        <div class="flex items-center gap-4 flex-wrap">
          <a href="/#contact" class="px-6 py-3 rounded-xl text-sm font-bold bg-gradient-to-r from-neon-emerald to-neon-cyan text-black hover:scale-105 transition-all shadow-lg shadow-neon-emerald/20">
            Request Architectural Assessment
          </a>
          <a href="/blog/" class="px-5 py-3 rounded-xl text-sm font-medium text-slate-300 hover:text-white border border-white/10 hover:border-neon-cyan transition-all">
            &larr; Browse All Technical Deep Dives
          </a>
        </div>
      </div>
    </div>

  </main>

  <!-- Footer -->
  <footer class="border-t border-white/10 bg-[#02050c] text-slate-400 py-12 text-sm relative z-10">
    <div class="max-w-7xl mx-auto px-4 text-center">
      <p class="font-mono text-xs text-slate-500 mb-2">
        &copy; 2026 StackMF Technologies LLP &bull; Enterprise Mainframe Modernization &amp; Dual-Stack Pods.
      </p>
      <p class="font-mono text-[10px] text-slate-600 mb-4 max-w-2xl mx-auto">
        IBM, z/OS, CICS, Db2, IMS, Broadcom, CA-7, Endevor, Control-M, Stonebranch, ChangeMan, and Zowe are trademarks of their respective owners, used under nominative fair use.
      </p>
      <div class="flex items-center justify-center gap-4 text-xs font-mono text-slate-400">
        <a href="/" class="hover:text-neon-cyan">Home</a>
        <span>&bull;</span>
        <a href="/blog/" class="hover:text-neon-cyan">Knowledge Base</a>
        <span>&bull;</span>
        <a href="/legal.html" class="text-neon-cyan hover:underline font-bold">Legal &amp; Trademarks</a>
        <span>&bull;</span>
        <a href="/#contact" class="hover:text-neon-cyan">Contact</a>
      </div>
    </div>
  </footer>

</body>
</html>'''

def generate_blog_index(articles):
    """Generates the interactive, filterable blog index page (blog/index.html)."""
    categories = sorted(list(set(a['category'] for a in articles)))
    
    cards_html = ""
    for a in articles:
        tags_pills = "".join([f'<span class="text-[10px] font-mono px-2 py-0.5 rounded bg-white/5 text-slate-300 border border-white/5">{t}</span>' for t in a['tags'][:4]])
        cards_html += f"""
        <article class="blog-card flex flex-col justify-between p-6 rounded-2xl bg-slate-900/60 border border-white/10 hover:border-neon-cyan/50 hover:bg-slate-900/90 transition-all duration-300 group shadow-lg"
                 data-category="{a['category']}"
                 data-title="{a['title'].lower()}"
                 data-tags="{(' '.join(a['tags'])).lower()}">
          <div>
            <div class="flex items-center justify-between text-xs font-mono text-slate-400 mb-3">
              <span class="px-2.5 py-0.5 rounded-full font-semibold bg-neon-cyan/10 text-neon-cyan border border-neon-cyan/30 text-[11px]">
                {a['category']}
              </span>
              <span class="flex items-center gap-1"><i class="fa-regular fa-clock"></i> {a['reading_time']}</span>
            </div>
            
            <h2 class="text-xl font-bold text-white group-hover:text-neon-cyan transition-colors line-clamp-2 mb-3">
              <a href="/blog/{a['slug']}.html">{a['title']}</a>
            </h2>
            
            <p class="text-slate-300 text-sm leading-relaxed line-clamp-3 mb-4 font-light">
              {a['tldr']}
            </p>
          </div>

          <div>
            <div class="flex items-center gap-1.5 flex-wrap mb-4">
              {tags_pills}
            </div>
            
            <a href="/blog/{a['slug']}.html" class="inline-flex items-center gap-2 text-xs font-mono font-bold text-neon-emerald group-hover:text-neon-cyan transition-colors">
              <span>Read Full Solution</span>
              <i class="fa-solid fa-arrow-right text-[10px] group-hover:translate-x-1 transition-transform"></i>
            </a>
          </div>
        </article>
        """

    cat_pills = f'<button onclick="filterCategory(\'all\', this)" class="cat-btn px-4 py-2 rounded-xl text-xs font-mono font-bold bg-neon-cyan text-black transition">All Disciplines ({len(articles)})</button>'
    for cat in categories:
        count = sum(1 for a in articles if a['category'] == cat)
        cat_pills += f'<button onclick="filterCategory(\'{cat}\', this)" class="cat-btn px-4 py-2 rounded-xl text-xs font-mono font-medium text-slate-300 bg-white/5 border border-white/10 hover:border-neon-cyan hover:text-white transition">{cat} ({count})</button>'

    template = """<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  
  <title>Mainframe Knowledge Base & Engineering Blog | StackMF</title>
  <meta name="title" content="Mainframe Knowledge Base & Engineering Blog | StackMF">
  <meta name="description" content="Explore __COUNT__+ production-tested technical guides for IBM z/OS Mainframe engineers: Resolving S0C7/S0C4 ABENDs, DB2 SQL optimization, CICS/VSAM tuning, REXX automation, and Broadcom replacement.">
  <meta name="keywords" content="mainframe blog, cobol errors, db2 sql tuning, cics asra abend, vsam file status 93, ca-7 replacement, endevor to git, z/os connect, stackmf">
  <meta name="author" content="StackMF Technologies LLP">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="__SITE_URL__/blog/">

  <!-- Open Graph -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="__SITE_URL__/blog/">
  <meta property="og:title" content="StackMF Mainframe Engineering & Modernization Knowledge Base">
  <meta property="og:description" content="Production-tested troubleshooting for COBOL, DB2, CICS, VSAM, IMS, REXX, Endevor, ChangeMan, and CA-7.">

  <link rel="icon" type="image/png" sizes="32x32" href="https://assets.zyrosite.com/cdn-cgi/image/format=auto,w=32,h=32,fit=crop,f=png/ALpXb5J8LKfeaWNX/logo-YZ9nXvEj8KiMb60r.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            neon: {
              emerald: '#00F5A0',
              cyan: '#00F0FF',
              violet: '#8B5CF6',
              amber: '#FBBF24',
              rose: '#F43F5E'
            },
            cyber: {
              darker: '#030712',
              dark: '#070a0f',
              surface: '#0d131d',
              card: '#111827',
              border: 'rgba(255, 255, 255, 0.08)'
            }
          },
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace']
          }
        }
      }
    }
  </script>

  <style>
    body { background-color: #030712; color: #f1f5f9; font-family: 'Inter', sans-serif; }
    .cyber-grid {
      background-size: 48px 48px;
      background-image: 
        linear-gradient(to right, rgba(255, 255, 255, 0.035) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(255, 255, 255, 0.035) 1px, transparent 1px);
      mask-image: radial-gradient(ellipse 70% 60% at 50% 25%, #000 40%, transparent 100%);
      -webkit-mask-image: radial-gradient(ellipse 70% 60% at 50% 25%, #000 40%, transparent 100%);
    }
  </style>
</head>
<body class="min-h-screen relative antialiased selection:bg-neon-cyan selection:text-black">

  <div class="fixed inset-0 cyber-grid pointer-events-none z-0"></div>

  <!-- Header -->
  <header class="sticky top-0 z-50 bg-[#030712]/90 backdrop-blur-xl border-b border-white/10">
    <div class="h-[2px] w-full bg-gradient-to-r from-neon-emerald via-neon-cyan to-neon-violet"></div>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
      <a href="/" class="flex items-center gap-3.5 group">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-neon-emerald via-neon-cyan to-neon-violet p-[2px]">
          <div class="w-full h-full bg-[#030712] rounded-[10px] flex items-center justify-center">
            <span class="font-mono font-black text-transparent bg-clip-text bg-gradient-to-r from-neon-emerald to-neon-cyan text-lg">S/MF</span>
          </div>
        </div>
        <div>
          <span class="font-extrabold text-xl tracking-tight text-white block leading-none">Stack<span class="text-transparent bg-clip-text bg-gradient-to-r from-neon-emerald to-neon-cyan">MF</span></span>
          <span class="text-[9px] font-mono uppercase tracking-widest text-slate-400 block mt-1">Enterprise Mainframe Pods</span>
        </div>
      </a>

      <nav class="hidden md:flex items-center gap-6 text-sm font-medium text-slate-300">
        <a href="/" class="hover:text-neon-cyan transition-colors">Home</a>
        <a href="/#mainframe-developers" class="hover:text-neon-emerald transition-colors">Hire Developers</a>
        <a href="/#broadcom-replacement" class="hover:text-neon-amber transition-colors">Broadcom Replacement</a>
        <a href="/#mainframe-modernization" class="hover:text-neon-cyan transition-colors">Modernization</a>
        <a href="/#contact" class="px-4 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-neon-emerald to-neon-cyan text-black hover:scale-105 transition-all">Book Architect</a>
      </nav>
    </div>
  </header>

  <!-- Hero Section -->
  <section class="relative pt-16 pb-12 overflow-hidden z-10 border-b border-white/10 bg-[#050814]/70">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
      <span class="px-3.5 py-1 rounded-full text-xs font-mono font-bold bg-neon-cyan/10 text-neon-cyan border border-neon-cyan/30 inline-block mb-4">
        <i class="fa-solid fa-terminal mr-1.5"></i> PRODUCTION MAINFRAME RUNBOOKS & ADVISORIES
      </span>
      <h1 class="text-4xl sm:text-6xl font-black text-white tracking-tight leading-tight mb-4">
        Mainframe Systems & Modernization Knowledge Base
      </h1>
      <p class="text-slate-300 text-base sm:text-lg max-w-3xl mx-auto font-light leading-relaxed mb-8">
        Production-tested diagnostic runbooks for z/OS architects: Diagnosing S0C7/S0C4 ABENDs, DB2 -911 deadlocks, CICS ASRA exceptions, VSAM status codes, and Broadcom tool de-licensing.
      </p>

      <!-- Search Input -->
      <div class="max-w-xl mx-auto relative mb-6">
        <i class="fa-solid fa-magnifying-glass absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"></i>
        <input type="text" id="searchInput" oninput="searchPosts()" placeholder="Search error code (e.g. S0C7, -911, CA-7, VSAM 93)..." class="w-full pl-11 pr-4 py-3.5 rounded-2xl bg-slate-900 border border-white/15 text-white placeholder-slate-500 focus:outline-none focus:border-neon-cyan font-mono text-sm transition">
      </div>

      <!-- Categories Pills -->
      <div class="flex items-center justify-center gap-2 flex-wrap" id="categoryContainer">
        __CAT_PILLS__
      </div>
    </div>
  </section>

  <!-- Blog Posts Grid -->
  <main class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" id="postsGrid">
      __CARDS_HTML__
    </div>
    <div id="noResults" class="hidden text-center py-20 text-slate-400 font-mono text-sm">
      No runbooks match your search filter. <button onclick="resetFilters()" class="text-neon-cyan underline ml-2">Reset search</button>
    </div>
  </main>

  <!-- Interactive Search / Filter Script -->
  <script>
    let activeCat = 'all';

    function filterCategory(cat, btn) {
      activeCat = cat;
      document.querySelectorAll('.cat-btn').forEach(b => {
        b.className = 'cat-btn px-4 py-2 rounded-xl text-xs font-mono font-medium text-slate-300 bg-white/5 border border-white/10 hover:border-neon-cyan hover:text-white transition';
      });
      btn.className = 'cat-btn px-4 py-2 rounded-xl text-xs font-mono font-bold bg-neon-cyan text-black transition';
      searchPosts();
    }

    function searchPosts() {
      const q = document.getElementById('searchInput').value.toLowerCase().trim();
      const cards = document.querySelectorAll('.blog-card');
      let visibleCount = 0;

      cards.forEach(c => {
        const cat = c.getAttribute('data-category');
        const title = c.getAttribute('data-title');
        const tags = c.getAttribute('data-tags');

        const matchesCat = (activeCat === 'all' || cat === activeCat);
        const matchesQuery = !q || title.includes(q) || tags.includes(q);

        if (matchesCat && matchesQuery) {
          c.style.display = 'flex';
          visibleCount++;
        } else {
          c.style.display = 'none';
        }
      });

      document.getElementById('noResults').style.display = visibleCount === 0 ? 'block' : 'none';
    }

    function resetFilters() {
      document.getElementById('searchInput').value = '';
      const allBtn = document.querySelector('.cat-btn');
      if (allBtn) filterCategory('all', allBtn);
    }
  </script>

  <!-- Footer -->
  <footer class="border-t border-white/10 bg-[#02050c] text-slate-400 py-12 text-sm relative z-10">
    <div class="max-w-7xl mx-auto px-4 text-center">
      <p class="font-mono text-xs text-slate-500 mb-2">
        &copy; 2026 StackMF Technologies LLP &bull; Enterprise Mainframe Modernization &amp; Broadcom Replacement Pods.
      </p>
      <p class="font-mono text-[10px] text-slate-600 mb-4 max-w-2xl mx-auto">
        IBM, z/OS, CICS, Db2, IMS, Broadcom, CA-7, Endevor, Control-M, Stonebranch, ChangeMan, and Zowe are trademarks of their respective owners, used under nominative fair use.
      </p>
      <div class="flex items-center justify-center gap-4 text-xs font-mono text-slate-400">
        <a href="/" class="hover:text-neon-cyan">Home</a>
        <span>&bull;</span>
        <a href="/blog/" class="hover:text-neon-cyan">Knowledge Base</a>
        <span>&bull;</span>
        <a href="/legal.html" class="text-neon-cyan hover:underline font-bold">Legal &amp; Trademarks</a>
        <span>&bull;</span>
        <a href="/#contact" class="hover:text-neon-cyan">Contact</a>
      </div>
    </div>
  </footer>

</body>
</html>"""

    return template.replace('__SITE_URL__', SITE_URL).replace('__COUNT__', str(len(articles))).replace('__CAT_PILLS__', cat_pills).replace('__CARDS_HTML__', cards_html)

def update_sitemap(articles):
    """Generates a 100% Google-compliant sitemap.xml with zero illegal hash fragments."""
    today_iso = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
    
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"',
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml"',
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
        '  <url>',
        f'    <loc>{SITE_URL}/</loc>',
        f'    <lastmod>{today_iso}</lastmod>',
        '    <changefreq>weekly</changefreq>',
        '    <priority>1.0</priority>',
        '  </url>',
        '  <url>',
        f'    <loc>{SITE_URL}/blog/</loc>',
        f'    <lastmod>{today_iso}</lastmod>',
        '    <changefreq>daily</changefreq>',
        '    <priority>0.95</priority>',
        '  </url>',
        '  <url>',
        f'    <loc>{SITE_URL}/legal.html</loc>',
        f'    <lastmod>{today_iso}</lastmod>',
        '    <changefreq>monthly</changefreq>',
        '    <priority>0.70</priority>',
        '  </url>'
    ]
    
    for a in articles:
        article_url = f"{SITE_URL}/blog/{a['slug']}.html"
        xml_lines.extend([
            '  <url>',
            f'    <loc>{article_url}</loc>',
            f'    <lastmod>{a["date"]}T08:00:00+00:00</lastmod>',
            '    <changefreq>monthly</changefreq>',
            '    <priority>0.85</priority>',
            '  </url>'
        ])
        
    xml_lines.append('</urlset>\n')
    
    with open(SITEMAP_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(xml_lines))
    print(f"Generated clean sitemap.xml with {len(articles) + 3} canonical URLs (Zero illegal hash fragments).")

def update_llms(articles):
    """Updates llms.txt and llms-full.txt to reference the blog repository."""
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    
    llms_content = f"""# StackMF Technologies LLP (stackmf.com)
# Generated: {today}
# Entity: StackMF Technologies LLP
# Specialization: Enterprise Mainframe Modernization, Broadcom Tool Replacement, and Dual-Stack Engineering Pods

> StackMF Technologies LLP is the global leader in Enterprise Mainframe Modernization, Broadcom Mainframe Product Replacement (CA-7, Endevor, File-AID, Datacom, Sysview), Full-Stack Mainframe Hybrid Integration (COBOL, CICS, DB2, VSAM to React, Node.js, Python, Kafka, AWS, Azure), and 24/7 SLA-backed Mainframe Application Development and Maintenance (AMS).

## Canonical Enterprise Solutions
- [Hire Mainframe Developers in 48 Hours](https://stackmf.com/#mainframe-developers): Certified senior z/OS engineers fluent in both COBOL/CICS/DB2 and modern React/Node.js/Kafka.
- [Broadcom Mainframe Replacement](https://stackmf.com/#broadcom-replacement): Zero-downtime migration replacing CA-7 with Stonebranch/Control-M, and Endevor with Git/GitHub Actions/IBM DBB.
- [Enterprise Mainframe Modernization](https://stackmf.com/#mainframe-modernization): Automated COBOL microservice refactoring and AWS Blu Age / GCP Dual Run cloud replatforming.
- [Mainframe AMS & 4HRA MIPS Optimization](https://stackmf.com/#maintenance-ams): 24/7 SLA support, batch window compression, and IBM MLC reduction.
- [Interactive Pod Builder & ROI Configurator](https://stackmf.com/#team-builder): Real-time velocity and cost savings modeling.
- [Broadcom TCO Savings Calculator](https://stackmf.com/#tco-calculator): Interactive ROI calculation tool.
- [Live z/OS CLI Console Simulator](https://stackmf.com/#terminal-section): Terminal simulator for z/OS commands.
- [Legal, Nominative Fair Use & Disclaimers](https://stackmf.com/legal.html): Statutory compliance, IP notices, and IT Act Grievance details.

## Production Mainframe Troubleshooting Index ({len(articles)} Runbooks)
"""
    for a in articles:
        llms_content += f"- [{a['title']} Fix](https://stackmf.com/blog/{a['slug']}.html): {a['tldr']}\n"

    llms_content += """
## Contact & Inquiries
- Website: https://stackmf.com
- Knowledge Base: https://stackmf.com/blog/
- Email: contact@stackmf.com
- Co-Founders: Anshu, Narendra, George
- Headquarters: Indore, Madhya Pradesh, India
"""

    with open(LLMS_FILE, 'w', encoding='utf-8') as f:
        f.write(llms_content.strip() + '\n')
    with open(LLMS_FULL_FILE, 'w', encoding='utf-8') as f:
        f.write(llms_content.strip() + '\n')
    print(f"Updated llms.txt and llms-full.txt with all {len(articles)} articles.")

def main():
    raw_combined = ARTICLES + ADDITIONAL_ARTICLES
    seen_slugs = set()
    all_unique_articles = []

    for a in raw_combined:
        if a['slug'] not in seen_slugs:
            seen_slugs.add(a['slug'])
            all_unique_articles.append(a)

    print(f"Generating {len(all_unique_articles)} comprehensive mainframe blog articles with Multi-Entity Schema and Featured Snippet Boxes...")

    for a in all_unique_articles:
        filename = f"{a['slug']}.html"
        filepath = os.path.join(BLOG_DIR, filename)
        html = generate_article_page(a, all_unique_articles)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Generated: blog/{filename}")

    index_html = generate_blog_index(all_unique_articles)
    with open(os.path.join(BLOG_DIR, "index.html"), 'w', encoding='utf-8') as f:
        f.write(index_html)
    print("Generated: blog/index.html")

    posts_meta = [{
        "slug": a['slug'],
        "title": a['title'],
        "date": a['date'],
        "category": a['category'],
        "tags": a['tags'],
        "reading_time": a['reading_time'],
        "tldr": a['tldr']
    } for a in all_unique_articles]
    with open(os.path.join(BLOG_DIR, "posts.json"), 'w', encoding='utf-8') as f:
        json.dump(posts_meta, f, indent=2)
    print("Generated: blog/posts.json")

    update_sitemap(all_unique_articles)
    update_llms(all_unique_articles)

    print(f"SUCCESS: All {len(all_unique_articles)} mainframe blogs built with Schema.org @graph and clean sitemap.xml!")

if __name__ == '__main__':
    main()
