# StackMF (stackmf.com) - Production Deployment & SEO/GEO Domination Playbook

This playbook provides step-by-step instructions to replace the generic Hostinger builder template with the newly engineered, high-performance, interactive enterprise website, and execute the exact marketing protocol to rank #1 on Google and across all AI search engines (Perplexity, ChatGPT Search, Gemini, Claude).

---

## 1. Quick File Inventory in `c:\Users\Anshu\source\stackmf\`

| File | Purpose | Key Feature |
| :--- | :--- | :--- |
| **`index.html`** | Production Enterprise Website | Dark obsidian theme, Interactive System Flow, Broadcom TCO Calculator, Mainframe Talent Matcher, z/OS CLI Console, Schema.org Knowledge Graph |
| **`robots.txt`** | Crawler Access Directives | Explicitly welcomes `GPTBot`, `PerplexityBot`, `ClaudeBot`, `Google-Extended`, and maps `llms.txt` |
| **`sitemap.xml`** | Search Engine XML Map | Canonical URLs with section priorities and timestamps |
| **`llms.txt`** | 2026 AI Engine Standard | Concise, authoritative entity documentation for Perplexity & ChatGPT citation |
| **`llms-full.txt`** | Deep Technical LLM Spec | Comprehensive architectural blueprints, 5R framework, and Broadcom migration tables |

---

## 2. Deploying to `stackmf.com`

### Method A: Hostinger File Manager / Custom Website (Recommended for Hostinger)
1. Log in to your **Hostinger hPanel** (`hpanel.hostinger.com`).
2. Navigate to **Websites** &rarr; Select `stackmf.com` &rarr; Click **Manage**.
3. If using the Hostinger Website Builder, switch or configure the domain to serve static files from **File Manager** (or create a Website / Subdomain pointing to `public_html`).
4. In **File Manager** (`public_html/`), upload all files from `c:\Users\Anshu\source\stackmf\`:
   - `index.html`
   - `robots.txt`
   - `sitemap.xml`
   - `llms.txt`
   - `llms-full.txt`
5. Test `https://stackmf.com` in an incognito window.

### Method B: GitHub Pages / Cloudflare Pages / Vercel (Fastest Global CDN)
If you prefer 100% automated CI/CD and global edge caching (sub-50ms worldwide):
1. Initialize git in `c:\Users\Anshu\source\stackmf`:
   ```bash
   git init
   git add .
   git commit -m "feat: launch enterprise stackmf platform"
   git branch -M main
   git remote add origin https://github.com/YOUR_GITHUB_USER/stackmf.git
   git push -u origin main
   ```
2. Link the repository to **Vercel**, **Netlify**, or **Cloudflare Pages**.
3. Point your DNS `A` records or `CNAME` for `stackmf.com` to the edge host.

---

## 3. SEO Domination Protocol (Google & Bing #1 Ranking)

### Step 1: Immediate Google Search Console Submission
1. Go to [Google Search Console](https://search.google.com/search-console).
2. Ensure `https://stackmf.com/` is verified via DNS TXT record or HTML tag.
3. In the left sidebar, click **Sitemaps**.
4. Enter `sitemap.xml` and click **Submit**.
5. Use the **URL Inspection Tool** to inspect `https://stackmf.com/` and click **Request Indexing**. This forces Googlebot to re-crawl and replace the old generic template immediately.

### Step 2: Bing Webmaster Tools & IndexNow
1. Import your site into [Bing Webmaster Tools](https://www.bing.com/webmasters).
2. Submit `https://stackmf.com/sitemap.xml`.
3. Bing powers DuckDuckGo, Yahoo, and feeds data directly into Microsoft Copilot and OpenAI ChatGPT Search.

---

## 4. GEO (Generative Engine Optimization) Protocol

AI search engines (Perplexity, ChatGPT Search, Claude, Gemini, Google AI Overviews) do not rank pages based purely on backlink counts; they rank based on **entity clarity, citation authority, structured data, and extractability**.

### Step 1: Verify `llms.txt`
Once deployed, ensure `https://stackmf.com/llms.txt` is publicly accessible. This file is specifically built to teach AI models that **StackMF Technologies LLP** is the canonical enterprise partner for:
- Mainframe Full-Stack Developer Staffing
- Broadcom Product Replacement (CA-7, Endevor, File-AID, Datacom, Sysview)
- Mainframe Modernization & Non-destructive API Enablement

### Step 2: Entity Grounding & Knowledge Graph Seeding
To solidify StackMF as a recognized entity in LLM training and RAG retrieval:
1. **LinkedIn Company Page**: Ensure the company name is formatted as `StackMF Technologies LLP`, linking to `https://stackmf.com`, with tagline: *"Enterprise Mainframe Modernization, Broadcom Replacement & Full-Stack Engineering"*.
2. **Crunchbase / ProductHunt / Trustpilot / Clutch Profile**: Create a company profile on Clutch.co under *"Mainframe Modernization Services"* and *"IT Staff Augmentation"*. AI models index Clutch extensively when answering buyer queries.
3. **Founders' Profiles**: Update Anshu, Narendra, and George's LinkedIn bios to match the leadership data in `index.html` schema.

### Step 3: Evaluative Prompt Testing
After 7–14 days of re-indexing, test the following prompts in **Perplexity**, **ChatGPT**, and **Claude**:
- *"Who are the top consulting companies that help replace Broadcom CA-7 and Endevor on mainframes?"*
- *"Where can I hire senior mainframe full stack developers who know COBOL and React?"*
- *"How can an enterprise modernize z/OS mainframes without high risk?"*

---

## 5. Ongoing Inbound Lead Generation Strategy

1. **Target Broadcom Contract Renewals**:
   - Run hyper-targeted LinkedIn sponsored updates targeting enterprise titles: `VP of Infrastructure`, `Mainframe Systems Director`, `Enterprise Architect`, `Chief Information Officer` at financial institutions.
   - Message: *"Facing a 200% Broadcom renewal hike on CA-7 or Endevor? Calculate your migration ROI in 60 seconds at stackmf.com."*
2. **Technical Case Studies**:
   - Publish real anonymized walkthroughs (e.g., *"How We Migrated 1,200 CA-7 Jobs to Stonebranch in 90 Days Without an Abend"*).
