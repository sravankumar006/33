import re

def normalize_ram(ram_val) -> int:
    """
    Normalizes RAM to integer GB.
    Input can be a string like "8GB", "12 GB", "512MB", or an integer.
    """
    if isinstance(ram_val, (int, float)):
        return int(ram_val)
    if not ram_val:
        return 0
    ram_str = str(ram_val).strip().lower()
    
    # Try parsing patterns like "12gb", "12 gb", "12"
    match = re.search(r'(\d+)\s*(gb|mb|tb)?', ram_str)
    if not match:
        return 0
        
    num = int(match.group(1))
    unit = match.group(2) or "gb"
    
    if unit == "tb":
        return num * 1024
    elif unit == "mb":
        return max(1, round(num / 1024))
    return num

def normalize_storage(storage_val) -> int:
    """
    Normalizes storage to integer GB.
    Input can be a string like "128GB", "1 TB", "256 GB", or an integer.
    """
    if isinstance(storage_val, (int, float)):
        return int(storage_val)
    if not storage_val:
        return 0
    storage_str = str(storage_val).strip().lower()
    
    match = re.search(r'(\d+)\s*(gb|tb|mb)?', storage_str)
    if not match:
        return 0
        
    num = int(match.group(1))
    unit = match.group(2) or "gb"
    
    if unit == "tb":
        return num * 1024
    elif unit == "mb":
        return max(1, round(num / 1024))
    return num

def clean_color(color_str: str) -> str:
    """
    Cleans up a color string.
    """
    if not color_str:
        return ""
    # Strip whitespace, convert to title case
    return color_str.strip().title()

def generate_variant_slug(phone_slug: str, ram_gb: int, storage_gb: int, color: str | None = None) -> str:
    """
    Generates a unique slug for a variant.
    Format: {phone_slug}-{ram_gb}gb-{storage_gb}gb[-{color_slug}]
    """
    slug = f"{phone_slug}-{ram_gb}gb-{storage_gb}gb"
    if color:
        # Slugify color: lowercase, replace non-alphanumeric with hyphen, strip multiple hyphens
        color_slug = re.sub(r'[^a-z0-9]+', '-', color.lower()).strip('-')
        if color_slug:
            slug += f"-{color_slug}"
    return slug
