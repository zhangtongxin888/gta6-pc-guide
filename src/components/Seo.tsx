import { useEffect } from 'react'

const SITE_URL = 'https://gta6pc.org'
const SITE_NAME = 'GTA VI PC Guide'
const OG_IMAGE_URL = `${SITE_URL}/og-image.png`

type StructuredData = Record<string, unknown> | Array<Record<string, unknown>>

interface SeoProps {
  title: string
  description: string
  path: string
  noIndex?: boolean
  ogType?: 'website' | 'article'
  publishedTime?: string
  modifiedTime?: string
  structuredData?: StructuredData
}

function upsertMeta(attribute: 'name' | 'property', key: string, content: string | undefined) {
  const element = document.head.querySelector<HTMLMetaElement>(`meta[${attribute}="${key}"]`)

  if (!content) {
    element?.remove()
    return
  }

  const meta = element ?? document.createElement('meta')
  meta.setAttribute(attribute, key)
  meta.content = content

  if (!element) {
    document.head.appendChild(meta)
  }
}

function upsertCanonical(url: string) {
  let element = document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]')

  if (!element) {
    element = document.createElement('link')
    element.rel = 'canonical'
    document.head.appendChild(element)
  }

  element.href = url
}

export default function Seo({
  title,
  description,
  path,
  noIndex = false,
  ogType = 'website',
  publishedTime,
  modifiedTime,
  structuredData,
}: SeoProps) {
  useEffect(() => {
    const canonicalUrl = new URL(path, SITE_URL).toString()

    document.title = title
    upsertMeta('name', 'description', description)
    upsertMeta('name', 'robots', noIndex ? 'noindex, nofollow' : 'index, follow')
    upsertMeta('property', 'og:type', ogType)
    upsertMeta('property', 'og:locale', 'en_US')
    upsertMeta('property', 'og:site_name', SITE_NAME)
    upsertMeta('property', 'og:title', title)
    upsertMeta('property', 'og:description', description)
    upsertMeta('property', 'og:url', canonicalUrl)
    upsertMeta('property', 'og:image', OG_IMAGE_URL)
    upsertMeta('property', 'og:image:width', '1200')
    upsertMeta('property', 'og:image:height', '630')
    upsertMeta('property', 'og:image:alt', 'GTA VI PC Guide: release date and system requirements')
    upsertMeta('property', 'article:published_time', ogType === 'article' ? publishedTime : undefined)
    upsertMeta('property', 'article:modified_time', ogType === 'article' ? modifiedTime : undefined)
    upsertMeta('name', 'twitter:card', 'summary_large_image')
    upsertMeta('name', 'twitter:title', title)
    upsertMeta('name', 'twitter:description', description)
    upsertMeta('name', 'twitter:image', OG_IMAGE_URL)
    upsertMeta('name', 'twitter:image:alt', 'GTA VI PC Guide: release date and system requirements')
    upsertCanonical(canonicalUrl)

    const scriptId = 'page-structured-data'
    const existingScript = document.getElementById(scriptId)

    if (!structuredData) {
      existingScript?.remove()
      return
    }

    const script = existingScript ?? document.createElement('script')
    script.id = scriptId
    script.setAttribute('type', 'application/ld+json')
    script.textContent = JSON.stringify(structuredData).replace(/</g, '\\u003c')

    if (!existingScript) {
      document.head.appendChild(script)
    }
  }, [description, modifiedTime, noIndex, ogType, path, publishedTime, structuredData, title])

  return null
}
