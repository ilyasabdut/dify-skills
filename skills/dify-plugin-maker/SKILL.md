---
name: dify-plugin-maker
description: "Use when creating a custom Dify plugin, scaffolding a tool provider, building a model integration, implementing an agent strategy, or setting up a trigger. Also for remote debugging plugins against a Dify instance."
---

# Dify Plugin Maker

Guide for creating Dify plugins. Plugins extend Dify with custom tools, model providers, agent strategies, triggers, and endpoints.

## Plugin Types

| Type | Purpose | Manifest Key |
|------|---------|-------------|
| Tool | Custom tools for workflows/agents (API calls, calculations) | `plugins.tools` |
| Model | LLM/embedding/rerank providers | `plugins.models` |
| Agent Strategy | Custom agent reasoning patterns (ReAct, FC) | `plugins.agent_strategies` |
| Trigger | Event-based workflow triggers (webhook, schedule, external) | `plugins.triggers` |
| Extension | Endpoints, OAuth, custom logic | `plugins.endpoints` |

## Plugin Structure

```
my-plugin/
├── _assets/              # Icons and images
│   └── icon.svg          # Plugin icon (required)
├── provider/             # Provider definition
│   ├── my_provider.py    # Provider class
│   └── my_provider.yaml  # Provider manifest
├── tools/                # For tool plugins
│   ├── my_tool.py        # Tool implementation
│   └── my_tool.yaml      # Tool schema (parameters/outputs)
├── models/               # For model plugins
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── llm.py        # LLM implementation
│   │   └── model-name.yaml  # Model definition
│   └── common.py
├── strategies/           # For agent strategy plugins
│   └── my_strategy.yaml  # Strategy definition
├── events/               # For trigger plugins
│   ├── my_event.py       # Event handler
│   └── my_event.yaml     # Event schema
├── main.py               # Entry point (required)
├── manifest.yaml         # Plugin manifest (required)
├── pyproject.toml        # Python dependencies
├── .env.example          # Environment variable template
└── README.md
```

## manifest.yaml (Required)

```yaml
version: 0.0.1
type: plugin
author: "your-org"
name: "my-plugin"
label:
  en_US: "My Plugin"
created_at: "2025-01-01T00:00:00.000000000Z"
icon: icon.svg
description:
  en_US: "Description of what this plugin does"
tags:
  - "tool"                 # or: model, agent, trigger
resource:
  memory: 1048576          # Memory limit in bytes (1MB default)
  permission:
    tool:
      enabled: true        # Can invoke tools
    model:
      enabled: true        # Can invoke models
      llm: true
    storage:
      enabled: true        # Can use persistent storage
      size: 1048576
    endpoint:
      enabled: false
plugins:
  tools:                   # List tool providers
    - "provider/my_provider.yaml"
  # OR
  models:                  # List model providers
    - "provider/my_provider.yaml"
  # OR
  agent_strategies:        # List agent strategies
    - "provider/my_provider.yaml"
  # OR
  endpoints:               # List endpoints
    - "endpoints/my_endpoint.yaml"
meta:
  version: 0.0.2           # SDK version
  minimum_dify_version: "1.7.0"
  arch:
    - "amd64"
    - "arm64"
  runner:
    language: "python"
    version: "3.12"
    entrypoint: "main"
```

## main.py (Required)

Every plugin has the same entry point:

```python
from dify_plugin import DifyPluginEnv, Plugin

plugin = Plugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=240))

if __name__ == "__main__":
    plugin.run()
```

## Creating a Tool Plugin

### 1. Provider YAML (`provider/my_tools.yaml`)

```yaml
identity:
  author: your-org
  name: my_tools
  label:
    en_US: My Tools
  description:
    en_US: A collection of custom tools
  icon: icon.svg
credentials_for_provider:       # Optional: provider-level credentials
  api_key:
    type: secret-input
    required: true
    label:
      en_US: API Key
    placeholder:
      en_US: Enter your API key
tools:
  - tools/my_tool.yaml
extra:
  python:
    source: provider/my_tools.py
```

### 2. Provider Python (`provider/my_tools.py`)

```python
from dify_plugin.provider import ToolProvider


class MyToolsProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        # Validate provider credentials
        api_key = credentials.get("api_key")
        if not api_key:
            raise ValueError("API key is required")
```

### 3. Tool YAML (`tools/my_tool.yaml`)

```yaml
identity:
  name: my_tool
  author: your-org
  label:
    en_US: My Tool
  description:
    en_US: Does something useful
parameters:
  - name: query
    type: string
    required: true
    label:
      en_US: Query
    human_description:
      en_US: The input query to process
    form: llm                  # llm = agent fills, form = user fills
  - name: limit
    type: number
    required: false
    default: 10
    label:
      en_US: Limit
    form: form
output:
  - name: result
    type: string
    description:
      en_US: The processed result
extra:
  python:
    source: tools/my_tool.py
```

### 4. Tool Python (`tools/my_tool.py`)

```python
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class MyTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        query = tool_parameters.get("query", "")
        limit = tool_parameters.get("limit", 10)

        # Get provider credentials
        api_key = self.runtime.credentials.get("api_key")

        # Do the work
        result = f"Processed: {query} (limit={limit})"

        # Yield result messages
        yield self.create_text_message(result)
        # Or yield JSON:
        # yield self.create_json_message({"key": "value"})
        # Or yield a link:
        # yield self.create_link_message("https://example.com")
```

### Parameter Types

| Type | Description |
|------|-------------|
| `string` | Text input |
| `number` | Numeric input |
| `boolean` | True/false |
| `select` | Dropdown (requires `options`) |
| `secret-input` | Hidden/encrypted input |
| `file` | File upload |

