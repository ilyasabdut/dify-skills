---
name: dify-node-catalog
description: "Complete configuration reference for all Dify workflow node types. Use when configuring specific nodes, looking up required fields, or understanding node inputs/outputs."
---

# Dify Node Catalog

Reference for configuring workflow nodes correctly. Each node type has required fields, optional fields, and expected outputs.

## Node Categories

| Category | Description | Node Types |
|----------|-------------|------------|
| **ROOT** | Workflow entry points | start, datasource, trigger-webhook, trigger-schedule, trigger-plugin |
| **EXECUTABLE** | Processing nodes | llm, code, http-request, tool, knowledge-retrieval, template-transform, etc. |
| **RESPONSE** | Output to user | end, answer |
| **BRANCH** | Conditional routing | if-else, question-classifier |
| **CONTAINER** | Sub-graph managers | iteration, loop |
| **VIRTUAL** | Internal boundary markers | iteration-start, loop-start, loop-end |

## How to Use This Catalog

1. Find the node type you need
2. Check the **Minimal Config** for required fields
3. Add optional fields as needed from **Full Config**
4. Note the **Outputs** section for downstream variable references
5. Review **Gotchas** to avoid common mistakes

## Reference Files

- `CORE_NODES.md` — start, end, answer, llm (used in every workflow)
- `LOGIC_NODES.md` — if-else, code, template-transform, iteration, loop, list-operator, assigner
- `DATA_NODES.md` — knowledge-retrieval, http-request, tool, datasource, document-extractor
- `ADVANCED_NODES.md` — agent, parameter-extractor, question-classifier, human-input, app

## Universal Node Fields

Every node object wraps its config in this structure:
```yaml
- id: "unique-id"
  type: custom
  position: {x: N, y: N}
  sourcePosition: right
  targetPosition: left
  data:
    type: "node-type-here"
    title: "Display Name"
    desc: ""                    # Optional description
    # ... type-specific fields below
```

## Position Guidelines

Space nodes 300px apart horizontally for readability:
- Start: x=80
- Second node: x=380
- Third node: x=680
- Fourth node: x=980

Vertical offset for branches: y±150 from main line.
