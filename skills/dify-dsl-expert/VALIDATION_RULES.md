# DSL Validation Rules

## Structural Validation

### Level 1: YAML Syntax
- File must parse as valid YAML
- No duplicate keys at the same level
- Proper indentation (2 spaces recommended)

### Level 2: Required Fields
```
version         → string, must be "0.6.0"
kind            → string, must be "app"
app.name        → non-empty string
app.mode        → one of: completion|workflow|chat|advanced-chat|agent-chat
app.icon        → non-empty string
app.icon_background → hex color string (e.g. "#FFEAD5")
```

### Level 3: Mode-Content Consistency
```
IF mode IN (workflow, advanced-chat):
  workflow section MUST exist
  workflow.graph.nodes MUST be non-empty array
  workflow.graph.edges MUST be array (can be empty for single-node)
  
IF mode IN (chat, completion, agent-chat):
  model_config section MUST exist
```

### Level 4: Graph Structure
```
EXACTLY ONE root node (start, trigger-webhook, trigger-schedule, trigger-plugin, datasource)
ALL non-root nodes MUST have at least one incoming edge
NO edges referencing non-existent nodes
NO duplicate node IDs
NO duplicate edge IDs
Terminal node type matches mode:
  workflow → end node required
  advanced-chat → answer node required
```

### Level 5: Variable References
```
FOR EACH variable selector {{#node_id.field#}} or [node_id, field]:
  node_id MUST exist in graph
  node_id MUST be upstream (reachable before current node)
  field MUST be a valid output of that node type
```

### Level 6: Node-Specific Validation

#### LLM Node
- `model.provider` must be non-empty
- `model.name` must be non-empty
- `model.mode` should be "chat" or "completion"
- `prompt_template` must be non-empty array (chat mode) or non-empty object

#### Code Node
- `code_language` must be "python3" or "javascript"
- `code` must be non-empty string
- `outputs` must define at least one output variable

#### If-Else Node
- `cases` must have at least one case
- Each case must have `case_id` and `conditions`
- Edges from if-else must use case_id or "false" as sourceHandle

#### Knowledge Retrieval Node
- `dataset_ids` must be non-empty array
- `retrieval_mode` must be "single" or "multiple"
- `query_variable_selector` must reference valid upstream output

#### HTTP Request Node
- `method` must be valid HTTP method
- `url` must be non-empty

#### Iteration Node
- `iterator_selector` must reference a list/array output
- Must contain internal nodes (iteration-start + at least one processing node)

## Edge Case Rules

1. **Parallel branches**: Multiple edges FROM same node are allowed (branching)
2. **Converging branches**: Multiple edges TO same node are allowed (merging)
3. **Self-loops**: NOT allowed (edge source == edge target)
4. **Cycles**: NOT allowed except within iteration/loop containers
5. **Container nodes** (iteration, loop): Have their own internal sub-graph
