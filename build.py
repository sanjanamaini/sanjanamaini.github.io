#!/usr/bin/env python3
"""Static site generator for sanjanamaini.github.io (standard library only).

    python3 build.py              build all pages, checking every number against the repos
    python3 build.py --cards      also render the 1200x630 link-preview cards (needs Google Chrome)
    python3 build.py --no-verify  build without the repo checks (only when the repos are not alongside)

Content lives in content/site.json and content/projects/*.json; pages are written to the repo root.
Inline markup in content text: [[12.3%]] renders as a mono number. Everything else is escaped.
"""
import json, os, re, sys, shutil, subprocess, datetime, html
ROOT = os.path.dirname(os.path.abspath(__file__))
GH = os.path.dirname(ROOT)            # sibling project repos live next to this one
SITE = json.load(open(os.path.join(ROOT, "content/site.json"), encoding="utf8"))
BASE = SITE["base_url"].rstrip("/")
TODAY = datetime.date.today().isoformat()
VERIFY = "--no-verify" not in sys.argv

def esc(s): return html.escape(s, quote=True)
def rich(s):
    s = esc(s)
    return re.sub(r"\[\[(.+?)\]\]", r'<span class="num">\1</span>', s)
def plain(s): return re.sub(r"\[\[(.+?)\]\]", r"\1", s)

# ---------- verification: every number on a page is tied to a repo file ----------
def dig(o, path):
    for k in path.split("/"):
        o = o[int(k)] if isinstance(o, list) else o[k]
    return o
def check_all(slug, checks):
    bad = []
    for c in checks:
        fp = os.path.join(GH, c["file"])
        if not os.path.exists(fp):
            bad.append(f'{slug}: missing {c["file"]}'); continue
        if "contains" in c:
            if c["contains"] not in open(fp, encoding="utf8").read():
                bad.append(f'{slug}: {c["file"]} no longer contains {c["contains"]!r}')
            continue
        v = dig(json.load(open(fp, encoding="utf8")), c["path"])
        if abs(v - c["expect"]) > c.get("tol", 1e-9):
            bad.append(f'{slug}: {c["file"]}:{c["path"]} is {v}, page says {c["expect"]}')
    return bad

# ---------- shared page pieces ----------
def head(title, desc, path, og_image=None, article=False):
    url = f"{BASE}{path}"
    img = f"{BASE}/{og_image}" if og_image else f"{BASE}/og/home.png"
    ga = ""
    if SITE.get("ga_measurement_id"):
        g = SITE["ga_measurement_id"]
        ga = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={g}"></script>\n'
              f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}'
              f'gtag("js",new Date());gtag("config","{g}");</script>\n')
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{'article' if article else 'website'}">
<meta property="og:site_name" content="Sanjana Maini">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#FAF8F4">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%230E6B60'/%3E%3Ctext x='16' y='22' font-family='Georgia,serif' font-size='18' font-weight='700' text-anchor='middle' fill='white'%3ESM%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{'/' if path=='/404.html' else ('../' if path.count('/')>1 else '')}assets/style.css">
{ga}</head>
<body>
"""
def rel(path): return "/" if path == "/404.html" else ("../" if path.count("/") > 1 else "")
def header(path):
    r = rel(path)
    return f"""<header class="site"><div class="wide">
  <a class="mark" href="{r or './'}">Sanjana Maini</a>
  <nav aria-label="Main"><a href="{r}#projects">Projects</a><a href="{r}#about">About</a><a href="{r}#contact">Contact</a><button class="theme" type="button" id="t" aria-label="Switch light or dark mode">Light / dark</button></nav>
</div></header>
"""
def footer(path):
    r = rel(path)
    s = SITE
    return f"""<footer class="site"><div class="wrap">
  <a href="mailto:{s['email']}" data-track="email">{s['email']}</a> &middot;
  <a href="{s['linkedin']}" data-track="linkedin" rel="me">LinkedIn</a> &middot;
  <a href="{r or './'}">All projects</a>
