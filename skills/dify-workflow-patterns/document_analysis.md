# Pattern: Document Analysis

Upload files, extract text, and analyze with LLM.

## Architecture

```
Start (file upload) → Document Extractor → LLM (analyze) → End
```

## Mode: `workflow`

## When to Use
- PDF/document summarization
- Contract analysis
- Resume parsing
- Invoice data extraction
- Any file-in → analysis-out task

## Complete DSL

```yaml
version: "0.6.0"
kind: "app"
app:
  name: "Document Analyzer"
  mode: "workflow"
  icon: "📄"
  icon_background: "#FFF3E0"
  description: "Upload a document and get AI analysis"
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
            - variable: files
              label: Upload Document
              type: file-list
              required: true
              max_length: null
            - variable: instruction
              label: Analysis Instruction
              type: text-input
              required: false
              max_length: 500
              default: "Summarize this document, highlighting key points and action items."
      - id: "extractor"
        type: custom
        position: {x: 380, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: document-extractor
          title: Extract Text
          variable_selector:
            - start
            - files
      - id: "llm"
        type: custom
        position: {x: 680, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: llm
          title: Analyze
          model:
            provider: openai
            name: gpt-4o
            mode: chat
            completion_params:
              temperature: 0.3
              max_tokens: 4096
          prompt_template:
            - role: system
              text: |
                You are a document analysis expert. Analyze the provided document text and follow the user's instruction precisely.
                Structure your response clearly with headings and bullet points where appropriate.
            - role: user
              text: |
                Instruction: {{#start.instruction#}}

                Document content:
                {{#extractor.text#}}
          memory:
            enabled: false
          context:
            enabled: false
          vision:
            enabled: false
      - id: "end"
        type: custom
        position: {x: 980, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: end
          title: End
          outputs:
            - variable: analysis
              value_type: string
              value_selector:
                - llm
                - text
    edges:
      - id: "start-extractor"
        source: "start"
        sourceHandle: "source"
        target: "extractor"
        targetHandle: "target"
      - id: "extractor-llm"
        source: "extractor"
        sourceHandle: "source"
        target: "llm"
        targetHandle: "target"
      - id: "llm-end"
        source: "llm"
        sourceHandle: "source"
        target: "end"
        targetHandle: "target"
  features:
    file_upload:
      enabled: true
  environment_variables: []
  conversation_variables: []
```

## Customization Points

| What to Change | Where |
|---------------|-------|
| File type (single vs list) | `start.variables[0].type` (file vs file-list) |
| Analysis task | `start.variables[1].default` |
| Model (accuracy vs cost) | `llm.data.model` |
| Output format | System prompt |

## Variations

### With Structured Extraction (JSON)
Add structured output to LLM:
```yaml
structured_output:
  enabled: true
  schema:
    type: object
    properties:
      title:
        type: string
      summary:
        type: string
      key_points:
        type: array
        items:
          type: string
      action_items:
        type: array
        items:
          type: string
    required: ["title", "summary"]
```

### Multiple Documents (Iteration)
```
Start → Document Extractor → Iteration [LLM per doc] → Code (merge) → End
```

### With Knowledge Base Context
Add a knowledge-retrieval node to provide domain context:
```
Start → Doc Extractor → Knowledge Retrieval → LLM (doc + context) → End
```
