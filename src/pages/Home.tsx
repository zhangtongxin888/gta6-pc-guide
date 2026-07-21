import { Link } from 'react-router'
import { ArrowRight, CalendarClock, Cpu, AlertTriangle } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

const entries = [
  {
    to: '/release-date',
    icon: CalendarClock,
    color: 'pink' as const,
    title: 'GTA 6 什么时候上 PC？',
    desc: '复盘 GTA 5 从主机到 PC 长达 19 个月的等待，结合 R 星历代作品的发售规律，推算 GTA 6 PC 版最可能的时间窗口。',
    tag: '结论先行：预计 2027 年底',
  },
  {
    to: '/pc-specs',
    icon: Cpu,
    color: 'cyan' as const,
    title: 'PC 需要什么样的配置？',
    desc: '以 PS5 / PS5 Pro 的硬件性能为锚点，拆解 CPU、显卡、显存与 SSD 需求，给出三档预测配置单。',
    tag: '起步门槛：16GB 内存 + NVMe SSD',
  },
]

export default function Home() {
  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="sunset-gradient absolute inset-x-0 top-0 h-[26rem] opacity-90" aria-hidden />
        {/* sun */}
        <div
          className="absolute left-1/2 top-24 -translate-x-1/2 w-56 h-56 rounded-full opacity-90"
          style={{
            background:
              'linear-gradient(180deg, #ffd76b 0%, #ff7b54 55%, #ff4da6 100%)',
            boxShadow: '0 0 90px 30px rgba(255, 123, 84, 0.45)',
          }}
          aria-hidden
        />
        {/* skyline silhouette */}
        <svg
          className="absolute bottom-0 inset-x-0 w-full h-40 text-[#12082b]"
          viewBox="0 0 1200 160"
          preserveAspectRatio="none"
          aria-hidden
        >
          <path
            fill="currentColor"
            d="M0 160 V120 h40 v-30 h25 v30 h30 V80 h35 v40 h20 v-15 h30 v15 h45 V60 h30 V45 h25 v15 h30 v60 h40 V95 h35 v25 h25 V70 h40 v50 h30 v-20 h35 v20 h50 V55 h30 v-20 h20 v20 h30 v65 h45 V90 h30 v30 h40 V65 h35 v55 h30 v-25 h40 v25 h40 V75 h45 v45 h30 v-30 h35 v30 h40 v40 Z"
          />
        </svg>

        <div className="relative mx-auto max-w-6xl px-4 pt-24 pb-44 text-center">
          <Badge
            variant="outline"
            className="mb-6 border-white/30 bg-black/30 text-white backdrop-blur px-4 py-1"
          >
            主机版定档 2026 年 11 月 19 日 · PC 版仍待官宣
          </Badge>
          <h1 className="font-display leading-none">
            <span className="block text-6xl sm:text-8xl tracking-tight text-white drop-shadow-[0_4px_24px_rgba(0,0,0,0.6)]">
              GTA VI
            </span>
            <span className="block mt-3 text-3xl sm:text-5xl tracking-wide text-white/95 drop-shadow-[0_2px_12px_rgba(0,0,0,0.6)]">
              PC 玩家等待指南
            </span>
          </h1>
          <p className="mt-6 text-sm sm:text-base text-white/85 max-w-xl mx-auto drop-shadow-[0_1px_8px_rgba(0,0,0,0.5)]">
            PC 版什么时候来？电脑要不要提前升级？
            <br className="hidden sm:block" />
            我们用历史数据和硬件分析，回答这两个 PC 玩家最关心的问题。
          </p>
        </div>
      </section>

      {/* Entry cards */}
      <section className="mx-auto max-w-6xl px-4 -mt-16 relative z-10">
        <div className="grid md:grid-cols-2 gap-6">
          {entries.map((e) => {
            const Icon = e.icon
            const isPink = e.color === 'pink'
            return (
              <Link key={e.to} to={e.to} className="group">
                <Card
                  className={`h-full bg-card/90 backdrop-blur border-white/10 transition-all duration-300 group-hover:-translate-y-1.5 ${
                    isPink ? 'group-hover:neon-box-pink' : 'group-hover:neon-box-cyan'
                  }`}
                >
                  <CardContent className="p-6 sm:p-8 flex flex-col h-full">
                    <div
                      className={`w-12 h-12 rounded-xl flex items-center justify-center mb-5 ${
                        isPink
                          ? 'bg-[#ff4da6]/15 text-[#ff4da6]'
                          : 'bg-[#22e5ee]/15 text-[#22e5ee]'
                      }`}
                    >
                      <Icon className="w-6 h-6" />
                    </div>
                    <h2 className="text-xl sm:text-2xl font-bold mb-3">{e.title}</h2>
                    <p className="text-sm text-muted-foreground leading-relaxed flex-1">
                      {e.desc}
                    </p>
                    <div className="mt-6 flex items-center justify-between">
                      <span
                        className={`text-xs font-medium ${isPink ? 'text-[#ff4da6]' : 'text-[#22e5ee]'}`}
                      >
                        {e.tag}
                      </span>
                      <ArrowRight
                        className={`w-5 h-5 transition-transform group-hover:translate-x-1.5 ${
                          isPink ? 'text-[#ff4da6]' : 'text-[#22e5ee]'
                        }`}
                      />
                    </div>
                  </CardContent>
                </Card>
              </Link>
            )
          })}
        </div>
      </section>

      {/* Quick facts */}
      <section className="mx-auto max-w-6xl px-4 mt-14">
        <div className="rounded-2xl border border-amber-400/20 bg-amber-400/5 p-5 sm:p-6 flex gap-4 items-start">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div className="text-sm leading-relaxed text-amber-100/80">
            <p className="font-semibold text-amber-300 mb-1">当前状态速览（2026 年 7 月）</p>
            Rockstar 至今<strong className="text-amber-200">未公布任何 PC 版计划</strong>——这符合其一贯做法：历代 GTA
            的 PC 版均在主机版发售后才正式宣布。主机版已两度跳票（2025 秋 → 2026 年 5 月 26 日 → 2026 年 11 月 19 日），
            PC 版的等待注定更漫长，一切预测都建立在主机版如期发售的前提上。
          </div>
        </div>
      </section>
    </div>
  )
}
