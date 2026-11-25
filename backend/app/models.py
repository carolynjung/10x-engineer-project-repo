"""Pydantic models for PromptLab"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import uuid4


def generate_id() -> str:
    """
    Generates a new random UUID4.

    Returns:
        str: A string representation of the randomly generated UUID4.
    """
    return str(uuid4())


def get_current_time() -> datetime:
    """
    Retrieves the current UTC time as a naive datetime object.

    This function returns the current UTC time without timezone information, which is useful for cases where timezone awareness is not necessary.

    Returns:
        datetime: The current UTC time without timezone information.
    """
    return datetime.utcnow()


# ============== Prompt Models ==============

class PromptBase(BaseModel):
    """
    Base model for a prompt containing essential metadata.

    This model enforces validation on the prompt's title and content, ensuring that both fields meet minimum length requirements. It also supports optional metadata fields such as description and collection ID.

    Attributes:
        title (str): The title of the prompt, required, limited to 1-200 characters.
        content (str): The content of the prompt, required, must be at least 1 character long.
        description (Optional[str]): An optional description of the prompt, capped at 500 characters.
        collection_id (Optional[str]): An optional identifier for the collection this prompt belongs to.
    """
    title: str = Field(..., min_length=1, max_length=200, description="The title of the prompt, required, limited to 1-200 characters.")
    content: str = Field(..., min_length=1, description="The content of the prompt, required, must be at least 1 character long.")
    description: Optional[str] = Field(None, max_length=500, description="An optional description of the prompt, capped at 500 characters.")
    collection_id: Optional[str] = Field(None, description="An optional identifier for the collection this prompt belongs to.")


class PromptCreate(PromptBase):
    """
    Model for creating a new prompt. It inherits from PromptBase and shares its validation rules.

    This model is used when creating a new prompt object via the API.

    Attributes:
        title (str): The title of the prompt, required, limited to 1-200 characters.
        content (str): The content of the prompt, required, must be at least 1 character long.
        description (Optional[str]): An optional description of the prompt, capped at 500 characters.
        collection_id (Optional[str]): An optional collection identifier associated with the prompt.
    """
    pass

class PromptUpdate(PromptBase):
    """
    Model for updating an existing prompt. It inherits from PromptBase, allowing users to modify fields of a prompt while maintaining validation rules.

    This model is particularly useful for API requests that partially update a prompt's attributes, including title, content, description, and collection_id.

    Attributes:
        title (Optional[str]): An optional title of the prompt, can be up to 200 characters long.
        content (Optional[str]): An optional content of the prompt, must be at least 1 character long if provided.
        description (Optional[str]): An optional description of the prompt, capped at 500 characters if provided.
        collection_id (Optional[str]): An optional identifier for the collection this prompt belongs to.
    """
    pass

class PromptPatch(BaseModel):
    """
    Represents a partial update model for a prompt, allowing specific attributes to be modified.

    This model is intended for API requests where users want to update certain fields of a prompt without changing all attributes.

    Attributes:
        title (Optional[str]): An optional title of the prompt, can be up to 200 characters long.
        content (Optional[str]): An optional content of the prompt, must be at least 1 character long if provided.
        description (Optional[str]): An optional description of the prompt, capped at 500 characters if provided.
        collection_id (Optional[str]): An optional identifier for the collection this prompt belongs to.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="An optional title of the prompt, can be up to 200 characters long.")
    content: Optional[str] = Field(None, min_length=1, description="An optional content of the prompt, must be at least 1 character long if provided.")
    description: Optional[str] = Field(None, max_length=500, description="An optional description of the prompt, capped at 500 characters if provided.")
    collection_id: Optional[str] = Field(None, description="An optional identifier for the collection this prompt belongs to.")

