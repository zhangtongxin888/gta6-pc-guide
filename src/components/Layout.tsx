import { useLayoutEffect } from 'react'
import { Link, NavLink, Outlet, useLocation } from 'react-router'
import { Gamepad2, CalendarClock, Cpu, Newspaper } from 'lucide-react'

function ScrollToTop() {
  const { pathname } = useLocation()

  useLayoutEffect(() => {
    if ('scrollRestoration' in window.history) {
      window.history.scrollRestoration = 'manual'
    }
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' })
  }, [pathname])

  return null
}

const navItems = [
  { to: '/', label: 'Home', mobileLabel: 'Home', icon: Gamepad2, end: true },
  { to: '/release-date', label: 'Release Date', mobileLabel: 'Date', icon: CalendarClock },
  { to: '/pc-specs', label: 'PC Specs', mobileLabel: 'Specs', icon: Cpu },
  { to: '/news/xbox-executable', label: 'News', mobileLabel: 'News', icon: Newspaper },
]

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col bg-background relative overflow-x-hidden">
      {/* ambient background */}
      <div className="pointer-events-none fixed inset-0 city-grid-bg" aria-hidden />
      <div
        className="pointer-events-none fixed -top-40 -left-40 w-[36rem] h-[36rem] rounded-full opacity-25 blur-3xl"
        style={{ background: 'radial-gradient(circle, #ff4da6 0%, transparent 65%)' }}
        aria-hidden
      />
      <div
        className="pointer-events-none fixed -bottom-40 -right-40 w-[36rem] h-[36rem] rounded-full opacity-20 blur-3xl"
        style={{ background: 'radial-gradient(circle, #22e5ee 0%, transparent 65%)' }}
        aria-hidden
      />

      <header className="sticky top-0 z-50 border-b border-white/10 bg-[#0d0718]/80 backdrop-blur-md">
        <div className="mx-auto max-w-6xl px-3 sm:px-4 py-2.5 sm:h-16 sm:py-0 flex flex-col items-stretch gap-2 sm:flex-row sm:items-center sm:justify-between">
          <Link to="/" className="flex items-center gap-2.5 shrink-0 self-start sm:self-auto group">
            <span className="font-display text-xl tracking-tight leading-none">
              <span className="neon-pink">GTA&nbsp;VI</span>{' '}
              <span className="neon-cyan">PC</span>
            </span>
            <span className="hidden sm:inline text-xs text-muted-foreground group-hover:text-foreground transition-colors">
              GUIDE
            </span>
          </Link>
          <nav className="flex flex-wrap items-center gap-1 sm:flex-nowrap sm:justify-end sm:gap-2">
            {navItems.map(({ to, label, mobileLabel, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  `flex items-center gap-1.5 rounded-full px-2.5 py-1.5 text-xs sm:px-3 sm:text-sm transition-all ${
                    isActive
                      ? 'bg-primary/15 text-[#ff4da6] neon-box-pink font-medium'
                      : 'text-muted-foreground hover:text-foreground hover:bg-white/5'
                  }`
                }
              >
                <Icon className="w-3.5 h-3.5" />
                <span className="hidden md:inline">{label}</span>
                <span className="md:hidden">{mobileLabel}</span>
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <ScrollToTop />
      <main className="relative z-10 flex-1">
        <Outlet />
      </main>

      <footer className="relative z-10 border-t border-white/10 mt-20">
        <div className="mx-auto max-w-6xl px-4 py-10 text-center space-y-3">
          <p className="font-display text-sm">
            <span className="neon-pink">GTA VI</span> <span className="neon-cyan">PC</span>{' '}
            <span className="text-muted-foreground">GUIDE</span>
          </p>
          <p className="text-xs text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            This fan-made guide is not affiliated with Rockstar Games or Take-Two Interactive.
            All estimates are based on public information and historical patterns; official announcements take precedence.
          </p>
          <p className="text-[11px] text-muted-foreground/60">Last reviewed: July 2026</p>
        </div>
      </footer>
    </div>
  )
}
