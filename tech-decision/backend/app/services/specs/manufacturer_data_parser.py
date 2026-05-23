"""
manufacturer_data_parser.py
Curated static knowledge base of on-device AI features and AI suite names per brand/model.
Returns structured AI feature labels based on brand + model pattern matching.
"""
import re
from typing import Optional, Dict, Any, List


# AI feature database: (brand_pattern, model_pattern, suite_name, features_list)
_AI_FEATURES_DB = [
    # Samsung Galaxy AI
    (
        "samsung",
        r"galaxy\s*s2[4-9]|galaxy\s*s[3-9]\d|galaxy\s*z\s*fold[5-9]|galaxy\s*z\s*flip[5-9]"
        r"|galaxy\s*a5[5-9]|galaxy\s*a[6-9]\d",
        "Galaxy AI",
        [
            "Circle to Search with Google",
            "Live Translate (call & chat)",
            "Chat Assist — tone and grammar correction",
            "Note Assist — AI summarization",
            "Transcript Assist — meeting transcription",
            "Generative Edit — AI photo editing",
            "AI Zoom — intelligent upscaling",
            "Interpreter — real-time conversation translation",
        ],
    ),
    # Google Gemini on Pixel
    (
        "google",
        r"pixel\s*[7-9]|pixel\s*fold|pixel\s*pro|pixel\s*ultra",
        "Google Gemini",
        [
            "Google Gemini Assistant on-device",
            "Magic Eraser — AI object removal",
            "Photo Unblur — AI sharpening",
            "Best Take — AI group photo merging",
            "Audio Magic Eraser — background noise removal",
            "Call Screen with AI",
            "Direct My Call — AI call navigation",
            "Summarize — on-device text summarization",
        ],
    ),
    (
        "google",
        r"pixel\s*[5-6]",
        "Google Assistant AI",
        [
            "Magic Eraser — AI object removal",
            "Photo Unblur",
            "Call Screen with AI",
            "Live Caption",
        ],
    ),
    # Apple Intelligence
    (
        "apple",
        r"iphone\s*1[5-9]|iphone\s*16|iphone\s*17",
        "Apple Intelligence",
        [
            "Writing Tools — AI rewrite, proofread, summarize",
            "Smart Reply suggestions",
            "Priority notifications — AI-ranked inbox",
            "Photo Cleanup — AI object removal",
            "Image Playground — AI image generation",
            "Genmoji — custom AI emoji",
            "Siri with ChatGPT integration",
            "On-device AI with full privacy",
        ],
    ),
    # OnePlus AI
    (
        "oneplus",
        r"oneplus\s*1[2-9]|oneplus\s*[2-9]\d",
        "OnePlus AI",
        [
            "AI Eraser — remove unwanted objects in photos",
            "AI Summary — one-tap meeting/text summarization",
            "AI Reflection Eraser — remove glass reflections",
            "AI Best Face — optimal face selection in group shots",
            "AI Writer — smart text suggestions",
        ],
    ),
    # Xiaomi HyperAI
    (
        "xiaomi",
        r"xiaomi\s*1[4-9]|xiaomi\s*[2-9]\d",
        "HyperAI",
        [
            "AI Photo Editing — object removal and enhancement",
            "AI Summarization — document and text condensing",
            "AI Translation — real-time multi-language support",
            "Xiaomi AI Assistant",
            "AI Portrait Enhancement",
        ],
    ),
    # Motorola Moto AI
    (
        "motorola",
        r"edge\s*[4-9]\d|razr\s*[4-9]\d",
        "Moto AI",
        [
            "Moto AI Assistant",
            "AI Photo Editing",
            "Smart Connect — seamless device pairing",
        ],
    ),
    # Nothing
    (
        "nothing",
        r"phone\s*[2-9]",
        "Essential Space AI",
        [
            "Essential Space — AI personal journal",
            "AI-powered summaries",
            "Smart lock screen widgets",
        ],
    ),
    # realme AI
    (
        "realme",
        r"gt\s*[6-9]|gt\s*[2-5]\s*pro",
        "realme AI",
        [
            "AI Photo Eraser",
            "AI Portrait Enhancement",
            "AI Video Call Enhancement",
        ],
    ),
    # OPPO AI
    (
        "oppo",
        r"find\s*x[6-9]|reno\s*1[2-9]",
        "OPPO AI",
        [
            "AI Eraser",
            "AI Smart Loop — context-aware actions",
            "AI Toolbox",
        ],
    ),
]


_DEFAULT_AI_FEATURES = [
    "AI Portrait mode",
    "AI Scene recognition",
    "AI Noise reduction",
]


