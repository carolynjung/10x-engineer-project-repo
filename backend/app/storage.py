"""In-memory storage for PromptLab

This module provides simple in-memory storage for prompts and collections.
In a production environment, this would be replaced with a database.
"""

from typing import Dict, List, Optional
from app.models import Prompt, Collection

class Storage:
    """
    In-memory storage for prompts and collections.

    This class manages the storage of prompts and collections using
    in-memory dictionaries. In a production environment, it is expected
    that this would be replaced with a persistent database.
    """

    def __init__(self):
        """
        Initializes a new instance of the Storage class.

        Sets up empty dictionaries for storing prompts and collections.
        """
        self._prompts: Dict[str, Prompt] = {}
        self._collections: Dict[str, Collection] = {}
    
    # ============== Prompt Operations ==============
    
    def create_prompt(self, prompt: Prompt) -> Prompt:
        """
        Stores the given prompt in the internal storage using its ID.

        Args:
            prompt (Prompt): The Prompt object to create and store.
        Returns:
            Prompt: The stored Prompt object with the same ID.
        """
        self._prompts[prompt.id] = prompt
        return prompt
    
    def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """
        Retrieves a prompt from the internal storage based on the provided ID.

        Args:
            prompt_id (str): The ID of the prompt to retrieve.
        Returns:
            Optional[Prompt]: The Prompt object if found, or None if not.
        """
        return self._prompts.get(prompt_id)
    
    def get_all_prompts(self) -> List[Prompt]:
        """
        Returns a list of all stored prompts in the internal storage.

        Returns:
            List[Prompt]: A list of all Prompt objects.
        """
        return list(self._prompts.values())
    
    def update_prompt(self, prompt_id: str, prompt: Prompt) -> Optional[Prompt]:
        """
        Updates the prompt associated with the given ID in the internal storage.
        If the prompt ID does not exist, no changes are made.

        Args:
            prompt_id (str): The ID of the prompt to update.
            prompt (Prompt): The new Prompt object to store.

        Returns:
            Optional[Prompt]: The updated Prompt object if the ID exists, or None if not.
        """
        if prompt_id not in self._prompts:
            return None
        self._prompts[prompt_id] = prompt
        return prompt
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """
        Deletes the prompt associated with the given ID from the internal storage.
        Returns True if the prompt was successfully deleted, False otherwise.

        Args:
            prompt_id (str): The ID of the prompt to delete.

        Returns:
            bool: True if the prompt was deleted, False if the ID was not found.
        """
        if prompt_id in self._prompts:
            del self._prompts[prompt_id]
            return True
        return False
    
    # ============== Collection Operations ==============
    
    def create_collection(self, collection: Collection) -> Collection:
        """
        Stores the given collection in the internal storage using its ID.

        This method adds the provided Collection object to the
        internal storage, allowing retrieval and management of
        collections.
    
        Args:
            collection (Collection): The Collection object to create and store.

        Returns:
            Collection: The stored Collection object with the same ID.
        """
        self._collections[collection.id] = collection
        return collection
    
    def get_collection(self, collection_id: str) -> Optional[Collection]:
        """
        Retrieves a collection from the internal storage based on the provided ID.

        Args:
            collection_id (str): The ID of the collection to retrieve.

        Returns:
            Optional[Collection]: The Collection object if found, or None if not.

        Note:
            Collection IDs are case-sensitive, ensure that the exact ID is provided.
        """
        return self._collections.get(collection_id)
    
    def get_all_collections(self) -> List[Collection]:
        """
        Retrieves all collections from the internal storage.

        This returns a list of all Collection objects stored
        in the internal storage. The list will be empty if no collections
        are present.

        Returns:
            List[Collection]: A list of all Collection objects. If no collections
            are stored, an empty list is returned.
        """
        return list(self._collections.values())
    
    def delete_collection(self, collection_id: str) -> bool:
        """
        Deletes a collection associated with the given ID from the internal storage.

        This operation will succeed only if the collection ID exists in
        the internal storage. It returns True if the deletion
        was successful, or False if the collection ID was not found.

        Args:
            collection_id (str): The ID of the collection to delete.
        Returns:
            bool: True if the collection was deleted, False if the ID was not found.

        Note:
            Collection IDs are case-sensitive; ensure that the correct ID is provided.
        """
        if collection_id in self._collections:
            del self._collections[collection_id]
            return True
        return False
    
    def get_prompts_by_collection(self, collection_id: str) -> List[Prompt]:
        """
        Retrieves all prompts that belong to the specified collection.

        This method filters prompts stored in memory by their collection ID.
        If no prompts match the given collection ID, an empty list is returned.

        Args:
            collection_id (str): The ID of the collection for which prompts are to be retrieved.

        Returns:
            List[Prompt]: A list of Prompt objects associated with the specified collection ID.
            If no prompts are found, an empty list is returned.
        """
        return [p for p in self._prompts.values() if p.collection_id == collection_id]
    
    # ============== Utility ==============
    
    def clear(self):
        """
        Clears all stored prompts and collections from memory.

        This method resets the internal storage by removing all entries
        and does not return any value. It effectively empties the storage.
        """
        self._prompts.clear()
        self._collections.clear()

# Global storage instance
storage = Storage()

