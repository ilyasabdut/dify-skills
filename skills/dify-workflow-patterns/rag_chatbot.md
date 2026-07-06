# Pattern: RAG Chatbot

Chat with your documents using knowledge base retrieval.

## Architecture

```
Start → Knowledge Retrieval → LLM (context + memory) → Answer
```

## Mode: `advanced-chat`

## When to Use
- Q&A over company documents
- Documentation assistant
- Knowledge base search with natural language answers
- Any chatbot that needs to reference stored documents

## Complete DSL

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
                You are a knowledgeable assistant. Answer the user's question based on the provided context.
                If the context doesn't contain relevant information, say "I don't have enough information to answer that question."
                Always cite which document or section your answer is based on when possible.

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
    opening_statement: "Hello! I can answer questions about your documents. What would you like to know?"
    suggested_questions:
      - "What is this document about?"
      - "Summarize the key points"
      - "Find information about..."
  environment_variables: []
  conversation_variables: []
```

## Customization Points

| What to Change | Where |
|---------------|-------|
| Knowledge bases | `dataset_ids` array (add real UUIDs) |
| Number of results | `multiple_retrieval_config.top_k` |
| Relevance threshold | `multiple_retrieval_config.score_threshold` |
| Answer style | System prompt in `prompt_template[0].text` |
| Show sources | `features.retriever_resource.enabled` |

## Variations

### Multiple Knowledge Bases
```yaml
dataset_ids:
  - "dataset-uuid-1"    # Product docs
  - "dataset-uuid-2"    # FAQ
  - "dataset-uuid-3"    # Release notes
```

### With Reranking (better accuracy)
```yaml
multiple_retrieval_config:
  top_k: 5
  score_threshold: 0.3
  reranking_enable: true
  reranking_model:
    provider: cohere
    model: rerank-english-v3.0
```

### Hybrid Search (keyword + semantic)
```yaml
multiple_retrieval_config:
  top_k: 3
  score_threshold: 0.5
  weights:
    weight_type: customized
    vector_setting:
      vector_weight: 0.7
    keyword_setting:
      keyword_weight: 0.3
```
