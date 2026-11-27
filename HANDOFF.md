# gta6pc.org 改版：上线交接说明

给负责上线的 Agent。按顺序做，每一步都有验证方法。

## 这是什么

gta6pc.org 的 2026-11-27 改版。生产仓库 `main` 在这次改版之前已经是 Python 生成的静态站（`python3 build.py` → `out/`，Vercel），不是 Vite。这次在那份站点上接上四种语言（英文、中文、西班牙语、巴西葡萄牙语）、FAQ / FPS / Online、新闻文章页和西语葡语翻译。不要删现有源码，也不要把压缩包里自带的 git 历史推到 `main`。

- 预览（只有站长能看）：https://claude.ai/artifact/Xe8BkryXNDjMXuD66BZZkT
- 内容快照时间：2026-11-27 03:00 UTC（新闻截至 11 月 26 日）

## 目录

| 路径 | 用途 |
|---|---|
| `i18n/es.json`、`i18n/pt.json` | 西语、葡语翻译表：英文原句 → 译文。英文和中文文案直接写在 `build.py` 和 `data/` 里，其他语言都从英文原句查这张表 |
| `build.py` | 生成器。`python3 build.py` 输出到 `out/`（上线用）；`python3 build.py preview` 输出到 `preview/`（平铺文件、相对链接，只用于预览） |
| `data/status.json` | 首页状态台三盏灯、移植统计数字、更新时间 |
| `data/projects.json` | 移植追踪的项目卡片（公开 + 私有），字段说明见下文“日常更新” |
| `data/trend.json` | “游戏内最高帧数，逐日变化”折线图的数据（公开代码 / 私有两条线） |
| `data/news.json` | 新闻。首页“最新动态”取最新 5 条，/news 显示全部，泄露页取泄露和移植相关条目。带 `slug` 和 `body` 的条目会生成独立文章页 `/news/<slug>`，并写进 RSS（`/news/feed.xml`、`/zh/news/feed.xml`）和 sitemap |
| `data/ads.json` | 生产广告配置：Popunder + Social Bar，`enabled: true`，`slots` 为空。保留了说明用的 `note` 字段。脚本地址不要改 |
| `static/` | `site.css`、`tracker.js`（旧页的筛选脚本，新页面改用内联脚本，文件仍留在 `static/`）和 11 张 Rockstar 官方图，部署到 `/static/` |
| `legacy/` | 构建时原样复制进 `out/`：`play/`（Neon Bay）、`og-image.png`、`adsterra/runtime.js`。仓库里没有单独的 favicon 文件 |
| `tools/check.py` | 上线前检查：内部链接、每种语言内 title/description/H1 不重复、占位文字、sitemap、广告注入、禁链 |
| `vercel.json` | 沿用生产配置：`python3 build.py` → `out`、`cleanUrls`、www 301、`/news/xbox-executable` 301 到 `/cyberleek-leak`、`/play` 重写、安全响应头。没有把未知地址改写成 `index.html` 的兜底 |
| `docs/plan.html` | 改版方案（用户意图、真伪核查、页面矩阵） |
| `research/` | Google 联想词原始数据、意图表 |

## URL 表

西班牙语和葡萄牙语版本的网址与中文一样，只是前缀换成 `/es` 和 `/pt-br`（例如 `/es/gta-6-fps`、`/pt-br/faq`）。

`vercel.json` 开了 `cleanUrls`，所以 `release-date.html` 对外是 `/release-date`。**旧站的 `/`、`/release-date`、`/pc-specs`、`/play/` 地址都保持不变。**

| 英文 | 中文 | 页面 |
|---|---|---|
| `/` | `/zh` | 首页：有 PC 版吗（状态台） |
| `/release-date` | `/zh/release-date` | PC 版发售日（沿用旧地址） |
| `/pc-specs` | `/zh/pc-specs` | 配置（沿用旧地址） |
| `/pc-port-tracker` | `/zh/pc-port-tracker` | 移植进度（新） |
| `/cyberleek-leak` | `/zh/cyberleek-leak` | EXE 泄露解读（新） |
| `/how-to-play-gta-6-on-pc` | `/zh/how-to-play-gta-6-on-pc` | Remote Play 教程（新） |
| `/is-gta-6-pc-download-safe` | `/zh/is-gta-6-pc-download-safe` | 假下载识别（新） |
| `/steam` | `/zh/steam` | Steam / Game Pass / Deck（新） |
| `/faq` | `/zh/faq` | 常见问题汇总，30 问（新） |
| `/gta-6-fps` | `/zh/gta-6-fps` | GTA 6 帧数（新） |
| `/gta-6-online-pc` | `/zh/gta-6-online-pc` | GTA 6 Online 与 PC 联机（新） |
| `/news` | `/zh/news` | 新闻汇总（新） |
| `/news/<slug>` | `/zh/news/<slug>` | 新闻文章页，目前 16 篇（新） |
| `/privacy`、`/terms` | `/zh/privacy`、`/zh/terms` | 法律页（不放广告） |
| `/play/` | — | Neon Bay 小游戏（旧文件，原样保留） |

