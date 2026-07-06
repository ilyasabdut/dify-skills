# Pattern: Text Generation

Single-shot text processing: summarize, translate, extract, rewrite.

## Architecture

```
Start (input text) → LLM → End (result)
```

## Mode: `workflow`

## When to Use
- Summarization
- Translation
- Data extraction
- Text rewriting/paraphrasing
- Any non-conversational text-in → text-out task

## Complete DSL

```yaml
version: "0.6.0"
kind: "app"
app:
  name: "Text Generator"
  mode: "workflow"
  icon: "✍️"
  icon_background: "#FBE8FF"
  description: "Generate or transform text"
dependencies: []
workflow:
  graph:
    nodes:
      - id: "start"
        type: custom
        position: {x: 80, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: start
          title: Start
          variables:
            - variable: input_text
              label: Input Text
              type: paragraph
              required: true
              max_length: 10000
            - variable: instruction
              label: Instruction
              type: text-input
              required: false
              max_length: 500
              default: "Summarize the following text concisely."
      - id: "llm"
        type: custom
        position: {x: 380, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: llm
          title: LLM
          model:
            provider: openai
            name: gpt-4o-mini
            mode: chat
            completion_params:
              temperature: 0.3
          prompt_template:
            - role: system
              text: "You are a precise text processing assistant. Follow the instruction exactly."
            - role: user
              text: |
                Instruction: {{#start.instruction#}}

                Text:
                {{#start.input_text#}}
          memory:
            enabled: false
          context:
            enabled: false
          vision:
            enabled: false
      - id: "end"
        type: custom
        position: {x: 680, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: end
          title: End
          outputs:
            - variable: result
              value_type: string
              value_selector:
                - llm
                - text
    edges:
      - id: "start-llm"
        source: "start"
        sourceHandle: "source"
        target: "llm"
        targetHandle: "target"
      - id: "llm-end"
        source: "llm"
        sourceHandle: "source"
        target: "end"
        targetHandle: "target"
  features: {}
  environment_variables: []
  conversation_variables: []
```

## Customization Points

| What to Change | Where |
|---------------|-------|
| Task type | `start.variables[1].default` (instruction) |
| Input format | `start.variables[0].type` (paragraph/text-input) |
| Precision vs creativity | `completion_params.temperature` |
| Output format | System prompt |

## Variations

### Translation
Change the instruction default and system prompt:
```yaml
# start variable
- variable: instruction
  default: "Translate the following text to English."

# system prompt
- role: system
  text: "You are a professional translator. Translate accurately while preserving tone and style."
```

### Structured Extraction (JSON output)
Add structured output to LLM:
```yaml
structured_output:
  enabled: true
  schema:
    type: object
    properties:
      name:
        type: string
        description: "Person's name"
      email:
        type: string
        description: "Email address"
      phone:
        type: string
        description: "Phone number"
    required: ["name"]
```

### Multi-Step Processing
Add a code node for post-processing:
```
Start → LLM → Code (format/validate) → End
```
