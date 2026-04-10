/**
 * Cloudflare Worker — Anthropic API proxy for build-with-ai demo
 *
 * Responsibilities:
 * - Hold the Anthropic API key server-side (never in the JS bundle)
 * - Rate limit: 10 requests per IP per hour via KV
 * - CORS: allow requests from the GitHub Pages origin only
 * - Forward POST /messages to Anthropic, stream response back
 *
 * Secrets (set via `wrangler secret put`):
 *   ANTHROPIC_API_KEY
 *
 * KV namespaces (set up via `wrangler kv:namespace create RATE_LIMIT_KV`):
 *   RATE_LIMIT_KV
 */

interface Env {
  ANTHROPIC_API_KEY: string
  RATE_LIMIT_KV?: KVNamespace  // Optional — rate limiting disabled if not bound
}

const ALLOWED_ORIGIN = 'https://gr8drmrslc.github.io'
const ANTHROPIC_API = 'https://api.anthropic.com/v1/messages'
const RATE_LIMIT_MAX = 10
const RATE_LIMIT_WINDOW_SEC = 3600  // 1 hour

const CORS_HEADERS: Record<string, string> = {
  'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, x-api-key, anthropic-version, anthropic-beta',
  'Access-Control-Max-Age': '86400',
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    // CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS_HEADERS })
    }

    // Only accept POST
    if (request.method !== 'POST') {
      return jsonError(405, 'Method not allowed')
    }

    // Rate limiting — skip gracefully if KV not configured
    if (env.RATE_LIMIT_KV) {
      const ip = request.headers.get('CF-Connecting-IP') ?? 'unknown'
      const key = `rl:${ip}`
      const raw = await env.RATE_LIMIT_KV.get(key)
      const count = raw ? parseInt(raw, 10) : 0

      if (count >= RATE_LIMIT_MAX) {
        return jsonError(
          429,
          'Rate limit reached — 10 requests per hour per visitor. Try again later.',
        )
      }

      // Increment with TTL so the window resets automatically
      await env.RATE_LIMIT_KV.put(key, String(count + 1), {
        expirationTtl: RATE_LIMIT_WINDOW_SEC,
      })
    }

    // Parse and validate request body
    let body: string
    try {
      body = await request.text()
      const parsed = JSON.parse(body)
      // Enforce Haiku — do not allow callers to request expensive models
      if (parsed.model && !parsed.model.includes('haiku')) {
        return jsonError(400, 'Only Haiku model is permitted on this proxy.')
      }
    } catch {
      return jsonError(400, 'Invalid JSON body')
    }

    // Forward to Anthropic
    let upstream: Response
    try {
      upstream = await fetch(ANTHROPIC_API, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': env.ANTHROPIC_API_KEY,
          'anthropic-version': '2023-06-01',
        },
        body,
      })
    } catch (err) {
      return jsonError(502, 'Upstream API unreachable')
    }

    // If Anthropic returned an error, surface it to the client
    if (!upstream.ok) {
      const errBody = await upstream.text()
      return new Response(errBody, {
        status: upstream.status,
        headers: {
          'Content-Type': 'application/json',
          ...CORS_HEADERS,
        },
      })
    }

    // Stream the response back — preserve content-type for SSE
    return new Response(upstream.body, {
      status: 200,
      headers: {
        'Content-Type': upstream.headers.get('Content-Type') ?? 'application/json',
        'Cache-Control': 'no-store',
        ...CORS_HEADERS,
      },
    })
  },
}

function jsonError(status: number, message: string): Response {
  return new Response(JSON.stringify({ error: message }), {
    status,
    headers: { 'Content-Type': 'application/json', ...CORS_HEADERS },
  })
}
