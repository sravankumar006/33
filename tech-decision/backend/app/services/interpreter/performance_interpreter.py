from typing import Dict, Any, Optional

def interpret_performance(chipset: Optional[str], ram_gb: Optional[int]) -> Dict[str, Any]:
    ram_text = f" {ram_gb}GB of RAM" if ram_gb else "standard RAM configuration"
    chipset_lower = (chipset or "").lower()
    
    is_flagship = False
    is_mid = False
    is_entry = False
    
    # Specific flagship chips
    flagship_kws = [
        "snapdragon 8", "tensor g", "dimensity 9", "bionic a15", "bionic a16", 
        "pro a17", "a18", "exynos 2200", "exynos 2400", "snapdragon elite"
    ]
    # Mid range
    mid_kws = [
        "snapdragon 7", "snapdragon 6", "dimensity 7", "dimensity 8", 
        "helio g9", "exynos 1", "bionic a14", "dimensity 1000", "dimensity 1080", "dimensity 7200"
    ]
    # Entry
    entry_kws = [
        "helio g3", "helio g2", "helio p", "unisoc", "snapdragon 4", "quad-core", "octa-core"
    ]
    
    if any(kw in chipset_lower for kw in flagship_kws):
        is_flagship = True
    elif any(kw in chipset_lower for kw in mid_kws):
        is_mid = True
    elif any(kw in chipset_lower for kw in entry_kws):
        is_entry = True
    else:
        # Fallback to RAM size if chipset keyword is not matched
        if ram_gb:
            if ram_gb >= 12:
                is_flagship = True
            elif ram_gb >= 6:
                is_mid = True
            else:
                is_entry = True
        else:
            is_mid = True # Safe default
            
    if is_flagship:
        level = "Flagship"
        summary = f"Top-tier performance powered by the {chipset or 'premium chipset'} and {ram_text}. Excellent for intensive gaming, heavy multitasking, and demanding workflows."
    elif is_mid:
        level = "Mid-Range"
        summary = f"Reliable everyday performance powered by the {chipset or 'mid-range processor'} and {ram_text}. Smooth UI navigation and good multitasking capacity for most users."
    else:
        level = "Entry-Level"
        summary = f"Basic performance suited for light tasks like messaging, browsing, and calls. Equipped with the {chipset or 'entry-level processor'} and {ram_text}."
        
    return {
        "performance_level": level,
        "performance_summary": summary
    }
