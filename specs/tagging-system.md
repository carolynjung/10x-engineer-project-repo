# Spec: Tagging System

> Status: Draft <br>
> Target: Module 4 <br>
> Owner: Carolyn Jung <br>

## 1. Overview and goals
Users attach short labels (tags) to prompts and filter by them, across collections.

Goals
- Tags are consistent: one canonical form per tag (lowercase, trimmed).
- Filter prompts by one or more tags.
- See every tag in use and how many prompts use it.

Non-goals: tag colors or descriptions, renaming a tag everywhere, tag hierarchies.

## 2. Tag rules (apply everywhere a tag is accepted)
1. Leading and trailing whitespace is trimmed; the tag is lowercased.
2. After that, it must be 1-32 characters and match `^[a-z0-9]+(-[a-z0-9]+)*$`
   (letters, digits, single hyphens between words). Example valid: `code-review`, `gpt4`.
3. Duplicates after normalization are removed silently; first occurrence order kept.
   `["SQL", "sql ", "python"]` is stored as `["sql", "python"]`.
4. A prompt has at most 10 tags (after de-duplication).
5. Changing only tags does not create a version or change current_version.


## 3. User stories (US) and acceptance criteria (AC)

US-1 As a user, I want to add tags when creating a prompt.
- AC-1.1 POST /prompts with `"tags": [" Code-Review ", "python"]` returns 201 with
  `tags == ["code-review", "python"]`.
- AC-1.2 POST /prompts without `tags` returns 201 with `tags == []`.
- AC-1.3 A tag longer than 32 characters returns 422 with
  `detail[0].loc == ["body", "tags", <index>]` and msg
  `"tag must be 1-32 characters"`. Nothing is created.
- AC-1.4 A tag with invalid characters (e.g. `"c++"`, `"two words"`) returns 422 with msg
  `"tag may contain only lowercase letters, digits and single hyphens"`.
- AC-1.5 An empty or whitespace-only tag returns 422 `"tag must be 1-32 characters"`.
- AC-1.6 More than 10 tags after de-duplication returns 422 with
  `loc == ["body", "tags"]` and msg `"tags must contain at most 10 items"`.

US-2 As a user, I want to replace or change tags on an existing prompt.
- AC-2.1 PATCH with `tags` replaces the whole list; returns 200 with the new list.
- AC-2.2 PATCH without `tags` leaves tags unchanged.
- AC-2.3 PUT without `tags` sets tags to `[]` (PUT replaces the whole prompt).
- AC-2.4 PUT and PATCH with a 33-character tag each return 422 with detail[0].loc == ["body", "tags", 0], and the prompt is unchanged.
- AC-2.5 PATCH with "tags": [] returns 200 with tags == [].
- AC-2.6 PATCH with "tags": null returns 422; omit the field to leave tags unchanged.

US-3 As a user, I want to add or remove a single tag without resending the list.
- AC-3.1 POST /prompts/{id}/tags with `{"tags": ["sql"]}` returns 200 with "sql"
  appended if not present; existing tags keep their order.
- AC-3.2 Adding a tag already present returns 200; tags and updated_at are both unchanged.
- AC-3.3 The limit is checked after merging and de-duplication; 9 existing tags + ["sql", "SQL"] gives 10 and succeeds.
- AC-3.4 The path tag is trimmed and lowercased before matching: /tags/%20SQL%20 removes "sql".
- AC-3.5 DELETE of a tag the prompt doesn't have returns 404 `"Tag not found"`.
- AC-3.6 Unknown prompt ID on either endpoint returns 404 `"Prompt not found"`.
- AC-3.7 On success, both endpoints set `updated_at` later than its value before the request; created_at is unchanged.
- AC-3.8 POST /prompts/{id}/tags with {"tags": ["a--b"]} returns 422 and the prompt's tags are unchanged.
- AC-3.9 DELETE /prompts/{id}/tags/a--b returns 422 (invalid tag format); the format check runs before the not-found check.
- AC-3.10 POST /prompts/{id}/tags with {"tags": []} returns 422 with loc ["body", "tags"].

