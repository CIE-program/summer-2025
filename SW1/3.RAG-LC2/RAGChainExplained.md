INPUT: "What is AI Product Management?"
↓
┌─────────────────────────────────────┐
│ Dictionary Processing │
│ ┌─────────────────────────────────┐ │
│ │ "context": retriever|format_docs│ │ → Retrieves & formats docs
│ │ "question": RunnablePassthrough │ │ → Passes question unchanged
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
↓
OUTPUT: {"context": "AI PM involves...", "question": "What is AI PM?"}
↓
┌─────────────────────────────────────┐
│ prompt_template │ → Substitutes {context} & {question}
└─────────────────────────────────────┘
↓
OUTPUT: "You are an AI assistant... Context: AI PM involves... Question: What is AI PM?"
↓
┌─────────────────────────────────────┐
│ llm │ → Generates response
└─────────────────────────────────────┘
↓
OUTPUT: "AI Product Management is the discipline of..."
↓
┌─────────────────────────────────────┐
│ StrOutputParser() │ → Extracts string from LLM response
└─────────────────────────────────────┘
↓
FINAL OUTPUT: "AI Product Management is the discipline of..."
