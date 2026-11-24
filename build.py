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
NEWS = sorted(json.loads((DATA / "news.json").read_text(encoding="utf-8")), key=lambda n: n["date"], reverse=True)

# key -> slug ('' = home). Slugs for release-date and pc-specs match the old site’s URLs.
PAGES = {
    "home": "", "release": "release-date", "specs": "pc-specs", "tracker": "pc-port-tracker",
    "leak": "cyberleek-leak", "play": "how-to-play-gta-6-on-pc", "safe": "is-gta-6-pc-download-safe",
    "steam": "steam", "news": "news", "privacy": "privacy", "terms": "terms",
}
IMG = {  # file: (width, height)
    "hero-vice-city-night.jpg": (1920, 1080), "beach-car.jpg": (1280, 720), "heist.jpg": (1280, 512),
    "tail-lights.jpg": (1306, 522), "ocean-view-hotel.jpg": (1280, 720), "cover-art.jpg": (1000, 562),
    "neon-club.jpg": (1600, 640), "key-art.jpg": (1600, 900),
}
MONTHS_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
Q = '"'


def cur_attr(on):
    return ' aria-current="page"' if on else ""


class Site:
    def __init__(self, mode, lang):
        self.mode, self.lang, self.zh = mode, lang, lang == "zh"

    # ---------- helpers ----------
    def t(self, en, zh):
        return zh if self.zh else en

    def url(self, key, lang=None, anchor=""):
        lang = lang or self.lang
        slug = PAGES[key]
        if self.mode == "prod":
            p = ("/zh" + ("/" + slug if slug else "")) if lang == "zh" else "/" + slug
        else:
            if not slug:
                p = "zh.html" if lang == "zh" else "index.html"
            else:
                p = ("zh-" if lang == "zh" else "") + slug + ".html"
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
        return f"{int(m)}/{int(d)}" if self.zh else f"{int(d)} {MONTHS_EN[int(m) - 1]}"

    def shot(self, name, alt, credit=None):
        credit = credit or self.t("Screenshot: Rockstar Games", "截图：Rockstar Games")
        return f'<figure class="shot">{self.img(name, alt)}<figcaption>{credit}</figcaption></figure>'

    # ---------- chrome ----------
    def nav(self, cur):
        t = self.t
        items = [("home", t("Is it on PC?", "有 PC 版吗")), ("release", t("Release date", "发售日")),
                 ("tracker", t("Port tracker", "移植进度")), ("leak", t("EXE leak", "EXE 泄露")),
                 ("play", t("Play on PC now", "现在怎么玩")), ("specs", t("PC specs", "配置")), ("news", t("News", "新闻"))]
        return "".join(f'<a href="{self.url(k)}"{cur_attr(k == cur)}>{l}</a>' for k, l in items)

    def header(self, cur):
        other = "en" if self.zh else "zh"
        ol = "en" if self.zh else "zh-CN"
        return f'''<header class="top">
  <div class="wrap">
    <a class="logo" href="{self.url("home")}">GTA VI <b>PC</b><small>STATUS</small></a>
    <nav class="nav" aria-label="Main">{self.nav(cur)}</nav>
    <a class="lang" href="{self.url(cur, other)}" hreflang="{ol}" lang="{ol}">{"EN" if self.zh else "中文"}</a>
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
                 ("news", t("News", "新闻")), ("privacy", t("Privacy", "隐私")), ("terms", t("Terms", "条款"))]
        a = "".join(f'<a href="{self.url(k)}">{l}</a>' for k, l in links)
        play = "/play/" if self.mode == "prod" else "https://gta6pc.org/play/"
        return f'''<footer>
  <div class="wrap">
    <div class="cols">{a}<a href="{play}">{t("Neon Bay mini game", "Neon Bay 小游戏")}</a></div>
    <p>{t("GTA6PC.org is an unofficial fan site, not affiliated with Rockstar Games or Take-Two Interactive. Screenshots © Rockstar Games. We never host or link game files.",
          "GTA6PC.org 是非官方粉丝站，与 Rockstar Games、Take-Two 无关。游戏截图版权归 Rockstar Games。本站不提供也不链接任何游戏文件。")}</p>
  </div>
