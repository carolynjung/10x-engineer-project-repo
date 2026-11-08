# SYSTEM MODEL

## Architecture

PromptLab is an internal tool designed for AI engineers to **store, organize, and manage their prompts**. The backend is built using **Python** with the **FastAPI** framework, providing a fast and efficient API service. The service is structured into multiple components:

- **API Endpoints**: Expose functionalities for managing prompts and collections.
- **Data Models**: Define the structure of prompts and collections, ensuring data validation.
- **Storage Layer**: Implements an in-memory storage solution for storing prompts and collections.

## Entry Points

The following table lists all routes exposed by the application, including their HTTP methods, paths, handler function names, request body/query parameters, response models, status codes, and purposes.

| HTTP Method | Path                      | Handler Function      | Request Body / Query Params                             | Response Model         | Status Codes            | Purpose                                                  |
|-------------|---------------------------|-----------------------|--------------------------------------------------------|-------------------------|-------------------------|----------------------------------------------------------|
| GET         | /health                  | health_check          | None                                                   | HealthResponse          | 200 OK                  | Check the health status of the API.                     |
| GET         | /prompts                 | list_prompts          | Query: collection_id (Optional), search (Optional)    | PromptList              | 200 OK                  | List all prompts, optionally filtered by collection or search. |
| GET         | /prompts/{prompt_id}     | get_prompt            | Path: prompt_id (Required)                             | Prompt                  | 200 OK, 404 Not Found   | Retrieve a specific prompt by its ID.                   |
| POST        | /prompts                 | create_prompt         | Request Body: PromptCreate                             | Prompt                  | 201 Created             | Create a new prompt.                                     |
| PUT         | /prompts/{prompt_id}     | update_prompt         | Path: prompt_id (Required), Request Body: PromptUpdate | Prompt                  | 200 OK, 404 Not Found, 400 Bad Request | Update an existing prompt by its ID.                   |
| DELETE      | /prompts/{prompt_id}     | delete_prompt         | Path: prompt_id (Required)                             | None                    | 204 No Content, 404 Not Found | Delete a specific prompt by its ID.                     |
| GET         | /collections              | list_collections      | None                                                   | CollectionList          | 200 OK                  | List all collections.                                     |
| GET         | /collections/{collection_id} | get_collection        | Path: collection_id (Required)                         | Collection              | 200 OK, 404 Not Found   | Retrieve a specific collection by its ID.                |
| POST        | /collections              | create_collection     | Request Body: CollectionCreate                         | Collection              | 201 Created             | Create a new collection.                                  |
| DELETE      | /collections/{collection_id} | delete_collection     | Path: collection_id (Required)                         | None                    | 204 No Content, 404 Not Found | Delete a specific collection by its ID.                  |

## Data Flow

### Creating a Prompt (POST)

1. **Client**: Sends a POST request to `/prompts` with prompt details in the request body.
2. **Route**: `create_prompt()` handles the request.
3. **Validation**: Validates the request body against the `PromptCreate` model.
4. **Storage**: Calls `storage.create_prompt(prompt)` to save the new prompt.
5. **Response**: Returns the created `Prompt` object with a 201 Created status.

### Retrieving a Prompt by ID (GET)

1. **Client**: Sends a GET request to `/prompts/{prompt_id}` with the prompt ID in the URL.
2. **Route**: `get_prompt()` handles the request.
3. **Validation**: Retrieves the prompt using `storage.get_prompt(prompt_id)`.
4. **Storage**: Returns the `Prompt` object or `None` if it doesn't exist.
5. **Response**: Returns the `Prompt` object with a 200 OK status or 404 Not Found if the prompt does not exist.

## Models and Relationships

### Prompt Models

- **PromptBase**: Base model defining common fields (`title`, `content`, `description`, `collection_id`).
- **PromptCreate**: Inherits from `PromptBase` for creating new prompts.
- **PromptUpdate**: Inherits from `PromptBase` for updating existing prompts.
- **Prompt**: Includes fields for `id`, `created_at`, and `updated_at`.

### Collection Models

- **CollectionBase**: Base model defining `name` and `description`.
- **CollectionCreate**: Inherits from `CollectionBase` for creating new collections.
- **Collection**: Includes fields for `id` and `created_at`.

### Relationship

