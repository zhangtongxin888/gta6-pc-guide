import { CalendarClock, Clock, TrendingUp, AlertTriangle, CheckCircle2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

const history = [
  { game: 'GTA 3', console: '2001-10-22', pc: '2002-05-21', months: 7, note: 'PS2 首发' },
  { game: 'GTA: Vice City', console: '2002-10-29', pc: '2003-05-13', months: 6.5, note: 'PS2 首发' },
  { game: 'GTA: San Andreas', console: '2004-10-26', pc: '2005-06-07', months: 7.5, note: 'PS2 首发' },
  { game: 'GTA 4', console: '2008-04-29', pc: '2008-12-02', months: 7, note: 'PS3 / Xbox 360' },
  { game: 'GTA 5', console: '2013-09-17', pc: '2015-04-14', months: 19, note: '中间隔了一代主机移植' },
  { game: '荒野大镖客 2', console: '2018-10-26', pc: '2019-11-05', months: 12, note: 'R 星最近一部大作' },
]

const gta6Timeline = [
  { date: '2023 年 12 月', event: '首支预告片发布，官宣 2025 年发售', status: 'done' as const },
  { date: '2025 年 5 月', event: '第一次跳票：定档 2026 年 5 月 26 日', status: 'done' as const },
  { date: '2026 年 4 月', event: '第二次跳票：推迟至 2026 年 11 月 19 日', status: 'done' as const },
  { date: '2026 年 6 月', event: '预购开启；官网一度移除具体发售日期，再引猜测', status: 'done' as const },
  { date: '2026 年 11 月 19 日', event: '主机版发售（PS5 / PS5 Pro / Xbox Series X|S）', status: 'future' as const },
  { date: '待定', event: 'PC 版：R 星至今只字未提', status: 'unknown' as const },
]

const scenarios = [
  {
    name: '乐观情景',
    window: '2027 年年中',
    gap: '主机版后约 7~8 个月',
    probability: '可能性较低',
    color: '#22e5ee',
    desc: '对标 GTA 4 时代 7 个月的间隔。前提是 R 星在主机版开发后期已同步推进 PC 移植，且不再跳票。',
  },
  {
    name: '基准情景',
    window: '2027 年底 ~ 2028 年初',
    gap: '主机版后约 12~15 个月',
    probability: '可能性最高',
    color: '#ff4da6',
    desc: '对标 RDR2 的 12 个月间隔，叠加圣诞档期与 R 星偏爱周二发售的习惯，2027 年 11 月前后是最合理的点估计。',
  },
  {
    name: '悲观情景',
    window: '2028 年中及以后',
    gap: '主机版后约 18 个月以上',
    probability: '需要警惕',
    color: '#f59e0b',
    desc: 'GTA 6 体量空前、PC 平台组合复杂，若 PC 版像 GTA 5 一样多次跳票，或主机版本身再延期，等待将进一步拉长。',
  },
]

export default function ReleaseDate() {
  return (
    <div className="mx-auto max-w-6xl px-4 pt-14">
      {/* header */}
      <div className="text-center mb-12">
        <Badge variant="outline" className="mb-4 border-[#ff4da6]/40 text-[#ff4da6]">
          <CalendarClock className="w-3.5 h-3.5 mr-1.5" />
          问题一 · 发售时间
        </Badge>
        <h1 className="font-display text-4xl sm:text-5xl tracking-tight">
          <span className="text-gradient-sunset">GTA 6 什么时候上 PC？</span>
        </h1>
        <p className="mt-4 text-muted-foreground max-w-2xl mx-auto text-sm sm:text-base leading-relaxed">
          一句话回答：<strong className="text-foreground">官方没有说，但历史规律指向 2027 年底。</strong>
          下面是完整的推导过程。
        </p>
      </div>

      {/* conclusion card */}
      <Card className="bg-card/90 border-[#ff4da6]/30 neon-box-pink mb-14">
        <CardContent className="p-6 sm:p-10 text-center">
          <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground mb-3">我们的预测</p>
          <p className="font-display text-3xl sm:text-5xl neon-pink">2027 年 11 月前后</p>
          <p className="mt-4 text-sm text-muted-foreground">
            置信窗口：<strong className="text-foreground">2027 年 11 月 ~ 2028 年 5 月</strong>
            （主机版发售后约 12~18 个月）
          </p>
          <p className="mt-2 text-xs text-muted-foreground/70">
            前提：主机版按当前定档的 2026 年 11 月 19 日如期发售
          </p>
        </CardContent>
      </Card>

      {/* GTA 6 timeline */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
          <Clock className="w-5 h-5 text-[#22e5ee]" />
          GTA 6 的官方时间线
        </h2>
        <p className="text-sm text-muted-foreground mb-8">
          理解 PC 版何时来，先看主机版走到了哪一步——它已经跳票两次。
        </p>
        <div className="relative pl-6 sm:pl-8">
          <div className="absolute left-[7px] sm:left-[11px] top-2 bottom-2 w-px bg-gradient-to-b from-[#22e5ee] via-[#ff4da6] to-white/10" />
          <div className="space-y-6">
            {gta6Timeline.map((t) => (
              <div key={t.date} className="relative">
                <span
                  className={`absolute -left-6 sm:-left-8 top-1.5 w-3.5 h-3.5 rounded-full border-2 ${
                    t.status === 'done'
                      ? 'bg-[#22e5ee] border-[#22e5ee]/40'
                      : t.status === 'future'
                        ? 'bg-[#ff4da6] border-[#ff4da6]/40 animate-pulse'
                        : 'bg-transparent border-dashed border-white/40'
                  }`}
                />
                <p className="text-xs text-muted-foreground">{t.date}</p>
                <p
                  className={`text-sm sm:text-base font-medium ${
                    t.status === 'unknown' ? 'text-muted-foreground italic' : ''
                  }`}
                >
                  {t.event}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* history table */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-[#ff4da6]" />
          历史规律：R 星的 PC 版总是迟到
        </h2>
        <p className="text-sm text-muted-foreground mb-8">
          过去 25 年，R 星从未让 PC 版与主机版同步发售。间隔从半年到一年半不等：
        </p>
        <Card className="bg-card/90 border-white/10 overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="border-white/10 hover:bg-transparent">
                <TableHead className="text-muted-foreground">作品</TableHead>
                <TableHead className="text-muted-foreground">主机首发</TableHead>
                <TableHead className="text-muted-foreground">PC 发售</TableHead>
                <TableHead className="text-muted-foreground text-right">间隔</TableHead>
                <TableHead className="text-muted-foreground hidden md:table-cell w-[38%]">
                  间隔可视化
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {history.map((h) => (
                <TableRow key={h.game} className="border-white/5">
                  <TableCell className="font-medium">
                    {h.game}
                    <span className="block text-[11px] text-muted-foreground font-normal">
                      {h.note}
                    </span>
                  </TableCell>
                  <TableCell className="text-muted-foreground whitespace-nowrap">{h.console}</TableCell>
                  <TableCell className="whitespace-nowrap">{h.pc}</TableCell>
                  <TableCell className="text-right font-semibold text-[#22e5ee] whitespace-nowrap">
                    {h.months} 个月
                  </TableCell>
                  <TableCell className="hidden md:table-cell">
                    <div className="h-2 rounded-full bg-white/5 overflow-hidden">
                      <div
                        className="h-full rounded-full"
                        style={{
                          width: `${(h.months / 19) * 100}%`,
                          background:
                            h.months > 12
                              ? 'linear-gradient(90deg,#f59e0b,#ff4da6)'
                              : 'linear-gradient(90deg,#22e5ee,#7c9cff)',
                        }}
                      />
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>

        {/* GTA5 deep dive */}
        <Card className="bg-card/90 border-white/10 mt-6">
          <CardHeader>
            <CardTitle className="text-lg">重点复盘：GTA 5 那 19 个月是怎么来的？</CardTitle>
          </CardHeader>
          <CardContent className="text-sm leading-relaxed text-muted-foreground space-y-3">
            <p>
              <strong className="text-foreground">2013 年 9 月 17 日</strong>，GTA 5 在 PS3 / Xbox 360 首发。
              玩家原以为 PC 版会像 GTA 4 一样半年就到，但 R 星先做了
              <strong className="text-foreground">次世代主机移植</strong>——
              2014 年 11 月 18 日登陆 PS4 / Xbox One，PC 版则被一路推迟：
              原定 2014 年秋，三度跳票后直到
              <strong className="text-foreground"> 2015 年 4 月 14 日</strong>才发售。
            </p>
            <p>
              也就是说，19 个月里包含了一次「中间隔代移植」和 PC 版自身的三次跳票。
              <strong className="text-[#22e5ee]">
                GTA 6 首发即当代主机（PS5 / Xbox Series），不存在隔代移植
              </strong>
              ，这是它比 GTA 5 更快登陆 PC 的最大利好；但 PC 版反复跳票的风险依然存在。
            </p>
          </CardContent>
        </Card>
      </section>

      {/* scenarios */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-2">三种情景推演</h2>
        <p className="text-sm text-muted-foreground mb-8">
          以 2026 年 11 月 19 日主机版发售为基准，PC 版的可能落点：
        </p>
        <div className="grid md:grid-cols-3 gap-5">
          {scenarios.map((s) => (
            <Card key={s.name} className="bg-card/90 border-white/10 flex flex-col">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">{s.name}</CardTitle>
                  <Badge
                    variant="outline"
                    style={{ color: s.color, borderColor: `${s.color}55` }}
                    className="text-[11px]"
                  >
                    {s.probability}
                  </Badge>
                </div>
                <p className="font-display text-2xl" style={{ color: s.color }}>
                  {s.window}
                </p>
                <p className="text-[11px] text-muted-foreground">{s.gap}</p>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground leading-relaxed flex-1">
                {s.desc}
              </CardContent>
            </Card>
          ))}
        </div>

        {/* visual window bar */}
        <Card className="bg-card/90 border-white/10 mt-8">
          <CardContent className="p-6">
            <p className="text-xs text-muted-foreground mb-4">预测窗口一览（2026.11 主机版 → PC 版）</p>
            <div className="relative h-24">
              {/* axis */}
              <div className="absolute left-0 right-0 top-1/2 h-px bg-white/15" />
              {/* year ticks */}
              {['2026.11', '2027.05', '2027.11', '2028.05', '2028.11'].map((label, i) => (
                <div
                  key={label}
                  className="absolute top-1/2 -translate-x-1/2"
                  style={{ left: `${(i / 4) * 100}%` }}
                >
                  <div className="w-px h-3 bg-white/30 mx-auto -mt-1.5" />
                  <p className="mt-2 text-[10px] text-muted-foreground whitespace-nowrap">{label}</p>
                </div>
              ))}
              {/* optimistic: mid 2027 */}
              <div
                className="absolute top-[12%] h-2.5 rounded-full bg-gradient-to-r from-[#22e5ee] to-[#22e5ee]/40"
                style={{ left: '12.5%', width: '12.5%' }}
                title="乐观：2027 年中"
              />
              {/* base: Nov 2027 - May 2028 */}
              <div
                className="absolute top-[27%] h-3.5 rounded-full bg-gradient-to-r from-[#ff4da6] to-[#ff7b54] neon-box-pink"
                style={{ left: '50%', width: '25%' }}
                title="基准：2027 年底 ~ 2028 年初"
              />
              {/* pessimistic: mid 2028+ */}
              <div
                className="absolute top-[42%] h-2.5 rounded-full bg-gradient-to-r from-amber-400/70 to-amber-400/25"
                style={{ left: '75%', width: '25%' }}
                title="悲观：2028 年中以后"
              />
            </div>
            <div className="flex flex-wrap gap-x-5 gap-y-1 mt-2 text-[11px] text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#22e5ee]" /> 乐观
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#ff4da6]" /> 基准（重点关注）
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400" /> 悲观
              </span>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* why */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-8">支撑这个判断的三个理由</h2>
        <div className="grid sm:grid-cols-3 gap-5">
          {[
            {
              title: 'RDR2 是最接近的参照',
              desc: '同为当代主机首发、同为 RAGE 引擎开放世界大作，RDR2 从主机到 PC 恰好 12 个月。GTA 6 的商业结构与之最相似。',
            },
            {
              title: '没有隔代移植拖后腿',
              desc: 'GTA 5 的 19 个月很大程度耗在 PS4/Xbox One 移植上。GTA 6 首发 PS5/XSX，PC 与主机共用 x86 架构，移植链路更短。',
            },
            {
              title: '但 R 星永远把 PC 放在第二步',
              desc: '先主机后 PC 是 R 星的商业策略（首发销量 + 双重购买），前 GTA 4 开发者也公开预测 PC 版要等到 2027 年。指望同步发售不现实。',
            },
          ].map((r) => (
            <Card key={r.title} className="bg-card/90 border-white/10">
              <CardContent className="p-6">
                <CheckCircle2 className="w-5 h-5 text-[#22e5ee] mb-3" />
                <h3 className="font-semibold mb-2">{r.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{r.desc}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 flex gap-3 items-start">
        <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <p className="text-xs text-muted-foreground leading-relaxed">
          重要提醒：截至 2026 年 7 月，Rockstar 未对 PC 版发布任何官方信息，以上全部是基于历史数据的推演。
          若主机版再度跳票，本预测窗口将整体顺延。另外，官网曾在 2026 年 6 月短暂移除 11 月 19 日的日期标识，
          说明时间节点仍存在变数。
        </p>
      </div>
    </div>
  )
}
