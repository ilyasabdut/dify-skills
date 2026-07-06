# Dify Skills

> Claude Code skills for generating [Dify](https://dify.ai) apps and plugins from natural language.

Tell Claude Code what you want — it generates valid, import-ready DSL YAML or scaffolds a complete plugin project.

Inspired by [n8n-skills](https://github.com/czlonkowski/n8n-skills) and [superpowers](https://github.com/obra/superpowers).

---

## Install

```bash
claude --plugin-dir /path/to/dify-skills
```

Or add to your project's `.claude/settings.json`:
```json
{
  "plugins": ["/path/to/dify-skills"]
}
```

---

## What It Does

```
You: "Build me a RAG chatbot that searches my product docs"

Claude: [invokes dify-workflow-patterns → dify-node-catalog → dify-dsl-expert]
        → Produces valid DSL YAML ready to import into Dify
```

```
You: "Create a Dify tool plugin that fetches weather data"

Claude: [invokes dify-plugin-maker]
        → Scaffolds manifest.yaml, provider, tool implementation
```

```
You: "This DSL fails on import — debug it"

Claude: [invokes dify-app-debugger]
        → Identifies broken variable selectors, missing edges, mode mismatches
```

---

## Skills

| Skill | Purpose |
|-------|---------|
| **using-dify-skills** | Router — always loaded, dispatches to specialists |
| **dify-dsl-expert** | DSL YAML format, validation rules, version handling |
| **dify-node-catalog** | All 40 node types with exact configuration schemas |
| **dify-workflow-patterns** | 8 proven workflow architectures with complete templates |
| **dify-variable-system** | How to wire nodes together (`{{#node.field#}}` syntax) |
| **dify-app-debugger** | Parse broken DSL, identify issues, suggest fixes |
| **dify-import-export** | Deploy via API, handle dependencies |
| **dify-plugin-maker** | Create tool/model/agent/trigger plugins from scratch |

---

## Workflow Patterns

| Pattern | Mode | Flow |
|---------|------|------|
| Simple Chatbot | `advanced-chat` | Start → LLM → Answer |
| RAG Chatbot | `advanced-chat` | Start → Knowledge → LLM → Answer |
| Text Generation | `workflow` | Start → LLM → End |
| Agent with Tools | `advanced-chat` | Start → Agent → Answer |
| Data Pipeline | `workflow` | Start → Code → Iteration[LLM] → End |
| API Orchestration | `workflow` | Start → HTTP → If-Else → End |
| Document Analysis | `workflow` | Start → DocExtractor → LLM → End |
| Conditional Routing | `advanced-chat` | Start → Classifier → [A/B/C] → Answer |

Each pattern includes a complete DSL YAML template you can import directly.

---

## Node Coverage

**40 node types** documented with minimal config, full config, outputs, and gotchas:

| Category | Nodes |
|----------|-------|
| Core | start, end, answer, llm |
| Logic | if-else, code, template-transform, iteration, loop, list-operator, assigner |
| Data | knowledge-retrieval, http-request, tool, datasource, document-extractor |
| Advanced | agent, parameter-extractor, question-classifier, human-input, app, variable-aggregator |
| SQL | vannaai-connector, vannaai-question, vannaai-training, sql-output-chart/table/summary |
| Cache | cache-retrieve, cache-store |
| Triggers | trigger-webhook, trigger-schedule, trigger-plugin |

---

## Plugin Maker

Generate complete Dify plugin projects:

| Plugin Type | What It Does |
|-------------|-------------|
| **Tool** | Custom tools for workflows/agents (API integrations, utilities) |
| **Model** | LLM/embedding/rerank providers |
| **Agent Strategy** | Custom reasoning loops (ReAct, Function Calling variants) |
| **Trigger** | Event-based workflow triggers (webhooks, schedules) |

Includes SDK reference, manifest format, and working code templates.

---

## Templates

Ready-to-import DSL files in `templates/`:

| File | Architecture |
|------|-------------|
| `simple-workflow.yml` | Start → LLM → End |
| `simple-chatbot.yml` | Start → LLM (memory) → Answer |
| `rag-chatbot.yml` | Start → Knowledge → LLM → Answer |
| `data-pipeline.yml` | Start → Code → Iteration[LLM] → End |
| `api-orchestration.yml` | Start → HTTP → Code → End |

Import via Dify console (Studio → Import DSL) or API:
```bash
curl -X POST http://your-dify/console/api/apps/imports \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mode": "yaml-content", "yaml_content": "'"$(cat templates/rag-chatbot.yml)"'"}'
```

---

## Project Structure

```
dify-skills/
├── .claude-plugin/           # Plugin metadata (validated)
│   ├── marketplace.json
│   └── plugin.json
├── skills/                   # 8 specialist skills
│   ├── using-dify-skills/    # Router (always loaded)
│   ├── dify-dsl-expert/      # DSL format + validation
│   ├── dify-node-catalog/    # Node configs (5 reference files)
│   ├── dify-workflow-patterns/ # 8 pattern files
│   ├── dify-variable-system/ # Selector syntax
│   ├── dify-app-debugger/    # Debug protocol + error catalog
│   ├── dify-import-export/   # API deployment
│   └── dify-plugin-maker/    # Plugin dev (4 reference files)
├── templates/                # Import-ready DSL YAML
├── hooks/                    # Session-start hook
├── evaluations/              # Test scenarios (4 suites)
├── docs/                     # Research + design spec
├── CLAUDE.md                 # Project instructions
├── LICENSE                   # MIT
└── README.md
```

---

## How It Works

This project follows the **structured knowledge injection** pattern:

1. **Router skill** loads at session start → knows all capabilities
2. **User describes intent** → router dispatches to specialist
3. **Specialist skill** provides expert knowledge (schemas, patterns, rules)
4. **LLM generates** valid output following the skill's guidance
5. **Validation rules** catch mistakes before output

No fine-tuning. No structured output schemas for generation. Just well-organized expert knowledge that gets injected at the right moment.

---

## Contributing

1. Fork the repo
2. Add/improve skills in `skills/`
3. Add evaluation scenarios in `evaluations/`
4. Validate: `claude plugin validate .`
5. Submit a PR

---

## License

MIT
