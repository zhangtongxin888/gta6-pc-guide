# gta6pc.org

Static, bilingual (English / Chinese) fan site answering "Is GTA 6 on PC?": release date, unofficial port tracker, EXE leak explainer, specs, Remote Play guide, fake-download check, Steam, news.

```bash
python3 build.py            # production build -> out/   (Vercel serves this)
python3 build.py preview    # flat preview -> preview/
python3 tools/check.py      # link / duplicate / sitemap checks on out/
```

No dependencies beyond the Python standard library (3.8+).

- Daily data: `data/status.json`, `data/projects.json`, `data/news.json`
- Ads: `data/ads.json` (Adsterra Popunder + Social Bar; never on privacy, terms or 404)
- Page copy: `build.py`, as `t("English", "中文")` pairs
- Old-site files kept as-is: `legacy/` (Neon Bay `/play/`, `og-image.png`, ad runtime)

Deployment and daily-update steps are in `HANDOFF.md`.
