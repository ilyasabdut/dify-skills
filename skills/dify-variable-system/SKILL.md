---
name: dify-variable-system
description: "Dify variable reference and selector syntax. Use when wiring nodes together, referencing outputs from upstream nodes, or debugging broken variable references."
---

# Dify Variable System

How to pass data between nodes in Dify workflows.

## Two Syntax Forms

### 1. Template Syntax (in text fields)
```
{{#node_id.output_field#}}
```
Used in: answer node text, LLM prompt templates, HTTP request URLs/headers/body

### 2. Array Selector Syntax (in config fields)
```yaml
value_selector:
  - node_id
  - output_field
```
Used in: end node outputs, knowledge-retrieval query, code node variables, iteration iterator

## System Variables

Available in all chatflow (`advanced-chat`) nodes:

| Variable | Selector | Description |
|----------|----------|-------------|
| User query | `sys.query` / `["sys", "query"]` | Current user message |
| Files | `sys.files` / `["sys", "files"]` | Uploaded files array |
| Conversation ID | `sys.conversation_id` | Current conversation |
| User ID | `sys.user_id` | Current user |

**Important**: System variables are only available in `advanced-chat` mode. In `workflow` mode, use start node variables instead.

## Environment Variables

```
{{#env.VARIABLE_NAME#}}
```

Defined in `workflow.environment_variables`:
```yaml
environment_variables:
  - variable: API_KEY
    value_type: secret       # secret or string
    value: "sk-..."          # Encrypted on export
```

## Conversation Variables

Persist across messages in a conversation:
```
{{#conversation.var_name#}}
```

Defined in `workflow.conversation_variables`:
```yaml
conversation_variables:
  - id: "counter"
    name: "counter"
    value_type: number
    value: 0
```

Modified using the `assigner` node.

## Node Output Reference

### Common Outputs by Node Type

| Node Type | Output Field | Type | How to Reference |
|-----------|-------------|------|-----------------|
| `start` | (variable name) | varies | `{{#start.query#}}` |
| `llm` | `text` | string | `{{#llm_id.text#}}` |
| `llm` | `usage` | object | `["llm_id", "usage"]` |
| `code` | (output name) | varies | `{{#code_id.result#}}` |
| `knowledge-retrieval` | `result` | array | `{{#knowledge_id.result#}}` |
| `http-request` | `body` | string | `{{#http_id.body#}}` |
| `http-request` | `status_code` | number | `["http_id", "status_code"]` |
| `http-request` | `headers` | object | `["http_id", "headers"]` |
| `template-transform` | `output` | string | `{{#template_id.output#}}` |
| `parameter-extractor` | (param name) | varies | `{{#extractor_id.city#}}` |
| `document-extractor` | `text` | string | `{{#doc_id.text#}}` |
| `iteration` | `output` | array | `["iteration_id", "output"]` |
| `variable-aggregator` | `output` | varies | `["aggregator_id", "output"]` |

### Inside Iteration Nodes

Within an iteration, reference the current item:
```
{{#iteration_start_id.item#}}
```
Or with array selector:
```yaml
value_selector:
  - iter_start
  - item
```

The `item` is whatever type is in the iterated array.

### Inside Loop Nodes

Within a loop, reference loop variables:
```
{{#loop_start_id.loop_var_name#}}
```

## Rules

1. **Upstream only** — You can only reference outputs from nodes that execute BEFORE the current node in the graph flow
2. **Node ID must exist** — The `node_id` part must match an actual node's `id` field
3. **Output must exist** — The `output_field` must be a valid output of that node type
4. **Type awareness** — Know what type the output is (string, array, object, number) for downstream nodes that expect specific types
5. **No circular references** — A node cannot reference itself or downstream nodes

## Debugging Variable Issues

### Symptom: "Variable not found"
- Check: Does the node ID exist in the graph?
- Check: Is the referenced node upstream (reachable before current node)?
- Check: Is the output field name correct for that node type?

### Symptom: Empty/null value
- Check: Did the upstream node execute successfully?
- Check: For if-else branches, is the referenced node on an executed branch?
- Check: Is the output field spelled correctly?

### Symptom: Wrong type
- Check: LLM output is always string — parse JSON in a code node if needed
- Check: HTTP response `body` is string — parse in code node
- Check: Knowledge retrieval `result` is array — may need to stringify for LLM prompt
