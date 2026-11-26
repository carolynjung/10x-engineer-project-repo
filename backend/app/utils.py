"""Utility functions for PromptLab"""

from typing import List
from app.models import Prompt

def sort_prompts_by_date(prompts: List[Prompt], descending: bool = True) -> List[Prompt]:
    """Sorts a list of prompts based on their creation date.

    Args:
        prompts (List[Prompt]): A list of prompts to sort.
        descending (bool): A flag indicating the sort order. If True, sorts in descending
            order (newest first); otherwise, sorts in ascending order. Default is True.

    Returns:
        List[Prompt]: A sorted list of prompts based on the creation date.

    Raises:
        ValueError: If the prompts list is empty or contains invalid Prompt instances.
    """
    return sorted(prompts, key=lambda p: p.created_at, reverse=descending)


def filter_prompts_by_collection(prompts: List[Prompt], collection_id: str) -> List[Prompt]:
    """Filters prompts by a specific collection ID.

    Args:
        prompts (List[Prompt]): A list of prompts to filter.
        collection_id (str): The collection ID to filter prompts by.

    Returns:
        List[Prompt]: A list of prompts that belong to the specified collection. Returns an
            empty list if no prompts match the collection ID.

    Raises:
        TypeError: If collection_id is not a string.
    """
    if not isinstance(collection_id, str):
        raise TypeError("collection_id must be a string.")

    return [p for p in prompts if p.collection_id == collection_id]


def search_prompts(prompts: List[Prompt], query: str) -> List[Prompt]:
    """
    Filters the provided list of prompts based on a search query.
    The search is case-insensitive and considers both titles and descriptions.

    Args:
        prompts (List[Prompt]): A list of Prompt instances to search through.
        query (str): The query string to search for in both the title and description.
    Returns:
        List[Prompt]: A list of prompts where the query matches either the title or
            description. Returns an empty list if no matches are found.

    Raises:
        ValueError: If prompts is empty or contains non-Prompt instances.
    """
    query_lower = query.lower()
    return [
        p for p in prompts 
        if query_lower in p.title.lower() or 
           (p.description and query_lower in p.description.lower())
    ]


def validate_prompt_content(content: str) -> bool:
    """Check if prompt content is valid.
    
    A valid prompt should not be empty, contain only whitespace, and must have at least 10 characters.

    Args:
        content (str): The prompt content to validate.

    Returns:
        bool: True if the prompt content is valid, otherwise False. If the content is None or only whitespace, returns False.

    Raises:
        None: This function does not raise any exceptions but returns False for invalid content.
    """
    if not content or not content.strip():
        return False
    return len(content.strip()) >= 10

def extract_variables(content: str) -> List[str]:
    """Extract template variables from prompt content.
    
    This function scans the input content for variables formatted as {{variable_name}}.
    It returns a list of variable names extracted from this content. The matching is case-sensitive.

    Args:
        content (str): The string content from which to extract variables.
            Must not be empty; otherwise, an empty list is returned.

    Returns:
        List[str]: A list of variable names extracted from the content. Returns an empty list if no
            variables are found.

    Raises:
        None: This function does not raise any exceptions.
    """
    import re
    pattern = r'\{\{(\w+)\}\}'
    return re.findall(pattern, content)
