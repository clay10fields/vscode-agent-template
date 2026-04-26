# Cline Rules — vscode-agent-template

These rules are loaded automatically by Cline on every conversation in this project.

## Operating principles

1. **Plan first, code second.** Use Plan mode for anything that touches >1 file or changes architecture. Hand off to Act mode only after the plan is reviewed.
2. **Read before writing.** Always read the relevant files into context before editing. Never guess at file contents.
3. **Small steps.** Prefer many small commits over one large one. Each commit should leave the project in a working state.
4. **Tests are not optional.** When changing behavior, add or update tests. Run the test suite before declaring done.
5. **No silent fallbacks.** If a primary model is unavailable and LiteLLM falls back to local Ollama, surface that to the user — don't pretend nothing changed.

## Role routing (model: head-dev, co-lead, etc.)

Models are friendly names mapped by the LiteLLM proxy at `http://localhost:4000`. See `litellm.config.yaml` for the routing.

- Use `head-dev` for architecture, code review, and big decisions.
- Use `code-gen` for actual code writing and refactors.
- Use `co-lead` for research, docs, and planning that doesn't need top-tier reasoning.
- Use `quick-shell` for short shell/terminal tasks.
- Use `long-runner` for overnight or multi-hour tasks (prompt-cached Sonnet or Kimi K2).

Switch by changing the `cline.openAiModelId` in workspace settings or selecting from the model picker.

## Filesystem hygiene

- Don't create files outside the project root unless explicitly asked.
- Never commit `.env`, secrets, or anything in `journal-vault.local/` or `qdrant-data/`.
- Treat anything in `profiles/` as a layered overlay — the bare project should still work without any profile applied.

## When stuck

Hand off to `head-dev` for a second opinion before going down a long debugging path. Write what you've tried into `docs/dev-log.md` so the next session has context.
