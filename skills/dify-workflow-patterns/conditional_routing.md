# Pattern: Conditional Routing

Route user queries to different handlers based on intent classification.

## Architecture

```
Start → Question Classifier → [Handler A / Handler B / Handler C] → Answer
```

## Mode: `advanced-chat`

## When to Use
- Support bot routing (tech / billing / general)
- Multi-domain assistant (each domain has specialized prompt)
- Language-based routing
- Complexity-based routing (simple → fast model, complex → powerful model)

## Complete DSL

```yaml
version: "0.6.0"
kind: "app"
app:
  name: "Smart Router"
  mode: "advanced-chat"
  icon: "🔀"
  icon_background: "#FFF3E0"
  description: "Routes queries to specialized handlers"
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
      - id: "classifier"
        type: custom
        position: {x: 380, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: question-classifier
          title: Route Query
          query_variable_selector:
            - sys
            - query
          model:
            provider: openai
            name: gpt-4o-mini
            mode: chat
            completion_params:
              temperature: 0.0
          classes:
            - id: "technical"
              name: "Technical Support"
            - id: "billing"
              name: "Billing & Account"
            - id: "general"
              name: "General Inquiry"
          instruction: |
            Classify the user's message into one of the categories:
            - Technical Support: bugs, errors, how-to questions, integration issues
            - Billing & Account: pricing, invoices, subscriptions, account changes
            - General Inquiry: everything else, greetings, feedback, general questions
          memory:
            enabled: false
          vision:
            enabled: false
      - id: "tech_llm"
        type: custom
        position: {x: 730, y: 132}
        sourcePosition: right
        targetPosition: left
        data:
          type: llm
          title: Tech Support
          model:
            provider: openai
            name: gpt-4o
            mode: chat
            completion_params:
              temperature: 0.3
          prompt_template:
            - role: system
              text: |
                You are a technical support specialist. Help users solve technical problems.
                Be precise, provide step-by-step solutions, and include code examples when relevant.
                If you need more information to diagnose the issue, ask specific questions.
            - role: user
              text: "{{#sys.query#}}"
          memory:
            enabled: true
            window:
              enabled: true
              size: 10
          context:
            enabled: false
          vision:
            enabled: false
      - id: "billing_llm"
        type: custom
        position: {x: 730, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: llm
          title: Billing Support
          model:
            provider: openai
            name: gpt-4o-mini
            mode: chat
            completion_params:
              temperature: 0.5
          prompt_template:
            - role: system
              text: |
                You are a billing and account support specialist.
                Help users with pricing questions, invoice issues, subscription changes.
                Be friendly and clear. If the request requires manual action, explain what steps the user should take.
            - role: user
              text: "{{#sys.query#}}"
          memory:
            enabled: true
            window:
              enabled: true
              size: 10
          context:
            enabled: false
          vision:
            enabled: false
      - id: "general_llm"
        type: custom
        position: {x: 730, y: 432}
        sourcePosition: right
        targetPosition: left
        data:
          type: llm
          title: General Assistant
          model:
            provider: openai
            name: gpt-4o-mini
            mode: chat
            completion_params:
              temperature: 0.7
          prompt_template:
            - role: system
              text: |
                You are a friendly general assistant. Help with any questions or requests.
                Keep responses concise and helpful.
            - role: user
              text: "{{#sys.query#}}"
          memory:
            enabled: true
            window:
              enabled: true
              size: 10
          context:
            enabled: false
          vision:
            enabled: false
      - id: "answer"
        type: custom
        position: {x: 1080, y: 282}
        sourcePosition: right
        targetPosition: left
        data:
          type: answer
          title: Answer
          answer: "{{#tech_llm.text#}}{{#billing_llm.text#}}{{#general_llm.text#}}"
    edges:
      - id: "start-classifier"
        source: "start"
        sourceHandle: "source"
        target: "classifier"
        targetHandle: "target"
      - id: "classifier-tech"
        source: "classifier"
        sourceHandle: "technical"
        target: "tech_llm"
        targetHandle: "target"
      - id: "classifier-billing"
        source: "classifier"
        sourceHandle: "billing"
        target: "billing_llm"
        targetHandle: "target"
      - id: "classifier-general"
        source: "classifier"
        sourceHandle: "general"
        target: "general_llm"
        targetHandle: "target"
      - id: "tech-answer"
        source: "tech_llm"
        sourceHandle: "source"
        target: "answer"
        targetHandle: "target"
      - id: "billing-answer"
        source: "billing_llm"
        sourceHandle: "source"
        target: "answer"
        targetHandle: "target"
      - id: "general-answer"
        source: "general_llm"
        sourceHandle: "source"
        target: "answer"
        targetHandle: "target"
  features:
    opening_statement: "Hello! I'm here to help. What can I assist you with?"
    suggested_questions:
      - "I'm getting an error when I try to connect"
      - "How do I change my subscription plan?"
      - "What features do you offer?"
  environment_variables: []
  conversation_variables: []
```

## Customization Points

| What to Change | Where |
|---------------|-------|
| Categories | `classifier.data.classes` array |
| Classification instructions | `classifier.data.instruction` |
| Handler prompts | Each LLM node's `prompt_template` |
| Model per handler | Different `model` config per LLM (powerful for tech, cheap for general) |
| Routing logic | Edge `sourceHandle` values matching class `id`s |

## Key Design Notes

1. **Edge handles must match class IDs**: `sourceHandle: "technical"` matches `classes[0].id: "technical"`
2. **Answer node collects all branches**: Since only one branch executes, the answer template with multiple `{{#...#}}` references works — only the executed branch produces output
3. **Different models per branch**: Use GPT-4o for complex tech support, GPT-4o-mini for simple general queries

## Variations

### With If-Else Instead of Classifier
Replace question-classifier with keyword-based if-else:
```yaml
data:
  type: if-else
  cases:
    - case_id: "technical"
      conditions:
        - variable_selector: [sys, query]
          comparison_operator: contains
          value: "error"
    - case_id: "billing"
      conditions:
        - variable_selector: [sys, query]
          comparison_operator: contains
          value: "invoice"
```
Simpler but less accurate than LLM classification.

### With Knowledge Base Per Handler
Add a knowledge-retrieval node before each handler LLM:
```
classifier → knowledge-tech → tech_llm → answer
classifier → knowledge-billing → billing_llm → answer
```

### With Escalation Path
Add a human-input node for complex cases:
```
classifier → "escalate" class → human-input → answer
```
