# Adapter Layer

This directory contains CLI-specific harness adapters.

Each adapter keeps the core harness contract intact while describing how a particular runtime should execute it.

## Required Files

Every adapter directory should include:

- `operator.prompt.md`
- `capabilities.yaml`
- `bootstrap-notes.md`

## Rules

- Adapters may change execution mechanics, not the core artifact contract.
- Capability gaps should degrade execution mode rather than weaken QA or completion rules.
- All adapter paths used by `project.yaml.runtime` must exist explicitly.

## Included Adapters

- `codex`
- `claude-code`
- `gemini-cli`
