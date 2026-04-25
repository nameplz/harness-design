# Codex Bootstrap Notes

- Set `runtime.platform` to `codex`.
- Set `runtime.adapter_path` to `harness/adapters/codex`.
- Keep shared role prompts in `harness/roles/` unless the project needs Codex-specific overrides.
- Use `runtime.capabilities` only when the project needs to override the adapter defaults.
