# Dify Skills

Claude Code skills for generating and debugging [Dify](https://dify.ai) applications and plugins. Generate valid DSL YAML from natural language descriptions, debug broken workflows, create custom plugins, and deploy apps programmatically.

Inspired by [n8n-skills](https://github.com/czlonkowski/n8n-skills).

## Skills

| Skill | Description |
|-------|-------------|
| `using-dify-skills` | Router — dispatches to specialist skills |
| `dify-dsl-expert` | DSL format, validation, structure rules |
| `dify-node-catalog` | All 40 node types with configurations |
| `dify-workflow-patterns` | 8 architectural templates for common use cases |
| `dify-variable-system` | Variable passing and selector syntax |
| `dify-app-debugger` | Parse and fix broken DSL files |
| `dify-import-export` | Deploy apps via API |
| `dify-plugin-maker` | Create custom Dify plugins (tools, models, agents, triggers) |

## Quick Start

### Install as Claude Code plugin
```bash
cd /path/to/your/project
claude plugin add /path/to/dify-skills
```

### Or copy skills directory
```bash
cp -r dify-skills/skills/* ~/.claude/skills/
```

## Usage

Once installed, tell Claude Code what you want:

```
"Build me a RAG chatbot that searches my product docs"
"Create a workflow that fetches data from an API, processes each item, and returns a summary"
"Debug this DSL file — it fails on import"
"Create a Dify plugin that integrates with Slack"
```

The router skill automatically dispatches to the right specialist.

## Workflow Patterns

| Pattern | Mode | Architecture |
|---------|------|-------------|
| Simple Chatbot | advanced-chat | Start → LLM → Answer |
| RAG Chatbot | advanced-chat | Start → Knowledge → LLM → Answer |
| Text Generation | workflow | Start → LLM → End |
| Agent with Tools | advanced-chat | Start → Agent → Answer |
| Data Pipeline | workflow | Start → Code → Iteration[LLM] → End |
| API Orchestration | workflow | Start → HTTP → If-Else → End |
| Document Analysis | workflow | Start → DocExtractor → LLM → End |
| Conditional Routing | advanced-chat | Start → Classifier → [LLM A/B/C] → Answer |

## Templates

Ready-to-import DSL YAML files in `templates/`:
- `simple-workflow.yml` — Start → LLM → End
- `simple-chatbot.yml` — Start → LLM (with memory) → Answer
- `rag-chatbot.yml` — Start → Knowledge Retrieval → LLM → Answer
- `data-pipeline.yml` — Start → Code → Iteration → End
- `api-orchestration.yml` — Start → HTTP → Code → End

## Supported Node Types (40)

**Core**: start, end, answer, llm
**Logic**: if-else, code, template-transform, iteration, loop, list-operator, assigner
**Data**: knowledge-retrieval, http-request, tool, datasource, document-extractor
**Advanced**: agent, parameter-extractor, question-classifier, human-input, app, variable-aggregator
**SQL**: vannaai-connector, vannaai-question, vannaai-training, sql-output-chart, sql-output-table, sql-output-summary
**Other**: cache-retrieve, cache-store, explainer, summarizer, filtered-knowledge-retrieval, knowledge-index
**Triggers**: trigger-webhook, trigger-schedule, trigger-plugin

## Project Structure

```
dify-skills/
├── skills/           # 8 specialist skills (markdown knowledge)
│   ├── using-dify-skills/       # Router
│   ├── dify-dsl-expert/         # DSL format + validation
│   ├── dify-node-catalog/       # Node configs (core/logic/data/advanced)
│   ├── dify-workflow-patterns/  # 8 workflow archetypes
│   ├── dify-variable-system/    # Variable wiring
│   ├── dify-app-debugger/       # Debug protocol + error catalog
│   ├── dify-import-export/      # API deployment
│   └── dify-plugin-maker/       # Plugin development
├── templates/        # Ready-to-import DSL YAML files
├── hooks/            # Claude Code hooks (session-start)
├── evaluations/      # Test scenarios per skill
├── docs/             # Research and design spec
└── .claude-plugin/   # Plugin metadata
```

## Development Status

- [x] Phase 1: Router + DSL Expert + Core Nodes + Templates
- [x] Phase 2: All workflow patterns (8) + logic/data/advanced nodes
- [x] Phase 3: Debugger + import/export + plugin maker
- [ ] Phase 4: Evaluations + polish + more templates
