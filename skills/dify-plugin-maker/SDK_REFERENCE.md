# Dify Plugin SDK Reference

Quick reference for the `dify_plugin` Python SDK.

## Installation

```bash
pip install dify-plugin
# Or in pyproject.toml:
# dependencies = ["dify-plugin>=0.9.0"]
```

## Key Imports

```python
# Entry point
from dify_plugin import Plugin, DifyPluginEnv

# Tool plugins
from dify_plugin import Tool, ToolProvider
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

# Model plugins
from dify_plugin import ModelProvider, LargeLanguageModel
from dify_plugin.entities.model import ModelType, AIModelEntity
from dify_plugin.entities.model.llm import LLMResult, LLMResultChunk, LLMResultChunkDelta
from dify_plugin.entities.model.message import (
    PromptMessage,
    PromptMessageTool,
    SystemPromptMessage,
    UserPromptMessage,
    AssistantPromptMessage,
)
from dify_plugin.errors.model import CredentialsValidateFailedError

# Agent strategy plugins
from dify_plugin.interfaces.agent import AgentStrategy, AgentModelConfig, ToolEntity
from dify_plugin.entities.agent import AgentInvokeMessage

# Trigger plugins
from dify_plugin import Trigger
from dify_plugin.entities.trigger import TriggerInvokeMessage
```

## Base Classes

| Plugin Type | Provider Base | Implementation Base |
|-------------|--------------|-------------------|
| Tool | `ToolProvider` | `Tool` |
| Model | `ModelProvider` | `LargeLanguageModel`, `TextEmbeddingModel`, etc. |
| Agent Strategy | (none) | `AgentStrategy` |
| Trigger | (provider class) | `Trigger` |

## Tool Message Types

```python
# In Tool._invoke():
yield self.create_text_message(text="result text")
yield self.create_json_message(data={"key": "value"})
yield self.create_link_message(link="https://example.com")
yield self.create_blob_message(blob=bytes_data, meta={"mime_type": "image/png"})
yield self.create_image_message(image="https://image-url.com")
yield self.create_log_message(label="debug", data={"info": "details"})
```

## Accessing Runtime

```python
# In any tool/strategy:
self.runtime.credentials          # Provider credentials dict
self.runtime.model_credentials    # Model credentials (model plugins)
```

## Session Methods (Agent Strategies)

```python
# Call an LLM
response = self.session.model.llm.invoke(
    model_config=LLMModelConfig(...),
    prompt_messages=[...],
    tools=[...],
    stream=True,
)

# Call a tool
result = self.session.tool.invoke(
    provider_type=ToolProviderType.BUILT_IN,
    provider="google",
    tool_name="google_search",
    parameters={"query": "search term"},
)
```

## Reverse Invocation (Call Dify FROM Plugin)

Plugins can call back into Dify services:

```python
# Call another LLM model
self.session.model.llm.invoke(model_config=..., prompt_messages=...)

# Call an app (Chat, Workflow, Completion)
self.session.app.chat.invoke(app_id=..., inputs=..., query=...)
self.session.app.workflow.invoke(app_id=..., inputs=...)
self.session.app.completion.invoke(app_id=..., inputs=...)

# Call a tool
self.session.tool.invoke(provider=..., tool_name=..., parameters=...)

# Call a specific workflow node
self.session.node.invoke(node_type=..., inputs=...)
```

## Credential Types (for provider YAML)

| Type | Description | Use For |
|------|-------------|---------|
| `secret-input` | Masked input | API keys, tokens |
| `text-input` | Plain text | URLs, names |
| `select` | Dropdown | Regions, modes |
| `boolean` | Checkbox | Feature toggles |

## Parameter Form Values

| Value | Description |
|-------|-------------|
| `llm` | LLM/agent fills automatically at runtime |
| `form` | User fills in the UI when configuring |

## Tags

Available tags for `manifest.yaml`:
```
search, image, videos, weather, finance, design, travel,
social, news, medical, productivity, education, business,
entertainment, utilities, other, agent, trigger
```

## CLI Commands

```bash
# Scaffold new plugin
dify plugin init

# Package for distribution
dify plugin package ./

# Create a bundle
dify bundle init
dify bundle append marketplace . --marketplace_pattern=org/plugin:version
dify bundle append package . --package_path=./plugin.difypkg
```
