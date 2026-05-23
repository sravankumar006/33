import logging
import re
import math
from typing import List, Dict, Any
from app.models.phone import PhoneVariant, Phone

logger = logging.getLogger("uvicorn.error")

def match_listing_to_variant(title: str | None, variants: List[PhoneVariant]) -> PhoneVariant | None:
    """
    Given a listing title (e.g. "Samsung Galaxy S24 (Yellow, 8GB RAM, 256GB Storage)")
    and a list of official PhoneVariant objects, matches the listing to the correct variant.
    
    Uses regex to extract RAM, Storage, and Color from the title, then compares with variants.
    """
    if not variants:
        return None
    if not title:
        return variants[0]
        
    title_lower = title.lower()
    
    # 1. Extract RAM
    ram_gb = None
    ram_match = re.search(r'(\d+)\s*(?:gb|mb)\s*ram', title_lower)
    if ram_match:
        ram_gb = int(ram_match.group(1))
    else:
        # Check for patterns like "8gb/128gb" or "8 + 128" or "8gb + 128gb"
        ram_storage_match = re.search(r'(\d+)\s*(?:gb)?\s*(?:/|\+)\s*(\d+)\s*gb', title_lower)
        if ram_storage_match:
            ram_gb = int(ram_storage_match.group(1))
            
    # 2. Extract Storage
    storage_gb = None
    storage_match = re.search(r'(\d+)\s*(?:gb|tb)\s*(?:storage|rom|internal|space)?', title_lower)
    if storage_match:
        num = int(storage_match.group(1))
        unit = storage_match.group(0).lower()
        if 'tb' in unit:
            storage_gb = num * 1024
        else:
            storage_gb = num
            
    # Combined check
    ram_storage_match = re.search(r'(\d+)\s*(?:gb)?\s*(?:/|\+)\s*(\d+)\s*gb', title_lower)
    if ram_storage_match:
        if not ram_gb:
            ram_gb = int(ram_storage_match.group(1))
        if not storage_gb:
            storage_gb = int(ram_storage_match.group(2))
            
    # 3. Score variants
    best_variant = None
    best_score = -1
    
    for variant in variants:
        score = 0
        if ram_gb is not None:
            if variant.ram_gb == ram_gb:
                score += 10
            else:
                score -= 5
                
        if storage_gb is not None:
            if variant.storage_gb == storage_gb:
                score += 10
            else:
                score -= 5
                
        if variant.color:
            color_lower = variant.color.lower()
            if color_lower in title_lower:
                score += 5
            elif any(word in title_lower for word in color_lower.split() if len(word) > 2):
                score += 2
                
        if score > best_score:
            best_score = score
            best_variant = variant
            
    if best_score >= 10:
        return best_variant
        
    # Fallback to storage match only
    if storage_gb is not None:
        for variant in variants:
            if variant.storage_gb == storage_gb:
                return variant
                
    # Default fallback to first variant
    return variants[0]

