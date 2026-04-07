#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${HOME}/.claude"
SKILL_DIR="${CLAUDE_DIR}/skills/vaultweaver"

echo "Installing Vaultweaver..."
echo ""

# Install as skill directory
mkdir -p "${SKILL_DIR}/scripts" "${SKILL_DIR}/references"
cp "${SCRIPT_DIR}/SKILL.md"                    "${SKILL_DIR}/SKILL.md"
cp "${SCRIPT_DIR}/hooks.json"                  "${SKILL_DIR}/hooks.json"
cp "${SCRIPT_DIR}/settings.json"               "${SKILL_DIR}/settings.json"
cp "${SCRIPT_DIR}/scripts/check-wiki-drift.sh" "${SKILL_DIR}/scripts/check-wiki-drift.sh"
cp "${SCRIPT_DIR}/scripts/search.py"           "${SKILL_DIR}/scripts/search.py"
cp "${SCRIPT_DIR}/references/operations.md"    "${SKILL_DIR}/references/operations.md"
chmod +x "${SKILL_DIR}/scripts/check-wiki-drift.sh"
echo "  Installed: ~/.claude/skills/vaultweaver/"

# Also install as command for /wiki access
mkdir -p "${CLAUDE_DIR}/commands"
cp "${SCRIPT_DIR}/SKILL.md" "${CLAUDE_DIR}/commands/wiki.md"
echo "  Command:   ~/.claude/commands/wiki.md"

echo ""
echo "Vaultweaver installed. Commands:"
echo ""
echo "  /wiki init \"Topic\"   Create wiki     /wiki lint     Health checks"
echo "  /wiki ingest         Process sources  /wiki search   BM25 search"
echo "  /wiki compile        Build articles   /wiki status   Stats"
echo "  /wiki query          Ask questions    /wiki serve    Web UI"
echo ""
echo "Auto-triggers: drift detection on session start, auto-ingest on session end."
