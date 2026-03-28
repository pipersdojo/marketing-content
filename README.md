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
PYTHONPATH=src python -m marketing_agent.cli intake
PYTHONPATH=src python -m marketing_agent.cli set offer.name "Back to Basics Workshop"
PYTHONPATH=src python -m marketing_agent.cli readiness-score
PYTHONPATH=src python -m marketing_agent.cli generate --channels email,landing_page,social
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