def get_ai_features(brand: str, model: str) -> Dict[str, Any]:
    """
    Returns on-device AI suite name and list of features for a given brand + model.
    Falls back to generic AI features if no specific match found.
    """
    brand_lower = (brand or "").lower().strip()
    model_lower = (model or "").lower().strip()
    full_name = f"{brand_lower} {model_lower}"

    for b_pattern, m_pattern, suite_name, features in _AI_FEATURES_DB:
        if b_pattern and b_pattern not in brand_lower:
            continue
        if m_pattern and not re.search(m_pattern, full_name, re.IGNORECASE):
            continue
        return {
            "ai_suite_name": suite_name,
            "ai_features": features,
        }

    # No match — return generic
    return {
        "ai_suite_name": None,
        "ai_features": _DEFAULT_AI_FEATURES,
    }


# ---------------------------------------------------------------------------
# Connectivity defaults database
# ---------------------------------------------------------------------------

_CONNECTIVITY_DB = [
    # Google Pixel 8+
    ("google", r"pixel\s*[8-9]|pixel\s*fold|pixel\s*pro|pixel\s*ultra", {
        "wifi_version": "Wi-Fi 7",
        "bluetooth_version": "5.3",
        "usb_type": "USB 3.2 Gen 2 Type-C",
        "esim": True,
    }),
    ("google", r"pixel\s*[6-7]", {
        "wifi_version": "Wi-Fi 6E",
        "bluetooth_version": "5.3",
        "usb_type": "USB 3.2 Type-C",
        "esim": True,
    }),
    # Samsung Galaxy S25 series
    ("samsung", r"galaxy\s*s2[5-9]", {
        "wifi_version": "Wi-Fi 7",
        "bluetooth_version": "5.4",
        "usb_type": "USB 3.2 Gen 2 Type-C",
        "esim": True,
    }),
    # Samsung Galaxy S24 series
    ("samsung", r"galaxy\s*s2[4]", {
        "wifi_version": "Wi-Fi 7",
        "bluetooth_version": "5.3",
        "usb_type": "USB 3.2 Gen 2 Type-C",
        "esim": True,
    }),
    # Samsung Galaxy S23 series
    ("samsung", r"galaxy\s*s2[3]", {
        "wifi_version": "Wi-Fi 6E",
        "bluetooth_version": "5.3",
        "usb_type": "USB 3.2 Gen 2 Type-C",
        "esim": True,
    }),
    # Samsung Galaxy Z series
    ("samsung", r"galaxy\s*z", {
        "wifi_version": "Wi-Fi 6E",
        "bluetooth_version": "5.3",
        "usb_type": "USB 3.2 Gen 2 Type-C",
        "esim": True,
    }),
    # Samsung Galaxy A series mid-range
    ("samsung", r"galaxy\s*a[5-9]\d", {
        "wifi_version": "Wi-Fi 6",
        "bluetooth_version": "5.3",
        "usb_type": "USB 2.0 Type-C",
        "esim": False,
    }),
    # OnePlus 13+
    ("oneplus", r"oneplus\s*1[3-9]|oneplus\s*[2-9]\d", {
        "wifi_version": "Wi-Fi 7",
        "bluetooth_version": "5.4",
        "usb_type": "USB 3.2 Gen 2 Type-C",
        "esim": False,
    }),
    ("oneplus", r"oneplus\s*1[2]", {
        "wifi_version": "Wi-Fi 7",
        "bluetooth_version": "5.4",
        "usb_type": "USB 3.2 Gen 2 Type-C",
        "esim": False,
    }),
    # Apple iPhone
    ("apple", r"iphone\s*1[6-9]|iphone\s*[2-9]\d", {
        "wifi_version": "Wi-Fi 7",
        "bluetooth_version": "5.3",
        "usb_type": "USB 3 Type-C",
        "esim": True,
    }),
    ("apple", r"iphone\s*1[5]", {
        "wifi_version": "Wi-Fi 6E",
        "bluetooth_version": "5.3",
        "usb_type": "USB 3 Type-C",
        "esim": True,
    }),
    # Xiaomi 14+
    ("xiaomi", r"xiaomi\s*1[4-9]\s*ultra|xiaomi\s*1[4-9]\s*pro", {
        "wifi_version": "Wi-Fi 7",
        "bluetooth_version": "5.4",
        "usb_type": "USB 3.2 Gen 2 Type-C",
        "esim": False,
    }),
    ("xiaomi", r"xiaomi\s*1[4-9]", {
        "wifi_version": "Wi-Fi 7",
        "bluetooth_version": "5.4",
        "usb_type": "USB 2.0 Type-C",
        "esim": False,
    }),
    # Nothing Phone 2+
    ("nothing", r"phone\s*[2-9]", {
        "wifi_version": "Wi-Fi 6E",
        "bluetooth_version": "5.3",
        "usb_type": "USB 2.0 Type-C",
        "esim": False,
    }),
]

