"""
display_enrichment.py
Converts raw brightness data and display specs into human-readable interpretations,
and parses raw GSMArena display strings to extract structured values.
"""
import re
from typing import Optional, Dict, Any


# ---------------------------------------------------------------------------
# Raw-string parsers — extract structured values from GSMArena text blobs
# ---------------------------------------------------------------------------

def enrich_display_from_raw(
    raw_display_type: Optional[str] = None,
    raw_brightness: Optional[str] = None,
    raw_protection: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Parse raw GSMArena display section text and return enriched display fields.

    Returns a dict with keys: peak_brightness_nits, hdr_support,
    display_protection, pwm_dimming, brightness_label, real_world_brightness_nits.
    All values default to None/False if not found.
    """
    result: Dict[str, Any] = {}

    # --- Peak brightness ---
    combined_text = " ".join(filter(None, [raw_display_type, raw_brightness]))
    peak_nits = _parse_peak_brightness(combined_text)
    if peak_nits:
        result["peak_brightness_nits"] = peak_nits
        brightness_data = interpret_brightness(peak_nits)
        result["real_world_brightness_nits"] = brightness_data["real_world_brightness_nits"]
        result["brightness_label"] = brightness_data["brightness_label"]

    # --- HDR support ---
    hdr = _parse_hdr_support(combined_text)
    if hdr:
        result["hdr_support"] = hdr

    # --- Display protection ---
    prot_text = " ".join(filter(None, [raw_display_type, raw_protection]))
    protection = _parse_display_protection(prot_text)
    if protection:
        result["display_protection"] = protection

    # --- PWM dimming ---
    result["pwm_dimming"] = _detect_pwm_dimming(combined_text)

    return result


def _parse_peak_brightness(text: Optional[str]) -> Optional[int]:
    """Extract peak brightness nits from a display spec string."""
    if not text:
        return None
    # Patterns: "4500 nits (peak)", "4500nits", "peak brightness 4500 nits"
    patterns = [
        r"(\d{3,5})\s*nits?\s*(?:\(peak\)|\bpeak\b)",
        r"(?:peak|max|hbm)\s*(?:brightness)?\s*[:\-]?\s*(\d{3,5})\s*nits?",
        r"(\d{3,5})\s*nits",
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            val = int(m.group(1))
            # Sanity: typical range 200–10000 nits
            if 200 <= val <= 10000:
                return val
    return None


def _parse_hdr_support(text: Optional[str]) -> Optional[str]:
    """Extract HDR certification from text."""
    if not text:
        return None
    t = text.lower()
    if "dolby vision" in t:
        return "Dolby Vision"
    if "hdr10+" in t:
        return "HDR10+"
    if "hdr10" in t:
        return "HDR10"
    if "hdr" in t:
        return "HDR"
    return None


def _parse_display_protection(text: Optional[str]) -> Optional[str]:
    """Extract display protection glass type from text."""
    if not text:
        return None
    t = text.lower()
    patterns = [
        (r"gorilla\s*glass\s*victus\s*\+", "Gorilla Glass Victus+"),
        (r"gorilla\s*glass\s*victus\s*2", "Gorilla Glass Victus 2"),
        (r"gorilla\s*glass\s*victus", "Gorilla Glass Victus"),
        (r"gorilla\s*glass\s*7i?", "Gorilla Glass 7"),
        (r"gorilla\s*glass\s*6", "Gorilla Glass 6"),
        (r"gorilla\s*glass\s*5", "Gorilla Glass 5"),
        (r"gorilla\s*glass\s*3", "Gorilla Glass 3"),
        (r"gorilla\s*glass", "Gorilla Glass"),
        (r"ceramic\s*shield", "Ceramic Shield"),
        (r"dragontrail\s*x", "Dragontrail X"),
        (r"dragontrail", "Dragontrail"),
        (r"panda\s*glass", "Panda Glass"),
        (r"schott\s*xensation", "Schott Xensation"),
    ]
    for pattern, label in patterns:
        if re.search(pattern, t):
            return label
    return None


def _detect_pwm_dimming(text: Optional[str]) -> bool:
    """Detect if PWM dimming is mentioned (i.e., has it, for low flicker info)."""
    if not text:
        return False
    keywords = ["pwm", "flicker-free", "dc dimming", "anti-flicker"]
    return any(kw in text.lower() for kw in keywords)


# ---------------------------------------------------------------------------
# Human-readable interpretation functions
# ---------------------------------------------------------------------------

def interpret_brightness(peak_nits: Optional[int]) -> Dict[str, Any]:
    """
    Convert peak brightness (nits) to human-readable label and real-world estimate.
    Returns: {"brightness_label": str, "real_world_brightness_nits": int}
    """
    if not peak_nits:
        return {
            "brightness_label": "Standard indoor brightness",
            "real_world_brightness_nits": None,
        }

    # Estimate typical real-world (sustained) brightness as ~35-45% of peak
    real_world = int(peak_nits * 0.38)

    if peak_nits >= 4000:
        label = "Exceptional outdoor visibility — readable even in direct sunlight"
    elif peak_nits >= 2500:
        label = "Excellent outdoor visibility — very clear in bright sunlight"
    elif peak_nits >= 1600:
        label = "Good outdoor visibility — comfortable in most outdoor conditions"
    elif peak_nits >= 1000:
        label = "Decent outdoor visibility — may be slightly dim in harsh sunlight"
    elif peak_nits >= 600:
        label = "Adequate for indoor use — outdoor readability is limited"
    else:
        label = "Basic brightness — primarily suited for indoor use"

    return {
        "brightness_label": label,
        "real_world_brightness_nits": real_world,
    }


def interpret_hdr(hdr_support: Optional[str]) -> str:
    """Return a human-friendly HDR description."""
    if not hdr_support:
        return ""
    h = hdr_support.lower()
    if "dolby vision" in h:
        return "Dolby Vision certified — best-in-class HDR with dynamic tone mapping"
    elif "hdr10+" in h:
        return "HDR10+ certified — cinema-grade dynamic range for streaming content"
    elif "hdr10" in h:
        return "HDR10 support — enhanced contrast and color for compatible content"
    elif "hdr" in h:
        return "HDR support — improved contrast for compatible content"
    return hdr_support


def interpret_display_protection(protection: Optional[str]) -> str:
    """Return a human-friendly display protection description."""
    if not protection:
        return ""
    p = protection.lower()
    if "victus+" in p or "victus 2" in p:
        return "Gorilla Glass Victus 2 — best-in-class drop and scratch resistance"
    elif "victus" in p:
        return "Gorilla Glass Victus — excellent scratch and drop protection"
    elif "gorilla glass 7" in p:
        return "Gorilla Glass 7 — strong scratch and impact resistance"
    elif "gorilla glass 6" in p:
        return "Gorilla Glass 6 — good scratch and drop resistance"
    elif "gorilla glass 5" in p:
        return "Gorilla Glass 5 — solid protection for everyday use"
    elif "gorilla glass" in p:
        return "Gorilla Glass protection — scratch and impact resistant"
    elif "ceramic shield" in p:
        return "Apple Ceramic Shield — exceptional drop protection"
    elif "dragontrail x" in p:
        return "Dragontrail X — premium scratch and impact resistance"
    elif "dragontrail" in p:
        return "Dragontrail — scratch and impact resistant"
    return protection
