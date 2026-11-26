# Spec: Prompt Versions

> Status: Draft <br>
> Target: Module 3 <br> 
> Owner: Carolyn Jung <br>

## 1. Overview and goals
Every time a prompt's title, content or description changes, PromptLab keeps an
immutable snapshot. Users can list past versions, view one, and restore an old one.

Goals
- No edit ever loses the previous text.
- Versions are numbered 1, 2, 3... per prompt, with no gaps.
- Restoring is itself a new version, so history is never rewritten.

Non-goals: diffs between versions, deleting individual versions, version limits.

## 2. User stories (US) and acceptance criteria (AC)

US-1 As a prompt engineer, I want a version recorded when I create a prompt,
so that history starts from the original text.
- AC-1.1 POST /prompts returns 201 with `current_version == 1`.
- AC-1.2 GET /prompts/{id}/versions then returns `total == 1` and
  `versions[0].version_number == 1` with the same title, content, description.

US-2 As a prompt engineer, I want each edit saved as a new version.
- AC-2.1 PUT or PATCH that changes title, content or description returns 200 with
  `current_version` increased by exactly 1.
- AC-2.2 The new version stores the values after the change.
- AC-2.3 Values are compared after the update is applied; a PUT that omits a non-null description is a change and creates a version.
- AC-2.4 PATCH that changes only collection_id does not create a version.
- AC-2.5 If the request includes `change_note`, the new version stores it;
  otherwise `change_note` is null.
- AC-2.6 A `change_note` longer than 200 characters returns 422 with
  `loc == ["body", "change_note"]` and nothing is updated.
- AC-2.7 updated_at changes on every successful PUT or PATCH, whether or not a version is created.

US-3 As a prompt engineer, I want to see a prompt's history.
- AC-3.1 GET /prompts/{id}/versions returns 200, versions sorted by
  version_number descending (newest first), and `total` equal to the list length.
- AC-3.2 Unknown prompt ID returns 404 `{"detail": "Prompt not found"}`.
- AC-3.3 After three PATCH requests that each change content, GET /prompts/{id}/versions returns version_number values [4, 3, 2, 1] in that order.
- AC-3.4 The list is never empty: every prompt has at least version 1, so no empty-list test applies.

US-4 As a prompt engineer, I want to view one specific version.
- AC-4.1 GET /prompts/{id}/versions/{n} returns 200 with that version.
- AC-4.2 Unknown prompt returns 404 `"Prompt not found"`.
- AC-4.3 Existing prompt but n not in its history returns 404 `"Version not found"`.
- AC-4.4 n = 0, negative, or not an integer returns 422.

US-5 As a prompt engineer, I want to restore an old version.
- AC-5.1 POST /prompts/{id}/versions/{n}/restore returns 200 with the prompt whose
  title, content and description equal version n, and `current_version` = old + 1.
- AC-5.2 The new version's change_note is exactly `"Restored from version {n}"`.
- AC-5.3 Restoring the version that is already current returns 409
  `{"detail": "Version {n} is already the current version"}` and creates nothing.
- AC-5.4 Unknown prompt or version returns 404 as in AC-4.2 / AC-4.3.
- AC-5.5 `updated_at` is later than its value before the restore; created_at and collection_id are unchanged.
- AC-5.6 Restore always creates a new version unless n equals current_version, even if the text matches the current text.

US-6 Deleting a prompt removes its history.
- AC-6.1 After DELETE /prompts/{id}, GET /prompts/{id}/versions returns 404.
- AC-6.2 After DELETE /collections/{cid}, versions of its prompts are also gone.

## 3. Data model changes

Version Changes
- current_version always equals the highest version_number for the prompt.
- Version 1's created_at equals the prompt's created_at; later versions use the time of the change.
- Path validation runs first: an invalid version_number returns 422 even if the prompt does not exist.
- Version id is informational; all endpoints address versions by version_number.
- No pagination; all versions are returned.

Change Notes
- change_note: 1-200 chars when given; "" returns 422 with loc ["body", "change_note"].
- change_note is never returned on Prompt responses; it appears only on PromptVersion.

New model `PromptVersion` (models.py)
| Field | Type | Rules |
|---|---|---|
| id | str | UUID4, server-set |
| prompt_id | str | ID of the parent prompt |
| version_number | int | >= 1, unique per prompt |
| title | str | snapshot |
| content | str | snapshot |
| description | Optional[str] | snapshot |
| change_note | Optional[str] | max 200 chars |
| created_at | datetime | server-set |

New model `PromptVersionList`: `versions: List[PromptVersion]`, `total: int`.

Changed models
- `Prompt`: add `current_version: int = 1`.
- `PromptUpdate` and `PromptPatch`: add optional `change_note: Optional[str]`
  (max 200). It is not stored on the prompt itself.

