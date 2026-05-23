from typing import Dict, Tuple

class NormalizationService:
    # A mapping of common brands to their canonical casing/spelling.
    BRAND_MAP: Dict[str, str] = {
        "samsung": "Samsung",
        "apple": "Apple",
        "oneplus": "OnePlus",
        "one plus": "OnePlus",
        "xiaomi": "Xiaomi",
        "oppo": "Oppo",
        "vivo": "Vivo",
        "realme": "Realme",
        "motorola": "Motorola",
        "google": "Google",
        "nothing": "Nothing",
        "asus": "Asus",
        "sony": "Sony",
        "huawei": "Huawei",
        "honor": "Honor",
        "nokia": "Nokia",
        "lenovo": "Lenovo",
        "lg": "LG",
        "htc": "HTC"
    }

    @classmethod
    def normalize(cls, brand: str, model: str) -> Tuple[str, str]:
        """
        Normalize brand and clean model names.
        Example:
            Input: brand="OnePlus", model="OnePlus 13"
            Output: ("OnePlus", "13")
        """
        # 1. Clean brand
        clean_brand = brand.strip()
        brand_lower = clean_brand.lower()
        
        # Check against common brand mapping
        matched_brand = cls.BRAND_MAP.get(brand_lower)
        if matched_brand:
            clean_brand = matched_brand
        else:
            # Capitalize first letter of brand by default
            clean_brand = clean_brand.title()

        # 2. Clean model
        clean_model = model.strip()

        # Keep checking if the model name starts with the brand name
        # to handle cases like model = "OnePlus OnePlus 13" or model = "OnePlus 13"
        brand_name_lower = clean_brand.lower()
        
        while True:
            model_lower = clean_model.lower()
            if model_lower.startswith(brand_name_lower):
                # Remove the brand name prefix
                prefix_len = len(brand_name_lower)
                clean_model = clean_model[prefix_len:].strip()
                # Strip leading hyphens/underscores/spaces/etc.
                clean_model = clean_model.lstrip("-_: ")
            else:
                break

        # Fallback if model becomes empty
        if not clean_model:
            clean_model = model.strip()

        return clean_brand, clean_model
