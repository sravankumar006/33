import re
from datetime import datetime
from typing import Optional, Union

class OfferNormalizer:
    @staticmethod
    def clean_price(price_val: Optional[Union[str, int, float]]) -> int:
        """
        Cleans currency values to standard integer.
        E.g., "₹69,999" -> 69999, 69999.0 -> 69999, None -> 0.
        """
        if price_val is None:
            return 0
        if isinstance(price_val, (int, float)):
            return int(price_val)
        
        # Strip currency symbols, commas, whitespace, and convert to int
        cleaned = re.sub(r'[^\d]', '', str(price_val))
        try:
            return int(cleaned) if cleaned else 0
        except ValueError:
            return 0

    @staticmethod
    def normalize_stock(stock_status: Optional[Union[str, bool]]) -> bool:
        """
        Converts stock status to boolean.
        """
        if stock_status is None:
            return True
        if isinstance(stock_status, bool):
            return stock_status
        
        status_str = str(stock_status).lower().strip()
        if any(term in status_str for term in ["out of stock", "unavailable", "sold out", "notify me"]):
            return False
        return True

    @staticmethod
    def normalize_delivery_eta(eta_val: Optional[Union[str, int]]) -> Optional[int]:
        """
        Normalizes delivery estimate string or int into integer days.
        E.g., "Delivery by Tomorrow" -> 1, "3 days" -> 3, "FREE delivery Wednesday" -> calculate, etc.
        """
        if eta_val is None:
            return None
        if isinstance(eta_val, int):
            return max(0, eta_val)
        
        eta_str = str(eta_val).lower().strip()
        if "tomorrow" in eta_str or "1 day" in eta_str or "same day" in eta_str:
            return 1
        
        # Look for numbers in the string
        match = re.search(r'\b(\d+)\b', eta_str)
        if match:
            return int(match.group(1))
            
        # Try to infer weekday delivery, e.g. "by Wednesday"
        weekdays = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6
        }
        for day_name, day_idx in weekdays.items():
            if day_name in eta_str:
                today = datetime.now()
                days_ahead = day_idx - today.weekday()
                if days_ahead <= 0:  # Target day is next week
                    days_ahead += 7
                return days_ahead
                
        return 3  # Default fallback

    @staticmethod
    def normalize_cashback(raw_cashback: Optional[Union[str, int, float]]) -> int:
        """
        Normalizes cashback value to integer.
        """
        return OfferNormalizer.clean_price(raw_cashback)

    @staticmethod
    def deduplicate_offers(listings: list) -> list:
        """
        Deduplicates listings keeping the first one for each platform.
        """
        seen_platforms = set()
        unique_listings = []
        for lst in listings:
            platform = lst.get("platform")
            if platform not in seen_platforms:
                seen_platforms.add(platform)
                unique_listings.append(lst)
        return unique_listings

    @staticmethod
    def validate_price_sanity(listed_price: int, launch_price: Optional[int]) -> bool:
        """
        Validates if the listed price is realistic compared to launch price.
        Rejects listed prices that are too low (e.g. < 25% of launch price, likely an accessory)
        or too high (e.g. > 1.8x of launch price).
        """
        if not launch_price or launch_price <= 0:
            return True
        if listed_price <= 0:
            return False
        
        # If listed price is less than 25% of launch price, it is likely a case/accessory
        if listed_price < launch_price * 0.25:
            return False
            
        # If listed price is way higher than launch price, reject
        if listed_price > launch_price * 1.8:
            return False
            
        return True

    @staticmethod
    def generate_cross_platform_insight(listings: list, launch_price: Optional[int] = None) -> Optional[str]:
        """
        Generates a top-level cross-platform pricing insight comparing all listings.
        """
        from app.services.pricing.fake_discount_detector import FakeDiscountDetector
        return FakeDiscountDetector.generate_cross_platform_insight(listings, launch_price)

