---
name: dify-app-debugger
description: "Use when a Dify app fails to import, produces errors at runtime, nodes don't execute, outputs are empty, or behavior doesn't match expectations. Symptoms: 'orphan node', 'variable not found', blank responses, import rejected."
---

# Dify App Debugger

Systematic debugging of Dify DSL YAML files.

## Debug Protocol

When given a broken DSL or error report, follow these steps in order:

### Step 1: Parse YAML
- Does it parse as valid YAML?
- Common: bad indentation, missing quotes on strings with special chars, duplicate keys

### Step 2: Check Required Fields
```
✓ version: "0.6.0"
✓ kind: "app"
✓ app.name (non-empty)
✓ app.mode (valid value)
✓ app.icon (non-empty)
✓ app.icon_background (non-empty)
✓ workflow section (if mode is workflow/advanced-chat)
✓ model_config section (if mode is chat/completion/agent-chat)
```

### Step 3: Validate Graph Structure
```
✓ Exactly one root node (start or trigger-*)
✓ All nodes have unique IDs
✓ All nodes have type: custom and data.type
✓ All edges reference existing nodes (source and target)
✓ No orphan nodes (every non-root has incoming edge)
✓ Correct terminal node (end for workflow, answer for advanced-chat)
```

### Step 4: Check Variable References
```
For each {{#node_id.field#}} and [node_id, field]:
✓ node_id exists in graph
✓ node_id is upstream of current node
✓ field is valid output for that node type
```

### Step 5: Node-Specific Validation
```
LLM: model.provider + model.name present
Code: code_language + code + outputs defined
If-else: cases with conditions, edges match case_ids
Knowledge: dataset_ids non-empty, query_variable_selector set
HTTP: method + url present
Iteration: iterator_selector points to array, has internal nodes
```

### Step 6: Edge Handle Validation
```
If-else edges: sourceHandle = case_id or "false"
Classifier edges: sourceHandle = class.id
Error handling edges: sourceHandle = "fail-branch" or "success-branch"
Normal edges: sourceHandle = "source"
```

## Common Errors Reference

See `COMMON_ERRORS.md` for a detailed catalog.

## Fix Template

When you find an issue, report it as:

```
ISSUE: [what's wrong]
LOCATION: [node ID or line in YAML]
CAUSE: [why it's wrong]
FIX: [exact change needed]
```