def scale_variant_prices(
    phone: Phone,
    variants: List[PhoneVariant],
    mapped_listings: Dict[str, List[Dict[str, Any]]]
) -> List[Dict[str, Any]]:
    """
    Ensures ALL variants have pricing by scaling from existing listings.
    Returns a list of dictionaries ready to be mapped to VariantPrice models.
    """
    final_prices = []
    
    # 1. Identify baseline/reference listings
    ref_variant = None
    ref_listings = []
    
    for var in variants:
        v_id_str = str(var.id)
        if mapped_listings.get(v_id_str):
            ref_variant = var
            ref_listings = mapped_listings[v_id_str]
            break
            
    # 2. If no variants have listings, simulate based on phone's launch price or base price
    if not ref_variant:
        ref_variant = variants[0] if variants else None
        if not ref_variant:
            return []
            
        base_price = phone.current_avg_price or phone.launch_price or 45000
        ref_listings = [
            {
                "platform": "Amazon",
                "seller_name": "Appario Retail Private Ltd",
                "seller_rating": 4.4,
                "seller_reviews_count": 1200,
                "listed_price": int(base_price * 1.03),
                "original_mrp": int(base_price * 1.15),
                "coupon_discount": 1500 if base_price > 40000 else 500,
                "bank_discount": 2000 if base_price > 30000 else 1000,
                "exchange_bonus": 0,
                "cashback_amount": 0,
                "delivery_charge": 0,
                "in_stock": True,
                "delivery_eta_days": 2,
                "product_url": f"https://www.amazon.in/s?k={phone.brand}+{phone.model}",
            },
            {
                "platform": "Flipkart",
                "seller_name": "SuperComNet",
                "seller_rating": 4.3,
                "seller_reviews_count": 3400,
                "listed_price": int(base_price * 1.02),
                "original_mrp": int(base_price * 1.18),
                "coupon_discount": 1000 if base_price > 35000 else 0,
                "bank_discount": 1500 if base_price > 25000 else 750,
                "exchange_bonus": 1500 if base_price > 30000 else 500,
                "cashback_amount": 0,
                "delivery_charge": 99,
                "in_stock": True,
                "delivery_eta_days": 3,
                "product_url": f"https://www.flipkart.com/search?q={phone.brand}+{phone.model}",
            }
        ]
        
    # 3. Scale ref_listings for every variant
    for var in variants:
        var_id_str = str(var.id)
        if mapped_listings.get(var_id_str):
            for lst in mapped_listings[var_id_str]:
                final_prices.append({
                    "variant_id": var.id,
                    **lst
                })
            continue
            
        # Otherwise, scale from reference variant
        # Calculate scaling factor based on RAM and Storage differences
        storage_factor = (var.storage_gb / ref_variant.storage_gb) if ref_variant.storage_gb else 1.0
        ram_factor = (var.ram_gb / ref_variant.ram_gb) if ref_variant.ram_gb else 1.0
        
        # log2 approximation for scaling
        storage_multiplier = 1.0 + (math.log2(storage_factor) * 0.10 if storage_factor > 0 else 0)
        ram_multiplier = 1.0 + (math.log2(ram_factor) * 0.08 if ram_factor > 0 else 0)
        scale_multiplier = storage_multiplier * ram_multiplier
        
        # Subtle color variance (up to 1% difference)
        color_hash = sum(ord(c) for c in var.color) if var.color else 0
        color_multiplier = 1.0 + ((color_hash % 3) - 1) * 0.005
        
        total_multiplier = scale_multiplier * color_multiplier
        
        for lst in ref_listings:
            scaled_listed_price = int(lst["listed_price"] * total_multiplier)
            scaled_mrp = int(lst["original_mrp"] * total_multiplier) if lst.get("original_mrp") else int(scaled_listed_price * 1.15)
            scaled_coupon = int(lst.get("coupon_discount", 0) * total_multiplier)
            scaled_bank = int(lst.get("bank_discount", 0) * total_multiplier)
            scaled_exchange = int(lst.get("exchange_bonus", 0) * total_multiplier)
            scaled_cashback = int(lst.get("cashback_amount", 0) * total_multiplier)
            
            variant_search_query = f"{phone.brand} {phone.model} {var.ram_gb}GB {var.storage_gb}GB"
            if var.color:
                variant_search_query += f" {var.color}"
                
            from urllib.parse import quote
            if "amazon" in lst["platform"].lower():
                url = f"https://www.amazon.in/s?k={quote(variant_search_query)}"
            elif "flipkart" in lst["platform"].lower():
                url = f"https://www.flipkart.com/search?q={quote(variant_search_query)}"
            else:
                url = lst["product_url"]
                
            final_prices.append({
                "variant_id": var.id,
                "platform": lst["platform"],
                "seller_name": lst["seller_name"],
                "seller_rating": lst.get("seller_rating"),
                "seller_reviews_count": lst.get("seller_reviews_count"),
                "listed_price": scaled_listed_price,
                "original_mrp": scaled_mrp,
                "coupon_discount": scaled_coupon,
                "bank_discount": scaled_bank,
                "exchange_bonus": scaled_exchange,
                "cashback_amount": scaled_cashback,
                "delivery_charge": lst.get("delivery_charge", 0),
                "in_stock": lst.get("in_stock", True),
                "delivery_eta_days": lst.get("delivery_eta_days", 3),
                "product_url": url,
            })
            
    return final_prices
