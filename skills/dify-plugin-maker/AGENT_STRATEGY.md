# Agent Strategy Plugin Guide

How to create custom agent reasoning strategies for Dify.

## Structure

```
my-agent-strategy/
├── _assets/
│   └── icon.svg
├── provider/
│   ├── my_agent.py          # Provider class
│   └── my_agent.yaml        # Provider identity + strategy list
├── strategies/
│   └── my_strategy.yaml     # Strategy definition (parameters)
├── main.py
├── manifest.yaml
├── pyproject.toml
└── README.md
```

## manifest.yaml

```yaml
version: 0.0.1
type: plugin
author: "your-org"
name: "my-agent"
label:
  en_US: "My Agent Strategy"
created_at: "2025-01-01T00:00:00.000000000Z"
icon: icon.svg
description:
  en_US: "Custom agent reasoning strategy"
tags:
  - "agent"
resource:
  memory: 1048576
  permission:
    tool:
      enabled: true
    model:
      enabled: true
      llm: true
plugins:
  agent_strategies:
    - "provider/my_agent.yaml"
meta:
  version: 0.0.2
  minimum_dify_version: "1.7.0"
  arch:
    - "amd64"
    - "arm64"
  runner:
    language: "python"
    version: "3.12"
    entrypoint: "main"
```

## provider/my_agent.yaml

```yaml
identity:
  author: your-org
  name: my_agent
  label:
    en_US: My Agent
  description:
    en_US: Custom agent strategy
  icon: icon.svg
strategies:
  - strategies/my_strategy.yaml
extra:
  python:
    source: provider/my_agent.py
```

## strategies/my_strategy.yaml

```yaml
identity:
  name: my_strategy
  author: your-org
  label:
    en_US: My Strategy
  description:
    en_US: A custom reasoning strategy
  icon: icon.svg
parameters:
  - name: model
    type: model-selector
    required: true
    label:
      en_US: Model
    scope: tool-call&llm
  - name: tools
    type: list[tools]
    required: true
    label:
      en_US: Tools
  - name: query
    type: string
    required: true
    label:
      en_US: Query
  - name: maximum_iterations
    type: number
    required: false
    default: 5
    label:
      en_US: Max Iterations
extra:
  python:
    source: strategies/my_strategy.py
```

## strategies/my_strategy.py

```python
import json
from collections.abc import Generator
from typing import Any

from dify_plugin.entities.agent import AgentInvokeMessage
from dify_plugin.entities.model.llm import LLMModelConfig, LLMResult, LLMResultChunk
from dify_plugin.entities.model.message import (
    PromptMessageTool,
    SystemPromptMessage,
    UserPromptMessage,
)
from dify_plugin.entities.tool import ToolInvokeMessage, ToolParameter
from dify_plugin.interfaces.agent import AgentModelConfig, AgentStrategy, ToolEntity
from pydantic import BaseModel


class StrategyParams(BaseModel):
    maximum_iterations: int = 5
    model: AgentModelConfig
    tools: list[ToolEntity]
    query: str


class MyAgentStrategy(AgentStrategy):
    def _invoke(self, parameters: dict[str, Any]) -> Generator[AgentInvokeMessage]:
        params = StrategyParams(**parameters)

        # Build tool definitions for the LLM
        tools = []
        for tool in params.tools:
            tools.append(
                PromptMessageTool(
                    name=tool.identity.name,
                    description=tool.description.llm or "",
                    parameters={
                        "type": "object",
                        "properties": {
                            p.name: p.model_dump()
                            for p in tool.parameters
                            if p.form == "llm"
                        },
                        "required": [
                            p.name for p in tool.parameters
                            if p.required and p.form == "llm"
                        ],
                    },
                )
            )

        # Initial messages
        messages = [
            SystemPromptMessage(content="You are a helpful agent. Use tools to answer."),
            UserPromptMessage(content=params.query),
        ]

        # Agent loop
        for iteration in range(params.maximum_iterations):
            # Call LLM
            response = self.session.model.llm.invoke(
                model_config=LLMModelConfig(**params.model.model_dump()),
                prompt_messages=messages,
                tools=tools,
                stream=False,
            )

            if isinstance(response, LLMResult):
                # Check if LLM wants to call a tool
                if response.message.tool_calls:
                    for tool_call in response.message.tool_calls:
                        # Execute the tool
                        tool_result = self.session.tool.invoke(
                            provider_type=ToolProviderType.BUILT_IN,
                            provider=tool_call.function.name.split("/")[0],
                            tool_name=tool_call.function.name,
                            parameters=json.loads(tool_call.function.arguments),
                        )

                        # Yield thought message
                        yield self.create_text_message(
                            f"Using tool: {tool_call.function.name}"
                        )

                        # Add tool result to messages for next iteration
                        # ... (append to messages)
                else:
                    # No tool call — final answer
                    yield self.create_text_message(response.message.content)
                    return

        # Max iterations reached
        yield self.create_text_message("Max iterations reached.")
```

## Key SDK Classes for Agent Strategies

```python
from dify_plugin.interfaces.agent import AgentStrategy, AgentModelConfig, ToolEntity
from dify_plugin.entities.agent import AgentInvokeMessage

# Session methods available:
self.session.model.llm.invoke(...)      # Call LLM
self.session.tool.invoke(...)           # Call a tool
```

## Gotchas

1. **Parameter types**: Use `model-selector` for model, `list[tools]` for tools
2. **Scope on model-selector**: `tool-call&llm` means model must support both
3. **Streaming**: Use `stream=True` for streaming responses, handle `LLMResultChunk`
4. **Tool results**: Must be appended to messages for multi-turn reasoning
5. **Yield messages**: Use `self.create_text_message()` for intermediate thoughts
