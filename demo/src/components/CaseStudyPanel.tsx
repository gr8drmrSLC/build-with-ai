import { useEffect, useState } from 'react'
import './CaseStudyPanel.css'

const NARRATIVE_URL =
  'https://raw.githubusercontent.com/gr8drmrSLC/build-with-ai/master/framework/PROJECT_NARRATIVE.md'

type Status = 'loading' | 'ready' | 'error'

export default function CaseStudyPanel() {
  const [content, setContent] = useState('')
  const [status, setStatus] = useState<Status>('loading')

  useEffect(() => {
    let cancelled = false

    fetch(NARRATIVE_URL)
      .then(res => {
        if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
        return res.text()
      })
      .then(text => {
        if (!cancelled) {
          setContent(text)
          setStatus('ready')
        }
      })
      .catch(() => {
        if (!cancelled) setStatus('error')
      })

    return () => { cancelled = true }
  }, [])

  return (
    <section className="panel case-study-panel" aria-label="Case Studies">
      <p className="panel-label">Case Studies</p>

      {status === 'loading' && (
        <p className="case-study-loading">Loading narrative...</p>
      )}

      {status === 'error' && (
        <p className="case-study-error">
          Could not fetch PROJECT_NARRATIVE.md — check network or repo visibility.
        </p>
      )}

      {status === 'ready' && (
        <div className="case-study-content">
          <NarrativeRenderer text={content} />
        </div>
      )}
    </section>
  )
}

// Renders the markdown patterns used in PROJECT_NARRATIVE.md:
// headers, bold, bullets, numbered lists, code blocks, blockquotes, hr
function NarrativeRenderer({ text }: { text: string }) {
  const blocks = parseBlocks(text)

  return (
    <div className="narrative-body">
      {blocks.map((block, i) => {
        switch (block.type) {
          case 'h1':
            return <h2 key={i} className="narrative-h1">{block.text}</h2>
          case 'h2':
            return <h3 key={i} className="narrative-h2">{block.text}</h3>
          case 'h3':
            return <h4 key={i} className="narrative-h3">{block.text}</h4>
          case 'hr':
            return <hr key={i} className="narrative-hr" />
          case 'meta':
            return <p key={i} className="narrative-meta">{block.text}</p>
          case 'code':
            return (
              <pre key={i} className="narrative-code">
                <code>{block.text}</code>
              </pre>
            )
          case 'bullet':
            return <p key={i} className="narrative-bullet">{inline(block.text)}</p>
          case 'numbered':
            return <p key={i} className="narrative-numbered">{inline(block.text)}</p>
          case 'blockquote':
            return <blockquote key={i} className="narrative-quote">{inline(block.text)}</blockquote>
          case 'blank':
            return <div key={i} className="narrative-spacer" />
          default:
            return block.text.trim()
              ? <p key={i} className="narrative-p">{inline(block.text)}</p>
              : null
        }
      })}
    </div>
  )
}

type Block = { type: string; text: string }

function parseBlocks(text: string): Block[] {
  const lines = text.split('\n')
  const blocks: Block[] = []
  let inCode = false
  let codeLines: string[] = []

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]

    // Code fence open
    if (!inCode && line.startsWith('```')) {
      inCode = true
      codeLines = []
      continue
    }
    // Code fence close
    if (inCode && line.startsWith('```')) {
      inCode = false
      blocks.push({ type: 'code', text: codeLines.join('\n') })
      continue
    }
    if (inCode) {
      codeLines.push(line)
      continue
    }

    if (line.startsWith('# '))  { blocks.push({ type: 'h1', text: line.slice(2) }); continue }
    if (line.startsWith('## ')) { blocks.push({ type: 'h2', text: line.slice(3) }); continue }
    if (line.startsWith('### ')){ blocks.push({ type: 'h3', text: line.slice(4) }); continue }
    if (line.trim() === '---')  { blocks.push({ type: 'hr',   text: '' }); continue }
    if (line.startsWith('**Date**') || line.startsWith('**Phase**')) {
      blocks.push({ type: 'meta', text: line.replace(/\*\*(.+?)\*\*/g, '$1') }); continue
    }
    if (line.startsWith('- '))  { blocks.push({ type: 'bullet',   text: line.slice(2) }); continue }
    if (/^\d+\.\s/.test(line))  { blocks.push({ type: 'numbered', text: line }); continue }
    if (line.startsWith('> '))  { blocks.push({ type: 'blockquote', text: line.slice(2) }); continue }
    if (line.trim() === '')     { blocks.push({ type: 'blank', text: '' }); continue }

    blocks.push({ type: 'p', text: line })
  }

  return blocks
}

// Inline bold rendering — **text** → <strong>
function inline(text: string): React.ReactNode {
  const parts = text.split(/(\*\*[^*]+\*\*)/)
  if (parts.length === 1) return text
  return (
    <>
      {parts.map((part, i) =>
        part.startsWith('**') && part.endsWith('**')
          ? <strong key={i}>{part.slice(2, -2)}</strong>
          : part
      )}
    </>
  )
}
