# Dify Skills

[![GitHub stars](https://img.shields.io/github/stars/ilyasabdut/dify-skills?style=social)](https://github.com/ilyasabdut/dify-skills)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Dify 1.30+](https://img.shields.io/badge/Dify-1.30%2B-blue.svg)](https://dify.ai)
[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-purple.svg)](https://docs.anthropic.com/en/docs/claude-code)

> **Expert Claude Code skills for building flawless Dify workflows and plugins.**

Tell Claude Code what you want — it generates valid, import-ready DSL YAML or scaffolds a complete plugin project. 8 specialist skills, 40 node types, 8 workflow patterns.

Inspired by [n8n-skills](https://github.com/czlonkowski/n8n-skills) and [superpowers](https://github.com/obra/superpowers).

---

## 🎯 What is this?

Building Dify apps by hand means learning DSL YAML format, node configuration schemas, variable selector syntax, and plugin SDK patterns. These skills teach Claude Code all of that so you don't have to.

- ✅ Generate complete, import-ready Dify apps from natural language
- ✅ All 40 workflow node types with correct configuration
- ✅ 8 proven architectural patterns (RAG, agents, pipelines, routing)
- ✅ Debug broken DSL files with systematic error identification
- ✅ Scaffold custom Dify plugins (tools, models, agent strategies, triggers)
- ✅ Validated against `claude plugin validate` — clean install

---

## 🚀 Installation

### Claude Code (plugin directory)
```bash
claude --plugin-dir /path/to/dify-skills
```

### Claude Code (settings.json)
Add to your project's `.claude/settings.json`:
```json
{
  "plugins": ["/path/to/dify-skills"]
}
```

### From GitHub
```bash
git clone https://github.com/ilyasabdut/dify-skills.git
claude --plugin-dir ./dify-skills
```

---

## 📚 The 8 Skills

### 1. using-dify-skills (Router)

The always-loaded entry point. Routes your intent to the right specialist skill.

**Activates when:** Any Dify-related request — building apps, debugging, creating plugins.

---

### 2. dify-dsl-expert

Knows the exact DSL YAML structure, required fields, version handling, and validation rules.

**Activates when:** Generating DSL YAML, validating structure before import, fixing format errors, mode mismatches.

**Key features:**
- Complete field reference (required vs optional)
- Structural validation checklist (14 checks)
- Common mistakes table with fixes
- Version compatibility handling

---

### 3. dify-node-catalog

Configuration reference for all 40 workflow node types — minimal config, full config, outputs, and gotchas.

**Activates when:** Configuring a specific node, looking up required fields, checking outputs, troubleshooting node errors.

**Key features:**
- 5 reference files: Core, Logic, Data, Advanced, SQL nodes
- Each node: minimal config, full config, outputs table, gotchas
- Copy-paste ready YAML snippets

---

### 4. dify-workflow-patterns

8 proven architectural patterns with complete DSL templates.

**Activates when:** Building a new app from scratch, choosing workflow vs chatflow, needing a template for RAG/agents/pipelines.

**Key features:**
- Complete import-ready DSL per pattern
- Customization points table
- Variations for common modifications
- Architecture diagrams

---

### 5. dify-variable-system

How to pass data between nodes — selector syntax, system variables, outputs per node type.

**Activates when:** Wiring nodes together, debugging "variable not found" errors, passing data between steps.

**Key features:**
- Two syntax forms (`{{#node.field#}}` and `[node, field]`)
- System variables reference (sys.query, sys.files)
- Output fields per node type table
- Debugging guide for empty/null values

---

### 6. dify-app-debugger

Systematic debugging protocol for broken DSL files with 50+ cataloged errors.

**Activates when:** App fails to import, nodes don't execute, outputs are empty, behavior doesn't match expectations.

**Key features:**
- 6-step debug protocol
- Error catalog: import errors, graph errors, variable errors, node config errors, mode mismatches
- Each error: symptom → cause → fix

---

### 7. dify-import-export

Deploy generated apps to a running Dify instance via API.

**Activates when:** Deploying DSL YAML, exporting apps, handling pending imports, replacing placeholder IDs.

**Key features:**
- Import/export API endpoints
- Response states and handling
- Deployment workflow checklist
- Console token guidance

---

### 8. dify-plugin-maker

Create custom Dify plugins from scratch — tools, models, agent strategies, triggers.

**Activates when:** Building a custom tool, integrating a model provider, implementing an agent strategy, setting up triggers.

**Key features:**
- Complete file structure per plugin type
- manifest.yaml format with all fields
- Tool implementation (Python SDK patterns)
- Model provider implementation
- Agent strategy with tool/LLM invocation
- Trigger plugin guide
- Remote debugging setup
- SDK quick reference

---

## 💡 Usage Examples

```
"Build me a RAG chatbot that searches my product docs"
→ dify-workflow-patterns → dify-node-catalog → dify-dsl-expert
→ Complete DSL YAML ready to import

"Create a workflow that fetches data from an API and summarizes each item"
→ dify-workflow-patterns (data_processing_pipeline)
→ Start → HTTP → Iteration[LLM] → End

"This DSL fails on import with 'orphan node' error"
→ dify-app-debugger → identifies disconnected node → suggests edge fix

"Create a Dify tool plugin that integrates with Slack"
→ dify-plugin-maker → scaffolds manifest + provider + tool implementation

"How do I reference the LLM output in my answer node?"
→ dify-variable-system → {{#llm_node_id.text#}}
```

---

## 📊 What's Included

| Component | Count |
|-----------|-------|
| Skills | 8 |
| Workflow patterns | 8 |
| Node types documented | 40 |
| DSL templates | 5 |
| Evaluation scenarios | 14 |
| Plugin type guides | 4 |
| Error catalog entries | 50+ |

---

## 🏗️ Workflow Patterns

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

---

## 🔌 Plugin Maker

| Plugin Type | Use Case |
|-------------|----------|
| **Tool** | API integrations, utilities, custom functions |
| **Model** | LLM/embedding/rerank provider wrappers |
| **Agent Strategy** | Custom reasoning loops (ReAct, FC, CoT) |
| **Trigger** | Webhook/schedule/event-based workflow starts |

---

## 📁 Project Structure

```
dify-skills/
├── .claude-plugin/           # Plugin metadata (validated ✔)
├── skills/                   # 8 specialist skills
│   ├── using-dify-skills/    # Router
│   ├── dify-dsl-expert/      # DSL format + validation
│   ├── dify-node-catalog/    # 40 nodes (5 reference files)
│   ├── dify-workflow-patterns/ # 8 patterns
│   ├── dify-variable-system/ # Selector syntax
│   ├── dify-app-debugger/    # Debug protocol + errors
│   ├── dify-import-export/   # API deployment
│   └── dify-plugin-maker/    # Plugin dev (4 files)
├── templates/                # Import-ready DSL YAML (5)
├── hooks/                    # Session-start hook
├── evaluations/              # Test scenarios (4 suites)
└── docs/                     # Research + design spec
```

---

## 🤝 Contributing

1. Fork the repo
2. Add/improve skills in `skills/`
3. Add evaluation scenarios in `evaluations/`
4. Validate: `claude plugin validate .`
5. Submit a PR

---

## 🔗 Related Projects

- [Dify](https://github.com/langgenius/dify) — The LLM app platform
- [dify-official-plugins](https://github.com/langgenius/dify-official-plugins) — Official plugin collection
- [n8n-skills](https://github.com/czlonkowski/n8n-skills) — Similar approach for n8n
- [superpowers](https://github.com/obra/superpowers) — Claude Code development methodology

---

## 📝 License

[MIT](LICENSE)
