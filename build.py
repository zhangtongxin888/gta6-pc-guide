#!/usr/bin/env python3
"""Static site generator for gta6pc.org (English + Chinese).

    python3 build.py            # production build -> out/   (deploy this on Vercel)
    python3 build.py preview    # flat preview     -> preview/ (relative links, used for review)

Content lives in two places:
  * data/*.json  - things that change daily (status board, port projects, news)
  * this file    - page copy, written as t("English", "中文") pairs so both languages stay in sync
"""
import json
import shutil
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
SITE = "https://gta6pc.org"
STATUS = json.loads((DATA / "status.json").read_text(encoding="utf-8"))
PROJECTS = json.loads((DATA / "projects.json").read_text(encoding="utf-8"))
ADS = json.loads((DATA / "ads.json").read_text(encoding="utf-8"))
TREND = json.loads((DATA / "trend.json").read_text(encoding="utf-8"))
NEWS = sorted(json.loads((DATA / "news.json").read_text(encoding="utf-8")), key=lambda n: n["date"], reverse=True)

# key -> slug ('' = home). Slugs for release-date and pc-specs match the old site’s URLs.
PAGES = {
    "home": "", "release": "release-date", "specs": "pc-specs", "tracker": "pc-port-tracker",
    "leak": "cyberleek-leak", "play": "how-to-play-gta-6-on-pc", "safe": "is-gta-6-pc-download-safe",
    "steam": "steam", "news": "news", "privacy": "privacy", "terms": "terms",
    "faq": "faq", "fps": "gta-6-fps", "online": "gta-6-online-pc",
}
IMG = {  # file: (width, height)
    "hero-vice-city-night.jpg": (1920, 1080), "beach-car.jpg": (1280, 720), "heist.jpg": (1280, 512),
    "tail-lights.jpg": (1306, 522), "ocean-view-hotel.jpg": (1280, 720), "cover-art.jpg": (1000, 562),
    "neon-club.jpg": (1600, 640), "key-art.jpg": (1600, 900),
    "sunset-art.jpg": (1600, 821), "collage.jpg": (1600, 900), "pool.jpg": (1600, 640),
}
MONTHS_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
# Languages. "en" and "zh" copy lives inline as t("English", "中文"); other languages are
# translated from the English text through i18n/<lang>.json (English string -> translation).
LANGS = {
    "en": {"prefix": "", "code": "en", "og": "en_US", "label": "EN", "name": "English",
           "months": MONTHS_EN},
    "zh": {"prefix": "zh", "code": "zh-CN", "og": "zh_CN", "label": "中文", "name": "中文"},
    "es": {"prefix": "es", "code": "es", "og": "es_ES", "label": "ES", "name": "Español",
           "months": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]},
    "pt": {"prefix": "pt-br", "code": "pt-BR", "og": "pt_BR", "label": "PT", "name": "Português",
           "months": ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]},
}
I18N = ROOT / "i18n"
TR = {l: (json.loads((I18N / f"{l}.json").read_text(encoding="utf-8")) if (I18N / f"{l}.json").exists() else {})
      for l in LANGS if l not in ("en", "zh")}
MISSING = {l: set() for l in TR}
Q = '"'


def cur_attr(on):
    return ' aria-current="page"' if on else ""


