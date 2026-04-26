# vscode-agent-template

A reusable VS Code multi-agent stack: **Cline + Roo Code + Continue**, routed through **LiteLLM** with **OpenRouter** primary and **Ollama** fallback. Drop-in for any project.

## What you get

- **Six role-specialized agents** (head-dev, co-lead, code-gen, autocomplete, quick-shell, long-runner) with prompt files in `agents/`
- **LiteLLM proxy** — one config maps friendly names to providers, automatic Ollama fallback when offline or rate-limited
- **MCP servers** pre-configured: filesystem, git, github
- **Project profiles** — overlays for project-specific tuning. Includes a `neurotrader` profile with a Trading Journal MCP

## Install

```bash
# In the project you want to add agents to:
curl -fsSL https://raw.githubusercontent.com/clay10fields/vscode-agent-template/main/scripts/setup.sh | bash

# With a profile:
curl -fsSL https://raw.githubusercontent.com/clay10fields/vscode-agent-template/main/scripts/setup.sh | bash -s -- --profile neurotrader
```

Or clone first, then run `scripts/setup.sh` from the target project.

## Stack

| Role           | VS Code tool      | Primary model              | Local fallback        |
| -------------- | ----------------- | -------------------------- | --------------------- |
| HEAD DEV       | Cline (Plan)      | claude-opus-4.6            | qwen3:32b             |
| CO-LEAD        | Cline (Ask)       | claude-sonnet-4.6          | qwen3:14b             |
| CODE GEN       | Roo Code          | deepseek-v3.5 / sonnet-4.6 | qwen2.5-coder:32b     |
| AUTOCOMPLETE   | Continue          | codestral / qwen2.5-coder  | qwen2.5-coder:7b      |
| QUICK SHELL    | Cline terminal    | sonnet-4.6                 | qwen2.5-coder:14b     |
| LONG-RUNNER    | OpenClaw via MCP  | kimi-k2 / sonnet caching   | —                     |

## Profiles

- **`neurotrader`** — Trading Journal MCP, NeuroTrader-aware agent prompts, slash commands `/run-cycle`, `/audit-ghost-code`, `/check-trades`, `/journal`

Add your own under `profiles/<name>/`.

## Layout

```
vscode-agent-template/
├── .vscode/                 # VS Code settings + extension recommendations
├── .cline/                  # Cline rules + system prompts
├── agents/                  # Role prompt files (head-dev, co-lead, ...)
├── mcp/                     # MCP server configs + custom servers
│   └── servers/
│       └── trading-journal/ # Reads SQLite, writes Obsidian markdown
├── profiles/                # Project-specific overlays
│   └── neurotrader/
├── scripts/                 # setup.sh, ollama-startup.sh, litellm-up.sh
└── docs/                    # Architecture notes
```

## License

MIT
