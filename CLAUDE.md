# Dify Skills

Claude Code skills for generating Dify apps and plugins.

## Structure

- `skills/` — 8 specialist skills (pure markdown knowledge documents)
- `templates/` — Ready-to-import DSL YAML files
- `hooks/` — Claude Code session hooks
- `evaluations/` — Test scenarios per skill
- `docs/` — Research and design documentation

## How It Works

The `using-dify-skills` router skill is loaded at session start and dispatches to specialist skills based on user intent. Skills teach the LLM how to generate valid Dify DSL YAML or plugin code.

## Testing

Import any template YAML into a Dify instance to verify validity:
- Dify Console → Studio → Import DSL File
- Or via API: POST /console/api/apps/imports

## Conventions

- Skills are markdown — no code, no schemas
- Each node type documented with minimal + full config
- Templates are complete, import-ready YAML
- Evaluations define expected behavior per query