US-4 As a user, I want to filter prompts by tag.
- AC-4.1 GET /prompts?tag=sql returns only prompts whose tags include "sql".
- AC-4.2 GET /prompts?tag=sql&tag=python returns only prompts that have BOTH tags.
- AC-4.3 The query tag is normalized: `?tag=SQL` matches "sql".
- AC-4.4 `tag` combines with `collection_id` and `search` (all filters must match);
  results stay sorted newest first.
- AC-4.5 GET /prompts?tag=a--b returns 422 {"detail": "tag may contain only lowercase letters, digits and single hyphens"}.
- AC-4.6 A valid tag no prompt uses returns 200 with `prompts == []`, `total == 0`.
- AC-4.7 `search` does not match tags (unchanged: title and description only).
- AC-4.8 GET /prompts?tag= returns 422 {"detail": "tag must be 1-32 characters"}.

US-5 As a user, I want to see all tags in use.
- AC-5.1 GET /tags returns 200 `{"tags": [{"name": "sql", "count": 3}, ...], "total": N}`.
- AC-5.2 Sorted by count descending, then name ascending.
- AC-5.3 A tag no longer on any prompt does not appear.
- AC-5.4 With no prompts, returns `{"tags": [], "total": 0}`.

## 4. Data model changes
- `PromptBase`: add `tags: List[str] = Field(default_factory=list)` with a
  per-item validator: `tags: List[Annotated[str, AfterValidator(normalize_tag)]]`.
  Per-item validation is what puts the index in `loc` (AC-1.3). The 10-tag limit and
  de-duplication run in a `field_validator` on the whole list (loc `["body", "tags"]`).
  Pydantic prefixes custom messages with "Value error, ", so tests assert that the
  message text is contained in `msg`, not equal to it.
- `PromptPatch`: `tags: Optional[List[str]] = None` (None = not sent).
- New `TagsAdd` request model: `tags: List[str]` (1-10 items, same rules).
- New `TagCount`: `name: str`, `count: int`. New `TagList`: `tags: List[TagCount]`, `total: int`.
- Storage: no new storage; tags live on each Prompt. GET /tags is computed.
- New utils: `normalize_tag(tag) -> str` (raises ValueError with the messages above),
  `filter_prompts_by_tags(prompts, tags) -> List[Prompt]`,
  `count_tags(prompts) -> List[TagCount]`.

## 5. API endpoints

### Changed: POST /prompts, PUT /prompts/{id}, PATCH /prompts/{id}
Request bodies accept `tags`. Every Prompt response includes `tags`.
```json
{ "title": "SQL explainer", "content": "Explain this query: {{sql}}",
  "tags": ["sql", "explain"] }
```

### Changed: GET /prompts
New query param `tag` (repeatable). Example: `GET /prompts?tag=sql&tag=explain`.

### POST /prompts/{prompt_id}/tags
Request: `{"tags": ["sql"]}` · Response 200: updated Prompt.
Errors: 404 Prompt not found · 422 invalid tag · 422 more than 10 tags.

### DELETE /prompts/{prompt_id}/tags/{tag}
Response 200: updated Prompt.
Errors: 404 Prompt not found · 404 Tag not found · 422 invalid tag format.

### GET /tags
- count is the number of prompts that have the tag, across all collections.

Response 200:
```json
{ "tags": [ {"name": "sql", "count": 3}, {"name": "python", "count": 1} ],
  "total": 2 }
```

