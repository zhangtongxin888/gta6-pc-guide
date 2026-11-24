import { Link } from 'react-router'
import { AlertTriangle, Newspaper } from 'lucide-react'
import Seo from '@/components/Seo'
import { Badge } from '@/components/ui/badge'

const PATH = '/news/xbox-executable'
const CANONICAL = 'https://gta6pc.org/news/xbox-executable'
const CHECKED = '2026-11-24T06:48:25-05:00'
const PUBLISHED = '2026-11-24T07:09:23-05:00'
const MODIFIED = '2026-11-24T07:12:55-05:00'
const TITLE = 'Reported GTA 6 Xbox Executable Is Not an Official PC Release'
const DESCRIPTION =
  'Cyberleek (Da Cong Ge in Chinese coverage) claims a GTA 6 Xbox executable is public. Rockstar has not announced a PC version. Checked November 24, 2026.'

const sources = [
  {
    name: 'Rockstar Games, “Grand Theft Auto VI: Out Now”',
    detail: 'PlayStation 5 and Xbox Series X|S, November 19, 2026. Read again on November 24, 2026.',
    href: 'https://www.rockstargames.com/VI/out-now',
  },
  {
    name: 'Take-Two Interactive, news release, November 19, 2026',
    detail: 'Names PlayStation 5 and Xbox Series X|S.',
    href: 'https://taketwointeractivesoftwareinc.gcs-web.com/news-releases/news-release-details/rockstar-games-announces-grand-theft-auto-vi-now-available/',
  },
  {
    name: 'The Verge, Dominic Preston, August 26, 2026',
    detail: 'Rockstar’s statement on earlier gameplay-video leaks.',
    href: 'https://www.theverge.com/games/984959/gta-vi-leaks-rockstar-games-official-statement-heartbreaking',
  },
  {
    name: 'PC Gamer, Morgan Park, November 19, 2026',
    detail: 'Reports the earlier Xbox-build claim and the “not a PC build” wording.',
    href: 'https://www.pcgamer.com/games/grand-theft-auto/cyberleek-drops-what-they-claim-is-a-near-complete-gta-6-xbox-build-online/',
  },
  {
    name: 'PC Gamer, Andy Chalk, November 23, 2026',
    detail: 'Reports the executable claim. The writer had not verified the file.',
    href: 'https://www.pcgamer.com/games/grand-theft-auto/cyberleek-releases-executable-for-gta-6-xbox-build-leaked-last-week-the-torch-passes-to-the-open-source-recomp-and-emulation-projects/',
  },
  {
    name: 'VideoCardz, WhyCry, November 23, 2026, 15:37 UTC',
    detail: 'Says the file had not been independently authenticated and that Rockstar had not commented.',
    href: 'https://videocardz.com/newz/gta-vi-xbox-executable-released-pc-recompilation-projects-can-now-begin-testing/',
  },
  {
    name: 'XDA, Patrick O’Rourke, November 23, 2026, 11:38 a.m. ET',
    detail: 'Reports the claim and, at the time of writing, a claimant site that appeared to be down.',
    href: 'https://www.xda-developers.com/gta-6-xbox-executable-leaked-opening-door-for-pc-recompilation-projects-begin-testing/',
  },
  {
    name: 'CBR, Kyle Gratton, November 23, 2026, 1:38 p.m. ET',
    detail: 'Describes an Xbox build labeled 1.0.2.1 and says CBR would not link the file.',
    href: 'https://www.cbr.com/gta-6-xbox-exe-leak-pc-port-cyberleek/',
  },
  {
    name: 'IGN, Wesley Yin-Poole, updated November 24, 2026, 12:59 a.m.',
    detail: 'IGN did not print a timezone on that byline. The article says “reportedly.”',
    href: 'https://sea.ign.com/grand-theft-auto-vi-rumored-title/252343/gta-6-leaker-cyberleek-reportedly-releases-exe-file-for-xbox-build-sparking-concern-an-unofficial-pc',
  },
  {
    name: 'IGN on X, @IGN, November 24, 2026, 6:30 a.m. ET',
    detail: 'Verified account post. Its wording is flatter than the article’s “reportedly.”',
    href: 'https://x.com/IGN/status/2125190201374851274',
  },
  {
    name: '3DM, compiled from VideoCardz, page time 2026-11-24 05:30:12',
    detail: 'Uses the nickname 大葱哥 (Cyberleek). The page does not print a timezone.',
    href: 'https://www.3dmgame.com/news/202611/3961075.html',
  },
] as const

