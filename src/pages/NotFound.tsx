import { Link, useLocation } from 'react-router'
import Seo from '@/components/Seo'

export default function NotFound() {
  const { pathname } = useLocation()

  return (
    <div className="mx-auto max-w-3xl px-4 py-24 text-center">
      <Seo
        title="Page Not Found | GTA6PC.org"
        description="The page you requested does not exist. Return to the GTA VI PC Guide homepage."
        path={pathname}
        noIndex
      />
      <p className="font-display text-7xl neon-pink">404</p>
      <h1 className="mt-5 text-2xl font-bold">We could not find that page</h1>
      <p className="mt-3 text-sm text-muted-foreground">
        It may have moved, or the address may be incorrect.
      </p>
      <Link
        to="/"
        className="mt-8 inline-flex rounded-full border border-[#22e5ee]/40 px-5 py-2 text-sm text-[#22e5ee] transition-colors hover:bg-[#22e5ee]/10"
      >
        Back to Home
      </Link>
    </div>
  )
}
