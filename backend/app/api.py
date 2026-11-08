"""FastAPI routes for PromptLab"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.models import (
    Prompt, PromptCreate, PromptUpdate,
    Collection, CollectionCreate,
    PromptList, CollectionList, HealthResponse,
    get_current_time
)
from app.storage import storage
from app.utils import sort_prompts_by_date, filter_prompts_by_collection, search_prompts
from app import __version__


app = FastAPI(
    title="PromptLab API",
    description="AI Prompt Engineering Platform",
    version=__version__
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Health Check ==============

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="healthy", version=__version__)


# ============== Prompt Endpoints ==============

@app.get("/prompts", response_model=PromptList)
def list_prompts(
    collection_id: Optional[str] = None,
    search: Optional[str] = None
):
    """List all prompts optionally filtered by collection or search query.

    This endpoint retrieves prompts, filters them by the specified collection ID,
    or searches based on a query. The results are sorted in descending order
    by creation date (newest first).

    Args:
        collection_id: An optional collection ID to filter prompts.
        search: An optional search string to filter prompts.

    Returns:
        A PromptList object containing the filtered and sorted prompts.

    Raises:
        None
    """
    prompts = storage.get_all_prompts()
    
    # Filter by collection if specified
    if collection_id:
        prompts = filter_prompts_by_collection(prompts, collection_id)
    
    # Search if query provided
    if search:
        prompts = search_prompts(prompts, search)
    
    # Sort by date (newest first)
    # Note: There might be an issue with the sorting...
    prompts = sort_prompts_by_date(prompts, descending=True)
    
    return PromptList(prompts=prompts, total=len(prompts))


@app.get("/prompts/{prompt_id}", response_model=Prompt)
def get_prompt(prompt_id: str):
    """Retrieve a prompt by its unique identifier.

    Args:
        prompt_id: The unique identifier of the prompt to retrieve.

    Returns:
        The Prompt object if found.

    Raises:
        HTTPException: If the prompt with the given ID does not exist (404 Not Found).
    """
    prompt = storage.get_prompt(prompt_id)
    # Check if prompt is not found
    # None leads to a TypeError
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # Only if found
    return prompt


@app.post("/prompts", response_model=Prompt, status_code=201)
def create_prompt(prompt_data: PromptCreate):
    # Validate collection exists if provided
    if prompt_data.collection_id:
        collection = storage.get_collection(prompt_data.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")
    
    prompt = Prompt(**prompt_data.model_dump())
    return storage.create_prompt(prompt)


@app.put("/prompts/{prompt_id}", response_model=Prompt)
def update_prompt(prompt_id: str, prompt_data: PromptUpdate):
    """Update an existing prompt by its unique identifier.

    This endpoint updates only the fields that are provided in the request body
    and updates the updated_at timestamp to the current time.

    Args:
        prompt_id: The unique identifier of the prompt to update.
        prompt_data: An object containing the fields to update in the prompt.

    Returns:
        The updated Prompt object.

    Raises:
        HTTPException: If the prompt with the given ID does not exist (404 Not Found).
        HTTPException: If the prompt is associated with a non-existent collection (400 Bad Request).
    """
    existing = storage.get_prompt(prompt_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Validate collection if provided
    if prompt_data.collection_id:
        collection = storage.get_collection(prompt_data.collection_id)
        if not collection:
            raise HTTPException(status_code=400, detail="Collection not found")
    
    # Update the prompt; set updated_at to the current time
    updated_prompt = Prompt(
        id=existing.id,
        title=prompt_data.title,
        content=prompt_data.content,
        description=prompt_data.description,
        collection_id=prompt_data.collection_id,
        created_at=existing.created_at,
        updated_at=get_current_time()
    )
    
    return storage.update_prompt(prompt_id, updated_prompt)


# NOTE: PATCH endpoint is missing! Students need to implement this.
# It should allow partial updates (only update provided fields)


@app.delete("/prompts/{prompt_id}", status_code=204)
def delete_prompt(prompt_id: str):
    if not storage.delete_prompt(prompt_id):
        raise HTTPException(status_code=404, detail="Prompt not found")
    return None


# ============== Collection Endpoints ==============

@app.get("/collections", response_model=CollectionList)
def list_collections():
    collections = storage.get_all_collections()
    return CollectionList(collections=collections, total=len(collections))


@app.get("/collections/{collection_id}", response_model=Collection)
def get_collection(collection_id: str):
    collection = storage.get_collection(collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


@app.post("/collections", response_model=Collection, status_code=201)
def create_collection(collection_data: CollectionCreate):
    collection = Collection(**collection_data.model_dump())
    return storage.create_collection(collection)


@app.delete("/collections/{collection_id}", status_code=204)
def delete_collection(collection_id: str):
    """Delete a collection and its associated prompts by its unique identifier.

    This endpoint removes a collection from storage and also deletes any
    associated prompts to maintain data integrity.

    Args:
        collection_id: The unique identifier of the collection to delete.

    Returns:
        None

    Raises:
        HTTPException: If the collection with the given ID does not exist (404 Not Found).
    """
    if not storage.delete_collection(collection_id):
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Delete all of the prompts associated with the deleted collection
    prompts_to_delete = storage.get_prompts_by_collection(collection_id)
    for prompt in prompts_to_delete:
        storage.delete_prompt(prompt.id)
    
    return None

@app.patch("/prompts/{prompt_id}", response_model=Prompt)
def partial_update_prompt(prompt_id: str, prompt_data: PromptUpdate):
    """Partially update a prompt by its unique identifier.

    This endpoint allows updating only the fields that are provided in the request body.
    The updated_at timestamp is always set to the current time on successful updates.

    Args:
        prompt_id: The unique identifier of the prompt to update.
        prompt_data: An object containing the fields to update in the prompt.

    Returns:
        The updated Prompt object.

    Raises:
        HTTPException: If the prompt with the given ID does not exist (404 Not Found).
    """
    existing = storage.get_prompt(prompt_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Prompt not found")

    # Update only the fields given
    if prompt_data.title is not None:
        existing.title = prompt_data.title
    if prompt_data.content is not None:
        existing.content = prompt_data.content
    if prompt_data.description is not None:
        existing.description = prompt_data.description
    if prompt_data.collection_id is not None:
        existing.collection_id = prompt_data.collection_id

    # Update the updated_at timestamp
    existing.updated_at = get_current_time()

    # Save the updated prompt to storage
    return storage.update_prompt(prompt_id, existing)