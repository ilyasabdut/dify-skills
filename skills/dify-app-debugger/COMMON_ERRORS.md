# Common Errors

Catalog of frequent Dify DSL errors with symptoms, causes, and fixes.

---

## Import Errors

### E001: "Invalid YAML format"
**Symptom**: Import fails immediately
**Cause**: YAML syntax error (bad indent, unquoted special chars, tabs)
**Fix**: Run YAML through a validator. Common culprits:
- Strings containing `:` or `#` need quotes
- Inconsistent indentation (use 2 spaces consistently)
- Tab characters (replace with spaces)

### E002: "Invalid app mode"
**Symptom**: Import rejects the DSL
**Cause**: `app.mode` is not a valid value
**Fix**: Must be one of: `completion`, `workflow`, `chat`, `advanced-chat`, `agent-chat`

### E003: "Version not compatible"
**Symptom**: Import shows "pending" status
**Cause**: DSL version is newer than the Dify instance supports
**Fix**: Confirm import, or downgrade version to `"0.6.0"`

---

## Graph Errors

### E010: "No start node found"
**Symptom**: Workflow fails to load/run
**Cause**: Missing a node with `data.type: start`
**Fix**: Add a start node to the graph

### E011: "Multiple start nodes"
**Symptom**: Workflow behavior is unpredictable
**Cause**: More than one root node in the graph
**Fix**: Keep exactly one start/trigger node

### E012: "Orphan node detected"
**Symptom**: Node never executes
**Cause**: Node has no incoming edges (not reachable from start)
**Fix**: Add an edge connecting it to the graph

### E013: "Unreachable end/answer node"
**Symptom**: Workflow produces no output
**Cause**: No path from start to terminal node
**Fix**: Ensure edges create a connected path to end/answer

---

## Variable Reference Errors

### E020: "Variable not found: {{#nonexistent.text#}}"
**Symptom**: Runtime error during execution
**Cause**: Node ID in selector doesn't exist in graph
**Fix**: Check spelling of node ID, ensure node exists

### E021: "Cannot reference downstream node"
**Symptom**: Empty variable value
**Cause**: Referencing a node that hasn't executed yet
**Fix**: Only reference nodes upstream (earlier) in the flow

### E022: "Invalid output field"
**Symptom**: Null/undefined output
**Cause**: Using wrong output field name for node type
**Fix**: Check correct outputs:
- LLM → `text`, `usage`
- Code → user-defined output names
- HTTP → `body`, `status_code`, `headers`
- Knowledge → `result`

### E023: "Type mismatch in selector"
**Symptom**: Node receives wrong data type
**Cause**: Passing array where string expected, etc.
**Fix**: Use a code node to transform types between incompatible nodes

---

## Node Configuration Errors

### E030: "LLM model not found"
**Symptom**: LLM node fails at runtime
**Cause**: Model provider/name doesn't match instance config
**Fix**: Check available models in your Dify instance settings

### E031: "Code node timeout"
**Symptom**: Code node fails after 10s
**Cause**: Infinite loop or very heavy computation
**Fix**: Optimize code, reduce data size, or simplify logic

### E032: "Code node output mismatch"
**Symptom**: Downstream nodes get null
**Cause**: Code returns keys that don't match `outputs` definition
**Fix**: Ensure `return` dict keys exactly match `outputs` keys

### E033: "Knowledge base not found"
**Symptom**: Knowledge retrieval fails
**Cause**: `dataset_ids` contains UUIDs that don't exist
**Fix**: Replace with valid dataset IDs from your instance

### E034: "HTTP timeout"
**Symptom**: HTTP request node fails
**Cause**: External API too slow or unreachable
**Fix**: Increase `timeout.read`, check URL accessibility

---

## Mode Mismatch Errors

### E040: "Using end node in chatflow"
**Symptom**: Import may succeed but behavior is wrong
**Cause**: `advanced-chat` mode should use `answer` node, not `end`
**Fix**: Replace `end` with `answer` node

### E041: "Using answer node in workflow"
**Symptom**: Answer node ignored
**Cause**: `workflow` mode should use `end` node, not `answer`
**Fix**: Replace `answer` with `end` node

### E042: "Memory enabled in workflow mode"
**Symptom**: Memory config ignored
**Cause**: LLM memory only works in `advanced-chat` mode
**Fix**: Either switch to `advanced-chat` or disable memory

### E043: "sys.query in workflow mode"
**Symptom**: Variable is empty/null
**Cause**: `sys.query` only exists in chatflow mode
**Fix**: Use start node variables instead: `{{#start.query#}}`

---

## Edge/Connection Errors

### E050: "Missing sourceHandle on if-else edge"
**Symptom**: Branch routing doesn't work
**Cause**: Edge from if-else needs `sourceHandle` matching case_id or "false"
**Fix**: Set `sourceHandle` to the correct case_id or `"false"` for else branch

### E051: "Missing sourceHandle on classifier edge"
**Symptom**: Classification routing fails
**Cause**: Edge from question-classifier needs `sourceHandle` matching class.id
**Fix**: Set `sourceHandle` to the correct class ID

### E052: "Edge references non-existent node"
**Symptom**: Import fails or graph is broken
**Cause**: Edge `source` or `target` doesn't match any node ID
**Fix**: Correct the node ID in the edge, or add the missing node
