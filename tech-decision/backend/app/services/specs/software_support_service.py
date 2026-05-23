"""
software_support_service.py
Maps brand + model patterns to software update commitment data.
Uses a curated static knowledge base derived from official manufacturer commitments.
"""
from typing import Optional, Dict, Any, Tuple
import re


# Update policy database: (brand_pattern, model_pattern, os_years, security_years, android_notes)
_UPDATE_POLICIES = [
    # Google Pixel
    ("google", r"pixel\s*[6-9]|pixel\s*fold|pixel\s*pro|pixel\s*ultra", 7, 7, "Android 15+"),
    ("google", r"pixel\s*[4-5]", 5, 5, "Android 14"),
    ("google", r"pixel", 3, 3, "Android"),

    # Samsung Galaxy S Ultra
    ("samsung", r"galaxy\s*s2[4-9]\s*ultra|galaxy\s*s[3-9]\d\s*ultra", 7, 7, "Android 15+"),
    # Samsung Galaxy S series (non-ultra)
    ("samsung", r"galaxy\s*s2[0-9]|galaxy\s*s[3-9]\d(?!\s*ultra)", 7, 7, "Android 15+"),
    # Samsung Galaxy Z Fold/Flip
    ("samsung", r"galaxy\s*z", 7, 7, "Android 15+"),
    # Samsung Galaxy A series recent
    ("samsung", r"galaxy\s*a[5-9]\d|galaxy\s*a[1-9][4-9]", 4, 5, "Android 13+"),
    # Samsung Galaxy A series older
    ("samsung", r"galaxy\s*a", 4, 4, "Android 13"),
    # Samsung Galaxy M series
    ("samsung", r"galaxy\s*m", 2, 4, "Android 13"),
    # Samsung Galaxy Tab S
    ("samsung", r"galaxy\s*tab\s*s[8-9]|galaxy\s*tab\s*s1[0-9]", 7, 7, "Android 15+"),
    ("samsung", r"galaxy\s*tab", 4, 4, "Android"),

    # OnePlus flagship
    ("oneplus", r"oneplus\s*1[2-9]|oneplus\s*[2-9]\d|oneplus\s*open|oneplus\s*fold", 4, 5, "Android 15+"),
    ("oneplus", r"oneplus\s*1[0-1]|oneplus\s*[7-9]", 3, 4, "Android 14"),
    # OnePlus Nord
    ("oneplus", r"nord\s*[4-9]|nord\s*ce\s*[4-9]|nord\s*[2-9]", 3, 4, "Android 14"),
    ("oneplus", r"nord", 2, 3, "Android 13"),
    ("oneplus", r"", 2, 3, "Android"),

    # Apple iPhone
    ("apple", r"iphone\s*1[5-9]|iphone\s*[2-9]\d", 6, 6, "iOS 18+"),
    ("apple", r"iphone\s*1[0-4]", 5, 6, "iOS 17"),
    ("apple", r"iphone", 4, 5, "iOS"),

    # Xiaomi / POCO
    ("xiaomi", r"xiaomi\s*1[4-9]\s*ultra|xiaomi\s*[2-9]\d\s*ultra", 4, 5, "Android 15+"),
    ("xiaomi", r"xiaomi\s*1[3-9]|xiaomi\s*[2-9]\d", 3, 4, "Android 14"),
    ("xiaomi", r"poco\s*f[5-9]|poco\s*x[5-7]", 3, 4, "Android 14"),
    ("xiaomi", r"poco|xiaomi|redmi", 2, 3, "Android 13"),

    # Motorola
    ("motorola", r"razr|edge\s*[4-9]\d", 4, 4, "Android 14"),
    ("motorola", r"", 3, 3, "Android 14"),

    # Nothing
    ("nothing", r"phone\s*[2-9]|phone\s*\([2-9]\)", 3, 4, "Android 14+"),
    ("nothing", r"", 2, 3, "Android"),

    # Realme / OPPO / vivo  
    ("realme", r"gt\s*[6-9]|gt\s*[2-5]\s*pro", 3, 4, "Android 14"),
    ("realme", r"", 2, 3, "Android"),
    ("oppo", r"find\s*x[6-9]|reno\s*1[2-9]", 4, 5, "Android 14"),
    ("oppo", r"", 2, 3, "Android"),
    ("vivo", r"x1[0-9][0-9]\s*pro|x[7-9]\d", 3, 4, "Android 14"),
    ("vivo", r"iqoo\s*[1-9][0-9]|iqoo\s*neo", 3, 4, "Android 14"),
    ("vivo", r"", 2, 3, "Android"),

    # Honor
    ("honor", r"magic\s*[6-9]|magic\s*v[2-9]", 3, 5, "Android 14"),
    ("honor", r"", 2, 3, "Android"),

    # Asus
    ("asus", r"rog\s*phone\s*[7-9]", 3, 5, "Android 14"),
    ("asus", r"zenfone\s*1[0-9]", 3, 5, "Android 14"),
    ("asus", r"", 2, 3, "Android"),
]


_POLICY_LABELS = {
    7: "Among the best long-term software support in Android",
    6: "Excellent long-term support — significantly above industry average",
    5: "Strong update commitment — well above Android average",
    4: "Good update commitment — above Android average",
    3: "Standard Android update cycle",
    2: "Below average update commitment",
    1: "Minimal update support",
}


def get_software_support(brand: str, model: str) -> Dict[str, Any]:
    """
    Returns estimated software update years, security update years, and human label
    for a given brand + model combination.
    """
    brand_lower = (brand or "").lower().strip()
    model_lower = (model or "").lower().strip()
    full_name = f"{brand_lower} {model_lower}"

    os_years = 2
    security_years = 3

    for b_pattern, m_pattern, os_y, sec_y, _ in _UPDATE_POLICIES:
        if b_pattern and b_pattern not in brand_lower:
            continue
        if m_pattern and not re.search(m_pattern, full_name, re.IGNORECASE):
            continue
        os_years = os_y
        security_years = sec_y
        break

    label = _POLICY_LABELS.get(os_years, "Standard update cycle")

    return {
        "os_updates_years": os_years,
        "security_updates_years": security_years,
        "update_policy_label": f"{os_years} years OS updates · {security_years} years security · {label}",
    }
