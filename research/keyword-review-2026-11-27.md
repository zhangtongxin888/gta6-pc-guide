# 关键词复盘（2026-11-27）

输入：`04-查量.tsv`（DataForSEO，美国，12 个月平均，逐月到 2026-10）、`google-serp.md`（10 个词的前 20，2026-11-26）、上一版《可加内页清单》、2026-11-27 Google 联想词（`google_suggest_2026-11-27.txt`）。

## 1. 量在哪里

| 词簇 | 代表词（月均 / 2026-10） | 合计月均 | 落地页 |
|---|---|---|---|
| 有没有 PC 版 | gta 6 pc、gta 6 on pc、grand theft auto 6 pc（各 40,500 / 110,000）；will gta 6 be on pc 14,800；gta vi pc 3,600；is gta 6 on pc 1,600；can you play gta 6 on pc 880 | 约 14 万 | 首页 |
| 发售日 | gta 6 pc release date 40,500 / 90,500；when is gta 6 coming to pc 2,400；gta 6 coming to pc 480；will gta 6 be on pc at launch 320 | 约 4.4 万 | /release-date |
| 配置 | gta 6 pc requirements 3,600；system requirements 1,300；pc specs 590；can my pc run gta 6 320 / 1,900 | 约 6,000 | /pc-specs |
| 商店 / 价格 | gta 6 steam 3,600（CPC 3.84，全表最高的大词出价）；pc pre order 720；game pass 480；steam release date 480；pc price 140 | 约 5,700 | /steam |
| 移植 | gta 6 pc port 210 / 1,000；tracker、progress、status、race 均未收录 | 广告数据看不到 | /pc-port-tracker |
| 主机意图 | gta 6 file size 8,100 / 49,500；is gta 6 delayed 1,600；ultimate edition worth it 590 | — | 不新开页 |

广告数据只到 10 月，主机发售（11/19）、Xbox 包泄露（11/19）、EXE 放出（11/23）都在这之后。所以移植相关的需求在这张表里几乎看不到，但联想词里 “gta 6 pc” 的前 10 条已有 4 条是 tracker / progress。

## 2. 和上一版清单相比，哪些判断变了

1. **“不往民间移植方向做”这条不再成立。** 前 20 里已经大量是移植新闻：Windows Central（Windows 上跑起来了）、Tom's Hardware（3,007 个仓库被删）、Yahoo、Hacker News、NeoGAF。“can my pc run gta 6”的 AI 摘要也提到了 early compatibility projects。Google 已经把移植当作 PC 查询的相关内容。仍然成立的是：别写得像官方 PC 版能买、能玩。新首页是“官方还没有”，和所有 AI 摘要的口径一致。
2. **直接竞品出现了：portwatchvi.com。** 它是 PortWatch 的配套站（页面里链向 portwatch-vi.xyz 169 次），标题是“Is GTA 6 on PC? Release Status, Port Progress & FAQ”，和我们的定位几乎一样。它的 /pc-release-date 已排进“will gta 6 be on pc at launch”第 11 位，站上共 8 个页面，含 38 条问答和一个葡萄牙语页（/pt-br/gta-6-no-pc）。
3. **“能不能跑”的小工具值得做。** 上一版担心工具会暗示 PC 版可玩。但“can my pc run gta 6”的前 20 里，工具类页面排得很靠前：第 1 的 pcgamebenchmark（预测）、第 5 的 gtabites 测试工具、第 2 页的 pc-builds 帧数计算器和 gta6test.com。这个词 10 月量是 1,900，联想里还有 fps calculator。建议放在 /pc-specs 页里，不单开页：选显卡和 CPU，告诉你落在哪一档，明确是对官方 PC 版的估算。
4. **新闻需要独立网址。** 几乎每个词的结果页都有 Top stories 模块。PortWatch 每条新闻一个页面，还有 RSS；我们只有一个 /news 汇总页，进不了 Top stories。

## 3. 同意上一版的地方

不新开页、只加厚现有页的词：file size、ultimate edition、is gta 6 delayed、pc pre order、pc price、xbox app、play anywhere、at launch、pc delay。理由和上一版一致。

## 4. 优化清单（按量排序）

1. **首页**（约 14 万）
   - title 里把 Specs 换成 Requirements（requirements 3,600 对 specs 590）。
   - description 加上 “GTA VI”（gta vi pc 3,600）。
   - FAQ 加一条“Will GTA 6 be on PC?”（14,800）。答案和“出了吗”不同：几乎肯定会出，GTA III 以来每部正传都上了 PC，报道的目标是 2027 年 Q1。
2. **发售日页**（约 4.4 万）
   - title 改成“GTA 6 PC Release Date: When Is GTA 6 Coming to PC?”。
   - 加入 gamegpu 的“2027 年 3 月、与 GTA 6 Online 同步上 PC”这一说法（未证实，和 Q1 窗口吻合；前 20 里 gamegpu 和 shattered.io 都有）。
   - FAQ 写死两句：发售当天没有 PC 版；官方从没给过 PC 日期，所以谈不上“延期”。
3. **配置页**（约 6,000）
   - 加“能不能跑”小工具。
   - 加体积小节：PS5 212 GB 已确认（Push Square）、泄露的 Xbox 包 209 GB、有人把体积压缩到 167 GB 的新闻（gamegpu）、PC 版体积未公布，建议预留 250 GB。
   - 加一条笔记本能不能跑的问答。
4. **Steam 页**（约 5,700，出价最高）
   - title 对准“GTA 6 Steam”。
   - 写清主机版 $80 标准版、$100 终极版，PC 版价格和预购都没公布，别把主机价当 PC 价。
5. **现在怎么玩页**
   - 标题和 FAQ 里出现“Xbox app”。
   - 补一条：不支持 Xbox Play Anywhere，买 Xbox 版不能装到 Windows 上。
   - 引用 Xbox Wire 11/23 的官方文章《How to Play Grand Theft Auto VI in the Cloud and with Remote Play》。
6. **移植进度页**：广告数据看不到它的量，上线后靠 GSC 观察。每张卡片加锚点（如 /pc-port-tracker#belobug），对应联想里出现的项目名。
7. **新闻**：重要新闻各生成一个文章页，加 RSS。
8. **多语言**：竞品已经做了葡萄牙语。上线后先看 GSC 的国家分布再决定加哪种语言。

## 5. 数据口径

- 月量是 12 个月平均，不含 11 月，主机发售后的变化看不到。
- 前 20 是个性化结果（登录账号、Kansas），名次可能差一两位，结论只看意图和页面类型。
- 趋势未查。