每个页面都有 canonical、hreflang（en / zh-CN / es / pt-BR / x-default）、OG 标签和 JSON-LD（WebPage、BreadcrumbList，有问答的页面加 FAQPage，新闻文章加 NewsArticle）。`sitemap.xml` 有 120 个 URL（4 种语言 × 14 个栏目页和 16 篇新闻），每个都带四种语言的 hreflang。`/play/` 和 404 不进 sitemap。

## 上线步骤

### 1. 放进仓库

生产源就是这个仓库。从当前 `main` 开分支，把改版文件合进来，提交后开 Pull Request。不要 force-push，不要把压缩包里的 `.git` 提交进来。

已经核对过、并保留生产版本的文件：

- `data/ads.json`：`enabled` 仍是 true，Popunder `https://abscloud.org/1/b640baabccdb568dd796990946539530`，Social Bar `https://bauval.org/14/0eba5089f9eb509606a14e9eebb4e230`，`slots` 仍是空数组，`runtime` 仍是 `/adsterra/runtime.js`，`no_ads_pages` 仍是 privacy 和 terms。说明字段 `note` 也保留。
- `vercel.json`：www 跳转、`/news/xbox-executable` 跳转、`/play` 重写、安全响应头。没有 SPA 兜底。
- `legacy/play/`、`legacy/og-image.png`、`legacy/adsterra/runtime.js`：和改版包是同一份文件。仓库里没有 favicon，改版包里也没有。
- `privacy` / `terms`：`build.py` 里的 `page_legal` 和当前生产是同一段通用文案，没有更具体的旧政策可替换。
- `static/tracker.js`：生产上的筛选脚本。新页面自己带内联脚本，这个文件留在 `static/` 里，不再注入到每个页面。

### 2. Vercel 设置

- 构建命令和输出目录已经写在 `vercel.json` 里（`python3 build.py` → `out`）。
- 不要加 `"rewrites": [{"source": "/(.*)", "destination": "/index.html"}]`。不存在的地址必须是真正的 404，根目录的 `404.html` 负责这件事。
- 如果 Vercel 构建环境报找不到 `python3`：把构建命令留空，在本地跑 `python3 build.py`，然后把 `out/` 提交上去（同时从 `.gitignore` 里去掉 `out/`）。

### 3. 用 Preview 部署验证

推送分支后，Vercel 会给一个 preview 地址。逐项检查：

```bash
BASE=https://<preview 域名>
for u in / /release-date /pc-specs /pc-port-tracker /cyberleek-leak /how-to-play-gta-6-on-pc /is-gta-6-pc-download-safe /steam /news /privacy /terms /zh /zh/pc-port-tracker /play/ /og-image.png /adsterra/runtime.js /sitemap.xml /robots.txt /does-not-exist; do printf "%-34s %s\n" "$u" "$(curl -s -o /dev/null -w '%{http_code}' $BASE$u)"; done
```

预期：最后一个 `/does-not-exist` 返回 404，其余都是 200。

再用浏览器打开 `/` 和 `/privacy`：首页应该请求 `abscloud.org` 和 `bauval.org`（广告），`/privacy` 不应该请求。

### 4. 上生产

- Promote 到 production（或合并到生产分支）。
- Google Search Console：重新提交 `https://gta6pc.org/sitemap.xml`，并对 `/`、`/pc-port-tracker`、`/cyberleek-leak` 请求编入索引。

## 日常更新（重要）

移植进度一天内会变好几次。至少每天更新一次：

1. 改 `data/` 下的 JSON：
   - `status.json`：`updated`、`updated_label`（中英两个都改）、三盏灯的文字、`race` 里的数字（最高帧数及说明、最好公开版本帧数、被下架仓库数）
   - `projects.json`：每个项目一条。`stage` 是 1–7（7 = 平均 20 帧以上且不常崩溃，比别家追踪站严）；`fps`；`story` / `picture` / `stability` 各有 `v`（0–1，画进度条）和中英文字；`evidence` 取 `verified`（追踪站核验）/ `press`（媒体报道）/ `self`（自报）/ `stream`（仅直播）；`public` 为 false 的是私有版本，不参与排名；`offline` 为 true 显示“已下线”；`sources` 是“数字出处”列表，每条有 `kind`（`tracker` / `video` / `press` / `readme` / `notice`）、中英文说明和 `url`（`readme` 类不填链接）
   - `trend.json`：每天加一行 `{"date", "public", "private"}`，填当天首次报道的最高游戏内帧数
   - `news.json`：在数组里加一条（重要新闻再加 `slug`、`body`、`page`，就会生成文章页，见下文），`tag` 取 `port` / `leak` / `official` / `report` / `legal` / `security`，中英各写一个标题和一句话，`source` 填原始报道的名称和链接（必填，页面上会显示“来源”）
   - 新闻文章页：`slug` 用英文小写加连字符；`body` 是中英文段落列表（每种语言 2–3 段）；`page` 是文末按钮指向的站内页面，格式 `[页面 key, 英文按钮文字, 中文按钮文字]`；`more` 是补充来源 `[[名称, 链接], ...]`。
   - “我的电脑能跑吗”检测工具的显卡和 CPU 列表在 `build.py` 的 `GPUS` / `CPUS` 里；新显卡上市时加一行，数字是相对性能（RTX 3060 12 GB = 100，Ryzen 5 3600 = 100）。分档门槛在 `checker()` 的 `need` 数组里。
