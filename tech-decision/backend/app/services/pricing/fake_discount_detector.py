"""
fake_discount_detector.py
Detects suspicious or misleading pricing by comparing the claimed platform discount
to the authentic discount based on launch price history.

Output:
    fake_discount_flag: bool        — True when discount appears inflated
    discount_authenticity_score: int  — 0-100 (100 = completely trustworthy)
    price_intelligence_note: str    — Plain-English pricing insight
"""
from typing import Optional, Dict, Any


class FakeDiscountDetector:
    """
    Analyses a single price listing against the phone's launch price history
    and produces authenticity signals.
    """

    # Thresholds
    # Gap between claimed discount % and authentic discount % that triggers flags
    SEVERE_INFLATION_GAP = 20    # e.g., "35% off" when real discount is only 5%
    MODERATE_INFLATION_GAP = 10  # e.g., "20% off" when real discount is 10%

    @classmethod
    def analyze(
        cls,
        listed_price: int,
        original_mrp: Optional[int],
        launch_price: Optional[int],
        current_avg_price: Optional[int],
        platform: str = "",
    ) -> Dict[str, Any]:
        """
        Analyse a listing and return pricing authenticity signals.

        Args:
            listed_price:     Current selling price shown on the platform
            original_mrp:     Platform-stated MRP (may be artificially inflated)
            launch_price:     Official MSRP at launch (our ground truth)
            current_avg_price: Historical current market average
            platform:         Platform name for context (used in notes)

        Returns:
            dict with keys: fake_discount_flag, discount_authenticity_score,
                            price_intelligence_note
        """
        if not listed_price or listed_price <= 0:
            return cls._unknown_result()

        # Claimed discount = what the platform says you're saving vs their MRP
        claimed_discount_pct = 0.0
        if original_mrp and original_mrp > listed_price:
            claimed_discount_pct = (original_mrp - listed_price) / original_mrp * 100

        # Authentic discount = actual saving vs official launch MSRP
        authentic_discount_pct = 0.0
        reference_price = launch_price or current_avg_price
        if reference_price and reference_price > listed_price:
            authentic_discount_pct = (reference_price - listed_price) / reference_price * 100
        elif reference_price and reference_price <= listed_price:
            # Phone is selling above launch price or has appreciated
            authentic_discount_pct = 0.0

        gap = claimed_discount_pct - authentic_discount_pct

        # --- Severe inflation ---
        if gap >= cls.SEVERE_INFLATION_GAP:
            note = (
                f"⚠️ Claimed {claimed_discount_pct:.0f}% discount appears misleading — "
                f"this phone has historically sold near ₹{listed_price:,}, making the actual "
                f"saving only ~{authentic_discount_pct:.0f}% from launch price."
            )
            return {
                "fake_discount_flag": True,
                "discount_authenticity_score": 15,
                "price_intelligence_note": note,
            }

        # --- Moderate inflation ---
        if gap >= cls.MODERATE_INFLATION_GAP:
            note = (
                f"Claimed {claimed_discount_pct:.0f}% discount appears partially inflated. "
                f"Real saving from launch price is ~{authentic_discount_pct:.0f}%. "
                f"The listed MRP seems higher than the phone's typical market price."
            )
            return {
                "fake_discount_flag": True,
                "discount_authenticity_score": 50,
                "price_intelligence_note": note,
            }

        # --- Price above launch (currently overpriced) ---
        if reference_price and listed_price > reference_price * 1.05:
            overpriced_pct = ((listed_price - reference_price) / reference_price) * 100
            note = (
                f"This phone is currently priced {overpriced_pct:.0f}% above its official "
                f"launch price of ₹{reference_price:,}. Consider waiting for a price normalisation."
            )
            return {
                "fake_discount_flag": False,
                "discount_authenticity_score": 70,
                "price_intelligence_note": note,
            }

        # --- At or near historical low (great deal) ---
        if reference_price and authentic_discount_pct >= 15:
            note = (
                f"Excellent value — currently {authentic_discount_pct:.0f}% below launch price. "
                f"Pricing appears consistent with market history. Good time to buy."
            )
            return {
                "fake_discount_flag": False,
                "discount_authenticity_score": 95,
                "price_intelligence_note": note,
            }

        # --- Standard / trustworthy pricing ---
        if claimed_discount_pct > 0:
            note = (
                f"Pricing appears consistent with market history. "
                f"Current price reflects ~{authentic_discount_pct:.0f}% saving from launch."
            )
        else:
            note = "Pricing appears consistent with market history."

        return {
            "fake_discount_flag": False,
            "discount_authenticity_score": 90,
            "price_intelligence_note": note,
        }

    @staticmethod
    def _unknown_result() -> Dict[str, Any]:
        return {
            "fake_discount_flag": False,
            "discount_authenticity_score": 80,
            "price_intelligence_note": None,
        }

    @classmethod
    def generate_cross_platform_insight(
        cls,
        listings: list,
        launch_price: Optional[int] = None,
    ) -> Optional[str]:
        """
        Generates a top-level cross-platform pricing insight comparing all listings.

        Args:
            listings: List of listing dicts with 'platform', 'final_price', 'trust_score'
            launch_price: Official launch MSRP for context

        Returns:
            A single human-readable string summarising the price landscape.
        """
        if not listings:
            return None

        in_stock = [l for l in listings if l.get("in_stock", True)]
        if not in_stock:
            return "No listings are currently in stock."

        # Find the cheapest effective price
        by_price = sorted(in_stock, key=lambda x: x.get("final_price", 999999))
        cheapest = by_price[0]
        cheapest_platform = cheapest.get("platform", "Unknown")
        cheapest_price = cheapest.get("final_price", 0)

        # Find the most trusted platform
        by_trust = sorted(in_stock, key=lambda x: x.get("trust_score", 0), reverse=True)
        most_trusted = by_trust[0]
        trusted_platform = most_trusted.get("platform", "Unknown")

        parts = []

        if cheapest_platform == trusted_platform:
            parts.append(
                f"{cheapest_platform} currently offers the best effective price "
                f"(₹{cheapest_price:,}) and has the highest seller trust score."
            )
        else:
            parts.append(
                f"{cheapest_platform} offers the lowest effective price (₹{cheapest_price:,})."
            )
            trusted_price = most_trusted.get("final_price", 0)
            price_gap = trusted_price - cheapest_price
            if price_gap <= 2000:
                parts.append(
                    f"{trusted_platform} is the most trusted seller "
                    f"at only ₹{price_gap:,} more."
                )

        # Compare to launch price
        if launch_price and launch_price > 0:
            best_saving_pct = ((launch_price - cheapest_price) / launch_price) * 100
            if best_saving_pct >= 10:
                parts.append(
                    f"Best deal is {best_saving_pct:.0f}% below official launch price."
                )
            elif best_saving_pct < 0:
                parts.append(
                    "All platforms are currently pricing above the official launch price — consider waiting."
                )

        return " ".join(parts) if parts else None