class Prompt(PromptBase):
    """
    Represents a prompt in the system, containing its unique identifier and timestamps for creation and updates.

    This model inherits from PromptBase, which includes attributes for metadata such as title and content. It automatically generates an ID and timestamps when a prompt object is created.

    Attributes:
        id (str): A unique identifier for the prompt, generated upon instantiation.
        created_at (datetime): The timestamp indicating when the prompt was created, automatically set to the current time.
        updated_at (datetime): The timestamp indicating the last update time of the prompt, automatically set to the current time upon creation.

    Config:
        from_attributes (bool): Config setting that allows attributes to be populated from incoming data.
    """
    id: str = Field(default_factory=generate_id, description="A unique identifier for the prompt, generated upon instantiation.")
    created_at: datetime = Field(default_factory=get_current_time, description="The timestamp indicating when the prompt was created, automatically set to the current time.")
    updated_at: datetime = Field(default_factory=get_current_time, description="The timestamp indicating the last update time of the prompt, automatically set to the current time upon creation.")

    class Config:
        from_attributes = True


# ============== Collection Models ==============

class CollectionBase(BaseModel):
    """
    Base model for a collection with essential attributes.

    This model defines the attributes for a collection, ensuring that the collection's name is not empty and has a character limit, and the description is optional.

    Attributes:
        name (str): The name of the collection, required, must be between 1 and 100 characters long.
        description (Optional[str]): An optional description of the collection, limited to 500 characters.
    """
    name: str = Field(..., min_length=1, max_length=100, description="The name of the collection, required, must be between 1 and 100 characters long.")
    description: Optional[str] = Field(None, max_length=500, description="An optional description of the collection, limited to 500 characters.")


class CollectionCreate(CollectionBase):
    """
    Model for creating a new collection, inheriting attributes and validation from CollectionBase.

    This model is used specifically for requests to create new collections via the API but does not introduce any new attributes.
    """
    pass


class Collection(CollectionBase):
    """
    Represents a collection in the system with an identifier and timestamps for creation.

    This model inherits from CollectionBase, which includes attributes for the collection's name and description. It automatically generates an ID and timestamps when a collection object is created.

    Attributes:
        id (str): A unique identifier for the collection, generated upon instantiation.
        created_at (datetime): The timestamp indicating when the collection was created, automatically set to the current time.
    """
    id: str = Field(default_factory=generate_id, description="A unique identifier for the collection, generated upon instantiation.")
    created_at: datetime = Field(default_factory=get_current_time, description="The timestamp indicating when the collection was created, automatically set to the current time.")

    class Config:
        from_attributes = True

class CollectionPatch(BaseModel):
    """
    Represents a partial update model for a collection, allowing specific attributes to be modified.

    This model is intended for API requests where users wish to update certain fields of a collection without changing all attributes. The name and description can be provided separately.

    Attributes:
        name (Optional[str]): An optional name for the collection, limited to 1-100 characters if provided.
        description (Optional[str]): An optional description of the collection, capped at 500 characters if provided.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    
# ============== Response Models ==============

class PromptList(BaseModel):
    """
    Represents a list of prompts along with the total count.

    This model is used to encapsulate the response containing multiple prompts and the total number of prompts available.

    Attributes:
        prompts (List[Prompt]): A list of prompts included in the response.
        total (int): The total number of prompts available. This may differ from the length of the prompts list if paginated.
    """
    prompts: List[Prompt] = Field(..., description="A list of prompts included in the response.")
    total: int = Field(..., description="The total number of prompts available, which may differ from the length of the prompts list if paginated.")

class CollectionList(BaseModel):
    """
    Represents a list of collections along with the total count.

    This model is used to encapsulate the response containing multiple collections and the total number of collections available.

    Attributes:
        collections (List[Collection]): A list of collections included in the response.
        total (int): The total number of collections available. This may differ from the length of the collections list if paginated.
    """
    collections: List[Collection] = Field(..., description="A list of collections included in the response.")
    total: int = Field(..., description="The total number of collections available in the system, which may differ from the length of the collections list if paginated.")

class HealthResponse(BaseModel):
    """
    Represents the health status of the service.

    This model provides information on the status of the service and its version. It's typically used for health checks.

    Attributes:
        status (str): The current status of the service, typically 'healthy' or 'unhealthy'.
        version (str): The version of the service currently running.
    """
    version: str = Field(..., description="The version of the service currently running.")
    status: str = Field(..., description="The current status of the service, indicating service health.")

