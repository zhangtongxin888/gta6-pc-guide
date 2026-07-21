import { Cpu, MemoryStick, HardDrive, MonitorPlay, Zap, AlertTriangle, Info } from 'lucide-react'
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

const ps5Specs = [
  { label: 'CPU', value: '8 核 AMD Zen 2 @ 3.5GHz', note: '约等于桌面级 Ryzen 7 3700X 的降频版' },
  { label: 'GPU', value: 'RDNA 2 · 36CU · 10.28 TFLOPS', note: '光栅性能约等于 RTX 2070 Super / RX 6700' },
  { label: '内存', value: '16GB GDDR6 统一内存', note: '游戏实际可用约 12~13GB，显存内存共享' },
  { label: '存储', value: '定制 NVMe SSD · 5.5GB/s', note: '支撑无缝开放世界流式加载' },
]

const tiers = [
  {
    name: '入门档',
    target: '1080p / 30fps · 低画质',
    color: '#22e5ee',
    cpu: 'Ryzen 5 3600 / i5-10400',
    gpu: 'RTX 3060 12GB / RX 6600 XT',
    ram: '16GB DDR4',
    storage: 'NVMe SSD · 200GB 可用空间',
    note: '对标「等于或略强于 PS5」的体验。1080p 下用低画质+上采样技术（DLSS/FSR）可以运行，但别指望流畅度超过主机。',
  },
  {
    name: '推荐档',
    target: '1440p / 60fps · 高画质',
    color: '#ff4da6',
    cpu: 'Ryzen 7 7700X / i5-13600K',
    gpu: 'RTX 4070 Super / RX 7800 XT',
    ram: '32GB DDR5',
    storage: 'PCIe 4.0 NVMe SSD · 200GB',
    note: '大多数玩家值得瞄准的甜点档。明显超越主机的分辨率和帧率，高画质下开启上采样可稳 60fps。',
  },
  {
    name: '发烧档',
    target: '4K / 60fps · 光追拉满',
    color: '#f59e0b',
    cpu: 'Ryzen 7 9800X3D / i7-14700K',
    gpu: 'RTX 5080 / RX 9070 XT 及以上',
    ram: '32GB DDR5（高频低延迟）',
    storage: 'PCIe 4.0/5.0 NVMe SSD',
    note: '预告片里密集的全局光照与反射效果，暗示 RAGE 引擎光追负载不轻。4K 光追全开需要旗舰显卡，X3D 处理器缓解 CPU 瓶颈。',
  },
]

const analysis = [
  {
    icon: MonitorPlay,
    title: '显卡：PS5 的 10 TFLOPS 只是起点',
    color: '#ff4da6',
    points: [
      'PS5 GPU 光栅性能约等于 RTX 2070 Super，PC 版要「追平主机体验」，RTX 3060 级别是底线。',
      '但主机有深度定制优化，PC 通常需要 20%~30% 的性能冗余才能打平，所以推荐档直接跳到 4070 Super 级别。',
      '预告片展示的水面反射、霓虹全局光照大概率是光追效果——想原汁原味体验，光追性能（RT 单元）比纯光栅更重要。',
    ],
  },
  {
    icon: Cpu,
    title: 'CPU：最容易被低估的瓶颈',
    color: '#22e5ee',
    points: [
      '数毛社（Digital Foundry）分析指出：GTA 6 的每条街道都有交通模拟和 NPC 行为演算，CPU 负载极高，连 PS5 Pro 都被预测难以稳定 60fps。',
      '这意味着 PC 端想上 60fps，一颗现代 6~8 核 CPU 是硬门槛；X3D 系列的大缓存对开放世界游戏收益明显。',
      '老平台（Zen 2 及更早、9 代酷睿及更早）很可能成为帧率天花板，换显卡也救不回来。',
    ],
  },
  {
    icon: MemoryStick,
    title: '显存与内存：16GB 是底线，32GB 才从容',
    color: '#7c9cff',
    points: [
      '主机 16GB 统一内存中游戏可用约 12~13GB，贴图与几何数据通过高速 SSD 实时流入，PC 端这部分压力转移到显存。',
      '8GB 显存的显卡（如 RTX 4060 8GB、RX 7600）在高贴图质量下大概率爆显存，建议 12GB 显存起步。',
      '系统内存方面 16GB 能进游戏，但后台开浏览器/语音软件就会吃紧，32GB 是 2027 年装机的合理选择。',
    ],
  },
  {
    icon: HardDrive,
    title: '存储：NVMe SSD 不是建议，是必需',
    color: '#f59e0b',
    points: [
      '参考 RDR2 的 150GB，GTA 6 的体量预计 200GB 上下，首发前预留 250GB 空间更稳妥。',
      'GTA 6 的世界流式加载围绕 PS5 的 5.5GB/s SSD 设计，机械硬盘几乎必然出现贴图加载延迟和卡顿。',
      'PCIe 3.0 NVMe 可以兜底，PCIe 4.0 是推荐档的合理配置。',
    ],
  },
]