</div></footer>
<script src="{r}assets/site.js" defer></script>
</body></html>
"""

# ---------- project page ----------
PIPELINE_SVG = """<svg viewBox="0 0 760 250" role="img" aria-labelledby="pt pd" class="diagram">
<title id="pt">The Pilot agent loop</title>
<desc id="pd">A goal and a screenshot go to a screen interpreter, then a planner, then an action agent that acts in the browser; a verifier checks a fresh screenshot and either sends the run back to the planner or on to the narrator.</desc>
<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="var(--muted)"/></marker></defs>
<g font-family="var(--sans)" font-size="14" fill="var(--ink)">
<g stroke="var(--rule)" fill="var(--surface)" stroke-width="1.2">
<rect x="10" y="40" width="130" height="56" rx="6"/><rect x="170" y="40" width="130" height="56" rx="6"/>
<rect x="330" y="40" width="130" height="56" rx="6"/><rect x="490" y="40" width="120" height="56" rx="6"/>
<rect x="630" y="40" width="120" height="56" rx="6"/></g>
<g text-anchor="middle"><text x="75" y="64">Screen</text><text x="75" y="82">interpreter</text>
<text x="235" y="73">Planner</text><text x="395" y="64">Action</text><text x="395" y="82">agent</text>
<text x="550" y="73">Verifier</text><text x="690" y="73">Narrator</text></g>
<g stroke="var(--muted)" stroke-width="1.5" fill="none" marker-end="url(#ar)">
<path d="M140 68H168"/><path d="M300 68H328"/><path d="M460 68H488"/><path d="M610 68H628"/></g>
<path d="M550 98V170H235V100" stroke="var(--accent)" stroke-width="1.5" fill="none" marker-end="url(#ar)" stroke-dasharray="5 4"/>
<text x="392" y="190" text-anchor="middle" fill="var(--accent)" font-size="13">failed check: replan (capped at 3 per goal)</text>
<text x="75" y="130" text-anchor="middle" fill="var(--muted)" font-size="12">screenshot in</text>
<text x="395" y="130" text-anchor="middle" fill="var(--muted)" font-size="12">click, type, scroll</text>
<text x="550" y="130" text-anchor="middle" fill="var(--muted)" font-size="12">fresh screenshot</text>
<text x="10" y="232" fill="var(--muted)" font-size="12">Goal in plain English, in a Chrome side panel. Gemini vision reads every screenshot.</text>
</g></svg>"""

def project_page(p):
    slug = p["slug"]; path = f"/{slug}/"
    r = "../"
    out = [head(f'{plain(p["title"])} | Sanjana Maini', plain(p["description"]), path, f'og/{slug}.png', True), header(path)]
    out.append('<main class="wrap">\n')
    out.append(f'  <p class="crumb"><a href="../#projects">Projects</a> / {esc(p["crumb"])}</p>\n')
    out.append(f'  <span class="status">{esc(p["status"])} &middot; numbers checked {TODAY}</span>\n')
    out.append(f'  <h1>{rich(p["title"])}</h1>\n  <p class="standfirst">{rich(p["standfirst"])}</p>\n')
    out.append('  <dl class="facts">\n' + "".join(f'    <div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>\n' for k, v in p["facts"]) + '  </dl>\n')
    n = 0
    def h2(t):
        nonlocal n; n += 1
        return f'  <h2><span class="n">{n:02d}</span>{esc(t)}</h2>\n'
    for s in p["sections"]:
        out.append(h2(s["h"]))
        out.extend(f'  <p>{rich(t)}</p>\n' for t in s["p"])
        if s.get("figure"): out.append(figure(p, s["figure"], r))
    out.append(h2("What this does not show"))
    out.append('  <div class="limits"><ul>\n' + "".join(f'    <li>{rich(t)}</li>\n' for t in p["limits"]) + '  </ul></div>\n')
    if p.get("changes"):
        out.append(h2(p["changes"]["h"]))
        out.extend(f'  <p>{rich(t)}</p>\n' for t in p["changes"]["p"])
    out.append(h2("Reproduce it"))
    out.append(f'  <pre>{esc(p["reproduce"])}</pre>\n')
    repo = p["repo"]
    out.append(f'  <p class="note">Source and code: <a href="https://github.com/sanjanamaini/{repo}?utm_source=site&amp;utm_medium=project_page&amp;utm_campaign={slug}" data-track="repo" data-project="{slug}">repository</a>. {esc(p["credit"])}</p>\n')
    out.append("</main>\n")
    out.append(footer(path))
    return "".join(out)

def figure(p, f, r):
    if f.get("svg") == "pipeline":
        body = f'<div class="plate diagram-plate">{PIPELINE_SVG}</div>'
    else:
        body = f'<div class="plate"><img src="{r}assets/fig/{f["file"]}" width="{f["w"]}" height="{f["h"]}" alt="{esc(f["alt"])}"></div>'
    return f'  <figure>\n    {body}\n    <figcaption><strong>Figure.</strong> {rich(f["caption"])}</figcaption>\n  </figure>\n'

# ---------- home page ----------
def home_page():
    s = SITE; path = "/"
    out = [head("Sanjana Maini | Data analyst: findings, with the limits stated", s["description"], path, "og/home.png"), header(path)]
    out.append('<main class="wrap">\n')
    out.append(f'  <h1 class="home">{rich(s["hero_title"])}</h1>\n  <p class="standfirst">{rich(s["hero_text"])}</p>\n')
    out.append('  <h2 id="projects"><span class="n">01</span>Projects, as findings</h2>\n')
    out.append('  <table class="hub">\n    <tr><th>Finding</th><th>Status</th><th>Stack</th></tr>\n')
    for p in PROJECTS:
        out.append(f'    <tr><td><a href="{p["slug"]}/" data-track="project" data-project="{p["slug"]}">{rich(p["hub"])}</a></td><td>{esc(p["status"])}</td><td>{esc(p["stack"])}</td></tr>\n')
    out.append('  </table>\n')
    out.append('  <h2 id="about"><span class="n">02</span>About</h2>\n')
    out.extend(f'  <p>{rich(t)}</p>\n' for t in s["about"])
    out.append('  <h2><span class="n">03</span>Experience</h2>\n  <dl class="rows">\n')
    for e in s["experience"]:
        out.append(f'    <div><dt>{esc(e["org"])}<span>{esc(e["when"])}</span></dt><dd><em>{esc(e["role"])}.</em> {rich(e["text"])}</dd></div>\n')
    out.append('  </dl>\n')
    out.append('  <h2><span class="n">04</span>Education and skills</h2>\n')
    out.append(f'  <p>{rich(s["education"])}</p>\n  <dl class="rows">\n')
    for k, v in s["skills"]:
        out.append(f'    <div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>\n')
    out.append('  </dl>\n')
    out.append(f'  <p class="note">{esc(s["certifications"])}</p>\n')
    out.append('  <h2 id="contact"><span class="n">05</span>Contact</h2>\n')
    out.append(f'  <p>{rich(s["contact_text"])}</p>\n')
    out.append(f'  <p><a href="mailto:{s["email"]}" data-track="email">{s["email"]}</a> &middot; <a href="{s["linkedin"]}" data-track="linkedin" rel="me">LinkedIn</a> &middot; <a href="{s["github"]}" data-track="github" rel="me">GitHub</a></p>\n')
    out.append('</main>\n')
    out.append(footer(path))
    return "".join(out)

# ---------- tagged-link generator ----------
def links_page():
    path = "/links/"
    out = [head("Tagged links | Sanjana Maini", "Link generator for the job search.", path), header(path)]
    out[0] = out[0].replace('<meta name="theme-color"', '<meta name="robots" content="noindex">\n<meta name="theme-color"')
    slugs = json.dumps([{"slug": p["slug"], "name": plain(p["crumb"])} for p in PROJECTS])
    out.append(f"""<main class="wrap">
  <p class="crumb">Job-search tools</p>
  <h1>Tagged links</h1>
  <p class="standfirst">Pick a page and where the link will live. Copy the link. The tags show up in Google Analytics as source, medium and campaign.</p>
  <form id="lg" class="lg" onsubmit="return false">
    <label>Page <select id="pg"></select></label>
    <label>Source <select id="src"><option>linkedin</option><option>resume</option><option>cover_letter</option><option>email</option><option>whatsapp</option><option>other</option></select></label>
    <label>Medium <select id="med"><option>post</option><option>profile</option><option>featured</option><option>message</option><option>pdf</option><option>application</option></select></label>
    <label>Campaign <input id="cmp" placeholder="project or company, e.g. Deloitte_Sales-Analytics"></label>
  </form>
  <pre id="out" aria-live="polite">{BASE}/</pre>
  <p class="note">This page needs JavaScript. Without it, build the link by hand: <code>{BASE}/layoff/?utm_source=linkedin&amp;utm_medium=post&amp;utm_campaign=layoff</code>. Use lowercase, no spaces; keep the campaign the same everywhere you use it.</p>
