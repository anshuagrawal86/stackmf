# StackMF Technologies LLP (stackmf.com)

> Enterprise Mainframe Modernization, Broadcom Product Replacement, Full-Stack Hybrid Cloud Engineering, and 24/7 Managed Application Maintenance (AMS).

---

## Repository Structure

```
├── .github/
│   ├── workflows/
│   │   └── deploy.yml                       # Production CI/CD Pipeline (Quality Gate + Hostinger Deploy)
│   └── CI_CD_GUIDE.md                       # Complete CI/CD & GitHub Actions Setup Instructions
├── index.html                               # Enterprise Website (Dark Obsidian Theme, Interactive Flows, TCO Calc)
├── llms.txt                                 # AI Search Engine Grounding (Perplexity, ChatGPT, Claude)
├── llms-full.txt                            # Deep Technical Entity & Migration Architecture Reference
├── robots.txt                               # Optimized Bot Directives & AI Crawler Permissions
├── sitemap.xml                              # Canonical XML Sitemap
├── DEPLOYMENT_AND_SEO_DOMINATION_GUIDE.md   # Google & Bing SEO Domination Protocol
└── .gitignore                               # Standard Git Ignore Rules
```

## Automated CI/CD Deployment

Every push to the `main` branch triggers the GitHub Actions pipeline:
1. **Schema & Asset Validation:** Verifies JSON-LD `@graph`, navigation anchors, and AI/SEO assets.
2. **Production Sync:** Deploys changed files to Hostinger `public_html/` via secure FTPS.
3. **Staging Preview:** Automatically generates a GitHub Pages staging preview.

For setup details, see [`.github/CI_CD_GUIDE.md`](.github/CI_CD_GUIDE.md).
