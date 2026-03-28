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
PYTHONPATH=src python -m marketing_agent.cli run --channels email --provider template --variants 1
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

## Rubric QA (Sprint B)

- QA scoring is rubric-driven via `qa/rubric.json`.
- Override rubric location with:
  - `--rubric <path>`
  - or `MARKETING_AGENT_RUBRIC_FILE=/path/to/rubric.json`
- Use strict mode to fail command execution when critical fail conditions are present:

```bash
PYTHONPATH=src python -m marketing_agent.cli qa --strict
```

## One-command flow (Sprint C)

Run generate + qa + export in one command:

```bash
PYTHONPATH=src python -m marketing_agent.cli run --channels email,landing_page --provider template --variants 2 --strict-qa
```

## Plain-text chat mode (Sprint D)

If you want natural-language style commands, use:

```bash
PYTHONPATH=src python -m marketing_agent.cli chat "hey bro, i need to make a new marketing campaign"
PYTHONPATH=src python -m marketing_agent.cli chat "run campaign"
PYTHONPATH=src python -m marketing_agent.cli chat
```

## Tests

```bash
PYTHONPATH=src python -m unittest tests/test_cli.py -v
```
