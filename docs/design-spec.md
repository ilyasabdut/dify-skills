# Dify Skills — Detailed Design Spec

> Claude Code skills for LLM-powered Dify app generation and debugging

## 1. Goals

1. **Generate valid Dify apps** — LLM takes a natural language description → produces import-ready DSL YAML
2. **Debug existing apps** — Parse DSL YAML, identify issues, suggest fixes
3. **Teach patterns** — Provide architectural guidance for common workflow designs

## 2. Architecture Overview

```
User: "Build me a RAG chatbot that searches my docs and answers questions"
         │
         ▼
┌─────────────────────────┐
│  Router Skill            │  ← Always loaded at session start
│  (using-dify-skills)     │
└────────┬────────────────┘
         │ Routes to specialist
         ▼
┌─────────────────────────┐     ┌──────────────────────┐
│  Workflow Patterns Skill │────▶│  Node Catalog Skill  │
│  (selects archetype)     │     │  (correct configs)   │
└────────┬────────────────┘     └──────────┬───────────┘
         │                                  │
         ▼                                  ▼
┌─────────────────────────┐     ┌──────────────────────┐
│  DSL Expert Skill        │◀───│  Variable System     │
│  (assembles valid YAML)  │     │  (wires nodes)       │
└────────┬────────────────┘     └──────────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Output: Valid DSL YAML  │──▶ Import via API or save to file
└─────────────────────────┘
```

## 3. Skill Definitions

### 3.1 Router Skill: `using-dify-skills`

**Loaded**: Always (session-start hook)

**Purpose**: Dispatch user intent to the right specialist skill.

**Contents**:
- Routing table (intent → skill)
- Non-negotiable rules (always validate, always include version)
- Quick-reference of what each skill does
- Protocol: understand → select pattern → configure nodes → assemble DSL → validate

**Routing Table**:

| User Intent | Route To |
|------------|----------|
| "Build/create a workflow/chatbot/app" | `dify-workflow-patterns` |
| "Configure/set up a [node type]" | `dify-node-catalog` |
| "Why isn't my app working?" / "Debug this DSL" | `dify-app-debugger` |
| "How do I pass data between nodes?" | `dify-variable-system` |
| "Import/export/deploy this app" | `dify-import-export` |
| "What's the DSL format?" | `dify-dsl-expert` |

**Non-Negotiable Rules**:
1. Every generated DSL MUST include `version: "0.6.0"` and `kind: "app"`
2. Every workflow MUST have exactly one start node
3. Workflow mode uses `end` node; chatflow mode uses `answer` node
4. All node IDs must be unique UUIDs or descriptive slugs
5. All edges must reference existing node IDs
6. Variable selectors must reference valid upstream node outputs
7. ALWAYS validate structure before presenting to user

---

### 3.2 DSL Expert: `dify-dsl-expert`

**Loaded**: When generating or validating DSL YAML

**Purpose**: Knows the exact DSL structure, validates output, handles versioning.

**Reference Files**:
- `DSL_STRUCTURE.md` — Complete field reference with types and defaults
- `VALIDATION_RULES.md` — Structural checks, common mistakes, fix patterns

**Key Knowledge**:

```yaml
# Required top-level structure
version: "0.6.0"
kind: "app"
app:
  name: string (required)
  mode: string (required) # completion|workflow|chat|advanced-chat|agent-chat
  icon: string (required)
  icon_background: string (required)
  description: string (optional, default "")
  use_icon_as_answer_icon: bool (optional, default false)
dependencies: [] # Auto-extracted if empty
workflow: {}     # Required for workflow|advanced-chat
model_config: {} # Required for completion|chat|agent-chat
```

**Validation Checklist** (enforced before output):
1. YAML parses without errors
2. Required fields present
3. Mode matches structure (workflow section vs model_config section)
4. Graph has exactly one root node (start/trigger)
5. All nodes reachable from root
6. No orphan nodes
7. Terminal nodes match mode (end vs answer)
8. All variable selectors resolve to existing nodes
9. LLM nodes have valid provider/name (use placeholder if unknown)
10. Edge source_handles are valid for node type

---

### 3.3 Node Catalog: `dify-node-catalog`

**Loaded**: When configuring specific node types

**Purpose**: Exact configuration schema for each of the 40 node types.