</footer>'''

    def head(self, key, title, desc, faqs=None, crumbs=None, noindex=False):
        fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                 '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600'
                 + ("&family=Noto+Sans+SC:wght@400;500;700;900" if self.zh else "") + f'&display=swap"><link rel="stylesheet" href="{self.asset("site.css")}">')
        h = [f"<title>{escape(title)}</title>", f'<meta name="description" content="{escape(desc)}">']
        if self.mode == "prod":
            canon = SITE + self.url(key)
            h += [f'<link rel="canonical" href="{canon}">',
                  f'<link rel="alternate" hreflang="en" href="{SITE + self.url(key, "en")}">',
                  f'<link rel="alternate" hreflang="zh-CN" href="{SITE + self.url(key, "zh")}">',
                  f'<link rel="alternate" hreflang="x-default" href="{SITE + self.url(key, "en")}">',
                  '<meta name="theme-color" content="#0d0718">',
                  f'<meta name="robots" content="{"noindex" if noindex else "index, follow"}">',
                  '<meta property="og:type" content="website">', '<meta property="og:site_name" content="GTA6PC.org">',
                  f'<meta property="og:locale" content="{"zh_CN" if self.zh else "en_US"}">',
                  f'<meta property="og:title" content="{escape(title)}">', f'<meta property="og:description" content="{escape(desc)}">',
                  f'<meta property="og:url" content="{canon}">', f'<meta property="og:image" content="{SITE}/og-image.png">',
                  '<meta name="twitter:card" content="summary_large_image">']
            graph = [{"@type": "WebPage", "@id": canon + "#webpage", "url": canon, "name": title, "description": desc,
                      "inLanguage": "zh-CN" if self.zh else "en", "dateModified": STATUS["updated"][:10],
                      "about": {"@type": "VideoGame", "name": "Grand Theft Auto VI", "alternateName": "GTA 6"}}]
            if crumbs:
                graph.append({"@type": "BreadcrumbList", "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + self.url(k)} for i, (k, n) in enumerate(crumbs)]})
            if faqs:
                graph.append({"@type": "FAQPage", "mainEntity": [
                    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]})
            h.append('<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + "</script>")
        h.append(fonts)
        return "\n".join(h)

    def ads(self, key, noindex):
        """Adsterra Popunder + Social Bar (config in data/ads.json). Production only; never on legal pages or 404."""
        if self.mode != "prod" or not ADS.get("enabled") or noindex or key in ADS.get("no_ads_pages", []):
            return ""
        allowed = sorted({Site("prod", l).url(k) for l in ("en", "zh") for k in PAGES if k not in ADS.get("no_ads_pages", [])})
        cfg = dict(ADS["config"], allowedPaths=allowed)
        return ('<script type="application/json" id="adsterra-config">' + json.dumps(cfg, ensure_ascii=False) + "</script>\n"
                f'<script src="{ADS["runtime"]}" defer></script>')

    def doc(self, key, title, desc, body, faqs=None, crumbs=None, noindex=False):
        head = self.head(key, title, desc, faqs, crumbs, noindex)
        body = body + "\n" + self.ads(key, noindex)
        if self.mode == "preview" and key == "home" and not self.zh:
            # Artifact preview entry page: the host supplies <html>/<head>.
            return f'<meta name="claude:viewport-fit-sides" content="cover">\n{head}\n{body}\n'
        return (f'<!doctype html>\n<html lang="{"zh-CN" if self.zh else "en"}">\n<head>\n<meta charset="utf-8">\n'
                f'<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body>\n{body}\n</body>\n</html>\n')

    # ---------- reusable blocks ----------
    def faq_block(self, faqs, open_first=False):
        return '<div class="faq">' + "".join(
            f'<details{" open" if open_first and i == 0 else ""}><summary>{escape(q)}</summary><p>{a}</p></details>' for i, (q, a) in enumerate(faqs)) + "</div>"

    def stage_chart(self, rows, title=True):
        t = self.t
        out = []
        for p in rows:
            st = p["stage"]
            cells = "".join((f'<i class="on{" end" if i == st - 1 else ""}"></i>' if i < st else "<i></i>") for i in range(7))
            tip = escape(f'{p["name"]}: {t("stage", "阶段")} {st}/7 · {p["note"][self.lang]}')
            out.append(f'<div class="row{" halt" if p["halted"] else ""}" title="{tip}"><span class="n">{p["name"]}</span>'
                       f'<span class="track" aria-label="{tip}">{cells}</span><span class="v">{st}/7</span></div>')
        axis = "".join(f"<span>{i + 1}</span>" for i in range(7))
        head = (f'<h3>{t("How far each project has got", "各项目进度")}</h3><p class="sub">{t("Stage reached on a 7-step ladder", "7 级进度")} · '
                f'{STATUS["updated_label"][self.lang]} · {t("hover a row for details", "悬停看详情")}</p>') if title else ""
        return f'<div class="chart">{head}<div class="rows">{"".join(out)}</div><div class="axis7"><span></span><div>{axis}</div><span></span></div></div>'

    def hbars(self, rows, scale, ticks, goal=None):
        """Horizontal bar chart. rows: (label, value, css_class, value_label)."""
        def pct(v):
            return f"{v / scale * 100:.2f}%"
        r = []
        for n, v, c, lbl in rows:
            cls = f' class="{c}"' if c else ""
            if v / scale < 0.66:
                r.append(f'<div class="r"><span>{n}</span><span class="bar"><s{cls} style="width:{pct(v)}"></s><em style="left:calc({pct(v)} + 8px)">{lbl}</em></span></div>')
            else:
                r.append(f'<div class="r"><span>{n}</span><span class="bar"><s{cls} style="width:{pct(v)}"></s><em style="right:8px;color:#13061f">{lbl}</em></span></div>')
        g = ""
        if goal:
            gv, gl = goal
            g = (f'<div class="r" aria-hidden="true" style="position:absolute;inset:0;pointer-events:none"><span></span>'
                 f'<span style="position:relative;align-self:stretch"><span class="goal" style="left:{pct(gv)}"><span>{gl}</span></span></span></div>')
        tk = "".join(f"<span>{x}</span>" for x in ticks)
        return f'<div class="fps">{"".join(r)}{g}</div><div class="fps-axis"><span></span><div>{tk}</div></div>'

    def fps_chart(self):
        t = self.t
        mx = STATUS["port_stats"]["world_fps_max"]
        rows = [(t("PS5 Pro (official)", "PS5 Pro（正版）"), 30, "ref", "30 fps"), (t("Best port · menus", "最好的移植 · 菜单"), 30, "", "30 fps"),
                (t("Best port · open world", "最好的移植 · 开放世界"), mx, "", f"≤ {mx} fps")]
        return (f'<div class="chart"><h3>{t("The speed gap", "帧数差距")}</h3><p class="sub">{t("Frames per second. Playable needs about 20.", "每秒帧数。能玩大约需要 20 帧。")}</p>'
                + self.hbars(rows, 30, [0, 10, 20, 30], (20, t("playable ≈ 20", "可玩线 ≈ 20"))) + "</div>")

    def screens(self):
        t = self.t
        items = [
            ('<div class="scr"><div class="tb">GTA VI</div><div class="spin"></div></div>', t("Stage 3 · window opens", "阶段 3 · 出窗口"), t("Black window, nothing drawn", "黑窗口，什么都没画")),
            ('<div class="scr"><span class="fpsc">0.3 fps</span></div>', t("Stage 4 · first frames", "阶段 4 · 出帧"), t("Frames present, still black", "能出帧，但仍是黑的")),
            ('<div class="scr" style="background:#0b0714"><span class="fpsc">30 fps</span><div class="menu-l"><i class="sel"></i><i></i><i></i><i></i><i></i></div><div class="logo6">VI</div></div>',
             t("Stage 5 · menus", "阶段 5 · 菜单"), t("Settings and legal screens at 30 fps", "设置和法律声明界面，30 帧")),
            ('<div class="scr world"><span class="fpsc">1.2 fps</span><div class="shape" style="left:10%;width:22%"></div><div class="shape" style="left:40%;width:14%;height:45%"></div>'
             '<div class="shape" style="left:62%;width:28%;height:22%"></div></div>', t("Stage 5 · world loads", "阶段 5 · 世界加载"), t("Dark scene, about 1 fps. Leaders are here.", "画面昏暗，约 1 帧。领先项目在这里")),
            (f'<div class="scr none">{t("Nobody yet", "还没有人做到")}</div>', t("Stage 6 · in-game", "阶段 6 · 进游戏"), t("Control a character in the world", "能在世界里操控角色")),
        ]
        figs = "".join(f'<figure class="screen">{s}<figcaption>{a}<small>{b}</small></figcaption></figure>' for s, a, b in items)
        return (f'<div class="screens">{figs}</div><p class="cap" style="margin-top:10px">'
                f'{t("Illustrations based on project status notes. We do not publish captures from the leaked build.", "示意图，根据各项目公开的进度说明绘制。本站不发布泄露版本的实机截图。")}</p>')

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

    def stepper(self):
        t = self.t
        steps = [
            ("ok", t("19 Nov", "11/19"), t("Console launch + 209 GB Xbox build leaks", "主机版发售，209 GB Xbox 版泄露"), t("No EXE, can’t start", "缺 EXE，无法启动")),
            ("warn", t("23 Nov", "11/23"), t("Cyberleek posts the EXE", "大葱哥放出 EXE"), t("Reported ZIP, ~57 MB", "报道约 57 MB")),
            ("", t("+3 hours", "3 小时后"), t("Reports: a settings screen", "报道称进到设置"), t("Boot not verified", "启动未经核验")),
            ("", t("23 Nov, night", "11/23 晚"), t("VIctory streams the menus", "VIctory 直播跑到菜单"), t("~15 fps, code goes public", "约 15 帧，代码随后公开")),
            ("bad", t("23 Nov", "11/23"), t("Leonida goes offline", "Leonida 下线"), t("Repo and Discord gone", "仓库和 Discord 都没了")),
            ("", t("24 Nov", "11/24"), t("World loads, still dark", "世界能加载，仍是黑的"), t("Under 2 fps", "不到 2 帧")),
        ]
        return '<ol class="stepper">' + "".join(f'<li class="{c}"><time>{d}</time><b>{a}</b><span>{b}</span></li>' for c, d, a, b in steps) + "</ol>"

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
            title, desc = n[self.lang]
            li.append(f'<li><time datetime="{n["date"]}">{self.date(n["date"])}</time><div><h3><span class="tag {c}" style="margin-right:8px">{lbl}</span>{title}</h3>'
                      + (f"<p>{desc}</p>" if detail else "") + "</div></li>")
        return '<ol class="log">' + "".join(li) + "</ol>"

    def board(self):
        t = self.t
        lamps = [("official_pc", "release", t("Official PC version", "官方 PC 版")), ("port", "tracker", t("Unofficial port", "民间移植")),
                 ("play_now", "play", t("Play on a PC screen", "在电脑屏幕上玩"))]
        sigs = "".join(f'<a class="sig" href="{self.url(k)}"><i class="lamp {STATUS[s]["lamp"]}"></i><div><div class="k">{lbl}</div>'
                       f'<div class="v">{STATUS[s][self.lang][0]}</div><div class="d">{STATUS[s][self.lang][1]}</div></div></a>' for s, k, lbl in lamps)
        return (f'<div class="board" aria-label="{t("Status board", "状态台")}"><header><span class="eyebrow">{t("Status board", "状态台")}</span>'
                f'<span class="eyebrow num">{STATUS["updated_label"][self.lang]}</span></header>{sigs}</div>')

    def yn_table(self, rows, head=None):
        th = ("<thead><tr>" + "".join(f"<th>{h}</th>" for h in head) + "</tr></thead>") if head else ""
        tr = "".join("<tr><td><span class=\"ico " + r[0] + "\">" + ("✓" if r[0] == "y" else "✕") + "</span></td>" + "".join(
            (f"<td><b>{c}</b></td>" if i == 0 else f"<td>{c}</td>") for i, c in enumerate(r[1:])) + "</tr>" for r in rows)
        return f'<div class="tbl"><table>{th}<tbody>{tr}</tbody></table></div>'

    # ---------- content page shell ----------
    def content_page(self, key, title, desc, h1, answer, body, faqs=None, image=None, tags=(), nexts=(), note=""):
        t = self.t
        crumbs = [("home", t("Home", "首页")), (key, h1)]
        rail_items = [("home", t("Is GTA 6 on PC?", "有 PC 版吗")), ("release", t("PC release date", "PC 版发售日")), ("tracker", t("Port tracker", "移植进度")),
                      ("leak", t("EXE leak explained", "EXE 泄露解读")), ("safe", t("Is that download safe?", "下载安全吗")), ("play", t("Play on PC now", "现在怎么玩")),
                      ("specs", t("PC specs", "配置")), ("steam", t("Steam & Game Pass", "Steam 与 Game Pass")), ("news", t("News", "新闻"))]
        rail = "".join(f'<a href="{self.url(k)}"{cur_attr(k == key)}>{l}</a>' for k, l in rail_items)
        tag_html = "".join(f'<span class="tag {c}">{x}</span>' for c, x in tags)
        img_html = self.img(image, "", lazy=False) if image else ""
        nx = ""
        if nexts:
            nx = (f'<div><p class="eyebrow" style="margin-bottom:12px">{t("Next", "接着看")}</p><div class="next">'
                  + "".join(f'<a href="{self.url(k)}">{a}<span>{b}</span></a>' for k, a, b in nexts) + "</div></div>")
        faq_html = (f'<h2>{t("FAQ", "常见问题")}</h2>' + self.faq_block(faqs)) if faqs else ""
        note_html = f'<p class="note">{note}</p>' if note else ""
        html = f'''{self.header(key)}
