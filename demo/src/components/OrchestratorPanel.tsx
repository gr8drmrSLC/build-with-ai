import { useState, useRef } from 'react'
import './OrchestratorPanel.css'

// Cloudflare Worker proxy URL — key lives server-side. See DECISIONS.md ADR-006.
const WORKER_URL = import.meta.env.VITE_WORKER_URL ?? ''

const SYSTEM_PROMPT = `You are an AI project architect using the build-with-ai framework.

When a user describes a project idea, decompose it using this exact structure:

**Complexity tier**: [Simple | Moderate | Complex]. One sentence explaining why.

**Phases**
1. Phase name. What gets built and why this comes first.
2. (continue for each phase, 3 to 6 total)

**Key risks**
1. Risk name. Why it matters and how the framework addresses it.
(3 to 5 risks covering architectural, technical, and operational concerns)

**Agent assignments**
| Phase | Agent | Reason |
|-------|-------|--------|
| (map each phase to: Claude Code, Codex, Gemini, or Haiku) |

**First atomic task**
The single first task to propose after reading this decomposition. One sentence, specific enough to execute without further clarification.

---
Rules:
Use numbered lists, not bullet points. Write in complete sentences with periods. Be specific to the project described, not generic. Apply the framework honestly. If the idea is simple, say so. Flag any security or cost risks in the architecture. Do not pad. A 3-phase project does not need 6 phases.`

export default function OrchestratorPanel() {
  const [input, setInput] = useState('')
  const [output, setOutput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const abortRef = useRef<AbortController | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!input.trim() || loading) return

    if (!WORKER_URL) {
      setError('VITE_WORKER_URL not configured.')
      return
    }

    setLoading(true)
    setOutput('')
    setError('')
    abortRef.current = new AbortController()

    try {
      const res = await fetch(WORKER_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: abortRef.current.signal,
        body: JSON.stringify({
          model: 'claude-haiku-4-5-20251001',
          max_tokens: 1024,
          stream: true,
          system: SYSTEM_PROMPT,
          messages: [{ role: 'user', content: input.trim() }],
        }),
      })

      if (!res.ok) {
        const body = await res.text()
        if (res.status === 429) {
          setError('Rate limit reached — 10 requests per hour. Try again later.')
        } else {
          setError(`Error ${res.status}: ${body}`)
        }
        return
      }

      // Parse Anthropic SSE stream
      const reader = res.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const data = line.slice(6).trim()
          if (data === '[DONE]') break
          try {
            const evt = JSON.parse(data)
            if (
              evt.type === 'content_block_delta' &&
              evt.delta?.type === 'text_delta'
            ) {
              setOutput(prev => prev + evt.delta.text)
            }
          } catch {
            // skip malformed lines
          }
        }
      }
    } catch (err) {
      if (err instanceof Error && err.name !== 'AbortError') {
        setError(err.message)
      }
    } finally {
      setLoading(false)
    }
  }

  function handleStop() {
    abortRef.current?.abort()
    setLoading(false)
  }

  return (
    <section className="panel orchestrator-panel" aria-label="Orchestrator">
      <p className="panel-label">Try It Live</p>
      <p className="orchestrator-description">
        Describe a project idea. The framework decomposes it into phases,
        risks, agent assignments, and a first task.
      </p>

      <form onSubmit={handleSubmit} className="orchestrator-form">
        <textarea
          className="orchestrator-input"
          placeholder="e.g. A bot that monitors Hacker News for mentions of my company and sends a Slack digest every morning"
          value={input}
          onChange={e => setInput(e.target.value)}
          rows={4}
          disabled={loading}
        />
        <div className="orchestrator-actions">
          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !input.trim()}
          >
            {loading ? 'Thinking...' : 'Decompose'}
          </button>
          {loading && (
            <button type="button" className="btn-stop" onClick={handleStop}>
              Stop
            </button>
          )}
        </div>
      </form>

      {error && <p className="orchestrator-error">{error}</p>}

      {output && (
        <div className="orchestrator-output">
          <OutputRenderer text={output} />
        </div>
      )}
    </section>
  )
}

function OutputRenderer({ text }: { text: string }) {
  const lines = text.split('\n')
  return (
    <div className="output-content">
      {lines.map((line, i) => {
        if (line.startsWith('## ')) return <h3 key={i} className="output-h2">{line.slice(3)}</h3>
        if (line.startsWith('# '))  return <h2 key={i} className="output-h1">{line.slice(2)}</h2>
        if (/^\*\*(.+)\*\*:/.test(line)) return <p key={i} className="output-section" dangerouslySetInnerHTML={{ __html: line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>') }} />
        if (line.startsWith('**') && line.endsWith('**') && !line.slice(2,-2).includes('**')) return <p key={i} className="output-bold">{line.slice(2,-2)}</p>
        if (/^\d+\.\s/.test(line)) return <p key={i} className="output-numbered">{line}</p>
        if (line.startsWith('- '))  return <p key={i} className="output-bullet">{line.slice(2)}</p>
        if (line.startsWith('|'))   return <p key={i} className="output-table-row">{line}</p>
        if (line.trim() === '---')  return <hr key={i} className="output-divider" />
        if (line.trim() === '')     return <div key={i} className="output-spacer" />
        return <p key={i} className="output-line" dangerouslySetInnerHTML={{ __html: line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>') }} />
      })}
    </div>
  )
}