class Site:
    def __init__(self, mode, lang):
        self.mode, self.lang, self.zh = mode, lang, lang == "zh"
        self.cfg = LANGS[lang]

    # ---------- helpers ----------
    def tr(self, en):
        """English text -> this language (via i18n/<lang>.json for languages other than en/zh)."""
        if self.lang in ("en", "zh"):
            return en
        v = self.L(TR).get(en)
        if v is None:
            self.L(MISSING).add(en)
            return en
        return v

    def t(self, en, zh):
        if self.lang == "zh":
            return zh
        return self.tr(en)

    def updated_label(self):
        lab = STATUS["updated_label"]
        if self.lang in lab:
            return lab[self.lang]
        y, m, d = STATUS["updated"][:10].split("-")
        return f'{int(d)} {self.cfg["months"][int(m) - 1]} {y}, {STATUS["updated"][11:16]} UTC'

    def L(self, obj):
        """Localized value of a data field that has "en"/"zh" keys."""
        if self.lang in obj:
            return obj[self.lang]
        v = obj["en"]
        return [self.tr(x) for x in v] if isinstance(v, list) else self.tr(v)

    def url(self, key, lang=None, anchor=""):
        lang = lang or self.lang
        pre = LANGS[lang]["prefix"]
        if key.startswith("a:"):
            slug = "news/" + key[2:]
        else:
            slug = PAGES[key]
        if self.mode == "prod":
            base = ("/" + pre) if pre else ""
            p = (base + "/" + slug) if slug else (base or "/")
        else:
            flat = slug.replace("/", "-")
            if not slug:
                p = (pre + ".html") if pre else "index.html"
            else:
                p = ((pre + "-") if pre else "") + flat + ".html"
        return p + (("#" + anchor) if anchor else "")

    def asset(self, name):
        return ("/static/" if self.mode == "prod" else "") + name

    def img(self, name, alt, cls="", lazy=True):
        w, h = IMG[name]
        c = f' class="{cls}"' if cls else ""
        lz = ' loading="lazy"' if lazy else ""
        return f'<img{c} src="{self.asset("img/" + name)}" width="{w}" height="{h}" alt="{escape(alt)}"{lz}>'

    def date(self, iso):
        y, m, d = iso.split("-")
        return f"{int(m)}/{int(d)}" if self.zh else f"{int(d)} {self.cfg['months'][int(m) - 1]}"

    def shot(self, name, alt, credit=None):
        credit = credit or self.t("Screenshot: Rockstar Games", "截图：Rockstar Games")
        return f'<figure class="shot">{self.img(name, alt)}<figcaption>{credit}</figcaption></figure>'

    # ---------- chrome ----------
    def nav(self, cur):
        t = self.t
        items = [("home", t("Is it on PC?", "有 PC 版吗")), ("release", t("Release date", "发售日")),
                 ("tracker", t("Port tracker", "移植进度")), ("fps", t("FPS", "帧数")),
                 ("play", t("Play on PC now", "现在怎么玩")), ("specs", t("PC specs", "配置")), ("news", t("News", "新闻")), ("faq", t("FAQ", "问答"))]
        return "".join(f'<a href="{self.url(k)}"{cur_attr(k == cur)}>{l}</a>' for k, l in items)

    def header(self, cur):
        langs = "".join(f'<a href="{self.url(cur, l)}" hreflang="{c["code"]}" lang="{c["code"]}"{cur_attr(l == self.lang)}>{c["name"]}</a>' for l, c in LANGS.items())
        return f'''<header class="top">
  <div class="wrap">
    <a class="logo" href="{self.url("home")}">GTA VI <b>PC</b><small>STATUS</small></a>
    <nav class="nav" aria-label="Main">{self.nav(cur)}</nav>
    <details class="langs"><summary aria-label="Language">{self.cfg["label"]}</summary><div>{langs}</div></details>
    <details class="menu">
      <summary>{self.t("Menu", "菜单")}</summary>
      <nav class="nav" aria-label="Main (mobile)">{self.nav(cur)}</nav>
    </details>
  </div>
</header>'''

    def footer(self):
        t = self.t
        links = [("release", t("PC release date", "PC 版发售日")), ("tracker", t("Port tracker", "移植进度")),
                 ("leak", t("EXE leak explained", "EXE 泄露解读")), ("safe", t("Is that download safe?", "下载安全吗")),
                 ("play", t("Play on PC now", "现在怎么玩")), ("specs", t("PC specs", "配置")), ("steam", t("Steam & Game Pass", "Steam 与 Game Pass")),
                 ("fps", t("GTA 6 FPS", "GTA 6 帧数")), ("online", t("GTA 6 Online on PC", "GTA 6 Online 与 PC")), ("faq", t("FAQ", "常见问题")),
                 ("news", t("News", "新闻")), ("privacy", t("Privacy", "隐私")), ("terms", t("Terms", "条款"))]
        a = "".join(f'<a href="{self.url(k)}">{l}</a>' for k, l in links)
        play = "/play/" if self.mode == "prod" else "https://gta6pc.org/play/"
        return f'''<footer>
  <div class="wrap">
    <div class="cols">{a}<a href="{play}">{t("Neon Bay mini game", "Neon Bay 小游戏")}</a></div>
    <p>{t("GTA6PC.org is an unofficial fan site, not affiliated with Rockstar Games or Take-Two Interactive. Screenshots © Rockstar Games.",
          "GTA6PC.org 是非官方粉丝站，与 Rockstar Games、Take-Two 无关。游戏截图版权归 Rockstar Games。")}</p>
    <p>{t("We never host or link game files.", "本站不提供也不链接任何游戏文件。")}</p>
  </div>
</footer>'''

    def head(self, key, title, desc, faqs=None, crumbs=None, noindex=False, article=None):
        fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                 '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600'
                 + ("&family=Noto+Sans+SC:wght@400;500;700;900" if self.zh else "") + f'&display=swap"><link rel="stylesheet" href="{self.asset("site.css")}">')
        h = [f"<title>{escape(title)}</title>", f'<meta name="description" content="{escape(desc)}">']
        if self.mode == "prod":
            canon = SITE + self.url(key)
            h += [f'<link rel="canonical" href="{canon}">',
                  *[f'<link rel="alternate" hreflang="{c["code"]}" href="{SITE + self.url(key, l)}">' for l, c in LANGS.items()],
                  f'<link rel="alternate" hreflang="x-default" href="{SITE + self.url(key, "en")}">',
                  '<meta name="theme-color" content="#0d0718">',
                  f'<meta name="robots" content="{"noindex" if noindex else "index, follow"}">',
                  '<meta property="og:type" content="website">', '<meta property="og:site_name" content="GTA6PC.org">',
                  f'<meta property="og:locale" content="{self.cfg["og"]}">',
                  f'<meta property="og:title" content="{escape(title)}">', f'<meta property="og:description" content="{escape(desc)}">',
                  f'<meta property="og:url" content="{canon}">', f'<meta property="og:image" content="{SITE}/og-image.png">',
                  '<meta name="twitter:card" content="summary_large_image">']
            graph = [{"@type": "WebPage", "@id": canon + "#webpage", "url": canon, "name": title, "description": desc,
                      "inLanguage": self.cfg["code"], "dateModified": STATUS["updated"][:10],
                      "about": {"@type": "VideoGame", "name": "Grand Theft Auto VI", "alternateName": "GTA 6"}}]
            if crumbs:
                graph.append({"@type": "BreadcrumbList", "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + self.url(k)} for i, (k, n) in enumerate(crumbs)]})
            if article:
                graph.append({"@type": "NewsArticle", "headline": title, "datePublished": article["date"], "dateModified": article["date"],
                              "inLanguage": self.cfg["code"], "mainEntityOfPage": canon, "image": [f"{SITE}/og-image.png"],
                              "author": {"@type": "Organization", "name": "GTA6PC.org", "url": SITE + "/"},
                              "publisher": {"@type": "Organization", "name": "GTA6PC.org", "url": SITE + "/"}})
            if faqs:
                graph.append({"@type": "FAQPage", "mainEntity": [
                    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]})
            feed = SITE + (("/" + self.cfg["prefix"]) if self.cfg["prefix"] else "") + "/news/feed.xml"
            h.append(f'<link rel="alternate" type="application/rss+xml" title="GTA6PC.org news" href="{feed}">')
            h.append('<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + "</script>")
        h.append(fonts)
        return "\n".join(h)

    def ads(self, key, noindex):
        """Adsterra Popunder + Social Bar (config in data/ads.json). Production only; never on legal pages or 404.

        allowedPaths is what runtime.js actually loads against. It must list every content URL,
        including news articles. /play/ is the legacy mini-game (not the "play" page key) and is
        excluded by the runtime's path segment list, and this generator never injects ads there.
        """
        if self.mode != "prod" or not ADS.get("enabled") or noindex or key in ADS.get("no_ads_pages", []):
            return ""
        skip = set(ADS.get("no_ads_pages", []))
        keys = [k for k in PAGES if k not in skip]
        keys += ["a:" + n["slug"] for n in NEWS if n.get("slug")]
        allowed = sorted({Site("prod", l).url(k) for l in LANGS for k in keys})
        cfg = dict(ADS["config"], allowedPaths=allowed)
        return ('<script type="application/json" id="adsterra-config">' + json.dumps(cfg, ensure_ascii=False) + "</script>\n"
                f'<script src="{ADS["runtime"]}" defer></script>')

    def doc(self, key, title, desc, body, faqs=None, crumbs=None, noindex=False, article=None):
        head = self.head(key, title, desc, faqs, crumbs, noindex, article)
        body = body + "\n" + self.ads(key, noindex)
        if self.mode == "preview" and key == "home" and self.lang == "en":
            # Artifact preview entry page: the host supplies <html>/<head>.
            return f'<meta name="claude:viewport-fit-sides" content="cover">\n{head}\n{body}\n'
        return (f'<!doctype html>\n<html lang="{self.cfg["code"]}">\n<head>\n<meta charset="utf-8">\n'
                f'<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n')

    # ---------- reusable blocks ----------
    def faq_block(self, faqs, open_first=False):
        return '<div class="faq">' + "".join(
            f'<details{" open" if open_first and i == 0 else ""}><summary>{escape(q)}</summary><p>{a}</p></details>' for i, (q, a) in enumerate(faqs)) + "</div>"

    # ---------- port race components (v3) ----------
    STAGES = [("Groundwork", "基础工作"), ("EXE runs", "程序运行"), ("First frames", "出画面"), ("Menus", "菜单"),
              ("In the world", "进世界"), ("In control", "能操控"), ("Playable", "可玩")]
    STAGE_DEF = [("Loader and shader translation built before the EXE existed", "EXE 出来之前做好的加载器和着色器转译"),
                 ("The game’s own code starts running", "游戏自己的代码开始运行"),
                 ("Logos, loading screens or video appear", "出现 Logo、加载画面或视频"),
                 ("Title screen and settings respond to input", "标题和设置界面能操作"),
                 ("Story mode loads the world, however broken", "剧情模式能加载世界，哪怕画面错乱"),
                 ("You move a character with the HUD or pause menu working", "能操控角色移动，HUD 或暂停菜单可用"),
                 ("20+ fps on average without regular crashes", "平均 20 帧以上，且不经常崩溃")]

    def ext(self, url, text):
        return f'<a href="{url}" rel="nofollow noopener" target="_blank">{escape(text)}</a>'

    def source_list(self, sources):
        t = self.t
        kinds = {"tracker": t("Tracker", "追踪站"), "video": t("Video", "视频"), "press": t("Press", "媒体"),
                 "readme": t("Project’s own notes", "项目自述"), "notice": t("Official record", "官方记录")}
        li = []
        for x in sources:
            k = f'<span class="sk {x["kind"]}">{kinds[x["kind"]]}</span>'
            if x.get("url"):
                li.append(f'<li>{k}{self.ext(x["url"], self.L(x))}</li>')
            else:
                li.append(f'<li>{k}<span>{escape(self.L(x))}</span></li>')
        return f'<div class="srcs"><p class="eyebrow">{t("Where these numbers come from", "数字出处")}</p><ul>{"".join(li)}</ul></div>'

    def stage_name(self, s):
        return self.t(*self.STAGES[s - 1])

    def evidence_tag(self, ev):
        tags = {"verified": ("ok", self.t("Seen by tracker", "追踪站核验")), "press": ("cy", self.t("Press-reported", "媒体报道")),
                "self": ("", self.t("Self-reported", "自报")), "stream": ("warn", self.t("Stream only", "仅直播"))}
        c, l = tags[ev]
        return f'<span class="tag {c}">{l}</span>'

    def clock(self):
        from datetime import datetime, timezone
        start = datetime.fromisoformat(STATUS["exe_released_at"].replace("Z", "+00:00"))
        now = datetime.fromisoformat(STATUS["updated"].replace("Z", "+00:00"))
        s = int((now - start).total_seconds())
        d, h, m = s // 86400, s % 86400 // 3600, s % 3600 // 60
        lab = [self.t("days", "天"), self.t("hrs", "时"), self.t("min", "分"), self.t("sec", "秒")]
        parts = "<em>:</em>".join(f'<span data-u="{u}">{v:02d}<small>{l}</small></span>' for u, v, l in zip("dhms", (d, h, m, 0), lab))
        return (f'<div class="clock" data-since="{STATUS["exe_released_at"]}" aria-label="{self.t("Time since the EXE leak", "距 EXE 泄露")}">{parts}</div>'
                '<script>(function(){var c=document.currentScript.previousElementSibling,t0=Date.parse(c.dataset.since);'
                'function p(n){return(n<10?"0":"")+n}function f(){var s=Math.max(0,Math.floor((Date.now()-t0)/1000)),v={d:Math.floor(s/86400),h:Math.floor(s%86400/3600),m:Math.floor(s%3600/60),s:s%60};'
                'c.querySelectorAll("[data-u]").forEach(function(e){e.firstChild.nodeValue=p(v[e.dataset.u])})}f();setInterval(f,1000)})();</script>')

    def in_game_count(self):
        return sum(1 for p in PROJECTS if p["stage"] >= 6)

    def stage_lanes(self):
        t = self.t
        furthest = max(p["stage"] for p in PROJECTS)
        cols = []
        for s in range(1, 8):
            here = [p for p in PROJECTS if p["stage"] == s]
            chips = "".join(f'<a class="lchip{" priv" if not p["public"] else ""}{" off" if p["offline"] else ""}" href="{self.url("tracker", anchor=p["id"])}" title="{escape(self.L(p["summary"]))}">{escape(p["name"].split(" (")[0])}</a>' for p in here)
            cols.append(f'<div class="lane{" on" if s <= furthest else ""}"><div class="lbar"></div><div class="lhead"><b>{s}</b> {self.stage_name(s)}</div>'
                        f'<div class="lcount">{len(here) or "–"}</div><div class="lchips">{chips}</div></div>')
        legend = (f'<p class="cap">{t("Each build sits at the furthest stage it has reached.", "每个版本放在它达到的最高阶段。")} '
                  f'<span class="lchip">{t("Public code", "公开代码")}</span> <span class="lchip priv">{t("Private", "私有")}</span> <span class="lchip off">{t("Offline", "已下线")}</span></p>')
        return f'<div class="lanes-wrap"><div class="lanes">{"".join(cols)}</div></div>{legend}'

    def trend_chart(self):
        t = self.t
        days = TREND["days"]
        W, H, L, R, T, B = 720, 270, 44, 92, 18, 34
        pw, ph = W - L - R, H - T - B
        n = len(days)

        def X(i):
            return L + pw * i / (n - 1)

        def Y(v):
            return T + ph * (1 - v / 30)
        g = "".join(f'<line class="gl" x1="{L}" x2="{W - R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}"/><text x="{L - 8}" y="{Y(v) + 4:.1f}" text-anchor="end">{v}</text>' for v in (0, 10, 20, 30))
        xl = "".join(f'<text x="{X(i):.1f}" y="{H - 10}" text-anchor="middle">{self.date(d["date"])}</text>' for i, d in enumerate(days))
        refs = (f'<line class="ref play" x1="{L}" x2="{W - R}" y1="{Y(20):.1f}" y2="{Y(20):.1f}"/><text class="rl play" x="{W - 2}" text-anchor="end" y="{Y(20) + 4:.1f}">{t("playable", "可玩线")}</text>'
                f'<line class="ref con" x1="{L}" x2="{W - R}" y1="{Y(30):.1f}" y2="{Y(30):.1f}"/><text class="rl" x="{W - 2}" text-anchor="end" y="{Y(30) + 4:.1f}">PS5 Pro</text>')
        ev = ""
        for j, e in enumerate(TREND["events"]):
            i = next(k for k, d in enumerate(days) if d["date"] == e["date"])
            ev += f'<line class="gl" x1="{X(i):.1f}" x2="{X(i):.1f}" y1="{T}" y2="{T + ph}" stroke-dasharray="2 3"/><text x="{X(i) + 4:.1f}" y="{T + 12 + j * 14}">{self.L(e)}</text>'
        series = ""
        for key, cls, lbl in (("private", "pv", t("Private", "私有")), ("public", "pb", t("Public code", "公开代码"))):
            pts = [(X(i), Y(d[key])) for i, d in enumerate(days)]
            path = " ".join(f'{"M" if i == 0 else "L"}{x:.1f},{y:.1f}' for i, (x, y) in enumerate(pts))
            series += f'<path class="ln {cls}" d="{path}"/>'
            for i, (x, y) in enumerate(pts):
                series += f'<circle class="dt {cls}{" last" if i == n - 1 else ""}" cx="{x:.1f}" cy="{y:.1f}" r="4"><title>{lbl} · {self.date(days[i]["date"])}: {days[i][key]} fps</title></circle>'
            lx, ly = pts[-1]
            series += f'<text class="v {cls}" x="{lx + 8:.1f}" y="{ly + 4:.1f}">{days[-1][key]} fps</text>'
        daysrc = "".join(f'<li><b>{self.date(x["date"])}</b> {self.L(x)} · ' + " · ".join(self.ext(u, n) for n, u in x["links"]) + "</li>" for x in TREND.get("sources", []))
        legend = (f'<div class="tleg"><span><i class="pv"></i>{t("Best private build", "最好的私有版本")}</span><span><i class="pb"></i>{t("Best public-code build", "最好的公开代码版本")}</span>'
                  f'<span><i class="rp"></i>{t("Playable line, 20 fps", "可玩线 20 帧")}</span></div>')
        return (f'<figure class="trend"><h3>{t("Best in-game frame rate, day by day", "游戏内最高帧数，逐日变化")}</h3>{legend}'
                f'<div class="svgwrap"><svg viewBox="0 0 {W} {H}" role="img" aria-label="{t("Line chart of best reported in-game fps from 19 to 27 November", "11 月 19 日到 27 日游戏内最高帧数折线图")}">{g}{refs}{ev}{series}{xl}</svg></div><script>(function(w){{w.scrollLeft=w.scrollWidth;}})(document.currentScript.previousElementSibling);</script>'
                f'<figcaption>{t("As first reported each day. Builds were not in game before 24 Nov.", "按每天首次报道的数字。11 月 24 日之前没有版本能进游戏。")}'
                f'<ul class="tsrc">{daysrc}</ul></figcaption></figure>')

    def race_board(self, compact=False):
        t = self.t
        clockrow = f'<div class="clockrow"><span class="eyebrow">{t("Since the EXE leaked", "距 EXE 泄露")}</span>{self.clock()}</div>'
        if compact:
            return f'<div class="race">{self.stage_lanes()}{self.takedown_mini()}</div>'
        side = f'<div class="tdpanel">{clockrow}{self.takedown_mini()}</div>'
        return f'{self.progress_card(side=side)}<div class="race" style="margin-top:18px"><h3>{t("Where every build sits", "每个版本走到了哪一步")}</h3>{self.stage_lanes()}</div>'

    def takedown_mini(self):
        t = self.t
        return (f'<div class="tdbox"><p class="eyebrow" style="color:var(--bad)">{t("Takedown watch", "下架动态")}</p>'
                f'<p><b>24 Nov</b> · {t("Take-Two’s DMCA notice disabled Leonida and 3,007 repositories on GitHub.", "Take-Two 的 DMCA 通知让 GitHub 下架了 Leonida 和 3,007 个仓库。")}</p>'
                f'<p><b>{t("Since then", "此后")}</b> · {t("Leading builds went private, and port Discords were closed or limited.", "领先版本转为私有，多个移植 Discord 被关闭或限制。")}</p></div>')

    def project_cards(self, rows, ranked=True):
        t = self.t
        out = []
        for i, p in enumerate(rows):
            gpu = " · ".join(p["gpu"]) if p["gpu"] else t("GPU not stated", "未说明显卡")
            tags = self.evidence_tag(p["evidence"]) + (f'<span class="tag">{t("Public code", "公开代码")}</span>' if p["public"] else f'<span class="tag">{t("Private", "私有")}</span>')
            if p["offline"]:
                tags += f'<span class="tag bad">{t("Offline", "已下线")}</span>'
            meters = ""
            for lbl, v, txt in ((t("Story", "剧情"), p["story"]["v"], self.L(p["story"])), (t("Picture", "画面"), p["picture"]["v"], self.L(p["picture"])),
                                (t("Speed", "帧数"), min(p["fps"] / 30, 1), (f'{p["fps"]} fps' if p["fps"] else "—")), (t("Stability", "稳定性"), p["stability"]["v"], self.L(p["stability"]))):
                meters += f'<div class="meter4"><div><span>{lbl}</span><b>{txt}</b></div><i><s style="width:{v * 100:.0f}%"></s></i></div>'
            wb = ""
            if self.L(p["works"]) or self.L(p["blocks"]):
                w = "".join(f"<li>{x}</li>" for x in self.L(p["works"]))
                b = "".join(f"<li>{x}</li>" for x in self.L(p["blocks"]))
                wb = (f'<div class="wb"><div><p class="eyebrow">{t("What works", "能做到")}</p><ul>{w}</ul></div>'
                      f'<div class="bl"><p class="eyebrow">{t("What’s blocking", "卡在哪")}</p><ul>{b}</ul></div></div>')
            meter_block = f'<div class="meters">{meters}</div>' if p["stage"] >= 6 else ""
            rk = f"{i + 1}" if ranked else "●"
            gpus = " ".join(p["gpu"]).lower() or "none"
            out.append(f'''<article class="pcard{"" if ranked else " priv"}" id="{p["id"]}" data-gpu="{gpus}" data-pub="{"1" if p["public"] else "0"}">
  <div class="rk">{rk}</div>
  <div><h3><a class="hlink" href="#{p["id"]}">{escape(p["name"])}</a></h3><p class="hw">{self.L(p["approach"])} · {gpu}</p></div>
  <div class="sc"><b>{(str(p["fps"]) + " fps") if p["fps"] else "—"}</b><span>{p["stage"]}/7 · {self.stage_name(p["stage"])}</span></div>
  <div class="body">
    <div class="tags">{tags}</div>
    <p class="sum">{self.L(p["summary"])}</p>
    {meter_block}
    {wb}
    <p class="hw">{t("Tested on", "测试平台")}: {escape(p["hw"])}</p>
    {self.source_list(p.get("sources", []))}
  </div>
</article>''')
        return '<div class="pcards">' + "".join(out) + "</div>"

    # ---------- headline progress card (v4) ----------
    MILESTONES = [("Groundwork", "基础工作"), ("EXE runs", "程序运行"), ("First frames", "出画面"), ("Menus", "菜单"),
                  ("In the world", "进世界"), ("In control", "能操控"), ("Playable", "可玩"), ("Console-like", "接近主机")]

    @staticmethod
    def score(p):
        seg = 100 / 7
        s, fps = p["stage"], p["fps"]
        if s <= 5:
            return (s - 1) * seg
        if s == 6:
            return 5 * seg + min(fps / 20, 0.99) * seg
        return 6 * seg + max(0, min((fps - 20) / 10, 1)) * seg

    def progress_card(self, side=None):
        t = self.t
        r = STATUS["race"]
        pub = sorted([p for p in PROJECTS if p["public"] and not p["offline"]], key=self.score, reverse=True)
        allp = sorted(PROJECTS, key=self.score, reverse=True)
        lead = pub[0]
        lead_pct = self.score(lead)
        # pins: top builds, spread so avatars don't overlap
        pick = []
        for p in allp:
            if p["offline"] or len(pick) >= 6:
                continue
            if any(abs(self.score(p) - self.score(q)) < 0.5 for q in pick):
                continue
            pick.append(p)
        pick = sorted(pick, key=self.score, reverse=True)
        gap, xs, prev = 6.5, [], None
        for p in pick:
            x = min(self.score(p), 97.5) if prev is None else min(self.score(p), prev - gap)
            xs.append(x)
            prev = x
        lines = "".join(f'<line x1="{x * 10:.1f}" y1="0" x2="{self.score(p) * 10:.1f}" y2="40"/>' for p, x in zip(pick, xs))
        pins = ""
        for p, x in zip(pick, xs):
            ini = "".join(w[0] for w in p["name"].replace("(", " ").split()[:2]).upper()[:2] if " " in p["name"] else p["name"][:2].upper()
            flag = f'<em>{escape(p["name"].split(" (")[0])} · {self.score(p):.0f}%</em>' if p is lead else ""
            pins += f'<span class="pp{" priv" if not p["public"] else ""}{" lead" if p is lead else ""}" style="left:{x:.1f}%" title="{escape(p["name"])} · {p["fps"]} fps · {self.score(p):.0f}%">{flag}<b>{ini}</b></span>'
        extra = {6: "<small>20 fps</small>", 7: "<small>30 fps</small>"}
        ticks = "".join(f'<span style="left:{i * 100 / 7:.2f}%"><b>{i * 100 / 7:.0f}%</b>{t(*m)}{extra.get(i, "")}</span>' for i, m in enumerate(self.MILESTONES))
        chips = (f'<div class="chip4"><b>{self.stage_name(r["furthest_stage"])}</b><span>{t("furthest milestone", "最高里程碑")}</span></div>'
                 f'<div class="chip4"><b>~{r["best_fps"]} fps</b><span>{t("best reported (private)", "最高报道（私有）")}</span></div>'
                 f'<div class="chip4"><b>{self.in_game_count()}</b><span>{t("builds in control", "能操控的版本")}</span></div>'
                 f'<div class="chip4"><b>{r["repos_taken_down"]:,}</b><span>{t("repos taken down", "仓库被下架")}</span></div>')
        if side is None:
            items = "".join(f'<li><time>{self.date(n["date"])}</time><span>' + (f'<a href="{self.url("a:" + n["slug"])}">{self.L(n)[0]}</a>' if n.get("slug") else self.L(n)[0]) + '</span></li>' for n in NEWS[:5])
            side = (f'<div class="feed"><p class="eyebrow">{t("What changed", "最新动态")}</p><ol>{items}</ol>'
                    f'<a class="more" href="{self.url("news")}">{t("All news →", "全部新闻 →")}</a></div>')
        return f'''<div class="pcard-hero">
  <div class="ph-top">
    <div>
      <p class="eyebrow">{t("Unofficial PC port · progress to a console-like game", "民间 PC 移植 · 距离“和主机一样能玩”")}</p>
      <div class="bignum">{lead_pct:.0f}<small>%</small></div>
      <p class="lead">{t("Leader: ", "领先：")}<b>{escape(lead["name"])}</b> · {lead["fps"]} fps · {self.stage_name(lead["stage"])}{t(". Best public build; a private one claims more.", "。这是最好的公开版本，有私有版本声称更快。")}</p>
    </div>
    <div class="chips4">{chips}</div>
  </div>
  <div class="pbar-wrap"><div class="pbar">
    <div class="ppins"><svg viewBox="0 0 1000 40" preserveAspectRatio="none" aria-hidden="true">{lines}</svg>{pins}</div>
    <div class="track8"><i style="width:{lead_pct:.1f}%"></i>{"".join(f'<u style="left:{i * 100 / 7:.2f}%"></u>' for i in range(1, 7))}</div>
    <div class="ticks8">{ticks}</div>
  </div></div>
  <script>(function(w){{if(w.scrollWidth>w.clientWidth)w.scrollLeft=w.scrollWidth;}})(document.currentScript.previousElementSibling);</script>
  <div class="ph-bottom">{self.trend_chart()}{side}</div>
</div>'''

    # ---------- "Can my PC run GTA 6?" checker (v5) ----------
    # Relative performance indexes, RTX 3060 12 GB = 100 (GPU) and Ryzen 5 3600 = 100 (CPU). Rough, for tiering only.
    GPUS = [
        ("NVIDIA", [("GTX 1660 Super", 55, 6), ("RTX 2060", 70, 6), ("RTX 2070 Super", 95, 8), ("RTX 3050", 60, 8), ("RTX 3060 12 GB", 100, 12),
                    ("RTX 3060 Ti", 125, 8), ("RTX 3070", 140, 8), ("RTX 3080", 180, 10), ("RTX 3090", 200, 24), ("RTX 4060", 110, 8),
                    ("RTX 4060 Ti 16 GB", 130, 16), ("RTX 4070", 175, 12), ("RTX 4070 Super", 205, 12), ("RTX 4070 Ti Super", 235, 16),
                    ("RTX 4080 Super", 280, 16), ("RTX 4090", 360, 24), ("RTX 5060", 125, 8), ("RTX 5060 Ti 16 GB", 145, 16), ("RTX 5070", 220, 12),
                    ("RTX 5070 Ti", 270, 16), ("RTX 5080", 300, 16), ("RTX 5090", 420, 32)]),
        ("NVIDIA laptop", [("RTX 4050 Laptop", 70, 6), ("RTX 4060 Laptop", 90, 8), ("RTX 4070 Laptop", 100, 8), ("RTX 4080 Laptop", 165, 12),
                           ("RTX 4090 Laptop", 195, 16), ("RTX 5070 Laptop", 115, 8), ("RTX 5070 Ti Laptop", 150, 12), ("RTX 5080 Laptop", 190, 16)]),
        ("AMD", [("RX 5700 XT", 95, 8), ("RX 6600", 85, 8), ("RX 6600 XT", 100, 8), ("RX 6700 XT", 125, 12), ("RX 6800", 160, 16),
                 ("RX 6800 XT", 185, 16), ("RX 6900 XT", 195, 16), ("RX 7600", 105, 8), ("RX 7700 XT", 150, 12), ("RX 7800 XT", 190, 16),
                 ("RX 7900 GRE", 210, 16), ("RX 7900 XT", 245, 20), ("RX 7900 XTX", 280, 24), ("RX 9060 XT 16 GB", 140, 16), ("RX 9070", 240, 16),
                 ("RX 9070 XT", 275, 16)]),
        ("Intel / handheld", [("Arc A770 16 GB", 110, 16), ("Arc B580", 120, 12), ("Steam Deck", 15, 4)]),
    ]
    CPUS = [
        ("AMD", [("Ryzen 5 2600", 75), ("Ryzen 5 3600", 100), ("Ryzen 7 3700X", 105), ("Ryzen 5 5600", 135), ("Ryzen 7 5800X", 145),
                 ("Ryzen 7 5800X3D", 175), ("Ryzen 5 7600", 160), ("Ryzen 7 7700X", 175), ("Ryzen 7 7800X3D", 215), ("Ryzen 7 9700X", 185),
                 ("Ryzen 7 9800X3D", 230), ("Ryzen 9 7950X", 190)]),
        ("Intel", [("Core i7-8700K", 90), ("Core i7-9700K", 100), ("Core i5-10400", 100), ("Core i7-10700K", 115), ("Core i5-11400", 115),
                   ("Core i5-12400", 135), ("Core i5-12600K", 150), ("Core i7-12700K", 165), ("Core i5-13400", 145), ("Core i5-13600K", 175),
                   ("Core i7-13700K", 190), ("Core i5-14600K", 180), ("Core i7-14700K", 200), ("Core i9-14900K", 210), ("Core Ultra 7 265K", 195)]),
    ]

    def checker(self):
        t = self.t
        glab = {"NVIDIA laptop": t("NVIDIA laptop", "NVIDIA 笔记本"), "Intel / handheld": t("Intel / handheld", "Intel / 掌机")}
        gopts = "".join(f'<optgroup label="{glab.get(g, g)}">' + "".join(f'<option value="{i}|{v}"{" selected" if n == "RTX 4060" else ""}>{n}</option>' for n, i, v in items) + "</optgroup>" for g, items in self.GPUS)
        copts = "".join(f'<optgroup label="{g}">' + "".join(f'<option value="{i}"{" selected" if n == "Ryzen 5 5600" else ""}>{n}</option>' for n, i in items) + "</optgroup>" for g, items in self.CPUS)
        ropts = "".join(f'<option value="{r}"{" selected" if r == 16 else ""}>{r} GB</option>' for r in (8, 16, 32, 64))
        L = {"tiers": [t("Minimum · 1080p 30 fps", "最低 · 1080p 30 帧"), t("Recommended · 1440p 60 fps", "推荐 · 1440p 60 帧"), t("Enthusiast · 4K 60 fps", "发烧 · 4K 60 帧")],
             "best": t("Your PC lands in", "你的电脑在"), "below": t("Below our minimum estimate", "低于我们估算的最低配置"),
             "gpu": t("graphics card", "显卡"), "cpu": t("processor", "CPU"), "ram": t("memory", "内存"), "held": t("held back by your", "拖后腿的是"),
             "vram": t("8 GB of video memory or less: expect to lower texture quality.", "显存 8 GB 或以下：要把材质调低。"),
             "ok": t("Meets this tier", "达到这一档")}
        return f'''<div class="checker" id="checker">
  <div class="ck-in">
    <h3>{t("Can my PC run GTA 6?", "我的电脑能跑 GTA 6 吗？")}</h3>
    <p class="sub">{t("Pick your parts. Tiers follow our estimate for the official PC version.", "选择你的配件，按我们对官方 PC 版的配置估算来分档。")}</p>
    <label for="ck-gpu">{t("Graphics card", "显卡")}</label><select id="ck-gpu">{gopts}</select>
    <label for="ck-cpu">{t("Processor", "CPU")}</label><select id="ck-cpu">{copts}</select>
    <label for="ck-ram">{t("Memory", "内存")}</label><select id="ck-ram">{ropts}</select>
  </div>
  <div class="ck-out" aria-live="polite"><p class="eyebrow" id="ck-head"></p><div class="ck-big" id="ck-big"></div><ul id="ck-list"></ul><p class="cap" id="ck-note"></p></div>
</div>
<script>
(function () {{
  var L = {json.dumps(L, ensure_ascii=False)}, need = [[100, 100, 16], [190, 170, 32], [270, 200, 32]];
  var g = document.getElementById('ck-gpu'), c = document.getElementById('ck-cpu'), r = document.getElementById('ck-ram');
  function run() {{
    var gv = g.value.split('|'), gi = +gv[0], vram = +gv[1], ci = +c.value, ram = +r.value, best = -1, rows = '';
    need.forEach(function (n, i) {{
      var miss = [];
      if (gi < n[0]) miss.push(L.gpu); if (ci < n[1]) miss.push(L.cpu); if (ram < n[2]) miss.push(L.ram);
      if (!miss.length) best = i;
      rows += '<li class="' + (miss.length ? 'no' : 'yes') + '"><span class="ico ' + (miss.length ? 'n' : 'y') + '">' + (miss.length ? '✕' : '✓') + '</span><span><b>' + L.tiers[i] + '</b><small>' + (miss.length ? L.held + ' ' + miss.join(' + ') : L.ok) + '</small></span></li>';
    }});
    document.getElementById('ck-head').textContent = best < 0 ? '' : L.best;
    document.getElementById('ck-big').textContent = best < 0 ? L.below : L.tiers[best];
    document.getElementById('ck-big').className = 'ck-big t' + (best + 1);
    document.getElementById('ck-list').innerHTML = rows;
    document.getElementById('ck-note').textContent = vram <= 8 ? L.vram : '';
  }}
  [g, c, r].forEach(function (e) {{ e.addEventListener('change', run); }}); run();
}})();
</script>'''

    def stage_defs(self):
        rows = "".join(f'<tr><td class="num"><b>{i + 1}</b></td><td><b>{self.t(*self.STAGES[i])}</b></td><td>{self.t(*self.STAGE_DEF[i])}</td></tr>' for i in range(7))
        return f'<div class="tbl"><table><tbody>{rows}</tbody></table></div>'

    def hbars(self, rows, scale, ticks, goal=None):
        """Horizontal bar chart. rows: (label, value, css_class, value_label)."""
        def pct(v):
            return f"{v / scale * 100:.2f}%"
        r = []
        for n, v, c, lbl in rows:
            cls = f' class="{c}"' if c else ""
            if v / scale <= 0.72:
                r.append(f'<div class="r"><span>{n}</span><span class="bar"><s{cls} style="width:{pct(v)}"></s><em style="left:calc({pct(v)} + 8px)">{lbl}</em></span></div>')
            else:
                r.append(f'<div class="r"><span>{n}</span><span class="bar"><s{cls} style="width:{pct(v)}"></s><em class="in" style="left:calc({pct(v)} - 6px)">{lbl}</em></span></div>')
        g = ""
        if goal:
            gv, gl = goal
            g = (f'<div class="r" aria-hidden="true" style="position:absolute;inset:0;pointer-events:none"><span></span>'
                 f'<span style="position:relative;align-self:stretch"><span class="goal" style="left:{pct(gv)}"><span>{gl}</span></span></span></div>')
        tk = "".join(f"<span>{x}</span>" for x in ticks)
        return f'<div class="fps">{"".join(r)}{g}</div><div class="fps-axis"><span></span><div>{tk}</div></div>'

    def release_chart(self):
        t = self.t
        return f'''<div class="win" role="img" aria-label="{t("Estimated PC release windows, Nov 2026 to Nov 2028", "PC 版预计窗口，2026 年 11 月至 2028 年 11 月")}">
  <div class="win-inner">
    <div class="win-label">{t("Reported target (GamesBeat)", "媒体报道的目标（GamesBeat）")}</div>
    <div class="win-row"><span style="left:8.3%;width:12.5%;background:var(--cyan)">Q1 2027</span></div>
    <div class="win-label">{t("Rockstar history: fast 7 mo · typical 12 mo (RDR2) · slow 18+ mo", "Rockstar 历史：快 7 个月 · 一般 12 个月（荒野大镖客 2）· 慢 18 个月以上")}</div>
    <div class="win-row"><span style="left:29.2%;width:8.3%;background:#ffd36b">{t("Fast", "快")}</span><span style="left:50%;width:16.7%;background:var(--sun)">{t("Typical", "一般")}</span><span style="left:75%;width:25%;background:#ff8a5b">{t("Slow", "慢")}</span></div>
    <div class="win-axis num"><span>Nov '26</span><span>Feb '27</span><span>May '27</span><span>Aug '27</span><span>Nov '27</span><span>Feb '28</span><span>May '28</span><span>Aug '28</span></div>
  </div>
</div>'''

    def numbered(self, items, cols, first_cls=""):
        li = "".join(f'<li class="{first_cls if i == 0 else ""}"><time>{i + 1}</time><b>{a}</b><span>{b}</span></li>' for i, (a, b) in enumerate(items))
        return f'<ol class="stepper" style="grid-template-columns:repeat({cols},minmax(0,1fr))">{li}</ol>'

    def news_list(self, items, detail=True):
        t = self.t
        tags = {"port": ("cy", t("Port", "移植")), "leak": ("warn", t("Leak", "泄露")), "official": ("ok", t("Official", "官方")),
                "report": ("", t("Report", "报道")), "legal": ("bad", t("Legal", "法务")), "security": ("bad", t("Security", "安全"))}
        li = []
        for n in items:
            c, lbl = tags[n["tag"]]
            title, desc = self.L(n)
            src = n.get("source")
            sl = (f'<span class="src">{t("Source", "来源")}: <a href="{src["url"]}" rel="nofollow noopener" target="_blank">{escape(src["name"])}</a></span>') if src else ""
            if n.get("slug"):
                title = f'<a class="alink" href="{self.url("a:" + n["slug"])}">{title}</a>'
            li.append(f'<li><time datetime="{n["date"]}">{self.date(n["date"])}</time><div><h3><span class="tag {c}" style="margin-right:8px">{lbl}</span>{title}</h3>'
                      + (f"<p>{desc}</p>" if detail else "") + sl + "</div></li>")
        return '<ol class="log">' + "".join(li) + "</ol>"

    def board(self):
        t = self.t
        lamps = [("official_pc", "release", t("Official PC version", "官方 PC 版")), ("port", "tracker", t("Unofficial port", "民间移植")),
                 ("play_now", "play", t("Play on a PC screen", "在电脑屏幕上玩"))]
        sigs = "".join(f'<a class="sig" href="{self.url(k)}"><i class="lamp {STATUS[s]["lamp"]}"></i><div><div class="k">{lbl}</div>'
                       f'<div class="v">{self.L(STATUS[s])[0]}</div><div class="d">{self.L(STATUS[s])[1]}</div></div></a>' for s, k, lbl in lamps)
        return (f'<div class="board" aria-label="{t("Status board", "状态台")}"><header class="bclock"><span class="eyebrow">{t("Since the EXE leaked", "距 EXE 泄露")}</span>'
                f'{self.clock()}</header>{sigs}</div>')

    def yn_table(self, rows, head=None):
        th = ("<thead><tr>" + "".join(f"<th>{h}</th>" for h in head) + "</tr></thead>") if head else ""
        tr = "".join("<tr><td><span class=\"ico " + r[0] + "\">" + ("✓" if r[0] == "y" else "✕") + "</span></td>" + "".join(
            (f"<td><b>{c}</b></td>" if i == 0 else f"<td>{c}</td>") for i, c in enumerate(r[1:])) + "</tr>" for r in rows)
        return f'<div class="tbl"><table>{th}<tbody>{tr}</tbody></table></div>'

    # ---------- content page shell ----------
    def content_page(self, key, title, desc, h1, answer, body, faqs=None, image=None, tags=(), nexts=(), note="", article=None, schema_faqs=None):
        t = self.t
        crumbs = [("home", t("Home", "首页"))] + ([("news", t("News", "新闻"))] if article else []) + [(key, h1)]
        rail_items = [("home", t("Is GTA 6 on PC?", "有 PC 版吗")), ("release", t("PC release date", "PC 版发售日")), ("tracker", t("Port tracker", "移植进度")),
                      ("leak", t("EXE leak explained", "EXE 泄露解读")), ("safe", t("Is that download safe?", "下载安全吗")), ("play", t("Play on PC now", "现在怎么玩")),
                      ("specs", t("PC specs", "配置")), ("fps", t("GTA 6 FPS", "GTA 6 帧数")), ("online", t("GTA 6 Online", "GTA 6 Online")),
                      ("steam", t("Steam & Game Pass", "Steam 与 Game Pass")), ("news", t("News", "新闻")), ("faq", t("FAQ", "常见问题"))]
        rail = "".join(f'<a href="{self.url(k)}"{cur_attr(k == key)}>{l}</a>' for k, l in rail_items)
        tag_html = "".join(f'<span class="tag {c}">{x}</span>' for c, x in tags)
        img_html = self.img(image, "", lazy=False) if image else ""
        nx = ""
        if nexts:
            nx = (f'<div><p class="eyebrow" style="margin-bottom:12px">{t("Next", "接着看")}</p><div class="next">'
                  + "".join(f'<a href="{self.url(k)}">{a}<span>{b}</span></a>' for k, a, b in nexts) + "</div></div>")
        faq_html = (f'<h2>{t("FAQ", "常见问题")}</h2>' + self.faq_block(faqs)) if faqs else ""
        note_html = f'<p class="note">{note}</p>' if note else ""
        mid = (f'<a href="{self.url("news")}">{t("News", "新闻")}</a><span>/</span>') if article else ""
        html = f'''{self.header(key)}
<main>
  <section class="page-head{" photo" if image else ""}">
    {img_html}
    <div class="wrap">
      <div class="crumbs"><a href="{self.url("home")}">{t("Home", "首页")}</a><span>/</span>{mid}<span>{h1}</span></div>
      <h1>{h1}</h1>
      <div class="meta"><span class="tag">{t("Updated", "更新于")} {self.updated_label()}</span>{tag_html}</div>
      <p class="answer">{answer}</p>
    </div>
  </section>
  <div class="wrap layout">
    <article class="prose">
      {body}
      {faq_html}
      {nx}
      {note_html}
    </article>
    <aside class="rail"><nav aria-label="GTA 6 PC"><span class="eyebrow" style="padding:0 10px 8px">GTA 6 PC</span>{rail}</nav></aside>
  </div>
</main>
{self.footer()}'''
        return self.doc(key, title, desc, html, faqs=faqs or schema_faqs, crumbs=crumbs, article=article)

    # ======================= PAGES =======================
    def page_home(self):
        t = self.t
        play_rows = [("y", t("PS Remote Play (Windows app)", "PS Remote Play（Windows 客户端）"), t("Your PS5 + the game", "你自己的 PS5 + 游戏")),
                     ("y", t("Xbox app remote play", "Xbox 应用远程游玩"), t("Your Xbox Series X|S + the game", "你自己的 Xbox Series X|S + 游戏")),
                     ("y", t("Capture card", "采集卡"), t("Console + capture card, lowest lag", "主机 + 采集卡，延迟最低")),
                     ("n", t("Xbox Cloud Gaming", "Xbox 云游戏"), t("Xbox consoles only, not PC", "只推流到 Xbox 主机，PC 不行")),
                     ("n", t("GeForce Now / Game Pass", "GeForce Now / Game Pass"), t("Not available", "没有"))]
        faqs = [(t("Is GTA 6 on PC yet?", "GTA 6 出 PC 版了吗？"), t("Not officially. It launched on 19 November 2026 for PS5 and Xbox Series X|S only. Unofficial ports of the leaked Xbox build run at around 20–25 fps on high-end PCs.", "官方没有。2026 年 11 月 19 日只发售了 PS5 和 Xbox Series X|S 版。泄露 Xbox 版的民间移植在高端电脑上能跑 20–25 帧左右。")),
                (t("Will GTA 6 be on PC?", "GTA 6 会出 PC 版吗？"), t("Almost certainly. Every mainline GTA since GTA III has come to PC, and GamesBeat reports Rockstar is aiming for the first quarter of 2027. Rockstar hasn’t announced it yet.", "几乎肯定会。GTA III 以来每部正传都上了 PC，GamesBeat 报道 Rockstar 的目标是 2027 年第一季度。Rockstar 还没正式公布。")),
                (t("Can I play the unofficial port?", "民间移植我能玩吗？"), t("Not legally. Every build needs the leaked game files, Take-Two is taking projects down, and “ready-to-play” downloads are where malware hides.", "没有合法途径。所有版本都需要泄露的游戏文件，Take-Two 正在下架这些项目，而“一键可玩”的下载正是木马藏身的地方。")),
                (t("Can I pre-order it on Steam?", "Steam 能预购吗？"), t("No. There is no PC store listing anywhere yet.", "不能。目前任何 PC 商店都没有上架。")),
                (t("Is the Cyberleek EXE a PC version?", "大葱哥放的 EXE 是 PC 版吗？"), t("No. It is the Xbox program file and needs an unofficial port to run.", "不是。那是 Xbox 版的主程序，要靠民间移植项目才能跑。")),
                (t("Is GTA 6 on Game Pass?", "GTA 6 进 Game Pass 了吗？"), t("No, on any platform.", "没有，哪个平台都没有。")),
                (t("Should I upgrade my PC now?", "现在要不要升级电脑？"), t("Wait for official requirements, usually 1–2 months before a PC launch.", "先等官方配置，一般在 PC 版发售前 1–2 个月公布。"))]
        body = f'''{self.header("home")}
<main>
  <section class="hero photo">
    {self.img("hero-vice-city-night.jpg", t("Vice City skyline at dusk, GTA 6 screenshot", "GTA 6 游戏截图：黄昏的罪恶都市"), "bg", lazy=False)}
    <div class="wrap">
      <div>
        <p class="eyebrow">{t("Updated", "更新于")} {self.updated_label()}</p>
        <h1>{t("Is GTA 6 on PC?", "GTA 6 有 PC 版了吗？")}<span class="no">{t("Not officially.", "官方还没有。")}</span></h1>
        <p class="lede">{t("Unofficial ports of the leaked Xbox build now reach <strong>about 20–25 fps</strong> on high-end PCs. Rockstar hasn’t announced a PC version.", "泄露 Xbox 版的民间移植，已在高端电脑上跑到<strong>约 20–25 帧</strong>。Rockstar 还没公布 PC 版。")}</p>
        <div class="ctas"><a class="btn primary" href="{self.url("release")}">{t("PC release date", "PC 版什么时候出")}</a><a class="btn" href="{self.url("tracker")}">{t("Port tracker", "移植进度")}</a></div>
      </div>
      {self.board()}
    </div>
    <span class="credit">{t("Screenshot: Rockstar Games", "截图：Rockstar Games")}</span>
  </section>
  <div class="wrap hero-card">{self.progress_card()}</div>

  <section class="sec" id="port">
    <div class="wrap">
      <div class="sec-head"><div><p class="eyebrow">{t("Unofficial port race", "民间移植进度")}</p><h2>{t("Where every build sits", "每个版本走到了哪一步")}</h2></div><a class="more" href="{self.url("tracker")}">{t("Full tracker →", "完整进度表 →")}</a></div>
      {self.race_board(compact=True)}
    </div>
  </section>

  <section class="sec" id="release">
    <div class="wrap">
      <div class="sec-head"><div><p class="eyebrow">{t("PC release date", "PC 版发售日")}</p><h2>{t("When is GTA 6 coming to PC?", "GTA 6 PC 版什么时候出？")}</h2></div><a class="more" href="{self.url("release")}">{t("Full breakdown →", "详细分析 →")}</a></div>
      <div class="split">
        <div class="grid2" style="grid-template-columns:minmax(0,1fr)">
          <div class="panel"><p class="eyebrow">{t("Insider report · GamesBeat, 13 Oct", "业内爆料 · GamesBeat，10 月 13 日")}</p><div class="big cyan">{t("Jan – Mar 2027", "2027 年 1–3 月")}</div><p style="margin-top:6px">{t("Four unnamed sources. Not confirmed.", "4 个匿名信源，官方未确认。")}</p></div>
          <div class="panel"><p class="eyebrow">{t("Rockstar history · RDR2 took 12 months", "历史规律 · 荒野大镖客 2 隔了 12 个月")}</p><div class="big amber">{t("Nov 2027", "2027 年 11 月")}</div><p style="margin-top:6px">{t("GTA 5 took 19 months, but had a PS4 port in between.", "GTA 5 隔了 19 个月，但中间多做了一次 PS4 版。")}</p></div>
        </div>
        {self.shot("beach-car.jpg", t("GTA 6 screenshot: beach and sports car", "GTA 6 截图：海滩与跑车"))}
      </div>
      {self.release_chart()}
    </div>
  </section>

  <section class="sec" id="play-now">
    <div class="wrap">
      <div class="sec-head"><div><p class="eyebrow">{t("Play on PC today", "现在怎么玩")}</p><h2>{t("Play GTA 6 on a PC screen", "在电脑上玩 GTA 6 的办法")}</h2><p>{t("You need a console that owns the game. The PC is only the screen.", "前提是你有主机和正版游戏，电脑只是当屏幕用。")}</p></div><a class="more" href="{self.url("play")}">{t("Step-by-step setup →", "设置步骤 →")}</a></div>
      <div class="split">
        {self.yn_table(play_rows)}
        {self.shot("heist.jpg", t("GTA 6 screenshot: Lucia and Jason in a heist", "GTA 6 截图：露西亚和杰森抢劫中"))}
      </div>
    </div>
  </section>

  <section class="sec" id="specs">
    <div class="wrap">
      <div class="sec-head"><div><p class="eyebrow">{t("PC specs (estimate)", "配置（预估）")}</p><h2>{t("Will my PC run GTA 6?", "我的电脑能跑吗？")}</h2><p>{t("Consoles are stuck at 30 fps by the CPU, so the CPU matters for 60 fps.", "主机被 CPU 卡在 30 帧，所以想上 60 帧，CPU 和显卡一样重要。")}</p></div><span class="mores"><a class="more" href="{self.url("fps")}">{t("60 fps on PC? →", "PC 能 60 帧吗？→")}</a><a class="more" href="{self.url("specs", anchor="checker")}">{t("Check your PC →", "检测你的电脑 →")}</a></span></div>
      <div class="grid3">
        <div class="panel"><p class="eyebrow">{t("Minimum", "最低")}</p><div class="big" style="font-size:1.4rem">1080p · 30</div><p style="margin-top:8px">Ryzen 5 3600 · RTX 3060 12GB · 16GB</p></div>
        <div class="panel"><p class="eyebrow">{t("Recommended", "推荐")}</p><div class="big cyan" style="font-size:1.4rem">1440p · 60</div><p style="margin-top:8px">Ryzen 7 7700X · RTX 4070 Super · 32GB</p></div>
        <div class="panel"><p class="eyebrow">{t("PS5 Pro does", "PS5 Pro 实测")}</p><div class="big amber" style="font-size:1.4rem">1440p → 4K · 30</div><p style="margin-top:8px">{t("Digital Foundry: near-locked 30 fps", "Digital Foundry：几乎稳定 30 帧")}</p></div>
      </div>
    </div>
  </section>

  <section class="sec">
    <div class="wrap">
      <div class="alert" id="safety">
        <div>
          <p class="eyebrow" style="color:var(--bad)">{t("Download warning", "下载警告")}</p>
          <h2 style="margin-top:8px">{t("There is no real GTA 6 PC download", "没有真的 GTA 6 PC 下载")}</h2>
          <a class="btn" style="margin-top:18px" href="{self.url("safe")}">{t("How to spot a fake", "怎么识别假下载")}</a>
        </div>
        <ul>
          <li>{t("Repacks, cracks, ISOs, “early access”", "所谓的整合版、破解版、ISO、“抢先体验”")}</li>
          <li>{t("Bundled “PS5 / Xbox emulators”", "附带“PS5 / Xbox 模拟器”")}</li>
          <li>{t("“Turn off your antivirus first”", "要求“先关掉杀毒软件”")}</li>
          <li>{t("Survey, login or crypto to unlock", "要填问卷、登录账号或付加密货币才能解锁")}</li>
        </ul>
      </div>
    </div>
  </section>

  <section class="sec" id="faq">
    <div class="wrap">
      <div class="sec-head"><div><p class="eyebrow">FAQ</p><h2>{t("Quick answers", "常见问题")}</h2></div><a class="more" href="{self.url("faq")}">{t("All 30 questions →", "全部 30 个问题 →")}</a></div>
      {self.faq_block(faqs, open_first=True)}
    </div>
  </section>
</main>
{self.footer()}'''
        return self.doc("home", t("GTA 6 PC: Is It Out? Release Date, Port Tracker & Requirements", "GTA 6 PC 版：出了吗？发售日、移植进度与配置要求"),
                        t("Is GTA 6 (GTA VI) on PC? Not officially. Live status of the PC release date, the unofficial port race after the Cyberleek EXE leak, PC requirements and fake downloads.",
                          "GTA 6 有 PC 版了吗？官方还没有。实时整理 PC 版发售日、大葱哥 EXE 泄露后的民间移植进度、配置预估和假下载识别。"),
                        body, faqs=faqs, crumbs=[("home", t("Home", "首页"))])

    def page_tracker(self):
        t = self.t
        ranked = sorted([p for p in PROJECTS if p["public"]], key=lambda p: (-p["stage"], -p["fps"]))
        private = sorted([p for p in PROJECTS if not p["public"]], key=lambda p: (-p["stage"], -p["fps"]))
        body = f'''{self.race_board()}
<h2>{t("The public builds, ranked", "公开代码的版本排名")}</h2>
<p>{t("Ranked by stage, then by frame rate. Each card says how we know: seen by a tracker, reported by the press, only shown on a stream, or claimed by the author.", "先按阶段排，再按帧数排。每张卡片都标了消息来源：追踪站核验、媒体报道、仅直播展示，或作者自报。")}</p>
<div class="vf" role="group" aria-label="{t("Filter by graphics card", "按显卡筛选")}">
  <button type="button" data-f="all" aria-pressed="true">{t("All", "全部")}</button>
  <button type="button" data-f="amd" aria-pressed="false">AMD</button>
  <button type="button" data-f="nvidia" aria-pressed="false">NVIDIA</button>
</div>
{self.project_cards(ranked)}
<h2>{t("Private builds", "私有版本")}</h2>
<p>{t("No public code, so nobody outside the group can check them. Not ranked.", "没有公开代码，组外的人无法核实，所以不参与排名。")}</p>
{self.project_cards(private, ranked=False)}
<h2>{t("Takedown watch", "下架动态")}</h2>
<div class="stats">
  <div class="stat hot"><b>3,007</b><span>{t("repos disabled on 24 Nov", "11 月 24 日被下架的仓库")}</span></div>
  <div class="stat"><b>§2.3</b><span>{t("Rockstar terms cited: no reverse engineering", "援引的 Rockstar 条款：禁止逆向")}</span></div>
  <div class="stat"><b>2</b><span>{t("Take-Two DMCA notices in Nov", "11 月 Take-Two 的 DMCA 通知")}</span></div>
  <div class="stat cy"><b>{t("Private", "私有化")}</b><span>{t("where the leaders went next", "领先项目的去向")}</span></div>
</div>
<p>{t("Take-Two’s notice named Leonida, and GitHub applied it to the whole fork network. Take-Two argues the port is a derivative work and that “bring your own files” is misleading, because the only files that work are the leaked ones. Projects outside that network, like VIctory and XCL, were still online on 27 Nov.", "Take-Two 的通知点名了 Leonida，GitHub 把它执行到了整个分支网络。Take-Two 认为这个移植是衍生作品，“自备游戏文件”的说法有误导性，因为能用的只有泄露文件。不在这个网络里的项目，比如 VIctory 和 XCL，截至 11 月 27 日仍在线。")}</p>
<h2>{t("How we rank", "我们怎么评级")}</h2>
<p>{t("Seven stages, each needing the one before it. We only call a build Playable at 20 fps or more without regular crashes, which is stricter than most trackers.", "共七个阶段，每一步都以前一步为前提。只有平均 20 帧以上、不经常崩溃，我们才算“可玩”，比大多数追踪站的标准更严。")}</p>
<p>{t("The headline percentage follows the same ladder. Each stage up to “In control” adds a seventh of the bar. After that, frame rate moves a build along: 20 fps is Playable at 86%, and 30 fps, the same as the PS5, is 100%.", "首页的百分比用的是同一把尺子：到“能操控”为止，每过一个阶段前进七分之一；之后按帧数推进，20 帧到“可玩”（86%），30 帧和 PS5 一样，就是 100%。")}</p>
{self.stage_defs()}
<h2>{t("Can I try it?", "我能试试吗？")}</h2>
<p>{t("Every build needs the leaked game files, and the “ready-to-play” copies going around often carry malware.", "所有版本都需要泄露的游戏文件，网上流传的“一键可玩”版常带木马。")} <a href="{self.url("safe")}">{t("Is that download safe? →", "下载安全吗？→")}</a></p>
<script>
(function () {{
  var bs = document.querySelectorAll('.vf button'), cards = document.querySelectorAll('.pcard');
  bs.forEach(function (b) {{ b.addEventListener('click', function () {{
    var f = b.dataset.f;
    bs.forEach(function (x) {{ x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); }});
    cards.forEach(function (c) {{ c.hidden = !(f === 'all' || c.dataset.gpu.indexOf(f) > -1); }});
  }}); }});
}})();
</script>'''
        faqs = [(t("Is the unofficial GTA 6 PC port playable?", "GTA 6 民间 PC 移植能玩了吗？"), t("Roughly. The best builds run the first missions at 20–25 fps on high-end PCs; most are still far slower.", "勉强能玩。最好的版本在高端电脑上前期任务能跑 20–25 帧，大多数版本仍然慢得多。")),
                (t("What PC do the ports need?", "移植版要什么电脑？"), t("The fastest builds run on a Radeon RX 9070 XT or RX 7900 XTX with 64 GB of RAM. They use 30–46 GB of memory, far more than an official port would.", "最快的版本用的是 Radeon RX 9070 XT 或 RX 7900 XTX，配 64 GB 内存，实际占用 30–46 GB，远多于官方移植的预期。")),
                (t("Will an unofficial port beat the official PC version?", "民间版会比官方 PC 版好吗？"), t("No. An official port brings full PC settings, mouse and keyboard, GTA Online and no legal risk.", "不会。官方版会有完整的画面设置、键鼠支持、GTA Online，也没有法律风险。"))]
        return self.content_page("tracker", t("GTA 6 PC Port Tracker: Is the Unofficial Port Playable?", "GTA 6 PC 移植进度：民间版能玩了吗？"),
                                 t("Is the unofficial GTA 6 PC port playable? Frame rates, stages and takedowns for every build running the leaked Xbox version, updated daily.", "GTA 6 民间 PC 移植能玩了吗？每个泄露 Xbox 版移植的帧数、阶段和下架情况，每日更新。"),
                                 t("GTA 6 PC Port Tracker", "GTA 6 PC 移植进度"),
                                 f'<strong>{t("Roughly playable, unofficially.", "民间版：勉强能玩了。")}</strong> {t("The best builds run the first missions at 20–25 fps on high-end PCs, using the leaked Xbox files.", "最好的版本在高端电脑上前期任务能跑 20–25 帧，用的是泄露的 Xbox 版文件。")}',
                                 body, faqs=faqs, image="tail-lights.jpg", tags=[("warn", t("Playable: roughly", "可玩：勉强")), ("cy", t("Best: ~25 fps", "最高：约 25 帧"))],
                                 nexts=[("leak", t("What Cyberleek leaked", "大葱哥泄露了什么"), t("Build, EXE, timeline", "游戏包、EXE、时间线")), ("specs", t("PC specs", "配置"), t("What the ports run on", "移植版用的硬件")), ("play", t("Play on PC today", "现在怎么玩"), t("The legal way", "合法的办法"))],
                                 note=t("Sources: PortWatch VI, TechRadar, Game Rant, Notebookcheck, heise, GitHub DMCA log.", "来源：PortWatch VI、TechRadar、Game Rant、Notebookcheck、heise、GitHub DMCA 记录。"))

    def page_leak(self):
        t = self.t
        verdicts = [("ok", t("Real", "真"), t("The Xbox build and EXE exist, and ports run them into the first missions", "Xbox 版和 EXE 确实存在，移植已能跑进前几个任务")),
                    ("ok", t("Real", "真"), t("Take-Two had Leonida and 3,007 repositories taken down (GitHub’s public DMCA log)", "Take-Two 让 GitHub 下架了 Leonida 和 3,007 个仓库（GitHub 公开 DMCA 记录）")),
                    ("ok", t("Real", "真"), t("Rockstar has announced no PC version and said nothing about the leak", "Rockstar 没公布 PC 版，也没对泄露表态")),
                    ("warn", t("Unconfirmed", "待证"), t("“25 fps, playable on PC”: clips and one tracker; no outlet ran a build", "“25 帧、PC 上能玩”：来自视频和一家追踪站，没有媒体实测")),
                    ("warn", t("Unconfirmed", "待证"), t("“Multiplayer is running on PC”: one tracker, private build", "“PC 上已经能联机”：仅一家追踪站，私有版本")),
                    ("warn", t("Unconfirmed", "待证"), t("“PC version in Q1 2027”: one report, anonymous sources", "“PC 版 2027 Q1”：单一报道，匿名信源")),
                    ("bad", t("Fake", "假"), t("Any “GTA 6 PC” download, repack or ISO", "任何“GTA 6 PC 下载 / 整合版 / ISO”")),
                    ("bad", t("Fake", "假"), t("Playing on PC via Xbox Cloud or Game Pass", "用 Xbox 云游戏或 Game Pass 在 PC 上玩")),
                    ("bad", t("Fake", "假"), t("“Rockstar confirmed the leak is 100% real”", "“Rockstar 已确认泄露内容 100% 真实”"))]
        vhtml = "".join(f'<div class="verdict"><span class="tag {c}">{l}</span><div><b>{x}</b></div></div>' for c, l, x in verdicts)
        timeline = [n for n in NEWS if n["tag"] in ("leak", "port", "legal") or n["date"] == "2026-10-13"]
        body = f'''<h2 style="margin-top:0">{t("What leaked", "泄露了什么")}</h2>
<div class="big3">
  <div class="stat"><b>209 GB</b><span>{t("Xbox Series build · 19 Nov", "Xbox Series 游戏包 · 11/19")}</span></div>
  <div class="stat hot"><b>57 MB</b><span>{t("Main EXE · 23 Nov", "主程序 EXE · 11/23")}</span></div>
  <div class="stat cy"><b>1.0.2.1</b><span>{t("Game version, already patched", "游戏版本，官方已更新")}</span></div>
</div>
<p>{t("Cyberleek (an anonymous leaker) tied the EXE to a meme-coin price target. The target was never hit; the file came out anyway, 3 hours before its own countdown ended.", "Cyberleek（中文圈叫“大葱哥”，匿名泄露者）把放 EXE 和一个迷因币的市值目标绑在一起。目标没达到，文件还是在他自己的倒计时结束前 3 小时放了出来。")}</p>
<h2 id="timeline">{t("Timeline", "时间线")}</h2>
{self.news_list(timeline, detail=True)}
<h2>{t("Real, unconfirmed or fake?", "真的、待证、假的")}</h2>
<div>{vhtml}</div>
<div class="alert" id="fake-check" style="grid-template-columns:minmax(0,1fr)"><div>
  <p class="eyebrow" style="color:var(--bad)">{t("Found a “GTA 6 PC” file?", "看到“GTA 6 PC”文件了？")}</p>
  <p style="margin-top:8px">{t("It is fake. Fake installers have carried password and crypto-wallet stealers since August.", "那是假的。从 8 月起，假安装包里一直夹带盗号和盗钱包木马。")}</p>
  <a class="btn" style="margin-top:14px" href="{self.url("safe")}">{t("Check a download →", "下载自查 →")}</a>
</div></div>'''
        faqs = [(t("Can I play GTA 6 on PC with the leaked EXE?", "用泄露的 EXE 能在 PC 上玩吗？"), t("Not on its own. You’d also need the 209 GB build and a working port, and the best ports only reach 20–25 fps on high-end PCs.", "单靠它不行。还需要 209 GB 的游戏包和能跑的移植，而最好的移植也只在高端电脑上跑 20–25 帧。")),
                (t("Will the leak delay the official PC version?", "泄露会推迟官方 PC 版吗？"), t("No report links the two. After the 2022 hack, Rockstar said it expected no long-term effect on development.", "没有报道把两者联系起来。2022 年被黑客入侵后，Rockstar 曾表示对开发不会有长期影响。"))]
        return self.content_page("leak", t("GTA 6 EXE Leak Explained: What Cyberleek Released", "GTA 6 EXE 泄露解读：大葱哥到底放了什么"),
                                 t("What Cyberleek leaked: the 209 GB GTA 6 Xbox build and the EXE released on 23 November. What is real, what is unconfirmed, and what is fake.", "大葱哥（Cyberleek）泄露了什么：209 GB 的 GTA 6 Xbox 版和 11 月 23 日放出的 EXE。哪些是真的、哪些待证、哪些是假的。"),
                                 t("The GTA 6 EXE Leak, Explained", "大葱哥的 GTA 6 EXE 到底是什么"),
                                 f'<strong>{t("It is not a PC version.", "它不是 PC 版。")}</strong> {t("It is the Xbox build’s program file. It only runs inside unofficial ports, which now reach roughly playable frame rates on high-end PCs.", "那是 Xbox 版的主程序，只能在民间移植项目里跑。这些项目现在在高端电脑上已勉强能玩。")}',
                                 body, faqs=faqs, image="ocean-view-hotel.jpg", tags=[("warn", t("Rockstar: no comment", "Rockstar：未回应")), ("bad", t("Not a PC version", "不是 PC 版"))],
                                 nexts=[("tracker", t("Port tracker", "移植进度"), t("Where each project stands", "各项目到哪一步了")), ("safe", t("Is that download safe?", "下载安全吗？"), t("Red flags and what to do", "危险信号和补救")), ("release", t("PC release date", "PC 版发售日"), t("Q1 2027 vs history", "2027 Q1 还是更晚"))])

    def page_release(self):
        t = self.t
        mo = t("mo", "个月")
        hist = [("GTA III", "2001-10-22", "2002-05-21", 7), ("Vice City", "2002-10-29", "2003-05-13", 6.5), ("San Andreas", "2004-10-26", "2005-06-07", 7.5),
                ("GTA IV", "2008-04-29", "2008-12-02", 7), ("GTA V", "2013-09-17", "2015-04-14", 19), (t("Red Dead Redemption 2", "荒野大镖客 2"), "2018-10-26", "2019-11-05", 12)]
        bar_rows = [(n, m, "" if m >= 12 else "ref", f"{m:g} {mo}") for n, _, _, m in hist]
        rows = "".join(f"<tr><td><b>{n}</b></td><td class='num'>{c}</td><td class='num'>{p}</td><td class='num'>{m:g} {mo}</td></tr>" for n, c, p, m in hist)
        body = f'''<div class="big3">
  <div class="stat cy"><b>Q1 2027</b><span>{t("Reported target (GamesBeat, 4 anonymous sources)", "报道目标（GamesBeat，4 个匿名信源）")}</span></div>
  <div class="stat"><b>{t("Nov 2027", "2027.11")}</b><span>{t("If it follows RDR2's 12-month gap", "按荒野大镖客 2 的 12 个月间隔")}</span></div>
  <div class="stat hot"><b>0</b><span>{t("official dates from Rockstar", "Rockstar 官方给出的日期")}</span></div>
</div>
{self.release_chart()}
<div class="panel"><p class="eyebrow" style="color:var(--warn)">{t("Latest claim · 25 Nov", "最新说法 · 11/25")}</p>
<h3 style="margin-top:6px">{t("March 2027, together with GTA 6 Online", "2027 年 3 月，和 GTA 6 Online 一起")}</h3>
<p style="margin-top:6px">{t("A GameGPU story says PC and GTA 6 Online arrive together in March 2027, based on an anonymous post reading Take-Two’s financial forecast. Nothing from Rockstar backs it, but it fits the Q1 window.", "GameGPU 报道称 PC 版和 GTA 6 Online 将于 2027 年 3 月一起推出，依据是一个解读 Take-Two 财务预测的匿名帖子。没有 Rockstar 方面的信息支持，但和 Q1 窗口吻合。")} <a href="{self.url("a:gta-6-pc-march-2027-rumor")}">{t("Read more →", "详细 →")}</a></p></div>
<h2>{t("How long Rockstar made PC players wait", "Rockstar 以往让 PC 玩家等了多久")}</h2>
<div class="chart"><h3>{t("Console to PC gap, in months", "主机版到 PC 版的间隔（月）")}</h3><p class="sub">{t("Highlighted: the two most recent, and closest to GTA 6", "高亮：最近的两部，也是与 GTA 6 最接近的两部")}</p>
  {self.hbars(bar_rows, 20, [0, 5, 10, 15, 20])}
</div>
<div class="tbl"><table><thead><tr><th>{t("Game", "游戏")}</th><th>{t("Console", "主机版")}</th><th>PC</th><th>{t("Gap", "间隔")}</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>{t("What could move the date", "什么会影响日期")}</h2>
<div class="grid2">
  <div class="panel"><p class="eyebrow" style="color:var(--ok)">{t("Earlier", "提前")}</p><ul style="margin-top:8px;padding-left:1.1em;color:var(--ink-dim)">
    <li>{t("No PS4-style port in between, unlike GTA 5", "不像 GTA 5，中间没有跨世代移植")}</li>
    <li>{t("Q1 2027 lands in Take-Two’s current fiscal year", "2027 Q1 正好落在 Take-Two 本财年内")}</li>
    <li>{t("Pressure from unofficial ports", "民间移植带来的压力")}</li></ul></div>
  <div class="panel"><p class="eyebrow" style="color:var(--bad)">{t("Later", "推迟")}</p><ul style="margin-top:8px;padding-left:1.1em;color:var(--ink-dim)">
    <li>{t("PC must match the console quality bar first (GamesBeat)", "PC 版要先达到主机版的质量标准（GamesBeat）")}</li>
    <li>{t("GTA 5's PC version slipped three times", "GTA 5 的 PC 版推迟过三次")}</li>
    <li>{t("A huge game on very varied PC hardware", "游戏体量巨大，PC 硬件千差万别")}</li></ul></div>
</div>
{self.shot("beach-car.jpg", t("GTA 6 screenshot", "GTA 6 截图"))}'''
        faqs = [(t("Has Rockstar confirmed a PC version?", "Rockstar 确认会出 PC 版吗？"), t("No. Every mainline GTA since GTA III has come to PC eventually, but GTA 6 has no announcement yet.", "没有。GTA III 以来每部正传最后都上了 PC，但 GTA 6 目前没有任何官方消息。")),
                (t("Will the PC version be on Steam?", "PC 版会上 Steam 吗？"), t("Very likely, but maybe not on day one. RDR2 reached Steam a month after its PC launch.", "大概率会，但不一定首发。荒野大镖客 2 晚了一个月才上 Steam。")),
                (t("Was GTA 6 on PC at launch?", "GTA 6 首发有 PC 版吗？"), t("No. It launched on 19 November 2026 on PS5 and Xbox Series X|S only.", "没有。2026 年 11 月 19 日只在 PS5 和 Xbox Series X|S 上发售。")),
                (t("Has the GTA 6 PC version been delayed?", "GTA 6 PC 版延期了吗？"), t("It can’t be: Rockstar has never given the PC version a date. The console version launched on 19 November 2026 after two delays.", "谈不上延期：Rockstar 从没给过 PC 版日期。主机版在两次延期后于 2026 年 11 月 19 日发售。")),
                (t("Will the leak delay the PC version?", "泄露会推迟 PC 版吗？"), t("No report says so.", "目前没有报道这么说。"))]
        return self.content_page("release", t("GTA 6 PC Release Date: When Is GTA 6 Coming to PC?", "GTA 6 PC 版发售日：GTA 6 什么时候出 PC 版？"),
                                 t("When is GTA 6 coming to PC? A GamesBeat report says Q1 2027; Rockstar’s history points to late 2027. Both estimates, side by side.", "GTA 6 PC 版什么时候出？GamesBeat 报道称 2027 年 Q1，历史规律指向 2027 年底。两种预测并排对比。"),
                                 t("GTA 6 PC Release Date", "GTA 6 PC 版发售日"),
                                 f'<strong>{t("Not announced.", "官方未公布。")}</strong> {t("If the GamesBeat report holds, January–March 2027. If Rockstar repeats RDR2, around November 2027.", "如果 GamesBeat 的爆料属实，是 2027 年 1–3 月；如果按荒野大镖客 2 的节奏，大约 2027 年 11 月。")}',
                                 body, faqs=faqs, image="key-art.jpg", tags=[("warn", t("Unconfirmed", "未确认"))],
                                 nexts=[("specs", t("PC specs", "配置"), t("Will your PC run it?", "电脑带得动吗")), ("steam", t("Steam & Game Pass", "Steam 与 Game Pass"), t("Pre-order, price, Deck", "预购、价格、Deck")), ("tracker", t("Port tracker", "移植进度"), t("The unofficial route", "民间版进度"))],
                                 note=t("Sources: GamesBeat (13 Oct 2026), Rockstar release history.", "来源：GamesBeat（2026-10-13）、Rockstar 历代发售记录。"))

    def page_specs(self):
        t = self.t
        tiers = [("", t("Minimum", "最低"), "1080p · 30 fps", t("Low settings", "低画质"), "Ryzen 5 3600 / i5-10400", "RTX 3060 12GB / RX 6600 XT", "16GB DDR4", "NVMe SSD"),
                 ("cyan", t("Recommended", "推荐"), "1440p · 60 fps", t("High settings", "高画质"), "Ryzen 7 7700X / i5-13600K", "RTX 4070 Super / RX 7800 XT", "32GB DDR5", "PCIe 4.0 NVMe"),
                 ("pink", t("Enthusiast", "发烧"), "4K · 60 fps", t("Max ray tracing", "满光追"), "Ryzen 7 9800X3D / i7-14700K", "RTX 5080 / RX 9070 XT", "32GB DDR5", "PCIe 4.0/5.0 NVMe")]

        def spec_rows(cpu, gpu, ram, ssd):
            cell = 'style="padding:6px 0"'
            dim = 'style="padding:6px 12px 6px 0;color:var(--ink-dim);white-space:nowrap"'
            return "".join(f"<tr><td {dim}>{k}</td><td {cell}>{v}</td></tr>" for k, v in (("CPU", cpu), ("GPU", gpu), ("RAM", ram), ("SSD", ssd)))
        cards = "".join(f'<div class="panel"><p class="eyebrow">{n}</p><div class="big {c}" style="font-size:1.35rem">{r}</div><p style="margin-top:2px">{s}</p>'
                        f'<table style="margin-top:12px;font-size:.86rem"><tbody>{spec_rows(cpu, gpu, ram, ssd)}</tbody></table></div>'
                        for c, n, r, s, cpu, gpu, ram, ssd in tiers)
        ps5 = [("CPU", t("8-core Zen 2 @ 3.5 GHz", "8 核 Zen 2 @ 3.5 GHz"), t("≈ downclocked Ryzen 7 3700X", "≈ 降频版 Ryzen 7 3700X")),
               ("GPU", "RDNA 2 · 36 CU · 10.3 TF", "≈ RTX 2070 Super / RX 6700"),
               (t("Memory", "内存"), t("16 GB GDDR6, ~12.5 GB for games", "16 GB GDDR6，游戏可用约 12.5 GB"), t("Shared by CPU and GPU", "CPU 和 GPU 共用")),
               (t("Storage", "存储"), "NVMe · 5.5 GB/s", t("Built for open-world streaming", "为开放世界流式加载设计"))]
        prow = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in ps5)
        upgrade = [(t("NVMe SSD + 32 GB RAM", "NVMe 固态 + 32 GB 内存"), t("Cheap, and decides whether it runs smoothly at all", "便宜，而且决定能不能流畅跑")),
                   (t("CPU, if Zen 2 / 9th-gen Intel or older", "CPU（Zen 2 / 英特尔 9 代及更老）"), t("The 60 fps bottleneck", "60 帧的瓶颈")),
                   (t("GPU with 12 GB+ VRAM", "12 GB 以上显存的显卡"), t("Wait for official specs first", "先等官方配置"))]
        body = f'''<div class="grid3">{cards}</div>
{self.checker()}
<h2>{t("What the consoles actually do", "主机实际表现")}</h2>
<div class="stats">
  <div class="stat"><b>1440p</b><span>{t("internal resolution on PS5 and Pro", "PS5 和 Pro 的内部分辨率")}</span></div>
  <div class="stat cy"><b>30 fps</b><span>{t("cap on both, near-locked on Pro", "两者都锁 30 帧，Pro 几乎不掉")}</span></div>
  <div class="stat hot"><b>CPU</b><span>{t("is what blocks 60 fps", "才是 60 帧的瓶颈")}</span></div>
  <div class="stat"><b>~210 GB</b><span>{t("console download size (reported)", "主机版下载体积（报道）")}</span></div>
</div>
<p>{t("Digital Foundry found the PS5 Pro holds 30 fps almost perfectly and upscales to a near-4K image, while the base PS5 dips in heavy action. For 60 fps on PC, a modern 8-core CPU matters as much as the graphics card.", "Digital Foundry 实测：PS5 Pro 几乎稳定 30 帧，画面升到接近 4K；普通 PS5 在激烈场面会掉帧。想在 PC 上跑 60 帧，一颗新的 8 核 CPU 和显卡一样重要。")}</p>
<h2>{t("The PS5 baseline", "以 PS5 为基准")}</h2>
<div class="tbl"><table><thead><tr><th></th><th>PS5</th><th>{t("PC equivalent", "PC 对应")}</th></tr></thead><tbody>{prow}</tbody></table></div>
<h2>{t("What today’s unofficial builds run on", "现在的民间移植版用什么硬件")}</h2>
<div class="tbl"><table><thead><tr><th>{t("Build", "版本")}</th><th>{t("Hardware", "硬件")}</th><th>{t("Reported fps", "报道帧数")}</th><th>{t("Memory used", "内存占用")}</th><th>{t("Source", "来源")}</th></tr></thead><tbody>
<tr><td><b>Belobug</b></td><td>RX 9070 XT 16 GB · Ryzen 7 9800X3D · 64 GB</td><td class="num">~22</td><td>{t("~30 GB RAM, ~12 GB VRAM", "约 30 GB 内存、12 GB 显存")}</td><td>{self.ext("https://portwatch-vi.xyz/#effort-belobug", "PortWatch VI")}</td></tr>
<tr><td><b>AvatarManz</b></td><td>RX 7900 XTX · Core i9-12900K · 64 GB</td><td class="num">~16</td><td>{t("40–46 GB", "40–46 GB")}</td><td>{self.ext("https://portwatch-vi.xyz/#effort-avatarmanz", "PortWatch VI")}</td></tr>
<tr><td><b>CGBJ</b> <span class="tag">{t("Private", "私有")}</span></td><td>{t("16 GB VRAM card", "16 GB 显存显卡")}</td><td class="num">~25</td><td>{t("8–10 GB RAM (disputed)", "8–10 GB 内存（说法不一）")}</td><td>{self.ext("https://www.techradar.com/gaming/pc-gamers-could-see-an-unofficial-gta-6-port-sooner-rather-than-later-stable-30fps-gameplay-at-4k-has-reportedly-been-achieved", "TechRadar")} · {self.ext("https://gamerant.com/gta-6-pc-port-progress-tracker-24-fps/", "Game Rant")}</td></tr>
<tr><td><b>Kelvaroq</b></td><td>RTX 4090</td><td class="num">~10</td><td>—</td><td>{self.ext("https://portwatch-vi.xyz/#effort-kelvaroq", "PortWatch VI")}</td></tr>
<tr><td>{t("A prologue clip", "一段序章视频")}</td><td>RTX 5070 Ti · Ryzen 7 7800X3D · 32 GB</td><td class="num">1–3</td><td>—</td><td>{self.ext("https://www.notebookcheck.net/GTA-6-PC-ports-reach-gameplay-despite-Take-Two-s-GitHub-DMCA.1459752.0.html", "Notebookcheck")}</td></tr>
</tbody></table></div>
<p>{t("The ports translate Xbox code on the fly, so they lean hard on the CPU and memory: one clip showed GPU use as low as 5% while the CPU was maxed. An official port should run much better on the same PC.", "移植版是实时转译 Xbox 代码，非常吃 CPU 和内存：有一段视频里显卡占用只有 5%，CPU 却跑满了。同样的电脑跑官方版应该会好得多。")} <span class="src">{t("GPU 5% claim", "显卡 5% 的说法")}: {self.ext("https://www.notebookcheck.net/GTA-6-recomp-hits-90-progress-and-here-s-what-that-means.1460623.0.html", "Notebookcheck")}</span></p>
<h2 id="file-size">{t("How many GB is GTA 6?", "GTA 6 要多少 GB？")}</h2>
<div class="stats">
  <div class="stat cy"><b>212 GB</b><span>{t("PS5, confirmed by Rockstar", "PS5 版，Rockstar 确认")}</span></div>
  <div class="stat"><b>209 GB</b><span>{t("leaked Xbox Series build", "泄露的 Xbox Series 版")}</span></div>
  <div class="stat hot"><b>{t("TBA", "未公布")}</b><span>{t("PC version", "PC 版")}</span></div>
  <div class="stat"><b>250 GB</b><span>{t("free SSD space to plan for", "建议预留的固态空间")}</span></div>
</div>
<p>{t("PC versions of Rockstar games usually match or exceed the console install, before high-resolution textures and patches. Plan for about 250 GB on an NVMe SSD.", "Rockstar 游戏的 PC 版体积通常不小于主机版，再加上高清材质和补丁会更大。建议在 NVMe 固态上预留约 250 GB。")} <span class="src">{t("PS5 size", "PS5 体积")}: {self.ext("https://www.pushsquare.com/news/2026/11/gta-6-ps5-file-size-confirmed-to-be-212gb-physical-map-available-but-not-in-boxed-copies", "Push Square")}</span></p>
<h2>{t("If you upgrade, do it in this order", "要升级的话，按这个顺序")}</h2>
{self.numbered(upgrade, 3, "ok")}
{self.shot("neon-club.jpg", t("GTA 6 screenshot: neon-lit club", "GTA 6 截图：霓虹夜店"))}'''
        faqs = [(t("Will an 8 GB graphics card work?", "8 GB 显存够吗？"), t("Probably at low texture settings only. We recommend 12 GB or more.", "大概只能开低材质。建议 12 GB 以上。")),
                (t("Is 16 GB of RAM enough?", "16 GB 内存够吗？"), t("For the minimum tier, yes. 32 GB is the comfortable target.", "最低档够用，32 GB 更从容。")),
                (t("Can I play from a hard drive?", "机械硬盘能玩吗？"), t("Expect stutter and pop-in. The game is built around fast SSD streaming.", "会卡顿、贴图延迟。游戏是按高速固态的加载速度设计的。")),
                (t("How many GB is GTA 6 on PC?", "GTA 6 PC 版多少 GB？"), t("Not announced. The PS5 version needs 212 GB, so plan for about 250 GB free on an SSD.", "还没公布。PS5 版需要 212 GB，建议在固态上预留约 250 GB。")),
                (t("Will a gaming laptop run GTA 6?", "游戏本能跑 GTA 6 吗？"), t("A laptop with an RTX 4070 or better should reach our minimum tier; for 1440p at 60 fps you’ll want an RTX 4090 or RTX 5080 laptop. Laptop GPUs are slower than desktop cards with the same name.", "RTX 4070 及以上的游戏本应能达到最低档；想要 1440p 60 帧，需要 RTX 4090 或 RTX 5080 笔记本。笔记本显卡比同名桌面卡慢。")),
                (t("Should I buy parts now?", "现在买配件吗？"), t("No. Rockstar usually posts PC requirements 1–2 months before launch.", "不用急。Rockstar 一般在 PC 版发售前 1–2 个月公布配置。"))]
        return self.content_page("specs", t("GTA 6 PC Requirements: Can My PC Run GTA 6? (Minimum to 4K)", "GTA 6 PC 配置要求：我的电脑能跑吗？（最低到 4K）"),
                                 t("Estimated GTA 6 PC requirements for 1080p, 1440p and 4K, based on PS5 hardware and Digital Foundry’s console analysis. No official specs yet.", "基于 PS5 硬件和 Digital Foundry 主机实测，预估 GTA 6 PC 版 1080p、1440p、4K 配置。官方尚未公布。"),
                                 t("GTA 6 PC System Requirements", "GTA 6 PC 配置要求"),
                                 f'<strong>{t("No official specs yet.", "官方还没公布。")}</strong> {t("Our estimate: RTX 3060 12 GB + Ryzen 5 3600 for 1080p/30, RTX 4070 Super + Ryzen 7 7700X for 1440p/60.", "我们的预估：1080p/30 帧要 RTX 3060 12G + Ryzen 5 3600，1440p/60 帧要 RTX 4070 Super + Ryzen 7 7700X。")}',
                                 body, faqs=faqs, image="neon-club.jpg", tags=[("warn", t("Estimate", "预估"))],
                                 nexts=[("release", t("PC release date", "PC 版发售日"), t("When to expect it", "大概什么时候")), ("play", t("Play on PC today", "现在怎么玩"), t("Remote Play", "Remote Play 串流")), ("steam", t("Steam & Steam Deck", "Steam 与 Deck"), t("Store and handheld", "商店和掌机"))],
                                 note=t("Based on PS5 hardware specs, Digital Foundry’s console analysis, and earlier Rockstar PC releases.", "依据：PS5 硬件参数、Digital Foundry 主机分析、Rockstar 以往 PC 版。"))

    def page_play(self):
        t = self.t
        rows = [("y", t("PS Remote Play", "PS Remote Play"), t("Your PS5 + the game", "自己的 PS5 + 游戏"), t("Low–medium", "低到中")),
                ("y", t("Xbox app remote play", "Xbox 应用远程游玩"), t("Your Xbox Series X|S + the game", "自己的 Xbox Series X|S + 游戏"), t("Low–medium", "低到中")),
                ("y", t("Capture card", "采集卡"), t("Console + capture card", "主机 + 采集卡"), t("Lowest", "最低")),
                ("n", t("Xbox Cloud Gaming", "Xbox 云游戏"), t("Streams to Xbox consoles only", "只推流到 Xbox 主机"), "—"),
                ("n", t("GeForce Now / Game Pass PC", "GeForce Now / Game Pass PC"), t("Not available", "没有"), "—"),
                ("n", t("Emulators / leaked-build ports", "模拟器 / 泄露版移植"), t("Need leaked files; illegal and risky", "需要泄露文件，违法且有风险"), "—")]

        def steps(title, items, note):
            li = "".join(f'<li><time>{i + 1}</time><b>{a}</b><span>{b}</span></li>' for i, (a, b) in enumerate(items))
            return f'<div class="panel"><h3>{title}</h3><ol class="stepper" style="grid-template-columns:minmax(0,1fr);margin-top:12px">{li}</ol><p class="cap">{note}</p></div>'
        ps = steps(t("PS5 → PC", "PS5 → 电脑"), [
            (t("Turn on Remote Play", "开启远程游玩"), t("PS5: Settings › System › Remote Play", "PS5：设置 › 系统 › 遥控游玩")),
            (t("Allow wake from rest", "允许从待机唤醒"), t("Settings › System › Power Saving › Features in Rest Mode", "设置 › 系统 › 节能 › 待机模式中的功能")),
            (t("Install PS Remote Play", "安装 PS Remote Play"), t("Windows 10/11, sign in with the same PSN account", "Windows 10/11，登录同一个 PSN 账号")),
            (t("Plug in a DualSense", "接上 DualSense 手柄"), t("USB or Bluetooth, then launch GTA 6", "USB 或蓝牙，然后启动 GTA 6"))], t("Sony recommends 15 Mbps or more. Use a wired connection on at least one end.", "索尼建议 15 Mbps 以上，至少一端用有线。"))
        xb = steps(t("Xbox → PC", "Xbox → 电脑"), [
            (t("Enable remote features", "开启远程功能"), t("Xbox: Settings › Devices & connections › Remote features", "Xbox：设置 › 设备和连接 › 远程功能")),
            (t("Set power mode to Sleep", "电源模式设为睡眠"), t("So the console can wake on request", "这样主机才能被远程唤醒")),
            (t("Open the Xbox app on PC", "在电脑上打开 Xbox 应用"), t("Sign in with the same account", "登录同一个账号")),
            (t("Pick your console › Remote play", "选择主机 › 远程游玩"), t("Connect a controller and start GTA 6", "接上手柄，启动 GTA 6"))], t("An Xbox One cannot host GTA 6; you need a Series X or S.", "Xbox One 不能当主机，需要 Series X 或 S。"))
        cc = steps(t("Capture card", "采集卡"), [
            (t("PS5 only: turn off HDCP", "仅 PS5：关闭 HDCP"), t("Settings › System › HDMI", "设置 › 系统 › HDMI")),
            (t("Console HDMI → card → PC", "主机 HDMI → 采集卡 → 电脑"), t("Use the card’s passthrough for a TV", "可以用采集卡直通再接电视")),
            (t("Open the preview", "打开预览"), t("OBS or the card’s own app, low-latency mode", "用 OBS 或采集卡自带软件，开低延迟模式"))], t("Best latency of the three, no network needed.", "三种里延迟最低，不需要网络。"))
        body = f'''{self.yn_table(rows, ["", t("Method", "方式"), t("What you need", "需要什么"), t("Input lag", "延迟")])}
<div class="grid3">{ps}{xb}{cc}</div>
<p>{t("Xbox’s own guide confirms remote play from a Series X|S to the Xbox app on PC, and limits cloud play to Xbox consoles.", "Xbox 官方指南确认可以从 Series X|S 远程游玩到电脑上的 Xbox 应用，云游戏只支持 Xbox 主机。")} <span class="src">{self.ext("https://news.xbox.com/en-us/2026/11/23/grand-theft-auto-vi-xbox-cloud-and-remote-play/", "Xbox Wire, 23 Nov")}</span></p>
{self.shot("heist.jpg", t("GTA 6 screenshot", "GTA 6 截图"))}'''
        faqs = [(t("Can you play GTA 6 on PC through the Xbox app?", "能用 Xbox 应用在电脑上玩 GTA 6 吗？"), t("Yes, with remote play, if you own an Xbox Series X|S and the game. In the Xbox app on PC, open Accessories & remote play and connect to your console.", "可以，用远程游玩，前提是你有 Xbox Series X|S 和游戏。在电脑上的 Xbox 应用里打开“配件和远程游玩”，连上你的主机。")),
                (t("Is GTA 6 Xbox Play Anywhere?", "GTA 6 支持 Xbox Play Anywhere 吗？"), t("No. Buying the Xbox version doesn’t give you a Windows copy; you can only stream it from your console.", "不支持。买 Xbox 版不会附带 Windows 版，只能从主机串流。")),
                (t("Can I play GTA 6 on PC without a console?", "没有主机能在电脑上玩吗？"), t("No. No cloud service streams GTA 6 to PC, and there is no PC version.", "不能。没有任何云服务把 GTA 6 推流到 PC，也没有 PC 版。")),
                (t("Does Remote Play work away from home?", "出门在外能串流吗？"), t("Yes, over the internet, if your home upload speed is good enough.", "可以，走互联网，前提是家里上传带宽够。")),
                (t("Is Xbox Cloud Gaming an option on PC?", "PC 能用 Xbox 云游戏玩吗？"), t("No. Xbox confirmed GTA 6 cloud streaming is limited to Xbox consoles.", "不能。Xbox 已确认 GTA 6 云游戏只支持 Xbox 主机。"))]
        return self.content_page("play", t("How to Play GTA 6 on PC: Xbox App, PS Remote Play & Cloud", "怎么在电脑上玩 GTA 6：Xbox 应用、PS Remote Play 与云游戏"),
                                 t("The only working ways to play GTA 6 on a PC today: PS Remote Play, Xbox remote play or a capture card. Why cloud gaming and emulators don’t work.", "目前在电脑上玩 GTA 6 的可行办法：PS Remote Play、Xbox 远程游玩、采集卡。以及为什么云游戏和模拟器不行。"),
                                 t("How to Play GTA 6 on PC Right Now", "现在怎么在电脑上玩 GTA 6"),
                                 f'<strong>{t("Stream it from your own console.", "从你自己的主机串流。")}</strong> {t("PS Remote Play, Xbox remote play or a capture card all work. Nothing runs GTA 6 on a PC by itself.", "PS Remote Play、Xbox 远程游玩、采集卡都可以。没有办法让电脑自己跑 GTA 6。")}',
                                 body, faqs=faqs, image="heist.jpg", tags=[("ok", t("Works today", "现在可用"))],
                                 nexts=[("release", t("PC release date", "PC 版发售日"), t("When it comes natively", "原生 PC 版什么时候")), ("safe", t("Is that download safe?", "下载安全吗？"), t("Avoid fake installers", "别中假安装包")), ("specs", t("PC specs", "配置"), t("Get ready for the PC port", "为 PC 版做准备"))],
                                 note=t("Sources: Rockstar Games (Remote Play support), Xbox (cloud streaming limits), Sony PS Remote Play requirements.", "来源：Rockstar（Remote Play 支持说明）、Xbox（云游戏限制）、索尼 PS Remote Play 要求。"))

    def page_safe(self):
        t = self.t
        flags = [t("Called a repack, crack, ISO, beta or “early access”", "名字叫整合版、破解版、ISO、测试版或“抢先体验”"),
                 t("Ships with a “PS5 / Xbox emulator” or launcher", "附带“PS5 / Xbox 模拟器”或启动器"),
                 t("Tells you to disable antivirus", "要你先关杀毒软件"),
                 t("A small .exe / .scr / .msi that “downloads the game”", "一个很小的 .exe / .scr / .msi，说会“自动下载游戏”"),
                 t("Link from comments, Discord DMs, Telegram or Google Colab", "链接来自评论区、Discord 私信、Telegram 或 Google Colab"),
                 t("Survey, Steam login or crypto to unlock", "要填问卷、登录 Steam 或付加密货币才能解锁")]
        fhtml = "".join(f'<li><span class="ico n">✕</span><span>{f}</span></li>' for f in flags)
        camp = [(t("Aug 2026", "2026.8"), t("Fake “Extended Look” and demo sites", "假的“加长预告”和试玩网站"), t("Infostealer", "信息窃取木马"), "Malwarebytes"),
                (t("Aug 2026", "2026.8"), t("113 GB “GTA 6 PC ISO”", "113 GB 的“GTA 6 PC ISO”"), t("99.99% empty filler + a small virus", "99.99% 空数据 + 一个小病毒"), "TechRadar"),
                (t("Nov 2026", "2026.11"), t("“GTA 6 EXE” via Google Colab → ZIP", "Google Colab 上的“GTA 6 EXE” → ZIP"), t("WARDEN stealer: passwords, cookies, Steam, crypto", "WARDEN：盗密码、Cookie、Steam、加密钱包"), "Cynet / Help Net Security"),
                ("2026", t("Fake game installers", "假游戏安装包"), t("Vidar stealer", "Vidar 窃密木马"), "ESET"),
                ("2026", t("Fake game installers", "假游戏安装包"), t("RATs, stealers, Chaos ransomware", "远控木马、窃密木马、Chaos 勒索软件"), "Huntress via TechRadar")]
        crow = "".join(f"<tr><td class='num'>{a}</td><td><b>{b}</b></td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in camp)
        fix = [(t("Disconnect from the internet", "断网"), t("Stops the stealer sending more data", "阻止木马继续往外传数据")),
               (t("Run a full scan", "全盘扫描"), t("Windows Security or Malwarebytes", "Windows 安全中心或 Malwarebytes")),
               (t("Change passwords from another device", "用另一台设备改密码"), t("Email first, then Steam, Discord, banks", "先改邮箱，再改 Steam、Discord、银行")),
               (t("Move crypto to a new wallet", "把加密资产转到新钱包"), t("Assume old seed phrases are stolen", "默认旧助记词已泄露")),
               (t("Turn on 2FA everywhere", "全部开启两步验证"), t("And sign out of all sessions", "并退出所有已登录设备"))]
        body = f'''<div class="stats">
  <div class="stat hot"><b>34/68</b><span>{t("engines flagged one “GTA 6 EXE”", "某“GTA 6 EXE”被 34/68 个引擎报毒")}</span></div>
  <div class="stat"><b>99.99%</b><span>{t("of a 113 GB “ISO” was filler", "某 113 GB“ISO”是空数据")}</span></div>
  <div class="stat"><b>WARDEN</b><span>{t("stealer in a fake EXE", "假 EXE 里的窃密木马")}</span></div>
  <div class="stat"><b>Vidar</b><span>{t("stealer in fake installers", "假安装包里的窃密木马")}</span></div>
</div>
<div class="alert" style="grid-template-columns:minmax(0,1fr)"><div>
  <p class="eyebrow" style="color:var(--bad)">{t("Delete it if it matches any of these", "符合任意一条，直接删掉")}</p>
  <ul class="chk" style="margin-top:12px">{fhtml}</ul>
</div></div>
<div class="panel"><p class="eyebrow" style="color:var(--warn)">{t("Now that the ports run", "移植能跑之后")}</p>
<p style="margin-top:8px">{t("Real progress makes fake “ready-to-play GTA 6 PC” downloads more convincing, and re-uploads of the leading projects were already circulating on 22 Nov. The real projects publish source code only, never a playable game, and they all need the leaked files.", "真实的进展让“GTA 6 PC 一键可玩版”这类假下载更有迷惑性，11 月 22 日就已出现领先项目的转传版本。真正的项目只发布源代码，从不提供能直接玩的游戏，而且都需要泄露文件。")}</p></div>
<h2>{t("Known fake GTA 6 downloads", "已知的假 GTA 6 下载")}</h2>
<div class="tbl"><table><thead><tr><th>{t("When", "时间")}</th><th>{t("Bait", "诱饵")}</th><th>{t("What it installs", "实际装了什么")}</th><th>{t("Reported by", "披露方")}</th></tr></thead><tbody>{crow}</tbody></table></div>
<h2>{t("Already ran one? Do this now", "已经运行过？马上这样做")}</h2>
{self.numbered(fix, 5, "bad")}'''
        faqs = [(t("Is the Cyberleek EXE a virus?", "大葱哥放的 EXE 是病毒吗？"), t("The EXE alone doesn’t run on Windows, and re-uploaded copies are a known way malware spreads.", "单靠这个 EXE 在 Windows 上根本跑不起来，而第三方转传的版本是常见的木马传播渠道。")),
                (t("Are “GTA 6 on PC” YouTube videos real?", "YouTube 上“GTA 6 PC 实机”视频是真的吗？"), t("No verified gameplay exists. At least one viral “PC” video was exposed as a hoax.", "目前没有可证实的实机画面，至少一个爆火的“PC 版”视频已被证实是假的。")),
                (t("Where can I safely get GTA 6 for PC?", "去哪里能安全下载 PC 版？"), t("Nowhere yet. When it launches, use Steam, Epic or the Rockstar Games Launcher.", "目前哪里都没有。等正式发售后，用 Steam、Epic 或 Rockstar 启动器。"))]
        return self.content_page("safe", t("Is That GTA 6 PC Download Safe? (No. Here’s How to Tell)", "GTA 6 PC 下载安全吗？（不安全，教你识别）"),
                                 t("Every GTA 6 PC download is fake. Known malware campaigns, red flags to check, and what to do if you already ran one.", "所有 GTA 6 PC 下载都是假的。已知的木马案例、危险信号，以及中招后怎么办。"),
                                 t("Is That GTA 6 PC Download Safe?", "GTA 6 PC 下载安全吗？"),
                                 f'<strong>{t("No.", "不安全。")}</strong> {t("There is no official PC version, and the unofficial ports are only ever published as source code that needs the leaked files. Any “ready-to-play” GTA 6 PC download is a scam, and many steal passwords and crypto.", "官方没有 PC 版，民间移植也只发布源代码，而且需要泄露文件。任何“一键可玩”的 GTA 6 PC 下载都是骗局，很多会盗号、盗币。")}',
                                 body, faqs=faqs, image="tail-lights.jpg", tags=[("bad", t("All fake", "全部是假的"))],
                                 nexts=[("leak", t("EXE leak explained", "EXE 泄露解读"), t("What’s real and what isn’t", "哪些是真的")), ("play", t("Play on PC today", "现在怎么玩"), t("The legal way", "合法的办法")), ("tracker", t("Port tracker", "移植进度"), t("Unofficial progress", "民间版进度"))],
                                 note=t("Sources: Malwarebytes, TechRadar, Help Net Security, ESET, Huntress, Space4Games, PCWorld.", "来源：Malwarebytes、TechRadar、Help Net Security、ESET、Huntress、Space4Games、PCWorld。"))

    def page_steam(self):
        t = self.t
        rows = [("n", t("Steam store page", "Steam 商店页"), t("None yet", "还没有")), ("n", t("PC pre-order", "PC 预购"), t("Not possible on any store", "任何商店都不能预购")),
                ("n", t("Game Pass (any platform)", "Game Pass（任何平台）"), t("Not included", "不在库里")), ("n", t("Steam Deck", "Steam Deck"), t("No PC version to run", "没有 PC 版可跑")),
                ("n", t("PC price", "PC 版价格"), t("Not announced", "未公布"))]
        hist = [("GTA V", "2015-04-14", t("Steam + Rockstar, same day", "Steam 和 Rockstar 同日")),
                (t("Red Dead Redemption 2", "荒野大镖客 2"), "2019-11-05", t("Rockstar Launcher + Epic first; Steam on 5 Dec 2019", "先上 Rockstar 启动器和 Epic，2019-12-05 才上 Steam"))]
        hrow = "".join(f"<tr><td><b>{a}</b></td><td class='num'>{b}</td><td>{c}</td></tr>" for a, b, c in hist)
        body = f'''<div class="split">
  {self.yn_table(rows)}
  {self.shot("cover-art.jpg", t("GTA 6 cover art", "GTA 6 封面"), t("Cover art: Rockstar Games", "封面：Rockstar Games"))}
</div>
<h2>{t("GTA 6 price", "GTA 6 价格")}</h2>
<div class="tbl"><table><thead><tr><th>{t("Edition", "版本")}</th><th>PS5 / Xbox Series</th><th>PC</th></tr></thead><tbody>
<tr><td><b>{t("Standard", "标准版")}</b></td><td class="num">$79.99</td><td>{t("Not announced", "未公布")}</td></tr>
<tr><td><b>{t("Ultimate", "终极版")}</b></td><td class="num">$100</td><td>{t("Not announced", "未公布")}</td></tr>
</tbody></table></div>
<p>{t("The console prices aren’t PC prices. Rockstar hasn’t set a PC price, and there is nowhere to pre-order a PC copy.", "主机价格不等于 PC 价格。Rockstar 还没定 PC 版价格，PC 版也没有任何地方能预购。")} <span class="src">{t("Prices", "价格")}: {self.ext("https://news.xbox.com/en-us/2026/11/23/grand-theft-auto-vi-xbox-cloud-and-remote-play/", "Xbox Wire")} · {self.ext("https://kotaku.com/so-is-the-100-gta-6-ultimate-edition-actually-worth-it-2000758998", "Kotaku")}</span></p>
<h2>{t("How Rockstar launched on PC before", "Rockstar 以往的 PC 首发方式")}</h2>
<div class="tbl"><table><thead><tr><th>{t("Game", "游戏")}</th><th>{t("PC launch", "PC 发售")}</th><th>{t("Stores", "商店")}</th></tr></thead><tbody>{hrow}</tbody></table></div>
<p>{t("Expect the Rockstar Games Launcher on day one. Steam is likely, but RDR2 shows it can come a month later. Every Rockstar PC game since 2019 runs through the Rockstar launcher, even when bought on Steam.", "首发大概率会上 Rockstar 启动器。Steam 很可能有，但荒野大镖客 2 晚了一个月才上 Steam。2019 年以来 Rockstar 的 PC 游戏即使在 Steam 买，也要通过 Rockstar 启动器运行。")}</p>'''
        faqs = [(t("Can I wishlist GTA 6 on Steam?", "Steam 能加愿望单吗？"), t("No. There is no store page to wishlist yet.", "不能，目前没有商店页。")),
                (t("Will GTA 6 be on the Epic Games Store?", "GTA 6 会上 Epic 吗？"), t("Probably. RDR2 launched on the Rockstar Games Launcher and Epic first, with Steam a month later.", "大概率会。荒野大镖客 2 首发就上了 Rockstar 启动器和 Epic，Steam 晚了一个月。")),
                (t("Does GTA 6 have online multiplayer?", "GTA 6 有线上多人吗？"), t("Not yet. GTA 6 launched as a single-player game. A rumor says GTA 6 Online and the PC version arrive together in March 2027.", "还没有。GTA 6 首发只有单人模式。有传闻称 GTA 6 Online 和 PC 版会在 2027 年 3 月一起推出。")),
                (t("Will GTA 6 come to Game Pass?", "GTA 6 会进 Game Pass 吗？"), t("Not at launch. Take-Two’s CEO has reportedly ruled out day one; GTA V took years to arrive.", "首发不会。据报道 Take-Two CEO 已排除首发入库的可能；GTA V 也是过了好几年才进。")),
                (t("Will it run on Steam Deck?", "Steam Deck 能跑吗？"), t("Nothing to run yet. With consoles CPU-limited at 30 fps, a handheld will struggle.", "现在没有可跑的版本。主机都被 CPU 卡在 30 帧，掌机会很吃力。"))]
        return self.content_page("steam", t("GTA 6 Steam: Release Date, PC Pre-Order, Price & Game Pass", "GTA 6 Steam：发售日、PC 预购、价格与 Game Pass"),
                                 t("GTA 6 is not on Steam, Epic or Game Pass yet. What Rockstar’s past PC launches suggest about stores, launchers and Steam Deck.", "GTA 6 还没上 Steam、Epic 或 Game Pass。从 Rockstar 以往 PC 首发看商店、启动器和 Steam Deck。"),
                                 t("Is GTA 6 on Steam?", "GTA 6 上 Steam 了吗？"),
                                 f'<strong>{t("No.", "没有。")}</strong> {t("There is no Steam, Epic or Rockstar Launcher page, so you can’t wishlist or pre-order GTA 6 on PC.", "Steam、Epic、Rockstar 启动器都没有商店页，PC 版不能加愿望单，也不能预购。")}',
                                 body, faqs=faqs, image="cover-art.jpg", tags=[("bad", t("Not listed", "未上架"))],
                                 nexts=[("release", t("PC release date", "PC 版发售日"), t("Q1 2027 vs history", "2027 Q1 还是更晚")), ("specs", t("PC specs", "配置"), t("Will your PC run it?", "电脑带得动吗")), ("play", t("Play on PC today", "现在怎么玩"), t("Remote Play", "Remote Play 串流"))],
                                 note=t("Sources: Steam and Rockstar store listings, Take-Two statements as reported by PCGamesN.", "来源：Steam 与 Rockstar 商店页、PCGamesN 转述的 Take-Two 表态。"))

    def page_news(self):
        t = self.t
        latest = self.L(NEWS[0])[0]
        return self.content_page("news", t("GTA 6 PC News: Leaks, Ports & Release Updates", "GTA 6 PC 新闻：泄露、移植与发售动态"),
                                 t("Dated GTA 6 PC news: release reports, the Cyberleek leak, unofficial port progress, takedowns and malware warnings.", "按日期整理的 GTA 6 PC 新闻：发售爆料、大葱哥泄露、民间移植进度、下架与木马预警。"),
                                 t("GTA 6 PC News", "GTA 6 PC 新闻"),
                                 f'<strong>{t("Latest", "最新")}:</strong> {latest}', self.news_list(NEWS, detail=True), image="key-art.jpg",
                                 nexts=[("tracker", t("Port tracker", "移植进度"), t("Live project status", "项目实时进度")), ("leak", t("EXE leak explained", "EXE 泄露解读"), t("What’s real", "哪些是真的")), ("release", t("PC release date", "PC 版发售日"), t("Both estimates", "两种预测"))])

    def page_article(self, n):
        t = self.t
        key = "a:" + n["slug"]
        title, dek = self.L(n)
        paras = "".join(f"<p>{x}</p>" for x in self.L(n["body"]))
        src = n["source"]
        more = "".join(f'<li>{self.ext(u, nm)}</li>' for nm, u in n.get("more", []))
        srcs = f'<div class="srcs"><p class="eyebrow">{t("Sources", "来源")}</p><ul><li>{self.ext(src["url"], src["name"])}</li>{more}</ul></div>'
        withs = [x for x in NEWS if x.get("slug")]
        i = withs.index(n)
        others = (withs[max(0, i - 1):i] + withs[i + 1:i + 3])[:3]
        rel = "".join(f'<a href="{self.url("a:" + x["slug"])}">{self.L(x)[0]}<span>{self.date(x["date"])}</span></a>' for x in others)
        tags = {"port": ("cy", t("Port", "移植")), "leak": ("warn", t("Leak", "泄露")), "official": ("ok", t("Official", "官方")),
                "report": ("", t("Report", "报道")), "legal": ("bad", t("Legal", "法务")), "security": ("bad", t("Security", "安全"))}
        c, lbl = tags[n["tag"]]
        cta = ""
        if n.get("page"):
            pk, pen, pzh = n["page"]
            cta = f'<p><a class="btn" href="{self.url(pk)}">{t(pen, pzh)} →</a></p>'
        body = (paras + cta + srcs +
                f'<div><p class="eyebrow" style="margin-bottom:12px">{t("More news", "更多新闻")}</p><div class="next">{rel}</div></div>')
        y = n["date"][:4]
        return self.content_page(key, f"{title} | GTA6PC.org", dek, title, dek, body, image=n.get("image", "key-art.jpg"),
                                 tags=[(c, lbl), ("", self.date(n["date"]) + ("" if self.zh else " " + y))], article=n)

    # ======================= v6: FAQ hub, FPS, Online =======================
    FAQ_GROUPS = [
        (("Release", "发售"), [
            ("Is GTA 6 on PC yet?", "GTA 6 出 PC 版了吗？", "Not officially. GTA 6 launched on 19 November 2026 for PS5 and Xbox Series X|S only.", "官方没有。GTA 6 于 2026 年 11 月 19 日只在 PS5 和 Xbox Series X|S 上发售。", "home"),
            ("Will GTA 6 be on PC?", "GTA 6 会出 PC 版吗？", "Almost certainly. Every mainline GTA since GTA III has come to PC.", "几乎肯定会。GTA III 以来每部正传都上了 PC。", "release"),
            ("When is GTA 6 coming to PC?", "GTA 6 什么时候出 PC 版？", "Rockstar hasn’t said. GamesBeat reports a target of January–March 2027; Rockstar’s history points to around November 2027.", "Rockstar 没说。GamesBeat 报道的目标是 2027 年 1–3 月；按 Rockstar 以往的节奏，大约是 2027 年 11 月。", "release"),
            ("Has Rockstar confirmed a PC version?", "Rockstar 确认 PC 版了吗？", "No. There is no announcement, store page or date.", "没有。没有公告、没有商店页，也没有日期。", "release"),
            ("Will GTA 6 release on PC at the same time as consoles?", "PC 版会和主机版同时发售吗？", "It didn’t. Consoles launched on 19 November 2026 without a PC version.", "已经错过了。主机版 2026 年 11 月 19 日发售时没有 PC 版。", "release"),
            ("Has the GTA 6 PC version been delayed?", "GTA 6 PC 版延期了吗？", "It can’t be: the PC version has never had a date.", "谈不上延期：PC 版从来没有过日期。", "release"),
        ]),
        (("Buying", "购买"), [
            ("Can I pre-order GTA 6 on PC?", "PC 版能预购吗？", "No. Steam, Epic and the Rockstar Store don’t list a PC version.", "不能。Steam、Epic 和 Rockstar 商店都没有 PC 版。", "steam"),
            ("Will GTA 6 be on Steam?", "GTA 6 会上 Steam 吗？", "Very likely, maybe not on day one. RDR2 reached Steam a month after its PC launch.", "大概率会，但不一定首发。荒野大镖客 2 的 Steam 版晚了一个月。", "steam"),
            ("Will GTA 6 need the Rockstar Games Launcher?", "GTA 6 需要 Rockstar 启动器吗？", "Expect so. Every Rockstar PC game since 2019 runs through it, even when bought on Steam.", "大概率需要。2019 年以来 Rockstar 的 PC 游戏即使在 Steam 买，也要通过它运行。", "steam"),
            ("How much will GTA 6 cost on PC?", "GTA 6 PC 版多少钱？", "Not announced. On consoles the Standard Edition is $79.99 and the Ultimate Edition $100.", "未公布。主机标准版 79.99 美元，终极版 100 美元。", "steam"),
            ("Is GTA 6 on Game Pass?", "GTA 6 在 Game Pass 里吗？", "No, on any platform.", "不在，哪个平台都没有。", "steam"),
        ]),
        (("Playing now", "现在怎么玩"), [
            ("Can I play GTA 6 on PC right now?", "现在能在电脑上玩 GTA 6 吗？", "Only by streaming from your own PS5 or Xbox Series X|S with remote play, or with a capture card.", "只能用远程游玩从你自己的 PS5 或 Xbox Series X|S 串流，或者用采集卡。", "play"),
            ("Can you play GTA 6 on PC through the Xbox app?", "能用 Xbox 应用在电脑上玩吗？", "Yes, with remote play from your own Xbox Series X|S.", "可以，用远程游玩连自己的 Xbox Series X|S。", "play"),
            ("Is GTA 6 Xbox Play Anywhere?", "GTA 6 支持 Xbox Play Anywhere 吗？", "No. The Xbox version doesn’t include a Windows copy.", "不支持。Xbox 版不附带 Windows 版。", "play"),
            ("Can I play GTA 6 with Xbox Cloud Gaming on PC?", "电脑上能用 Xbox 云游戏玩吗？", "No. Cloud play is limited to Xbox One and Xbox Series consoles.", "不能。云游戏只支持 Xbox One 和 Xbox Series 主机。", "play"),
            ("Is GTA 6 on GeForce Now?", "GTA 6 上 GeForce Now 了吗？", "No. There is no PC version to stream.", "没有。没有 PC 版可以串流。", "play"),
        ]),
        (("Specs and performance", "配置与帧数"), [
            ("Can my PC run GTA 6?", "我的电脑能跑 GTA 6 吗？", "Use our checker: pick your graphics card, CPU and RAM to see which tier you land in.", "用我们的检测工具：选显卡、CPU 和内存，看看落在哪一档。", "specs"),
            ("What are the GTA 6 PC requirements?", "GTA 6 PC 配置要求是什么？", "Not announced. Our estimate: RTX 3060 12 GB and Ryzen 5 3600 for 1080p at 30 fps, RTX 4070 Super and Ryzen 7 7700X for 1440p at 60.", "官方没公布。我们的估算：1080p 30 帧要 RTX 3060 12G 和 Ryzen 5 3600，1440p 60 帧要 RTX 4070 Super 和 Ryzen 7 7700X。", "specs"),
            ("How many GB is GTA 6?", "GTA 6 多少 GB？", "212 GB on PS5. The PC size isn’t announced; plan for about 250 GB.", "PS5 版 212 GB。PC 版体积未公布，建议预留约 250 GB。", "specs"),
            ("Will GTA 6 run at 60 fps on PC?", "PC 版能跑 60 帧吗？", "It should on a recommended-tier PC. Consoles are capped at 30.", "推荐档配置应该可以。主机被锁在 30 帧。", "fps"),
            ("Will GTA 6 run on Windows 10?", "Windows 10 能玩吗？", "Not announced. Microsoft ended Windows 10 support in October 2025, so Windows 11 is the safer bet.", "未公布。微软已于 2025 年 10 月停止支持 Windows 10，用 Windows 11 更稳妥。", "specs"),
            ("Will GTA 6 run on Steam Deck?", "Steam Deck 能跑吗？", "There is no PC version yet, and consoles already need their full CPU for 30 fps.", "还没有 PC 版，而且主机要用满 CPU 才能跑 30 帧。", "specs"),
        ]),
        (("Online", "线上模式"), [
            ("Does GTA 6 have online multiplayer?", "GTA 6 有线上多人吗？", "Not yet. It launched as a single-player game.", "还没有。首发只有单人模式。", "online"),
            ("Will GTA 6 Online be on PC?", "GTA 6 Online 会上 PC 吗？", "Very likely when the PC version launches, as with GTA Online and Red Dead Online. A rumor puts both in March 2027.", "大概率会随 PC 版一起上线，GTA Online 和 Red Dead Online 都是这样。有传闻说两者在 2027 年 3 月一起推出。", "online"),
            ("Will GTA 6 have crossplay between PC and consoles?", "GTA 6 支持 PC 和主机跨平台联机吗？", "Not announced, and Rockstar’s online games have never had it.", "未公布，Rockstar 的线上游戏从来没有过跨平台联机。", "online"),
        ]),
        (("Unofficial ports and safety", "民间移植与安全"), [
            ("Is the unofficial GTA 6 PC port playable?", "民间 PC 移植能玩了吗？", "Roughly. The best builds run the first missions at 20–25 fps on high-end PCs, using the leaked Xbox files.", "勉强能玩。最好的版本在高端电脑上前期任务能跑 20–25 帧，用的是泄露的 Xbox 版文件。", "tracker"),
            ("Is the Cyberleek EXE a PC version?", "大葱哥放的 EXE 是 PC 版吗？", "No. It’s the Xbox build’s program file and only runs inside the unofficial ports.", "不是。那是 Xbox 版的主程序，只能在民间移植里跑。", "leak"),
            ("Will Take-Two shut the ports down?", "Take-Two 会下架这些移植吗？", "It already started: a DMCA notice took down Leonida and 3,007 repositories on 24 November.", "已经开始了：11 月 24 日的 DMCA 通知下架了 Leonida 和 3,007 个仓库。", "tracker"),
            ("Is any GTA 6 PC download safe?", "有安全的 GTA 6 PC 下载吗？", "No. “Ready-to-play” GTA 6 PC downloads are scams, and many carry password and crypto stealers.", "没有。“一键可玩”的 GTA 6 PC 下载都是骗局，很多带盗号、盗币木马。", "safe"),
        ]),
    ]

    def page_faq(self):
        t = self.t
        links = {"home": t("Status", "状态"), "release": t("Release date", "发售日"), "steam": t("Steam & price", "Steam 与价格"), "play": t("Play on PC now", "现在怎么玩"),
                 "specs": t("PC requirements", "配置要求"), "fps": t("FPS", "帧数"), "online": t("GTA 6 Online", "GTA 6 Online"), "tracker": t("Port tracker", "移植进度"),
                 "leak": t("EXE leak", "EXE 泄露"), "safe": t("Download safety", "下载安全")}
        jump, groups, schema = [], [], []
        for gi, ((gen, gzh), qs) in enumerate(self.FAQ_GROUPS):
            gid = f"g{gi + 1}"
            jump.append(f'<a href="#{gid}">{t(gen, gzh)}</a>')
            items = []
            for i, (qen, qzh, aen, azh, pk) in enumerate(qs):
                q, a = t(qen, qzh), t(aen, azh)
                schema.append((q, a))
                items.append(f'<details{" open" if gi == 0 and i == 0 else ""}><summary>{escape(q)}</summary><p>{a} <a href="{self.url(pk)}">{links[pk]} →</a></p></details>')
            groups.append(f'<h2 id="{gid}">{t(gen, gzh)}</h2><div class="faq">{"".join(items)}</div>')
        n = len(schema)
        body = f'<nav class="vf jump" aria-label="{t("Sections", "分类")}">{"".join(jump)}</nav>' + "".join(groups)
        return self.content_page("faq", t("GTA 6 PC FAQ: 30 Answers on Release, Steam, Specs & Ports", "GTA 6 PC 常见问题：发售、Steam、配置与移植 30 问"),
                                 t("Short answers to the most-asked GTA 6 PC questions: release date, Steam and price, the Xbox app, requirements, 60 fps, GTA 6 Online and the unofficial ports.", "GTA 6 PC 最常被问到的问题，一句话回答：发售日、Steam 与价格、Xbox 应用、配置、60 帧、GTA 6 Online 和民间移植。"),
                                 t("GTA 6 PC FAQ", "GTA 6 PC 常见问题"),
                                 f'<strong>{n} {t("questions, one-line answers.", "个问题，一句话回答。")}</strong> {t("Each one links to the page with the full detail.", "每条都链到有完整内容的页面。")}',
                                 body, image="pool.jpg", schema_faqs=schema,
                                 nexts=[("home", t("Is GTA 6 on PC?", "有 PC 版吗"), t("The live status", "实时状态")), ("fps", t("GTA 6 FPS", "GTA 6 帧数"), t("30, 60 and what PC gets", "30 帧、60 帧与 PC")), ("online", t("GTA 6 Online on PC", "GTA 6 Online 与 PC"), t("Multiplayer and crossplay", "多人与跨平台"))])

    def page_fps(self):
        t = self.t
        r = STATUS["race"]
        rows = [(t("PS5", "PS5"), 30, "ref", "30 fps"), (t("PS5 Pro", "PS5 Pro"), 30, "ref", "30 fps"),
                (t("Jailbroken PS5 (patch)", "破解版 PS5（补丁）"), 40, "warn", "~40 fps"), (t("Jailbroken PS5 Pro (patch)", "破解版 PS5 Pro（补丁）"), 45, "warn", "45+ fps"),
                (t("Unofficial PC port, public", "民间 PC 移植 · 公开"), r["best_public_fps"], "", f'~{r["best_public_fps"]} fps'),
                (t("Unofficial PC port, private", "民间 PC 移植 · 私有"), r["best_fps"], "", f'~{r["best_fps"]} fps'),
                (t("Official PC, recommended tier", "官方 PC · 推荐档"), 60, "est", t("60 fps (our estimate)", "60 帧（我们的估算）"))]
        chart = (f'<div class="chart"><h3>{t("GTA 6 frame rates side by side", "GTA 6 各平台帧数对比")}</h3>'
                 f'<p class="sub">{t("Frames per second in gameplay. Striped bar = our estimate.", "游戏中的每秒帧数。斜纹 = 我们的估算。")}</p>'
                 + self.hbars(rows, 60, [0, 15, 30, 45, 60], (30, t("console cap", "主机上限"))) + "</div>")
        tiers = [(t("Minimum", "最低"), "1080p · 30 fps", "RTX 3060 12GB / RX 6600 XT", "Ryzen 5 3600 / i5-10400"),
                 (t("Recommended", "推荐"), "1440p · 60 fps", "RTX 4070 Super / RX 7800 XT", "Ryzen 7 7700X / i5-13600K"),
                 (t("Enthusiast", "发烧"), "4K · 60 fps", "RTX 5080 / RX 9070 XT", "Ryzen 7 9800X3D / i7-14700K")]
        trs = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in tiers)
        body = f'''<div class="stats">
  <div class="stat"><b>30</b><span>{t("fps cap on PS5 and PS5 Pro", "PS5 和 Pro 的帧数上限")}</span></div>
  <div class="stat hot"><b>~{r["best_fps"]}</b><span>{t("best unofficial PC port", "最好的民间 PC 移植")}</span></div>
  <div class="stat"><b>40–45+</b><span>{t("jailbroken PS5 with a patch", "破解版 PS5 打补丁后")}</span></div>
  <div class="stat cy"><b>60</b><span>{t("official PC, recommended tier (estimate)", "官方 PC 推荐档（估算）")}</span></div>
</div>
{chart}
<h2>{t("Why consoles are stuck at 30 fps", "主机为什么被锁在 30 帧")}</h2>
<p>{t("Rockstar locks GTA 6 to 30 fps on every console, and there is no performance mode. Digital Foundry traced the limit to the CPU: the dense traffic and crowds keep the processor busy, and the PS5 Pro only adds a small CPU bump over the base PS5. It calls 60 fps on current consoles extremely unlikely.", "Rockstar 在所有主机上都把 GTA 6 锁在 30 帧，没有性能模式。Digital Foundry 认为瓶颈在 CPU：密集的车流和人群让处理器满负荷，而 PS5 Pro 的 CPU 只比普通 PS5 提升了一点。它认为现世代主机跑 60 帧可能性极低。")} <span class="src">{self.ext("https://www.pcgamer.com/games/grand-theft-auto/gta-6-looks-gorgeous-and-seeing-it-run-at-a-stable-30-fps-on-ageing-ps5-pro-hardware-makes-me-hopeful-for-pc-performance/", "PC Gamer")} · {self.ext("https://techradar.com/gaming/analysts-say-getting-gta-6-to-run-at-60fps-is-extremely-unlikely-on-console-hardware-as-rockstar-confirms-30fps-limit", "TechRadar")}</span></p>
<p>{t("A patch for jailbroken consoles removes the cap and reaches about 40 fps on a base PS5 and above 45 on a PS5 Pro, which shows how much headroom the 30 fps lock leaves.", "破解主机上的补丁解除了上限，普通 PS5 约 40 帧，PS5 Pro 超过 45 帧，可见 30 帧锁留下了不少余量。")} <a href="{self.url("a:gta-6-ps5-30-fps-cap-unlocked")}">{t("Read more →", "详细 →")}</a></p>
<h2>{t("What it takes to hit 60 fps on PC", "PC 上跑 60 帧需要什么")}</h2>
<p>{t("Because the game leans so hard on the CPU, 60 fps needs a modern 8-core processor as much as a strong graphics card. Our estimate by tier:", "因为这款游戏非常吃 CPU，想跑 60 帧，一颗新的 8 核处理器和显卡一样重要。按档位估算：")}</p>
<div class="tbl"><table><thead><tr><th>{t("Tier", "档位")}</th><th>{t("Target", "目标")}</th><th>GPU</th><th>CPU</th></tr></thead><tbody>{trs}</tbody></table></div>
<p><a class="btn" href="{self.url("specs", anchor="checker")}">{t("Check your PC →", "检测你的电脑 →")}</a></p>
<h2>{t("DLSS, FSR and frame generation", "DLSS、FSR 和插帧")}</h2>
<p>{t("Rockstar hasn’t announced PC features yet. Its last two PC releases, Red Dead Redemption 2 and GTA V Enhanced, both support NVIDIA DLSS and AMD FSR upscaling, so expect the same for GTA 6. Upscaling will matter most at 1440p and 4K.", "Rockstar 还没公布 PC 版的画面功能。它最近的两款 PC 作品，荒野大镖客 2 和 GTA V 增强版，都支持 NVIDIA DLSS 和 AMD FSR 超分，GTA 6 大概率也会有。在 1440p 和 4K 下，超分最关键。")}</p>
<h2>{t("Frame rates in the unofficial ports", "民间移植的帧数")}</h2>
<p>{t("The best unofficial builds reach 20–25 fps in the first missions on high-end AMD PCs; most are still in single digits. They translate Xbox code on the fly, so they are far slower than an official port will be.", "最好的民间版本在高端 AMD 电脑上前期任务能跑 20–25 帧，大多数还只有个位数。它们是实时转译 Xbox 代码，比官方移植慢得多。")} <a href="{self.url("tracker")}">{t("Port tracker →", "移植进度 →")}</a></p>'''
        faqs = [(t("Is GTA 6 60 fps on PS5?", "GTA 6 在 PS5 上有 60 帧吗？"), t("No. It runs at 30 fps on PS5 and PS5 Pro, with no performance mode.", "没有。PS5 和 PS5 Pro 都是 30 帧，没有性能模式。")),
                (t("Is there a 60 fps mode on PS5 Pro?", "PS5 Pro 有 60 帧模式吗？"), t("No. The Pro holds 30 fps more steadily and looks sharper, but it is still capped at 30.", "没有。Pro 的 30 帧更稳、画面更清晰，但仍然锁 30 帧。")),
                (t("Will GTA 6 run at 60 fps on PC?", "GTA 6 PC 版能跑 60 帧吗？"), t("It should on a recommended-tier PC: roughly an RTX 4070 Super with a Ryzen 7 7700X at 1440p.", "推荐档的电脑应该可以：1440p 下大约是 RTX 4070 Super 配 Ryzen 7 7700X。")),
                (t("Will the PC version have an fps cap?", "PC 版会锁帧吗？"), t("Not announced. Rockstar’s PC versions of GTA V and Red Dead Redemption 2 let you run above 60 fps.", "未公布。Rockstar 的 GTA V 和荒野大镖客 2 PC 版都能跑到 60 帧以上。"))]
        return self.content_page("fps", t("GTA 6 FPS: 30 fps Cap, 60 fps on PC and Port Frame Rates", "GTA 6 帧数：30 帧上限、PC 能否 60 帧与移植帧数"),
                                 t("GTA 6 runs at 30 fps on PS5 and PS5 Pro. What it takes to hit 60 fps on PC, how far jailbroken consoles and unofficial ports get, and DLSS/FSR.", "GTA 6 在 PS5 和 PS5 Pro 上都是 30 帧。PC 上跑 60 帧需要什么配置，破解主机和民间移植能跑多少帧，以及 DLSS/FSR。"),
                                 t("GTA 6 FPS", "GTA 6 帧数"),
                                 f'<strong>{t("30 fps on every console.", "所有主机都是 30 帧。")}</strong> {t("On PC, a recommended-tier build should reach 60 fps at 1440p. The unofficial ports run at 20–25 fps today.", "PC 上推荐档的配置应能在 1440p 跑到 60 帧。民间移植目前是 20–25 帧。")}',
                                 body, faqs=faqs, image="sunset-art.jpg", tags=[("cy", t("PC 60 fps: estimate", "PC 60 帧：估算"))],
                                 nexts=[("specs", t("PC requirements", "配置要求"), t("Check your PC", "检测你的电脑")), ("tracker", t("Port tracker", "移植进度"), t("Unofficial build fps", "民间版帧数")), ("release", t("PC release date", "PC 版发售日"), t("When it comes", "什么时候出"))],
                                 note=t("Sources: Digital Foundry via PC Gamer, TechRadar, Notebookcheck, PortWatch VI.", "来源：Digital Foundry（经 PC Gamer）、TechRadar、Notebookcheck、PortWatch VI。"))

    def page_online(self):
        t = self.t
        rows = [(t("GTA V → GTA Online", "GTA V → GTA Online"), 14, "ref", t("14 days", "14 天")),
                (t("RDR2 → Red Dead Online beta", "荒野大镖客 2 → Red Dead Online 测试版"), 32, "ref", t("32 days", "32 天")),
                (t("GTA 6 → online mode, so far", "GTA 6 → 线上模式，目前"), 8, "", t("8 days, none yet", "8 天，还没有")),
                (t("GTA 6 Online, rumored March 2027", "GTA 6 Online，传闻 2027 年 3 月"), 120, "est", t("~100–130 days", "约 100–130 天"))]
        chart = (f'<div class="chart"><h3>{t("Days from launch to online mode", "从发售到线上模式隔了几天")}</h3>'
                 f'<p class="sub">{t("Striped bar = rumor, not confirmed.", "斜纹 = 传闻，未确认。")}</p>' + self.hbars(rows, 140, [0, 35, 70, 105, 140]) + "</div>")
        hist = [("GTA V", t("17 Sep 2013", "2013-09-17"), t("1 Oct 2013", "2013-10-01"), t("14 Apr 2015, same day as GTA V PC", "2015-04-14，与 GTA V PC 版同日")),
                (t("Red Dead Redemption 2", "荒野大镖客 2"), t("26 Oct 2018", "2018-10-26"), t("27 Nov 2018 (beta)", "2018-11-27（测试版）"), t("5 Nov 2019, same day as RDR2 PC", "2019-11-05，与荒野大镖客 2 PC 版同日")),
                ("GTA 6", t("19 Nov 2026", "2026-11-19"), t("Not yet", "还没有"), t("Not announced", "未公布"))]
        trs = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in hist)
        body = f'''<div class="stats">
  <div class="stat hot"><b>{t("None", "无")}</b><span>{t("online mode today, any platform", "目前任何平台都没有线上模式")}</span></div>
  <div class="stat"><b>{t("Mar 2027", "2027.3")}</b><span>{t("rumored for Online and PC", "传闻中 Online 与 PC 版时间")}</span></div>
  <div class="stat"><b>{t("Never", "从未")}</b><span>{t("PC–console crossplay in Rockstar online games", "Rockstar 线上游戏的 PC–主机跨平台")}</span></div>
  <div class="stat cy"><b>{t("Private", "私有")}</b><span>{t("unofficial multiplayer demo on PC", "PC 上的民间联机演示")}</span></div>
</div>
{chart}
<h2>{t("GTA 6 launched single-player only", "GTA 6 首发只有单人模式")}</h2>
<p>{t("Xbox’s store listing calls GTA 6 “a single-player experience”, and the PlayStation listing names no multiplayer modes. That’s a change from GTA V and RDR2, whose online modes followed within about a month.", "Xbox 商店写明 GTA 6 是“单人游戏体验”，PlayStation 商店也没有列出多人模式。这和 GTA V、荒野大镖客 2 不同，那两款的线上模式都在发售后一个月左右上线。")} <span class="src">{self.ext("https://news.xbox.com/en-us/2026/11/23/grand-theft-auto-vi-xbox-cloud-and-remote-play/", "Xbox Wire")} · {self.ext("https://shattered.io/gta-6-pc-march-2027-gamegpu-leak-zero-rockstar-confirmations-nov-25/", "Shattered")}</span></p>
<h2>{t("When GTA 6 Online could come to PC", "GTA 6 Online 什么时候会上 PC")}</h2>
<p>{t("Rockstar has brought its online modes to PC on the same day as the PC game both times. A 25 November rumor, based on an anonymous reading of Take-Two’s forecasts, says GTA 6 Online and the PC version launch together in March 2027.", "Rockstar 前两次都是 PC 版发售当天就带上线上模式。11 月 25 日有传闻称，根据对 Take-Two 财务预测的匿名解读，GTA 6 Online 和 PC 版会在 2027 年 3 月一起推出。")} <a href="{self.url("a:gta-6-pc-march-2027-rumor")}">{t("Read more →", "详细 →")}</a></p>
<div class="tbl"><table><thead><tr><th>{t("Game", "游戏")}</th><th>{t("Console launch", "主机发售")}</th><th>{t("Online mode", "线上模式")}</th><th>{t("Online on PC", "线上模式上 PC")}</th></tr></thead><tbody>{trs}</tbody></table></div>
<h2>{t("Crossplay between PC and consoles", "PC 与主机跨平台联机")}</h2>
<p>{t("Not announced. Neither GTA Online nor Red Dead Online has ever let PC and console players play together. Rockstar has, however, let players move their GTA Online characters to new platforms, including to PC in 2015.", "未公布。GTA Online 和 Red Dead Online 都从未支持 PC 和主机玩家一起玩。不过 Rockstar 允许过把 GTA Online 角色转移到新平台，2015 年就开放过转到 PC。")}</p>
<h2>{t("Unofficial multiplayer on PC", "PC 上的民间联机")}</h2>
<p>{t("A private group working from a leaked-build port has shown players, cars and proximity voice chat at 25–30 fps. It’s their own networking, not Rockstar’s GTA Online, and the build isn’t public.", "一个基于泄露版移植的私有小组展示了玩家、车辆和近距离语音，帧数 25–30。这是他们自己做的联网，不是 Rockstar 的 GTA Online，版本也没公开。")} <a href="{self.url("a:gta-6-pc-multiplayer-private-build")}">{t("Read more →", "详细 →")}</a></p>
{self.shot("collage.jpg", t("GTA 6 cover collage", "GTA 6 封面拼贴图"), t("Artwork: Rockstar Games", "美术：Rockstar Games"))}'''
        faqs = [(t("Is GTA 6 multiplayer?", "GTA 6 有多人模式吗？"), t("Not yet. It launched as a single-player game on PS5 and Xbox Series X|S.", "还没有。PS5 和 Xbox Series X|S 版首发只有单人模式。")),
                (t("When is GTA 6 Online coming out?", "GTA 6 Online 什么时候出？"), t("Rockstar hasn’t said. A rumor points to March 2027, together with the PC version.", "Rockstar 没说。有传闻称 2027 年 3 月，和 PC 版一起。")),
                (t("Will GTA 6 Online be on PC?", "GTA 6 Online 会上 PC 吗？"), t("Very likely. GTA Online and Red Dead Online both came to PC on the PC launch day.", "大概率会。GTA Online 和 Red Dead Online 都是 PC 版发售当天就上了 PC。")),
                (t("Will GTA 6 have crossplay?", "GTA 6 会有跨平台联机吗？"), t("Not announced. Rockstar’s online games have never had PC–console crossplay.", "未公布。Rockstar 的线上游戏从没有过 PC 与主机跨平台。")),
                (t("Can I play GTA 6 co-op?", "GTA 6 能合作玩吗？"), t("No. There is no co-op or online mode in the released game.", "不能。目前发售的版本没有合作或线上模式。"))]
        return self.content_page("online", t("GTA 6 Online on PC: Multiplayer, Crossplay & Release Date", "GTA 6 Online 与 PC：多人、跨平台与上线时间"),
                                 t("GTA 6 launched single-player only. When GTA 6 Online could reach PC, whether it will have crossplay, how GTA V and RDR2 handled it, and the unofficial PC multiplayer demo.", "GTA 6 首发只有单人模式。GTA 6 Online 什么时候可能上 PC、会不会跨平台、GTA V 和荒野大镖客 2 是怎么做的，以及 PC 上的民间联机演示。"),
                                 t("GTA 6 Online on PC", "GTA 6 Online 与 PC"),
                                 f'<strong>{t("No online mode yet, on any platform.", "目前任何平台都没有线上模式。")}</strong> {t("GTA 6 launched single-player only. A rumor puts GTA 6 Online and the PC version together in March 2027.", "GTA 6 首发只有单人模式。有传闻称 GTA 6 Online 和 PC 版将在 2027 年 3 月一起推出。")}',
                                 body, faqs=faqs, image="collage.jpg", tags=[("warn", t("Online: not yet", "线上：还没有"))],
                                 nexts=[("release", t("PC release date", "PC 版发售日"), t("Q1 2027 vs history", "2027 Q1 还是更晚")), ("steam", t("Steam & price", "Steam 与价格"), t("Stores and editions", "商店与版本")), ("tracker", t("Port tracker", "移植进度"), t("Unofficial builds", "民间版本"))],
                                 note=t("Sources: Xbox Wire, Shattered, GameGPU, PortWatch VI; Rockstar launch history.", "来源：Xbox Wire、Shattered、GameGPU、PortWatch VI；Rockstar 历代发售记录。"))

    def page_legal(self, key):
        t = self.t
        if key == "privacy":
            h1 = t("Privacy Policy", "隐私政策")
            body = f'''<p>{t("GTA6PC.org does not ask you to create an account and does not collect your name, email or payment details.", "GTA6PC.org 不需要注册，也不收集你的姓名、邮箱或支付信息。")}</p>
<p>{t("Our hosting provider (Vercel) keeps standard server logs. If we use analytics or advertising, those services may set cookies and receive your IP address and browser details; you can block them in your browser settings.", "我们的托管服务商（Vercel）会记录标准服务器日志。如果本站使用统计或广告服务，这些服务可能会设置 Cookie 并获取你的 IP 和浏览器信息，你可以在浏览器设置中屏蔽。")}</p>'''
        else:
            h1 = t("Terms of Use", "使用条款")
            body = f'''<p>{t("GTA6PC.org is an unofficial fan site. It is not affiliated with Rockstar Games or Take-Two Interactive. Grand Theft Auto and related marks belong to their owners.", "GTA6PC.org 是非官方粉丝站，与 Rockstar Games、Take-Two 无关。Grand Theft Auto 及相关商标归其所有者。")}</p>
<p>{t("Release dates and system requirements here are estimates unless marked official. We do not host, link or help you obtain leaked or pirated game files.", "除非标注为官方，本站的发售日和配置均为预估。本站不提供、不链接、也不协助获取任何泄露或盗版游戏文件。")}</p>
<p>{t("Content is provided as is. Official announcements from Rockstar always take precedence.", "内容按现状提供，一切以 Rockstar 官方公告为准。")}</p>'''
        return self.content_page(key, f"{h1} | GTA6PC.org", h1, h1, h1, body)

    def page_404(self):
        t = self.t
        body = f'''{self.header("home")}
<main><section class="page-head"><div class="wrap">
  <h1>{t("Page not found", "页面不存在")}</h1>
  <p class="answer">{t("This page doesn’t exist. Neither does an official GTA 6 PC version, yet.", "这个页面不存在。GTA 6 的官方 PC 版也还不存在。")}</p>
  <div class="ctas"><a class="btn primary" href="{self.url("home")}">{t("Is GTA 6 on PC?", "有 PC 版吗？")}</a><a class="btn" href="{self.url("tracker")}">{t("Port tracker", "移植进度")}</a></div>
</div></section></main>
{self.footer()}'''
        return self.doc("home", t("Page not found | GTA6PC.org", "页面不存在 | GTA6PC.org"), "404", body, noindex=True)

    def all_pages(self):
        return {"home": self.page_home(), "release": self.page_release(), "specs": self.page_specs(), "tracker": self.page_tracker(),
                "leak": self.page_leak(), "play": self.page_play(), "safe": self.page_safe(), "steam": self.page_steam(),
                "news": self.page_news(), "privacy": self.page_legal("privacy"), "terms": self.page_legal("terms"),
                "faq": self.page_faq(), "fps": self.page_fps(), "online": self.page_online()}


def rss(s, lang):
    from datetime import datetime
    items = []
    for n in NEWS:
        link = SITE + (s.url("a:" + n["slug"]) if n.get("slug") else s.url("news"))
        y, m, d = (int(x) for x in n["date"].split("-"))
        pub = datetime(y, m, d, 12).strftime("%a, %d %b %Y %H:%M:%S +0000")
        items.append(f"<item><title>{escape(s.L(n)[0])}</title><link>{link}</link><guid isPermaLink=\"false\">{link}#{n['date']}</guid>"
                     f"<pubDate>{pub}</pubDate><description>{escape(s.L(n)[1])}</description></item>")
    title = s.t("GTA 6 PC News | GTA6PC.org", "GTA 6 PC 新闻 | GTA6PC.org")
    desc = s.t("GTA 6 PC release, port and leak news", "GTA 6 PC 发售、移植与泄露新闻")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
            f"<title>{escape(title)}</title><link>{SITE + s.url('news')}</link><description>{escape(desc)}</description>"
            f"<language>{LANGS[lang]['code'].lower()}</language>\n" + "\n".join(items) + "\n</channel></rss>\n")


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build(mode):
    out = ROOT / ("out" if mode == "prod" else "preview")
    if out.exists():
        shutil.rmtree(out)
    for lang, cfg in LANGS.items():
        s = Site(mode, lang)
        dirp = (cfg["prefix"] + "/") if cfg["prefix"] else ""
        for key, html in s.all_pages().items():
            slug = PAGES[key]
            rel = (dirp + (slug + ".html" if slug else "index.html")) if mode == "prod" else s.url(key)
            write(out / rel, html)
        for n in NEWS:
            if n.get("slug"):
                rel = (dirp + "news/" + n["slug"] + ".html") if mode == "prod" else s.url("a:" + n["slug"])
                write(out / rel, s.page_article(n))
        if mode == "prod":
            write(out / (dirp + "404.html"), s.page_404())
            write(out / (dirp + "news/feed.xml"), rss(s, lang))
    if mode == "prod":
        shutil.copytree(ROOT / "static", out / "static")
        # Files kept from the old deployment (Neon Bay at /play/, og-image.png, favicon...) live in legacy/.
        legacy = ROOT / "legacy"
        if legacy.is_dir():
            shutil.copytree(legacy, out, dirs_exist_ok=True, ignore=shutil.ignore_patterns("README.md"))
        urls = []
        for key in list(PAGES) + ["a:" + n["slug"] for n in NEWS if n.get("slug")]:
            alts = {l: SITE + Site("prod", l).url(key) for l in LANGS}
            links = "".join(f'<xhtml:link rel="alternate" hreflang="{LANGS[l]["code"]}" href="{u}"/>' for l, u in alts.items())
            for loc in alts.values():
                urls.append(f'  <url><loc>{loc}</loc><lastmod>{STATUS["updated"][:10]}</lastmod>{links}</url>')
        write(out / "sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
              + "\n".join(urls) + "\n</urlset>\n")
        write(out / "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    else:
        shutil.copy(ROOT / "static" / "site.css", out / "site.css")
        shutil.copytree(ROOT / "static" / "img", out / "img")
    miss = {l: len(v) for l, v in MISSING.items() if v}
    if miss:
        I18N.mkdir(exist_ok=True)
        for l, v in MISSING.items():
            (I18N / f"_missing_{l}.json").write_text(json.dumps(sorted(v), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"built {mode} -> {out.relative_to(ROOT)} ({sum(1 for _ in out.rglob('*.html'))} html files)" + (f"; untranslated strings: {miss}" if miss else ""))


if __name__ == "__main__":
    build("preview" if len(sys.argv) > 1 and sys.argv[1] == "preview" else "prod")
