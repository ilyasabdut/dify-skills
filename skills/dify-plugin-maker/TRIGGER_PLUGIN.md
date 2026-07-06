# Trigger Plugin Guide

How to create event-based triggers for Dify workflows (Dify 1.10.0+).

## Structure

```
my-trigger/
├── _assets/
│   └── icon.svg
├── provider/
│   ├── my_trigger.py        # Provider class (OAuth, credential validation)
│   └── my_trigger.yaml      # Provider identity
├── events/
│   ├── my_event.py          # Event handler
│   └── my_event.yaml        # Event schema
├── main.py
├── manifest.yaml
├── pyproject.toml
└── README.md
```

## manifest.yaml

```yaml
version: 0.1.0
type: plugin
author: "your-org"
name: "my-trigger"
label:
  en_US: "My Trigger"
created_at: "2025-01-01T00:00:00.000000000Z"
icon: icon.svg
description:
  en_US: "Triggers workflows from external events"
tags:
  - "trigger"
resource:
  memory: 1048576
  permission:
    tool:
      enabled: true
    model:
      enabled: false
    endpoint:
      enabled: true
plugins:
  triggers:
    - "provider/my_trigger.yaml"
meta:
  version: 0.0.2
  minimum_dify_version: "1.10.0"
  arch:
    - "amd64"
    - "arm64"
  runner:
    language: "python"
    version: "3.12"
    entrypoint: "main"
```

## provider/my_trigger.yaml

```yaml
identity:
  author: your-org
  name: my_trigger
  label:
    en_US: My Trigger
  description:
    en_US: Receives external events and triggers workflows
  icon: icon.svg
credentials_for_provider:
  webhook_secret:
    type: secret-input
    required: true
    label:
      en_US: Webhook Secret
    placeholder:
      en_US: Enter your webhook signing secret
events:
  - events/my_event.yaml
extra:
  python:
    source: provider/my_trigger.py
```

## events/my_event.yaml

```yaml
identity:
  name: my_event
  author: your-org
  label:
    en_US: My Event
  description:
    en_US: Triggered when an external event occurs
parameters:
  - name: filter_type
    type: select
    required: false
    label:
      en_US: Event Filter
    options:
      - value: all
        label:
          en_US: All Events
      - value: specific
        label:
          en_US: Specific Events
    form: form
output:
  - name: event_type
    type: string
    description:
      en_US: The type of event that occurred
  - name: payload
    type: string
    description:
      en_US: Event payload data as JSON string
  - name: timestamp
    type: string
    description:
      en_US: When the event occurred
extra:
  python:
    source: events/my_event.py
```

## events/my_event.py

```python
from collections.abc import Generator
from typing import Any

from dify_plugin import Trigger
from dify_plugin.entities.trigger import TriggerInvokeMessage


class MyEventTrigger(Trigger):
    def _invoke(self, parameters: dict[str, Any]) -> Generator[TriggerInvokeMessage]:
        """
        Called when the trigger receives an event.
        Yield messages to start the workflow.
        """
        filter_type = parameters.get("filter_type", "all")

        # Access the incoming event data
        event_data = parameters.get("event_data", {})
        event_type = event_data.get("type", "unknown")

        # Filter if needed
        if filter_type == "specific" and event_type != "target_event":
            return

        # Yield trigger output — this starts the workflow
        yield self.create_trigger_message(
            data={
                "event_type": event_type,
                "payload": str(event_data),
                "timestamp": event_data.get("timestamp", ""),
            }
        )
```

## Example: Outlook Email Trigger (Real Plugin)

The `outlook_trigger` plugin listens for new emails and starts workflows:

```python
class EmailReceivedTrigger(Trigger):
    def _invoke(self, parameters: dict[str, Any]) -> Generator[TriggerInvokeMessage]:
        # OAuth credentials from provider
        access_token = self.runtime.credentials.get("access_token")
        
        # Poll or receive webhook for new emails
        # When email arrives, yield trigger message
        yield self.create_trigger_message(
            data={
                "subject": email.subject,
                "from": email.sender,
                "body": email.body,
                "received_at": email.received_at,
            }
        )
```

## Gotchas

1. **Minimum Dify version**: Triggers require Dify 1.10.0+
2. **Endpoint permission**: Must enable `endpoint.enabled: true` in manifest
3. **Output schema**: Define outputs in event YAML — these become workflow start variables
4. **Polling vs webhook**: Plugin can poll external service or expose an endpoint for webhooks
5. **OAuth**: Use `credentials_for_provider` with OAuth flow for services that need it