**Reference Files**:
- `CORE_NODES.md` — start, end, answer, llm (most common)
- `LOGIC_NODES.md` — if-else, code, template-transform, iteration, loop, list-operator
- `DATA_NODES.md` — knowledge-retrieval, http-request, tool, datasource, document-extractor
- `ADVANCED_NODES.md` — agent, parameter-extractor, question-classifier, human-input
- `SQL_NODES.md` — vannaai-*, sql-output-*, cache-*

**Per-Node Documentation Format**:
```markdown
## Node: `llm`

### Minimal Config
(smallest valid configuration)

### Full Config
(all fields with defaults shown)

### Common Patterns
(2-3 real-world usage examples)

### Gotchas
- Memory only works in chatflow mode
- Vision requires model that supports it
- structured_output requires function-calling-capable model

### Outputs
- `text` (string) — Generated text
- `usage` (object) — Token usage stats
```

---

### 3.4 Workflow Patterns: `dify-workflow-patterns`

**Loaded**: When user asks to build/create an app

**Purpose**: Architectural templates for common use cases.

**Pattern Files**:

#### `simple_chatbot.md`
- Mode: `advanced-chat`
- Nodes: start → llm → answer
- Use case: Basic conversational AI
- Variations: with memory, with system prompt customization

#### `rag_chatbot.md`
- Mode: `advanced-chat`
- Nodes: start → knowledge-retrieval → llm → answer
- Use case: Q&A over documents
- Variations: single vs multiple knowledge bases, with reranking

#### `text_generation.md`
- Mode: `workflow`
- Nodes: start → llm → end
- Use case: Single-shot text generation (summarize, translate, extract)
- Variations: with template-transform pre-processing

#### `agent_with_tools.md`
- Mode: `agent-chat` or `advanced-chat` with agent node
- Nodes: start → agent → answer
- Use case: Autonomous agent with tool access
- Variations: different strategies (ReAct vs FC)

#### `data_processing_pipeline.md`
- Mode: `workflow`
- Nodes: start → http-request → code → iteration(llm) → end
- Use case: Fetch data, transform, process each item with LLM
- Variations: with error handling, with caching

#### `api_orchestration.md`
- Mode: `workflow`
- Nodes: start → http-request → if-else → [branch A / branch B] → variable-aggregator → end
- Use case: Call APIs, route based on response, merge results
- Variations: parallel branches, retry logic

#### `document_analysis.md`
- Mode: `workflow`
- Nodes: start → document-extractor → llm → end
- Use case: Upload file, extract text, analyze with LLM
- Variations: with knowledge base lookup for context

#### `conditional_routing.md`
- Mode: `advanced-chat`
- Nodes: start → question-classifier → [branch per class] → answer
- Use case: Route queries to different handlers based on intent
- Variations: with if-else instead of classifier

**Pattern Selection Guide** (in SKILL.md):
```
User wants...                    → Use pattern
─────────────────────────────────────────────────
Simple Q&A                       → simple_chatbot
Q&A over documents               → rag_chatbot
One-shot text task               → text_generation
Agent with tools                 → agent_with_tools
Process list of items            → data_processing_pipeline
Call external APIs               → api_orchestration
Analyze uploaded files           → document_analysis
Route queries to handlers        → conditional_routing
```

---

### 3.5 Variable System: `dify-variable-system`

**Loaded**: When wiring nodes together or debugging variable references

**Purpose**: How to reference outputs from upstream nodes.

**Key Concepts**:

```markdown
## Selector Syntax

### In template strings (answer node, llm prompts):
{{#node_id.output_field#}}

### In JSON config (value_selector arrays):
["node_id", "output_field"]

## Addressing Rules
- node_id = the `id` field of the source node
- output_field = specific output name from that node type
- For start node: output_field = variable name defined in start.variables
- For iteration: use "item" to reference current iteration item

## System Variables (available everywhere in chatflows):
- sys.query — current user message
- sys.files — uploaded files array
- sys.conversation_id
- sys.user_id

## Environment Variables:
- env.VARIABLE_NAME — references workflow environment variables

## Common Output Fields by Node:
| Node | Outputs |
|------|---------|
| llm | text, usage |
| code | (user-defined in outputs dict) |
| knowledge-retrieval | result (array) |
| http-request | body, status_code, headers |
| template-transform | output |
| parameter-extractor | (extracted param names) |
| document-extractor | text |
| iteration | (collected from output_selector) |
```

---

