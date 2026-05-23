from typing import List, Tuple, Optional
from app.services.seller_trust import SellerTrust

class BestPlatformSelector:
    @staticmethod
    def select_best(listings: List[dict]) -> Tuple[Optional[dict], str]:
        """
        Selects the best listing based on price, seller trust, and delivery time.
        Out-of-stock listings are ignored.
        """
        # Filter out out-of-stock listings
        in_stock_listings = [l for l in listings if l.get('in_stock', True)]
        if not in_stock_listings:
            return None, "No listings are currently in stock."

        scored_listings = []
        for listing in in_stock_listings:
            final_price = listing.get('final_price', 0)
            
            # Trust score calculation
            trust_score = SellerTrust.calculate_score(
                listing.get('platform', ''),
                listing.get('seller_rating'),
                listing.get('seller_reviews_count')
            )
            # Annotate listing dict with calculated trust score
            listing['trust_score'] = trust_score
            
            # Trust penalty:
            # - trust >= 85: 0 penalty
            # - trust 70-84: +500 (equivalent to ₹500 penalty)
            # - trust 50-69: +1500 (equivalent to ₹1500 penalty)
            # - trust < 50: +4000 (equivalent to ₹4000 penalty)
            if trust_score >= 85:
                trust_penalty = 0
            elif trust_score >= 70:
                trust_penalty = 500
            elif trust_score >= 50:
                trust_penalty = 1500
            else:
                trust_penalty = 4000

            # Delivery penalty:
            # - delivery <= 1 day: 0 penalty
            # - delivery 2-3 days: +200 (equivalent to ₹200 penalty)
            # - delivery 4-5 days: +500 (equivalent to ₹500 penalty)
            # - delivery > 5 days (or null): +1000 (equivalent to ₹1000 penalty)
            delivery_eta = listing.get('delivery_eta_days')
            if delivery_eta is None:
                delivery_penalty = 1000
            elif delivery_eta <= 1:
                delivery_penalty = 0
            elif delivery_eta <= 3:
                delivery_penalty = 200
            elif delivery_eta <= 5:
                delivery_penalty = 500
            else:
                delivery_penalty = 1000

            effective_cost = final_price + trust_penalty + delivery_penalty
            scored_listings.append((effective_cost, listing))

        # Sort by effective cost ascending (lower cost/penalty is better)
        scored_listings.sort(key=lambda x: x[0])
        _, best_listing = scored_listings[0]

        # Generate custom explanation comparing to other listings
        platform = best_listing.get('platform')
        final_price = best_listing.get('final_price')
        trust_score = best_listing.get('trust_score')

        if len(scored_listings) > 1:
            # Find the next best option (excluding best_listing's platform)
            other_listings = [l for _, l in scored_listings if l.get('platform') != platform]
            if other_listings:
                runner_up = other_listings[0]
                price_diff = runner_up.get('final_price') - final_price
                
                if price_diff > 0:
                    explanation = (
                        f"{platform} is ₹{price_diff:,} cheaper than {runner_up.get('platform')} "
                        f"and the seller has a strong trust score of {trust_score}."
                    )
                elif price_diff == 0:
                    if trust_score > runner_up.get('trust_score'):
                        explanation = (
                            f"Both {platform} and {runner_up.get('platform')} have the same price, "
                            f"but {platform} is recommended because its seller has a higher trust score ({trust_score} vs {runner_up.get('trust_score')})."
                        )
                    else:
                        explanation = (
                            f"Both {platform} and {runner_up.get('platform')} have the same price, "
                            f"but {platform} is recommended because it offers faster delivery."
                        )
                else:
                    # runner_up is actually cheaper in final_price but has worse trust/delivery penalty!
                    explanation = (
                        f"Although {runner_up.get('platform')} is ₹{abs(price_diff):,} cheaper, "
                        f"{platform} is recommended because the seller is more trustworthy (trust score: {trust_score} vs {runner_up.get('trust_score')}) "
                        f"and offers faster delivery."
                    )
            else:
                # All other listings are on the same platform
                runner_up = scored_listings[1][1]
                price_diff = runner_up.get('final_price') - final_price
                explanation = f"We recommend the listing from {platform} ({best_listing.get('seller_name')}) as it is ₹{price_diff:,} cheaper than another seller on the same platform."
        else:
            explanation = f"{platform} is currently the only available platform in stock, offering a final price of ₹{final_price:,}."

        return best_listing, explanation
