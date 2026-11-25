---
name: Documentation standards
description: Standards that define coding style, documentation requirements, error handling patterns, and naming conventions.
invokable: true
---

# Module 2 Project 

## Coding Style
- Follow PEP 8. Max line length 100. Use 4-space indentation.
- Use type hints on all function signatures and public attributes.
- Prefer small, single-purpose functions (aim for < 40 lines).
- Prefer composition over inheritance; avoid deep class hierarchies.
- No unused imports, variables, or commented-out code.
- Use f-strings for formatting; never string concatenation in loops.
- Keep business logic out of route/controller handlers; put it in service modules.

## Documentation Requirements
- Every public module, class, and function gets a Google-style docstring:
 summary line, blank line, Args, Returns, Raises (and Example when non-obvious).
- Docstrings describe *what* and *why*, not a line-by-line *how*.
- Inline comments only for non-obvious logic, workarounds, or business rules.
- Any new endpoint, CLI command, or config option must be reflected in README.md.
- Update CHANGELOG/notes when behavior changes.

## Error Handling Patterns
- Never use bare `except:`; catch specific exceptions.
- Validate inputs at boundaries (API handlers, CLI args) and fail fast.
- Raise custom exceptions (subclass a project base `AppError`) for domain errors.
- Don't swallow exceptions silently; log with context, then re-raise or convert.
- Use the `logging` module, never `print`, for diagnostics.
- API errors return a consistent shape: {"error": {"code": str, "message": str}}
 with an appropriate HTTP status code.
- Use context managers (`with`) for files, connections, and locks.

## Naming Conventions
- Variables/functions: snake_case, verbs for functions (`get_prompt`, `validate_input`).
- Classes: PascalCase (`PromptService`). Exceptions end in `Error`.
- Constants: UPPER_SNAKE_CASE.
- Private helpers: leading underscore (`_build_query`).
- Booleans read as questions: `is_valid`, `has_access`.
- Test files: `test_<module>.py`; test functions: `test_<behavior>_<condition>`.
- No single-letter names except loop indices and comprehensions.

## Passing docstrings compared to failing docstrings
- The summary does not repeat the name in sentence form and adds information that the function name does not.
- Only list the errors the function itself raises. If something else raises it, describe it in the paragraph, not under Raises:. If the function raises nothing, leave the section out entirely.
- A docstring should describe cases that are both the usual or normal case as well as the surprise case. For example, in None returns, empty lists, case-sensitivity, and side effects beyond the obvious result.

## Formatting
- Write docstrings with real line breaks. Never put literal \n escape sequences in the source.

## Modification instructions
- Modify only the highlighted block or blocks of code as specified. Do not expand changes to nearby classes or functions unless besides the highlighted block or blocks.
- Ensure any modifications within the specified block or blocks and maintain clarity and consistency without affecting the overall context of related classes.
- For any new changes that require documentation in nearby classes or functions, they must be mentioned explicitly in the prompt.
