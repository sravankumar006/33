import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import delete

from app.models.phone import Phone, PriceListing, PhoneVariant, VariantPrice
from app.services.pricing.offer_normalizer import OfferNormalizer
from app.services.pricing.seller_score_service import SellerScoreService
from app.services.pricing.fake_discount_detector import FakeDiscountDetector
from app.services.final_price_calculator import FinalPriceCalculator

from app.parsers.pricing.amazon_parser import AmazonParser
from app.parsers.pricing.flipkart_parser import FlipkartParser
from app.parsers.pricing.croma_parser import CromaParser
from app.parsers.pricing.reliance_parser import RelianceParser

from app.services.variants.variant_extractor import generate_all_variants
from app.services.variants.variant_normalizer import generate_variant_slug
from app.services.variants.variant_pricing_mapper import match_listing_to_variant, scale_variant_prices

logger = logging.getLogger("uvicorn.error")

class PricingService:
    @classmethod
    def fetch_and_save_prices(cls, phone: Phone, db: Session) -> list:
        """
        Fetches prices from Amazon, Flipkart, Croma, and Reliance Digital.
        Normalizes listings, computes effective final prices & trust scores,
        saves them to the database (deleting old listings), and returns the new models.
        Also maps, scales, and persists variant-specific prices in variant_prices.
        """
        query = f"{phone.brand} {phone.model}"
        base_price = phone.current_avg_price or phone.launch_price or 45000
        
        logger.info(f"PricingService: Aggregating prices for '{query}' (base_price: {base_price})")
        
        # 1. Ensure variants exist for the phone. If not, auto-create them from specs.
        if not phone.variants and phone.spec:
            try:
                extracted_variants = generate_all_variants(
                    raw_ram_str=phone.spec.raw_ram,
                    raw_colors_str=phone.spec.raw_colors,
                    fallback_ram=phone.spec.ram_gb,
                    fallback_storage=phone.spec.storage_gb
                )
                for ev_dict in extracted_variants:
                    ram = ev_dict["ram_gb"]
                    storage = ev_dict["storage_gb"]
                    color = ev_dict["color"]
                    v_slug = generate_variant_slug(phone.slug, ram, storage, color)
                    
                    new_var = PhoneVariant(
                        phone_id=phone.id,
                        ram_gb=ram,
                        storage_gb=storage,
                        color=color,
                        slug=v_slug
                    )
                    db.add(new_var)
                db.commit()
                db.refresh(phone)
            except Exception as exc:
                logger.error(f"PricingService: Error auto-populating variants: {exc}", exc_info=True)
                db.rollback()

        parsers = [
            AmazonParser(),
            FlipkartParser(),
            CromaParser(),
            RelianceParser()
        ]
        
        raw_listings = []
        for parser in parsers:
            try:
                # Retrieve parsed listings (which might be real or simulated fallback)
                listings = parser.search_and_parse(query, base_price=base_price)
                if listings:
                    raw_listings.extend(listings)
            except Exception as exc:
                logger.error(f"PricingService: Failure in parser {parser.PLATFORM}: {exc}", exc_info=True)
                # Ensure parser failure does not crash the entire orchestration pipeline
                continue

        # Remove duplicate platforms
        unique_listings = OfferNormalizer.deduplicate_offers(raw_listings)

        # Clear existing listings for this phone (legacy support)
        try:
            db.execute(delete(PriceListing).where(PriceListing.phone_id == phone.id))
            db.commit()
        except Exception as exc:
            logger.error(f"PricingService: Error clearing old listings: {exc}")
            db.rollback()

        saved_listings = []
        for lst in unique_listings:
            try:
                # Clean up and normalize properties
                listed_p = OfferNormalizer.clean_price(lst["listed_price"])
                
                # Sanity check listed price against launch price
                if phone.launch_price and not OfferNormalizer.validate_price_sanity(listed_p, phone.launch_price):
                    logger.warning(f"PricingService: Rejecting sanity-failed listing for {lst.get('platform')}: price={listed_p}, launch={phone.launch_price}")
                    continue

                original_mrp = OfferNormalizer.clean_price(lst.get("original_mrp"))
                coupon_d = OfferNormalizer.clean_price(lst["coupon_discount"])
                bank_d = OfferNormalizer.clean_price(lst["bank_discount"])
                exchange_b = OfferNormalizer.clean_price(lst["exchange_bonus"])
                cashback_a = OfferNormalizer.normalize_cashback(lst.get("cashback_amount", 0))
                delivery_c = OfferNormalizer.clean_price(lst["delivery_charge"])

                final_p = FinalPriceCalculator.calculate(
                    listed_price=listed_p,
                    coupon_discount=coupon_d,
                    bank_discount=bank_d,
                    exchange_bonus=exchange_b,
                    delivery_charge=delivery_c
                )
                
                # Fake discount detection
                try:
                    authenticity = FakeDiscountDetector.analyze(
                        listed_price=listed_p,
                        original_mrp=original_mrp if original_mrp > 0 else None,
                        launch_price=phone.launch_price,
                        current_avg_price=phone.current_avg_price,
                        platform=lst.get("platform", ""),
                    )
                except Exception as det_exc:
                    logger.warning(f"PricingService: FakeDiscountDetector failed: {det_exc}")
                    authenticity = {
                        "fake_discount_flag": False,
                        "discount_authenticity_score": 80,
                        "price_intelligence_note": None,
                    }
                
                in_stock = OfferNormalizer.normalize_stock(lst.get("in_stock", True))
                delivery_days = OfferNormalizer.normalize_delivery_eta(lst.get("delivery_eta_days", 3))
                
                new_listing = PriceListing(
                    phone_id=phone.id,
                    platform=lst["platform"],
                    seller_name=lst["seller_name"],
                    seller_rating=lst["seller_rating"],
                    seller_reviews_count=lst["seller_reviews_count"],
                    listed_price=listed_p,
                    original_mrp=original_mrp if original_mrp > 0 else None,
                    coupon_discount=coupon_d,
                    bank_discount=bank_d,
                    exchange_bonus=exchange_b,
                    cashback_amount=cashback_a,
                    delivery_charge=delivery_c,
                    final_price=final_p,
                    in_stock=in_stock,
                    delivery_eta_days=delivery_days,
                    product_url=lst["product_url"],
                    fake_discount_flag=authenticity["fake_discount_flag"],
                    discount_authenticity_score=authenticity["discount_authenticity_score"],
                    price_intelligence_note=authenticity["price_intelligence_note"],
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(new_listing)
                saved_listings.append(new_listing)
            except Exception as exc:
                logger.error(f"PricingService: Error processing/saving listing for {lst.get('platform')}: {exc}", exc_info=True)
                continue
                
        try:
            db.commit()
            for sl in saved_listings:
                db.refresh(sl)
        except Exception as exc:
            logger.error(f"PricingService: Error committing new listings to database: {exc}")
            db.rollback()

        # 2. Match, scale, and save variant-specific pricing
        if phone.variants:
            mapped_listings = {str(v.id): [] for v in phone.variants}
            for lst in unique_listings:
                matched_var = match_listing_to_variant(lst.get("title"), phone.variants)
                if matched_var:
                    mapped_listings[str(matched_var.id)].append(lst)
            
            scaled_prices = scale_variant_prices(phone, phone.variants, mapped_listings)
            
            # Clear existing variant prices for these variants
            try:
                variant_ids = [v.id for v in phone.variants]
                if variant_ids:
                    db.execute(delete(VariantPrice).where(VariantPrice.variant_id.in_(variant_ids)))
                    db.commit()
            except Exception as exc:
                logger.error(f"PricingService: Error clearing old variant prices: {exc}")
                db.rollback()

            saved_variant_prices = []
            for sp in scaled_prices:
                try:
                    listed_p = sp["listed_price"]
                    original_mrp = sp.get("original_mrp")
                    coupon_d = sp.get("coupon_discount", 0)
                    bank_d = sp.get("bank_discount", 0)
                    exchange_b = sp.get("exchange_bonus", 0)
                    cashback_a = sp.get("cashback_amount", 0)
                    delivery_c = sp.get("delivery_charge", 0)
                    
                    final_p = FinalPriceCalculator.calculate(
                        listed_price=listed_p,
                        coupon_discount=coupon_d,
                        bank_discount=bank_d,
                        exchange_bonus=exchange_b,
                        delivery_charge=delivery_c
                    )
                    
                    try:
                        authenticity = FakeDiscountDetector.analyze(
                            listed_price=listed_p,
                            original_mrp=original_mrp if original_mrp and original_mrp > 0 else None,
                            launch_price=phone.launch_price,
                            current_avg_price=phone.current_avg_price,
                            platform=sp.get("platform", ""),
                        )
                    except Exception as det_exc:
                        logger.warning(f"PricingService: FakeDiscountDetector failed for variant: {det_exc}")
                        authenticity = {
                            "fake_discount_flag": False,
                            "discount_authenticity_score": 80,
                            "price_intelligence_note": None,
                        }
                    
                    new_vp = VariantPrice(
                        variant_id=sp["variant_id"],
                        platform=sp["platform"],
                        seller_name=sp["seller_name"],
                        seller_rating=sp.get("seller_rating"),
                        seller_reviews_count=sp.get("seller_reviews_count"),
                        listed_price=listed_p,
                        original_mrp=original_mrp if original_mrp and original_mrp > 0 else None,
                        coupon_discount=coupon_d,
                        bank_discount=bank_d,
                        exchange_bonus=exchange_b,
                        cashback_amount=cashback_a,
                        delivery_charge=delivery_c,
                        final_price=final_p,
                        in_stock=sp.get("in_stock", True),
                        delivery_eta_days=sp.get("delivery_eta_days", 3),
                        product_url=sp["product_url"],
                        fake_discount_flag=authenticity["fake_discount_flag"],
                        discount_authenticity_score=authenticity["discount_authenticity_score"],
                        price_intelligence_note=authenticity["price_intelligence_note"],
                        updated_at=datetime.now(timezone.utc)
                    )
                    db.add(new_vp)
                    saved_variant_prices.append(new_vp)
                except Exception as exc:
                    logger.error(f"PricingService: Error processing variant price: {exc}", exc_info=True)
                    continue

            try:
                db.commit()
                logger.info(f"PricingService: Saved {len(saved_variant_prices)} variant prices for phone '{phone.model}'")
            except Exception as exc:
                logger.error(f"PricingService: Error committing new variant prices: {exc}")
                db.rollback()

        logger.info(f"PricingService: Saved {len(saved_listings)} listings for phone '{phone.model}'")
        return saved_listings
