---
name: using-dify-skills
description: "Use when building Dify apps, generating workflow DSL YAML, debugging broken imports, creating plugins, or asking about node configuration. Always loaded as the entry point for all Dify-related tasks."
---

# Dify Skills Router

You have access to a set of specialist skills for generating and debugging Dify applications. This router tells you WHICH skill to invoke based on user intent.

## Protocol

1. **Understand** — What does the user want? (build, debug, configure, deploy)
2. **Route** — Invoke the right specialist skill
3. **Generate** — Produce valid DSL YAML following the specialist's guidance
4. **Validate** — Check structure before presenting output
5. **Deliver** — Present the YAML or save to file

## Routing Table

| User Intent | Invoke Skill |
|------------|--------------|
| "Build/create a workflow/chatbot/app" | `dify-workflow-patterns` |
| "Configure/set up a [node type]" | `dify-node-catalog` |
| "Why isn't my app working?" / "Debug this DSL" | `dify-app-debugger` |
| "How do I pass data between nodes?" / "Variable reference" | `dify-variable-system` |
| "Import/export/deploy this app" | `dify-import-export` |
| "What's the DSL format?" / "Validate this YAML" | `dify-dsl-expert` |
| "Create/build a plugin" / "Custom tool/model provider" | `dify-plugin-maker` |

## Non-Negotiable Rules

1. **Every generated DSL MUST include**:
   ```yaml
   version: "0.6.0"
   kind: "app"
   ```

2. **Mode determines terminal node**:
   - `workflow` mode → uses `end` node (defines output variables)
   - `advanced-chat` mode → uses `answer` node (streams text to user)
   - `chat`/`completion`/`agent-chat` → uses `model_config` section, not workflow

3. **Every workflow MUST have exactly one root node** (start or trigger-*)

4. **All node IDs must be unique** — use descriptive slugs (e.g., `llm_1`, `knowledge_retrieval`)

5. **All edges must reference existing node IDs** — no dangling references

6. **Variable selectors must reference valid upstream node outputs**:
   - Template syntax: `{{#node_id.output_field#}}`
   - Array syntax: `["node_id", "output_field"]`

7. **ALWAYS validate before presenting** — run through the DSL Expert validation checklist mentally

## Quick Reference: App Modes

| Mode | Use Case | Terminal Node | Has Workflow Section |
|------|----------|--------------|---------------------|
| `workflow` | Single-shot tasks | `end` | Yes |
| `advanced-chat` | Conversational with workflow | `answer` | Yes |
| `chat` | Simple chatbot | N/A | No (uses model_config) |
| `completion` | Text generation | N/A | No (uses model_config) |
| `agent-chat` | Agent with tools | N/A | No (uses model_config) |

## Quick Reference: Common Node Outputs

| Node Type | Key Outputs |
|-----------|-------------|
| `start` | User-defined variable names |
| `llm` | `text`, `usage` |
| `code` | User-defined in `outputs` dict |
| `knowledge-retrieval` | `result` |
| `http-request` | `body`, `status_code`, `headers` |
| `template-transform` | `output` |
| `parameter-extractor` | Extracted parameter names |
| `document-extractor` | `text` |
| `iteration` | Collected from `output_selector` |

## When Multiple Skills Apply

Invoke them in this order:
1. `dify-workflow-patterns` (select architecture)
2. `dify-node-catalog` (configure each node correctly)
3. `dify-variable-system` (wire nodes together)
4. `dify-dsl-expert` (validate final output)
5. `dify-plugin-maker` (when building custom plugins, invoked standalone)
