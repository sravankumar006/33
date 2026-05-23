from typing import Optional

def interpret_camera(
    main_camera: Optional[str],
    ultrawide_camera: Optional[str],
    telephoto_camera: Optional[str],
    selfie_camera: Optional[str]
) -> str:
    if not main_camera:
        return "Camera details not specified."
        
    main_lower = main_camera.lower()
    has_ois = "ois" in main_lower or "optical image stabilization" in main_lower
    
    # Parse megapixels roughly from main_camera if possible (e.g., "50 MP")
    mp_text = "high-resolution"
    for word in main_lower.split():
        if "mp" in word:
            num_part = word.replace("mp", "")
            if num_part.isdigit() and int(num_part) >= 48:
                mp_text = f"{num_part}MP high-resolution"
                break
                
    parts = []
    parts.append(f"Equipped with a {mp_text} main sensor that captures sharp everyday photos.")
    
    if has_ois:
        parts.append("Features Optical Image Stabilization (OIS), helping to keep shots steady and improve low-light clarity.")
    else:
        parts.append("Lacks hardware optical stabilization, so steady hands are recommended for night/low-light shots.")
        
    if telephoto_camera:
        tele_lower = telephoto_camera.lower()
        if "zoom" in tele_lower:
            parts.append("Includes a dedicated telephoto zoom lens, allowing you to get closer to subjects without losing detail.")
        else:
            parts.append("Includes a telephoto lens for better portrait shots and zoom versatility.")
    else:
        parts.append("No dedicated zoom lens, meaning zoomed-in shots will rely on digital cropping.")
        
    if ultrawide_camera:
        parts.append("The secondary ultrawide lens is perfect for landscape, group, and architecture photos.")
        
    if selfie_camera:
        parts.append(f"The front camera ({selfie_camera.split(',')[0]}) ensures clear selfies and video calls.")
        
    return " ".join(parts)
