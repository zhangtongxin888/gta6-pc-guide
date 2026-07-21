import { Cpu, MemoryStick, HardDrive, MonitorPlay, Zap, AlertTriangle, Info } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import Seo from '@/components/Seo'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

const ps5Specs = [
  { label: 'CPU', value: '8-core AMD Zen 2 @ 3.5GHz', note: 'Roughly a downclocked desktop Ryzen 7 3700X' },
  { label: 'GPU', value: 'RDNA 2 · 36CU · 10.28 TFLOPS', note: 'Raster performance near an RTX 2070 Super / RX 6700' },
  { label: 'Memory', value: '16GB unified GDDR6', note: 'About 12–13GB available to games, shared by CPU and GPU' },
  { label: 'Storage', value: 'Custom NVMe SSD · 5.5GB/s', note: 'Designed for seamless open-world streaming' },
]

const tiers = [
  {
    name: 'Minimum',
    target: '1080p / 30fps · Low settings',
    color: '#22e5ee',
    cpu: 'Ryzen 5 3600 / i5-10400',
    gpu: 'RTX 3060 12GB / RX 6600 XT',
    ram: '16GB DDR4',
    storage: 'NVMe SSD · 200GB free',
    note: 'Aims to match or slightly exceed the PS5 experience. Low settings plus DLSS or FSR should make 1080p playable, but do not expect performance beyond the console version.',
  },
  {
    name: 'Recommended',
    target: '1440p / 60fps · High settings',
    color: '#ff4da6',
    cpu: 'Ryzen 7 7700X / i5-13600K',
    gpu: 'RTX 4070 Super / RX 7800 XT',
    ram: '32GB DDR5',
    storage: 'PCIe 4.0 NVMe SSD · 200GB',
    note: 'The sweet spot for most players: clearly above console resolution and frame rate, with upscaling helping high settings hold 60fps.',
  },
  {
    name: 'Enthusiast',
    target: '4K / 60fps · Max ray tracing',
    color: '#f59e0b',
    cpu: 'Ryzen 7 9800X3D / i7-14700K',
    gpu: 'RTX 5080 / RX 9070 XT or better',
    ram: '32GB low-latency DDR5',
    storage: 'PCIe 4.0/5.0 NVMe SSD',
    note: 'The trailers show dense global illumination and reflections, suggesting a heavy ray-tracing load. Maxed-out 4K will need a flagship GPU, while an X3D CPU should reduce simulation bottlenecks.',
  },
]

const analysis = [
  {
    icon: MonitorPlay,
    title: "GPU: the PS5's 10 TFLOPS is only a starting point",
    color: '#ff4da6',
    points: [
      'PS5 raster performance is close to an RTX 2070 Super, making the RTX 3060 class a reasonable floor for matching console visuals.',
      'Consoles benefit from deep platform-specific optimization, so PCs often need 20%–30% more headroom. That moves our recommended tier to the RTX 4070 Super class.',
      'The water reflections and neon global illumination shown in trailers are likely ray-traced, making RT performance more important than raster power alone.',
    ],
  },
  {
    icon: Cpu,
    title: 'CPU: the easiest bottleneck to underestimate',
    color: '#22e5ee',
    points: [
      'Digital Foundry has highlighted the dense traffic and NPC simulation visible on every street. That workload could keep even PS5 Pro from sustaining 60fps.',
      'A modern 6- to 8-core CPU is therefore the practical floor for 60fps on PC. Large-cache X3D processors are especially strong in open-world games.',
      'Older platforms—Zen 2 and earlier, or 9th-gen Core and earlier—may impose a frame-rate ceiling that a GPU upgrade cannot fix.',
    ],
  },
  {
    icon: MemoryStick,
    title: 'VRAM and RAM: 16GB is the floor, 32GB is comfortable',
    color: '#7c9cff',
    points: [
      "Games can use about 12–13GB of the console's unified memory, with textures and geometry streamed from the SSD. On PC, much of that pressure shifts to VRAM.",
      'Cards with 8GB VRAM, such as the RTX 4060 8GB and RX 7600, may struggle with high-resolution textures. We recommend at least 12GB VRAM.',
      '16GB system RAM may run the game, but browsers and voice chat will leave little headroom. For a 2027 build, 32GB is the sensible target.',
    ],
  },
  {
    icon: HardDrive,
    title: 'Storage: an NVMe SSD is a requirement, not a suggestion',
    color: '#f59e0b',
    points: [
      "RDR2 uses about 150GB. GTA 6 could land around 200GB, so reserving 250GB before launch is the safer plan.",
      "The world is designed around the PS5's 5.5GB/s SSD. A mechanical hard drive would almost certainly cause texture pop-in and traversal stutter.",
      'PCIe 3.0 NVMe should be the minimum; PCIe 4.0 is the sensible recommendation.',
    ],
  },
]

