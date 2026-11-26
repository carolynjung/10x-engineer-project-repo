---
description: project rules for the AI assistant
---
# PromptLab: project rules for the AI assistant

## Project context
FastAPI + Pydantic v2 REST API for storing prompt templates. Python 3.10+.
Storage is the in-memory singleton `storage` in backend/app/storage.py (no database).
All commands run from backend/. Imports are absolute from `app`, e.g. `from app.models import Prompt`.

## Coding standards
- Follow PEP 8. snake_case for functions and variables, PascalCase for classes, UPPER_CASE for constants.
- Type hints on every parameter and return value. Use Optional[X] for nullable values.
- Never access storage._prompts or other private attributes outside storage.py.
- Never create a new Storage() instance; import the `storage` singleton.
- Timestamps come from models.get_current_time(); IDs from models.generate_id().
- Set updated_at = get_current_time() on every modification of a stored object.
- Generated code must be complete and syntactically valid: consistent 4-space indentation,
  every import it uses, no placeholders.

## Docstrings
- Google-style docstring on every function and class: a summary line, then Args, Returns,
  and Raises where they apply.
- The summary line adds information the name does not. "Get prompt." fails;
  "Return the prompt with this ID, or None if it does not exist." passes.
- Raises lists only exceptions the function itself raises. If something else raises it
  (e.g. Pydantic's 422), describe it in the paragraph instead. If the function raises
  nothing, leave the Raises section out entirely; never write "Raises: None".
- Describe the normal case and the surprising cases: None returns, empty results,
  case-sensitivity, and side effects beyond the obvious result (e.g. cascade delete).
- Docstrings use real line breaks and 4-space indentation; never literal \n escape sequences.

## Preferred patterns and conventions
- Keep endpoint functions thin: validate, call storage/utils, return a model.
- Check lookups with `if x is None:`, never `if not x:`.
- PATCH: accept a <Resource>Patch model (all fields Optional), apply
  `model_dump(exclude_unset=True)`, then `existing.model_copy(update=...)`.
- List endpoints return {<plural resource name>: [...], "total": N}, sorted newest first by created_at.
- Filtering and search go in utils.py as pure functions that take and return lists.
- Do not add logging, dependency injection, or custom exception classes unless asked.

## Model fields (check before writing code or tests)
- Prompt: title (str, 1-200, required), content (str, min 1, required),
  description (str or null, max 500), collection_id (str or null);
  server-set: id, created_at, updated_at.
- Collection: name (str, 1-100, required), description (str or null, max 500);
  server-set: id, created_at.
- Request bodies: PromptCreate (POST), PromptUpdate (PUT, full replace),
  PromptPatch (PATCH, all optional), CollectionCreate (POST).
- Keep this section in sync with backend/app/models.py whenever models change.

## File naming and layout
- Lowercase with underscores for Python files.
- Routes: backend/app/api.py only, under the matching `# ===== X Endpoints =====` banner.
- Models: backend/app/models.py, named <Resource>Base, <Resource>Create,
  <Resource>Update (PUT, full replace), <Resource>Patch (PATCH), <Resource>, <Resource>List.
- Storage methods: backend/app/storage.py, named create_x, get_x, get_all_xs, update_x, delete_x.
- Pure helpers with no FastAPI imports: backend/app/utils.py.
- Tests: backend/tests/test_api.py, inside classes named Test<Resource>; shared fixtures in conftest.py.
- Specs: specs/<feature-name>.md (kebab-case). API docs: docs/API_REFERENCE.md.

## Error handling approach
- Raise fastapi.HTTPException only from api.py, never from storage.py or utils.py.
  Storage returns None (not found) or False (delete miss) and never raises.
- Status codes:
  - 404 when the resource in the URL path does not exist.
  - 400 when the request body references another resource that does not exist (e.g. collection_id).
  - 422 for invalid input. Prefer Pydantic Field constraints over manual checks.
  - 409 when the request conflicts with the current state (e.g. restoring the version that is already current); detail describes the state, e.g. "Version 2 is already the current version".
  - 201 for create, 204 with no body for delete, 200 otherwise.
- detail strings: exactly "<Resource> not found" (e.g. "Prompt not found", "Collection not found").
  Field-level messages: "<field> <problem>", e.g. "title cannot be null".
- Never expose stack traces or return 500 for user input errors; never catch and silence exceptions.

## Testing requirements
- Add tests to backend/tests/test_api.py inside the existing class for the resource:
  TestHealth, TestPrompts or TestCollections. Do not create new test files or
  module-level test functions unless asked.
- Fixtures available from backend/tests/conftest.py (pytest injects them by parameter
  name; never import from conftest.py, never redefine them):
  - client: a TestClient for the app
  - clear_storage: autouse; empties storage before and after every test
  - sample_prompt_data: {"title", "content", "description"} dict for POST /prompts
  - sample_collection_data: {"name", "description"} dict for POST /collections
- Never define fixtures in test files. If a new shared fixture is needed, add it to conftest.py.
- Never call storage.clear() or write to storage directly in tests.
- Create test data through the API with client.post(...) and the sample_* fixtures,
  so tests exercise the real request path.
- Never hard-code IDs. Use the "id" from the create response; for not-found cases
  use the literal "does-not-exist".
- Test URLs must match the route path in api.py exactly.
- Every new or changed endpoint gets: one success test, one 404 test, and one test
  per other error status it can return.
- Success tests assert status_code, "total" where present, and at least one returned
  value (e.g. an id or title), not only the length.
- Error tests assert status_code and the exact body, e.g.
  response.json() == {"detail": "Collection not found"}.
- List endpoints also get a test for the empty case ([] and total 0).
- Run `pytest tests/ -v` from backend/; all tests must pass before committing.
- Keep coverage at or above 80%: `pytest tests/ --cov=app`.

### Example test to follow
```python
class TestCollections:
    def test_list_prompts_in_collection(self, client, sample_collection_data, sample_prompt_data):
        collection = client.post("/collections", json=sample_collection_data).json()
        payload = {**sample_prompt_data, "collection_id": collection["id"]}
        prompt = client.post("/prompts", json=payload).json()

        response = client.get(f"/collections/{collection['id']}/prompts")

        assert response.status_code == 200
        assert response.json()["total"] == 1
        assert response.json()["prompts"][0]["id"] == prompt["id"]

    def test_list_prompts_unknown_collection(self, client):
        response = client.get("/collections/does-not-exist/prompts")

        assert response.status_code == 404
        assert response.json() == {"detail": "Collection not found"}
```

## Documentation
- When an endpoint is added or changed, update docs/API_REFERENCE.md and the README
  endpoint table in the same change.
