#!/usr/bin/env python3
"""Mechanical checks on out/: links, unique titles, sitemap, ads, and safety."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
POPUNDER = "https://abscloud.org/1/b640baabccdb568dd796990946539530"
SOCIAL = "https://bauval.org/14/0eba5089f9eb509606a14e9eebb4e230"
DMCA = "github.com/github/dmca"
errors = []
titles, descs, h1s = {}, {}, {}


def public_path(rel):
    parts = list(rel.parts)
    if parts[-1] == "index.html":
        parts = parts[:-1]
    elif parts[-1].endswith(".html"):
        parts[-1] = parts[-1][:-5]
    return "/" + "/".join(parts) if parts else "/"


def lang_of(rel):
    if rel.parts and rel.parts[0] in ("zh", "es", "pt-br"):
        return rel.parts[0]
    return "en"


def no_ads(rel):
    if rel.name == "404.html":
        return True
    if rel.name in ("privacy.html", "terms.html"):
        return True
    return bool(rel.parts) and rel.parts[0] == "play"


def resolve(p):
    p = p.split("#")[0].split("?")[0]
    if p in ("/", ""):
        return (OUT / "index.html").exists()
    q = OUT / p.lstrip("/")
    return q.is_file() or q.with_suffix(".html").is_file() or (q / "index.html").is_file()


def forbidden_href(url):
    u = url.lower()
    if any(tok in u for tok in ("discord.gg", "discord.com/invite", "magnet:", ".torrent", "gitlab.com")):
        return "forbidden link"
    if re.search(r"\.exe($|\?|#)", u):
        return "executable link"
    if "github.com/" in u and DMCA not in u:
        return "github link"
    return ""


ads = json.loads((ROOT / "data" / "ads.json").read_text(encoding="utf-8"))
cfg = ads.get("config") or {}
if ads.get("enabled") is not True:
    errors.append("ads.json: enabled must stay true")
if ads.get("runtime") != "/adsterra/runtime.js":
    errors.append("ads.json: runtime must stay /adsterra/runtime.js")
if ads.get("no_ads_pages") != ["privacy", "terms"]:
    errors.append("ads.json: no_ads_pages must stay privacy and terms")
if cfg.get("slots") != [] or cfg.get("enablePopunder") is not True or cfg.get("enableSocialBar") is not True:
    errors.append("ads.json: keep Popunder + Social Bar only, slots empty")
if cfg.get("popunderScriptUrl") != POPUNDER or cfg.get("socialBarScriptUrl") != SOCIAL:
    errors.append("ads.json: ad script URLs changed")
if cfg.get("cleanPage") is not False:
    errors.append("ads.json: cleanPage must stay false")

if not (OUT / "adsterra" / "runtime.js").is_file():
    errors.append("missing out/adsterra/runtime.js")
if not (OUT / "play" / "index.html").is_file():
    errors.append("missing out/play/index.html")
if not (OUT / "og-image.png").is_file():
    errors.append("missing out/og-image.png")
vercel = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
rewrites = json.dumps(vercel.get("rewrites", []))
if "index.html" in rewrites and "(.*)" in rewrites:
    errors.append("vercel.json: SPA catch-all rewrite is not allowed")

for f in sorted(OUT.rglob("*")):
    if not f.is_file() or f.suffix.lower() not in {".html", ".css", ".js", ".xml", ".txt"}:
        continue
    low = f.read_text(encoding="utf-8", errors="replace").lower()
    rel = f.relative_to(OUT)
    if "4lwayz" in low:
        errors.append(f"{rel}: forbidden name '4lwayz'")

for f in sorted(OUT.rglob("*.html")):
    s = f.read_text(encoding="utf-8")
    rel = f.relative_to(OUT)
    for attr in re.findall(r'(?:href|src)="([^"]+)"', s, flags=re.I):
        if attr.startswith("/") and not attr.startswith("//") and not resolve(attr):
            errors.append(f"{rel}: broken link {attr}")
        why = forbidden_href(attr)
        if why:
            errors.append(f"{rel}: {why} {attr}")
    for card in re.findall(r'class="pcard.*?</article>', s, flags=re.S):
        for attr in re.findall(r'href="([^"]+)"', card, flags=re.I):
            why = forbidden_href(attr)
            if why:
                errors.append(f"{rel}: project card {why} {attr}")
    blocked = no_ads(rel)
    has_cfg = 'id="adsterra-config"' in s
    has_runtime = "/adsterra/runtime.js" in s
    has_nets = POPUNDER in s and SOCIAL in s
    if blocked and (has_cfg or has_runtime or "abscloud.org" in s or "bauval.org" in s):
        errors.append(f"{rel}: ads present on a no-ad page")
    if not blocked and not (has_cfg and has_runtime and has_nets):
        errors.append(f"{rel}: missing ad config")
    if has_cfg:
        raw = re.search(r'id="adsterra-config">(.*?)</script>', s, flags=re.S)
        try:
            page_cfg = json.loads(raw.group(1)) if raw else {}
        except json.JSONDecodeError:
            page_cfg = {}
            errors.append(f"{rel}: adsterra-config is not JSON")
        if page_cfg.get("popunderScriptUrl") != POPUNDER or page_cfg.get("socialBarScriptUrl") != SOCIAL:
            errors.append(f"{rel}: ad script URL mismatch")
        if page_cfg.get("slots") not in ([], None):
            errors.append(f"{rel}: unexpected ad slots")
        allowed = page_cfg.get("allowedPaths") or []
        own = public_path(rel)
        if own not in allowed:
            errors.append(f"{rel}: {own} missing from allowedPaths")
        for path in allowed:
            norm = path.rstrip("/") or "/"
            parts = [p for p in norm.split("/") if p]
            if parts and parts[-1] in ("privacy", "terms", "play") or norm == "/play":
                errors.append(f"{rel}: allowedPaths includes a no-ad path {path}")
                break
    if rel.name == "404.html" or (rel.parts and rel.parts[0] == "play"):
        continue
    title_m = re.search(r"<title>(.*?)</title>", s)
    desc_m = re.search(r'name="description" content="(.*?)"', s)
    h1_m = re.search(r"<h1>(.*?)</h1>", s, re.S)
    if not (title_m and desc_m and h1_m):
        errors.append(f"{rel}: missing title, description, or h1")
        continue
    lang = lang_of(rel)
    t = title_m.group(1)
    d = desc_m.group(1)
    h = re.sub("<[^>]+>", "", h1_m.group(1))
    for store, v, kind in ((titles, t, "title"), (descs, d, "description"), (h1s, h, "h1")):
        key = (lang, v)
        if key in store:
            errors.append(f"{rel}: duplicate {kind} {v!r} (also {store[key]})")
        store[key] = rel
    visible = re.sub(r"<script.*?</script>", "", s, flags=re.S)
    for bad in ("lorem", "TODO", "TBD", "{{", "}}"):
        if bad in visible:
            errors.append(f"{rel}: placeholder text {bad!r}")

home = (OUT / "index.html").read_text(encoding="utf-8")
zh = (OUT / "zh" / "index.html").read_text(encoding="utf-8")
if 'class="no">Not officially.</span>' not in home:
    errors.append("home: official answer must stay 'Not officially.'")
if "官方还没有。" not in zh:
    errors.append("zh home: missing 官方还没有。")
if "Mostly." in home or "Mostly." in zh:
    errors.append("home uses Mostly.")
tracker = (OUT / "pc-port-tracker.html").read_text(encoding="utf-8")
if "hero-card" not in home or 'class="pcard' not in tracker:
    errors.append("home or tracker: missing progress / project cards")
if 'data-f="all"' not in tracker:
    errors.append("tracker: missing filters")
css = (ROOT / "static" / "site.css").read_text(encoding="utf-8")
if ".pcard[hidden]" not in css or "display: none" not in css.split(".pcard[hidden]", 1)[-1][:80]:
    errors.append("site.css: .pcard[hidden] must be display:none or the tracker filter stays visible")
if 'class="src"' not in (OUT / "news.html").read_text(encoding="utf-8"):
    errors.append("news: missing sources")

for name in ("projects.json", "news.json", "trend.json", "status.json"):
    blob = (ROOT / "data" / name).read_text(encoding="utf-8")
    for url in re.findall(r"https?://[^\"\s]+", blob):
        why = forbidden_href(url)
        if why:
            errors.append(f"data/{name}: {why} {url}")

sm = (OUT / "sitemap.xml").read_text(encoding="utf-8")
locs = re.findall(r"<loc>https://gta6pc.org(.*?)</loc>", sm)
locset = set(locs)
for loc in locs:
    if not resolve(loc):
        errors.append(f"sitemap: {loc} has no page")
    block = sm.split(f"<loc>https://gta6pc.org{loc}</loc>", 1)[-1].split("</url>", 1)[0]
    for code in ("en", "zh-CN", "es", "pt-BR"):
        if f'hreflang="{code}"' not in block:
            errors.append(f"sitemap {loc}: missing hreflang {code}")
indexed = []
for f in OUT.rglob("*.html"):
    rel = f.relative_to(OUT)
    if rel.name == "404.html" or (rel.parts and rel.parts[0] == "play"):
        continue
    indexed.append(public_path(rel))
for path in indexed:
    if path not in locset:
        errors.append(f"sitemap: missing {path}")
for loc in locs:
    if loc not in indexed:
        errors.append(f"sitemap: extra {loc}")

pages = len(list(OUT.rglob("*.html")))
print(f"{pages} pages, {len(locs)} sitemap urls")
print("\n".join(errors) if errors else "all checks passed")
sys.exit(1 if errors else 0)
