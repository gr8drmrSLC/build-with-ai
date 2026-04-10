import { useState, useRef } from 'react'
import Anthropic from '@anthropic-ai/sdk'
import './OrchestratorPanel.css'

const SYSTEM_PROMPT = `You are an AI project architect using the build-with-ai framework.

When a user describes a project idea, decompose it using this exact structure:

**Complexity tier**: [Simple | Moderate | Complex] — one sentence explaining why.

**Phases**
1. Phase name — what gets built and why this comes first
2. (continue for each phase, 3–6 total)

**Key risks**
- Risk — why it matters and how the framework addresses it
(3–5 risks: architectural, technical, and operational)

**Agent assignments**
| Phase | Agent | Reason |
|-------|-------|--------|
| (map each phase to: Claude Code, Codex, Gemini, or Haiku) |

**First atomic task**
The single first task to propose after reading this decomposition.
One sentence. Specific enough to execute without further clarification.

---
Rules:
- Be specific to the project described, not generic
- Apply the framework honestly — if the idea is simple, say so
- Flag any security or cost risks you see in the architecture
- Do not pad. A 3-phase project does not need 6 phases.`

export default function OrchestratorPanel() {
  const [input, setInput] = useState('')
  const [output, setOutput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const abortRef = useRef<AbortController | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!input.trim() || loading) return

    const apiKey = import.meta.env.VITE_ANTHROPIC_API_KEY
    if (!apiKey) {
      setError('VITE_ANTHROPIC_API_KEY not set in .env.local')
      return
    }

    setLoading(true)
    setOutput('')
    setError('')

    abortRef.current = new AbortController()

    try {
      // KNOWN TRADEOFF: API key exposed at build time via env var.
      // Acceptable for portfolio demo. Production would use a
      // Cloudflare Worker proxy. See DECISIONS.md ADR-005.
      const client = new Anthropic({ apiKey, dangerouslyAllowBrowser: true })

      const stream = client.messages.stream({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 1024,
        system: SYSTEM_PROMPT,
        messages: [{ role: 'user', content: input.trim() }],
      })

      for await (const event of stream) {
        if (abortRef.current?.signal.aborted) break
        if (
          event.type === 'content_block_delta' &&
          event.delta.type === 'text_delta'
        ) {
          const delta = event.delta as { type: 'text_delta'; text: string }
          setOutput(prev => prev + delta.text)
        }
      }
    } catch (err) {
      if (!abortRef.current?.signal.aborted) {
        setError(err instanceof Error ? err.message : 'Unknown error')
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

// Minimal markdown renderer — bold, headers, tables, bullets
// Avoids a full markdown library dependency for this scope
function OutputRenderer({ text }: { text: string }) {
  const lines = text.split('\n')

  return (
    <div className="output-content">
      {lines.map((line, i) => {
        if (line.startsWith('**') && line.endsWith('**') && !line.slice(2, -2).includes('**')) {
          return <p key={i} className="output-bold">{line.slice(2, -2)}</p>
        }
        if (/^\*\*(.+)\*\*:/.test(line)) {
          return <p key={i} className="output-section" dangerouslySetInnerHTML={{ __html: line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>') }} />
        }
        if (line.startsWith('## ')) {
          return <h3 key={i} className="output-h2">{line.slice(3)}</h3>
        }
        if (line.startsWith('# ')) {
          return <h2 key={i} className="output-h1">{line.slice(2)}</h2>
        }
        if (/^\d+\.\s/.test(line)) {
          return <p key={i} className="output-numbered">{line}</p>
        }
        if (line.startsWith('- ')) {
          return <p key={i} className="output-bullet">{line.slice(2)}</p>
        }
        if (line.startsWith('|')) {
          return <p key={i} className="output-table-row">{line}</p>
        }
        if (line.trim() === '---') {
          return <hr key={i} className="output-divider" />
        }
        if (line.trim() === '') {
          return <div key={i} className="output-spacer" />
        }
        return (
          <p key={i} className="output-line" dangerouslySetInnerHTML={{ __html: line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>') }} />
        )
      })}
    </div>
  )
}
