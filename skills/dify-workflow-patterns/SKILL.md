---
name: dify-workflow-patterns
description: "Use when building a new Dify app from scratch, choosing between workflow vs chatflow, deciding which nodes to combine, or needing a complete DSL template for a common use case like RAG, agents, or data processing."
---

# Dify Workflow Patterns

Select the right pattern based on what the user wants to build.

## Pattern Selection Guide

| User wants... | Pattern | Mode |
|--------------|---------|------|
| Simple Q&A chatbot | `simple_chatbot` | advanced-chat |
| Q&A over documents | `rag_chatbot` | advanced-chat |
| One-shot text task (summarize, translate) | `text_generation` | workflow |
| Agent with tools (search, calculate) | `agent_with_tools` | advanced-chat |
| Process list of items with LLM | `data_processing_pipeline` | workflow |
| Call external APIs and process results | `api_orchestration` | workflow |
| Analyze uploaded files | `document_analysis` | workflow |
| Route queries to different handlers | `conditional_routing` | advanced-chat |

## Pattern Files

Each pattern file contains:
1. Architecture diagram (node flow)
2. Complete DSL YAML template
3. Customization points (what to change for specific use cases)
4. Variations (common modifications)

## General Principles

1. **Start simple** — use the fewest nodes possible, add complexity only when needed
2. **Mode choice matters**:
   - `workflow` = single input → single output (API-like)
   - `advanced-chat` = conversational with memory
3. **One LLM per concern** — don't make one LLM do everything; chain focused LLMs
4. **Error paths** — for production apps, add if-else checks after HTTP/code nodes
5. **Variables flow downstream** — you can only reference outputs from nodes that execute BEFORE the current node
