# code-graph

## Backend

### Install

```bash
python -m pip install -r backend/requirements.txt
```

### Configure

Create your env file:

```powershell
Copy-Item backend\.env.example backend\.env
```

Set `GEMINI_API_KEY` in `backend/.env` (and optionally `TESTING=1` for debug logging).

Configure per-agent model parameters in `backend/config/agents.toml`.

### Run

```bash
python -m backend.src.main
```

## Logging

- Logs are written as JSONL to `backend/_data/logs/app.jsonl`.
- Logs rotate daily and keep 7 days.
- `TESTING=1` enables `DEBUG` level and console logging.

## Architecture

The backend is a LangGraph `StateGraph` with this retry loop:

User Input
    ↓
[Code Generator]
    ↓
[Sandbox]
    ↓
[Validator]
    ↓
   ├── PASS -> END
   └── FAIL -> back to Code Generator (until `max_attempts`)

## Config

Agent settings live in `backend/config/agents.toml`:

- `provider`: currently only `gemini`
- `model`: Gemini model name
- `temperature`: float
- `prompt_file`: file in `backend/src/prompts/`
- `output_json`: boolean (when `true`, the Gemini response is requested as JSON)

## Prompts

Prompts live in `backend/src/prompts/` and are rendered with state placeholders like `{input}`, `{generated_code}`, and `{execution_result}`. Missing placeholders render as an empty string.
