# CONVENTIONS.md

Code style, naming, and file organization rules for projects using
this framework. Conventions exist to eliminate low-stakes decisions
so attention goes to high-stakes ones.

---

## Python

### Style
- Formatter: **ruff** (`ruff format`) — enforced by pre-commit hook
- Linter: **ruff** (`ruff check`) with rule sets: `S` (security),
  `B` (bugbear), `T20` (no print statements in production code)
- Line length: 88 characters (ruff default)
- Python version: 3.11+

### Naming
```python
module_name.py          # lowercase, underscores
ClassName               # PascalCase
function_name()         # lowercase, underscores
CONSTANT_VALUE          # uppercase, underscores
_internal_function()    # single underscore prefix = module-private
```

### Imports — order
```python
# 1. Standard library
import os
import json

# 2. Third-party
import anthropic
from pydantic import BaseModel

# 3. Local
from core.budget_guard import BudgetGuard
from core.config import settings
```

### No print statements in production code
Use the logging module. `print()` is acceptable in scripts and
notebooks, not in `src/`. The ruff `T20` rule enforces this.

```python
# Wrong
print(f"Calling API with model {model}")

# Right
logger.info("Calling API", extra={"model": model})
```

### Config is loaded from environment only
No hardcoded values for URLs, model names, limits, or keys.
Load via `core/config.py` which reads from environment variables.

```python
# Wrong
client = anthropic.Anthropic(api_key="sk-ant-...")

# Right
from core.config import settings
client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
```

---

## TypeScript / React

### Style
- Formatter: **Prettier** (default config)
- Linter: **ESLint** (Vite default config)
- TypeScript strict mode: on

### Naming
```typescript
ComponentName.tsx       // PascalCase for components
useHookName.ts          // camelCase with "use" prefix for hooks
utilityFunction.ts      // camelCase for utilities
CONSTANT_VALUE          // uppercase for module-level constants
```

### Component structure
```typescript
// Props interface first
interface Props {
  title: string
  onSubmit: (value: string) => void
}

// Default export, named function
export default function ComponentName({ title, onSubmit }: Props) {
  // hooks
  // handlers
  // render
}
```

### No inline styles
Use CSS classes. `App.css` for layout. Component-level `.css`
files for component-specific styles. No `style={{ }}` props
except for truly dynamic values (e.g., computed widths).

---

## File Organization

### Python projects
```
src/
  core/           ← shared infrastructure (budget_guard, config, etc.)
  <feature>/      ← one directory per major feature area
tests/
  smoke_test.py   ← baseline; runs in < 30 seconds
  test_<module>.py
```

### React / TypeScript
```
src/
  components/     ← one file per component
  hooks/          ← custom hooks
  utils/          ← pure functions, no React dependency
  types/          ← shared TypeScript interfaces and types
```

### Documentation
```
framework/        ← all .md files
  CLAUDE.md       ← always first; auto-loaded by Claude Code
  PROJECT_STATUS.md
  DECISIONS.md
  ...
```

---

## Markdown

- Headers: `#` for title, `##` for sections, `###` for subsections
- Code blocks: always specify language (` ```python `, ` ```bash `, etc.)
- Tables: used for comparisons and reference data; not for prose
- Line length: not enforced in `.md` files — readability over width

---

## .env.example

Every required environment variable is documented in `.env.example`
with a placeholder value and a one-line comment explaining what it is:

```bash
# Anthropic API key — get from console.anthropic.com
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Maximum spend per session in USD
SESSION_BUDGET_USD=5.00

# Claude model for orchestration tasks
ORCHESTRATOR_MODEL=claude-sonnet-4-6
```

`.env.example` is committed. `.env` is never committed.

---

## The Anti-Patterns This Prevents

- **Magic strings**: model names, API URLs, and config values
  scattered through source files with no single source of truth
- **Silent failures**: `print()` debugging left in production code
  that obscures real log output
- **Convention drift**: inconsistent naming that makes grep unreliable
  and makes the codebase harder to navigate as it grows
- **Config in code**: credentials or environment-specific values
  that must be changed manually when deploying to a new environment