export default function PcSpecs() {
  return (
    <div className="mx-auto max-w-6xl px-4 pt-14">
      {/* header */}
      <div className="text-center mb-12">
        <Badge variant="outline" className="mb-4 border-[#22e5ee]/40 text-[#22e5ee]">
          <Cpu className="w-3.5 h-3.5 mr-1.5" />
          问题二 · 硬件配置
        </Badge>
        <h1 className="font-display text-4xl sm:text-5xl tracking-tight">
          <span className="text-gradient-ocean">PC 需要什么样的配置？</span>
        </h1>
        <p className="mt-4 text-muted-foreground max-w-2xl mx-auto text-sm sm:text-base leading-relaxed">
          官方配置单不存在，但 PS5 是最好的参照系——GTA 6 的预告片全部基于 PS5 实机录制，
          主机的性能上限就是 PC 配置的推导起点。
        </p>
      </div>

      {/* PS5 anchor */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
          <Zap className="w-5 h-5 text-[#22e5ee]" />
          参照系：PS5 展现了什么水平的性能？
        </h2>
        <p className="text-sm text-muted-foreground mb-8">
          第二支预告片已确认全程基于 PS5 实机画面录制。这台 2020 年的主机，大致相当于这样一台 PC：
        </p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {ps5Specs.map((s) => (
            <Card key={s.label} className="bg-card/90 border-[#22e5ee]/20">
              <CardContent className="p-5">
                <p className="text-[11px] uppercase tracking-widest text-[#22e5ee] mb-2">{s.label}</p>
                <p className="font-semibold text-sm leading-snug">{s.value}</p>
                <p className="text-xs text-muted-foreground mt-2 leading-relaxed">{s.note}</p>
              </CardContent>
            </Card>
          ))}
        </div>
        <div className="mt-5 rounded-2xl border border-white/10 bg-white/[0.03] p-5 flex gap-3 items-start">
          <Info className="w-4 h-4 text-[#22e5ee] shrink-0 mt-0.5" />
          <p className="text-xs text-muted-foreground leading-relaxed">
            关于帧率：多方分析认为 GTA 6 在基础版 PS5 上将以 <strong className="text-foreground">30fps</strong> 为目标；
            有爆料称 PS5 Pro 存在 60fps 模式，但数毛社指出 Pro 的 CPU 仅小幅提频，
            面对 GTA 6 庞大的世界模拟运算，<strong className="text-foreground">稳定 60fps 存疑</strong>。
            换句话说：主机版锁 30fps 的可能性不低，PC 版的高帧率反而更值得期待——前提是你的 CPU 足够强。
          </p>
        </div>
      </section>

      {/* tiers */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-2">三档预测配置单</h2>
        <p className="text-sm text-muted-foreground mb-8">
          由「追平 PS5」到「全面超越主机」，按你的目标体验对号入座：
        </p>
        <div className="grid lg:grid-cols-3 gap-5">
          {tiers.map((t) => (
            <Card
              key={t.name}
              className="bg-card/90 flex flex-col"
              style={{ borderColor: `${t.color}44` }}
            >
              <CardHeader className="pb-4">
                <div className="flex items-center justify-between mb-1">
                  <CardTitle className="text-lg">{t.name}</CardTitle>
                  <span className="w-2.5 h-2.5 rounded-full" style={{ background: t.color }} />
                </div>
                <p className="font-display text-sm" style={{ color: t.color }}>
                  {t.target}
                </p>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col">
                <dl className="space-y-3 text-sm mb-5">
                  {[
                    ['CPU', t.cpu],
                    ['显卡', t.gpu],
                    ['内存', t.ram],
                    ['存储', t.storage],
                  ].map(([k, v]) => (
                    <div key={k} className="flex gap-3">
                      <dt className="w-10 shrink-0 text-xs text-muted-foreground pt-0.5">{k}</dt>
                      <dd className="font-medium leading-snug">{v}</dd>
                    </div>
                  ))}
                </dl>
                <p className="text-xs text-muted-foreground leading-relaxed border-t border-white/10 pt-4 mt-auto">
                  {t.note}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* compact table */}
        <Card className="bg-card/90 border-white/10 mt-6 overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="border-white/10 hover:bg-transparent">
                <TableHead className="text-muted-foreground">档位</TableHead>
                <TableHead className="text-muted-foreground">目标体验</TableHead>
                <TableHead className="text-muted-foreground">CPU</TableHead>
                <TableHead className="text-muted-foreground">显卡</TableHead>
                <TableHead className="text-muted-foreground">内存</TableHead>
                <TableHead className="text-muted-foreground">存储</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tiers.map((t) => (
                <TableRow key={t.name} className="border-white/5">
                  <TableCell className="font-medium whitespace-nowrap" style={{ color: t.color }}>
                    {t.name}
                  </TableCell>
                  <TableCell className="text-muted-foreground text-xs whitespace-nowrap">
                    {t.target}
                  </TableCell>
                  <TableCell className="text-xs">{t.cpu}</TableCell>
                  <TableCell className="text-xs">{t.gpu}</TableCell>
                  <TableCell className="text-xs whitespace-nowrap">{t.ram}</TableCell>
                  <TableCell className="text-xs">{t.storage}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      </section>

      {/* deep analysis */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-2">为什么是这些配置？逐件拆解</h2>
        <p className="text-sm text-muted-foreground mb-8">
          每一档配置背后，都是 PS5 硬件特性在 PC 端的映射：
        </p>
        <div className="grid md:grid-cols-2 gap-5">
          {analysis.map((a) => {
            const Icon = a.icon
            return (
              <Card key={a.title} className="bg-card/90 border-white/10">
                <CardContent className="p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <div
                      className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
                      style={{ background: `${a.color}1f`, color: a.color }}
                    >
                      <Icon className="w-5 h-5" />
                    </div>
                    <h3 className="font-semibold leading-snug">{a.title}</h3>
                  </div>
                  <ul className="space-y-2.5">
                    {a.points.map((p, i) => (
                      <li key={i} className="text-sm text-muted-foreground leading-relaxed flex gap-2.5">
                        <span
                          className="mt-[7px] w-1.5 h-1.5 rounded-full shrink-0"
                          style={{ background: a.color }}
                        />
                        {p}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </section>

      {/* buying advice */}
      <section className="mb-8">
        <Card className="bg-gradient-to-br from-[#ff4da6]/10 via-card to-[#22e5ee]/10 border-white/10">
          <CardContent className="p-6 sm:p-8">
            <h2 className="text-xl font-bold mb-4">给准备攒机的你：三条实用建议</h2>
            <ol className="space-y-4 text-sm leading-relaxed">
              {[
                {
                  t: '现在不要急着为 GTA 6 买硬件',
                  d: 'PC 版最快也要 2027 年底。届时 RTX 60 系显卡、新一代 CPU 已经上市，今天的高端配置到那天只是中端。等 PC 版官宣后再出手，同样的预算能买到强得多的性能。',
                },
                {
                  t: '预算优先级：显卡 > CPU > 显存容量 > SSD',
                  d: '开放世界游戏大多 GPU 受限，但 GTA 6 的模拟密度让 CPU 权重异常高。如果二选一升级，老旧平台优先换 CPU 主板套装，新平台优先堆显卡。',
                },
                {
                  t: '先把 SSD 和内存补齐，成本最低收益最快',
                  d: '一块 1TB PCIe 4.0 NVMe SSD 和 32GB 内存的总价不到一张中端显卡的零头，却直接决定了你能不能「正常进游戏」。这两项现在升级也不亏，所有游戏都受益。',
                },
              ].map((item, i) => (
                <li key={i} className="flex gap-4">
                  <span className="font-display text-2xl neon-cyan shrink-0 w-8">{i + 1}</span>
                  <div>
                    <p className="font-semibold mb-1">{item.t}</p>
                    <p className="text-muted-foreground">{item.d}</p>
                  </div>
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>
      </section>

      <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 flex gap-3 items-start">
        <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <p className="text-xs text-muted-foreground leading-relaxed">
          重要提醒：以上配置单为基于 PS5 硬件水平、Digital Foundry 等技术分析以及 RDR2 等前作 PC 版需求的
          <strong className="text-foreground">推测</strong>，并非官方数据。
          R 星历来会在 PC 版发售前 1~2 个月公布官方配置要求，届时请以官方配置单为准再最终敲定硬件。
        </p>
      </div>
    </div>
  )
}
