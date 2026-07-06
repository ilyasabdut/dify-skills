# Pattern: Agent with Tools

An autonomous agent that can use external tools to answer questions.

## Architecture

```
Start → Agent (with tools + memory) → Answer
```

## Mode: `advanced-chat`

## When to Use
- Chatbot that needs to search the web
- Assistant that can perform calculations
- Bot that calls external APIs autonomously
- Any task requiring multi-step reasoning with tool access

## Complete DSL

```yaml
version: "0.6.0"
kind: "app"
app:
  name: "Agent with Tools"
  mode: "advanced-chat"
  icon: "🤖"
  icon_background: "#FFE4DE"
  description: "An agent that can search the web and use tools"
dependencies:
  - type: "plugin"
    value:
      organization: "langgenius"
      plugin: "openai"
      version: "1.0.0"
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
      - id: "agent"
        type: custom
        position: {x: 380, y: 282}
        sourcePosition: right
        targetPosition: left
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
                  max_tokens: 4096
            tools:
              type: constant
              value:
                - provider_id: google
                  provider_type: builtin
                  provider_name: google
                  tool_name: google_search
                  tool_label: Google Search
                  tool_configurations:
                    result_type: link
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
      - id: "answer"
        type: custom
        position: {x: 680, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: answer
          title: Answer
          answer: "{{#agent.text#}}"
    edges:
      - id: "start-agent"
        source: "start"
        sourceHandle: "source"
        target: "agent"
        targetHandle: "target"
      - id: "agent-answer"
        source: "agent"
        sourceHandle: "source"
        target: "answer"
        targetHandle: "target"
  features:
    opening_statement: "Hi! I can search the web and look up information for you. What would you like to know?"
    suggested_questions:
      - "What's the latest news about AI?"
      - "Search for the population of Tokyo"
      - "Look up the history of the internet"
  environment_variables: []
  conversation_variables: []
```

## Customization Points

| What to Change | Where |
|---------------|-------|
| Tools available | `agent_parameters.tools.value` array |
| Agent model | `agent_parameters.model.value` |
| Max reasoning steps | `agent_parameters.max_iterations.value` |
| Strategy | `agent_strategy_name` (function_calling / react) |
| Memory length | `memory.window.size` |

## Variations

### With Custom API Tool
```yaml
tools:
  type: constant
  value:
    - provider_id: "custom-api-uuid"
      provider_type: api
      provider_name: weather_api
      tool_name: get_weather
      tool_label: Get Weather
      tool_configurations: {}
```

### ReAct Strategy (for models without function calling)
```yaml
agent_strategy_name: "react"
agent_strategy_label: "ReAct"
```

### With System Prompt
Add a system message in agent parameters:
```yaml
agent_parameters:
  system_prompt:
    type: constant
    value: "You are a research assistant. Always cite your sources."
```