### 3.6 App Debugger: `dify-app-debugger`

**Loaded**: When user has a broken DSL or app that doesn't work

**Purpose**: Parse DSL, identify structural/logical issues, suggest fixes.

**Reference Files**:
- `COMMON_ERRORS.md` — Error catalog with symptoms and fixes
- `DEBUG_PROTOCOL.md` — Step-by-step debugging approach

**Debug Protocol**:
1. Parse YAML — check for syntax errors
2. Validate structure — run checklist from DSL Expert
3. Check connectivity — ensure all nodes reachable
4. Verify variable references — all selectors resolve
5. Check node configs — required fields present per node type
6. Check mode consistency — end vs answer, workflow vs chat type
7. Check edge handles — if-else has true/false, classifier has class IDs

**Error Catalog** (examples):

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| "Node X not found" | Variable selector references non-existent node | Check node ID spelling |
| App runs but produces empty output | End node outputs have wrong value_selector | Verify selector path |
| "Invalid graph" on import | Orphan nodes or missing edges | Connect all nodes to graph |
| LLM node fails | Invalid model provider/name | Check available models |
| Iteration produces nothing | output_selector points to wrong inner node | Fix to inner node's output |

---

### 3.7 Import/Export: `dify-import-export`

**Loaded**: When deploying generated apps

**Purpose**: API mechanics for getting DSL into a running Dify instance.

**Key Endpoints**:
```markdown
## Import
POST /console/api/apps/imports
Content-Type: application/json
Authorization: Bearer <console_token>

{"mode": "yaml-content", "yaml_content": "<YAML string>"}

## Export  
GET /console/api/apps/<app_id>/export?include_secret=false
Authorization: Bearer <console_token>

## Check Dependencies
GET /console/api/apps/imports/<app_id>/check-dependencies

## Confirm Import (if version mismatch)
POST /console/api/apps/imports/<import_id>/confirm
```

---

## 4. Templates Directory

Complete, tested DSL YAML files for each pattern. These are the "golden examples" the LLM starts from.

### `templates/simple-workflow.yml`
```yaml
version: "0.6.0"
kind: "app"
app:
  name: "Simple Text Generator"
  mode: "workflow"
  icon: "✨"
  icon_background: "#E4FBCC"
  description: "Generate text from a prompt"
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
            - variable: query
              label: Query
              type: text-input
              required: true
              max_length: 2000
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
              text: "You are a helpful assistant."
            - role: user
              text: "{{#start.query#}}"
          memory:
            enabled: false
          context:
            enabled: false
          vision:
            enabled: false
      - id: "end"
        type: custom
        position: {x: 680, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: end
          title: End
          outputs:
            - variable: result
              value_type: string
              value_selector:
                - llm
                - text
    edges:
      - id: "start-llm"
        source: "start"
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
      enabled: false
  environment_variables: []
  conversation_variables: []
```

### `templates/rag-chatbot.yml`
```yaml
version: "0.6.0"
kind: "app"
app:
  name: "RAG Chatbot"
  mode: "advanced-chat"
  icon: "📚"
  icon_background: "#D5F5F6"
  description: "Chat with your documents"
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
      - id: "knowledge"
        type: custom
        position: {x: 380, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: knowledge-retrieval
          title: Knowledge Retrieval
          query_variable_selector:
            - sys
            - query
          dataset_ids:
            - "DATASET_ID_PLACEHOLDER"
          retrieval_mode: multiple
          multiple_retrieval_config:
            top_k: 3
            score_threshold: 0.5
            reranking_enable: false
      - id: "llm"
        type: custom
        position: {x: 680, y: 282}
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
              text: |
                Answer the user's question based on the following context.
                If the context doesn't contain relevant information, say so.
                
                Context:
                {{#knowledge.result#}}
            - role: user
              text: "{{#sys.query#}}"
          memory:
            enabled: true
            window:
              enabled: true
              size: 10
          context:
            enabled: true
            variable_selector:
              - knowledge
              - result
          vision:
            enabled: false
      - id: "answer"
        type: custom
        position: {x: 980, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: answer
          title: Answer
          answer: "{{#llm.text#}}"
    edges:
      - id: "start-knowledge"
        source: "start"
        sourceHandle: "source"
        target: "knowledge"
        targetHandle: "target"
      - id: "knowledge-llm"
        source: "knowledge"
        sourceHandle: "source"
        target: "llm"
        targetHandle: "target"
      - id: "llm-answer"
        source: "llm"
        sourceHandle: "source"
        target: "answer"
        targetHandle: "target"
  features:
    retriever_resource:
      enabled: true
    opening_statement: "Hello! Ask me anything about your documents."
    suggested_questions:
      - "What is this document about?"
      - "Summarize the key points"
  environment_variables: []
  conversation_variables: []
```