## 6. Error conditions and edge cases
| Case | Result |
|---|---|
| Tag 33+ chars | 422 "Tag must be 1-32 characters" |
| Tag "" or "   " | 422 "Tag must be 1-32 characters" |
| Tag "c++", "two words", "a--b", "-x" | 422 format message |
| 11+ tags after de-dup | 422 "tags must contain at most 10 items" |
| ["SQL", "sql"] | stored once as "sql" |
| `tags: null` on POST or PUT | 422 (must be a list) |
| `tags: []` on PATCH | clears all tags, 200 |
| Add existing tag | 200, no change |
| Remove missing tag | 404 "Tag not found" |
| Filter by unused tag | 200, empty list |
| Prompt deleted | its tags disappear from GET /tags |

## 7. Test plan (one test per AC)

| AC | Test |
|---|---|
| AC-1.1 | `test_create_prompt_normalizes_tags` |
| AC-1.2 | `test_create_prompt_without_tags_defaults_to_empty` |
| AC-1.3 | `test_create_prompt_tag_over_32_chars_returns_422` |
| AC-1.4 | `test_create_prompt_tag_invalid_chars_returns_422` (parametrized: `c++`, `two words`, `a--b`, `-x`) |
| AC-1.5 | `test_create_prompt_blank_tag_returns_422` |
| AC-1.6 | `test_create_prompt_more_than_10_tags_returns_422` |
| Rule 3 (de-duplication) | `test_create_prompt_deduplicates_tags` |
| Edge: `tags: null` on POST | `test_create_prompt_tags_null_returns_422` |
| AC-2.1 | `test_patch_tags_replaces_list` |
| AC-2.2 | `test_patch_without_tags_keeps_tags` |
| AC-2.3 | `test_put_without_tags_clears_tags` |
| AC-2.4 | `test_put_tag_over_32_chars_returns_422` |
| AC-2.4 | `test_patch_tag_over_32_chars_returns_422` |
| AC-2.5 | `test_patch_empty_tags_clears_all` |
| AC-2.6 | `test_patch_tags_null_returns_422` |
| AC-3.1 | `test_add_tag_appends_and_keeps_order` |
| AC-3.2 | `test_add_existing_tag_leaves_tags_and_updated_at_unchanged` |
| AC-3.3 | `test_add_tag_over_limit_returns_422_and_no_change` |
| AC-3.3 | `test_add_tag_limit_counted_after_merge_and_dedup` |
| AC-3.4 | `test_remove_tag` |
| AC-3.4 | `test_remove_tag_normalizes_path_tag` |
| AC-3.4 | `test_remove_tag_trims_path_tag` |
| AC-3.5 | `test_remove_missing_tag_returns_404` |
| AC-3.6 | `test_add_tag_returns_404_for_unknown_prompt` |
| AC-3.6 | `test_remove_tag_returns_404_for_unknown_prompt` |
| AC-3.7 | `test_add_tag_updates_updated_at` |
| AC-3.8 | `test_add_invalid_tag_returns_422` |
| AC-3.9 | `test_remove_invalid_tag_format_returns_422` |
| AC-3.10 | `test_add_empty_tag_list_returns_422` |
| AC-4.1 | `test_filter_by_single_tag` |
| AC-4.2 | `test_filter_by_two_tags_requires_both` |
| AC-4.3 | `test_filter_tag_is_case_insensitive` |
| AC-4.4 | `test_filter_tag_combines_with_collection_and_search` |
| AC-4.5 | `test_filter_invalid_tag_returns_422` |
| AC-4.6 | `test_filter_unused_tag_returns_empty` |
| AC-4.7 | `test_search_does_not_match_tags` |
| AC-4.8 | `test_filter_empty_tag_returns_422` |
| AC-5.1 | `test_list_tags_returns_counts` |
| AC-5.2 | `test_list_tags_sorted_by_count_then_name` |
| AC-5.3 | `test_list_tags_omits_unused_tag` |
| AC-5.4 | `test_list_tags_empty` |
| Data model: count across collections | `test_list_tags_counts_across_collections` |
| Edge: prompt deleted | `test_list_tags_excludes_deleted_prompt` |