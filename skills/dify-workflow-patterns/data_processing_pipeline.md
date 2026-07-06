# Pattern: Data Processing Pipeline

Process lists of items with LLM — batch summarization, categorization, enrichment.

## Architecture

```
Start (items) → Code (parse/split) → Iteration [ LLM per item ] → Code (merge) → End
```

## Mode: `workflow`

## When to Use
- Batch process CSV/JSON records
- Summarize multiple articles
- Categorize a list of items
- Enrich data with LLM analysis
- Any list-in → processed-list-out task

## Complete DSL

```yaml
version: "0.6.0"
kind: "app"
app:
  name: "Data Processing Pipeline"
  mode: "workflow"
  icon: "⚙️"
  icon_background: "#E4FBCC"
  description: "Process a list of items with LLM"
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
            - variable: items_json
              label: Items (JSON array)
              type: paragraph
              required: true
              max_length: 50000
      - id: "parse"
        type: custom
        position: {x: 380, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: code
          title: Parse Items
          variables:
            - variable: raw_input
              value_selector:
                - start
                - items_json
          code_language: python3
          code: |
            import json

            def main(raw_input: str) -> dict:
                items = json.loads(raw_input)
                return {"items": items, "count": len(items)}
          outputs:
            items:
              type: array[object]
            count:
              type: number
      - id: "iteration"
        type: custom
        position: {x: 680, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: iteration
          title: Process Each Item
          iterator_selector:
            - parse
            - items
          output_selector:
            - iter_llm
            - text
          is_parallel: false
          parallel_nums: 10
          error_handle_mode: CONTINUE_ON_ERROR
          flatten_output: true
      - id: "iter_start"
        type: custom
        position: {x: 720, y: 400}
        sourcePosition: right
        targetPosition: left
        parentId: "iteration"
        data:
          type: iteration-start
          title: Iteration Start
      - id: "iter_llm"
        type: custom
        position: {x: 920, y: 400}
        sourcePosition: right
        targetPosition: left
        parentId: "iteration"
        data:
          type: llm
          title: Process Item
          model:
            provider: openai
            name: gpt-4o-mini
            mode: chat
            completion_params:
              temperature: 0.3
          prompt_template:
            - role: system
              text: "Summarize the following item in one sentence."
            - role: user
              text: "{{#iter_start.item#}}"
          memory:
            enabled: false
          context:
            enabled: false
          vision:
            enabled: false
      - id: "merge"
        type: custom
        position: {x: 980, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: code
          title: Merge Results
          variables:
            - variable: results
              value_selector:
                - iteration
                - output
            - variable: count
              value_selector:
                - parse
                - count
          code_language: python3
          code: |
            import json

            def main(results: list, count: int) -> dict:
                output = json.dumps({
                    "total": count,
                    "processed": len(results),
                    "results": results
                }, indent=2)
                return {"output": output}
          outputs:
            output:
              type: string
      - id: "end"
        type: custom
        position: {x: 1280, y: 282}
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
      - id: "start-parse"
        source: "start"
        sourceHandle: "source"
        target: "parse"
        targetHandle: "target"
      - id: "parse-iteration"
        source: "parse"
        sourceHandle: "source"
        target: "iteration"
        targetHandle: "target"
      - id: "iter_start-iter_llm"
        source: "iter_start"
        sourceHandle: "source"
        target: "iter_llm"
        targetHandle: "target"
      - id: "iteration-merge"
        source: "iteration"
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
| Processing task | `iter_llm` system prompt |
| Input format | `parse` code node (JSON, CSV, etc.) |
| Output format | `merge` code node |
| Parallelism | `iteration.is_parallel` + `parallel_nums` |
| Error handling | `iteration.error_handle_mode` |

## Variations

### Parallel Processing (faster)
```yaml
is_parallel: true
parallel_nums: 5
error_handle_mode: CONTINUE_ON_ERROR
```

### With HTTP Fetch Per Item
Add an http-request node inside the iteration:
```
iter_start → http-request (fetch details) → llm (analyze) 
```

### CSV Input
Change the parse node:
```python
import csv
import io

def main(raw_input: str) -> dict:
    reader = csv.DictReader(io.StringIO(raw_input))
    items = [row for row in reader]
    return {"items": items, "count": len(items)}
```
