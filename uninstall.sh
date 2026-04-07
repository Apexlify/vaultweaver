#!/usr/bin/env bash
set -euo pipefail

CLAUDE_DIR="${HOME}/.claude"

echo "Uninstalling Vaultweaver..."

rm -rf "${CLAUDE_DIR}/skills/vaultweaver"
echo "  Removed: ~/.claude/skills/vaultweaver/"

rm -f "${CLAUDE_DIR}/commands/wiki.md"
echo "  Removed: ~/.claude/commands/wiki.md"

rm -f "${CLAUDE_DIR}/rules/common/wiki.md"
echo "  Removed: ~/.claude/rules/common/wiki.md (if present)"

echo ""
echo "Done. Wiki data in your projects (raw/, wiki/) is untouched."
