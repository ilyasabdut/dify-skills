# Data Nodes

Nodes for retrieving, fetching, and processing external data.

---

## Knowledge Retrieval Node (`knowledge-retrieval`)

Retrieves relevant documents from knowledge bases using semantic search.

### Minimal Config
```yaml
data:
  type: knowledge-retrieval
  title: Knowledge Retrieval
  query_variable_selector:
    - sys
    - query
  dataset_ids:
    - "DATASET_ID_PLACEHOLDER"
  retrieval_mode: multiple
```

### Full Config
```yaml
data:
  type: knowledge-retrieval
  title: Knowledge Retrieval
  desc: ""
  query_variable_selector:     # What to search for
    - sys
    - query
  dataset_ids:                  # Knowledge base IDs to search
    - "dataset-uuid-1"
    - "dataset-uuid-2"
  retrieval_mode: multiple      # single or multiple
  multiple_retrieval_config:    # When retrieval_mode = multiple
    top_k: 3                   # Number of results
    score_threshold: 0.5       # Minimum relevance (0-1)
    reranking_enable: false
    reranking_model:
      provider: ""
      model: ""
    weights:
      weight_type: customized
      vector_setting:
        vector_weight: 0.7
        embedding_provider_name: ""
        embedding_model_name: ""
      keyword_setting:
        keyword_weight: 0.3
  single_retrieval_config:      # When retrieval_mode = single
    model:
      provider: openai
      name: gpt-4o-mini
      mode: chat
      completion_params:
        temperature: 0.7
```

### Outputs
| Output | Type | Description |
|--------|------|-------------|
| `result` | array | Array of retrieved document chunks |

### Gotchas
- `dataset_ids` must be real UUIDs from your Dify instance — use placeholders in templates
- `query_variable_selector` uses `[sys, query]` for chatflow user messages
- In workflows, point to start variable: `[start, query]`
- `multiple` mode returns top_k results from ALL datasets combined
- `single` mode uses an LLM to pick the best single result

---

## HTTP Request Node (`http-request`)

Makes HTTP API calls to external services.

### Minimal Config
```yaml
data:
  type: http-request
  title: HTTP Request
  method: GET
  url: "https://api.example.com/data"
  headers: ""
  params: ""
  body: null
  authorization:
    type: no-auth
  timeout:
    connect: 10
    read: 60
    write: 10
```

### Full Config
```yaml
data:
  type: http-request
  title: HTTP Request
  desc: ""
  method: GET                   # GET|POST|PUT|DELETE|PATCH|HEAD
  url: "https://api.example.com/{{#start.endpoint#}}"
  headers: |
    Content-Type: application/json
    X-Custom-Header: {{#start.token#}}
  params: |
    page=1
    limit=10
  body:                         # For POST/PUT/PATCH
    type: json                  # none|form-data|x-www-form-urlencoded|raw-text|json|binary
    data: |
      {
        "query": "{{#start.query#}}",
        "limit": 10
      }
  authorization:
    type: api-key               # no-auth|api-key|custom
    config:
      type: bearer              # bearer|basic|custom
      api_key: "{{#env.API_KEY#}}"
      header: "Authorization"   # Custom header name
  timeout:
    connect: 10                 # Connection timeout (seconds)
    read: 60                    # Read timeout
    write: 10                   # Write timeout
  ssl_verify: true
  retry_config:
    enabled: false
    max_retries: 3
    retry_interval: 1000
```

### Outputs
| Output | Type | Description |
|--------|------|-------------|
| `body` | string | Response body |
| `status_code` | number | HTTP status code |
| `headers` | object | Response headers |

### Authorization Types
| Type | Config |
|------|--------|
| `no-auth` | No config needed |
| `api-key` | `config.type` (bearer/basic/custom), `config.api_key` |
| `custom` | Custom header/value |

### Body Types
| Type | Use Case |
|------|----------|
| `json` | JSON APIs (most common) |
| `form-data` | File uploads, multipart forms |
| `x-www-form-urlencoded` | Simple form data |
| `raw-text` | Plain text body |
| `binary` | Binary file data |
| `none` | GET/DELETE (no body) |

### Gotchas
- Variable references work in URL, headers, params, and body
- Use `{{#env.API_KEY#}}` for sensitive values (environment variables)
- Headers are newline-separated key:value pairs (not JSON)
- Params are newline-separated key=value pairs
- Response `body` is always a string — use a code node to parse JSON

---

## Tool Node (`tool`)

Invokes a built-in or plugin tool.

### Config
```yaml
data:
  type: tool
  title: Google Search
  provider_id: google
  provider_type: builtin        # builtin|api|workflow
  provider_name: google
  tool_name: google_search
  tool_label: Google Search
  tool_configurations:
    result_type: link
  tool_parameters:
    query:
      type: variable            # variable|constant|mixed
      value:
        - start
        - query
```

### Outputs
- Tool-specific — varies per tool
- Common: `text` (string result), `json` (structured result), `files` (file outputs)

### Gotchas
- `provider_id` and `tool_name` must match what's installed in your Dify instance
- `credential_id` is stripped on export — tools need re-authorization on import
- Plugin tools need a `plugin_unique_identifier` field

---

## Datasource Node (`datasource`)

Connects to external data sources (databases, APIs via plugins).

### Config
```yaml
data:
  type: datasource
  title: Database Query
  datasource_provider_id: "provider-id"
  datasource_provider_name: "postgres"
  datasource_name: "query"
  datasource_label: "PostgreSQL Query"
  datasource_parameters:
    query:
      type: variable
      value:
        - start
        - sql_query
  datasource_configurations:
    host: "localhost"
    port: 5432
    database: "mydb"
  plugin_unique_identifier: "org/postgres-plugin/1.0.0"
```

### Gotchas
- Datasource nodes can serve as workflow entry points (ROOT category)
- Configuration depends entirely on the specific datasource plugin
- Credentials are handled via `datasource_configurations`

---

## Document Extractor Node (`document-extractor`)

Extracts text content from uploaded files (PDF, Word, TXT, etc.)

### Config
```yaml
data:
  type: document-extractor
  title: Document Extractor
  variable_selector:
    - start
    - files
```

### Outputs
| Output | Type | Description |
|--------|------|-------------|
| `text` | string | Extracted text content |

### Supported Formats
PDF, DOCX, DOC, TXT, MD, HTML, XLSX, XLS, CSV, EPUB

### Gotchas
- Input must be a file or file-list variable
- For chatflows, files come from `sys.files`
- For workflows, files come from start variables with `type: file` or `type: file-list`
- Large files may be truncated — check your instance limits