</main>
<script>var PAGES={slugs};</script>
<script src="../assets/links.js" defer></script>
""")
    out.append(footer(path))
    return "".join(out)

def write(path, text):
    full = os.path.join(ROOT, path.lstrip("/"))
    if full.endswith("/"): full = os.path.join(full, "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf8").write(text)

# ---------- main ----------
PROJECTS = []
for name in SITE["project_order"]:
    PROJECTS.append(json.load(open(os.path.join(ROOT, f"content/projects/{name}.json"), encoding="utf8")))
problems = []
if VERIFY:
    for p in PROJECTS: problems += check_all(p["slug"], p.get("checks", []))
if problems:
    print("BUILD STOPPED: numbers on a page no longer match the repo results:"); [print("  -", x) for x in problems]; sys.exit(1)
print(f"verified {sum(len(p.get('checks', [])) for p in PROJECTS)} checks" if VERIFY else "verification skipped")

for p in PROJECTS:
    for f in p.get("copy", []):
        src = os.path.join(GH, f["from"]); dst = os.path.join(ROOT, "assets/fig", f["to"])
        shutil.copyfile(src, dst)
    write(f'/{p["slug"]}/', project_page(p))
write("/", home_page())
write("/links/", links_page())
write("/404.html", head("Page not found | Sanjana Maini", "Page not found", "/404.html") + header("/404.html") +
      '<main class="wrap"><h1>That page is not here</h1><p class="standfirst"><a href="/">Back to the projects</a>.</p></main>' + footer("/404.html"))
pages = ["/"] + [f'/{p["slug"]}/' for p in PROJECTS]
write("/sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      "".join(f"  <url><loc>{BASE}{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in pages) + "</urlset>\n")
write("/robots.txt", f"User-agent: *\nAllow: /\nDisallow: /links/\nSitemap: {BASE}/sitemap.xml\n")
print("pages:", ", ".join(pages))

# ---------- link-preview cards (1200x630) ----------
def card_html(c):
    fig = f'<div class="thumb"><img src="file://{ROOT}/assets/fig/{c["image"]}"></div>' if c.get("image") else ""
    return f"""<!doctype html><meta charset=utf-8><style>
