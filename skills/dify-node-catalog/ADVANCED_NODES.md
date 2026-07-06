# Advanced Nodes

Nodes for AI agents, structured extraction, classification, and human-in-the-loop.

---

## Agent Node (`agent`)

Invokes an autonomous agent with tools (ReAct, Function Calling strategies).

### Config
```yaml
data:
  type: agent
  title: Agent
  agent_strategy_provider_name: "langgenius"
  agent_strategy_name: "function_calling"
  agent_strategy_label: "Function Calling"
  agent_parameters:
    model:
      type: constant
      value:
        provider: openai
        name: gpt-4o
        mode: chat
        completion_params:
          temperature: 0.7
    tools:
      type: constant
      value:
        - provider_id: google
          provider_type: builtin
          provider_name: google
          tool_name: google_search
          tool_label: Google Search
          tool_configurations: {}
        - provider_id: wikipedia
          provider_type: builtin
          provider_name: wikipedia
          tool_name: wikipedia_search
          tool_label: Wikipedia
          tool_configurations: {}
    query:
      type: variable
      value:
        - sys
        - query
    max_iterations:
      type: constant
      value: 5
  memory:
    enabled: true
    window:
      enabled: true
      size: 10
```

### Agent Strategies
| Strategy | Description |
|----------|-------------|
| `function_calling` | Uses model's native function calling (recommended) |
| `react` | ReAct (Reason + Act) loop |

### Outputs
| Output | Type | Description |
|--------|------|-------------|
| `text` | string | Agent's final response |

### Gotchas
- Agent tools must be installed/configured in your Dify instance
- `credential_id` is stripped on export
- Memory only works in chatflow (advanced-chat) mode
- `max_iterations` prevents runaway agent loops
- Agent nodes are expensive — use them only when tools are genuinely needed

---

## Parameter Extractor Node (`parameter-extractor`)

Uses an LLM to extract structured parameters from natural language text.

### Config
```yaml
data:
  type: parameter-extractor
  title: Extract Parameters
  model:
    provider: openai
    name: gpt-4o-mini
    mode: chat
    completion_params:
      temperature: 0.0
  query:
    - start
    - query
  parameters:
    - name: city
      type: string
      description: "The city name"
      required: true
    - name: date
      type: string
      description: "The date in YYYY-MM-DD format"
      required: false
    - name: guests
      type: number
      description: "Number of guests"
      required: false
      options: []
  instruction: "Extract booking parameters from the user's message."
  reasoning_mode: function_call   # function_call or prompt
  memory:
    enabled: false
  vision:
    enabled: false
```

### Parameter Types
`string`, `number`, `bool`, `select` (requires `options` array)

### Outputs
- Each parameter `name` becomes an output field
- Example: `["parameter_extractor", "city"]`, `["parameter_extractor", "date"]`

### Gotchas
- `reasoning_mode: function_call` requires a model that supports function calling
- `reasoning_mode: prompt` works with any model but is less reliable
- Set `temperature: 0.0` for consistent extraction
- Good `description` fields dramatically improve extraction quality
- Required parameters may still be null if not found in text

---

## Question Classifier Node (`question-classifier`)

Uses an LLM to classify user queries into predefined categories.

### Config
```yaml
data:
  type: question-classifier
  title: Question Classifier
  query_variable_selector:
    - sys
    - query
  model:
    provider: openai
    name: gpt-4o-mini
    mode: chat
    completion_params:
      temperature: 0.0
  classes:
    - id: "class_1"
      name: "Technical Support"
    - id: "class_2"
      name: "Billing Question"
    - id: "class_3"
      name: "General Inquiry"
  instruction: "Classify the user's question into one of the categories."
  memory:
    enabled: false
  vision:
    enabled: false
```

### Edge Handles
Each class `id` becomes a `sourceHandle` on outgoing edges:
```yaml
edges:
  - source: "classifier"
    sourceHandle: "class_1"     # Routes to tech support branch
    target: "tech_support_llm"
  - source: "classifier"
    sourceHandle: "class_2"     # Routes to billing branch
    target: "billing_llm"
  - source: "classifier"
    sourceHandle: "class_3"     # Routes to general branch
    target: "general_llm"
```

### Outputs
- No direct outputs referenced by downstream nodes
- Routing is done via edges with class ID handles

### Gotchas
- Each class needs a unique `id` (used as edge sourceHandle)
- `instruction` helps the model understand the classification context
- Works best with clear, non-overlapping class definitions
- Use `temperature: 0.0` for consistent classification

---

## Human Input Node (`human-input`)

Pauses workflow execution to wait for human review, approval, or form input.

### Config
```yaml
data:
  type: human-input
  title: Human Review
  type: review                  # review|fill_form|approve
  review_config:
    variable_selector:
      - llm
      - text
    description: "Please review the generated response before sending."
  timeout_config:
    enabled: true
    timeout: 3600               # Seconds to wait before timeout
    default_action: reject      # approve|reject on timeout
```

### Human Input Types
| Type | Use Case |
|------|----------|
| `review` | Show output and let human edit/approve |
| `fill_form` | Present form for human to fill |
| `approve` | Simple approve/reject gate |

### Gotchas
- Workflow pauses at this node — not suitable for real-time chatbots
- Requires the Dify UI or API polling to provide human input
- `timeout_config` prevents workflows from hanging indefinitely

---

## App Node (`app`)

Calls another Dify application as a sub-workflow.

### Config
```yaml
data:
  type: app
  title: Call Sub-App
  provider_id: "app"
  app_id: "APP_UUID_PLACEHOLDER"
  inputs_parameters:
    query:
      type: variable
      value:
        - start
        - query
  query: null                   # Override query for chat apps
  files: null
  timeout:
    connect: 10
    read: 300
    write: 10
```

### Outputs
| Output | Type | Description |
|--------|------|-------------|
| `text` | string | App's response text |

### Gotchas
- `app_id` must be a valid app UUID in the same workspace
- The target app must be published (not just draft)
- Input parameters must match the target app's expected inputs
- Long-running sub-apps may timeout — adjust timeout accordingly

---

## Variable Aggregator Node (`variable-aggregator`)

Merges variables from multiple parallel branches into one output.

### Config
```yaml
data:
  type: variable-aggregator
  title: Merge Results
  output_type: array
  variables:
    - - branch_a_llm
      - text
    - - branch_b_llm
      - text
    - - branch_c_llm
      - text
  advanced_settings:
    group_enabled: false
```

### Outputs
| Output | Type | Description |
|--------|------|-------------|
| `output` | string/array | Merged result |

### Output Types
| Type | Behavior |
|------|----------|
| `string` | Concatenates all values |
| `array` | Collects into array |
| `object` | First non-null value |

### Gotchas
- Essential after parallel branches that need to converge
- `variables` is an array of arrays (each inner array is a selector)
- Order in `variables` determines order in output
- Null/empty values from unexecuted branches are skipped
