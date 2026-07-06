# Pattern: API Orchestration

Call external APIs, branch based on responses, and merge results.

## Architecture

```
Start → HTTP Request → If-Else (check status) → [Success: Process / Failure: Error] → End
```

Or with parallel APIs:
```
Start → [HTTP A, HTTP B, HTTP C] → Variable Aggregator → Code (merge) → End
```

## Mode: `workflow`

## When to Use
- Fetching data from external APIs and transforming results
- Multi-API aggregation (call several endpoints, merge)
- Conditional logic based on API responses
- Data enrichment pipelines

## Complete DSL (Single API with Error Handling)

```yaml
version: "0.6.0"
kind: "app"
app:
  name: "API Orchestration"
  mode: "workflow"
  icon: "🔗"
  icon_background: "#D5F5F6"
  description: "Fetch from API, handle errors, process results"
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
            - variable: endpoint
              label: API Endpoint
              type: text-input
              required: true
              max_length: 500
      - id: "http"
        type: custom
        position: {x: 380, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: http-request
          title: Fetch API
          method: GET
          url: "{{#start.endpoint#}}"
          headers: |
            Accept: application/json
          params: ""
          body: null
          authorization:
            type: no-auth
          timeout:
            connect: 10
            read: 30
            write: 10
          ssl_verify: true
      - id: "check_status"
        type: custom
        position: {x: 680, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: if-else
          title: Check Status
          cases:
            - case_id: "success"
              logical_operator: and
              conditions:
                - variable_selector:
                    - http
                    - status_code
                  comparison_operator: "="
                  value: "200"
      - id: "process"
        type: custom
        position: {x: 980, y: 182}
        sourcePosition: right
        targetPosition: left
        data:
          type: code
          title: Process Response
          variables:
            - variable: response_body
              value_selector:
                - http
                - body
          code_language: python3
          code: |
            import json

            def main(response_body: str) -> dict:
                data = json.loads(response_body)
                # Process the API response
                summary = json.dumps(data, indent=2)
                return {"result": summary, "success": True}
          outputs:
            result:
              type: string
            success:
              type: number
      - id: "error_handler"
        type: custom
        position: {x: 980, y: 382}
        sourcePosition: right
        targetPosition: left
        data:
          type: code
          title: Handle Error
          variables:
            - variable: status_code
              value_selector:
                - http
                - status_code
            - variable: body
              value_selector:
                - http
                - body
          code_language: python3
          code: |
            def main(status_code: int, body: str) -> dict:
                return {
                    "result": f"API Error: HTTP {status_code} - {body[:200]}",
                    "success": False
                }
          outputs:
            result:
              type: string
            success:
              type: number
      - id: "merge"
        type: custom
        position: {x: 1280, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: variable-aggregator
          title: Merge Results
          output_type: string
          variables:
            - - process
              - result
            - - error_handler
              - result
      - id: "end"
        type: custom
        position: {x: 1580, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: end
          title: End
          outputs:
            - variable: result
              value_type: string
              value_selector:
                - merge
                - output
    edges:
      - id: "start-http"
        source: "start"
        sourceHandle: "source"
        target: "http"
        targetHandle: "target"
      - id: "http-check"
        source: "http"
        sourceHandle: "source"
        target: "check_status"
        targetHandle: "target"
      - id: "check-success"
        source: "check_status"
        sourceHandle: "success"
        target: "process"
        targetHandle: "target"
      - id: "check-error"
        source: "check_status"
        sourceHandle: "false"
        target: "error_handler"
        targetHandle: "target"
      - id: "process-merge"
        source: "process"
        sourceHandle: "source"
        target: "merge"
        targetHandle: "target"
      - id: "error-merge"
        source: "error_handler"
        sourceHandle: "source"
        target: "merge"
        targetHandle: "target"
      - id: "merge-end"
        source: "merge"
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
| HTTP method | `http.data.method` |
| URL/endpoint | `http.data.url` |
| Headers/auth | `http.data.headers`, `http.data.authorization` |
| Success condition | `check_status.cases[0].conditions` |
| Response processing | `process.code` |
| Error handling | `error_handler.code` |

## Variations

### With Authentication (Bearer Token)
```yaml
authorization:
  type: api-key
  config:
    type: bearer
    api_key: "{{#env.API_TOKEN#}}"
```

### POST with JSON Body
```yaml
method: POST
body:
  type: json
  data: |
    {
      "query": "{{#start.query#}}",
      "limit": 10
    }
```

### Multiple Parallel API Calls
```
Start → [HTTP A, HTTP B] → Variable Aggregator → LLM (summarize) → End
```
Create multiple HTTP nodes with edges from start to each, then all converge to aggregator.

### With Retry Logic
```yaml
retry_config:
  enabled: true
  max_retries: 3
  retry_interval: 2000
  exponential_backoff:
    enabled: true
    multiplier: 2
    max_interval: 10000
```
