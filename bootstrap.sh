#!/usr/bin/env bash
# bootstrap.sh — install the build-with-ai framework into a new project
#
# Usage: run this from your new project directory
#   bash /path/to/build-with-ai/bootstrap.sh
#
# What it does:
#   1. Copies framework/ policy files into your project's framework/ directory
#   2. Creates src/core/ with Python module stubs
#   3. Creates a .env.example stub
#   4. Prints next steps

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$(pwd)"

if [ "$SCRIPT_DIR" = "$TARGET_DIR" ]; then
  echo "ERROR: Run this from your new project directory, not from build-with-ai itself."
  echo "  cd /path/to/your-new-project"
  echo "  bash /path/to/build-with-ai/bootstrap.sh"
  exit 1
fi

echo "Installing build-with-ai framework into: $TARGET_DIR"
echo ""

# --- 1. Copy framework policy files ---

mkdir -p "$TARGET_DIR/framework"

POLICY_FILES=(
  "CLAUDE.md"
  "AI_DELEGATION_POLICY.md"
  "ARCHITECTURE.md"
  "BUDGET_POLICY.md"
  "CONVENTIONS.md"
  "DEVELOPMENT_PROTOCOL.md"
  "GIT_POLICY.md"
  "SECURITY.md"
  "USER_MANUAL.md"
  "PROJECT_BRIEF_TEMPLATE.md"
)

for file in "${POLICY_FILES[@]}"; do
  src="$SCRIPT_DIR/framework/$file"
  dst="$TARGET_DIR/framework/$file"
  if [ -f "$dst" ]; then
    echo "  SKIP (exists): framework/$file"
  elif [ -f "$src" ]; then
    cp "$src" "$dst"
    echo "  COPY: framework/$file"
  else
    echo "  MISSING in source: framework/$file"
  fi
done

# Project-specific state files — always create fresh, never copy
for state_file in "PROJECT_STATUS.md" "DECISIONS.md" "PROJECT_NARRATIVE.md"; do
  dst="$TARGET_DIR/framework/$state_file"
  if [ ! -f "$dst" ]; then
    touch "$dst"
    echo "  CREATE (empty): framework/$state_file"
  else
    echo "  SKIP (exists): framework/$state_file"
  fi
done

echo ""

# --- 2. Create src/core/ Python module stubs ---

mkdir -p "$TARGET_DIR/src/core"

touch "$TARGET_DIR/src/__init__.py"
touch "$TARGET_DIR/src/core/__init__.py"

CORE_MODULES=(
  "config.py"
  "budget_guard.py"
  "agent_dispatcher.py"
  "task_schema.py"
  "logging_config.py"
  "rate_limiter.py"
)

for module in "${CORE_MODULES[@]}"; do
  dst="$TARGET_DIR/src/core/$module"
  if [ ! -f "$dst" ]; then
    echo "# $module — stub created by bootstrap.sh" > "$dst"
    echo "# See build-with-ai/src/core/ for reference implementations" >> "$dst"
    echo "  CREATE: src/core/$module"
  else
    echo "  SKIP (exists): src/core/$module"
  fi
done

echo ""

# --- 3. Create .env.example stub ---

env_example="$TARGET_DIR/.env.example"
if [ ! -f "$env_example" ]; then
  cat > "$env_example" <<'EOF'
# .env.example — copy to .env and fill in values
# Never commit .env — only .env.example belongs in the repo

# Anthropic API (if using Claude)
# ANTHROPIC_API_KEY=sk-ant-...

# Add project-specific secrets below
EOF
  echo "  CREATE: .env.example"
else
  echo "  SKIP (exists): .env.example"
fi

echo ""

# --- 4. Next steps ---

echo "Done. Next steps:"
echo ""
echo "  1. If you haven't already, create .gitignore as your FIRST commit:"
echo "     Add: .env, .env.*, *.pem, *.key, __pycache__, .venv, *.db, *.sqlite"
echo "     Add: /logs/, /data/, /output/, node_modules/"
echo "     Add a blank line before: !.env.example  (inline comments break negation)"
echo ""
echo "  2. Fill out framework/PROJECT_BRIEF_TEMPLATE.md"
echo "     The more complete this is before the first Claude Code session,"
echo "     the less time that session wastes on scope clarification."
echo ""
echo "  3. Edit framework/CLAUDE.md — update the project name at the top"
echo ""
echo "  4. Fill out framework/PROJECT_STATUS.md and framework/DECISIONS.md"
echo "     with whatever is already known or decided"
echo ""
echo "  5. Open Claude Code and say:"
echo "     'Read CLAUDE.md, then read framework/PROJECT_BRIEF_TEMPLATE.md."
echo "      Confirm understanding and propose the first task.'"
echo ""
echo "See framework/USER_MANUAL.md for the full workflow."
