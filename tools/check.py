#!/usr/bin/env python3
"""Mechanical checks on out/: internal links resolve (Vercel cleanUrls rules), unique title/description/h1, sitemap matches pages."""
import re, sys
from pathlib import Path
OUT = Path(__file__).resolve().parent.parent / "out"
ALLOW_EXTERNAL_PATHS = set()  # /play/ and /og-image.png are copied from legacy/ into out/
errors, titles, descs, h1s = [], {}, {}, {}

def resolve(p):
    p = p.split("#")[0].split("?")[0]
    if p in ALLOW_EXTERNAL_PATHS: return True
    if p in ("/", ""): return (OUT / "index.html").exists()
    q = OUT / p.lstrip("/")
    return q.is_file() or q.with_suffix(".html").is_file() or (q / "index.html").is_file()

for f in sorted(OUT.rglob("*.html")):
    s = f.read_text(encoding="utf-8")
    rel = f.relative_to(OUT)
    for attr in re.findall(r'(?:href|src)="([^"]+)"', s):
        if attr.startswith("/") and not attr.startswith("//") and not resolve(attr):
            errors.append(f"{rel}: broken link {attr}")
    if "404" in f.name or rel.parts[0] == "play": continue  # legacy page is not built here
    t = re.search(r"<title>(.*?)</title>", s).group(1); d = re.search(r'name="description" content="(.*?)"', s).group(1); h = re.sub("<[^>]+>", "", re.search(r"<h1>(.*?)</h1>", s, re.S).group(1))
    for store, v in ((titles, t), (descs, d), (h1s, h)):
        if v in store: errors.append(f"{rel}: duplicate {v!r} (also {store[v]})")
        store[v] = rel
    for bad in ("lorem", "TODO", "TBD", "{{", "}}"):
        if bad in re.sub(r"<script.*?</script>", "", s, flags=re.S): errors.append(f"{rel}: placeholder text {bad!r}")
sm = (OUT / "sitemap.xml").read_text()
locs = re.findall(r"<loc>https://gta6pc.org(.*?)</loc>", sm)
for l in locs:
    if not resolve(l): errors.append(f"sitemap: {l} has no page")
print(f"{len(list(OUT.rglob('*.html')))} pages, {len(locs)} sitemap urls")
print("\n".join(errors) if errors else "all checks passed")
sys.exit(1 if errors else 0)
