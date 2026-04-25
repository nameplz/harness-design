# Claude Code Bootstrap Notes

- Set `runtime.platform` to `claude-code`.
- Set `runtime.adapter_path` to `harness/adapters/claude-code`.
- Keep CLI-specific approval and delegation instructions inside the adapter files.
- Do not duplicate shared planning, QA, or artifact rules into project-local prompts unless the project truly changes them.
