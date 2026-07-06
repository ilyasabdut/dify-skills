# SQL & Cache Nodes

Nodes for database queries, AI-powered SQL generation, and caching.

---

## Vanna.AI Connector (`vannaai-connector`)

Establishes database connections for SQL operations.

### Config
```yaml
data:
  type: vannaai-connector
  title: Database Connection
  database:
    host: "localhost"
    port: 5432
    username: "user"
    password: "{{#env.DB_PASSWORD#}}"
    database_name: "mydb"
    database_type: "postgresql"    # postgresql, mysql, mssql, sqlite
    ssl_cert: ""
    schemas: ["public"]
```

### Outputs
| Output | Type | Description |
|--------|------|-------------|
| `connector` | object | Connection handle for downstream SQL nodes |

---

## Vanna.AI Question (`vannaai-question`)

Converts natural language questions to SQL queries using AI.

### Config
```yaml
data:
  type: vannaai-question
  title: Ask Database
  connector:
    - vannaai_connector
    - connector
  model:
    provider: openai
    name: gpt-4o
    mode: chat
    completion_params:
      temperature: 0.0
  context:
    enabled: false
  number_validation: 5
  app_id_collection: ""
```

### Outputs
| Output | Type | Description |
|--------|------|-------------|
| `sql` | string | Generated SQL query |
| `result` | string | Query result data |

---

## Vanna.AI Training (`vannaai-training`)

Trains the SQL model with DDL, examples, and documentation.

### Config
```yaml
data:
  type: vannaai-training
  title: Train SQL Model
  connector:
    - vannaai_connector
    - connector
  model:
    provider: openai
    name: gpt-4o-mini
    mode: chat
    completion_params:
      temperature: 0.0
  training_sql:
    - question: "How many users are there?"
      sql: "SELECT COUNT(*) FROM users"
    - question: "Show recent orders"
      sql: "SELECT * FROM orders ORDER BY created_at DESC LIMIT 10"
  documentation:
    - "The users table contains all registered users with fields: id, name, email, created_at"
    - "The orders table has: id, user_id, total, status, created_at"
  is_clear_data: false
```

---

## SQL Output Chart (`sql-output-chart`)

Generates chart visualizations from SQL results using an LLM.

### Config
```yaml
data:
  type: sql-output-chart
  title: Chart from SQL
  connector:
    - vannaai_connector
    - connector
  model:
    provider: openai
    name: gpt-4o-mini
    mode: chat
    completion_params:
      temperature: 0.3
  sql_query:
    type: variable
    value:
      - vannaai_question
      - sql
  context:
    enabled: false
  prompt_template:
    - role: system
      text: "Generate a chart specification from the SQL results."
```

### Outputs
| Output | Type | Description |
|--------|------|-------------|
| `chart` | object | Chart specification |

---

## SQL Output Table (`sql-output-table`)

Outputs SQL results as formatted table (JSON or CSV).

### Config
```yaml
data:
  type: sql-output-table
  title: Table from SQL
  connector:
    - vannaai_connector
    - connector
  sql_query:
    type: variable
    value:
      - vannaai_question
      - sql
  output_type: json              # json or csv
  precision: 4                   # Decimal precision
```

### Outputs
| Output | Type | Description |
|--------|------|-------------|
| `table` | string | Formatted table data |

---

## SQL Output Summary (`sql-output-summary`)

Generates natural language summary of SQL query results.

### Config
```yaml
data:
  type: sql-output-summary
  title: Summarize Results
  connector:
    - vannaai_connector
    - connector
  model:
    provider: openai
    name: gpt-4o-mini
    mode: chat
    completion_params:
      temperature: 0.5
  sql_query:
    type: variable
    value:
      - vannaai_question
      - sql
  context:
    enabled: false
```

### Outputs
| Output | Type | Description |
|--------|------|-------------|
| `summary` | string | Natural language summary |

---

## Cache Retrieve (`cache-retrieve`)

Retrieves cached values by key.

### Config
```yaml
data:
  type: cache-retrieve
  title: Get Cache
  cache_key:
    - start
    - query
  cache_scope: workflow          # workflow or conversation
```

### Outputs
| Output | Type | Description |
|--------|------|-------------|
| `value` | string | Cached value (null if miss) |
| `hit` | boolean | Whether cache key was found |

---

## Cache Store (`cache-store`)

Stores values in cache with TTL.

### Config
```yaml
data:
  type: cache-store
  title: Set Cache
  cache_key:
    - start
    - query
  cache_value:
    - llm
    - text
  cache_scope: workflow
  ttl: 3600                      # Time-to-live in seconds
```

### Outputs
None (write-only operation).

### Gotchas
- `cache_scope: workflow` — shared across all runs of this workflow
- `cache_scope: conversation` — scoped to current conversation (chatflows only)
- TTL of 0 means no expiry
- Cache is per-tenant (workspace)
