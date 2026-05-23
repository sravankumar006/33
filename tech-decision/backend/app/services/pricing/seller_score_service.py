from typing import Optional
from app.services.seller_trust import SellerTrust

class SellerScoreService:
    @staticmethod
    def calculate(
        platform: str,
        seller_rating: Optional[float],
        reviews_count: Optional[int]
    ) -> int:
        """
        Calculates a seller trust score from 0 to 100.
        Delegates to the core SellerTrust calculation.
        """
        return SellerTrust.calculate_score(platform, seller_rating, reviews_count)
