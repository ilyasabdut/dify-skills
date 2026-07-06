# Pattern: Simple Chatbot

A basic conversational AI with customizable personality.

## Architecture

```
Start → LLM (with memory) → Answer
```

## Mode: `advanced-chat`

## When to Use
- Simple Q&A chatbot
- Customer service bot with personality
- Writing assistant
- Any conversational app without external data

## Complete DSL

```yaml
version: "0.6.0"
kind: "app"
app:
  name: "Simple Chatbot"
  mode: "advanced-chat"
  icon: "💬"
  icon_background: "#E4FBCC"
  description: "A simple conversational chatbot"
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
          variables: []
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
              temperature: 0.7
          prompt_template:
            - role: system
              text: "You are a helpful, friendly assistant. Answer questions clearly and concisely."
            - role: user
              text: "{{#sys.query#}}"
          memory:
            enabled: true
            window:
              enabled: true
              size: 10
          context:
            enabled: false
          vision:
            enabled: false
      - id: "answer"
        type: custom
        position: {x: 680, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: answer
          title: Answer
          answer: "{{#llm.text#}}"
    edges:
      - id: "start-llm"
        source: "start"
        sourceHandle: "source"
        target: "llm"
        targetHandle: "target"
      - id: "llm-answer"
        source: "llm"
        sourceHandle: "source"
        target: "answer"
        targetHandle: "target"
  features:
    opening_statement: "Hello! How can I help you today?"
    suggested_questions:
      - "What can you help me with?"
      - "Tell me about yourself"
    suggested_questions_after_answer:
      enabled: true
  environment_variables: []
  conversation_variables: []
```

## Customization Points

| What to Change | Where |
|---------------|-------|
| Bot personality | `prompt_template[0].text` (system prompt) |
| Model | `model.provider` + `model.name` |
| Creativity | `completion_params.temperature` |
| Memory length | `memory.window.size` |
| Welcome message | `features.opening_statement` |
| Suggested questions | `features.suggested_questions` |

## Variations

### With File Upload Support
Add to features:
```yaml
features:
  file_upload:
    enabled: true
    allowed_file_types:
      - image
      - document
    max_file_size: 10
    max_file_count: 5
```
And enable vision on LLM node:
```yaml
vision:
  enabled: true
  configs:
    detail: high
```

### With System Prompt Variable
Add a conversation variable for dynamic system prompts:
```yaml
conversation_variables:
  - id: "system_prompt"
    name: "system_prompt"
    value_type: string
    value: "You are a helpful assistant."
```
Then reference: `{{#conversation.system_prompt#}}`
