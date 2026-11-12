import { Link } from 'react-router'
import { ArrowRight, CalendarClock, Cpu, AlertTriangle } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import Seo from '@/components/Seo'

const homeStructuredData = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'WebSite',
      '@id': 'https://gta6pc.org/#website',
      name: 'GTA VI PC Guide',
      url: 'https://gta6pc.org/',
      inLanguage: 'en',
      description: 'An evidence-based guide to the GTA 6 PC release date and system requirements.',
    },
    {
      '@type': 'WebPage',
      '@id': 'https://gta6pc.org/#webpage',
      url: 'https://gta6pc.org/',
      name: 'GTA 6 PC Release Date and System Requirements',
      isPartOf: { '@id': 'https://gta6pc.org/#website' },
      about: { '@type': 'VideoGame', name: 'Grand Theft Auto VI', alternateName: 'GTA 6' },
      inLanguage: 'en',
      dateModified: '2026-07-22',
    },
  ],
}

const entries = [
  {
    to: '/release-date',
    icon: CalendarClock,
    color: 'pink' as const,
    title: 'When is GTA 6 coming to PC?',
    desc: "We revisit GTA 5's 19-month console-to-PC wait and Rockstar's release history to estimate the most likely launch window for GTA 6 on PC.",
    tag: 'Our estimate: late 2027',
  },
  {
    to: '/pc-specs',
    icon: Cpu,
    color: 'cyan' as const,
    title: 'What PC specs will GTA 6 need?',
    desc: 'Using PS5 and PS5 Pro performance as a baseline, we estimate CPU, GPU, VRAM, memory, and SSD requirements across three build tiers.',
    tag: 'Starting point: 16GB RAM + NVMe SSD',
  },
]

export default function Home() {
  return (
    <div>
      <Seo
        title="GTA 6 PC Release Date & System Requirements | GTA6PC.org"
        description="When is GTA 6 coming to PC, and what hardware will it need? Explore evidence-based release date and system requirement estimates."
        path="/"
        structuredData={homeStructuredData}
      />
      {/* Neon Bay mini game */}
      <section id="home-minigame" aria-label="Neon Bay mini game" className="container mx-auto px-4 pt-4 pb-2">
        <div className="relative w-full overflow-hidden rounded-2xl border border-white/10 bg-black shadow-lg h-[min(64vh,560px)] min-h-[380px] sm:h-[min(72vh,620px)] sm:min-h-[420px]">
          <iframe
            src="/play/"
            title="Neon Bay, a free fan-made mini game"
            className="absolute inset-0 h-full w-full border-0 block"
            loading="eager"
            allow="fullscreen; autoplay"
            allowFullScreen
          />
        </div>
        <p className="mt-2 text-sm text-muted-foreground">
          <strong>Neon Bay</strong> is a free fan-made mini game inspired by GTA 6, not an official Rockstar product.{' '}
          <a href="/play/" target="_blank" rel="noopener" className="underline">Open it full screen</a>.
        </p>
      </section>
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
            Console release: November 19, 2026 · PC version unannounced
          </Badge>
          <h1 className="font-display leading-none">
            <span className="block text-6xl sm:text-8xl tracking-tight text-white drop-shadow-[0_4px_24px_rgba(0,0,0,0.6)]">
              GTA VI
            </span>
            <span className="block mt-3 text-3xl sm:text-5xl tracking-wide text-white/95 drop-shadow-[0_2px_12px_rgba(0,0,0,0.6)]">
              THE PC PLAYER'S GUIDE
            </span>
          </h1>
          <p className="mt-6 text-sm sm:text-base text-white/85 max-w-xl mx-auto drop-shadow-[0_1px_8px_rgba(0,0,0,0.5)]">
            When will the PC version arrive? Should you upgrade now?
            <br className="hidden sm:block" />
            We use release history and hardware analysis to answer the two questions PC players care about most.
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
            <p className="font-semibold text-amber-300 mb-1">Current status (July 2026)</p>
            Rockstar has <strong className="text-amber-200">not announced a PC version</strong>. That matches its usual pattern:
            recent GTA PC editions were announced after their console launches. The console release has already moved twice
            (fall 2025 → May 26, 2026 → November 19, 2026), so every estimate here assumes the current console date holds.
          </div>
        </div>
      </section>
    </div>
  )
}
