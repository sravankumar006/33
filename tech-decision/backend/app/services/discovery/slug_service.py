import re

class SlugService:
    @classmethod
    def generate(cls, brand: str, model: str) -> str:
        """
        Generate a stable, lowercase, hyphen-separated slug for a phone.
        Example:
            brand="Samsung", model="Galaxy S25 Ultra" -> "samsung-galaxy-s25-ultra"
        """
        # Combine brand and model
        combined = f"{brand} {model}"
        
        # Lowercase the entire string
        s = combined.lower()
        
        # Remove any character that is not alphanumeric, a space, or a hyphen
        s = re.sub(r"[^a-z0-9\s\-]", "", s)
        
        # Replace spaces, underscores, and multiple hyphens with a single hyphen
        s = re.sub(r"[\s_]+", "-", s)
        s = re.sub(r"\-+", "-", s)
        
        # Strip any leading or trailing hyphens
        return s.strip("-")