---

## 5. Hooks Configuration

### `hooks/hooks.json`
```json
{
  "hooks": [
    {
      "type": "SessionStart",
      "script": "hooks/session-start.sh"
    },
    {
      "type": "PreToolUse",
      "matcher": "Write",
      "script": "hooks/pre-tool-use/validate-dsl.sh"
    }
  ]
}
```

### `hooks/session-start.sh`
```bash
#!/bin/bash
# Inject router skill context at session start
echo '{"continue": true, "suppressOutput": true}'
# The router skill is loaded via the skill system automatically
```

### `hooks/pre-tool-use/validate-dsl.sh`
```bash
#!/bin/bash
# Before writing a .yml file that looks like a DSL, remind about validation
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""')

if [[ "$FILE_PATH" == *.yml ]] || [[ "$FILE_PATH" == *.yaml ]]; then
  echo '{"continue": true, "message": "REMINDER: Validate DSL structure before writing. Check: version field, mode matches structure, all nodes connected, variable selectors resolve."}'
else
  echo '{"continue": true}'
fi
```

---

## 6. Evaluations

### `evaluations/workflow-patterns/eval-001-simple-chatbot.json`
```json
{
  "id": "pattern-001",
  "skills": ["dify-workflow-patterns", "dify-dsl-expert"],
  "query": "Build me a simple chatbot that helps users write emails",
  "expected_behavior": [
    "Identifies this as simple_chatbot pattern",
    "Uses advanced-chat mode",
    "Creates start → llm → answer structure",
    "Sets appropriate system prompt for email writing",
    "Enables memory for conversation context",
    "Produces valid DSL YAML with version 0.6.0",
    "All variable selectors resolve correctly"
  ]
}
```

### `evaluations/workflow-patterns/eval-002-rag-workflow.json`
```json
{
  "id": "pattern-002",
  "skills": ["dify-workflow-patterns", "dify-node-catalog"],
  "query": "I need a workflow that searches my knowledge base and summarizes the results",
  "expected_behavior": [
    "Identifies this as rag_chatbot or text_generation+knowledge pattern",
    "Includes knowledge-retrieval node with placeholder dataset_ids",
    "LLM node references knowledge retrieval output in context",
    "Uses correct variable selector syntax",
    "Notes that dataset_ids need to be filled with actual IDs"
  ]
}
```

### `evaluations/debugging/eval-001-broken-selectors.json`
```json
{
  "id": "debug-001",
  "skills": ["dify-app-debugger"],
  "query": "Why does this workflow fail? [provides DSL with typo in node ID reference]",
  "expected_behavior": [
    "Parses the YAML successfully",
    "Identifies the broken variable selector",
    "Shows which node ID is referenced vs which exist",
    "Suggests the correct node ID",
    "Provides fixed YAML"
  ]
}
```

---

## 7. Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Router skill (`using-dify-skills/SKILL.md`)
- [ ] DSL Expert skill with validation rules
- [ ] Node Catalog: core nodes only (start, end, answer, llm)
- [ ] 2 templates: simple-workflow.yml, simple-chatbot.yml (advanced-chat)
- [ ] Basic session-start hook

**Deliverable**: LLM can generate valid simple workflow and chatbot DSL

### Phase 2: Patterns (Week 2)
- [ ] Workflow Patterns skill with 4 patterns (chatbot, RAG, text-gen, data-pipeline)
- [ ] Node Catalog: logic nodes (if-else, code, template-transform, iteration)
- [ ] Node Catalog: data nodes (knowledge-retrieval, http-request)
- [ ] Variable System skill
- [ ] 2 more templates: rag-chatbot.yml, data-pipeline.yml

**Deliverable**: LLM can generate multi-node workflows with branching and data retrieval

### Phase 3: Advanced & Debugging (Week 3)
- [ ] Node Catalog: advanced nodes (agent, parameter-extractor, question-classifier)
- [ ] App Debugger skill with error catalog
- [ ] Remaining patterns (agent, api-orchestration, conditional-routing)
- [ ] Import/Export skill
- [ ] Pre-write validation hook