Storage (storage.py)
- New `_versions: Dict[str, List[PromptVersion]]` keyed by prompt_id.
- New methods: `add_version(version)`, `get_versions(prompt_id) -> List`,
  `get_version(prompt_id, n) -> Optional`, `delete_versions(prompt_id)`.
- `clear()` also clears versions.

## 4. API endpoints

### GET /prompts/{prompt_id}/versions
Response 200
```json
{ "versions": [
    { "id": "b1...", "prompt_id": "7c...", "version_number": 2,
      "title": "Summarize", "content": "Summarize in 3 bullets: {{text}}",
      "description": null, "change_note": "Bullets read better",
      "created_at": "2026-12-01T15:00:00" },
    { "...": "version 1" } ],
  "total": 2 }
```
Errors: 404 Prompt not found.

### GET /prompts/{prompt_id}/versions/{version_number}
Response 200: one PromptVersion object.
Errors: 404 Prompt not found · 404 Version not found · 422 version_number < 1 or not an int.

### POST /prompts/{prompt_id}/versions/{version_number}/restore
Request body: none. Response 200: the updated Prompt. Returns 200 (not 201) because the response is the updated prompt; the new version is a side effect.
Errors: 404 Prompt not found · 404 Version not found · 409 already current · 422 bad number.

### Changed: POST, PUT, PATCH /prompts
Responses gain `current_version`. PUT and PATCH accept optional `change_note`.

## 5. Error conditions and edge cases
| Case | Result |
|---|---|
| Unknown prompt on any versions endpoint | 404 "Prompt not found" |
| Version number not in history | 404 "Version not found" |
| version_number = 0, -1, "abc" | 422 (Pydantic path validation) |
| Restore current version | 409, no new version |
| Update with identical title/content/description | 200, no new version |
| Update changing only collection_id | 200, no new version |
| change_note > 200 chars | 422, prompt not modified |
| change_note sent with no actual change | 200, ignored, no version |
| Prompt deleted, or its collection deleted | its versions deleted |

## 6. Test plan (one test per AC)

| AC | Test |
|---|---|
| AC-1.1 | `test_create_prompt_sets_current_version_1` |
| AC-1.2 | `test_create_prompt_creates_version_1_snapshot` |
| AC-2.1 | `test_patch_content_increments_current_version` |
| AC-2.1 | `test_put_title_increments_current_version` |
| AC-2.2 | `test_new_version_stores_values_after_change` |
| AC-2.3 | `test_identical_update_creates_no_version` |
| AC-2.3 | `test_put_omitting_description_counts_as_change` |
| AC-2.4 | `test_patch_collection_only_creates_no_version` |
| AC-2.5 | `test_change_note_stored_on_new_version` |
| AC-2.5 | `test_change_note_null_when_omitted` |
| AC-2.6 | `test_change_note_over_200_chars_returns_422` |
| AC-2.6 | `test_change_note_empty_returns_422` |
| AC-2.7 | `test_update_without_new_version_still_changes_updated_at` |
| Edge: change_note with no actual change | `test_change_note_without_changes_creates_no_version` |
| AC-3.1 | `test_list_versions_newest_first_with_total` |
| AC-3.2 | `test_list_versions_returns_404_for_unknown_prompt` |
| AC-3.3 | `test_rapid_updates_numbered_sequentially` |
| AC-4.1 | `test_get_version_returns_snapshot` |
| AC-4.2 | `test_get_version_returns_404_for_unknown_prompt` |
| AC-4.3 | `test_get_version_returns_404_for_unknown_version` |
| AC-4.4 | `test_get_version_zero_returns_422` |
| AC-4.4 | `test_get_version_negative_returns_422` |
| AC-4.4 | `test_get_version_non_integer_returns_422` |
| AC-4.4 | `test_get_version_invalid_number_checked_before_prompt` |
| AC-5.1 | `test_restore_copies_old_version_and_increments` |
| AC-5.2 | `test_restore_sets_change_note` |
| AC-5.3 | `test_restore_current_version_returns_409` |
| AC-5.4 | `test_restore_returns_404_for_unknown_prompt` |
| AC-5.4 | `test_restore_returns_404_for_unknown_version` |
| AC-5.5 | `test_restore_updates_updated_at_keeps_created_at` |
| AC-5.6 | `test_restore_matching_text_still_creates_version` |
| AC-6.1 | `test_delete_prompt_removes_versions` |
| AC-6.2 | `test_delete_collection_removes_prompt_versions` |
| Data model: current_version | `test_current_version_equals_highest_version_number` |
| Data model: change_note | `test_prompt_response_has_no_change_note` |
| Data model: version created_at | `test_version_1_created_at_matches_prompt` |

