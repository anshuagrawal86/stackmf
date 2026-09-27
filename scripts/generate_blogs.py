import os
import re
import json
import datetime
from blogs_data import ARTICLES

SITE_URL = "https://stackmf.com"
BLOG_DIR = os.path.join(os.path.dirname(__file__), "..", "blog")
SITEMAP_FILE = os.path.join(os.path.dirname(__file__), "..", "sitemap.xml")
LLMS_FILE = os.path.join(os.path.dirname(__file__), "..", "llms.txt")
LLMS_FULL_FILE = os.path.join(os.path.dirname(__file__), "..", "llms-full.txt")

os.makedirs(BLOG_DIR, exist_ok=True)

def markdown_to_html(md_text):
    """Converts a subset of markdown (code blocks, inline code, headings, lists, bold, links) to HTML."""
    # Escape code blocks first
    code_blocks = []
    def save_code_block(match):
        lang = match.group(1) or 'text'
        code = match.group(2)
        # Escape html entities in code
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

    # Match ```lang ... ```
    content = re.sub(r'```([a-zA-Z0-9_\-]*)\n(.*?)```', save_code_block, md_text, flags=re.DOTALL)

    # Process line-by-line
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

        # Headings
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

        # List items (- or *)
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

        # Regular paragraph
        if not stripped.startswith('<!--CODE_BLOCK_'):
            output_lines.append(f'<p class="text-slate-300 leading-relaxed my-4 text-base sm:text-lg font-light">{stripped}</p>')
        else:
            output_lines.append(stripped)

    if in_list:
        output_lines.append('</ul>')

    html_out = '\n'.join(output_lines)

    # Inline replacements: bold, inline code, links
    html_out = re.sub(r'\*\*(.*?)\*\*', r'<strong class="text-white font-semibold">\1</strong>', html_out)
    html_out = re.sub(r'`([^`]+)`', r'<code class="font-mono text-neon-cyan bg-slate-900/90 px-1.5 py-0.5 rounded border border-white/10 text-xs sm:text-sm">\1</code>', html_out)
    html_out = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener noreferrer" class="text-neon-cyan hover:underline font-medium">\1 <i class="fa-solid fa-arrow-up-right-from-square text-[10px] ml-0.5"></i></a>', html_out)

    # Restore code blocks
    for idx, block in enumerate(code_blocks):
        html_out = html_out.replace(f'<!--CODE_BLOCK_{idx}-->', block)

    return html_out

