# Core Nodes

The 4 nodes used in virtually every Dify workflow.

---

## Start Node (`start`)

Entry point for every workflow/chatflow. Defines user input variables.

### Minimal Config
```yaml
data:
  type: start
  title: Start
  variables: []
```

### Full Config
```yaml
data:
  type: start
  title: Start
  desc: ""
  variables:
    - variable: query          # Variable name (used as reference)
      label: Query             # Display label
      type: text-input         # Input type (see below)
      required: true
      max_length: 2000         # null for no limit
      options: []              # For select type only
      default: ""              # Default value
```

### Variable Types
| Type | Description |
|------|-------------|
| `text-input` | Single-line text |
| `paragraph` | Multi-line text |
| `select` | Dropdown (requires `options`) |
| `number` | Numeric input |
| `file` | File upload |
| `file-list` | Multiple file uploads |

### Outputs
- Each variable name defined in `variables` becomes an output
- Reference: `{{#start.variable_name#}}` or `["start", "variable_name"]`

### Gotchas
- In `advanced-chat` mode, the user's message is available as `sys.query` — you don't need to define a `query` variable in start (start variables become form fields)
- For simple chatbots, leave `variables: []` empty

---

## End Node (`end`)

Terminal node for `workflow` mode. Defines what the workflow returns.

### Minimal Config
```yaml
data:
  type: end
  title: End
  outputs:
    - variable: result
      value_type: string
      value_selector:
        - llm_node_id
        - text
```

### Full Config
```yaml
data:
  type: end
  title: End
  desc: ""
  outputs:
    - variable: result         # Output variable name
      value_type: string       # string|number|object|array
      value_selector:          # Source: [node_id, output_field]
        - llm
        - text
    - variable: metadata
      value_type: object
      value_selector:
        - code_node
        - parsed_data
```

### Value Types
| Type | Description |
|------|-------------|
| `string` | Text output |
| `number` | Numeric output |
| `object` | JSON object |
| `array` | JSON array |
| `file` | File reference |

### Outputs
- End node has no downstream outputs (it's terminal)
- The defined `outputs` become the workflow's return values

### Gotchas
- Only used in `workflow` mode — chatflows use `answer` instead
- `value_selector` must point to a node that executes BEFORE end node
- Multiple outputs are allowed (workflow returns all of them)

---

## Answer Node (`answer`)

Terminal node for `advanced-chat` mode. Streams response text to the user.

### Minimal Config
```yaml
data:
  type: answer
  title: Answer
  answer: "{{#llm.text#}}"
```

### Full Config
```yaml
data:
  type: answer
  title: Answer
  desc: ""
  answer: |
    {{#llm.text#}}
    
    Sources: {{#knowledge.result#}}
```

### Template Syntax
- Use `{{#node_id.output_field#}}` to insert node outputs
- Plain text is passed through as-is
- Supports multi-line with `|` YAML syntax
- Can combine multiple node outputs in one template

### Outputs
- Answer node has no downstream outputs (it's terminal)
- The rendered template is streamed to the user

### Gotchas
- Only used in `advanced-chat` mode — workflows use `end` instead
- The answer is STREAMED — if referencing an LLM node, the text streams in real-time
- Multiple answer nodes in different branches are allowed (only the executed branch streams)

---

## LLM Node (`llm`)

Calls a Large Language Model for text generation.

### Minimal Config
```yaml
data:
  type: llm
  title: LLM
  model:
    provider: openai
    name: gpt-4o-mini
    mode: chat
    completion_params:
      temperature: 0.7
  prompt_template:
    - role: system
      text: "You are a helpful assistant."
    - role: user
      text: "{{#start.query#}}"
  memory:
    enabled: false
  context:
    enabled: false
  vision:
    enabled: false
```

### Full Config
```yaml
data:
  type: llm
  title: LLM
  desc: ""
  model:
    provider: openai           # Model provider ID
    name: gpt-4o-mini          # Model name
    mode: chat                 # chat or completion
    completion_params:
      temperature: 0.7        # 0.0 - 2.0
      top_p: 1.0              # 0.0 - 1.0
      max_tokens: 4096         # Max output tokens
      presence_penalty: 0.0
      frequency_penalty: 0.0
  prompt_template:             # Array of messages for chat mode
    - role: system
      text: "System prompt here"
    - role: user
      text: "{{#start.query#}}"
    - role: assistant
      text: ""                 # Optional: prefill
  memory:                      # Conversation memory (chatflow only)
    enabled: true
    window:
      enabled: true
      size: 10                 # Number of messages to retain
    query_prompt_template: "{{#sys.query#}}"
  context:                     # Knowledge context injection
    enabled: true
    variable_selector:
      - knowledge_node_id
      - result
  vision:                      # Image understanding
    enabled: false
    configs:
      variable_selector: []
      detail: high             # high, low, auto
  structured_output:           # JSON schema output
    enabled: false
    schema: {}                 # JSON Schema object
  retry_config:
    enabled: false
    max_retries: 3
    retry_interval: 1000
```

### Outputs
| Output | Type | Description |
|--------|------|-------------|
| `text` | string | Generated text |
| `usage` | object | Token usage stats |

### Common Providers
| Provider | Models |
|----------|--------|
| `openai` | gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo |
| `anthropic` | claude-3-5-sonnet, claude-3-opus, claude-3-haiku |
| `google` | gemini-pro, gemini-1.5-pro |
| `azure_openai` | (deployment names) |

### Gotchas
- `memory` only works in `advanced-chat` mode — ignored in workflows
- `context` injects knowledge retrieval results into the system prompt automatically
- `vision` requires a model that supports image input
- In `prompt_template`, use `{{#sys.query#}}` for the user's chat message (chatflows)
- In workflows, reference start variables: `{{#start.variable_name#}}`
- Provider/model must match what's configured in the Dify instance
