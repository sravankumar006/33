from typing import Optional

class SellerTrust:
    @staticmethod
    def calculate_score(
        platform: str,
        seller_rating: Optional[float],
        reviews_count: Optional[int]
    ) -> int:
        """
        Calculates a seller trust score from 0 to 100.
        Uses platform reputation baseline, seller rating, and review count.
        """
        # 1. Platform reputation baseline (Max 40 points)
        platform_lower = platform.lower()
        if 'amazon' in platform_lower or 'croma' in platform_lower:
            platform_score = 40
        elif 'flipkart' in platform_lower:
            platform_score = 35
        elif 'reliance' in platform_lower:
            platform_score = 30
        else:
            platform_score = 20

        # 2. Seller rating factor (Max 40 points)
        # Default rating to 3.5 if none provided
        rating = seller_rating if seller_rating is not None else 3.5
        # Cap rating between 0 and 5
        rating = max(0.0, min(5.0, rating))
        rating_score = int((rating / 5.0) * 40)

        # 3. Review count factor / confidence (Max 20 points)
        reviews = reviews_count if reviews_count is not None else 0
        if reviews <= 0:
            reviews_score = 0
        elif reviews < 100:
            reviews_score = 5
        elif reviews < 1000:
            reviews_score = 10
        elif reviews < 5000:
            reviews_score = 15
        else:
            reviews_score = 20

        total_score = platform_score + rating_score + reviews_score
        return max(0, min(100, total_score))
