import { CalendarClock, Clock, TrendingUp, AlertTriangle, CheckCircle2 } from 'lucide-react'
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

const history = [
  { game: 'GTA 3', console: '2001-10-22', pc: '2002-05-21', months: 7, note: 'PS2 debut' },
  { game: 'GTA: Vice City', console: '2002-10-29', pc: '2003-05-13', months: 6.5, note: 'PS2 debut' },
  { game: 'GTA: San Andreas', console: '2004-10-26', pc: '2005-06-07', months: 7.5, note: 'PS2 debut' },
  { game: 'GTA 4', console: '2008-04-29', pc: '2008-12-02', months: 7, note: 'PS3 / Xbox 360' },
  { game: 'GTA 5', console: '2013-09-17', pc: '2015-04-14', months: 19, note: 'Included a next-gen console port' },
  { game: 'Red Dead Redemption 2', console: '2018-10-26', pc: '2019-11-05', months: 12, note: "Rockstar's latest major PC release" },
]

const gta6Timeline = [
  { date: 'December 2023', event: 'Trailer 1 arrives; Rockstar announces a 2025 launch', status: 'done' as const },
  { date: 'May 2025', event: 'First delay: release moves to May 26, 2026', status: 'done' as const },
  { date: 'April 2026', event: 'Second delay: release moves to November 19, 2026', status: 'done' as const },
  { date: 'June 2026', event: 'Pre-orders open; a temporarily missing date on the official site sparks speculation', status: 'done' as const },
  { date: 'November 19, 2026', event: 'Console launch (PS5 / PS5 Pro / Xbox Series X|S)', status: 'future' as const },
  { date: 'TBA', event: 'PC version: still unannounced', status: 'unknown' as const },
]

const scenarios = [
  {
    name: 'Optimistic',
    window: 'Mid-2027',
    gap: 'About 7–8 months after consoles',
    probability: 'Less likely',
    color: '#22e5ee',
    desc: 'This mirrors the seven-month GTA 4 gap. It assumes Rockstar has been developing the PC port alongside the final console build and avoids further delays.',
  },
  {
    name: 'Baseline',
    window: 'Late 2027 – early 2028',
    gap: 'About 12–15 months after consoles',
    probability: 'Most likely',
    color: '#ff4da6',
    desc: "This follows RDR2's 12-month gap. Holiday timing and Rockstar's preference for Tuesday launches make November 2027 our most reasonable point estimate.",
  },
  {
    name: 'Pessimistic',
    window: 'Mid-2028 or later',
    gap: '18+ months after consoles',
    probability: 'Worth watching',
    color: '#f59e0b',
    desc: "GTA 6 is enormous and PC hardware is fragmented. Multiple PC delays like GTA 5's—or another console delay—would push the wait well beyond our baseline.",
  },
]

const releaseDateStructuredData = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'WebPage',
      '@id': 'https://gta6pc.org/release-date#webpage',
      url: 'https://gta6pc.org/release-date',
      name: 'When Is GTA 6 Coming to PC? Release Date Estimate',
      description: "An evidence-based GTA 6 PC release date estimate using Rockstar's console-to-PC launch history.",
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
          name: 'GTA 6 PC Release Date Estimate',
          item: 'https://gta6pc.org/release-date',
        },
      ],
    },
  ],
}

