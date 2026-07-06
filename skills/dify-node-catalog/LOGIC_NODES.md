# Logic Nodes

Nodes for control flow, data transformation, and code execution.

---

## If-Else Node (`if-else`)

Conditional branching based on variable comparisons.

### Minimal Config
```yaml
data:
  type: if-else
  title: IF/ELSE
  cases:
    - case_id: "true-case"
      logical_operator: and
      conditions:
        - variable_selector:
            - start
            - query
          comparison_operator: contains
          value: "hello"
```

### Comparison Operators
| Operator | Description |
|----------|-------------|
| `contains` | String contains value |
| `not contains` | String does not contain |
| `start with` | String starts with |
| `end with` | String ends with |
| `is` | Exact match |
| `is not` | Not exact match |
| `empty` | Is empty/null |
| `not empty` | Is not empty/null |
| `=` | Numeric equal |
| `≠` | Numeric not equal |
| `>` | Greater than |
| `<` | Less than |
| `≥` | Greater or equal |
| `≤` | Less or equal |

### Edge Handles
- True branch: `sourceHandle` = `case_id` value
- Else branch: `sourceHandle` = `"false"`

### Outputs
- Pass-through only — no new outputs. Downstream nodes reference upstream nodes.

### Gotchas
- Multiple cases create multiple true branches (evaluated in order, first match wins)
- Each case needs its own edge with `sourceHandle` matching `case_id`
- The else branch edge uses `sourceHandle: "false"`

---

## Code Node (`code`)

Execute custom Python3 or JavaScript code.

### Minimal Config
```yaml
data:
  type: code
  title: Code
  variables:
    - variable: input_text
      value_selector:
        - start
        - query
  code_language: python3
  code: |
    def main(input_text: str) -> dict:
        return {"result": input_text.upper()}
  outputs:
    result:
      type: string
```

### Full Config
```yaml
data:
  type: code
  title: Code
  desc: ""
  variables:                   # Input variables
    - variable: input_text     # Local var name in code
      value_selector:          # Source: [node_id, field]
        - start
        - query
    - variable: context
      value_selector:
        - knowledge
        - result
  code_language: python3       # python3 or javascript
  code: |
    def main(input_text: str, context: list) -> dict:
        # Process inputs
        result = f"Processed: {input_text}"
        count = len(context)
        return {
            "result": result,
            "count": count
        }
  outputs:                     # Must match return dict keys
    result:
      type: string
    count:
      type: number
```

### Output Types
`string`, `number`, `object`, `array[string]`, `array[number]`, `array[object]`

### Python3 Rules
- Must define `def main(...) -> dict:` function
- Parameters match `variables` list names
- Must return a dict matching `outputs` keys
- Available: json, math, re, datetime, random, hashlib, hmac, base64, itertools

### JavaScript Rules
- Must define `function main({var1, var2}) { return {...} }`
- Destructured params from variables list
- Must return object matching outputs keys

### Gotchas
- Return type MUST be a dict/object
- Output keys MUST match defined `outputs`
- Limited stdlib — no network access, no file system
- Max execution time: 10 seconds default

---

## Template Transform Node (`template-transform`)

Transform data using Jinja2 templates.

### Minimal Config
```yaml
data:
  type: template-transform
  title: Template
  variables:
    - variable: name
      value_selector:
        - start
        - name
  template: "Hello, {{ name }}!"
```

### Outputs
| Output | Type |
|--------|------|
| `output` | string |

### Gotchas
- Uses Jinja2 syntax (`{{ var }}` not `{{#node.field#}}`)
- Variables are already resolved before template — use their local names
- Good for string formatting, bad for complex logic (use code node instead)

---

## Iteration Node (`iteration`)

Iterate over a list, executing a sub-graph for each item.

### Config
```yaml
data:
  type: iteration
  title: Iteration
  iterator_selector:           # Must reference a list/array
    - code_node
    - items_list
  output_selector:             # Which inner node output to collect
    - inner_llm
    - text
  is_parallel: false           # Process items in parallel
  parallel_nums: 10            # Max parallel workers
  error_handle_mode: CONTINUE_ON_ERROR  # TERMINATED|CONTINUE_ON_ERROR|REMOVE_ABNORMAL_OUTPUT
  flatten_output: true
```

### Internal Structure
The iteration contains its own sub-graph:
```yaml
# Inside the iteration, you need:
- iteration-start node (entry point, provides current item)
- Processing nodes (llm, code, etc.)
# No explicit end needed — output_selector defines what's collected
```

### Outputs
| Output | Type |
|--------|------|
| `output` | array — collected results from each iteration |

### Gotchas
- `iterator_selector` MUST point to an array/list output
- Inner nodes reference current item via the iteration-start node
- `output_selector` points to the inner node whose output gets collected
- Parallel mode can be faster but uses more resources

---

## Loop Node (`loop`)

Repeat a sub-graph up to N times or until break conditions met.

### Config
```yaml
data:
  type: loop
  title: Loop
  loop_count: 10               # Maximum iterations
  break_conditions:
    - variable_selector:
        - inner_code
        - done
      comparison_operator: is
      value: "true"
  logical_operator: or         # and|or for multiple conditions
  loop_variables:              # Variables that persist across iterations
    - label: counter
      var_type: variable
      value_type: number
      value: 0
```

### Gotchas
- Always set a reasonable `loop_count` to prevent infinite loops
- Break conditions are checked after each iteration
- Loop variables persist and can be modified each iteration

---

## List Operator Node (`list-operator`)

Filter, sort, limit, and extract from arrays.

### Config
```yaml
data:
  type: list-operator
  title: List Filter
  variable:                    # Input list
    - code_node
    - items
  filter_by:
    enabled: true
    conditions:
      - key: "$.status"
        comparison_operator: is
        value: "active"
  order_by:
    enabled: true
    key: "$.created_at"
    value: desc                # asc|desc
  limit:
    enabled: true
    size: 10
  extract_by:
    enabled: false
    serial: 0                  # Index to extract
```

### Outputs
| Output | Type |
|--------|------|
| `result` | array (filtered/sorted/limited) |
| `first_record` | object (first item) |
| `last_record` | object (last item) |

---

## Variable Assigner Node (`assigner`)

Modify variable values with operations.

### Config
```yaml
data:
  type: assigner
  title: Set Variable
  version: "2"
  items:
    - variable_selector:
        - conversation_var_name
      input_type: constant     # constant|variable
      operation: set           # set|append|clear|add|subtract
      value: "new value"
```

### Operations
| Operation | Types | Description |
|-----------|-------|-------------|
| `set` | all | Replace value |
| `append` | string, array | Add to end |
| `clear` | all | Reset to empty |
| `add` | number | Add numeric value |
| `subtract` | number | Subtract numeric value |
