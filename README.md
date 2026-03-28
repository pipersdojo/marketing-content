# marketing-content

Checklist-driven marketing campaign memory system with a chat-friendly CLI.

## What happens to legacy content?

Nothing is overwritten automatically.

- New campaign memory lives under `campaigns/<campaign-id>/...`.
- Older, pre-CLI assets are preserved under `archive/legacy-content/`.
- The CLI only writes to `campaigns/` unless you explicitly move files yourself.

## Quickstart

Run commands with no installation:

```bash
PYTHONPATH=src python -m marketing_agent.cli create 2026-04-back-to-basics
PYTHONPATH=src python -m marketing_agent.cli open 2026-04-back-to-basics
PYTHONPATH=src python -m marketing_agent.cli intake --interactive
PYTHONPATH=src python -m marketing_agent.cli set offer.name "Back to Basics Workshop"
PYTHONPATH=src python -m marketing_agent.cli readiness-score
PYTHONPATH=src python -m marketing_agent.cli generate --channels email,landing_page,social --provider template --variants 3
PYTHONPATH=src python -m marketing_agent.cli qa
PYTHONPATH=src python -m marketing_agent.cli export
```

Or via helper script:

```bash
./scripts/campaign list
```

## Repository memory structure

```text
campaigns/
  <campaign-id>/
    campaign.yaml
    artifacts/
    qa/
    history/
    exports/
```

`campaign.yaml` is the source of truth for campaign memory.

## Prompt-driven generation (Sprint A)

- Prompt templates are stored under `prompts/` and `prompts/channels/`.
- `campaign generate` supports:
  - `--provider template` (local deterministic drafts, no API key)
  - `--provider openai` (calls OpenAI Chat Completions API)
  - `--model <model-name>` and `--variants <n>`

For OpenAI provider:

```bash
export OPENAI_API_KEY=your_key_here
PYTHONPATH=src python -m marketing_agent.cli generate --channels email --provider openai --model gpt-4.1-mini --variants 2
```

## Tests

```bash
PYTHONPATH=src python -m unittest tests/test_cli.py -v
```