export default function ReleaseDate() {
  return (
    <div className="mx-auto max-w-6xl px-4 pt-14">
      <Seo
        title="When Is GTA 6 Coming to PC? Release Date Estimate (2027–2028)"
        description="When will GTA 6 launch on PC? We analyze Rockstar's console-to-PC release history to estimate a likely 2027–2028 window."
        path="/release-date"
        structuredData={releaseDateStructuredData}
      />
      {/* header */}
      <div className="text-center mb-12">
        <Badge variant="outline" className="mb-4 border-[#ff4da6]/40 text-[#ff4da6]">
          <CalendarClock className="w-3.5 h-3.5 mr-1.5" />
          QUESTION 1 · RELEASE DATE
        </Badge>
        <h1 className="font-display text-4xl sm:text-5xl tracking-tight">
          <span className="text-gradient-sunset">When is GTA 6 coming to PC?</span>
        </h1>
        <p className="mt-4 text-muted-foreground max-w-2xl mx-auto text-sm sm:text-base leading-relaxed">
          Short answer: <strong className="text-foreground">Rockstar has not said, but its history points to late 2027.</strong>
          Here is how we reached that estimate.
        </p>
      </div>

      {/* conclusion card */}
      <Card className="bg-card/90 border-[#ff4da6]/30 neon-box-pink mb-14">
        <CardContent className="p-6 sm:p-10 text-center">
          <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground mb-3">OUR ESTIMATE</p>
          <p className="font-display text-3xl sm:text-5xl neon-pink">AROUND NOVEMBER 2027</p>
          <p className="mt-4 text-sm text-muted-foreground">
            Confidence window: <strong className="text-foreground">November 2027 – May 2028</strong>
            {' '}(about 12–18 months after the console launch)
          </p>
          <p className="mt-2 text-xs text-muted-foreground/70">
            Assumes the console version launches on November 19, 2026 as currently scheduled
          </p>
        </CardContent>
      </Card>

      {/* GTA 6 timeline */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-2 flex items-center gap-2">
          <Clock className="w-5 h-5 text-[#22e5ee]" />
          The official GTA 6 timeline
        </h2>
        <p className="text-sm text-muted-foreground mb-8">
          To estimate the PC release, start with the console timeline—it has already moved twice.
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
          The pattern: Rockstar's PC versions arrive later
        </h2>
        <p className="text-sm text-muted-foreground mb-8">
          Over the past 25 years, Rockstar has never launched these PC versions alongside consoles. The gap has ranged from roughly six months to a year and a half:
        </p>
        <Card className="bg-card/90 border-white/10 overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="border-white/10 hover:bg-transparent">
                <TableHead className="text-muted-foreground">Game</TableHead>
                <TableHead className="text-muted-foreground">Console</TableHead>
                <TableHead className="text-muted-foreground">PC</TableHead>
                <TableHead className="text-muted-foreground text-right">Gap</TableHead>
                <TableHead className="text-muted-foreground hidden md:table-cell w-[38%]">
                  Visual comparison
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
                    {h.months} months
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
            <CardTitle className="text-lg">Why did GTA 5 take 19 months?</CardTitle>
          </CardHeader>
          <CardContent className="text-sm leading-relaxed text-muted-foreground space-y-3">
            <p>
              GTA 5 debuted on PS3 and Xbox 360 on <strong className="text-foreground">September 17, 2013</strong>.
              Players expected a GTA 4-style six-month wait, but Rockstar prioritized a
              <strong className="text-foreground"> next-generation console port</strong> for PS4 and Xbox One on November 18, 2014.
              The PC edition, originally planned for fall 2014, was delayed three times and finally launched on
              <strong className="text-foreground"> April 14, 2015</strong>.
            </p>
            <p>
              In other words, the 19-month gap included an intermediate console port and three PC-specific delays.
              <strong className="text-[#22e5ee]">
                {' '}GTA 6 begins on current-generation consoles, so there is no equivalent cross-generation port
              </strong>
              . That is the strongest reason to expect a shorter wait than GTA 5, though PC delays remain possible.
            </p>
          </CardContent>
        </Card>
      </section>

      {/* scenarios */}
      <section className="mb-16">
        <h2 className="text-2xl font-bold mb-2">Three release scenarios</h2>
        <p className="text-sm text-muted-foreground mb-8">
          Based on a November 19, 2026 console launch, these are the most plausible PC windows:
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
            <p className="text-xs text-muted-foreground mb-4">Estimated windows (November 2026 console launch → PC)</p>
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
                title="Optimistic: mid-2027"
              />
              {/* base: Nov 2027 - May 2028 */}
              <div
                className="absolute top-[27%] h-3.5 rounded-full bg-gradient-to-r from-[#ff4da6] to-[#ff7b54] neon-box-pink"
                style={{ left: '50%', width: '25%' }}
                title="Baseline: late 2027 to early 2028"
              />
              {/* pessimistic: mid 2028+ */}
              <div
                className="absolute top-[42%] h-2.5 rounded-full bg-gradient-to-r from-amber-400/70 to-amber-400/25"
                style={{ left: '75%', width: '25%' }}
                title="Pessimistic: mid-2028 or later"
              />
            </div>
            <div className="flex flex-wrap gap-x-5 gap-y-1 mt-2 text-[11px] text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#22e5ee]" /> Optimistic
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#ff4da6]" /> Baseline (our pick)
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400" /> Pessimistic
              </span>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* why */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold mb-8">Three reasons behind our estimate</h2>
        <div className="grid sm:grid-cols-3 gap-5">
          {[
            {
              title: 'RDR2 is the closest comparison',
              desc: 'Like GTA 6, RDR2 was a current-generation, open-world RAGE title. Its PC version arrived exactly 12 months after consoles, making it the most relevant precedent.',
            },
            {
              title: 'No cross-generation port in the way',
              desc: "Much of GTA 5's 19-month gap went into PS4 and Xbox One versions. GTA 6 starts on PS5 and Xbox Series hardware, shortening the path to an x86 PC port.",
            },
            {
              title: 'But Rockstar still puts PC second',
              desc: 'Console first, PC later is a consistent Rockstar strategy. A former GTA 4 developer has also publicly predicted a 2027 PC release, making a simultaneous launch unrealistic.',
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
          Important: as of July 2026, Rockstar has announced no PC version. Every date above is an estimate based on historical data.
          Another console delay would move the entire window back. The official site also briefly removed the November 19 date in June 2026,
          so the schedule may still change.
        </p>
      </div>
    </div>
  )
}
