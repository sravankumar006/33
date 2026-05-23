import re
from typing import Dict, Any, Optional

def normalize_ram(raw_ram: Optional[str]) -> Optional[int]:
    """
    Normalizes RAM string to an integer representing GB.
    Example: '12GB RAM', '256GB 12GB RAM' -> 12
    """
    if not raw_ram:
        return None
    # Find all matches like "12GB RAM" or "12 GB RAM"
    matches = re.findall(r'(\d+)\s*(GB|MB)\s*RAM', raw_ram, re.IGNORECASE)
    if matches:
        val, unit = matches[0]
        val = int(val)
        if unit.upper() == 'MB':
            val = max(1, val // 1024)
        return val
    # Fallback to any number before "RAM"
    matches = re.findall(r'(\d+)\s*RAM', raw_ram, re.IGNORECASE)
    if matches:
        return int(matches[0])
    return None

def normalize_storage(raw_storage: Optional[str]) -> Optional[int]:
    """
    Normalizes storage string to an integer representing GB.
    Example: '256GB', '256GB 12GB RAM', '1TB' -> 256 or 1024
    """
    if not raw_storage:
        return None
    # Find all matches of GB/TB that are NOT followed by RAM
    # We use negative lookahead to ignore the RAM GB value
    matches = re.findall(r'(\d+)\s*(GB|TB)(?!\s*RAM)', raw_storage, re.IGNORECASE)
    if matches:
        val, unit = matches[0]
        val = int(val)
        if unit.upper() == 'TB':
            val *= 1024
        return val
    # Fallback: search for any GB/TB
    matches = re.findall(r'(\d+)\s*(GB|TB)', raw_storage, re.IGNORECASE)
    if matches:
        val, unit = matches[0]
        val = int(val)
        if unit.upper() == 'TB':
            val *= 1024
        return val
    return None

def normalize_battery(raw_battery: Optional[str]) -> Optional[int]:
    """
    Normalizes battery string to integer mAh.
    Example: 'Li-Po 6000 mAh' -> 6000
    """
    if not raw_battery:
        return None
    match = re.search(r'(\d+)\s*mAh', raw_battery, re.IGNORECASE)
    if match:
        return int(match.group(1))
    # Fallback: look for a 3-5 digit number
    match = re.search(r'\b(\d{3,5})\b', raw_battery)
    if match:
        return int(match.group(1))
    return None

def normalize_charging_watts(raw_charging: Optional[str]) -> Optional[int]:
    """
    Normalizes charging string to integer Watts.
    Example: '80W wired, 50W wireless' -> 80
    """
    if not raw_charging:
        return None
    # Look for a number followed by W with "wired" or "fast" or similar keywords
    match = re.search(r'(\d+)\s*W\s*(?:wired|fast|pd|qc)', raw_charging, re.IGNORECASE)
    if match:
        return int(match.group(1))
    # Look for any W not followed by wireless
    matches = re.findall(r'(\d+)\s*W(?!\s*wireless)', raw_charging, re.IGNORECASE)
    if matches:
        return int(matches[0])
    # Fallback to any W
    match = re.search(r'(\d+)\s*W', raw_charging, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def normalize_wireless_charging(raw_charging: Optional[str]) -> Optional[bool]:
    """
    Determines if wireless charging is supported.
    """
    if not raw_charging:
        return False
    # Check for "wireless" or "qi" or "magsafe"
    if 'wireless' in raw_charging.lower() or 'qi' in raw_charging.lower():
        return True
    return False

def normalize_display_size(raw_size: Optional[str]) -> Optional[float]:
    """
    Normalizes display size to float inches.
    Example: '6.82 inches' -> 6.82
    """
    if not raw_size:
        return None
    match = re.search(r'(\d+(?:\.\d+)?)\s*(?:inches|")', raw_size, re.IGNORECASE)
    if match:
        return float(match.group(1))
    match = re.search(r'(\d+\.\d+)', raw_size)
    if match:
        return float(match.group(1))
    return None

def normalize_display_resolution(raw_resolution: Optional[str]) -> Optional[str]:
    """
    Normalizes resolution.
    Example: '1440 x 3168 pixels' -> '1440x3168'
    """
    if not raw_resolution:
        return None
    match = re.search(r'(\d+\s*x\s*\d+)', raw_resolution)
    if match:
        return match.group(1).replace(" ", "")
    return raw_resolution.strip()

def normalize_refresh_rate(raw_refresh: Optional[str]) -> Optional[int]:
    """
    Normalizes refresh rate to integer Hz.
    Example: '120Hz' -> 120
    """
    if not raw_refresh:
        return None
    match = re.search(r'(\d+)\s*Hz', raw_refresh, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def normalize_display_type(raw_type: Optional[str]) -> Optional[str]:
    """
    Normalizes display type string to the panel type.
    Example: 'LTPO AMOLED, 120Hz, HDR10+' -> 'LTPO AMOLED'
    """
    if not raw_type:
        return None
    return raw_type.split(",")[0].strip()

def normalize_weight(raw_weight: Optional[str]) -> Optional[int]:
    """
    Normalizes weight to integer grams.
    Example: '210 g' -> 210
    """
    if not raw_weight:
        return None
    match = re.search(r'(\d+)\s*g\b', raw_weight)
    if match:
        return int(match.group(1))
    match = re.search(r'(\d+)', raw_weight)
    if match:
        return int(match.group(1))
    return None

def normalize_ip_rating(raw_ip: Optional[str]) -> Optional[str]:
    """
    Normalizes IP rating string.
    Example: 'IP68 dust/water resistant' -> 'IP68'
    """
    if not raw_ip:
        return None
    match = re.search(r'(IP\d{2})', raw_ip, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    match = re.search(r'(IP[a-zA-Z0-9]{2})', raw_ip, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None

def normalize_cameras(raw_main: Optional[str]) -> Dict[str, Optional[str]]:
    """
    Splits combined main camera lines into main, ultrawide, and telephoto.
    """
    result = {
        "main_camera": None,
        "ultrawide_camera": None,
        "telephoto_camera": None
    }
    if not raw_main:
        return result
        
    lines = [line.strip() for line in raw_main.replace("\r", "").split("\n") if line.strip()]
    if not lines:
        return result
        
    if len(lines) == 1:
        result["main_camera"] = lines[0]
        return result
        
    for line in lines:
        line_lower = line.lower()
        if "ultrawide" in line_lower or "ultra-wide" in line_lower or "ultra wide" in line_lower:
            result["ultrawide_camera"] = line
        elif "telephoto" in line_lower or "periscope" in line_lower or "zoom" in line_lower:
            result["telephoto_camera"] = line
        elif "wide" in line_lower or "main" in line_lower:
            result["main_camera"] = line
        else:
            if not result["main_camera"]:
                result["main_camera"] = line
            elif not result["telephoto_camera"] and "macro" in line_lower:
                result["telephoto_camera"] = line
                
    if not result["main_camera"] and lines:
        result["main_camera"] = lines[0]
        
    return result

def normalize_selfie_camera(raw_selfie: Optional[str]) -> Optional[str]:
    """
    Cleans up selfie camera string.
    """
    if not raw_selfie:
        return None
    lines = [line.strip() for line in raw_selfie.replace("\r", "").split("\n") if line.strip()]
    if lines:
        return lines[0]
    return None


# ---------------------------------------------------------------------------
# Connectivity normalizers
# ---------------------------------------------------------------------------

def normalize_wifi_version(raw_connectivity: Optional[str]) -> Optional[str]:
    """
    Normalizes WiFi version from connectivity string.
    Examples: '802.11 a/b/g/n/ac/ax/be' -> 'Wi-Fi 7',
              'Wi-Fi 7 (802.11be)' -> 'Wi-Fi 7'
    """
    if not raw_connectivity:
        return None
    text = raw_connectivity.lower()

    # Explicit Wi-Fi version labels
    wifi_map = [
        (r"wi[-\s]?fi\s*7|802\.11be", "Wi-Fi 7"),
        (r"wi[-\s]?fi\s*6e|802\.11ax.*6ghz", "Wi-Fi 6E"),
        (r"wi[-\s]?fi\s*6|802\.11ax", "Wi-Fi 6"),
        (r"wi[-\s]?fi\s*5|802\.11ac", "Wi-Fi 5"),
        (r"wi[-\s]?fi\s*4|802\.11n", "Wi-Fi 4"),
    ]
    for pattern, label in wifi_map:
        if re.search(pattern, text):
            return label

    # Detect from 802.11 protocol list
    if re.search(r"802\.11.*\bax\b", text):
        return "Wi-Fi 6"
    if re.search(r"802\.11.*\bac\b", text):
        return "Wi-Fi 5"
    if re.search(r"802\.11.*\bn\b", text):
        return "Wi-Fi 4"
    return None


def normalize_bluetooth_version(raw_connectivity: Optional[str]) -> Optional[str]:
    """
    Normalizes Bluetooth version from connectivity string.
    Example: 'Bluetooth 5.4' -> '5.4'
    """
    if not raw_connectivity:
        return None
    match = re.search(r"bluetooth\s+(\d+(?:\.\d+)?)", raw_connectivity, re.IGNORECASE)
    if match:
        return match.group(1)
    # Version-only pattern e.g. "BT 5.3"
    match = re.search(r"\bBT\s+(\d+(?:\.\d+)?)\b", raw_connectivity, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def normalize_usb_type(raw_connectivity: Optional[str]) -> Optional[str]:
    """
    Normalizes USB type from connectivity string.
    Examples: 'USB Type-C 3.2 Gen 2' -> 'USB 3.2 Gen 2 Type-C',
              'USB 2.0' -> 'USB 2.0 Type-C' (if Type-C also present)
    """
    if not raw_connectivity:
        return None
    text = raw_connectivity

    # Look for USB standard version first
    usb_patterns = [
        (r"USB\s*3\.2\s*Gen\s*2x2", "USB 3.2 Gen 2x2 Type-C"),
        (r"USB\s*3\.2\s*Gen\s*2(?!\s*x)", "USB 3.2 Gen 2 Type-C"),
        (r"USB\s*3\.2\s*Gen\s*1", "USB 3.2 Gen 1 Type-C"),
        (r"USB\s*3\.2", "USB 3.2 Type-C"),
        (r"USB\s*3\.1\s*Gen\s*2", "USB 3.1 Gen 2 Type-C"),
        (r"USB\s*3\.1", "USB 3.1 Type-C"),
        (r"USB\s*3\.0", "USB 3.0 Type-C"),
        (r"USB\s*2\.0", "USB 2.0 Type-C"),
    ]
    for pattern, label in usb_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return label

    # Thunderbolt
    if re.search(r"thunderbolt\s*4", text, re.IGNORECASE):
        return "Thunderbolt 4 / USB 4"
    if re.search(r"thunderbolt\s*3", text, re.IGNORECASE):
        return "Thunderbolt 3 / USB 3.2"

    # Generic Type-C fallback
    if re.search(r"type[-\s]?c|usb[-\s]?c", text, re.IGNORECASE):
        return "USB Type-C"
    return None


def normalize_ufs_type(raw_storage: Optional[str]) -> Optional[str]:
    """
    Normalizes UFS storage type from storage string.
    Examples: 'UFS 4.0' -> 'UFS 4.0', '256GB UFS 3.1' -> 'UFS 3.1'
    """
    if not raw_storage:
        return None
    match = re.search(r"UFS\s*(\d+(?:\.\d+)?)", raw_storage, re.IGNORECASE)
    if match:
        return f"UFS {match.group(1)}"
    # NVMe storage
    if re.search(r"nvme", raw_storage, re.IGNORECASE):
        return "NVMe"
    return None


def normalize_esim(raw_connectivity: Optional[str]) -> Optional[bool]:
    """
    Detects eSIM support from connectivity string.
    Returns True if eSIM mentioned, False if explicitly not mentioned, None if unknown.
    """
    if not raw_connectivity:
        return None
    text = raw_connectivity.lower()
    if "esim" in text or "e-sim" in text:
        return True
    return None


# ---------------------------------------------------------------------------
# Main normalizer
# ---------------------------------------------------------------------------

def normalize_all_specs(raw_specs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given a dictionary of raw specs, normalizes them all and returns a dictionary
    containing both raw and normalized fields.
    """
    normalized = {}
    
    # Simple mapping of key to normalizer function
    normalized["chipset"] = raw_specs.get("raw_chipset")
    normalized["cpu"] = raw_specs.get("raw_cpu")
    normalized["gpu"] = raw_specs.get("raw_gpu")
    
    normalized["ram"] = normalize_ram(raw_specs.get("raw_ram"))
    normalized["storage"] = normalize_storage(raw_specs.get("raw_storage"))
    
    # Also populate legacy fields for backwards compatibility
    normalized["ram_gb"] = normalized["ram"]
    normalized["storage_gb"] = normalized["storage"]
    normalized["processor"] = raw_specs.get("raw_chipset")
    
    normalized["battery_mah"] = normalize_battery(raw_specs.get("raw_battery_mah"))
    normalized["charging_watts"] = normalize_charging_watts(raw_specs.get("raw_charging_watts"))
    normalized["wireless_charging"] = normalize_wireless_charging(raw_specs.get("raw_charging_watts"))
    
    normalized["display_size"] = normalize_display_size(raw_specs.get("raw_display_size"))
    normalized["display_resolution"] = normalize_display_resolution(raw_specs.get("raw_display_resolution"))
    normalized["refresh_rate"] = normalize_refresh_rate(raw_specs.get("raw_refresh_rate"))
    if normalized["refresh_rate"] is None:
        # Check display type which often has refresh rate
        normalized["refresh_rate"] = normalize_refresh_rate(raw_specs.get("raw_display_type"))
    normalized["refresh_rate_hz"] = normalized["refresh_rate"]
    
    normalized["display_type"] = normalize_display_type(raw_specs.get("raw_display_type"))
    
    camera_mapping = normalize_cameras(raw_specs.get("raw_main_camera"))
    normalized["main_camera"] = camera_mapping["main_camera"]
    normalized["ultrawide_camera"] = camera_mapping["ultrawide_camera"]
    normalized["telephoto_camera"] = camera_mapping["telephoto_camera"]
    
    # Legacy fields
    # Try to extract number from main camera (e.g. "50 MP" -> 50)
    main_camera_str = camera_mapping["main_camera"]
    if main_camera_str:
        cam_match = re.search(r'(\d+)\s*MP', main_camera_str, re.IGNORECASE)
        normalized["camera_main_mp"] = int(cam_match.group(1)) if cam_match else None
    else:
        normalized["camera_main_mp"] = None
        
    normalized["selfie_camera"] = normalize_selfie_camera(raw_specs.get("raw_selfie_camera"))
    
    normalized["weight"] = normalize_weight(raw_specs.get("raw_weight"))
    normalized["ip_rating"] = normalize_ip_rating(raw_specs.get("raw_ip_rating"))
    
    # Connectivity
    raw_conn = raw_specs.get("raw_connectivity", "") or ""
    normalized["wifi_version"] = normalize_wifi_version(raw_conn)
    normalized["bluetooth_version"] = normalize_bluetooth_version(raw_conn)
    normalized["usb_type"] = normalize_usb_type(raw_conn)
    normalized["esim"] = normalize_esim(raw_conn)

    # Storage type
    raw_storage_str = raw_specs.get("raw_storage", "") or ""
    normalized["ufs_type"] = normalize_ufs_type(raw_storage_str)
    
    # Add raw specs to output
    for k, v in raw_specs.items():
        normalized[k] = v
        
    return normalized
