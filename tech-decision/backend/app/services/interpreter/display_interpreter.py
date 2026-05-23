from typing import Optional

def interpret_display(
    display_size: Optional[float],
    display_type: Optional[str],
    refresh_rate: Optional[int],
    display_resolution: Optional[str]
) -> str:
    if not display_size:
        return "Display specifications not detailed."
        
    size_desc = f"{display_size}-inch"
    if display_size >= 6.7:
        size_text = f"Large {size_desc}"
    elif display_size >= 6.1:
        size_text = f"Standard {size_desc}"
    else:
        size_text = f"Compact {size_desc}"
        
    type_lower = (display_type or "").lower()
    if any(kw in type_lower for kw in ["amoled", "oled", "ltpo", "super amoled", "dynamic amoled"]):
        type_text = f"{display_type or 'AMOLED'} screen offering vibrant colors, deep blacks, and excellent contrast."
    else:
        type_text = f"{display_type or 'LCD'} display with natural colors and standard contrast."
        
    refresh_text = "standard 60Hz refresh rate"
    if refresh_rate:
        if refresh_rate >= 120:
            refresh_text = f"ultra-smooth {refresh_rate}Hz refresh rate for highly fluid animations and gaming"
        elif refresh_rate >= 90:
            refresh_text = f"smooth {refresh_rate}Hz refresh rate for fluid scrolling"
            
    res_text = f" with crisp {display_resolution} resolution" if display_resolution else ""
    
    return f"{size_text} {type_text} Features an {refresh_text}{res_text}."