def generate_article_page(article):
    """Generates the full standalone HTML page for an article."""
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
                <span class="text-sm font-medium text-slate-200 group-hover:text-white">{ref['title']}</span>
              </div>
              <a href="{ref['url']}" target="_blank" rel="noopener noreferrer" class="text-xs font-mono text-neon-cyan hover:text-white flex items-center gap-1.5 px-3 py-1 rounded-lg bg-white/5 border border-white/10 hover:bg-neon-cyan hover:text-black transition">
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

    article_url = f"{SITE_URL}/blog/{article['slug']}.html"

    # Schema JSON-LD
    schema_json = json.dumps({
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": article['title'],
        "description": article['tldr'],
        "url": article_url,
        "datePublished": f"{article['date']}T08:00:00+00:00",
        "dateModified": f"{article['date']}T08:00:00+00:00",
        "inLanguage": "en",
        "author": {
            "@type": "Organization",
            "name": "StackMF Mainframe Architecture Pod",
            "url": "https://stackmf.com"
        },
        "publisher": {
            "@type": "Organization",
            "name": "StackMF Technologies LLP",
            "url": "https://stackmf.com",
            "logo": {
                "@type": "ImageObject",
                "url": "https://assets.zyrosite.com/cdn-cgi/image/format=auto,w=32,h=32,fit=crop,f=png/ALpXb5J8LKfeaWNX/logo-YZ9nXvEj8KiMb60r.png"
            }
        },
        "about": [article['category']] + article['tags'],
        "articleBody": f"{article['problem']} {article['root_cause']} {article['solution']}"
    }, indent=2)

    return f'''<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  
  <title>{article['title']} | StackMF Mainframe Knowledge Base</title>
  <meta name="title" content="{article['title']} | StackMF">
  <meta name="description" content="{article['tldr']}">
  <meta name="keywords" content="{', '.join(article['tags'])}, mainframe modernization, cobol abend, z/os debugging, stackmf">
  <meta name="author" content="StackMF Mainframe Architecture Pod">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
  <link rel="canonical" href="{article_url}">

  <!-- Open Graph -->
  <meta property="og:type" content="article">
  <meta property="og:url" content="{article_url}">
  <meta property="og:title" content="{article['title']}">
  <meta property="og:description" content="{article['tldr']}">
  <meta property="og:site_name" content="StackMF Technologies LLP">
  <meta property="article:published_time" content="{article['date']}T08:00:00+00:00">
  <meta property="article:section" content="{article['category']}">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{article['title']}">
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
      {article['title']}
    </h1>

    <!-- Author & Trust Pod -->
    <div class="flex items-center justify-between p-4 rounded-xl bg-slate-900/60 border border-white/10 mb-8 flex-wrap gap-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-neon-emerald to-neon-cyan p-[2px]">
          <div class="w-full h-full bg-[#030712] rounded-full flex items-center justify-center">
            <i class="fa-solid fa-server text-neon-emerald text-sm"></i>
          </div>
        </div>
        <div>
          <div class="text-sm font-bold text-white">StackMF Mainframe Architecture Pod</div>
          <div class="text-xs font-mono text-slate-400">Principal Modernization & z/OS Systems Engineers</div>
        </div>
      </div>
      <span class="inline-flex items-center gap-1.5 text-xs font-mono text-neon-emerald bg-neon-emerald/10 px-3 py-1 rounded-full border border-neon-emerald/30 font-semibold">
        <i class="fa-solid fa-circle-check"></i> Verified Production Fix
      </span>
    </div>

    <!-- TL;DR Box -->
    <div class="p-6 rounded-2xl bg-gradient-to-r from-cyan-950/40 via-slate-900 to-emerald-950/40 border border-neon-cyan/30 shadow-xl mb-12">
      <div class="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-neon-cyan font-bold mb-2">
        <i class="fa-solid fa-bolt"></i> Executive Summary / TL;DR
      </div>
      <p class="text-slate-200 text-base sm:text-lg leading-relaxed font-normal">
        {article['tldr']}
      </p>
    </div>

    <!-- Section 1: The Production Incident / Problem -->
    <section class="mb-12">
      <h2 class="text-2xl sm:text-3xl font-extrabold text-white mb-4 flex items-center gap-3">
        <span class="w-8 h-8 rounded-lg bg-rose-500/20 text-rose-400 flex items-center justify-center text-sm border border-rose-500/30">1</span>
        The Real-World Developer Incident
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
        Step-by-Step Production Resolution
      </h2>
      <div class="prose prose-invert max-w-none text-slate-300">
        {solution_html}
      </div>
    </section>

    <!-- Section 4: Architectural Prevention & Tuning -->
    <section class="mb-12 p-6 rounded-2xl bg-slate-900/50 border border-white/10">
      <h3 class="text-xl font-bold text-white mb-4 flex items-center gap-2.5">
        <i class="fa-solid fa-list-check text-neon-cyan"></i>
        Architectural Prevention & Performance Tuning Checklist
      </h3>
      <ul class="space-y-3">
        {prevention_items}
      </ul>
    </section>

    <!-- Section 5: Authoritative Reference Links -->
    <section class="mb-14">
      <h3 class="text-xl font-bold text-white mb-4 flex items-center gap-2.5">
        <i class="fa-solid fa-graduation-cap text-neon-violet"></i>
        Authoritative Reference Documentation
      </h3>
      <p class="text-sm text-slate-400 mb-4">
        Explore more directly in official manuals, IBM Knowledge Center, and vendor technical advisories:
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
            &larr; Browse All 25 Technical Deep Dives
          </a>
        </div>
      </div>
    </div>

  </main>

  <!-- Footer -->
  <footer class="border-t border-white/10 bg-[#02050c] text-slate-400 py-12 text-sm relative z-10">
    <div class="max-w-7xl mx-auto px-4 text-center">
      <p class="font-mono text-xs text-slate-500 mb-2">
        &copy; 2026 StackMF Technologies LLP &bull; Enterprise Mainframe Modernization & Broadcom Replacement Pods.
      </p>
      <div class="flex items-center justify-center gap-4 text-xs font-mono text-slate-400">
        <a href="/" class="hover:text-neon-cyan">Home</a>
        <span>&bull;</span>
        <a href="/blog/" class="hover:text-neon-cyan">Knowledge Base</a>
        <span>&bull;</span>
        <a href="/#broadcom-replacement" class="hover:text-neon-cyan">Broadcom Replacement</a>
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
        cards_html += f'''
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
        '''

    cat_pills = '<button onclick="filterCategory(\'all\', this)" class="cat-btn px-4 py-2 rounded-xl text-xs font-mono font-bold bg-neon-cyan text-black transition">All Disciplines ({})</button>'.format(len(articles))
    for cat in categories:
        count = sum(1 for a in articles if a['category'] == cat)
        cat_pills += f'<button onclick="filterCategory(\'{cat}\', this)" class="cat-btn px-4 py-2 rounded-xl text-xs font-mono font-medium text-slate-300 bg-white/5 border border-white/10 hover:border-neon-cyan hover:text-white transition">{cat} ({count})</button>'

    return f'''<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  
  <title>Mainframe Knowledge Base & Engineering Blog | StackMF</title>
  <meta name="title" content="Mainframe Knowledge Base & Engineering Blog | StackMF">
  <meta name="description" content="Explore {len(articles)}+ production-tested technical guides for IBM z/OS Mainframe engineers: Resolving S0C7/S0C4 ABENDs, DB2 SQL optimization, CICS/VSAM tuning, REXX automation, and Broadcom replacement.">
  <meta name="keywords" content="mainframe blog, cobol errors, db2 sql tuning, cics asra abend, vsam file status 93, ca-7 replacement, endevor to git, z/os connect, stackmf">
  <meta name="author" content="StackMF Technologies LLP">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{SITE_URL}/blog/">

  <!-- Open Graph -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="{SITE_URL}/blog/">
  <meta property="og:title" content="StackMF Mainframe Engineering & Modernization Knowledge Base">
  <meta property="og:description" content="Production-tested troubleshooting for COBOL, DB2, CICS, VSAM, IMS, REXX, Endevor, ChangeMan, and CA-7.">

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
  {{
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "name": "StackMF Mainframe Engineering & Modernization Knowledge Base",
    "description": "Deep-dive technical knowledge base covering COBOL, DB2 for z/OS, CICS TS, VSAM, IMS DB/DC, Telon, REXX, Endevor, ChangeMan, and CA-7.",
    "url": "{SITE_URL}/blog/",
    "publisher": {{
      "@type": "Organization",
      "name": "StackMF Technologies LLP",
      "url": "{SITE_URL}"
    }}
  }}
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
          <span class="text-[9px] font-mono uppercase tracking-widest text-slate-400 block mt-1">Mainframe &bull; Hybrid Cloud</span>
        </div>
      </a>

      <nav class="hidden md:flex items-center gap-6 text-sm font-medium text-slate-300">
        <a href="/" class="hover:text-neon-cyan transition-colors">Home</a>
        <a href="/#mainframe-developers" class="hover:text-neon-emerald transition-colors">Hire Developers</a>
        <a href="/#broadcom-replacement" class="hover:text-neon-amber transition-colors">Broadcom Replacement</a>
        <a href="/#mainframe-modernization" class="hover:text-neon-cyan transition-colors">Modernization</a>
        <a href="/#contact" class="px-4 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-neon-emerald to-neon-cyan text-black hover:scale-105 transition-all">Book Assessment</a>
      </nav>
    </div>
  </header>

  <!-- Hero Section -->
  <section class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-12 text-center">
    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-neon-cyan/10 text-neon-cyan border border-neon-cyan/30 text-xs font-mono uppercase tracking-wider mb-6">
      <span class="w-2 h-2 rounded-full bg-neon-cyan animate-pulse"></span>
      Daily Mainframe Advisory &bull; Continuous Publication
    </div>
    
    <h1 class="text-4xl sm:text-5xl lg:text-6xl font-black text-white tracking-tight leading-tight max-w-4xl mx-auto mb-6">
      Mainframe Application Engineering & <span class="text-transparent bg-clip-text bg-gradient-to-r from-neon-emerald via-neon-cyan to-neon-violet">Modernization Knowledge Base</span>
    </h1>

    <p class="text-slate-300 text-lg max-w-3xl mx-auto leading-relaxed font-light mb-10">
      Production-tested blueprints for enterprise engineers: Resolving S0C7 & S0C4 ABENDs, tuning DB2 SQL queries, debugging CICS & VSAM deadlocks, automating REXX workflows, and replacing Broadcom CA-7 / Endevor.
    </p>

    <!-- Search Bar -->
    <div class="max-w-2xl mx-auto relative mb-10">
      <i class="fa-solid fa-magnifying-glass absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"></i>
      <input type="text" id="searchInput" oninput="handleSearch()" placeholder="Search error codes, topics (e.g. S0C7, SQLCODE -911, VSAM, CA-7, REXX)..." 
             class="w-full pl-12 pr-4 py-4 rounded-2xl bg-slate-900/90 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-neon-cyan shadow-2xl text-sm font-mono">
    </div>

    <!-- Category Filters -->
    <div class="flex items-center justify-center gap-2 flex-wrap max-w-4xl mx-auto" id="categoryFilters">
      {cat_pills}
    </div>
  </section>

  <!-- Blog Cards Grid -->
  <section class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-24">
    <div class="flex items-center justify-between mb-8 pb-4 border-b border-white/10">
      <div class="text-xs font-mono text-slate-400">
        Showing <span id="articleCount" class="text-neon-cyan font-bold">{len(articles)}</span> Technical Articles
      </div>
      <div class="text-xs font-mono text-neon-emerald flex items-center gap-1.5">
        <i class="fa-solid fa-circle-check"></i> Authoritative IBM & Broadcom References Included
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" id="articlesGrid">
      {cards_html}
    </div>

    <div id="noResults" class="hidden text-center py-16 text-slate-400 font-mono text-sm">
      <i class="fa-solid fa-triangle-exclamation text-amber-400 text-3xl mb-3 block"></i>
      No articles found matching your query. Try searching for "S0C7", "DB2", "VSAM", or "CA-7".
    </div>
  </section>

  <!-- Interactive Search / Filter Script -->
  <script>
    let activeCategory = 'all';

    function filterCategory(cat, btn) {{
      activeCategory = cat;
      document.querySelectorAll('.cat-btn').forEach(b => {{
        b.classList.remove('bg-neon-cyan', 'text-black', 'font-bold');
        b.classList.add('text-slate-300', 'bg-white/5', 'font-medium');
      }});
      btn.classList.add('bg-neon-cyan', 'text-black', 'font-bold');
      btn.classList.remove('text-slate-300', 'bg-white/5', 'font-medium');
      applyFilters();
    }}

    function handleSearch() {{
      applyFilters();
    }}

    function applyFilters() {{
      const query = document.getElementById('searchInput').value.toLowerCase().trim();
      const cards = document.querySelectorAll('.blog-card');
      let visibleCount = 0;

      cards.forEach(card => {{
        const cat = card.getAttribute('data-category');
        const title = card.getAttribute('data-title');
        const tags = card.getAttribute('data-tags');

        const matchesCat = (activeCategory === 'all' || cat === activeCategory);
        const matchesQuery = !query || title.includes(query) || tags.includes(query);

        if (matchesCat && matchesQuery) {{
          card.style.display = 'flex';
          visibleCount++;
        }} else {{
          card.style.display = 'none';
        }}
      }});

      document.getElementById('articleCount').innerText = visibleCount;
      const noResults = document.getElementById('noResults');
      if (visibleCount === 0) {{
        noResults.classList.remove('hidden');
      }} else {{
        noResults.classList.add('hidden');
      }}
    }}
  </script>

  <!-- Footer -->
  <footer class="border-t border-white/10 bg-[#02050c] text-slate-400 py-12 text-sm relative z-10">
    <div class="max-w-7xl mx-auto px-4 text-center">
      <p class="font-mono text-xs text-slate-500 mb-2">
        &copy; 2026 StackMF Technologies LLP &bull; Enterprise Mainframe Modernization & Broadcom Replacement Pods.
      </p>
      <div class="flex items-center justify-center gap-4 text-xs font-mono text-slate-400">
        <a href="/" class="hover:text-neon-cyan">Home</a>
        <span>&bull;</span>
        <a href="/blog/" class="hover:text-neon-cyan">Knowledge Base</a>
        <span>&bull;</span>
        <a href="/#broadcom-replacement" class="hover:text-neon-cyan">Broadcom Replacement</a>
        <span>&bull;</span>
        <a href="/#contact" class="hover:text-neon-cyan">Contact</a>
      </div>
    </div>
  </footer>

