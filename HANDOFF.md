# gta6pc.org 改版：上线交接说明

给负责上线的 Agent。按顺序做，每一步都有验证方法。

## 这是什么

gta6pc.org 的整站改版。旧站是 Vite + React 单页应用，只有 3 个页面，HTML 里只有 `<div id="root">`。新站是 Python 生成的纯静态 HTML，中英双语，每种语言 11 个页面，部署在原来的 Vercel 项目上。

- 预览（只有站长能看）：https://claude.ai/artifact/Xe8BkryXNDjMXuD66BZZkT
- 内容快照时间：2026-11-24 11:30 UTC

## 目录

| 路径 | 用途 |
|---|---|
| `build.py` | 生成器。`python3 build.py` 输出到 `out/`（上线用）；`python3 build.py preview` 输出到 `preview/`（平铺文件、相对链接，只用于预览） |
| `data/status.json` | 首页状态台三盏灯、移植统计数字、更新时间 |
| `data/projects.json` | 移植追踪表的 14 个项目 |
| `data/news.json` | 新闻流（首页取最新 5 条，/news 显示全部，泄露页取泄露和移植相关条目） |
| `data/ads.json` | Adsterra 广告配置（从旧站原样搬过来的 Popunder + Social Bar 地址） |
| `static/` | `site.css` 和 8 张 Rockstar 官方截图，部署到 `/static/` |
| `legacy/` | 旧站保留的文件，构建时原样复制进 `out/`：`play/`（Neon Bay 小游戏）、`og-image.png`、`adsterra/runtime.js` |
| `tools/check.py` | 上线前检查：内部链接、重复的 title/description/H1、占位文字、sitemap |
| `vercel.json` | 构建命令、输出目录、`cleanUrls`、静态资源缓存头 |
| `docs/plan.html` | 改版方案（用户意图、真伪核查、页面矩阵） |
| `research/` | Google 联想词原始数据、意图表 |

## URL 表

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
| `/news` | `/zh/news` | 新闻（新） |
| `/privacy`、`/terms` | `/zh/privacy`、`/zh/terms` | 法律页（不放广告） |
| `/play/` | — | Neon Bay 小游戏（旧文件，原样保留） |

每个页面都有 canonical、hreflang（en / zh-CN / x-default）、OG 标签和 JSON-LD（WebPage、BreadcrumbList，有问答的页面加 FAQPage）。`sitemap.xml` 有 22 个 URL，每个都带 hreflang 互指。

旧文 `/news/xbox-executable`（带或不带结尾斜杠）在 `vercel.json` 里 301 到 `/cyberleek-leak`。`www.gta6pc.org` 仍 301 到 apex。没有 SPA 兜底 rewrite。

## 本轮先不接广告（2026-11-24）

`data/ads.json` 里两个脚本地址已和现网 `https://gta6pc.org/` 核对，是同一套 Popunder（`abscloud.org`）和 Social Bar（`bauval.org`）。`enabled` 现为 `false`，构建出的 HTML 不会请求它们。等这一版进入生产后，再按站长指令打开，并且不要新开广告位、不要换成别的站的代码。注意：`enabled` 改回 `true` 时，`build.py` 会把这两条脚本放到除隐私页和条款页以外的全部内容页，比现网只允许 `/`、`/release-date`、`/pc-specs` 更宽，接线时要按当时的决定收窄或保留。

## 上线步骤

### 1. 放进仓库

找到 Vercel 上 gta6pc.org 项目连接的那个 GitHub 仓库。

- 新开一个分支，比如 `redesign-static`。
- 删除旧的 Vite 源码（`src/`、`index.html`、`vite.config.*`、`package.json` 等）。删之前把旧仓库 `public/` 里的 `play/`、`og-image.png`、`adsterra/runtime.js`、favicon 复制到本包的 `legacy/`，覆盖本包里的快照，因为旧仓库里的文件可能比快照新。
- 把本包所有文件放到仓库根目录，提交并推送。

本包自带一个 git 仓库（`main` 分支，一个提交）。如果想保留这段历史，可以 `git remote add origin <仓库地址>` 后推送到新分支。

### 2. Vercel 设置

- Framework Preset 改为 **Other**。构建命令和输出目录由 `vercel.json` 指定（`python3 build.py` → `out`）。
- 删掉旧的 SPA 兜底 rewrite（例如 `"rewrites": [{"source": "/(.*)", "destination": "/index.html"}]`），不管它在旧的 `vercel.json` 里还是在项目设置里。旧站任何不存在的地址都返回 200，新站必须对不存在的地址返回真正的 404。
- 如果 Vercel 构建环境报找不到 `python3`：把构建命令留空，在本地跑 `python3 build.py`，然后把 `out/` 提交上去（同时从 `.gitignore` 里去掉 `out/`）。

