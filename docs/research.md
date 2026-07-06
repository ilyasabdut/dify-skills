# Dify App Creation Research

> Research for building LLM skills to programmatically generate Dify apps (similar to [n8n-skills](https://github.com/czlonkowski/n8n-skills))

## Table of Contents

1. [App Modes](#app-modes)
2. [Database Tables](#database-tables)
3. [DSL Format](#dsl-format)
4. [Workflow Nodes](#workflow-nodes)
5. [App Creation Flow](#app-creation-flow)
6. [Skills Architecture Plan](#skills-architecture-plan)

---

## App Modes

```python
class AppMode(StrEnum):
    COMPLETION = "completion"       # Simple text generation
    WORKFLOW = "workflow"            # Workflow with Start → ... → End
    CHAT = "chat"                   # Basic chatbot
    ADVANCED_CHAT = "advanced-chat" # Chatflow with Start → ... → Answer
    AGENT_CHAT = "agent-chat"       # Agent with tools
    CHANNEL = "channel"
    RAG_PIPELINE = "rag-pipeline"
```

---

## Database Tables

### Primary Tables for App Creation

#### 1. `apps` table (App model)

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| id | UUID | auto | Primary key |
| tenant_id | UUID | yes | Workspace ID |
| name | String(255) | yes | App name |
| description | LongText | no | Default: '' |
| mode | String(255) | yes | AppMode value |
| icon_type | String(255) | no | 'image', 'emoji', 'link' |
| icon | String(255) | no | Emoji or image ref |
| icon_background | String(255) | no | Hex color |
| app_model_config_id | UUID | no | FK to app_model_configs (for non-workflow modes) |
| workflow_id | UUID | no | FK to workflows (for workflow/advanced-chat modes) |
| status | String(255) | auto | Default: 'normal' |
| enable_site | Boolean | yes | Enable web app |
| enable_api | Boolean | yes | Enable API access |
| api_rpm | Integer | no | Rate limit per minute |
| api_rph | Integer | no | Rate limit per hour |
| is_demo | Boolean | auto | Default: false |
| is_public | Boolean | auto | Default: false |
| is_universal | Boolean | auto | Default: false |
| tracing | LongText | no | Tracing config |
| max_active_requests | Integer | no | |
| use_icon_as_answer_icon | Boolean | auto | Default: false |
| created_by | UUID | no | Account ID |
| created_at | DateTime | auto | |
| updated_by | UUID | no | |
| updated_at | DateTime | auto | |

#### 2. `workflows` table (Workflow model)

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| id | UUID | auto | Primary key |
| tenant_id | UUID | yes | Workspace ID |
| app_id | UUID | yes | FK to apps |
| type | String(255) | yes | 'workflow' or 'chat' |
| version | String(255) | yes | 'draft' or version number |
| marked_name | String(255) | no | Version label |
| marked_comment | String(255) | no | Version comment |
| graph | LongText | yes | JSON: {nodes: [], edges: []} |
| features | LongText | no | JSON: feature flags |
| environment_variables | LongText | no | JSON |
| conversation_variables | LongText | no | JSON |
| rag_pipeline_variables | LongText | no | JSON |
| created_by | UUID | yes | |
| created_at | DateTime | auto | |
| updated_by | UUID | no | |
| updated_at | DateTime | auto | |

#### 3. `app_model_configs` table (for non-workflow modes)

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| id | UUID | auto | Primary key |
| app_id | UUID | yes | FK to apps |
| provider | String(255) | no | Model provider |
| model_id | String(255) | no | Model name |
| configs | JSON | no | |
| opening_statement | LongText | no | Welcome message |
| suggested_questions | LongText | no | JSON array |
| suggested_questions_after_answer | LongText | no | JSON |
| speech_to_text | LongText | no | JSON |
| text_to_speech | LongText | no | JSON |
| more_like_this | LongText | no | JSON |
| model | LongText | no | JSON: model config |
| user_input_form | LongText | no | JSON: form fields |
| dataset_query_variable | String(255) | no | |
| pre_prompt | LongText | no | System prompt |
| agent_mode | LongText | no | JSON: agent config |
| sensitive_word_avoidance | LongText | no | JSON |
| retriever_resource | LongText | no | JSON |
| prompt_type | String(255) | yes | 'simple' or 'advanced' |
| chat_prompt_config | LongText | no | JSON |
| completion_prompt_config | LongText | no | JSON |
| dataset_configs | LongText | no | JSON |
| external_data_tools | LongText | no | JSON |
| file_upload | LongText | no | JSON |
| created_by | UUID | no | |
| created_at | DateTime | auto | |
| updated_by | UUID | no | |
| updated_at | DateTime | auto | |

#### 4. `installed_apps` table (via event handler after app creation)

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| id | UUID | auto | Primary key |
| tenant_id | UUID | yes | Workspace ID |
| app_id | UUID | yes | FK to apps |
| app_owner_tenant_id | UUID | yes | Same as tenant_id |
| position | Integer | no | Default: 0 |
| is_pinned | Boolean | auto | Default: false |
| last_used_at | DateTime | no | |
| created_at | DateTime | auto | |

#### 5. `sites` table (via event handler after app creation)

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| id | UUID | auto | Primary key |
| app_id | UUID | yes | FK to apps |
| title | String(255) | yes | Set to app.name |
| icon_type | String(255) | no | |
| icon | String(255) | no | |
| icon_background | String(255) | no | |
| description | LongText | no | |
| default_language | String(255) | yes | From account.interface_language |
| chat_color_theme | String(255) | no | |
| chat_color_theme_inverted | Boolean | auto | Default: false |
| copyright | String(255) | no | |
| privacy_policy | String(255) | no | |
| show_workflow_steps | Boolean | auto | Default: true |
| use_icon_as_answer_icon | Boolean | auto | Default: false |
| custom_disclaimer | LongText | no | Max 512 chars |
| customize_domain | String(255) | no | |
| customize_token_strategy | String(255) | yes | Default: 'not_allow' |
| prompt_public | Boolean | auto | Default: false |
| status | String(255) | auto | Default: 'normal' |
| code | String(255) | auto | 16-char random unique code |
| created_by | UUID | no | |
| created_at | DateTime | auto | |
| updated_by | UUID | no | |
| updated_at | DateTime | auto | |

### What Gets Created When Making a New App

| # | Table | Condition |
|---|-------|-----------|
| 1 | `apps` | Always |
| 2 | `app_model_configs` | Only for chat/completion/agent-chat modes |
| 3 | `installed_apps` | Always (via `app_was_created` signal handler) |
| 4 | `sites` | Always when account present (via signal handler) |
| 5 | `workflows` | NOT during create — created later via `WorkflowService.sync_draft_workflow()` |

**Note**: The DSL import path (`AppDslService`) handles workflow creation internally, so importing a DSL YAML creates all necessary records including the workflow.

---

## DSL Format

The DSL is a YAML file used for import/export. This is the **primary interface for programmatic app creation**.

### Top-Level Structure

```yaml
version: "0.6.0"
kind: "app"
app:
  name: "My App"
  mode: "workflow"          # completion|workflow|chat|advanced-chat|agent-chat
  icon: "🤖"
  icon_background: "#FFEAD5"
  description: "Description"
  use_icon_as_answer_icon: false
dependencies: []            # Plugin dependencies
workflow: {}                # For workflow/advanced-chat modes
model_config: {}            # For chat/completion/agent-chat modes
```

### Workflow Section

```yaml
workflow:
  graph:
    nodes: []              # Node list
    edges: []              # Connection list
    viewport:
      x: 0
      y: 0
      zoom: 0.7
  features:
    file_upload: {}
    opening_statement: ''
    retriever_resource:
      enabled: true
    sensitive_word_avoidance:
      enabled: false
    speech_to_text:
      enabled: false
    suggested_questions: []
    suggested_questions_after_answer:
      enabled: false
    text_to_speech:
      enabled: false
  environment_variables: []
  conversation_variables: []
```

### Node Structure

```yaml
- id: "node-id-uuid"
  type: custom
  position:
    x: 80
    y: 282
  sourcePosition: right
  targetPosition: left
  data:
    type: "start"           # Actual node type
    title: "Start"
    desc: ""
    # ... node-type-specific config
```

### Edge Structure

```yaml
- id: "edge-id"
  source: "source-node-id"
  sourceHandle: "source"    # or "true"/"false" for if-else, class_id for classifier
  target: "target-node-id"
  targetHandle: "target"
  data:
    sourceType: start
    targetType: llm
```

### Import Endpoint

- **POST** `/console/api/apps/imports`
- Body: `{"mode": "yaml-content", "yaml_content": "<yaml string>"}`
- Max size: 10MB

### Export Endpoint

- **GET** `/console/api/apps/<app_id>/export`

---

## Workflow Nodes

### Complete Node Type List (37 types)

| # | Type ID | Category | Purpose |
|---|---------|----------|---------|
| 1 | `start` | ROOT | Entry point, defines input variables |
| 2 | `end` | RESPONSE | Terminal node for workflows (output variables) |
| 3 | `answer` | RESPONSE | Streams response in chatflows (template string) |
| 4 | `llm` | EXECUTABLE | LLM text generation |
| 5 | `knowledge-retrieval` | EXECUTABLE | RAG semantic search |
| 6 | `knowledge-index` | EXECUTABLE | Index documents into knowledge base |
| 7 | `if-else` | BRANCH | Conditional branching |
| 8 | `code` | EXECUTABLE | Python3/JavaScript code execution |
| 9 | `template-transform` | EXECUTABLE | Jinja2 template transformation |
| 10 | `question-classifier` | BRANCH | LLM-based query classification |
| 11 | `http-request` | EXECUTABLE | HTTP API calls |
| 12 | `tool` | EXECUTABLE | Built-in/plugin tool invocation |
| 13 | `datasource` | ROOT | External data source connection |
| 14 | `variable-aggregator` | EXECUTABLE | Merge variables from branches |
| 15 | `assigner` | EXECUTABLE | Assign/modify variable values |
| 16 | `iteration` | CONTAINER | Loop over list items |
| 17 | `iteration-start` | VIRTUAL | Start node inside iteration |
| 18 | `loop` | CONTAINER | Loop N times or until condition |
| 19 | `loop-start` | VIRTUAL | Start node inside loop |
| 20 | `loop-end` | VIRTUAL | End node inside loop |
| 21 | `parameter-extractor` | EXECUTABLE | LLM-based structured extraction |
| 22 | `document-extractor` | EXECUTABLE | Extract text from files (PDF, Word) |
| 23 | `list-operator` | EXECUTABLE | Filter/sort/limit lists |
| 24 | `agent` | EXECUTABLE | Agent with tools (ReAct/FC) |
| 25 | `app` | EXECUTABLE | Call another Dify app |
| 26 | `trigger-webhook` | ROOT | Webhook-triggered entry |
| 27 | `trigger-schedule` | ROOT | Cron-scheduled entry |
| 28 | `trigger-plugin` | ROOT | Plugin-triggered entry |
| 29 | `human-input` | EXECUTABLE | Pause for human review/input |
| 30 | `sql-output-chart` | EXECUTABLE | Chart from SQL results |
| 31 | `sql-output-table` | EXECUTABLE | Table from SQL results |
| 32 | `sql-output-summary` | EXECUTABLE | LLM summary of SQL results |
| 33 | `vannaai-question` | EXECUTABLE | Natural language → SQL |
| 34 | `vannaai-training` | EXECUTABLE | Train Vanna.AI model |
| 35 | `vannaai-connector` | EXECUTABLE | Database connection for Vanna |
| 36 | `cache-retrieve` | EXECUTABLE | Get cached values |
| 37 | `cache-store` | EXECUTABLE | Store values in cache |
| 38 | `explainer` | EXECUTABLE | Generate explanations |
| 39 | `filtered-knowledge-retrieval` | EXECUTABLE | Knowledge retrieval with filters |
| 40 | `summarizer` | EXECUTABLE | Summarize text |

### Key Node Configurations

#### Start Node
```yaml
data:
  type: start
  title: "Start"
  variables:
    - variable: query
      label: query
      type: text-input      # text-input|paragraph|select|number
      required: true
      max_length: null
      options: []
```

#### LLM Node
```yaml
data:
  type: llm
  title: "LLM"
  model:
    provider: openai
    name: gpt-4o
    mode: chat
    completion_params:
      temperature: 0.7
  prompt_template:
    - role: system
      text: "You are a helpful assistant."
    - role: user
      text: '{{#start.query#}}'
  memory:
    enabled: false
  context:
    enabled: false
  vision:
    enabled: false
  structured_output:
    enabled: false
```

#### End Node (workflow mode)
```yaml
data:
  type: end
  title: "End"
  outputs:
    - variable: answer
      value_type: string
      value_selector:
        - llm_node_id
        - text
```

#### Answer Node (chatflow mode)
```yaml
data:
  type: answer
  title: "Answer"
  answer: '{{#llm.text#}}'
```

#### If-Else Node
```yaml
data:
  type: if-else
  title: "IF/ELSE"
  cases:
    - case_id: "case1"
      conditions:
        - variable_selector: [start, query]
          comparison_operator: contains
          value: "hello"
  # Edge source_handle uses case_id for true branches, "false" for else
```

#### HTTP Request Node
```yaml
data:
  type: http-request
  title: "HTTP Request"
  method: GET
  url: "https://api.example.com/data"
  headers: "Content-Type: application/json"
  params: ""
  body:
    type: json
    data: '{"key": "value"}'
  authorization:
    type: api-key
    config:
      type: bearer
      api_key: "{{#env.API_KEY#}}"
  timeout:
    connect: 10
    read: 60
    write: 10
```

#### Code Node
```yaml
data:
  type: code
  title: "Code"
  variables:
    - variable: input_text
      value_selector: [start, query]
  code_language: python3
  code: |
    def main(input_text: str) -> dict:
        return {"result": input_text.upper()}
  outputs:
    result:
      type: string
```

#### Knowledge Retrieval Node
```yaml
data:
  type: knowledge-retrieval
  title: "Knowledge Retrieval"
  query_variable_selector: [start, query]
  dataset_ids:
    - "dataset-uuid-1"
  retrieval_mode: multiple
  multiple_retrieval_config:
    top_k: 3
    score_threshold: 0.5
    reranking_model:
      provider: ""
      model: ""
```

#### Iteration Node
```yaml
data:
  type: iteration
  title: "Iteration"
  iterator_selector: [code_node, list_output]
  output_selector: [llm_inside, text]
  is_parallel: false
  parallel_nums: 10
  error_handle_mode: CONTINUE_ON_ERROR
```

---

## App Creation Flow

### Via API (Programmatic)

```python
# 1. Create app
POST /console/api/apps
{
    "name": "My App",
    "mode": "workflow",
    "icon": "🤖",
    "icon_background": "#FFEAD5",
    "description": "..."
}

# 2. For workflow apps, sync draft workflow
POST /console/api/apps/<app_id>/workflows/draft
{
    "graph": {"nodes": [...], "edges": [...]},
    "features": {...},
    "environment_variables": [...],
    "conversation_variables": [...]
}
```

### Via DSL Import (Recommended for Skills)

```python
# Single-step: import complete app from YAML
POST /console/api/apps/imports
{
    "mode": "yaml-content",
    "yaml_content": "<full DSL YAML>"
}
```

### Internal Flow (`AppService.create_app`)

1. Determine mode from args
2. Get default model config from template
3. Create `App` row with metadata
4. If non-workflow mode: create `AppModelConfig` row
5. Commit to database
6. Fire `app_was_created` signal

### For Workflow Apps After Creation

The `WorkflowService.sync_draft_workflow()` method:
1. Gets or creates draft workflow for the app
2. Updates graph (nodes + edges), features, env vars, conversation vars
3. Validates the graph structure

---

## Skills Architecture Plan

### Approach: Structured Markdown Knowledge Injection

Following the [n8n-skills](https://github.com/czlonkowski/n8n-skills) pattern:
- Skills are pure markdown documents teaching the LLM HOW to generate valid Dify DSL
- Hooks enforce skill consultation at the right moments
- Evaluations validate correctness

### Proposed Skill Structure

```
dify-skills/
├── skills/
│   ├── using-dify-skills/           # ROUTER SKILL (always loaded)
│   │   └── SKILL.md
│   ├── dify-dsl-expert/             # DSL format, validation, structure
│   │   ├── SKILL.md
│   │   ├── DSL_STRUCTURE.md
│   │   └── VALIDATION_RULES.md
│   ├── dify-node-catalog/           # All node types + configurations
│   │   ├── SKILL.md
│   │   ├── CORE_NODES.md            # start, end, answer, llm
│   │   ├── LOGIC_NODES.md           # if-else, code, template, iteration
│   │   ├── DATA_NODES.md            # knowledge, http, tool, datasource
│   │   └── ADVANCED_NODES.md        # agent, parameter-extractor, etc.
│   ├── dify-workflow-patterns/      # Common workflow archetypes
│   │   ├── SKILL.md
│   │   ├── simple_chatbot.md
│   │   ├── rag_chatbot.md
│   │   ├── text_generation.md
│   │   ├── agent_with_tools.md
│   │   ├── data_processing.md
│   │   └── api_orchestration.md
│   ├── dify-variable-system/        # Variable passing between nodes
│   │   ├── SKILL.md
│   │   └── SELECTOR_SYNTAX.md
│   ├── dify-app-debugger/           # DSL debugging and troubleshooting
│   │   ├── SKILL.md
│   │   └── COMMON_ERRORS.md
│   └── dify-import-export/          # Import/export mechanics
│       └── SKILL.md
├── hooks/
│   ├── hooks.json
│   ├── session-start.sh             # Load router skill
│   └── pre-tool-use/
│       └── generate-dsl.sh          # Enforce validation before output
├── evaluations/
│   ├── workflow-patterns/
│   │   ├── eval-001-simple-chatbot.json
│   │   ├── eval-002-rag-workflow.json
│   │   ├── eval-003-agent-app.json
│   │   └── eval-004-data-pipeline.json
│   └── node-configuration/
│       ├── eval-001-llm-node.json
│       └── eval-002-code-node.json
├── templates/                       # Complete DSL YAML templates
│   ├── simple-workflow.yml
│   ├── rag-chatbot.yml
│   ├── agent-chat.yml
│   └── advanced-chatflow.yml
└── README.md
```

### Skill Responsibilities

| Skill | When Invoked | What It Does |
|-------|-------------|--------------|
| `using-dify-skills` | Always (session start) | Routes to specialist skills, non-negotiable rules |
| `dify-dsl-expert` | Generating/validating YAML | DSL structure, version, required fields |
| `dify-node-catalog` | Configuring specific nodes | Correct config for each node type |
| `dify-workflow-patterns` | "Build me a workflow for X" | Architecture patterns with examples |
| `dify-variable-system` | Connecting nodes | `{{#node_id.output#}}` syntax, selectors |
| `dify-app-debugger` | "Why isn't my app working?" | Parse DSL, find issues, suggest fixes |
| `dify-import-export` | Deploying generated apps | API calls, dependency handling |

### Key Design Decisions

1. **DSL-first approach**: Generate YAML DSL → import via API (not direct DB manipulation)
2. **Template-based generation**: Start from working templates, modify for user requirements
3. **Validation before output**: Every generated DSL must pass structural validation
4. **Progressive complexity**: Simple patterns first, compose for complex workflows

### Implementation Phases

#### Phase 1: Core Foundation
- Router skill + DSL expert + basic node catalog
- 3 workflow templates (simple workflow, chatbot, RAG)
- Basic variable system documentation

#### Phase 2: Pattern Library
- All workflow patterns with complete examples
- Advanced node configurations
- Evaluation scenarios

#### Phase 3: Debugging & Import
- App debugger skill for troubleshooting DSL issues
- Import/export skill with API integration
- Error catalog with fixes

#### Phase 4: Hooks & Automation
- Session start hook to load router
- Pre-generation validation hooks
- Post-generation testing hooks

---

## Variable Selector Syntax

Nodes reference outputs from other nodes using variable selectors:

```
{{#node_id.output_field#}}          # In template strings (answer, llm prompt)
[node_id, output_field]             # In JSON selector arrays (value_selector)
```

### Common Output Fields by Node Type

| Node Type | Output Fields |
|-----------|--------------|
| start | User-defined variable names |
| llm | `text`, `usage` |
| code | User-defined in `outputs` dict |
| knowledge-retrieval | `result` (array of documents) |
| http-request | `body`, `status_code`, `headers` |
| tool | Tool-specific outputs |
| template-transform | `output` |
| if-else | Pass-through (no new outputs) |
| iteration | Collected outputs from inner nodes |
| parameter-extractor | Extracted parameter names |
| document-extractor | `text` |

### System Variables

Available in all nodes via `sys.*`:
- `sys.query` — User query (chatflows)
- `sys.files` — Uploaded files
- `sys.conversation_id` — Conversation ID
- `sys.user_id` — User ID

---

## Key Source Files

| File | Purpose |
|------|---------|
| `api/services/app_dsl_service.py` | DSL import/export logic |
| `api/services/app_service.py` | App CRUD operations |
| `api/services/workflow_service.py` | Workflow sync/publish |
| `api/models/model.py` | App, AppModelConfig models |
| `api/models/workflow.py` | Workflow model |
| `api/core/workflow/nodes/` | All node implementations |
| `api/core/workflow/enums.py` | NodeType enum |
| `api/controllers/console/app/app_import.py` | Import endpoints |
| `api/controllers/console/app/app.py` | Export endpoint |

---

## DSL Debugging Guide

### Common Issues

1. **Missing node connections**: Every node (except start/triggers) needs incoming edge
2. **Invalid variable selectors**: Referenced node ID must exist in graph
3. **Wrong terminal node**: Workflow mode uses `end`, chatflow uses `answer`
4. **Version mismatch**: Use `version: "0.6.0"` for current compatibility
5. **Missing dependencies**: Plugin tools need explicit dependency declarations

### Validation Checklist

- [ ] `version` and `kind` present
- [ ] `app.mode` matches workflow structure
- [ ] Start node exists with correct variables
- [ ] All nodes have unique IDs
- [ ] All edges reference existing node IDs
- [ ] Terminal node matches mode (end vs answer)
- [ ] Variable selectors reference valid node outputs
- [ ] LLM nodes have valid model provider/name
- [ ] No orphan nodes (unreachable from start)