_DEFAULT_CONNECTIVITY = {
    "wifi_version": "Wi-Fi 6",
    "bluetooth_version": "5.0",
    "usb_type": "USB Type-C",
    "esim": None,
}


def get_connectivity_info(brand: str, model: str) -> dict:
    """
    Returns connectivity defaults for a given brand + model.
    Used as a fallback when raw connectivity text doesn't have enough detail.
    """
    brand_lower = (brand or "").lower().strip()
    model_lower = (model or "").lower().strip()
    full_name = f"{brand_lower} {model_lower}"

    for b_pattern, m_pattern, conn_data in _CONNECTIVITY_DB:
        if b_pattern and b_pattern not in brand_lower:
            continue
        if m_pattern and not re.search(m_pattern, full_name, re.IGNORECASE):
            continue
        return conn_data

    return dict(_DEFAULT_CONNECTIVITY)


# ---------------------------------------------------------------------------
# Build info database (cooling system, materials)
# ---------------------------------------------------------------------------

_BUILD_DB = [
    # Samsung Galaxy S Ultra series
    ("samsung", r"galaxy\s*s2[3-9]\s*ultra|galaxy\s*s[3-9]\d\s*ultra", {
        "cooling_system": "Vapor Chamber + Graphene",
        "build_materials": "Titanium frame, Corning Gorilla Glass Armor",
    }),
    # Samsung Galaxy S flagship (non-ultra)
    ("samsung", r"galaxy\s*s2[4-9]|galaxy\s*s[3-9]\d(?!\s*ultra)", {
        "cooling_system": "Vapor Chamber",
        "build_materials": "Armor Aluminum frame, Corning Gorilla Glass",
    }),
    # Samsung Galaxy Z Fold
    ("samsung", r"galaxy\s*z\s*fold", {
        "cooling_system": "Vapor Chamber",
        "build_materials": "Titanium frame, Armor Aluminum hinge",
    }),
    # Samsung Galaxy Z Flip
    ("samsung", r"galaxy\s*z\s*flip", {
        "cooling_system": "Graphene",
        "build_materials": "Armor Aluminum frame, glass back",
    }),
    # Google Pixel Pro
    ("google", r"pixel\s*\d+\s*pro|pixel\s*ultra", {
        "cooling_system": "Vapor Chamber",
        "build_materials": "Polished aluminum frame, matte glass back",
    }),
    # Google Pixel standard
    ("google", r"pixel", {
        "cooling_system": "Thermal spreader",
        "build_materials": "Matte aluminum frame, matte glass back",
    }),
    # OnePlus flagship
    ("oneplus", r"oneplus\s*1[2-9]|oneplus\s*[2-9]\d", {
        "cooling_system": "Vapor Chamber + Graphene",
        "build_materials": "Aluminum frame, glass/vegan leather back",
    }),
    # Apple iPhone Pro
    ("apple", r"iphone\s*\d+\s*pro", {
        "cooling_system": "Stainless steel thermal system",
        "build_materials": "Titanium frame, textured matte glass back",
    }),
    # Apple iPhone standard
    ("apple", r"iphone", {
        "cooling_system": "Aluminum thermal system",
        "build_materials": "Aluminum frame, color-infused glass back",
    }),
    # Xiaomi Ultra
    ("xiaomi", r"xiaomi\s*\d+\s*ultra", {
        "cooling_system": "4D Hyper-cooling Vapor Chamber",
        "build_materials": "Titanium/Aluminum frame, ceramic/leather back",
    }),
    # Xiaomi flagship
    ("xiaomi", r"xiaomi\s*1[4-9]", {
        "cooling_system": "Vapor Chamber",
        "build_materials": "Aluminum frame, glass/leather back",
    }),
    # Nothing Phone
    ("nothing", r"phone", {
        "cooling_system": "Graphene",
        "build_materials": "Aluminum frame, transparent glass back",
    }),
    # Motorola Edge / Razr
    ("motorola", r"edge|razr", {
        "cooling_system": "Vapor Chamber",
        "build_materials": "Aluminum frame, glass back",
    }),
]


def get_build_info(brand: str, model: str) -> dict:
    """
    Returns build info (cooling system, materials) for a given brand + model.
    Used as a fallback when build data is not in raw specs.
    """
    brand_lower = (brand or "").lower().strip()
    model_lower = (model or "").lower().strip()
    full_name = f"{brand_lower} {model_lower}"

    for b_pattern, m_pattern, build_data in _BUILD_DB:
        if b_pattern and b_pattern not in brand_lower:
            continue
        if m_pattern and not re.search(m_pattern, full_name, re.IGNORECASE):
            continue
        return dict(build_data)

    return {
        "cooling_system": None,
        "build_materials": None,
    }