### Parameter Form Values

| Form | Description |
|------|-------------|
| `llm` | Agent/LLM fills this parameter automatically |
| `form` | User must fill this in the UI |

### Tool Invoke Message Types

```python
self.create_text_message("text result")
self.create_json_message({"key": "value"})
self.create_link_message("https://url.com")
self.create_blob_message(bytes_data, meta={"mime_type": "image/png"})
self.create_image_message("https://image-url.com")
```

## Creating a Model Provider Plugin

### Provider YAML (`provider/my_model.yaml`)

```yaml
provider: my_model
label:
  en_US: My Model Provider
description:
  en_US: Custom model provider
icon_small:
  en_US: icon_s_en.svg
icon_large:
  en_US: icon_l_en.png
supported_model_types:
  - llm
  - text-embedding
configurate_methods:
  - predefined-model         # Models defined in YAML files
  # OR
  - customizable-model       # User can add any model name
credentials_for_provider:
  api_key:
    type: secret-input
    required: true
    label:
      en_US: API Key
    placeholder:
      en_US: Enter API key
  api_base:
    type: text-input
    required: false
    label:
      en_US: API Base URL
    placeholder:
      en_US: https://api.example.com/v1
extra:
  python:
    source: provider/my_model.py
```

### Model Definition YAML (`models/llm/my-model.yaml`)

```yaml
model: my-model-name
label:
  en_US: My Model
model_type: llm
features:
  - agent-thought
  - stream-tool-call
model_properties:
  mode: chat
  context_size: 128000
parameter_rules:
  - name: temperature
    use_template: temperature
  - name: top_p
    use_template: top_p
  - name: max_tokens
    use_template: max_tokens
    default: 4096
    min: 1
    max: 128000
pricing:
  input: "0.003"
  output: "0.015"
  unit: "0.001"
  currency: USD
```

### LLM Implementation (`models/llm/llm.py`)

```python
from collections.abc import Generator
from typing import Optional, Union

from dify_plugin.entities.model import (
    AIModelEntity,
    FetchFrom,
    ModelType,
)
from dify_plugin.entities.model.llm import (
    LLMResult,
    LLMResultChunk,
    LLMResultChunkDelta,
)
from dify_plugin.entities.model.message import (
    PromptMessage,
    PromptMessageTool,
)
from dify_plugin.interfaces.model.large_language_model import LargeLanguageModel


class MyLLM(LargeLanguageModel):
    def _invoke(
        self,
        model: str,
        credentials: dict,
        prompt_messages: list[PromptMessage],
        model_parameters: dict,
        tools: Optional[list[PromptMessageTool]] = None,
        stop: Optional[list[str]] = None,
        stream: bool = True,
        user: Optional[str] = None,
    ) -> Union[LLMResult, Generator[LLMResultChunk, None, None]]:
        # Implement model invocation
        ...

    def validate_credentials(self, model: str, credentials: dict) -> None:
        # Validate that credentials work
        ...

    def get_num_tokens(
        self, model: str, credentials: dict, prompt_messages: list[PromptMessage],
        tools: Optional[list[PromptMessageTool]] = None,
    ) -> int:
        # Return token count estimate
        return 0
```

## Creating a Trigger Plugin

### Event YAML (`events/my_event.yaml`)

```yaml
identity:
  name: my_event
  author: your-org
  label:
    en_US: My Event Trigger
  description:
    en_US: Triggers workflow when event occurs
parameters:
  - name: webhook_url
    type: string
    required: false
    label:
      en_US: Webhook URL
    form: form
output:
  - name: payload
    type: string
    description:
      en_US: Event payload data
extra:
  python:
    source: events/my_event.py
```

## pyproject.toml

```toml
[project]
name = "my-plugin"
version = "0.0.1"
requires-python = ">=3.12"
dependencies = [
    "dify-plugin>=0.1.0",
    "httpx>=0.27.0",
]
```

## Remote Debugging

To debug a plugin against a running Dify instance:

1. Set environment variables:
```bash
INSTALL_METHOD=remote
REMOTE_INSTALL_HOST=http://localhost  # Dify host
REMOTE_INSTALL_PORT=5003             # Plugin daemon port
REMOTE_INSTALL_KEY=your-debug-key    # From Dify plugin settings
```

2. Run plugin locally:
```bash
python main.py
```

3. The plugin connects to the Dify instance and registers itself for testing.

## Packaging and Publishing

```bash
# Install Dify CLI
pip install dify-cli

# Initialize new plugin
dify plugin init

# Package plugin
dify plugin package ./my-plugin

# Publish to marketplace
dify plugin publish ./my-plugin.difypkg
```

## Quick Start Templates

### Minimal Tool Plugin
```
manifest.yaml + main.py + provider/tools.yaml + provider/tools.py + tools/my_tool.yaml + tools/my_tool.py
```

### Minimal Model Plugin  
```
manifest.yaml + main.py + provider/model.yaml + provider/model.py + models/llm/llm.py + models/llm/model-name.yaml
```

## Gotchas

1. **Entry point must be `main`** — specified in manifest `meta.runner.entrypoint`
2. **Python 3.12** — plugins run on Python 3.12
3. **Memory limits** — default 1MB, increase in `resource.memory`
4. **Permissions** — must explicitly enable tool/model/storage access
5. **Credentials are per-provider** — defined in provider YAML, accessed via `self.runtime.credentials`
6. **Tool form types** — `llm` means the agent fills it, `form` means user fills it in UI
7. **Yield messages** — tools use generator pattern, yield `ToolInvokeMessage` objects
8. **Icons** — put in `_assets/` directory, reference from manifest