### 3. 用 Preview 部署验证

推送分支后，Vercel 会给一个 preview 地址。逐项检查：

```bash
BASE=https://<preview 域名>
for u in / /release-date /pc-specs /pc-port-tracker /cyberleek-leak /how-to-play-gta-6-on-pc /is-gta-6-pc-download-safe /steam /news /privacy /terms /zh /zh/pc-port-tracker /play/ /og-image.png /adsterra/runtime.js /sitemap.xml /robots.txt /does-not-exist; do printf "%-34s %s\n" "$u" "$(curl -s -o /dev/null -w '%{http_code}' $BASE$u)"; done
```

预期：最后一个 `/does-not-exist` 返回 404，其余都是 200。

再用浏览器打开 `/` 和 `/privacy`。本轮 `ads.json` 的 `enabled` 是 `false`，两个页面都不应该请求 `abscloud.org` 或 `bauval.org`。下一轮打开广告之后，首页才会请求这两条现有脚本，`/privacy` 仍然不应该请求。

### 4. 上生产

- Promote 到 production（或合并到生产分支）。
- Google Search Console：重新提交 `https://gta6pc.org/sitemap.xml`，并对 `/`、`/pc-port-tracker`、`/cyberleek-leak` 请求编入索引。

## 日常更新（重要）

移植进度一天内会变好几次。至少每天更新一次：

1. 改 `data/` 下的 JSON：
   - `status.json`：`updated`、`updated_label`（中英两个都改）、三盏灯的文字、`port_stats` 里的数字
   - `projects.json`：每个项目的 `stage`（1–7）、`halted`、`note`（中英各一句）
   - `news.json`：在数组里加一条，`tag` 取 `port` / `leak` / `official` / `report` / `legal` / `security`，中英各写一个标题和一句话
2. 运行：

```bash
python3 build.py && python3 tools/check.py
```

3. 提交并推送，Vercel 会自动部署。

进度数据来源：GTA VI PC Race（vuyp.github.io/gta6-pc-race）、Six on PC（sixonpc.com）。每条事实都要交叉核对，只有单一来源的写成“报道称 / 自述”。

需要改状态台三盏灯的时机：Rockstar 正式公布 PC 版；或任何民间项目经证实达到第 6 阶段（能操控角色）。到时候同时改首页 H1 下面那句话（在 `build.py` 的 `page_home` 里）。

改页面文案就直接改 `build.py`，每段文案都是 `t("English", "中文")` 两个版本挨着写。

## 红线

- **不链接**任何泄露文件、EXE、种子、网盘，也不链接需要泄露文件才能用的移植仓库（GitHub、Discord 都不行）。页面上只写项目名。
- 不在标题、锚文本里用“download / crack / 下载 / 破解”去吸引流量。
- 不发布泄露版本的实机截图。移植进度页的“每个阶段长什么样”用的是 CSS 示意图，保持这样。
- 图片只用 Rockstar 官方素材（`static/img/` 里的 8 张都来自 rockstargames.com/VI），并保留“截图：Rockstar Games”的署名。

## 已知限制 / 待办

- `privacy` 页的文字是通用写法（提到 Vercel 日志和可能的统计、广告 Cookie）。如果旧站的隐私政策写得更具体，请用旧站的版本替换 `build.py` 里 `page_legal` 的内容。
- 中文 404 页（`out/zh/404.html`）已经生成，但 Vercel 默认对所有不存在的地址都返回根目录的 `404.html`（英文版），这个可以接受。
- 新站没有接入统计代码（旧站也没有）。如果要加，写在 `build.py` 的 `head()` 里。
- 构建已在 Python 3.11 和 3.13 下验证通过，只用标准库，不需要 pip install。

## 交接时已验证的项目

- `python3 tools/check.py`：25 个 HTML 页面，内部链接 0 个坏链；title、description、H1 无重复；sitemap 22 个 URL 全部对应到真实页面。
- 本地用 `serve`（同样开了 clean URLs）请求了 22 个地址，全部返回预期状态码，不存在的地址返回 404。
- 浏览器加载英文首页、中文首页、移植进度、中文下载安全页、隐私页：没有 JS 报错；广告只在内容页加载，隐私页没有；桌面 1366 和手机 390 宽度下都没有横向滚动。