<main>
  <section class="page-head{" photo" if image else ""}">
    {img_html}
    <div class="wrap">
      <div class="crumbs"><a href="{self.url("home")}">{t("Home", "首页")}</a><span>/</span><span>{h1}</span></div>
      <h1>{h1}</h1>
      <div class="meta"><span class="tag">{t("Updated", "更新于")} {STATUS["updated_label"][self.lang]}</span>{tag_html}</div>
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
        return self.doc(key, title, desc, html, faqs=faqs, crumbs=crumbs)

    # ======================= PAGES =======================
    def page_home(self):
        t = self.t
        ps = STATUS["port_stats"]
        play_rows = [("y", t("PS Remote Play (Windows app)", "PS Remote Play（Windows 客户端）"), t("Your PS5 + the game", "你自己的 PS5 + 游戏")),
                     ("y", t("Xbox app remote play", "Xbox 应用远程游玩"), t("Your Xbox Series X|S + the game", "你自己的 Xbox Series X|S + 游戏")),
                     ("y", t("Capture card", "采集卡"), t("Console + capture card, lowest lag", "主机 + 采集卡，延迟最低")),
                     ("n", t("Xbox Cloud Gaming", "Xbox 云游戏"), t("Xbox consoles only, not PC", "只推流到 Xbox 主机，PC 不行")),
                     ("n", t("GeForce Now / Game Pass", "GeForce Now / Game Pass"), t("Not available", "没有"))]
        faqs = [(t("Is GTA 6 on PC yet?", "GTA 6 出 PC 版了吗？"), t("No. It launched on 19 November 2026 for PS5 and Xbox Series X|S only.", "没有。2026 年 11 月 19 日只发售了 PS5 和 Xbox Series X|S 版。")),
                (t("Can I pre-order it on Steam?", "Steam 能预购吗？"), t("No. There is no PC store listing anywhere yet.", "不能。目前任何 PC 商店都没有上架。")),
                (t("Is the Cyberleek EXE a PC version?", "大葱哥放的 EXE 是 PC 版吗？"), t("No. It is the Xbox program file and needs an unofficial port to run.", "不是。那是 Xbox 版的主程序，要靠民间移植项目才能跑。")),
                (t("Is GTA 6 on Game Pass?", "GTA 6 进 Game Pass 了吗？"), t("No, on any platform.", "没有，哪个平台都没有。")),
                (t("Should I upgrade my PC now?", "现在要不要升级电脑？"), t("Wait for official requirements, usually 1–2 months before a PC launch.", "先等官方配置，一般在 PC 版发售前 1–2 个月公布。"))]
        lead = [p for p in PROJECTS if not p["halted"]][:6] + [p for p in PROJECTS if p["halted"]]
        body = f'''{self.header("home")}
<main>
  <section class="hero photo">
    {self.img("hero-vice-city-night.jpg", t("Vice City skyline at dusk, GTA 6 screenshot", "GTA 6 游戏截图：黄昏的罪恶都市"), "bg", lazy=False)}
    <div class="wrap">
      <div>
        <p class="eyebrow">{t("Updated", "更新于")} {STATUS["updated_label"][self.lang]}</p>
        <h1>{t("Is GTA 6 on PC?", "GTA 6 有 PC 版了吗？")}<span class="no">{t("Not yet.", "还没有。")}</span></h1>
        <p class="lede">{t("No official PC version. Reports say the leaked Xbox build can boot on PC, but <strong>nobody can play it</strong>.", "官方没有 PC 版。有报道称泄露的 Xbox 版能在 PC 上启动，但<strong>还没人能玩</strong>。")}</p>
        <div class="ctas"><a class="btn primary" href="{self.url("release")}">{t("PC release date", "PC 版什么时候出")}</a><a class="btn" href="{self.url("tracker")}">{t("Port tracker", "移植进度")}</a></div>
      </div>
      {self.board()}
    </div>
    <span class="credit">{t("Screenshot: Rockstar Games", "截图：Rockstar Games")}</span>
  </section>

  <section class="sec" id="port">
    <div class="wrap">
      <div class="sec-head"><div><p class="eyebrow">{t("Unofficial port race", "民间移植进度")}</p><h2>{t("Can the leaked build run on PC?", "泄露版能在 PC 上跑吗？")}</h2></div><a class="more" href="{self.url("tracker")}">{t("Full tracker →", "完整进度表 →")}</a></div>
      <div class="stats">
        <div class="stat hot"><b>{ps["playable"]}</b><span>{t("playable ports", "能玩的移植")}</span></div>
        <div class="stat"><b>{ps["tracked"]}</b><span>{t("projects tracked", "追踪中的项目")}</span></div>
        <div class="stat cy"><b>{ps["best_stage"]}/7</b><span>{t("furthest stage", "最高进度")}</span></div>
        <div class="stat"><b>&lt;2</b><span>{t("fps in the world", "开放世界帧数")}</span></div>
      </div>
      {self.screens()}
      <div class="grid2" style="margin-top:22px">{self.stage_chart(lead)}{self.fps_chart()}</div>
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

  <section class="sec" id="news">
    <div class="wrap">
      <div class="sec-head"><div><p class="eyebrow">{t("This week", "本周")}</p><h2>{t("GTA 6 PC news", "GTA 6 PC 新闻")}</h2></div><a class="more" href="{self.url("news")}">{t("All news →", "全部新闻 →")}</a></div>
      {self.news_list(NEWS[:5], detail=False)}
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
      <div class="sec-head"><div><p class="eyebrow">{t("PC specs (estimate)", "配置（预估）")}</p><h2>{t("Will my PC run GTA 6?", "我的电脑能跑吗？")}</h2><p>{t("Consoles are stuck at 30 fps by the CPU, so the CPU matters for 60 fps.", "主机被 CPU 卡在 30 帧，所以想上 60 帧，CPU 和显卡一样重要。")}</p></div><a class="more" href="{self.url("specs")}">{t("Full estimate →", "完整配置分析 →")}</a></div>
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
      <div class="sec-head"><div><p class="eyebrow">FAQ</p><h2>{t("Quick answers", "常见问题")}</h2></div></div>
      {self.faq_block(faqs, open_first=True)}
    </div>
  </section>
</main>
{self.footer()}'''
        return self.doc("home", t("GTA 6 PC: Is It Out? Release Date, Port Tracker & Specs", "GTA 6 PC 版：出了吗？发售日、移植进度与配置"),
                        t("Is GTA 6 on PC? Not officially. Live status of the PC release date, the unofficial port race after the Cyberleek EXE leak, PC specs and fake downloads.",
                          "GTA 6 有 PC 版了吗？官方还没有。实时整理 PC 版发售日、大葱哥 EXE 泄露后的民间移植进度、配置预估和假下载识别。"),
                        body, faqs=faqs, crumbs=[("home", t("Home", "首页"))])

    def page_tracker(self):
        t = self.t
        ps = STATUS["port_stats"]
        off = f' <span class="tag bad">{t("Offline", "已下线")}</span>'
        rows = "".join(
            f'<tr data-stage="{p["stage"]}"><td><b>{p["name"]}</b>{off if p["halted"] else ""}</td>'
            f'<td>{p["approach"][self.lang]}</td><td class="num">{p["stage"]}/7</td><td>{p["note"][self.lang]}</td></tr>' for p in PROJECTS)
        label = json.dumps(t("Showing {n} of {t}", "显示 {n} / {t} 个"), ensure_ascii=False)
        body = f'''<div class="stats">
  <div class="stat hot"><b>{ps["playable"]}</b><span>{t("playable", "能玩")}</span></div>
  <div class="stat cy"><b>{ps["at_stage5"]}</b><span>{t("at stage 5", "到达阶段 5")}</span></div>
  <div class="stat"><b>{ps["offline"]}</b><span>{t("taken offline", "已下线")}</span></div>
  <div class="stat"><b>{ps["hours_since_exe"]}</b><span>{t("since the EXE", "距 EXE 放出")}</span></div>
</div>
{self.stage_chart(PROJECTS)}
<h2>{t("What each stage looks like", "每个阶段长什么样")}</h2>
{self.screens()}
<h2>{t("Race timeline", "进度时间线")}</h2>
{self.stepper()}
{self.fps_chart()}
<h2>{t("All projects", "全部项目")}</h2>
<div class="filter">
  <input id="q" type="search" placeholder="{t("Filter by name or approach", "按名称或技术路线筛选")}" aria-label="{t("Filter", "筛选")}">
  <select id="stage" aria-label="{t("Minimum stage", "最低阶段")}"><option value="0">{t("All stages", "全部阶段")}</option><option value="5">{t("Stage 5+", "阶段 5 以上")}</option><option value="4">{t("Stage 4+", "阶段 4 以上")}</option></select>
</div>
<div class="tbl"><table id="projects"><thead><tr><th>{t("Project", "项目")}</th><th>{t("Approach", "技术路线")}</th><th>{t("Stage", "阶段")}</th><th>{t("Latest", "最新状态")}</th></tr></thead><tbody>{rows}</tbody></table></div>
<p id="count" class="eyebrow num"></p>
<h2>{t("Can I try it?", "我能试试吗？")}</h2>
<p>{t("No. Every project needs the leaked game files, which you can’t get legally, and fake copies carry malware. We don’t link any of them.", "不能。所有项目都需要泄露的游戏文件，没有合法来源，网上流传的副本还常带木马。本站不提供任何相关链接。")} <a href="{self.url("safe")}">{t("Is that download safe? →", "下载安全吗？→")}</a></p>
<h2>{t("Will they be shut down?", "会被下架吗？")}</h2>
<p>{t("Probably. Take-Two removed GTA 5 ports from GitHub on 18 Nov, and Leonida’s founder says Rockstar took down its Discord.", "大概率会。Take-Two 11 月 18 日刚让 GitHub 下架了一批 GTA 5 移植；Leonida 创始人称其 Discord 是被 Rockstar 申请删除的。")}</p>
<script>
(function () {{
  var q = document.getElementById('q'), s = document.getElementById('stage'), rows = document.querySelectorAll('#projects tbody tr'), c = document.getElementById('count');
  function run() {{
    var x = q.value.trim().toLowerCase(), min = +s.value, n = 0;
    rows.forEach(function (r) {{ var ok = (+r.dataset.stage >= min) && (!x || r.textContent.toLowerCase().indexOf(x) > -1); r.hidden = !ok; if (ok) n++; }});
    c.textContent = {label}.replace('{{n}}', n).replace('{{t}}', rows.length);
  }}
  q.addEventListener('input', run); s.addEventListener('change', run); run();
}})();
</script>'''
        faqs = [(t("Has anyone played GTA 6 on PC?", "有人在 PC 上玩到 GTA 6 了吗？"), t("Not in any verified way. The furthest confirmed result is a world that loads but renders black.", "没有可证实的。目前能确认的最远进度是世界能加载但全黑。")),
                (t("Does the port need an Xbox?", "移植需要 Xbox 吗？"), t("No console, but every project needs the leaked Xbox build files.", "不需要主机，但所有项目都需要泄露的 Xbox 版游戏文件。")),
                (t("Will an unofficial port beat the official PC version?", "民间版会比官方 PC 版好吗？"), t("No. An official port brings proper PC settings, mouse and keyboard, and GTA Online.", "不会。官方版会有完整的画面设置、键鼠支持和 GTA Online。"))]
        return self.content_page("tracker", t("GTA 6 PC Port Tracker: Is the Unofficial Port Playable?", "GTA 6 PC 移植进度：民间版能玩了吗？"),
                                 t("Is the unofficial GTA 6 PC port playable? Stage-by-stage status of 14 projects running the leaked Xbox build, updated daily.", "GTA 6 民间 PC 移植能玩了吗？14 个项目的分阶段进度，每日更新。"),
                                 t("GTA 6 PC Port Tracker", "GTA 6 PC 移植进度"),
                                 f'<strong>{t("No port is playable yet.", "还没有能玩的移植。")}</strong> {t("Leaders run the menus at 30 fps; the world loads dark at under 2 fps.", "领先项目的菜单能跑 30 帧，世界能加载但全黑，不到 2 帧。")}',
                                 body, faqs=faqs, image="tail-lights.jpg", tags=[("bad", t("Playable: no", "能玩：否")), ("cy", t("Best: stage 5 of 7", "最高：5/7"))],
                                 nexts=[("leak", t("What Cyberleek leaked", "大葱哥泄露了什么"), t("Build, EXE, timeline", "游戏包、EXE、时间线")), ("release", t("Official release date", "官方发售日"), t("Q1 2027 vs history", "2027 Q1 还是更晚")), ("play", t("Play on PC today", "现在怎么玩"), t("Remote Play", "Remote Play 串流"))],
                                 note=t("Stage data: GTA VI PC Race and Six on PC trackers; reporting from PC Games Hardware, heise, TweakTown, TorrentFreak.", "进度数据：GTA VI PC Race、Six on PC 两个追踪站；报道来源：PC Games Hardware、heise、TweakTown、TorrentFreak。"))

    def page_leak(self):
        t = self.t
        verdicts = [("warn", t("Reported", "报道"), t("Outlets report an Xbox build and EXE; some ports are said to reach menus. The file has not been authenticated", "多家媒体报道有 Xbox 版和 EXE，有移植称能到菜单。文件本身未经核验")),
                    ("ok", t("Real", "真"), t("Rockstar has announced no PC version and said nothing about the leak", "Rockstar 没公布 PC 版，也没对泄露表态")),
                    ("warn", t("Unconfirmed", "待证"), t("“Rockstar took down Leonida”: only the founder says so", "“Leonida 是被 Rockstar 弄下线的”：只有创始人自己这么说")),
                    ("warn", t("Unconfirmed", "待证"), t("“PC version in Q1 2027”: one report, anonymous sources", "“PC 版 2027 Q1”：单一报道，匿名信源")),
                    ("warn", t("Unconfirmed", "待证"), t("A 3 fps clip of a lit scene on PC", "一段 3 帧的 PC 亮场景片段")),
                    ("bad", t("Fake", "假"), t("Any “GTA 6 PC” download, repack or ISO", "任何“GTA 6 PC 下载 / 整合版 / ISO”")),
                    ("bad", t("Fake", "假"), t("Playing on PC via Xbox Cloud or Game Pass", "用 Xbox 云游戏或 Game Pass 在 PC 上玩")),
                    ("bad", t("Fake", "假"), t("“Rockstar confirmed the leak is 100% real”", "“Rockstar 已确认泄露内容 100% 真实”"))]
        vhtml = "".join(f'<div class="verdict"><span class="tag {c}">{l}</span><div><b>{x}</b></div></div>' for c, l, x in verdicts)
        timeline = [n for n in NEWS if n["tag"] in ("leak", "port", "legal") or n["date"] == "2026-10-13"]
        body = f'''<h2 style="margin-top:0">{t("What leaked", "泄露了什么")}</h2>
<div class="big3">
  <div class="stat"><b>209 GB</b><span>{t("Xbox Series build · 19 Nov", "Xbox Series 游戏包 · 11/19")}</span></div>
  <div class="stat hot"><b>57 MB</b><span>{t("Reported EXE size · 23 Nov", "报道的 EXE 大小 · 11/23")}</span></div>
  <div class="stat cy"><b>1.0.2.1</b><span>{t("Label on the leaked build", "泄露包上的版本号")}</span></div>
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
        faqs = [(t("Can I play GTA 6 on PC with the leaked EXE?", "用泄露的 EXE 能在 PC 上玩吗？"), t("No. You’d also need the 209 GB build plus a port that works, and none does yet. Using leaked files is copyright infringement.", "不能。还需要 209 GB 的游戏包和一个能跑的移植项目，目前没有。使用泄露文件属于侵权。")),
                (t("Will the leak delay the official PC version?", "泄露会推迟官方 PC 版吗？"), t("No report links the two. After the 2022 hack, Rockstar said it expected no long-term effect on development.", "没有报道把两者联系起来。2022 年被黑客入侵后，Rockstar 曾表示对开发不会有长期影响。"))]
        return self.content_page("leak", t("GTA 6 EXE Leak Explained: What Cyberleek Released", "GTA 6 EXE 泄露解读：大葱哥到底放了什么"),
                                 t("What Cyberleek leaked: the 209 GB GTA 6 Xbox build and the EXE released on 23 November. What is real, what is unconfirmed, and what is fake.", "大葱哥（Cyberleek）泄露了什么：209 GB 的 GTA 6 Xbox 版和 11 月 23 日放出的 EXE。哪些是真的、哪些待证、哪些是假的。"),
                                 t("The GTA 6 EXE Leak, Explained", "大葱哥的 GTA 6 EXE 到底是什么"),
                                 f'<strong>{t("It is not a PC version.", "它不是 PC 版。")}</strong> {t("It is the Xbox build’s program file. It only runs inside unofficial ports, and none is playable.", "那是 Xbox 版的主程序，只能在民间移植项目里跑，而这些项目目前都不能玩。")}',
                                 body, faqs=faqs, image="ocean-view-hotel.jpg", tags=[("warn", t("Rockstar: no comment", "Rockstar：未回应")), ("bad", t("Not a PC version", "不是 PC 版"))],
                                 nexts=[("tracker", t("Port tracker", "移植进度"), t("Where each project stands", "各项目到哪一步了")), ("safe", t("Is that download safe?", "下载安全吗？"), t("Red flags and what to do", "危险信号和补救")), ("release", t("PC release date", "PC 版发售日"), t("Q1 2027 vs history", "2027 Q1 还是更晚"))],
                                 note=t("Reporting: PC Games Hardware, Notebookcheck, heise, TweakTown, Space4Games, GamesBeat. We do not host or link leaked files.", "来源：PC Games Hardware、Notebookcheck、heise、TweakTown、Space4Games、GamesBeat。本站不提供也不链接泄露文件。"))

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
                (t("Will the leak delay the PC version?", "泄露会推迟 PC 版吗？"), t("No report says so.", "目前没有报道这么说。"))]
        return self.content_page("release", t("GTA 6 PC Release Date: Q1 2027 Report vs Rockstar’s History", "GTA 6 PC 版发售日：2027 Q1 爆料与历史规律"),
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
<h2>{t("If you upgrade, do it in this order", "要升级的话，按这个顺序")}</h2>
{self.numbered(upgrade, 3, "ok")}
{self.shot("neon-club.jpg", t("GTA 6 screenshot: neon-lit club", "GTA 6 截图：霓虹夜店"))}'''
        faqs = [(t("Will an 8 GB graphics card work?", "8 GB 显存够吗？"), t("Probably at low texture settings only. We recommend 12 GB or more.", "大概只能开低材质。建议 12 GB 以上。")),
                (t("Is 16 GB of RAM enough?", "16 GB 内存够吗？"), t("For the minimum tier, yes. 32 GB is the comfortable target.", "最低档够用，32 GB 更从容。")),
                (t("Can I play from a hard drive?", "机械硬盘能玩吗？"), t("Expect stutter and pop-in. The game is built around fast SSD streaming.", "会卡顿、贴图延迟。游戏是按高速固态的加载速度设计的。")),
                (t("Should I buy parts now?", "现在买配件吗？"), t("No. Rockstar usually posts PC requirements 1–2 months before launch.", "不用急。Rockstar 一般在 PC 版发售前 1–2 个月公布配置。"))]
        return self.content_page("specs", t("GTA 6 PC System Requirements: Minimum, Recommended & 4K (Estimate)", "GTA 6 PC 配置要求：最低、推荐与 4K（预估）"),
                                 t("Estimated GTA 6 PC requirements for 1080p, 1440p and 4K, based on PS5 hardware and Digital Foundry’s console analysis. No official specs yet.", "基于 PS5 硬件和 Digital Foundry 主机实测，预估 GTA 6 PC 版 1080p、1440p、4K 配置。官方尚未公布。"),
                                 t("GTA 6 PC System Requirements", "GTA 6 PC 配置要求"),
                                 f'<strong>{t("No official specs yet.", "官方还没公布。")}</strong> {t("Our estimate: RTX 3060 12 GB + Ryzen 5 3600 for 1080p/30, RTX 4070 Super + Ryzen 7 7700X for 1440p/60.", "我们的预估：1080p/30 帧要 RTX 3060 12G + Ryzen 5 3600，1440p/60 帧要 RTX 4070 Super + Ryzen 7 7700X。")}',
                                 body, faqs=faqs, image="neon-club.jpg", tags=[("warn", t("Estimate", "预估"))],
                                 nexts=[("release", t("PC release date", "PC 版发售日"), t("When to expect it", "大概什么时候")), ("play", t("Play on PC today", "现在怎么玩"), t("Remote Play", "Remote Play 串流")), ("steam", t("Steam & Steam Deck", "Steam 与 Deck"), t("Store and handheld", "商店和掌机"))],
                                 note=t("Based on PS5 hardware specs, Digital Foundry’s console analysis, and earlier Rockstar PC releases. Not official.", "依据：PS5 硬件参数、Digital Foundry 主机分析、Rockstar 以往 PC 版。非官方数据。"))

    def page_play(self):
        t = self.t
        rows = [("y", t("PS Remote Play", "PS Remote Play"), t("Your PS5 + the game", "自己的 PS5 + 游戏"), t("Low–medium", "低到中")),
                ("y", t("Xbox app remote play", "Xbox 应用远程游玩"), t("Your Xbox Series X|S + the game", "自己的 Xbox Series X|S + 游戏"), t("Low–medium", "低到中")),
                ("y", t("Capture card", "采集卡"), t("Console + capture card", "主机 + 采集卡"), t("Lowest", "最低")),
                ("n", t("Xbox Cloud Gaming", "Xbox 云游戏"), t("Streams to Xbox consoles only", "只推流到 Xbox 主机"), "—"),
                ("n", t("GeForce Now / Game Pass PC", "GeForce Now / Game Pass PC"), t("Not available", "没有"), "—"),
                ("n", t("Emulators / leaked-build ports", "模拟器 / 泄露版移植"), t("Not playable, and risky", "不能玩，且有风险"), "—")]

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
{self.shot("heist.jpg", t("GTA 6 screenshot", "GTA 6 截图"))}'''
        faqs = [(t("Can I play GTA 6 on PC without a console?", "没有主机能在电脑上玩吗？"), t("No. No cloud service streams GTA 6 to PC, and there is no PC version.", "不能。没有任何云服务把 GTA 6 推流到 PC，也没有 PC 版。")),
                (t("Does Remote Play work away from home?", "出门在外能串流吗？"), t("Yes, over the internet, if your home upload speed is good enough.", "可以，走互联网，前提是家里上传带宽够。")),
                (t("Is Xbox Cloud Gaming an option on PC?", "PC 能用 Xbox 云游戏玩吗？"), t("No. Xbox confirmed GTA 6 cloud streaming is limited to Xbox consoles.", "不能。Xbox 已确认 GTA 6 云游戏只支持 Xbox 主机。"))]
        return self.content_page("play", t("How to Play GTA 6 on PC Right Now (Remote Play Guide)", "现在怎么在电脑上玩 GTA 6（Remote Play 串流教程）"),
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
<h2>{t("Known fake GTA 6 downloads", "已知的假 GTA 6 下载")}</h2>
<div class="tbl"><table><thead><tr><th>{t("When", "时间")}</th><th>{t("Bait", "诱饵")}</th><th>{t("What it installs", "实际装了什么")}</th><th>{t("Reported by", "披露方")}</th></tr></thead><tbody>{crow}</tbody></table></div>
<h2>{t("Already ran one? Do this now", "已经运行过？马上这样做")}</h2>
{self.numbered(fix, 5, "bad")}'''
        faqs = [(t("Is the Cyberleek EXE a virus?", "大葱哥放的 EXE 是病毒吗？"), t("We don’t test or link leaked files. Re-uploads by third parties are a known malware route, and it can’t run GTA 6 on PC anyway.", "本站不测试也不链接泄露文件。第三方转传的版本是已知的木马传播渠道，而且它本来就不能让你在 PC 上玩。")),
                (t("Are “GTA 6 on PC” YouTube videos real?", "YouTube 上“GTA 6 PC 实机”视频是真的吗？"), t("No verified gameplay exists. At least one viral “PC” video was exposed as a hoax.", "目前没有可证实的实机画面，至少一个爆火的“PC 版”视频已被证实是假的。")),
                (t("Where can I safely get GTA 6 for PC?", "去哪里能安全下载 PC 版？"), t("Nowhere yet. When it launches, use Steam, Epic or the Rockstar Games Launcher.", "目前哪里都没有。等正式发售后，用 Steam、Epic 或 Rockstar 启动器。"))]
        return self.content_page("safe", t("Is That GTA 6 PC Download Safe? (No. Here’s How to Tell)", "GTA 6 PC 下载安全吗？（不安全，教你识别）"),
                                 t("Every GTA 6 PC download is fake. Known malware campaigns, red flags to check, and what to do if you already ran one.", "所有 GTA 6 PC 下载都是假的。已知的木马案例、危险信号，以及中招后怎么办。"),
                                 t("Is That GTA 6 PC Download Safe?", "GTA 6 PC 下载安全吗？"),
                                 f'<strong>{t("No.", "不安全。")}</strong> {t("No playable PC build of GTA 6 exists, official or unofficial. Every download claiming to be one is a scam, and many steal passwords and crypto.", "GTA 6 根本没有能玩的 PC 版，官方和民间都没有。所有自称是 PC 版的下载都是骗局，很多会盗号、盗币。")}',
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
<h2>{t("How Rockstar launched on PC before", "Rockstar 以往的 PC 首发方式")}</h2>
<div class="tbl"><table><thead><tr><th>{t("Game", "游戏")}</th><th>{t("PC launch", "PC 发售")}</th><th>{t("Stores", "商店")}</th></tr></thead><tbody>{hrow}</tbody></table></div>
<p>{t("Expect the Rockstar Games Launcher on day one. Steam is likely, but RDR2 shows it can come a month later. Every Rockstar PC game since 2019 runs through the Rockstar launcher, even when bought on Steam.", "首发大概率会上 Rockstar 启动器。Steam 很可能有，但荒野大镖客 2 晚了一个月才上 Steam。2019 年以来 Rockstar 的 PC 游戏即使在 Steam 买，也要通过 Rockstar 启动器运行。")}</p>'''
        faqs = [(t("Can I wishlist GTA 6 on Steam?", "Steam 能加愿望单吗？"), t("No. There is no store page to wishlist yet.", "不能，目前没有商店页。")),
                (t("Will GTA 6 come to Game Pass?", "GTA 6 会进 Game Pass 吗？"), t("Not at launch. Take-Two’s CEO has reportedly ruled out day one; GTA V took years to arrive.", "首发不会。据报道 Take-Two CEO 已排除首发入库的可能；GTA V 也是过了好几年才进。")),
                (t("Will it run on Steam Deck?", "Steam Deck 能跑吗？"), t("Nothing to run yet. With consoles CPU-limited at 30 fps, a handheld will struggle.", "现在没有可跑的版本。主机都被 CPU 卡在 30 帧，掌机会很吃力。"))]
        return self.content_page("steam", t("Is GTA 6 on Steam? Pre-Order, Game Pass & Steam Deck", "GTA 6 上 Steam 了吗？预购、Game Pass 与 Steam Deck"),
                                 t("GTA 6 is not on Steam, Epic or Game Pass yet. What Rockstar’s past PC launches suggest about stores, launchers and Steam Deck.", "GTA 6 还没上 Steam、Epic 或 Game Pass。从 Rockstar 以往 PC 首发看商店、启动器和 Steam Deck。"),
                                 t("Is GTA 6 on Steam?", "GTA 6 上 Steam 了吗？"),
                                 f'<strong>{t("No.", "没有。")}</strong> {t("There is no Steam, Epic or Rockstar Launcher page, so you can’t wishlist or pre-order GTA 6 on PC.", "Steam、Epic、Rockstar 启动器都没有商店页，PC 版不能加愿望单，也不能预购。")}',
                                 body, faqs=faqs, image="cover-art.jpg", tags=[("bad", t("Not listed", "未上架"))],
                                 nexts=[("release", t("PC release date", "PC 版发售日"), t("Q1 2027 vs history", "2027 Q1 还是更晚")), ("specs", t("PC specs", "配置"), t("Will your PC run it?", "电脑带得动吗")), ("play", t("Play on PC today", "现在怎么玩"), t("Remote Play", "Remote Play 串流"))],
                                 note=t("Sources: Steam and Rockstar store listings, Take-Two statements as reported by PCGamesN.", "来源：Steam 与 Rockstar 商店页、PCGamesN 转述的 Take-Two 表态。"))

    def page_news(self):
        t = self.t
        latest = NEWS[0][self.lang][0]
        return self.content_page("news", t("GTA 6 PC News: Leaks, Ports & Release Updates", "GTA 6 PC 新闻：泄露、移植与发售动态"),
                                 t("Dated GTA 6 PC news: release reports, the Cyberleek leak, unofficial port progress, takedowns and malware warnings.", "按日期整理的 GTA 6 PC 新闻：发售爆料、大葱哥泄露、民间移植进度、下架与木马预警。"),
                                 t("GTA 6 PC News", "GTA 6 PC 新闻"),
                                 f'<strong>{t("Latest", "最新")}:</strong> {latest}', self.news_list(NEWS, detail=True), image="key-art.jpg",
                                 nexts=[("tracker", t("Port tracker", "移植进度"), t("Live project status", "项目实时进度")), ("leak", t("EXE leak explained", "EXE 泄露解读"), t("What’s real", "哪些是真的")), ("release", t("PC release date", "PC 版发售日"), t("Both estimates", "两种预测"))])

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
  <p class="answer">{t("This page doesn’t exist. Neither does GTA 6 on PC, yet.", "这个页面不存在。GTA 6 的 PC 版也还不存在。")}</p>
  <div class="ctas"><a class="btn primary" href="{self.url("home")}">{t("Is GTA 6 on PC?", "有 PC 版吗？")}</a><a class="btn" href="{self.url("tracker")}">{t("Port tracker", "移植进度")}</a></div>
</div></section></main>
{self.footer()}'''
        return self.doc("home", t("Page not found | GTA6PC.org", "页面不存在 | GTA6PC.org"), "404", body, noindex=True)

    def all_pages(self):
        return {"home": self.page_home(), "release": self.page_release(), "specs": self.page_specs(), "tracker": self.page_tracker(),
                "leak": self.page_leak(), "play": self.page_play(), "safe": self.page_safe(), "steam": self.page_steam(),
                "news": self.page_news(), "privacy": self.page_legal("privacy"), "terms": self.page_legal("terms")}


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build(mode):
    out = ROOT / ("out" if mode == "prod" else "preview")
    if out.exists():
        shutil.rmtree(out)
    for lang in ("en", "zh"):
        s = Site(mode, lang)
        for key, html in s.all_pages().items():
            slug = PAGES[key]
            if mode == "prod":
                rel = ("zh/" if lang == "zh" else "") + (slug + ".html" if slug else "index.html")
            else:
                rel = s.url(key)
            write(out / rel, html)
        if mode == "prod":
            write(out / ("zh/404.html" if lang == "zh" else "404.html"), s.page_404())
    if mode == "prod":
        shutil.copytree(ROOT / "static", out / "static")
        # Files kept from the old deployment (Neon Bay at /play/, og-image.png, favicon...) live in legacy/.
        legacy = ROOT / "legacy"
        if legacy.is_dir():
            shutil.copytree(legacy, out, dirs_exist_ok=True, ignore=shutil.ignore_patterns("README.md"))
        urls = []
        for key in PAGES:
            en = SITE + Site("prod", "en").url(key)
            zh = SITE + Site("prod", "zh").url(key)
            for loc in (en, zh):
                urls.append(f'  <url><loc>{loc}</loc><lastmod>{STATUS["updated"][:10]}</lastmod>'
                            f'<xhtml:link rel="alternate" hreflang="en" href="{en}"/><xhtml:link rel="alternate" hreflang="zh-CN" href="{zh}"/></url>')
        write(out / "sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
              + "\n".join(urls) + "\n</urlset>\n")
        write(out / "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    else:
        shutil.copy(ROOT / "static" / "site.css", out / "site.css")
        shutil.copytree(ROOT / "static" / "img", out / "img")
    print(f"built {mode} -> {out.relative_to(ROOT)} ({sum(1 for _ in out.rglob('*.html'))} html files)")


if __name__ == "__main__":
    build("preview" if len(sys.argv) > 1 and sys.argv[1] == "preview" else "prod")