**Deliverable**: Full pattern coverage + debugging capability

### Phase 4: Polish & Evaluation (Week 4)
- [ ] Complete evaluation scenarios (10+ per skill)
- [ ] Refine skills based on eval results
- [ ] Add remaining node types to catalog
- [ ] Documentation and README
- [ ] Package for distribution

**Deliverable**: Production-ready skill set with evaluation coverage

---

## 8. File Structure

```
dify-skills/
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── skills/
│   ├── using-dify-skills/
│   │   └── SKILL.md
│   ├── dify-dsl-expert/
│   │   ├── SKILL.md
│   │   ├── DSL_STRUCTURE.md
│   │   └── VALIDATION_RULES.md
│   ├── dify-node-catalog/
│   │   ├── SKILL.md
│   │   ├── CORE_NODES.md
│   │   ├── LOGIC_NODES.md
│   │   ├── DATA_NODES.md
│   │   ├── ADVANCED_NODES.md
│   │   └── SQL_NODES.md
│   ├── dify-workflow-patterns/
│   │   ├── SKILL.md
│   │   ├── simple_chatbot.md
│   │   ├── rag_chatbot.md
│   │   ├── text_generation.md
│   │   ├── agent_with_tools.md
│   │   ├── data_processing_pipeline.md
│   │   ├── api_orchestration.md
│   │   ├── document_analysis.md
│   │   └── conditional_routing.md
│   ├── dify-variable-system/
│   │   ├── SKILL.md
│   │   └── SELECTOR_SYNTAX.md
│   ├── dify-app-debugger/
│   │   ├── SKILL.md
│   │   ├── COMMON_ERRORS.md
│   │   └── DEBUG_PROTOCOL.md
│   └── dify-import-export/
│       └── SKILL.md
├── hooks/
│   ├── hooks.json
│   ├── session-start.sh
│   └── pre-tool-use/
│       └── validate-dsl.sh
├── evaluations/
│   ├── workflow-patterns/
│   │   ├── eval-001-simple-chatbot.json
│   │   ├── eval-002-rag-workflow.json
│   │   ├── eval-003-agent-app.json
│   │   ├── eval-004-data-pipeline.json
│   │   └── eval-005-api-orchestration.json
│   ├── node-configuration/
│   │   ├── eval-001-llm-node.json
│   │   ├── eval-002-code-node.json
│   │   └── eval-003-http-node.json
│   ├── debugging/
│   │   ├── eval-001-broken-selectors.json
│   │   ├── eval-002-orphan-nodes.json
│   │   └── eval-003-wrong-terminal.json
│   └── variable-system/
│       └── eval-001-cross-node-refs.json
├── templates/
│   ├── simple-workflow.yml
│   ├── simple-chatbot.yml
│   ├── rag-chatbot.yml
│   ├── data-pipeline.yml
│   ├── agent-chat.yml
│   └── api-orchestration.yml
├── CLAUDE.md
└── README.md
```

---

## 9. Success Criteria

| Metric | Target |
|--------|--------|
| Generated DSL passes import without errors | 95%+ |
| Correct mode/terminal node pairing | 100% |
| Variable selectors resolve correctly | 95%+ |
| Pattern selection matches user intent | 90%+ |
| Debugger identifies root cause | 85%+ |
| Evaluation pass rate | 80%+ across all scenarios |

---

## 10. Open Questions

1. **Model placeholders**: Should skills use a generic `{{MODEL_PROVIDER}}`/`{{MODEL_NAME}}` placeholder or default to `openai/gpt-4o-mini`?
   - Recommendation: Default to a common model, note in comments that user should change

2. **Dataset IDs**: Knowledge retrieval nodes need real dataset UUIDs. Skills should:
   - Use `DATASET_ID_PLACEHOLDER` and instruct user to replace
   - Or query the Dify API to list available datasets

3. **Plugin dependencies**: Should skills auto-detect which plugins are needed?
   - Recommendation: Yes, based on model provider and tool usage in the graph

4. **Scope of node catalog**: Include all 40 nodes in Phase 1 or progressive?
   - Recommendation: Progressive — core nodes first, expand based on usage

5. **Distribution**: Claude Code plugin marketplace or git-based installation?
   - Recommendation: Start as git repo (like n8n-skills), consider marketplace later
