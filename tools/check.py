#!/usr/bin/env python3
"""Mechanical checks on out/: links, unique titles, sitemap, ads, and safety."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
ALLOW_EXTERNAL_PATHS = set()  # /play/ and /og-image.png are copied from legacy/ into out/
NO_ADS = {"privacy.html", "terms.html", "zh/privacy.html", "zh/terms.html", "404.html", "zh/404.html"}
errors, titles, descs, h1s = [], {}, {}, {}

def resolve(p):
    p = p.split("#")[0].split("?")[0]
    if p in ALLOW_EXTERNAL_PATHS: return True
    if p in ("/", ""): return (OUT / "index.html").exists()
    q = OUT / p.lstrip("/")
    return q.is_file() or q.with_suffix(".html").is_file() or (q / "index.html").is_file()

for f in sorted(OUT.rglob("*")):
    if not f.is_file() or f.suffix.lower() not in {".html", ".css", ".js", ".xml", ".txt"}: continue
    low = f.read_text(encoding="utf-8", errors="replace").lower()
    rel = f.relative_to(OUT)
    for bad in ("portwatch", "4lwayz"):
        if bad in low: errors.append(f"{rel}: forbidden name {bad!r}")

for f in sorted(OUT.rglob("*.html")):
    s = f.read_text(encoding="utf-8")
    rel = f.relative_to(OUT)
    rel_key = rel.as_posix()
    for attr in re.findall(r'(?:href|src)="([^"]+)"', s, flags=re.I):
        if attr.startswith("/") and not attr.startswith("//") and not resolve(attr):
            errors.append(f"{rel}: broken link {attr}")
        u = attr.lower()
        if any(tok in u for tok in ("discord.gg", "discord.com/invite", "magnet:", ".torrent", "gitlab.com")):
            errors.append(f"{rel}: forbidden link {attr}")
        if re.search(r"\.exe($|\?|#)", u):
            errors.append(f"{rel}: executable link {attr}")
        if "github.com/" in u and "github.com/github/dmca" not in u:
            errors.append(f"{rel}: github link {attr}")
    for card in re.findall(r'class="race-card".*?</article>', s, flags=re.S):
        cl = card.lower()
        if "github.com" in cl or "discord.gg" in cl or "magnet:" in cl:
            errors.append(f"{rel}: race card contains a forbidden link")
    no_ads = rel_key in NO_ADS or rel_key.startswith("play/")
    has_cfg = 'id="adsterra-config"' in s
    if no_ads and (has_cfg or "abscloud.org" in s or "bauval.org" in s):
        errors.append(f"{rel}: ads present on a no-ad page")
    if not no_ads and (not has_cfg or "abscloud.org" not in s or "bauval.org" not in s or "/adsterra/runtime.js" not in s):
        errors.append(f"{rel}: missing ad config")
    if "404" in f.name or (rel.parts and rel.parts[0] == "play"): continue
    t = re.search(r"<title>(.*?)</title>", s).group(1); d = re.search(r'name="description" content="(.*?)"', s).group(1); h = re.sub("<[^>]+>", "", re.search(r"<h1>(.*?)</h1>", s, re.S).group(1))
    for store, v in ((titles, t), (descs, d), (h1s, h)):
        if v in store: errors.append(f"{rel}: duplicate {v!r} (also {store[v]})")
        store[v] = rel
    for bad in ("lorem", "TODO", "TBD", "{{", "}}"):
        if bad in re.sub(r"<script.*?</script>", "", s, flags=re.S): errors.append(f"{rel}: placeholder text {bad!r}")

home = (OUT / "index.html").read_text(encoding="utf-8")
zh = (OUT / "zh" / "index.html").read_text(encoding="utf-8")
if "Not yet." not in home: errors.append("home: missing Not yet.")
if "还没有。" not in zh: errors.append("zh home: missing 还没有。")
if "Mostly." in home or "Mostly." in zh: errors.append("home uses Mostly.")
for name, text in (("home", home), ("zh", zh)):
    if 'class="overall"' not in text: errors.append(f"{name}: missing overall progress")
    if 'class="race-card' not in text: errors.append(f"{name}: missing race cards")
    if 'class="ncard' not in text and 'class="nmini' not in text: errors.append(f"{name}: missing news cards")
tracker = (OUT / "pc-port-tracker.html").read_text(encoding="utf-8")
if 'data-race' not in tracker or 'data-filter="all"' not in tracker: errors.append("tracker: missing race filters")
if "How we score progress" not in tracker: errors.append("tracker: missing methodology")
news = (OUT / "news.html").read_text(encoding="utf-8")
if 'class="srcs"' not in news: errors.append("news: missing sources")

banned = {"repo", "url", "github", "gitlab", "discord", "download", "magnet", "torrent"}
for p in json.loads((ROOT / "data" / "projects.json").read_text(encoding="utf-8")):
    for k in p:
        if k.lower() in banned: errors.append(f"projects.json {p.get('name')}: forbidden field {k}")

sm = (OUT / "sitemap.xml").read_text()
locs = re.findall(r"<loc>https://gta6pc.org(.*?)</loc>", sm)
for l in locs:
    if not resolve(l): errors.append(f"sitemap: {l} has no page")
if len(locs) != 22: errors.append(f"sitemap: expected 22 urls, found {len(locs)}")
print(f"{len(list(OUT.rglob('*.html')))} pages, {len(locs)} sitemap urls")
print("\n".join(errors) if errors else "all checks passed")
sys.exit(1 if errors else 0)
