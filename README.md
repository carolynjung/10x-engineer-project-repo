# PromptLab

PromptLab is a REST API for storing, organizing and searching AI prompt templates.
Think "Postman for prompts": teams keep reusable prompts with `{{variables}}`, group them into collections, and find them again by keyword.

## Features

- Create, read, replace (PUT), partially update (PATCH) and delete prompts
- Group prompts into collections; deleting a collection deletes its prompts
- Filter prompts by collection and search by title or description
- Results sorted newest first
- Input validation with clear 4xx errors (Pydantic)
- Interactive API docs at /docs (Swagger UI) and /redoc
- Health check endpoint for monitoring

## Tech stack

Python 3.10+, FastAPI, Pydantic v2, Uvicorn, pytest. Storage is in memory.

## Prerequisites

- Python 3.10 or newer (`python --version`)
- pip
- Git
- No environment variables, database or API keys are required.

## Installation
```bash
    git clone https://github.com/carolynjung/10x-engineer-project-repo.git
    cd 10x-engineer-project-repo
    python -m venv .venv
    source .venv/bin/activate          # MacOS; On Windows use venv\Scripts\activate
    pip install -r backend/requirements.txt
```
## Quick start
```bash
    cd backend
    python main.py
```
- API base URL: http://127.0.0.1:8000 (the root `/` returns 404 by design; try `/health`)
- Swagger UI: http://127.0.0.1:8000/docs

In a second terminal:
```bash
    curl http://127.0.0.1:8000/health
    # {"status":"healthy","version":"0.1.0"}

    curl -X POST http://127.0.0.1:8000/prompts \
      -H "Content-Type: application/json" \
      -d '{"title":"Summarize","content":"Summarize this: {{text}}"}'
```
## API endpoint summary

Full details, request/response examples and error codes: [docs/API_REFERENCE.md](docs/API_REFERENCE.md).

| Method | Endpoint | Description | Success |
|---|---|---|---|
| GET | /health | Health check and version | 200 |
| GET | /prompts | List prompts (`collection_id`, `search` query params) | 200 |
| GET | /prompts/{prompt_id} | Get one prompt | 200 |
| POST | /prompts | Create a prompt | 201 |
| PUT | /prompts/{prompt_id} | Replace a prompt (all fields) | 200 |
| PATCH | /prompts/{prompt_id} | Update only the fields sent | 200 |
| DELETE | /prompts/{prompt_id} | Delete a prompt | 204 |
| GET | /collections | List collections | 200 |
| GET | /collections/{collection_id} | Get one collection | 200 |
| POST | /collections | Create a collection | 201 |
| DELETE | /collections/{collection_id} | Delete a collection and its prompts | 204 |

Example: update only the description of a prompt
```bash
    curl -X PATCH http://127.0.0.1:8000/prompts/<prompt_id> \
      -H "Content-Type: application/json" \
      -d '{"description":"Short summaries for meeting notes"}'
```
## Project structure
```bash
10x-engineer-project-repo/
├── backend/
│   ├── app/
│   │   ├── api.py        FastAPI routes
│   │   ├── models.py     Pydantic request/response models
│   │   ├── storage.py    In-memory storage class
│   │   └── utils.py      Sorting, filtering, search helpers
│   ├── tests/            pytest suite and fixtures
│   ├── main.py           Entry point (uvicorn)
│   └── requirements.txt
├── docs/                 API reference, system model, AI logs
├── specs/                Feature specifications
└── frontend/             (planned)
```

---
## Development setup
```bash
    cd backend
    pytest tests/ -v                       # run tests
    pytest tests/ --cov=app                # with coverage
    python -m pydoc app.storage            # view docstrings
```
- Code style: PEP 8, type hints on all functions, Google-style docstrings.
- AI assistant rules for this repo live in `.continuerules`.
- Data resets every time the server restarts.

## Contributing

1. Create a branch from `main`: `git checkout -b feature/<your-short-name>`.
2. Make the change with tests. New endpoints need a success test and an error test.
3. Run `pytest tests/ -v`; all tests must pass.
4. Update `docs/API_REFERENCE.md` and this README if an endpoint changes.
5. Write a clear commit message (what and why) and open a pull request.

## Known issues

- Storage is in memory; nothing persists across restarts.
- No authentication.
- `datetime.utcnow()` triggers deprecation warnings on Python 3.12+.
- Search does not look at prompt `content`.

## Roadmap

Specs for upcoming features: [prompt versions](specs/prompt-versions.md), [tagging](specs/tagging-system.md).
