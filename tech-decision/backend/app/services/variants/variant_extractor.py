import re
import logging
from app.services.variants.variant_normalizer import clean_color

logger = logging.getLogger("uvicorn.error")

def extract_memory_variants(raw_memory_str: str) -> list[tuple[int, int]]:
    """
    Parses strings like:
      "128GB 8GB RAM, 256GB 8GB RAM, 256GB 12GB RAM, 512GB 12GB RAM"
      "64GB 4GB RAM, 128GB 4GB RAM"
      "128GB 6GB RAM (UFS 2.2)"
    Returns a list of tuples: (ram_gb, storage_gb)
    """
    if not raw_memory_str:
        return []
        
    variants = []
    # Split by comma or semicolon or newline
    parts = re.split(r'[,;\n]', raw_memory_str)
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        # Match patterns like "256GB 12GB RAM" or "256 GB 12 GB RAM" or "256GB/12GB"
        # We can look for storage and RAM.
        # Storage is typically first, RAM is typically second (followed by "RAM" or similar).
        # E.g., "(\d+)\s*(GB|TB)\s*(\d+)\s*(GB|MB)?\s*(?:RAM)?"
        match = re.search(r'(\d+)\s*(gb|tb)\s+(?:or\s+)?(\d+)\s*(gb|mb)?\s*(?:ram)?', part, re.IGNORECASE)
        if match:
            storage_num = int(match.group(1))
            storage_unit = match.group(2).lower()
            ram_num = int(match.group(3))
            ram_unit = (match.group(4) or "gb").lower()
            
            storage_gb = storage_num * 1024 if storage_unit == "tb" else storage_num
            ram_gb = ram_num
            if ram_unit == "mb":
                ram_gb = max(1, round(ram_num / 1024))
                
            variants.append((ram_gb, storage_gb))
            continue
            
        # Try another pattern: "(\d+)\s*(GB|TB)\s*(?:storage)?\s*(?:with|\+|,)?\s*(\d+)\s*(GB|MB)\s*RAM"
        match2 = re.search(r'(\d+)\s*(gb|tb).*?(\d+)\s*(gb|mb)\s*ram', part, re.IGNORECASE)
        if match2:
            storage_num = int(match2.group(1))
            storage_unit = match2.group(2).lower()
            ram_num = int(match2.group(3))
            ram_unit = match2.group(4).lower()
            
            storage_gb = storage_num * 1024 if storage_unit == "tb" else storage_num
            ram_gb = ram_num
            if ram_unit == "mb":
                ram_gb = max(1, round(ram_num / 1024))
                
            variants.append((ram_gb, storage_gb))
            continue

        # If it doesn't match above, but has a storage and RAM somewhere
        # e.g., "128GB, 8GB RAM"
        storage_match = re.search(r'(\d+)\s*(gb|tb)(?!\s*ram)', part, re.IGNORECASE)
        ram_match = re.search(r'(\d+)\s*(gb|mb)\s*ram', part, re.IGNORECASE)
        if storage_match and ram_match:
            storage_num = int(storage_match.group(1))
            storage_unit = storage_match.group(2).lower()
            ram_num = int(ram_match.group(1))
            ram_unit = ram_match.group(2).lower()
            
            storage_gb = storage_num * 1024 if storage_unit == "tb" else storage_num
            ram_gb = ram_num
            if ram_unit == "mb":
                ram_gb = max(1, round(ram_num / 1024))
            variants.append((ram_gb, storage_gb))
            
    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for v in variants:
        if v not in seen:
            seen.add(v)
            deduped.append(v)
            
    return deduped

def extract_colors(raw_colors_str: str) -> list[str]:
    """
    Parses strings like:
      "Black, White, Blue"
      "Phantom Black, Cream, Green, Lavender"
    Returns a list of cleaned color names.
    """
    if not raw_colors_str:
        return []
    
    # Split by comma or semicolon or slash
    parts = re.split(r'[,;/]', raw_colors_str)
    colors = []
    for part in parts:
        cleaned = part.strip()
        # Filter out marketing / descriptor words that aren't colors, or things like "etc."
        if not cleaned or cleaned.lower() in ["etc", "etc.", "other colors", "others"]:
            continue
        # Clean color using our normalizer
        colors.append(clean_color(cleaned))
        
    return colors

def generate_all_variants(
    raw_ram_str: str | None,
    raw_colors_str: str | None,
    fallback_ram: int | None = None,
    fallback_storage: int | None = None
) -> list[dict]:
    """
    Generates all variant dictionaries with fields:
      ram_gb: int
      storage_gb: int
      color: str | None
    """
    memory_combos = extract_memory_variants(raw_ram_str) if raw_ram_str else []
    colors = extract_colors(raw_colors_str) if raw_colors_str else []
    
    # If no memory combinations could be extracted, use fallbacks
    if not memory_combos and fallback_ram and fallback_storage:
        memory_combos = [(fallback_ram, fallback_storage)]
        
    # If still no memory combos, return empty list
    if not memory_combos:
        return []
        
    variants = []
    if not colors:
        for ram, storage in memory_combos:
            variants.append({
                "ram_gb": ram,
                "storage_gb": storage,
                "color": None
            })
    else:
        for ram, storage in memory_combos:
            for color in colors:
                variants.append({
                    "ram_gb": ram,
                    "storage_gb": storage,
                    "color": color
                })
    return variants