</body>
</html>'''

def update_sitemap(articles):
    """Updates sitemap.xml to include the blog hub and all individual articles."""
    today_iso = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
    
    # Read existing sitemap
    with open(SITEMAP_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Collect existing locs
    existing_locs = set(re.findall(r'<loc>(.*?)</loc>', content))

    new_urls = []
    # Add blog hub if missing
    blog_hub_url = f"{SITE_URL}/blog/"
    if blog_hub_url not in existing_locs:
        new_urls.append(f'''  <url>
    <loc>{blog_hub_url}</loc>
    <lastmod>{today_iso}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>''')

    for a in articles:
        article_url = f"{SITE_URL}/blog/{a['slug']}.html"
        if article_url not in existing_locs:
            new_urls.append(f'''  <url>
    <loc>{article_url}</loc>
    <lastmod>{a['date']}T08:00:00+00:00</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.85</priority>
  </url>''')

    if new_urls:
        insert_marker = '</urlset>'
        replacement = '\n' + '\n'.join(new_urls) + '\n' + insert_marker
        content = content.replace(insert_marker, replacement)
        with open(SITEMAP_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated sitemap.xml with {len(new_urls)} new URLs.")

def update_llms(articles):
    """Updates llms.txt and llms-full.txt to reference the blog repository."""
    # Update llms.txt
    with open(LLMS_FILE, 'r', encoding='utf-8') as f:
        llms_text = f.read()

    if "## Mainframe Engineering Knowledge Base & Production Advisories" not in llms_text:
        kb_section = """\n## Mainframe Engineering Knowledge Base & Production Advisories
StackMF publishes daily production troubleshooting guides, ABEND resolution runbooks, and performance tuning advisories for enterprise z/OS developers:
- [Mainframe Knowledge Base Hub](https://stackmf.com/blog/): Curated deep dives covering COBOL, DB2, CICS, VSAM, IMS DB/DC, Telon, REXX, Endevor, ChangeMan, and CA-7.
"""
        # Append before Contact
        llms_text = llms_text.replace("## Contact & Inquiries", kb_section + "\n## Contact & Inquiries")
        with open(LLMS_FILE, 'w', encoding='utf-8') as f:
            f.write(llms_text)
        print("Updated llms.txt with Knowledge Base section.")

def main():
    print(f"Generating {len(ARTICLES)} blog articles...")

    # Write each article HTML
    for a in ARTICLES:
        filename = f"{a['slug']}.html"
        filepath = os.path.join(BLOG_DIR, filename)
        html = generate_article_page(a)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Generated: blog/{filename}")

    # Write blog/index.html
    index_html = generate_blog_index(ARTICLES)
    with open(os.path.join(BLOG_DIR, "index.html"), 'w', encoding='utf-8') as f:
        f.write(index_html)
    print("Generated: blog/index.html")

    # Write blog/posts.json
    posts_meta = [{
        "slug": a['slug'],
        "title": a['title'],
        "date": a['date'],
        "category": a['category'],
        "tags": a['tags'],
        "reading_time": a['reading_time'],
        "tldr": a['tldr']
    } for a in ARTICLES]
    with open(os.path.join(BLOG_DIR, "posts.json"), 'w', encoding='utf-8') as f:
        json.dump(posts_meta, f, indent=2)
    print("Generated: blog/posts.json")

    # Update sitemap
    update_sitemap(ARTICLES)

    # Update llms.txt
    update_llms(ARTICLES)

    print("All 25 initial blogs built and cataloged successfully!")

if __name__ == '__main__':
    main()