const pcSpecsStructuredData = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'WebPage',
      '@id': 'https://gta6pc.org/pc-specs#webpage',
      url: 'https://gta6pc.org/pc-specs',
      name: 'GTA 6 PC System Requirements: Minimum, Recommended and 4K',
      description: 'Estimated GTA 6 PC CPU, GPU, memory, VRAM and NVMe SSD requirements using PS5 performance as a baseline.',
      about: { '@type': 'VideoGame', name: 'Grand Theft Auto VI', alternateName: 'GTA 6' },
      inLanguage: 'en',
      dateModified: '2026-07-22',
    },
    {
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Home', item: 'https://gta6pc.org/' },
        {
          '@type': 'ListItem',
          position: 2,
          name: 'GTA 6 PC System Requirements',
          item: 'https://gta6pc.org/pc-specs',
        },
      ],
    },
  ],
}

export default function PcSpecs() {
  return (
    <div className="mx-auto max-w-6xl px-4 pt-14">
      <Seo
        title="GTA 6 PC System Requirements: Minimum, Recommended & 4K"
        description="What PC specs will GTA 6 need? Using PS5 performance as a baseline, we estimate minimum, recommended and 4K CPU, GPU, memory and SSD requirements."
        path="/pc-specs"
        structuredData={pcSpecsStructuredData}
      />
      {/* header */}
      <div className="text-center mb-12">
        <Badge variant="outline" className="mb-4 border-[#22e5ee]/40 text-[#22e5ee]">
          <Cpu className="w-3.5 h-3.5 mr-1.5" />
          QUESTION 2 · SYSTEM REQUIREMENTS
        </Badge>
        <h1 className="font-display text-4xl sm:text-5xl tracking-tight">
          <span className="text-gradient-ocean">What PC specs will GTA 6 need?</span>
        </h1>
        <p className="mt-4 text-muted-foreground max-w-2xl mx-auto text-sm sm:text-base leading-relaxed">
          Official requirements do not exist yet, but PS5 is our best baseline. GTA 6 trailers have been captured on PS5,
          so the console's performance gives us a practical starting point for PC estimates.
        </p>
      </div>

      {/* PS5 anchor */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
          <Zap className="w-5 h-5 text-[#22e5ee]" />
          Baseline: what level of performance does PS5 deliver?
        </h2>
        <p className="text-sm text-muted-foreground mb-8">
          Rockstar says Trailer 2 was captured entirely on PS5. This 2020 console is broadly comparable to the following PC hardware:
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
            Frame-rate outlook: multiple analyses expect the base PS5 to target <strong className="text-foreground">30fps</strong>.
            Rumors suggest a PS5 Pro 60fps mode, but Digital Foundry notes that the Pro only modestly improves CPU clocks.
            Given GTA 6's simulation load, a <strong className="text-foreground">stable 60fps remains uncertain</strong>.
            A 30fps console target would make high-frame-rate PC play especially appealing—if your CPU is fast enough.
          </p>
        </div>
      </section>

      {/* tiers */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-2">Three estimated PC tiers</h2>
        <p className="text-sm text-muted-foreground mb-8">
          From matching PS5 to clearly surpassing consoles, choose the tier that fits your target experience:
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
                    ['GPU', t.gpu],
                    ['RAM', t.ram],
                    ['SSD', t.storage],
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
                <TableHead className="text-muted-foreground">Tier</TableHead>
                <TableHead className="text-muted-foreground">Target</TableHead>
                <TableHead className="text-muted-foreground">CPU</TableHead>
                <TableHead className="text-muted-foreground">GPU</TableHead>
                <TableHead className="text-muted-foreground">RAM</TableHead>
                <TableHead className="text-muted-foreground">Storage</TableHead>
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
        <h2 className="text-2xl font-bold mb-2">Why these specs? A component-by-component analysis</h2>
        <p className="text-sm text-muted-foreground mb-8">
          Each tier maps the PS5's hardware characteristics to realistic PC parts:
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
            <h2 className="text-xl font-bold mb-4">Three practical upgrade tips</h2>
            <ol className="space-y-4 text-sm leading-relaxed">
              {[
                {
                  t: 'Do not rush to buy GTA 6 hardware today',
                  d: "Our earliest realistic PC window is late 2027. New GPU and CPU generations should arrive before then, turning today's high-end parts into tomorrow's midrange. Waiting for an official PC announcement should buy far more performance for the same budget.",
                },
                {
                  t: 'Budget priority: GPU > CPU > VRAM capacity > SSD',
                  d: "Open-world games are usually GPU-bound, but GTA 6's simulation density makes the CPU unusually important. On an old platform, upgrade the CPU and motherboard first; on a modern platform, put more of the budget into the GPU.",
                },
                {
                  t: 'Upgrade the SSD and RAM first for low-cost gains',
                  d: 'A 1TB PCIe 4.0 NVMe SSD and 32GB of RAM cost much less than a midrange GPU, yet they may determine whether the game runs smoothly at all. Both upgrades also benefit the rest of your library today.',
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
          Important: these requirements are <strong className="text-foreground">estimates</strong> based on PS5 hardware,
          technical analysis from outlets including Digital Foundry, and earlier Rockstar PC releases such as RDR2. They are not official.
          Rockstar typically publishes PC requirements one or two months before release; wait for that list before making a final hardware decision.
        </p>
      </div>
    </div>
  )
}