const structuredData = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'NewsArticle',
      '@id': `${CANONICAL}#article`,
      headline: TITLE,
      description: DESCRIPTION,
      datePublished: PUBLISHED,
      dateModified: MODIFIED,
      inLanguage: 'en',
      mainEntityOfPage: CANONICAL,
      url: CANONICAL,
      isAccessibleForFree: true,
      author: {
        '@type': 'Organization',
        name: 'GTA VI PC Guide',
        url: 'https://gta6pc.org/',
      },
      publisher: {
        '@type': 'Organization',
        name: 'GTA VI PC Guide',
        url: 'https://gta6pc.org/',
      },
      about: {
        '@type': 'VideoGame',
        name: 'Grand Theft Auto VI',
        alternateName: 'GTA 6',
      },
      citation: sources.map((source) => source.href),
    },
    {
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Home', item: 'https://gta6pc.org/' },
        { '@type': 'ListItem', position: 2, name: TITLE, item: CANONICAL },
      ],
    },
  ],
}

export default function XboxExecutableClaim() {
  return (
    <article className="mx-auto max-w-3xl px-4 pt-14 pb-4">
      <Seo
        title={`${TITLE} | GTA6PC.org`}
        description={DESCRIPTION}
        path={PATH}
        ogType="article"
        publishedTime={PUBLISHED}
        modifiedTime={MODIFIED}
        structuredData={structuredData}
      />

      <Badge variant="outline" className="mb-4 border-[#ff4da6]/40 text-[#ff4da6]">
        <Newspaper className="w-3.5 h-3.5 mr-1.5" />
        NEWS CHECK
      </Badge>
      <h1 className="font-display text-3xl sm:text-4xl tracking-tight leading-tight">
        <span className="text-gradient-sunset">
          The reported GTA 6 Xbox executable is not an official PC release
        </span>
      </h1>
      <p className="mt-4 text-sm text-muted-foreground">
        Checked{' '}
        <time dateTime={CHECKED}>November 24, 2026, 6:48 a.m. Eastern Time</time>.
        This page records what Rockstar, the claimant, and named news outlets had published by then.
      </p>

      <div className="mt-8 rounded-2xl border border-amber-400/30 bg-amber-400/10 p-5 sm:p-6 flex gap-4 items-start">
        <AlertTriangle className="w-5 h-5 text-amber-300 shrink-0 mt-0.5" aria-hidden />
        <div className="text-sm leading-relaxed text-amber-50/90">
          <p className="font-semibold text-amber-200 mb-1">No download on this site</p>
          <p>
            GTA6PC.org does not host, mirror, or link to the reported executable, archives,
            torrents, magnet links, file-host copies, passwords, or paid offers. We did not
            download or run any of those files. An advertised link is not a file we have
            authenticated.
          </p>
        </div>
      </div>

      <div className="mt-8 space-y-4 text-sm sm:text-base leading-relaxed text-foreground/90">
        <p>
          On November 23, 2026, Cyberleek said the missing main executable from a leaked
          Xbox build of Grand Theft Auto VI was out. Chinese coverage at 3DM refers to
          that name as 大葱哥. The claimant’s own November 19 post calls the material an
          Xbox build. Rockstar’s current “Out Now” page, read again for this check, lists
          PlayStation 5 and Xbox Series X|S.
        </p>
        <p>
          Several newsrooms report that a file is circulating. None of the reports below
          is a Rockstar authentication, and this page is not one either. There is also no
          verified, normally playable unofficial PC version in the sources checked here.
        </p>
      </div>

      <section className="mt-12">
        <h2 className="text-2xl font-bold mb-4">What Rockstar and Take-Two have published</h2>
        <div className="space-y-4 text-sm sm:text-base leading-relaxed text-foreground/90">
          <p>
            Rockstar’s{' '}
            <a
              href="https://www.rockstargames.com/VI/out-now"
              className="text-[#22e5ee] underline underline-offset-2"
              target="_blank"
              rel="noopener noreferrer"
            >
              Grand Theft Auto VI: Out Now
              <span className="sr-only"> (opens in a new tab)</span>
            </a>{' '}
            page says the game is available worldwide for PlayStation 5 and Xbox Series
            X|S and dates that release November 19, 2026. Take-Two’s{' '}
            <a
              href="https://taketwointeractivesoftwareinc.gcs-web.com/news-releases/news-release-details/rockstar-games-announces-grand-theft-auto-vi-now-available/"
              className="text-[#22e5ee] underline underline-offset-2"
              target="_blank"
              rel="noopener noreferrer"
            >
              November 19, 2026 news release
              <span className="sr-only"> (opens in a new tab)</span>
            </a>{' '}
            uses those same two platforms. Neither page states a PC release date, price,
            PC store listing, or PC system requirements.
          </p>
          <p>
            Rockstar did speak earlier about leaked footage. The Verge, on August 26, 2026,
            published the studio’s statement on a week of gameplay-video leaks. Rockstar
            called that period “heartbreaking for our team” and asked players to wait for
            the November 19 launch. That statement is about pre-release footage. It does
            not mention a November executable, and it does not confirm any file released
            after launch.
          </p>
        </div>
      </section>

      <section className="mt-12">
        <h2 className="text-2xl font-bold mb-4">What Cyberleek’s page said</h2>
        <div className="space-y-4 text-sm sm:text-base leading-relaxed text-foreground/90">
          <p>
            The sentences in this section are the claimant’s, read from Cyberleek’s public
            announcement page. That page prints dates and clock times without a timezone.
            The times below are quoted as printed. We are not treating them as confirmed
            Eastern or UTC time.
          </p>
          <ul className="list-disc pl-5 space-y-3">
            <li>
              A post the page dates November 19, 2026, 6:42 p.m., titled “THE BUILD GOES
              OUT,” says the group was sending out a November 2026 build by torrent while
              holding back the main executable, and: “it is an Xbox build this time, not a
              PC build.” PC Gamer quoted that sentence the same day. Morgan Park wrote that
              the outlet had not yet seen confirmation the build was genuine. Park also
              reported Reddit comments, on a thread that had been removed, describing the
              archive as around 200 GB. VideoCardz and 3DM later describe a reported 209 GB
              Xbox build. We did not measure any file, so this page does not pick one size
              as a fact.
            </li>
            <li>
              A post the page dates November 21, 2026, 7:43 a.m., says the executable would
              be provided in a ZIP with SHA-256 hashes, that “you do NOT need to run the
              exe, and it won’t run anyway,” and that it is “meant for those who will
              develop an Xbox emulator.” The same post says “CL is not selling anything.”
            </li>
            <li>
              A post titled “XMAS CAME EARLY,” dated on the page as November 23, 2026,
              2:36 p.m., says: “The exe is out. Always free.” It also says: “The torch
              passes to the open source recomp and emulation projects.” The post includes
              checksum strings. This page does not repeat them. A file that matched those
              strings would match whatever the claimant hashed. That match would not be a
              statement from Rockstar.
            </li>
          </ul>
          <p>
            The same page labels an item “GTA 6: XBOX EXE 1.0.2.1.” CBR also describes an
            Xbox Series X|S executable for a build labeled 1.0.2.1. That label comes from
            the claimant and from coverage of the claim. It is not a Rockstar PC version
            number published on the official pages above.
          </p>
          <p>
            At 6:48 a.m. ET on November 24, 2026, a browser-style request to the
            announcement page returned HTTP 200, and the November 23 post was still in the
            HTML. The HTML included magnet links and third-party file-host links. We did
            not open them. During the same morning, a request with a non-browser user
            agent received HTTP 403. XDA, at 11:38 a.m. ET on November 23, wrote that the
            site appeared to be down. The page can be up in one check and unavailable in
            another. A page that advertises a download is not evidence that a given link
            still serves a complete file, or that the bytes are genuine, safe, or usable.
          </p>
          <p>
            A separate notice titled “DEVELOPMENT BUILD IS OUT” was also on the page and
            advertised a paid download at $40. Its printed clock was not stable across
            loads a few minutes apart: we saw both “Nov 24, 2026, 10:52 AM” and
            “Nov 24, 2026, 11:36 AM,” still with no timezone. That notice is a different
            offer from the November 23 post that said the Xbox executable was free, and
            the page still contains the November 21 line “CL is not selling anything.”
            We did not pay for the offer, test it, or link it.
          </p>
        </div>
      </section>

      <section className="mt-12">
        <h2 className="text-2xl font-bold mb-4">What the news reports establish</h2>
        <div className="space-y-4 text-sm sm:text-base leading-relaxed text-foreground/90">
          <p>
            PC Gamer’s Andy Chalk, published November 23, 2026, wrote that Cyberleek
            appears to have released the executable from the Xbox build leaked the week
            before, and quoted the line passing the work to open-source recompilation and
            emulation projects. Chalk wrote that he had not verified whether the executable
            is legitimate. He added that earlier material appears to be, and that the
            general consensus pointed the same way, while still leaving the new file
            unverified by him. The article says software piracy is illegal and that files
            from strangers on the internet can contain malware. It also says GTA 6 still
            has not been announced for PC. Chalk reported that the group had tied the
            executable’s timing to a cryptocurrency market-cap target of $15 million or to
            November 23, whichever came first, and that the token target was missed.
          </p>
          <p>
            VideoCardz published at 15:37 UTC on November 23, 2026. It says the group
            claims the file is publicly available. It also says the executable “has not yet
            been independently authenticated, and Rockstar Games has not commented on the
            release.” 3DM’s compilation, timestamped 05:30:12 on a page dated November 24,
            2026, with no timezone printed, uses the headline nickname 大葱哥 (Cyberleek)
            and carries the same two limits: no independent authentication, and no Rockstar
            comment in the coverage it compiled. 3DM writes that a verified file would
            still leave Xbox-specific system pieces to translate before anyone could try
            to start the game on Windows, and that this would not mean the game already
            runs on PC.
          </p>
          <p>
            CBR’s Kyle Gratton, November 23, 2026 at 1:38 p.m. ET, wrote that the
            executable being discussed is the Xbox version and not an available PC
            version. CBR said it would not link to Cyberleek’s website or the executable,
            and it told readers to be extremely cautious of malware.
          </p>
          <p>
            XDA’s Patrick O’Rourke, November 23, 2026 at 11:38 a.m. ET, reported the
            missing Xbox executable as publicly available and wrote that Rockstar had not
            announced a PC version. XDA also wrote that a fan-made PC build could appear
            within days if unofficial projects succeed. That is XDA’s prediction. It is
            not a completed port. PC Gamer separately reported a Leonida project Discord
            message, attributed to Shayder, saying it would take at least a week before
            the project reached a point where GTA was playable on PC. That is one
            participant’s expectation. It is not a Rockstar schedule, and it is not a
            report that a playable PC edition already exists.
          </p>
          <p>
            IGN’s Wesley Yin-Poole article, on the IGN Southeast Asia edition, says
            Cyberleek has “reportedly” released the executable and that this has sparked
            concern an unofficial PC port could follow. The page’s update line reads
            “Updated: Nov. 24, 2026, 12:59 a.m.” and does not name a timezone. The article
            says some people are predicting that recompilation could move quickly. Those
            are predictions reported by IGN, not a result we observed.
          </p>
          <p>
            IGN’s verified @IGN account posted at 6:30 a.m. ET on November 24, 2026
            (11:30 UTC): “Cyberleek has released the executable file for the leaked Xbox
            build of GTA 6, sparking concern that an unofficial PC port could be around
            the corner.” The post states the release more flatly than the article’s
            “reportedly.” We read the post through public post metadata. We did not treat
            it as a forensic check of a binary.
          </p>
        </div>
      </section>

      <section className="mt-12">
        <h2 className="text-2xl font-bold mb-4">What remains unproven</h2>
        <div className="space-y-4 text-sm sm:text-base leading-relaxed text-foreground/90">
          <p>
            As of this check, the public record supports a narrower statement. Cyberleek
            claims to have published the main executable of an Xbox build it labels
            1.0.2.1, and reputable outlets have reported that claim. The claimant’s page
            was advertising links, including magnet links, when we read it. We do not know
            from our own check whether those links still serve a complete file, whether
            the bytes match the claimant’s checksums, or whether the file is the Xbox
            executable it is said to be.
          </p>
          <p>
            We also have no Rockstar or Take-Two statement, in the pages read for this
            article, that authenticates the November 23 file, announces a PC edition, or
            gives a PC date. Our{' '}
            <Link to="/release-date" className="text-[#22e5ee] underline underline-offset-2">
              release-date page
            </Link>{' '}
            is this site’s older estimate from Rockstar’s past console-to-PC gaps. It is
            not a date Rockstar has announced, and this executable claim does not turn
            that estimate into one.
          </p>
          <p>
            Unofficial copies of a commercial game can infringe copyright. PC Gamer and
            CBR both warn that files offered as GTA 6 on PC can carry malware. The
            claimant’s November 21 post itself says the executable is not something a
            reader needs to run, and that it will not run as-is. For the edition Rockstar
            has actually released, use the official Out Now page linked above.
          </p>
        </div>
      </section>

      <section className="mt-12">
        <h2 className="text-2xl font-bold mb-2">Sources</h2>
        <p className="text-sm text-muted-foreground mb-4">
          Each link leaves this site and opens in a new tab. These are news and official
          pages. They are not downloads.
        </p>
        <ol className="space-y-4">
          {sources.map((source) => (
            <li key={source.href} className="text-sm leading-relaxed">
              <a
                href={source.href}
                className="text-[#22e5ee] underline underline-offset-2"
                target="_blank"
                rel="noopener noreferrer"
              >
                {source.name}
                <span className="sr-only"> (opens in a new tab)</span>
              </a>
              <span className="block text-muted-foreground">{source.detail}</span>
            </li>
          ))}
        </ol>
      </section>
    </article>
  )
}