*{{box-sizing:border-box;margin:0}}body{{width:1200px;height:630px;background:#FAF8F4;color:#1A1D21;font-family:Georgia,'Times New Roman',serif;padding:64px 72px;display:flex;flex-direction:column;justify-content:space-between;border-left:14px solid #0E6B60}}
.e{{font:500 24px/1 Menlo,monospace;letter-spacing:.1em;text-transform:uppercase;color:#0E6B60}}
.m{{display:flex;gap:48px;align-items:flex-end;justify-content:space-between}}
.b{{font-weight:600;font-size:{c.get("size", 58)}px;line-height:1.14;letter-spacing:-.01em;max-width:{ "640px" if c.get("image") else "1000px"}}}
.thumb{{width:400px;background:#fff;border:2px solid #DAD6CD;border-radius:8px;padding:8px}}.thumb img{{display:block;width:100%}}
.f{{display:flex;justify-content:space-between;font:22px Menlo,monospace;color:#555D69}}</style>
<div class=e>{esc(c["eyebrow"])}</div><div class=m><div class=b>{esc(c["big"])}</div>{fig}</div><div class=f><span>{esc(c["left"])}</span><span>{esc(c["right"])}</span></div>"""
if "--cards" in sys.argv:
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cards = [dict(slug="home", **SITE["og"])] + [dict(slug=p["slug"], **p["og"]) for p in PROJECTS]
    tmp = os.path.join(ROOT, ".cards"); os.makedirs(tmp, exist_ok=True)
    for c in cards:
        hp = os.path.join(tmp, c["slug"] + ".html"); open(hp, "w", encoding="utf8").write(card_html(c))
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1200,630",
                        f"--screenshot={ROOT}/og/{c['slug']}.png", "file://" + hp], capture_output=True, timeout=60)
    shutil.rmtree(tmp); print("cards:", ", ".join(c["slug"] for c in cards))
