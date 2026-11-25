---
name: docstrings prompt
description: Prompt to add docstring to a function in backend/app
invokable: true
---

Add Google-style docstrings following the project rules in .continue/rules/.

Requirements:
- Do not change any code. Only add or edit docstrings (and comments if noted below).
- The summary line must add information beyond the function name.
- Use Args, Returns and Raises only where they apply. List under Raises only
  exceptions this function itself raises. Never write "Raises: None".
- Describe None returns, empty results, case-sensitivity and side effects.
- Keep any existing docstring that is already accurate; fix any that are vague or wrong.
- Do not expand changes to nearby classes or functions other than what was highlighted
- Ensure consistency and clarity within the highlighted block, but refrain from altering related classes or functions unless specified.


When done, list every function and class you documented so I can check nothing was skipped.