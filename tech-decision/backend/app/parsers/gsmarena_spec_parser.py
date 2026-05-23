import logging
from bs4 import BeautifulSoup

logger = logging.getLogger("uvicorn.error")

def parse_gsmarena_specs(html: str) -> dict:
    """
    Parses a GSMArena phone specifications HTML page.
    Returns a dictionary of raw spec strings mapping directly to the DB columns.
    Now extracts: connectivity, display extras (HDR, protection, brightness),
    software/Android version, build materials, cooling, battery reverse charging,
    UFS storage type.
    """
    soup = BeautifulSoup(html, "html.parser")
    specs_list = soup.find(id="specs-list")

    raw_data = {
        # Original fields
        "raw_chipset": None,
        "raw_cpu": None,
        "raw_gpu": None,
        "raw_ram": None,
        "raw_storage": None,
        "raw_battery_mah": None,
        "raw_charging_watts": None,
        "raw_wireless_charging": None,
        "raw_display_size": None,
        "raw_display_resolution": None,
        "raw_refresh_rate": None,
        "raw_display_type": None,
        "raw_main_camera": None,
        "raw_ultrawide_camera": None,
        "raw_telephoto_camera": None,
        "raw_selfie_camera": None,
        "raw_weight": None,
        "raw_ip_rating": None,
        # New fields Phase 4
        "raw_connectivity": None,
        "raw_software": None,
        "raw_colors": None,
        # Parsed direct fields (returned inline for direct mapping)
        "hdr_support": None,
        "display_protection": None,
        "wifi_version": None,
        "bluetooth_version": None,
        "usb_type": None,
        "nfc": None,
        "esim": None,
        "android_version": None,
        "reverse_charging": None,
        "ufs_type": None,
        "cooling_system": None,
        "build_materials": None,
        "peak_brightness_nits": None,
    }

    if not specs_list:
        logger.warning("parse_gsmarena_specs: id='specs-list' not found in HTML.")
        return raw_data

    # Gather all key-values by section
    sections = {}
    tables = specs_list.find_all("table")
    for table in tables:
        th = table.find("th")
        section_name = th.get_text(strip=True).lower() if th else "unknown"
        if section_name not in sections:
            sections[section_name] = []

        last_key = ""
        for tr in table.find_all("tr"):
            ttl = tr.find("td", class_="ttl")
            nfo = tr.find("td", class_="nfo")
            if nfo:
                key = ttl.get_text(strip=True) if ttl else ""
                key = key.replace("\xa0", " ").strip()
                if not key:
                    key = last_key
                else:
                    last_key = key

                val = nfo.get_text(separator="\n", strip=True).replace("\xa0", " ").strip()
                sections[section_name].append((key.lower(), val))

    # Platform Section
    platform_rows = sections.get("platform", [])
    for key, val in platform_rows:
        if "chipset" in key and not raw_data["raw_chipset"]:
            raw_data["raw_chipset"] = val
        elif "cpu" in key and not raw_data["raw_cpu"]:
            raw_data["raw_cpu"] = val
        elif "gpu" in key and not raw_data["raw_gpu"]:
            raw_data["raw_gpu"] = val

    # Memory Section
    memory_rows = sections.get("memory", [])
    for key, val in memory_rows:
        if "internal" in key and not raw_data["raw_ram"]:
            raw_data["raw_ram"] = val
            raw_data["raw_storage"] = val
            # Extract UFS type
            val_lower = val.lower()
            if "ufs 4" in val_lower:
                raw_data["ufs_type"] = "UFS 4.0"
            elif "ufs 3.1" in val_lower:
                raw_data["ufs_type"] = "UFS 3.1"
            elif "ufs 3" in val_lower:
                raw_data["ufs_type"] = "UFS 3.0"
            elif "ufs 2.2" in val_lower:
                raw_data["ufs_type"] = "UFS 2.2"
            elif "ufs 2.1" in val_lower:
                raw_data["ufs_type"] = "UFS 2.1"
            elif "ufs 2" in val_lower:
                raw_data["ufs_type"] = "UFS 2.0"
            elif "emmc" in val_lower:
                raw_data["ufs_type"] = "eMMC"

    # Battery Section
    battery_rows = sections.get("battery", [])
    for key, val in battery_rows:
        if "type" in key and not raw_data["raw_battery_mah"]:
            raw_data["raw_battery_mah"] = val
        elif "charging" in key:
            if not raw_data["raw_charging_watts"]:
                raw_data["raw_charging_watts"] = val
                raw_data["raw_wireless_charging"] = val
            # Detect reverse wireless charging
            val_lower = val.lower()
            if "reverse" in val_lower:
                raw_data["reverse_charging"] = True

    # Display Section — enhanced
    display_rows = sections.get("display", [])
    brightness_texts = []
    for key, val in display_rows:
        if "size" in key and not raw_data["raw_display_size"]:
            raw_data["raw_display_size"] = val
        elif "resolution" in key and not raw_data["raw_display_resolution"]:
            raw_data["raw_display_resolution"] = val
        elif "type" in key and not raw_data["raw_display_type"]:
            raw_data["raw_display_type"] = val
            raw_data["raw_refresh_rate"] = val
            # HDR extraction from type string
            val_lower = val.lower()
            if "dolby vision" in val_lower:
                raw_data["hdr_support"] = "Dolby Vision, HDR10+"
            elif "hdr10+" in val_lower:
                raw_data["hdr_support"] = "HDR10+"
            elif "hdr10" in val_lower:
                raw_data["hdr_support"] = "HDR10"
            elif "hdr" in val_lower:
                raw_data["hdr_support"] = "HDR"
        elif "protection" in key and not raw_data["display_protection"]:
            raw_data["display_protection"] = val.split(",")[0].strip()
        elif "brightness" in key:
            brightness_texts.append(val)

    # Try to parse brightness from combined text
    if brightness_texts:
        import re
        combined = " ".join(brightness_texts)
        # Find peak brightness (look for patterns like "2600 nits", "4500 nits (peak)")
        peak_match = re.search(r'(\d{3,5})\s*nits?\s*(?:\(peak\))?', combined, re.IGNORECASE)
        if peak_match:
            raw_data["peak_brightness_nits"] = int(peak_match.group(1))

    # Main Camera Section
    main_camera_parts = []
    main_camera_rows = sections.get("main camera", [])
    for key, val in main_camera_rows:
        if key in ["single", "dual", "triple", "quad", "five", "features", "video"]:
            if key not in ["features", "video"]:
                main_camera_parts.append(val)
    if main_camera_parts:
        combined_cam = "\n".join(main_camera_parts)
        raw_data["raw_main_camera"] = combined_cam
        raw_data["raw_ultrawide_camera"] = combined_cam
        raw_data["raw_telephoto_camera"] = combined_cam

    # Selfie Camera Section
    selfie_camera_parts = []
    selfie_camera_rows = sections.get("selfie camera", [])
    for key, val in selfie_camera_rows:
        if key in ["single", "dual", "triple", "features", "video"]:
            if key not in ["features", "video"]:
                selfie_camera_parts.append(val)
    if selfie_camera_parts:
        raw_data["raw_selfie_camera"] = "\n".join(selfie_camera_parts)

    # Body Section — weight, IP rating, materials, cooling
    body_rows = sections.get("body", [])
    body_all_vals = []
    for key, val in body_rows:
        body_all_vals.append(val.lower())
        if "weight" in key and not raw_data["raw_weight"]:
            raw_data["raw_weight"] = val
        if "ip" in val.lower() and not raw_data["raw_ip_rating"]:
            raw_data["raw_ip_rating"] = val
        if "build" in key or "back" in key or "frame" in key or "front" in key:
            if not raw_data["build_materials"]:
                raw_data["build_materials"] = val

    # Cooling detection from body section
    full_body = " ".join(body_all_vals)
    if "vapor" in full_body:
        raw_data["cooling_system"] = "Vapor Chamber"
    elif "graphene" in full_body:
        raw_data["cooling_system"] = "Graphene Cooling"

    # Comms / Connectivity Section
    comms_rows = sections.get("comms", [])
    comms_parts = []
    for key, val in comms_rows:
        comms_parts.append(f"{key}: {val}")
        val_lower = val.lower()
        key_lower = key.lower()
        # WiFi
        if "wlan" in key_lower or "wi-fi" in key_lower:
            if not raw_data["wifi_version"]:
                if "802.11 be" in val_lower or "wi-fi 7" in val_lower:
                    raw_data["wifi_version"] = "Wi-Fi 7 (802.11be)"
                elif "802.11 ax" in val_lower or "wi-fi 6e" in val_lower:
                    raw_data["wifi_version"] = "Wi-Fi 6E (802.11ax)"
                elif "802.11ax" in val_lower or "wi-fi 6" in val_lower:
                    raw_data["wifi_version"] = "Wi-Fi 6 (802.11ax)"
                elif "802.11ac" in val_lower or "wi-fi 5" in val_lower:
                    raw_data["wifi_version"] = "Wi-Fi 5 (802.11ac)"
                elif "802.11n" in val_lower:
                    raw_data["wifi_version"] = "Wi-Fi 4 (802.11n)"
                else:
                    raw_data["wifi_version"] = "Wi-Fi"
        # Bluetooth
        if "bluetooth" in key_lower:
            if not raw_data["bluetooth_version"]:
                import re
                bt_match = re.search(r'(\d+\.\d+)', val)
                if bt_match:
                    raw_data["bluetooth_version"] = bt_match.group(1)
        # USB
        if "usb" in key_lower:
            if not raw_data["usb_type"]:
                raw_data["usb_type"] = val.split(",")[0].strip()
        # NFC
        if "nfc" in key_lower:
            raw_data["nfc"] = "yes" in val_lower or val_lower == "yes"
        # eSIM
        if "esim" in key_lower or "e-sim" in val_lower or "esim" in val_lower:
            raw_data["esim"] = True

    if comms_parts:
        raw_data["raw_connectivity"] = "; ".join(comms_parts)

    # Network section — also check eSIM
    network_rows = sections.get("network", [])
    for key, val in network_rows:
        val_lower = val.lower()
        if "esim" in val_lower or "e-sim" in val_lower:
            raw_data["esim"] = True

    # Software section
    software_rows = sections.get("software", [])
    sw_parts = []
    for key, val in software_rows:
        sw_parts.append(f"{key}: {val}")
        if "os" in key.lower() or "android" in val.lower() or "ios" in val.lower():
            if not raw_data["android_version"]:
                raw_data["android_version"] = val.split(",")[0].strip()
    if sw_parts:
        raw_data["raw_software"] = "; ".join(sw_parts)

    # Features section — additional HDR, cooling clues
    features_rows = sections.get("features", [])
    for key, val in features_rows:
        val_lower = val.lower()
        if "dolby vision" in val_lower and not raw_data["hdr_support"]:
            raw_data["hdr_support"] = "Dolby Vision, HDR10+"
        elif "hdr10+" in val_lower and not raw_data["hdr_support"]:
            raw_data["hdr_support"] = "HDR10+"
        if "vapor" in val_lower and not raw_data["cooling_system"]:
            raw_data["cooling_system"] = "Vapor Chamber"
        if "esim" in val_lower and raw_data["esim"] is None:
            raw_data["esim"] = True

    # Misc section — check for eSIM and colors
    misc_rows = sections.get("misc", [])
    for key, val in misc_rows:
        val_lower = val.lower()
        if "esim" in val_lower or "e-sim" in val_lower:
            raw_data["esim"] = True
        if "colors" in key.lower() or "color" in key.lower():
            raw_data["raw_colors"] = val

    return raw_data
