from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseProvider(ABC):
    @abstractmethod
    def search_phone(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for phones matching the query.
        Returns a list of dicts:
        [
            {
                "brand": "OnePlus",
                "model": "13",
                "image_url": "...",
                "source": "GSMArena",
                "source_url": "..."
            }
        ]
        """
        pass

    @abstractmethod
    def fetch_phone_details(self, slug: str) -> Dict[str, Any]:
        """
        Fetch details of a phone using the provider-specific identifier/slug.
        """
        pass
