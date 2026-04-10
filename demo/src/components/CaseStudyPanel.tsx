import { useEffect, useState } from 'react'
import './CaseStudyPanel.css'

const NARRATIVE_URL =
  'https://raw.githubusercontent.com/gr8drmrSLC/build-with-ai/master/framework/PROJECT_NARRATIVE.md'

type Status = 'loading' | 'ready' | 'error'

interface Entry {
  title: string
  date: string
  phase: string
  lines: string[]   // all content lines after the metadata
}

export default function CaseStudyPanel() {
  const [entries, setEntries] = useState<Entry[]>([])
  const [status, setStatus] = useState<Status>('loading')
  const [expanded, setExpanded] = useState<Set<number>>(new Set())

  useEffect(() => {
    let cancelled = false
    fetch(NARRATIVE_URL)
      .then(r => { if (!r.ok) throw new Error(); return r.text() })
      .then(text => {
        if (!cancelled) {
          setEntries(parseEntries(text))
          setStatus('ready')
        }
      })
      .catch(() => { if (!cancelled) setStatus('error') })
    return () => { cancelled = true }
  }, [])

  function toggle(i: number) {
    setExpanded(prev => {
      const next = new Set(prev)
      next.has(i) ? next.delete(i) : next.add(i)
      return next
    })
  }

  return (
    <section className="panel case-study-panel" aria-label="Case Studies">
      <p className="panel-label">Case Studies</p>

      {status === 'loading' && <p className="cs-loading">Loading...</p>}
      {status === 'error'   && <p className="cs-error">Could not load narrative.</p>}

      {status === 'ready' && (
        <div className="cs-entries">
          {entries.map((entry, i) => {
            const isExpanded = expanded.has(i)
            const preview = entry.lines.filter(l => l.trim() && !l.startsWith('#')).slice(0, 3)

            return (
              <article key={i} className="cs-entry">
                <div className="cs-meta">
                  {entry.phase && <span className="cs-phase">{entry.phase}</span>}
                  {entry.date  && <span className="cs-date">{entry.date}</span>}
                </div>
                <h3 className="cs-title">{entry.title}</h3>

                {!isExpanded && (
                  <>
                    <div className="cs-preview">
                      {preview.map((line, j) => (
                        <p key={j} className="cs-preview-line">{stripBold(line)}</p>
                      ))}
                    </div>
                    <button className="cs-toggle" onClick={() => toggle(i)}>
                      Read more →
                    </button>
                  </>
                )}

                {isExpanded && (
                  <>
                    <div className="cs-body">
                      <BodyRenderer lines={entry.lines} />
                    </div>
                    <button className="cs-toggle cs-toggle--collapse" onClick={() => toggle(i)}>
                      Show less ↑
                    </button>
                  </>
                )}
              </article>
            )
          })}
        </div>
      )}
    </section>
  )
}

// --- Markdown entry parser ---

function parseEntries(text: string): Entry[] {
  const entries: Entry[] = []
  const sections = text.split(/\n(?=## )/)

  for (const section of sections) {
    const lines = section.split('\n')
    const titleLine = lines.find(l => l.startsWith('## '))
    if (!titleLine) continue

    const title = titleLine.replace(/^## /, '').trim()
    // Skip the file header
    if (title === 'On Human Oversight' || !title) {
      // Still include it — just no metadata
    }

    let date = ''
    let phase = ''
    const bodyStart: number[] = []

    for (let i = 1; i < lines.length; i++) {
      const l = lines[i]
      if (l.startsWith('**Date**:')) { date = l.replace('**Date**:', '').trim(); continue }
      if (l.startsWith('**Phase**:')) { phase = l.replace('**Phase**:', '').trim(); continue }
      bodyStart.push(i)
    }

    const bodyLines = bodyStart.map(i => lines[i])

    entries.push({ title, date, phase, lines: bodyLines })
  }

  return entries
}

// --- Body renderer (expanded view) ---

function BodyRenderer({ lines }: { lines: string[] }) {
  let inCode = false
  let codeLines: string[] = []
  const blocks: React.ReactNode[] = []

  const flush = (key: number) => {
    if (codeLines.length) {
      blocks.push(<pre key={`code-${key}`} className="cs-code"><code>{codeLines.join('\n')}</code></pre>)
      codeLines = []
    }
  }

  lines.forEach((line, i) => {
    if (!inCode && line.startsWith('```')) { inCode = true; return }
    if (inCode && line.startsWith('```')) { inCode = false; flush(i); return }
    if (inCode) { codeLines.push(line); return }

    if (line.startsWith('### ')) {
      blocks.push(<p key={i} className="cs-section-label">{line.slice(4)}</p>)
    } else if (line.startsWith('- ')) {
      blocks.push(<p key={i} className="cs-bullet">{inline(line.slice(2))}</p>)
    } else if (/^\d+\.\s/.test(line)) {
      blocks.push(<p key={i} className="cs-numbered">{inline(line)}</p>)
    } else if (line.trim() === '---') {
      blocks.push(<hr key={i} className="cs-hr" />)
    } else if (line.trim() === '') {
      blocks.push(<div key={i} className="cs-spacer" />)
    } else if (line.startsWith('|')) {
      blocks.push(<p key={i} className="cs-table-row">{line}</p>)
    } else if (line.trim()) {
      blocks.push(<p key={i} className="cs-p">{inline(line)}</p>)
    }
  })

  return <>{blocks}</>
}

function inline(text: string): React.ReactNode {
  const parts = text.split(/(\*\*[^*]+\*\*)/)
  if (parts.length === 1) return text
  return <>{parts.map((p, i) => p.startsWith('**') && p.endsWith('**')
    ? <strong key={i}>{p.slice(2, -2)}</strong>
    : p
  )}</>
}

function stripBold(text: string): string {
  return text.replace(/\*\*(.+?)\*\*/g, '$1')
}
