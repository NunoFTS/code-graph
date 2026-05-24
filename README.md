# code-graph

## Run

### Backend

```bash
python -m backend.src.main
```

## Current Architecture

### Topology

User Input
    ↓
[Code Generator]
    ↓
[Validator]
    ↓
   ├── PASS → END
   └── FAIL → back to Code Generator

### Orchestrator

The orchestrator is implemented through LangGraph conditional routing.

Behavior:

- Always starts at the Code Generator
- Routes output based on validator result:
  - PASS → end execution
  - FAIL → retry generation

### Generator

Generates Python code based on a user prompt.

Output is raw code only (no explanations or formatting)

Input:

- User request
- Current state (optional context)

Output:

- Generated Python code as a string

### Validator

Evaluates generated code for correctness.

Responsibilities:

- Check syntax and logical validity
- Ensure code satisfies the user request
- Return pass/fail decision

## Plan

- sandbox execution layer
- structured validation output (JSON)
- attempt limiting + failure handling policies