- **Type**: One-to-Many
  - Each `Collection` can contain many `Prompts`, but each `Prompt` may belong to one collection, indicated by its `collection_id`.
- **Integrity Enforcement**: Currently, the application does not enforce integrity. If a collection is deleted, prompts that reference it may remain with orphaned `collection_id` values.

## Storage Layer

The storage layer provides an in-memory implementation using two dictionaries: `_prompts` for storing prompts and `_collections` for storing collections. 

### Operations

- **Create**: Prompts and collections are stored in their respective dictionaries.
- **Read**: Methods retrieve prompts and collections by their IDs or return lists of all stored entities.
- **Update**: Existing prompts can be updated by their ID.
- **Delete**: Prompts and collections can be removed by their IDs.

### Limitations

| Limitation          | Risk                                                     |
|---------------------|---------------------------------------------------------|
| **Persistence**     | Data is lost on application restart due to in-memory storage. |
| **Data Integrity**  | Lack of referential integrity can lead to orphaned references if collections are deleted while prompts still reference them. |
| **Scalability**     | Performance may degrade as the number of prompts and collections increases, leading to slower access times. |
| **Querying/Filtering** | Limited querying capabilities; currently, it only supports basic filtering without advanced search functions. |
| **Concurrency**     | The storage does not manage concurrent access, which may lead to data inconsistencies in multi-threaded scenarios. |

## External Dependencies

| Dependency       | Version    | Category | Used In                        | Purpose                                                     | Flag                   |
|-------------------|------------|----------|-------------------------------|-------------------------------------------------------------|------------------------|
| Python            | 3.10+      | Runtime  | N/A                           | The primary programming language for the application.       |                        |
| FastAPI           | 0.109.0    | Runtime  | `main.py`, `api.py`          | Framework for building APIs.                                |                        |
| Uvicorn           | 0.27.0     | Runtime  | `main.py`                    | ASGI server implementation to run the FastAPI application.  |                        |
| Pydantic          | >=2.10     | Runtime  | `models.py`, `api.py`        | Data validation and settings management using type annotations. |                        |
| pytest            | 7.4.4      | Dev      | `test_api.py`, `conftest.py` | Testing framework for running unit tests.                   |                        |
| pytest-cov        | 4.1.0      | Dev      | `tests`                       | Plugin for measuring code coverage of tests.                |                        |
| httpx             | 0.26.0     | Dev      | _None (not used)             | HTTP client for making asynchronous requests.               | **Listed but not imported** |
| SQLAlchemy (if implemented) | 1.4.22+ | Runtime  | _None (not used)             | SQL toolkit and ORM library for potential future use.       | **Listed but not imported** |
| .env              | N/A        | Config   | _N/A                          | For managing environment variables in the project.          |                        |
| CORS Middleware    | N/A        | Runtime  | `api.py`                     | Middleware for handling CORS requests.                      |                        |


## Context Strategy

The exploration of the codebase for the PromptLab application involved analyzing various components based on their size, complexity, and interdependencies. 
Using a context strategy allowed for understanding the PromptLab application without having to analyzed all unlinked files.

Here’s the context for each area explored:

### Architecture
- **Strategy**: Entire Repository (@Entire Codebase)
- **Reason**: Understanding the overall architecture required `main.py`, `api.py`, and `models.py` to grasp how they work together to form the application's structure.

### Entry Points
- **Strategy**: Single File (@api.py)
- **Reason**: The entry points, that is, routes exposed by the application, are exclusively defined in the `api.py` file.

### Data Flow
- **Strategy**: Entire Repository
- **Reason**: Tracing how requests travel from routes to storage required context for routes from `api.py` and context for data handling from `storage.py`.

### Models and Relationships
- **Strategy**: Single File (@models.py)
- **Reason**: The data models and their relationships are defined within `models.py`, that is, this is the only file for context to understand the structure and connections between prompts and collections.

### Storage Layer
- **Strategy**: Single File (@storage.py)
- **Reason**: The storage layer implementation, that is, all functions related to data management are in `storage.py` as well as how it operates and its limitations.

### External Dependencies
- **Strategy**: Single File (@requirements.txt and some context from @main.py)
- **Reason**: The list of external dependencies is specified in `requirements.txt`, along with relevant imports in `main.py`, that is they show the libraries and frameworks utilized by the application.