2. 运行：

```bash
python3 build.py && python3 tools/check.py
```

3. 看构建输出的最后一行。如果出现 `untranslated strings: {'es': N, 'pt': N}`，说明有新增或改动的英文文案还没有西语 / 葡语译文，这些句子在西语和葡语页面上会暂时显示英文。缺译清单在 `i18n/_missing_es.json` 和 `i18n/_missing_pt.json`，把每句的译文以 `"英文原句": "译文"` 的形式加进 `i18n/es.json` 和 `i18n/pt.json`，再构建一次，直到不再提示。注意保留原句里的 HTML 标签和 `{n}` 这类占位符。
4. 提交并推送，Vercel 会自动部署。

进度数据来源：PortWatch VI（portwatch-vi.xyz，每 3 小时更新）、Six on PC（sixonpc.com）、GTA VI PC Race（vuyp.github.io/gta6-pc-race），以及 TechRadar、Game Rant、Notebookcheck、heise 的报道。注意：截至 11 月 27 日，媒体报道的帧数几乎都转述自 PortWatch 和 Reddit / X 上的视频，没有媒体自己跑过这些版本，所以每个数字都要标核验程度（`evidence` 字段）。PortWatch 的仓库没有开源许可证，只能引用它的核验结论并注明来源，不能整段复制它的文字或数据文件。

需要改状态台三盏灯和首页 H1 的时机：Rockstar 正式公布 PC 版；或有媒体 / 独立第三方亲自跑通某个民间版本（目前所有帧数都只是“报道”）。H1 和导语在 `build.py` 的 `page_home` 里。

改页面文案就直接改 `build.py`，每段文案都是 `t("English", "中文")` 两个版本挨着写。

## 红线

- **不链接**任何泄露文件、EXE、种子、网盘，也不链接需要泄露文件才能用的移植仓库（GitHub、GitLab、Discord 邀请都不行）。项目卡片写名字和进度，出处只链新闻、追踪站页面和这份 DMCA 通知：https://github.com/github/dmca/blob/master/2026/11/2026-11-24-take-two.md
- 不在标题、锚文本里用“download / crack / 下载 / 破解”去吸引流量。
- 不发布泄露版本的实机截图。移植进度页的“每个阶段长什么样”用的是 CSS 示意图，保持这样。
- 图片只用 Rockstar 官方素材（`static/img/` 里的 11 张都来自 rockstargames.com/VI），并保留“截图：Rockstar Games”的署名。项目卡片可以链新闻、追踪站结论和 GitHub 上的 DMCA 通知原文，不要链移植仓库、Discord 邀请、种子或可执行文件。

## 已知限制 / 待办

- `privacy` 页的文字是通用写法（提到 Vercel 日志和可能的统计、广告 Cookie）。已和当前生产的 `page_legal` 对过，两边是同一段，仓库里没有更具体的版本。
- 中文 404 页（`out/zh/404.html`）已经生成，但 Vercel 默认对所有不存在的地址都返回根目录的 `404.html`（英文版），这个可以接受。
- 新站没有接入统计代码（旧站也没有）。如果要加，写在 `build.py` 的 `head()` 里。
- 构建已在 Python 3.11 和 3.13 下验证通过，只用标准库，不需要 pip install。

## 交接时已验证的项目

- `python3 build.py && python3 tools/check.py`：125 个 HTML 页面，120 个 sitemap URL，检查通过。内容页 112 个都带 `adsterra-config` 和 `/adsterra/runtime.js`；privacy、terms、四种语言的 404、以及 `/play/` 都没有。`out/adsterra/runtime.js` 有复制出来。
- 本地按 cleanUrls 打开过 `/`、`/zh`、`/es`、`/pt-br`、发售日、配置、移植进度、FAQ、FPS、Online、新闻和一篇文章、隐私、条款、`/play/`、`/og-image.png`、`/adsterra/runtime.js`、sitemap、robots，都是 200。`/does-not-exist` 是 404，正文是 “Page not found”，没有广告脚本。
- `/news/xbox-executable` 不是静态文件。生产 `vercel.json` 把它 301 到 `/cyberleek-leak`。
- 西语和葡语这次构建没有缺译（`untranslated strings` 没有出现）。
- 首页官方结论仍是 “Not officially.” / “官方还没有。” / “No oficialmente.” / “Não oficialmente.” 民间移植的帧数是带来源的报道，不是 Rockstar 公布了 PC 版。
- 移植页的 AMD / NVIDIA 筛选会给卡片设 `hidden`。`.pcard` 用了 `display: grid`，会盖掉浏览器默认的 `[hidden]`，所以 `site.css` 里有 `.pcard[hidden] { display: none; }`。浏览器里点 NVIDIA 后 Belobug 会从页面上消失，再点 All 会回来。
